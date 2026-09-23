"""
Activated Sludge Process (ASP)

Functions
---------
1. BOD removal
2. COD removal
3. TSS removal
4. Aeration tank sizing
5. Sludge generation
6. Energy estimation
7. CAPEX estimation
8. OPEX estimation

Standard Interface:
    unit = ASP(flow_m3_day)
    result = unit.design(influent)
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class ASP:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["ASP"]

    # =====================================================
    # VOLUME
    # =====================================================

    def calculate_volume(self):

        hrt_hr = self.criteria["hrt_hr"]

        return (
            self.flow
            * hrt_hr
            / 24
        )

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        volume = self.calculate_volume()

        depth = self.criteria["depth_m"]

        area = volume / depth

        return area * 1.8

    # =====================================================
    # REMOVALS
    # =====================================================

    def calculate_removals(
        self,
        influent
    ):

        bod_in = influent.get("BOD", 0)
        cod_in = influent.get("COD", 0)
        tss_in = influent.get("TSS", 0)
        color_in = influent.get("Color", 0)

        bod_removal = self.criteria["bod_removal"]
        cod_removal = self.criteria["cod_removal"]
        tss_removal = self.criteria["tss_removal"]
        color_removal = self.criteria["color_removal"]

        return {

            "BOD":
                bod_in * (1 - bod_removal),

            "COD":
                cod_in * (1 - cod_removal),

            "TSS":
                tss_in * (1 - tss_removal),

            "Color":
                color_in * (1 - color_removal)

        }

    # =====================================================
    # SLUDGE
    # =====================================================

    def calculate_sludge(
        self,
        influent
    ):

        bod_removed = (
            influent.get("BOD", 0)
            -
            self.calculate_removals(
                influent
            )["BOD"]
        )

        bod_removed_kg_day = (
            bod_removed
            * self.flow
            / 1000
        )

        yield_factor = (
            self.criteria["yield_factor"]
        )

        return (
            bod_removed_kg_day
            * yield_factor
        )

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(
        self,
        influent
    ):

        bod_removed = (
            influent.get("BOD", 0)
            -
            self.calculate_removals(
                influent
            )["BOD"]
        )

        bod_removed_kg_day = (
            bod_removed
            * self.flow
            / 1000
        )

        aeration_energy = (
            bod_removed_kg_day
            * self.criteria["aeration_kwh_per_kg_bod"]
        )

        pumping_energy = (
            self.criteria["pump_kw"]
            * 24
        )

        return (
            aeration_energy
            + pumping_energy
        )

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        volume = self.calculate_volume()

        # Fix: Route construction rates through central ECONOMICS database
        civil_tank_rate = ECONOMICS["civil_costs"]["rcc_tank"]
        civil_clarifier_rate = ECONOMICS["civil_costs"]["clarifier"]

        civil = (
            volume
            * civil_tank_rate
        )

        # Aeration engineering hardware cost benchmarks scaled from equipment indicators
        aeration_system = volume * ECONOMICS["equipment_costs"]["diffuser_point"] * 0.5

        # Secondary settling tank scales with volumetric space constraints
        clarifier = (volume * 0.35) * civil_clarifier_rate

        return (
            civil
            + aeration_system
            + clarifier
        )

    # =====================================================
    # OPEX
    # =====================================================

    def calculate_opex(
        self,
        influent
    ):

        tariff = (
            ECONOMICS["electricity_tariff"]
            ["industrial"]
        )

        electricity = (
            self.calculate_energy(
                influent
            )
            * tariff
            * 365
        )

        maintenance = (
            self.calculate_capex()
            * ECONOMICS["maintenance_factor"]
        )

        # Fix: Pull nested sludge disposal total cost and multiply annually
        sludge_kg_day = self.calculate_sludge(influent)
        sludge_rate = ECONOMICS["sludge_disposal"]["total"]
        sludge_disposal_cost = sludge_kg_day * sludge_rate * 365

        return (
            electricity
            + maintenance
            + sludge_disposal_cost
        )

    # =====================================================
    # EFFLUENT
    # =====================================================

    def calculate_effluent(
        self,
        influent
    ):

        effluent = influent.copy()

        removals = (
            self.calculate_removals(
                influent
            )
        )

        effluent.update(
            removals
        )

        return effluent

    # =====================================================
    # DESIGN
    # =====================================================

    def design(
        self,
        influent
    ):

        # Guard: Ensure current execution instance operates on actual input stream boundaries
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "ASP",

            "influent":
                influent,

            "effluent":
                self.calculate_effluent(
                    influent
                ),

            "land_m2":
                self.calculate_land(),

            "energy_kwh_day":
                self.calculate_energy(
                    influent
                ),

            "sludge_kg_day":
                self.calculate_sludge(
                    influent
                ),

            "capex_npr":
                self.calculate_capex(),

            "opex_npr_year":
                self.calculate_opex(
                    influent
                ),

            "chemicals":
                {},

            "design": {

                "volume_m3":
                    self.calculate_volume(),

                "hrt_hr":
                    self.criteria["hrt_hr"]

            }

        }


if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 1200,
        "COD": 3500,
        "TSS": 1500,
        "Color": 2500,
        "TDS": 2200,
        "Oil": 45,
        "pH": 8.5

    }

    unit = ASP(100)

    result = unit.design(
        influent
    )

    print("\n========== ASP Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
