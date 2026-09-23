"""
Primary Clarifier (Multi-Industry Edition)

Dynamically adapts separation sizing factors and performance indexes based 
on the active Nepalese industrial manufacturing profile context.
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS
from config.standards import INDUSTRIAL_STANDARDS_DATABASE


class PrimaryClarifier:

    def __init__(self, flow_m3_day):
        self.flow = max(flow_m3_day, 1)
        self.criteria = DESIGN_CRITERIA["Primary_Clarifier"]

    def _get_active_industry(self):
        from config.standards import STANDARDS
        for ind_key, dataset in INDUSTRIAL_STANDARDS_DATABASE.items():
            if dataset.get("pH") == STANDARDS.get("pH") and dataset.get("BOD") == STANDARDS.get("BOD"):
                return ind_key
        return "Generic_Surface"

    def calculate_surface_area(self):
        sor = self.criteria["surface_overflow_rate"]
        # Distilleries or paper mills with heavy solids demand more settling area
        industry = self._get_active_industry()
        if industry in ["Distillery", "Pulp_Paper"]:
            sor = sor * 0.8  # Drops overflow rate by 20% to make the tank larger/safer
        return self.flow / sor

    def calculate_volume(self):
        return self.calculate_surface_area() * self.criteria["depth_m"]

    def calculate_land(self):
        return self.calculate_surface_area() * 1.5

    def calculate_removals(self, influent):
        industry = self._get_active_industry()
        
        tss_rem = self.criteria["tss_removal"]
        bod_rem = self.criteria["bod_removal"]
        cod_rem = self.criteria["cod_removal"]
        oil_rem = self.criteria.get("oil_removal", 0.70)

        # Fine-tune primary screening/settling boundaries dynamically
        if industry == "Pulp_Paper":
            tss_rem = max(tss_rem, 0.75)  # Heavy wood fiber primary capture
        elif industry == "Dairy":
            oil_rem = max(oil_rem, 0.75)  # Captures free floating milk fats early
        elif industry == "Distillery":
            tss_rem = max(tss_rem, 0.40)  # Molasses yeast debris is tough to settle primary

        return {
            "TSS": influent.get("TSS", 0) * (1 - tss_rem),
            "BOD": influent.get("BOD", 0) * (1 - bod_rem),
            "COD": influent.get("COD", 0) * (1 - cod_rem),
            "Oil": influent.get("Oil", 0) * (1 - oil_rem)
        }

    def calculate_sludge(self, influent):
        removals = self.calculate_removals(influent)
        return (influent.get("TSS", 0) - removals["TSS"]) * self.flow / 1000

    def calculate_energy(self):
        return self.criteria["scraper_power_kw"] * 24

    def calculate_capex(self):
        volume = self.calculate_volume()
        civil = volume * ECONOMICS["civil_costs"]["clarifier"]
        scraper = volume * ECONOMICS["equipment_costs"]["pump_kw"] * 0.15
        return civil + scraper

    def calculate_opex(self, influent):
        electricity = self.calculate_energy() * ECONOMICS["electricity_tariff"]["industrial"] * 365
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        sludge_cost = self.calculate_sludge(influent) * ECONOMICS["sludge_disposal"]["total"] * 365
        return electricity + maintenance + sludge_cost

    def calculate_effluent(self, influent):
        effluent = influent.copy()
        removals = self.calculate_removals(influent)
        effluent.update(removals)
        return effluent

    def design(self, influent):
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)
        return {
            "unit": "Primary_Clarifier",
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
                "volume_m3": self.calculate_volume(),
                "depth_m": self.criteria["depth_m"]
            }
        }
