"""
MAIN ENTRY POINT - MULTI-INDUSTRY SYSTEM WITH SLUDGE TREATMENT MODES

National Industrial Wastewater Optimization Framework for Nepal.
Supports: Strict cost constraints, No-Limit execution optimization,
and selectable Mechanical or Natural sludge dewatering treatment subsystems.
"""

from config.standards import set_active_industry
from optimizer.optimizer import WWTPOptimizer
from simulator.process_simulator import ProcessSimulator
from simulator.structural_sizer import StructuralSizer

# Import sludge treatment unit modules directly
from units.filter_press import FilterPress
from units.sludge_drying_bed import SludgeDryingBed


def main():
    # ==================================================================
    # ⚙️ SYSTEM CONTROL CONFIGURATION PARAMS
    # ==================================================================
    # Factory Target Profile Options: "Textile", "Tanning", "Pulp_Paper", "Dairy", "Distillery", "Sugar", "Brewery"
    CHOSEN_INDUSTRY = "Textile" 
    
    # 🌟 CONSTRAINT ENFORCEMENT MODE: Set True for unconstrained optimization, False to enforce budget limits
    NO_LIMIT_MODE = True 

    # 💩 SLUDGE TREATMENT SUB-SYSTEM CONFIGURATION SELECTORS:
    SLUDGE_TREATMENT_ENABLED = True     # 🔹 Toggle True to turn on post-sludge dewatering, False to bypass
    SLUDGE_TREATMENT_METHOD = "Natural" # 🔹 Option: "Mechanical" (Filter Press) or "Natural" (Sludge Drying Beds)

    # Synchronize the global regulatory checking engine context
    set_active_industry(CHOSEN_INDUSTRY)

    print("\n" + "=" * 90)
    print(f"      NEPAL INDUSTRIAL WASTEWATER TREATMENT DESIGN & OPTOSOLVER ENGINE")
    print(f"      Active Industrial Sector Context: {CHOSEN_INDUSTRY.upper()}")
    print(f"      Constraint Mode: {'[ UNCONSTRAINED UNLIMITED ]' if NO_LIMIT_MODE else '[ STRICT BUDGET CAPS FORCED ]'}")
    print(f"      Sludge Dewatering Sub-System: {'[ ENABLED - ' + SLUDGE_TREATMENT_METHOD.upper() + ' ]' if SLUDGE_TREATMENT_ENABLED else '[ DISABLED - RAW LIQUID HAULING ]'}")
    print("=" * 90)

    FACTORY_INFLUENT_DATABASE = {
        "Textile":    {"flow": 100, "BOD": 1200, "COD": 3500, "TSS": 1800, "Color": 2500, "TDS": 2200, "Oil": 45, "pH": 10.5},
        "Tanning":    {"flow": 80,  "BOD": 2000, "COD": 5000, "TSS": 3500, "Color": 1200, "TDS": 8000, "Oil": 60, "pH": 11.0},
        "Pulp_Paper": {"flow": 400, "BOD": 800,  "COD": 2500, "TSS": 2200, "Color": 3000, "TDS": 1500, "Oil": 15, "pH": 8.0},
        "Dairy":      {"flow": 150, "BOD": 1500, "COD": 3000, "TSS": 800,  "Color": 50,   "TDS": 1200, "Oil": 450, "pH": 5.5},
        "Sugar":      {"flow": 300, "BOD": 1000, "COD": 2200, "TSS": 1200, "Color": 400,  "TDS": 1600, "Oil": 20,  "pH": 4.5},
        "Distillery": {"flow": 50,  "BOD": 45000, "COD": 95000, "TSS": 8000, "Color": 15000, "TDS": 12000, "Oil": 30, "pH": 4.0},
        "Brewery":    {"flow": 250, "BOD": 1800, "COD": 3500, "TSS": 600,  "Color": 400,  "TDS": 1500, "Oil": 15, "pH": 6.0}
    }

    influent = FACTORY_INFLUENT_DATABASE[CHOSEN_INDUSTRY]

    print("\nRaw Influent Wastewater Design Loading:")
    print("-" * 55)
    for k, v in influent.items():
        unit_label = "m³/day" if k == "flow" else ("Pt-Co" if k == "Color" else ("SU" if k == "pH" else "mg/L"))
        print(f"  🔹 {k:6} : {v:<7} {unit_label}")

    print("\nExecuting multi-stage combinatorial process optimizations...")
    print("-" * 55)

    optimizer = WWTPOptimizer()
    simulator = ProcessSimulator()
    sizer = StructuralSizer()

    # --- CONDITIONAL CONSTRAINT ROUTING ---
    if NO_LIMIT_MODE:
        LAND_CAP, CAPEX_CAP, OPEX_CAP = None, None, None
    else:
        LAND_CAP = max(150.0, influent["flow"] * 2.0)
        CAPEX_CAP = max(3500000.0, influent["flow"] * 45000.0)
        OPEX_CAP = max(4000000.0, influent["flow"] * 30000.0)

    optimization_package = optimizer.optimize(
        influent,
        land_available=LAND_CAP,
        capex_limit=CAPEX_CAP,
        opex_limit=OPEX_CAP,
        verbose=False
    )
    
    if optimization_package is None or len(optimization_package["feasible"]) == 0:
        fallbacks = optimization_package.get("fallbacks", []) if optimization_package else []
        if len(fallbacks) > 0:
            best_solution = fallbacks[0]
            print(f"\n⚠️ WARNING: NO FULLY COMPLIANT SOLUTION FOUND UNDER THESE BUDGET RULES.")
            print(f"   Target Attainment Efficiency: {best_solution['attainment_efficiency']:.2f}% of discharge laws met.")
            print("=" * 90)
        else:
            print("\n❌ CRITICAL ERROR: No train options fit within these limits or can be compiled.")
            return
    else:
        best_solution = optimization_package["feasible"][0]
        print("\n⚡ OPTIMAL FEASIBLE ENGINEERING SOLUTION FOUND (100% LEGAL COMPLIANCE)")
        print("=" * 90)

    # ==================================================================
    # 🧮 INTERCEPT AND RUN DYNAMIC POST-SLUDGE DEWATERING INJECTIONS
    # ==================================================================
    raw_liquid_sludge_kg_day = best_solution["sludge_kg_day"]
    
    # Initialize variables for sludge add-ons
    sludge_unit_name = None
    sludge_design_data = {}
    sludge_capex = 0.0
    sludge_opex = 0.0
    sludge_land = 0.0
    sludge_energy = 0.0
    final_disposed_sludge_mass = raw_liquid_sludge_kg_day

    if SLUDGE_TREATMENT_ENABLED and raw_liquid_sludge_kg_day > 0:
        if SLUDGE_TREATMENT_METHOD == "Mechanical":
            sludge_unit_name = "Filter_Press"
            sludge_processor = FilterPress(raw_liquid_sludge_kg_day)
            sludge_design_data = sludge_processor.design()
        else:
            sludge_unit_name = "Sludge_Drying_Bed"
            sludge_processor = SludgeDryingBed(raw_liquid_sludge_kg_day)
            sludge_design_data = sludge_processor.design()
            
        # Extract additions
        sludge_capex = sludge_design_data["capex_npr"]
        sludge_opex = sludge_design_data["opex_npr_year"]
        sludge_land = sludge_design_data["land_m2"]
        sludge_energy = sludge_design_data["energy_kwh_day"]
        final_disposed_sludge_mass = sludge_design_data["sludge_kg_day"]

    # Compute compiled consolidated framework metrics
    compiled_capex = best_solution["capex_npr"] + sludge_capex
    compiled_opex = best_solution["opex_npr_year"] + sludge_opex
    compiled_land = best_solution["land_m2"] + sludge_land
    compiled_energy = best_solution["energy_kwh_day"] + sludge_energy

    print("Recommended Process Train Blueprint Sequence:")
    print("   " + " ──► ".join(best_solution["train"]))
    if SLUDGE_TREATMENT_ENABLED and raw_liquid_sludge_kg_day > 0:
        print(f"   [Sludge Handling Sub-Loop Active] ──► Solid Dewatering via {sludge_unit_name}")

    print(f"\n💸 Financial & Sizing Resource Aggregations (Water Train + Sludge Sub-System):")
    
    # Render unconstrained strings properly if limits are bypassed
    capex_lim_str = "Unlimited" if LAND_CAP is None else f"NPR {CAPEX_CAP:,.0f}"
    opex_lim_str = "Unlimited" if LAND_CAP is None else f"NPR {OPEX_CAP:,.0f}/year"
    land_lim_str = "Unlimited" if LAND_CAP is None else f"{LAND_CAP:.2f} m²"

    print(f"   🔸 Consolidated CAPEX : NPR {compiled_capex:,.0f} (Base WWTP: NPR {best_solution['capex_npr']:,.0f}, Dewatering: NPR {sludge_capex:,.0f}) [Limit: {capex_lim_str}]")
    print(f"   🔸 Consolidated OPEX  : NPR {compiled_opex:,.0f}/year [Limit: {opex_lim_str}]")
    print(f"   🔸 Total Land Footprint: {compiled_land:.2f} m² (Base WWTP: {best_solution['land_m2']:.2f} m², Dewatering: {sludge_land:.2f} m²) [Limit: {land_lim_str}]")
    print(f"   🔸 Combined Power Load : {compiled_energy:.2f} kWh/day")
    print(f"   🔸 Raw Sludge Gen Rate : {raw_liquid_sludge_kg_day:.2f} kg/day (Liquid Mud form)")
    print(f"   🔸 Disposed Solid Mass : {final_disposed_sludge_mass:.2f} kg/day (Dewatered Cake form)")

    # If it is running in fallback due to financial caps, report the failures
    if "constraint_result" in best_solution and not best_solution["constraint_result"]["feasible"]:
        print(f"\n❌ Regulatory Violations Flagged by Constraint Checker:")
        for reason in best_solution["constraint_result"]["reasons"]:
            print(f"   ⚠️ Violation -> {reason}")

    print("\nFinal Effluent Water Quality Design Parameters:")
    print("-" * 55)
    for k, v in best_solution["effluent"].items():
        if k == "flow":
            print(f"   ✔️ {k:11} : {round(v,2):<7} m³/day")
        elif k == "Color":
            print(f"   ✔️ {k:11} : {round(v,2):<7} Pt-Co scale")
        elif k == "pH":
            print(f"   ✔️ {k:11} : {round(v,2):<7} SU")
        elif isinstance(v, (int, float)):
            print(f"   ✔️ {k:11} : {round(v,2):<7} mg/L")

    # =====================================================
    # PHYSICAL SIZING DIMENSION METRIC SECTION
    # =====================================================
    print("\n" + "=" * 90)
    print("CIVIL STRUCTURAL ELEMENT SIZING & GEOMETRIC MATRICES")
    print("=" * 90)

    detailed_run = simulator.simulate_train(best_solution["train"], influent)

    # 1. Size standard water processing unit nodes
    for index, step in enumerate(detailed_run["history"], start=1):
        unit_name = step["unit"]
        unit_class = simulator.run_unit(unit_name, step["influent"])
        sizing_report = sizer.size_unit(unit_name, unit_class)

        print(f"\n [{index}] Unit Process Node: {unit_name}")
        print(f"     Geometry Classification: {sizing_report['geometry']}")
        
        if isinstance(sizing_report["dimensions"], dict):
            for dim_key, dim_val in sizing_report["dimensions"].items():
                print(f"       📌 {dim_key:35} : {dim_val}")
        else:
            print(f"       📌 Operational Notes                 : {sizing_report['dimensions']}")

    # =====================================================
    # PHYSICAL SIZING DIMENSION METRIC SECTION (CONTINUED)
    # =====================================================
    
    # 2. Size the sludge dewatering hardware dynamically if switched on
    if SLUDGE_TREATMENT_ENABLED and raw_liquid_sludge_kg_day > 0:
        print(f"\n [{len(detailed_run['history']) + 1}] Sludge Dewatering Node: {sludge_unit_name}")
        
        # Nested safely inside the activation wrapper to prevent crashing when disabled
        if SLUDGE_TREATMENT_METHOD == "Mechanical":
            print(f"     Geometry Classification: Automated Recessed Chamber Filter Press Assembly")
            print(f"       📌 Number of Squeeze Chambers       : {sludge_design_data['design']['chambers_count']}")
            print(f"       📌 Total Coated Plate Count         : {sludge_design_data['design']['plates_count']}")
            print(f"       📌 Water Extracted from Sludge      : {sludge_design_data['design']['filtrate_water_removed_m3_day']:.2f} m³/day")
            print(f"       📌 Footprint Allocation Area        : 15.0 m²")
        else:
            print(f"     Geometry Classification: Multi-Cell Shallow Open Civil Drying Beds Bed")
            print(f"       📌 Number of Parallel Drying Cells  : {sludge_design_data['design']['number_of_beds']}")
            print(f"       📌 Individual Bed Cell Length       : {sludge_design_data['design']['cell_length_m']} m")
            print(f"       📌 Individual Bed Cell Width        : {sludge_design_data['design']['cell_width_m']} m")
            print(f"       📌 Total Surface Drying Surface Area : {sludge_design_data['design']['total_surface_area_m2']} m²")

    print("\n" + "=" * 90)
    print("COMPUTATIONAL PROCESS FLOW ENGINEERING RUN PASSED SUCCESSFULY")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
