"""
WWTP Web Application Server Engine

Replaces main.py as the primary runtime execution vector.
Handles incoming user inputs, runs optimization loops, passes the top configurations 
to the structural sizer, and renders data directly onto an interactive dashboard.
"""

import copy
import os
import json
import sys
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ==============================================================================
# 🛠️ EXPLICIT FILESYSTEM INJECTION PATCH (Clears Linter Errors)
# ==============================================================================
PROJECT_ROOT_DIRECTORY = Path(__file__).resolve().parent

if str(PROJECT_ROOT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_DIRECTORY))

UNITS_SUBFOLDER_DIRECTORY = PROJECT_ROOT_DIRECTORY / "units"
if str(UNITS_SUBFOLDER_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(UNITS_SUBFOLDER_DIRECTORY))

# Import existing core engineering architecture natively
from config.standards import set_active_industry
from optimizer.optimizer import WWTPOptimizer
from simulator.process_simulator import ProcessSimulator
from simulator.structural_sizer import StructuralSizer
from simulator.cad_generator import CADGenerator

try:
    from filter_press import FilterPress
    from sludge_drying_bed import SludgeDryingBed
except (ImportError, ModuleNotFoundError):
    from units.filter_press import FilterPress
    from units.sludge_drying_bed import SludgeDryingBed
# ==============================================================================

app = FastAPI(title="Nepal Industrial WWTP Optimization Portal")

templates = Jinja2Templates(directory="templates")

optimizer = WWTPOptimizer()
simulator = ProcessSimulator()
sizer = StructuralSizer()
cad_gen = CADGenerator()


