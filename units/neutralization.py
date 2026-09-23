"""
Neutralization Tank

Functions
---------
1. pH correction
2. Acid dosing
3. Alkali dosing
4. Mixing energy estimation
5. Chemical consumption estimation
6. CAPEX estimation
7. OPEX estimation

Standard Interface:
    unit = Neutralization(flow_m3_day)
    result = unit.design(influent)
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class Neutralization:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["Neutralization"]

    # =====================================================
    # TARGET PH
    # =====================================================

    def target_ph(self):

        return self.criteria["target_ph"]

    # =====================================================
    # VOLUME
    # =====================================================

    def calculate_volume(self):

        hrt_hr = self.criteria["hrt_hr"]

        volume = (
            self.flow
            * hrt_hr
            / 24
        )

        return volume

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        volume = self.calculate_volume()

        depth = self.criteria["depth_m"]

        area = volume / depth

        return area * 1.5

    # =====================================================
    # CHEMICAL REQUIREMENT
    # =====================================================

    def calculate_chemical_requirement(
        self,
        influent
    ):

        ph = influent.get("pH", 7)

        target = self.target_ph()

        delta = abs(ph - target)

        dose_kg_m3 = delta * 0.20

        chemical_kg_day = (
            dose_kg_m3
            * self.flow
        )

        # Fix: Sync chemical strings to exact ECONOMICS["chemicals"] dictionary keys
        if ph > target:

            chemical = "Sulfuric_Acid"

        elif ph < target:

            chemical = "Caustic"

        else:

            chemical = None

            chemical_kg_day = 0

        return {

            "chemical": chemical,

            "dose_kg_day": chemical_kg_day

        }

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(self):

        volume = self.calculate_volume()

        mixing_power = (
            self.criteria["mixing_power_kw_m3"]
        )

        power_kw = (
            volume
            * mixing_power
        )

        return power_kw * 24

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        volume = self.calculate_volume()

        # Fix: Route asset rates dynamically through centralized global economics definitions
        civil_tank_rate = ECONOMICS["civil_costs"]["rcc_tank"]

        civil = (
            volume
            * civil_tank_rate
        )

        # Fix: Scale mixer hardware system dynamically using the mixer_kw rate benchmark
        mixer_kw = volume * self.criteria["mixing_power_kw_m3"]
        mixer = mixer_kw * ECONOMICS["equipment_costs"]["mixer_kw"]

        # Fix: Scale dosing system pump infrastructure dynamically using pump_kw index 
        dosing_system = 2 * ECONOMICS["equipment_costs"]["pump_kw"]

        return (
            civil
            + mixer
            + dosing_system
        )

    # =====================================================
    # OPEX
    # =====================================================

    def calculate_opex(
        self,
        influent
    ):

        energy = self.calculate_energy()

        tariff = (
            ECONOMICS["electricity_tariff"]
            ["industrial"]
        )

        electricity_cost = (
            energy
            * tariff
            * 365
        )

        chemical_data = (
            self.calculate_chemical_requirement(
                influent
            )
        )

        chemical_cost = 0

        chem = chemical_data["chemical"]

        if chem:

            # Fix: Pull pricing directly without arbitrary hardcoded fallbacks
            unit_price = ECONOMICS["chemicals"][chem]

            chemical_cost = (
                chemical_data["dose_kg_day"]
                * unit_price
                * 365
            )

        maintenance = (
            self.calculate_capex()
            * ECONOMICS["maintenance_factor"]
        )

        return (
            electricity_cost
            + chemical_cost
            + maintenance
        )

    # =====================================================
    # EFFLUENT
    # =====================================================

    def calculate_effluent(
        self,
        influent
    ):

        effluent = influent.copy()

        effluent["pH"] = (
            self.target_ph()
        )

        return effluent

    # =====================================================
    # DESIGN
    # =====================================================

    def design(
        self,
        influent
    ):

        # Guard: Guarantee process scope scales correctly to active fluid volume parameter boundaries
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        chemical_data = (
            self.calculate_chemical_requirement(
                influent
            )
        )

        chemicals = {}

        if chemical_data["chemical"]:

            chemicals[
                chemical_data["chemical"]
            ] = chemical_data["dose_kg_day"]

        return {

            "unit":
                "Neutralization",

            "influent":
                influent,

            "effluent":
                self.calculate_effluent(
                    influent
                ),

            "land_m2":
                self.calculate_land(),

            "energy_kwh_day":
                self.calculate_energy(),

            "sludge_kg_day":
                0,

            "capex_npr":
                self.calculate_capex(),

            "opex_npr_year":
                self.calculate_opex(
                    influent
                ),

            "chemicals":
                chemicals,

            "design": {

                "volume_m3":
                    self.calculate_volume(),

                "target_ph":
                    self.target_ph(),

                "chemical":
                    chemical_data["chemical"],

                "chemical_kg_day":
                    chemical_data["dose_kg_day"]

            }

        }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 1000,
        "COD": 2500,
        "TSS": 1200,
        "Color": 2000,
        "TDS": 1800,
        "Oil": 50,
        "pH": 10.5

    }

    unit = Neutralization(100)

    result = unit.design(
        influent
    )

    print("\n========== Neutralization Tank Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
