"""
Dissolved Air Flotation (DAF) Module

Functions
---------
1. Highly efficient oil, grease, and light floating fat removal.
2. Moderate TSS/COD polishing.
3. Air saturator energy and compressor sizing.
4. Centralized CAPEX and OPEX mapping.
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class DAF:

    def __init__(self, flow_m3_day):
        self.flow = max(flow_m3_day, 1)
        self.criteria = DESIGN_CRITERIA.get("DAF", {
            "loading_rate_m3_m2_hr": 5.0,
            "depth_m": 2.5,
            "air_to_solids_ratio": 0.02,
            "compressor_power_kw": 2.2,
            "oil_removal": 0.92,
            "tss_removal": 0.60,
            "cod_removal": 0.25,
            "bod_removal": 0.20
        })

    def calculate_surface_area(self):
        hourly_flow = self.flow / 24.0
        return hourly_flow / self.criteria["loading_rate_m3_m2_hr"]

    def calculate_volume(self):
        return self.calculate_surface_area() * self.criteria["depth_m"]

    def calculate_land(self):
        return self.calculate_surface_area() * 1.6

    def calculate_removals(self, influent):
        return {
            "Oil": influent.get("Oil", 0) * (1 - self.criteria["oil_removal"]),
            "TSS": influent.get("TSS", 0) * (1 - self.criteria["tss_removal"]),
            "COD": influent.get("COD", 0) * (1 - self.criteria["cod_removal"]),
            "BOD": influent.get("BOD", 0) * (1 - self.criteria["bod_removal"])
        }

    def calculate_sludge(self, influent):
        # Scum/Sludge scraped from top and bottom
        removals = self.calculate_removals(influent)
        tss_removed_kg = (influent.get("TSS", 0) - removals["TSS"]) * self.flow / 1000
        oil_removed_kg = (influent.get("Oil", 0) - removals["Oil"]) * self.flow / 1000
        return tss_removed_kg + oil_removed_kg

    def calculate_energy(self):
        # Recycle pump + air compressor run 24/7
        return self.criteria["compressor_power_kw"] * 24

    def calculate_capex(self):
        volume = self.calculate_volume()
        civil = volume * ECONOMICS["civil_costs"]["rcc_tank"]
        # Mechanized scraper + saturation vessel bundle costs scaled off blowers
        equipment = ECONOMICS["equipment_costs"]["blower_kw"] * 1.2
        return civil + equipment

    def calculate_opex(self, influent):
        electricity = self.calculate_energy() * ECONOMICS["electricity_tariff"]["industrial"] * 365
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        sludge_cost = self.calculate_sludge(influent) * ECONOMICS["sludge_disposal"]["total"] * 365
        return electricity + maintenance + sludge_cost

    def calculate_effluent(self, influent):
        effluent = influent.copy()
        effluent.update(self.calculate_removals(influent))
        return effluent

    def design(self, influent):
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)
        return {
            "unit": "DAF",
            "influent": influent,
            "effluent": self.calculate_effluent(influent),
            "land_m2": self.calculate_land(),
            "energy_kwh_day": self.calculate_energy(),
            "sludge_kg_day": self.calculate_sludge(influent),
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(influent),
            "chemicals": {},
            "design": {
                "surface_area_m2": self.calculate_surface_area(),
                "volume_m3": self.calculate_volume()
            }
        }
