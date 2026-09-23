"""
Coagulation + Flocculation Unit (Multi-Industry Edition)

Dynamically adapts chemical dosage calculations and contaminant removal efficiencies 
based on the active industrial wastewater profile.
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS
from config.standards import INDUSTRIAL_STANDARDS_DATABASE


class Coagulation:

    def __init__(self, flow_m3_day):
        self.flow = max(flow_m3_day, 1)
        self.criteria = DESIGN_CRITERIA["Coagulation"]

    def calculate_volume(self):
        rapid_mix_hr = self.criteria["rapid_mix_hr"]
        floc_hr = self.criteria["flocculation_hr"]
        return self.flow * (rapid_mix_hr + floc_hr) / 24

    def calculate_land(self):
        volume = self.calculate_volume()
        depth = self.criteria["depth_m"]
        return (volume / depth) * 1.8

    def _get_active_industry(self):
        """Infers active industry by cross-referencing global threshold records."""
        from config.standards import STANDARDS
        for ind_key, dataset in INDUSTRIAL_STANDARDS_DATABASE.items():
            if dataset.get("pH") == STANDARDS.get("pH") and dataset.get("BOD") == STANDARDS.get("BOD"):
                return ind_key
        return "Generic_Surface"

    def calculate_chemical_dose(self, influent):
        industry = self._get_active_industry()
        color = influent.get("Color", 0)
        cod = influent.get("COD", 0)
        tss = influent.get("TSS", 0)

        # Profile-specific chemical dosage logic
        if industry == "Textile":
            alum_dose = 50 + 0.02 * color + 0.005 * cod
            polymer_dose = alum_dose * 0.02
        elif industry == "Tanning":
            # Leather wastewater demands heavy lime and alum to trap chrome/sulfides
            alum_dose = 150 + 0.01 * tss
            polymer_dose = alum_dose * 0.03
        elif industry == "Pulp_Paper":
            # Paper mills require massive chemical addition to bind short lignocellulosic fibers
            alum_dose = 200 + 0.03 * color
            polymer_dose = alum_dose * 0.025
        elif industry in ["Dairy", "Sugar"]:
            # Dairy/Sugar use primary coagulation mainly for fat/grease conditioning
            alum_dose = 80 + 0.002 * cod
            polymer_dose = alum_dose * 0.01
        else:
            alum_dose = 100
            polymer_dose = 2

        return {
            "Alum": alum_dose * self.flow / 1000,
            "Polymer": polymer_dose * self.flow / 1000
        }

    def calculate_removals(self, influent):
        industry = self._get_active_industry()
        
        # Primary base criteria constants
        color_rem = self.criteria["color_removal"]
        tss_rem = self.criteria["tss_removal"]
        cod_rem = self.criteria["cod_removal"]
        bod_rem = self.criteria["bod_removal"]
        oil_rem = self.criteria.get("oil_removal", 0.85)

        # Tailor removal efficiencies based on the physical chemistry of the industry
        if industry == "Tanning":
            tss_rem = max(tss_rem, 0.75)  # Chromium/Lime precipitates easily
            oil_rem = max(oil_rem, 0.90)
        elif industry == "Pulp_Paper":
            tss_rem = max(tss_rem, 0.80)  # High fiber removal density
            color_rem = max(color_rem, 0.65)
        elif industry == "Dairy":
            oil_rem = max(oil_rem, 0.92)   # Highly responsive to fat trapping
            cod_rem = max(cod_rem, 0.35)

        return {
            "Color": influent.get("Color", 0) * (1 - color_rem),
            "TSS": influent.get("TSS", 0) * (1 - tss_rem),
            "COD": influent.get("COD", 0) * (1 - cod_rem),
            "BOD": influent.get("BOD", 0) * (1 - bod_rem),
            "Oil": influent.get("Oil", 0) * (1 - oil_rem)
        }

    def calculate_sludge(self, influent):
        removals = self.calculate_removals(influent)
        tss_removed_kg = (influent.get("TSS", 0) - removals["TSS"]) * self.flow / 1000
        chems = self.calculate_chemical_dose(influent)
        return tss_removed_kg + chems["Alum"] + chems["Polymer"]

    def calculate_energy(self):
        volume = self.calculate_volume()
        return volume * (self.criteria["rapid_mix_kw_m3"] + self.criteria["floc_kw_m3"]) * 24

    def calculate_capex(self):
        volume = self.calculate_volume()
        civil = volume * ECONOMICS["civil_costs"]["rcc_tank"]
        mixer_kw = volume * (self.criteria["rapid_mix_kw_m3"] + self.criteria["floc_kw_m3"])
        equipment = mixer_kw * ECONOMICS["equipment_costs"]["mixer_kw"]
        return civil + equipment

    def calculate_opex(self, influent):
        electricity = self.calculate_energy() * ECONOMICS["electricity_tariff"]["industrial"] * 365
        chems = self.calculate_chemical_dose(influent)
        alum_cost = chems["Alum"] * ECONOMICS["chemicals"]["Alum"] * 365
        poly_cost = chems["Polymer"] * ECONOMICS["chemicals"]["Polymer"] * 365
        maintenance = self.calculate_capex() * ECONOMICS["maintenance_factor"]
        sludge_cost = self.calculate_sludge(influent) * ECONOMICS["sludge_disposal"]["total"] * 365
        return electricity + alum_cost + poly_cost + maintenance + sludge_cost

    def calculate_effluent(self, influent):
        effluent = influent.copy()
        effluent.update(self.calculate_removals(influent))
        return effluent

    def design(self, influent):
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)
        chemicals = self.calculate_chemical_dose(influent)
        return {
            "unit": "Coagulation",
            "influent": influent,
            "effluent": self.calculate_effluent(influent),
            "land_m2": self.calculate_land(),
            "energy_kwh_day": self.calculate_energy(),
            "sludge_kg_day": self.calculate_sludge(influent),
            "capex_npr": self.calculate_capex(),
            "opex_npr_year": self.calculate_opex(influent),
            "chemicals": chemicals,
            "design": {
                "volume_m3": self.calculate_volume(),
                "alum_kg_day": chemicals["Alum"],
                "polymer_kg_day": chemicals["Polymer"]
            }
        }