@app.get("/", response_class=HTMLResponse)
async def render_input_form(request: Request):
    """
    Renders the default dashboard control panel web form.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": None,
            "error": None,
            "inputs": {
                "industry": "Textile", "flow": 100, "peak_factor": 1.2,
                "BOD": 1200, "COD": 3500, "TSS": 1800, "Color": 2500, "TDS": 2200, "Oil": 45, "pH": 10.5,
                "no_limit": "true", "land_cap": 150, "capex_cap": 3500000, "opex_cap": 4000000,
                "sludge_enabled": "true", "sludge_method": "Natural"
            }
        }
    )


@app.post("/", response_class=HTMLResponse)
async def process_and_optimize(
    request: Request,
    industry: str = Form(...),
    flow: float = Form(...),
    peak_factor: float = Form(...),
    BOD: float = Form(...),
    COD: float = Form(...),
    TSS: float = Form(...),
    Color: float = Form(...),
    TDS: float = Form(...),
    Oil: float = Form(...),
    pH: float = Form(...),
    no_limit: str = Form(...),
    land_cap: float = Form(None),
    capex_cap: float = Form(None),
    opex_cap: float = Form(None),
    sludge_enabled: str = Form(...),
    sludge_method: str = Form(...)
):
    """
    Captures live user browser inputs, executes core design math, 
    and returns a full compilation report back to the dashboard layout.
    """
    set_active_industry(industry)
    
    inputs_cache = {
        "industry": industry, "flow": flow, "peak_factor": peak_factor,
        "BOD": BOD, "COD": COD, "TSS": TSS, "Color": Color, "TDS": TDS, "Oil": Oil, "pH": pH,
        "no_limit": no_limit, "land_cap": land_cap, "capex_cap": capex_cap, "opex_cap": opex_cap,
        "sludge_enabled": sludge_enabled, "sludge_method": sludge_method
    }

    design_flow = flow * peak_factor
    influent = {
        "flow": design_flow, "BOD": BOD, "COD": COD, "TSS": TSS, 
        "Color": Color, "TDS": TDS, "Oil": Oil, "pH": pH
    }

    if no_limit == "true":
        land_limit, capex_limit, opex_limit = None, None, None
    else:
        land_limit = land_cap
        capex_limit = capex_cap
        opex_limit = opex_cap

    optimization_package = optimizer.optimize(
        influent,
        land_available=land_limit,
        capex_limit=capex_limit,
        opex_limit=opex_limit,
        verbose=False
    )

    if optimization_package is None or (len(optimization_package["feasible"]) == 0 and len(optimization_package.get("fallbacks", [])) == 0):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "result": None,
                "error": "CRITICAL DESIGN CONSTRAINT BREACH: No valid process train combinations can fit within these budget or land bounds.",
                "inputs": inputs_cache
            }
        )

    is_fallback = False
    # ✔️ CRITICAL FIX: Explicitly extract the first element [0] from the sorted ranking collection lists
    if len(optimization_package["feasible"]) > 0:
        raw_solution = optimization_package["feasible"][0]
    else:
        raw_solution = optimization_package["fallbacks"][0]
        is_fallback = True

    best_solution = copy.deepcopy(raw_solution)

    raw_liquid_sludge_kg_day = best_solution["sludge_kg_day"]
    sludge_capex, sludge_opex, sludge_land, sludge_energy = 0.0, 0.0, 0.0, 0.0
    final_disposed_sludge_mass = raw_liquid_sludge_kg_day
    sludge_report = None

    is_sludge_active = (sludge_enabled == "true" and raw_liquid_sludge_kg_day > 0)
    if is_sludge_active:
        if sludge_method == "Mechanical":
            processor = FilterPress(raw_liquid_sludge_kg_day)
        else:
            processor = SludgeDryingBed(raw_liquid_sludge_kg_day)
            
        sludge_report = processor.design()
        sludge_capex = sludge_report["capex_npr"]
        sludge_opex = sludge_report["opex_npr_year"]
        sludge_land = sludge_report["land_m2"]
        sludge_energy = sludge_report["energy_kwh_day"]
        final_disposed_sludge_mass = sludge_report["sludge_kg_day"]

    compiled_data = {
        "train": " → ".join(best_solution["train"]),
        "is_fallback": is_fallback,
        "attainment_efficiency": round(best_solution.get("attainment_efficiency", 100.0), 2),
        "capex_total": best_solution["capex_npr"] + sludge_capex,
        "capex_base": best_solution["capex_npr"],
        "capex_sludge": sludge_capex,
        "opex_total": best_solution["opex_npr_year"] + sludge_opex,
        "land_total": best_solution["land_m2"] + sludge_land,
        "land_base": best_solution["land_m2"],
        "land_sludge": sludge_land,
        "energy_total": best_solution["energy_kwh_day"] + sludge_energy,
        "sludge_liquid": raw_liquid_sludge_kg_day,
        "sludge_solid": final_disposed_sludge_mass,
        "violations": best_solution["constraint_result"]["reasons"] if is_fallback else [],
        "effluent": {k: round(v, 2) if isinstance(v, (int, float)) else v for k, v in best_solution["effluent"].items()}
    }

    detailed_run = simulator.simulate_train(best_solution["train"], influent)
    structural_components = []
    
    for step in detailed_run["history"]:
        unit_name = step["unit"]
        unit_class = simulator.run_unit(unit_name, step["influent"])
        sizing_report = sizer.size_unit(unit_name, unit_class)
        
        structural_components.append({
            "name": unit_name,
            "geometry": sizing_report["geometry"],
            "dimensions": dict(copy.deepcopy(sizing_report["dimensions"]))
        })

    if is_sludge_active and sludge_report and "design" in sludge_report:
        structural_components.append({
            "name": f"Sludge Dewatering ({sludge_method})",
            "geometry": "Filter Press Array" if sludge_method == "Mechanical" else "Solar Drying Beds",
            "dimensions": dict(copy.deepcopy(sludge_report["design"]))
        })

    components_json = json.dumps(structural_components)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "result": compiled_data,
            "components": structural_components,
            "components_json": components_json,
            "error": None,
            "inputs": inputs_cache
        }
    )


@app.post("/download-cad")
async def download_cad_blueprint(
    industry: str = Form(...),
    components_data: str = Form(...)
):
    """
    Catches the active components payload list array from the webpage form 
    and writes out a downloadable .dxf file to the client browser.
    """
    structural_components = json.loads(components_data)
    dxf_filepath = cad_gen.generate_blueprint(structural_components, industry)
    filename = f"wwtp_layout_{industry.lower()}.dxf"
    
    return FileResponse(
        path=dxf_filepath,
        filename=filename,
        media_type="application/dxf"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
