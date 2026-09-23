"""
Sludge Drying Bed Module

Functions
---------
1. Dewaters liquid sludge using natural sand/gravel percolation and solar evaporation.
2. Squeezes moisture out naturally, achieving a solid cake concentration of 30%.
3. Calculates the total drying area footprint and modular bed cell divisions.
4. Estimates low civil construction CAPEX and annual cake hauling OPEX.
"""

import math
from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class SludgeDryingBed:

    def __init__(self, liquid_sludge_kg_day):
        # Prevent division errors, establish a baseline mass feed
        self.sludge_load = max(liquid_sludge_kg_day, 0.1)
        
        # Pull performance assumptions from database matrix fallback blocks
        self.criteria = DESIGN_CRITERIA.get("Sludge_Drying_Bed", {
            "feed_solids_fraction": 0.03,      # 3% solids in raw liquid sludge feed
            "cake_solids_fraction": 0.30,      # 30% solids achieved in dried sludge cake
            "solids_loading_kg_m2_year": 120.0, # Sizing index: annual dry solid mass per m²
            "cleaning_cycle_days": 15.0,       # Days bed is occupied before manual cake scraping
            "depth_m": 0.3                     # Height of applied liquid sludge layer
        })

    def calculate_cake_mass(self):
        """
        Mass Balance: Solids in = Solids out.
        """
        dry_solid_mass = self.sludge_load * self.criteria["feed_solids_fraction"]
        dewatered_cake_kg_day = dry_solid_mass / self.criteria["cake_solids_fraction"]
        return dewatered_cake_kg_day

    def calculate_area_and_land(self):
        """
        Sizes total open-surface drying area footprint according to solid loading indices.
        """
        dry_solids_per_day = self.sludge_load * self.criteria["feed_solids_fraction"]
        dry_solids_annual = dry_solids_per_day * 365.0
        
        # Area = Total annual solids load / allowable loading rate per m² per year
        required_surface_area = dry_solids_annual / self.criteria["solids_loading_kg_m2_year"]
        
        # Add a 20% spatial allowance factor for access paths and piping headers
        total_land_footprint = required_surface_area * 1.2
        return required_surface_area, total_land_footprint

    def calculate_bed_configuration(self):
        surface_area, _ = self.calculate_area_and_land()
        
        # Standard modular bed cell layout (usually capped at max 50-100 m² per single bed)
        default_cell_area = 40.0
        number_of_beds = max(2, math.ceil(surface_area / default_cell_area))
        
        # Standard width of 4m-5m to allow easy manual shovel cleaning/scraping from the sides
        cell_width = 4.0
        cell_length = (surface_area / number_of_beds) / cell_width
        
        return {
            "number_of_beds": number_of_beds,
            "cell_length_m": round(cell_length, 2),
            "cell_width_m": round(cell_width, 2)
        }

    def calculate_energy(self):
        # Natural gravity and solar evaporation consume exactly zero electricity
        return 0.0

    def calculate_capex(self):
        surface_area, _ = self.calculate_area_and_land()
        
        # Sizing civil concrete walls, brick linings, and underdrain pipe works using wetland base rates
        civil_wetland_rate = ECONOMICS["civil_costs"]["wetland"]
        civil_cost = surface_area * civil_wetland_rate
        
        # Cost of underdrain perforated piping, sand, and support gravel layers
        media_and_piping_cost = surface_area * ECONOMICS["equipment_costs"]["diffuser_point"] * 0.1
        
        return civil_cost + media_and_piping_cost

    def calculate_opex(self):
        # Maintenance factor tracking (manual sand washing, gate valve maintenance, wall patching)
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        
        # Manual labor costs for cake scraping/shoveling (estimated relative to supervisor wages)
        manual_scraping_labor = ECONOMICS["labour"]["supervisor_salary_month"] * 0.15
        
        # Hauling fees applied directly to the final dried solid sludge cake mass matrix
        cake_hauling_mass = self.calculate_cake_mass()
        disposal_rate = ECONOMICS["sludge_disposal"]["total"]
        hauling_cost = cake_hauling_mass * disposal_rate * 365
        
        return maintenance + manual_scraping_labor + hauling_cost

    def design(self):
        surface_area, land_footprint = self.calculate_area_and_land()
        bed_layout = self.calculate_bed_configuration()
        cake_mass = self.calculate_cake_mass()
        
        return {
            "unit": "Sludge_Drying_Bed",
            "land_m2": land_footprint,
            "energy_kwh_day": self.calculate_energy(),
            "sludge_kg_day": cake_mass,
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(),
            "design": {
                "number_of_beds": bed_layout["number_of_beds"],
                "cell_length_m": bed_layout["cell_length_m"],
                "cell_width_m": bed_layout["cell_width_m"],
                "total_surface_area_m2": round(surface_area, 2),
                "liquid_feed_kg_day": round(self.sludge_load, 2),
                "cake_dry_mass_kg_day": round(cake_mass, 2)
            }
        }


if __name__ == "__main__":
    # Test execution using the identical wet sludge output weight from your recent textile run
    bed = SludgeDryingBed(liquid_sludge_kg_day=396.15)
    result = bed.design()
    print("\n========== Sludge Drying Bed Solution ==========\n")
    for k, v in result.items():
        if k != "design":
            print(f"{k}: {v}")
    print("\nCivil Structural Layer Metrics:")
    for k, v in result["design"].items():
        print(f"  🔹 {k}: {v}")
