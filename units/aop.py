"""
Advanced Oxidation Process (AOP) Module - Fenton's Reagent

Functions
---------
1. Hydroxyl radical generation for heavy recalcitrant COD and Color destruction.
2. Acidic pH oxidation followed by chemical sludge precipitation.
3. Co-reagent chemical dosing estimation.
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class AOP:

    def __init__(self, flow_m3_day):
        self.flow = max(flow_m3_day, 1)
        self.criteria = DESIGN_CRITERIA.get("AOP", {
            "hrt_hr": 2.0,
            "depth_m": 3.5,
            "h2o2_mg_per_mg_cod": 1.0,
            "feso4_mg_per_mg_cod": 2.0,
            "mixer_kw_m3": 0.012,
            "color_removal": 0.90,
            "cod_removal": 0.75,
            "bod_removal": 0.15
        })

    def calculate_volume(self):
        return self.flow * self.criteria["hrt_hr"] / 24

    def calculate_land(self):
        return (self.calculate_volume() / self.criteria["depth_m"]) * 1.5

    def calculate_chemical_dose(self, influent):
        cod_in = influent.get("COD", 0)
        cod_load_kg = (cod_in * self.flow) / 1000.0

        h2o2_kg_day = cod_load_kg * self.criteria["h2o2_mg_per_mg_cod"]
        feso4_kg_day = cod_load_kg * self.criteria["feso4_mg_per_mg_cod"]

        return {
            "Sulfuric_Acid": h2o2_kg_day * 0.15,  # Fenton's needs initial pH drop to ~3.0
            "Activated_Carbon": 0.0  # Safe dictionary lookup placeholder
        }

    def calculate_removals(self, influent):
        return {
            "Color": influent.get("Color", 0) * (1 - self.criteria["color_removal"]),
            "COD": influent.get("COD", 0) * (1 - self.criteria["cod_removal"]),
            "BOD": influent.get("BOD", 0) * (1 - self.criteria["bod_removal"])
        }

    def calculate_sludge(self, influent):
        # Fenton's iron catalyst precipitates as heavy chemical ferric hydroxide sludge
        cod_in = influent.get("COD", 0)
        cod_load_kg = (cod_in * self.flow) / 1000.0
        feso4_kg_day = cod_load_kg * self.criteria["feso4_mg_per_mg_cod"]
        
        # 1 kg of FeSO4 generates roughly 0.35 kg of iron hydroxide chemical solids
        iron_sludge_kg_day = feso4_kg_day * 0.35
        return iron_sludge_kg_day

    def calculate_energy(self):
        return self.calculate_volume() * self.criteria["mixer_kw_m3"] * 24

    def calculate_capex(self):
        volume = self.calculate_volume()
        civil = volume * ECONOMICS["civil_costs"]["rcc_tank"]
        mixer = (volume * self.criteria["mixer_kw_m3"]) * ECONOMICS["equipment_costs"]["mixer_kw"]
        dosing = ECONOMICS["equipment_costs"]["pump_kw"] * 2.0
        return civil + mixer + dosing

    def calculate_opex(self, influent):
        electricity = self.calculate_energy() * ECONOMICS["electricity_tariff"]["industrial"] * 365
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        
        # Chemical Costs mapping
        cod_in = influent.get("COD", 0)
        cod_load_kg = (cod_in * self.flow) / 1000.0
        h2o2_cost = (cod_load_kg * self.criteria["h2o2_mg_per_mg_cod"]) * ECONOMICS["chemicals"].get("Antiscalant", 250) * 365 # proxy pricing map
        feso4_cost = (cod_load_kg * self.criteria["feso4_mg_per_mg_cod"]) * ECONOMICS["chemicals"].get("Alum", 35) * 365
        
        sludge_cost = self.calculate_sludge(influent) * ECONOMICS["sludge_disposal"]["total"] * 365
        return electricity + maintenance + h2o2_cost + feso4_cost + sludge_cost

    def calculate_effluent(self, influent):
        effluent = influent.copy()
        effluent.update(self.calculate_removals(influent))
        # Downstream neutralization will be forced after AOP to fix pH back to 7.0
        effluent["pH"] = 3.5
        return effluent

    def design(self, influent):
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)
        return {
            "unit": "AOP",
            "influent": influent,
            "effluent": self.calculate_effluent(influent),
            "land_m2": self.calculate_land(),
            "energy_kwh_day": self.calculate_energy(),
            "sludge_kg_day": self.calculate_sludge(influent),
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(influent),
            "chemicals": self.calculate_chemical_dose(influent),
            "design": {
                "volume_m3": self.calculate_volume()
            }
        }
