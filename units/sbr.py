"""
Sequencing Batch Reactor (SBR)

Functions
---------
1. BOD removal
2. COD removal
3. TSS removal
4. Reactor sizing
5. Sludge generation
6. Energy estimation
7. CAPEX estimation
8. OPEX estimation
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class SBR:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["SBR"]

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

        return {

            "BOD":
                influent.get("BOD", 0)
                * (1 - self.criteria["bod_removal"]),

            "COD":
                influent.get("COD", 0)
                * (1 - self.criteria["cod_removal"]),

            "TSS":
                influent.get("TSS", 0)
                * (1 - self.criteria["tss_removal"]),

            "Color":
                influent.get("Color", 0)
                * (1 - self.criteria["color_removal"])

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

        return (
            bod_removed_kg_day
            * self.criteria["yield_factor"]
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

        aeration = (
            bod_removed_kg_day
            * self.criteria["aeration_kwh_per_kg_bod"]
        )

        mixing = (
            self.criteria["mixing_kw"]
            * 24
        )

        return aeration + mixing

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        volume = self.calculate_volume()

        # Fix: Route structural rates dynamically through global ECONOMICS civil registry
        civil_tank_rate = ECONOMICS["civil_costs"]["rcc_tank"]
        civil_cost = (
            volume
            * civil_tank_rate
        )

        # Fix: Scale automated decanters, valves, and diffusers dynamically using cost indices
        aeration_hardware = volume * ECONOMICS["equipment_costs"]["diffuser_point"] * 0.4
        decant_valves = volume * ECONOMICS["equipment_costs"]["blower_kw"] * 0.05
        equipment_cost = aeration_hardware + decant_valves

        return (
            civil_cost
            + equipment_cost
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

        # Fix: Account for the annual hauling and treatment costs of generated WAS bio-solids
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

        effluent.update(
            self.calculate_removals(
                influent
            )
        )

        return effluent

    # =====================================================
    # DESIGN
    # =====================================================

    def design(
        self,
        influent
    ):

        # Guard: Guarantee process boundaries match current routing configurations
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "SBR",

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
        "Color": 2500

    }

    unit = SBR(100)

    result = unit.design(influent)

    print("\n========== SBR Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
