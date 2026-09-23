"""
Natural Sludge Drying Bed Module

Functions
---------
1. Sustainable, zero-power evaporation-driven sludge dewatering bed.
2. Sizing footprints based on solid loading criteria.
3. Zero operational electricity consumption tracking profiles.
"""

import math
from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class SludgeDryingBed:

    def __init__(self, liquid_sludge_kg_day):
        self.sludge_load = max(liquid_sludge_kg_day, 0.1)
        self.criteria = DESIGN_CRITERIA.get("Sludge_Drying_Bed", {
            "solids_loading_kg_m2_year": 120.0, # Sizing index for open drying beds in Nepal climate
            "cake_solids_fraction": 0.30,        # 30% solids achieved via natural evaporation
            "feed_solids_fraction": 0.03
        })

    def calculate_area(self):
        dry_solids_year = (self.sludge_load * self.criteria["feed_solids_fraction"]) * 365.0
        return dry_solids_year / self.criteria["solids_loading_kg_m2_year"]

    def calculate_cake_mass(self):
        dry_solid_mass = self.sludge_load * self.criteria["feed_solids_fraction"]
        return dry_solid_mass / self.criteria["cake_solids_fraction"]

    def calculate_capex(self):
        # High civil spatial footprint area, zero mechanical parts
        area = self.calculate_area()
        # Sludge drying bed civil masonry works scale off the wetland unit cost benchmarks
        return area * ECONOMICS["civil_costs"]["wetland"] * 1.5

    def calculate_opex(self):
        # Zero electricity cost! Only minor labor cake-raking maintenance and hauling fees
        maintenance = self.calculate_capex() * 0.02
        cake_hauling = self.calculate_cake_mass() * ECONOMICS["sludge_disposal"]["total"] * 365
        return maintenance + cake_hauling

    def design(self):
        area = self.calculate_area()
        cake_mass = self.calculate_cake_mass()
        return {
            "unit": "Sludge_Drying_Bed",
            "land_m2": area,               # ⚠️ Notice the massive land requirement compared to a press!
            "energy_kwh_day": 0.0,         # 🌱 Zero power demand
            "sludge_kg_day": cake_mass,
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(),
            "design": {
                "drying_bed_area_m2": round(area, 2),
                "cake_dry_mass_kg_day": round(cake_mass, 2)
            }
        }
