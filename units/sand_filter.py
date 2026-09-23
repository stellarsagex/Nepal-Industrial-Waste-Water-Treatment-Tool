"""
Rapid Sand Filter

Functions
---------
1. TSS removal
2. Color polishing
3. Bed sizing
4. Energy estimation
5. CAPEX estimation
6. OPEX estimation
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class SandFilter:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["Sand_Filter"]

    # =====================================================
    # FILTER AREA
    # =====================================================

    def calculate_area(self):

        filtration_rate = (
            self.criteria["filtration_rate"]
        )

        hourly_flow = (
            self.flow / 24
        )

        return (
            hourly_flow
            / filtration_rate
        )

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        return (
            self.calculate_area()
            * 2.0
        )

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

        tss_removed = (

            influent.get("TSS", 0)

            -

            self.calculate_removals(
                influent
            )["TSS"]

        )

        return (
            tss_removed
            * self.flow
            / 1000
        )

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(
        self,
        influent
    ):

        return (
            self.criteria["pump_kw"]
            * 24
        )

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        area = self.calculate_area()
        depth = self.criteria.get("depth_m", 2.0)
        volume = area * depth

        # Fix: Pull structure cost from centralized ECONOMICS civil blocks
        civil_tank_rate = ECONOMICS["civil_costs"]["rcc_tank"]
        civil = volume * civil_tank_rate

        # Fix: Filter multi-media layers scale dynamically off mechanical equipment metrics
        media = area * ECONOMICS["equipment_costs"]["pump_kw"] * 0.15

        return civil + media

    # =====================================================
    # OPEX
    # =====================================================

    def calculate_opex(
        self,
        influent
    ):

        electricity = (

            self.calculate_energy(
                influent
            )

            *

            ECONOMICS[
                "electricity_tariff"
            ]["industrial"]

            * 365

        )

        maintenance = (

            self.calculate_capex()

            *

            ECONOMICS[
                "maintenance_factor"
            ]

        )

        # Fix: Account for the annual handling/disposal fees of backwash solids mass
        backwash_solids_kg_day = self.calculate_sludge(influent)
        sludge_rate = ECONOMICS["sludge_disposal"]["total"]
        disposal_cost = backwash_solids_kg_day * sludge_rate * 365

        return (
            electricity
            + maintenance
            + disposal_cost
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

        # Guard: Synchronize tracking flow to active processing payload
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "Sand Filter",

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

                "filter_area_m2":
                    self.calculate_area()

            }

        }


if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 150,
        "COD": 450,
        "TSS": 120,
        "Color": 600

    }

    unit = SandFilter(100)

    result = unit.design(influent)

    print("\n========== Sand Filter Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
