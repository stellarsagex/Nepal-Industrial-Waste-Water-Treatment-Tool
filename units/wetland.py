"""
Constructed Wetland

Functions
---------
1. BOD removal
2. COD removal
3. TSS removal
4. Color reduction
5. Wetland area sizing
6. Sludge estimation
7. Energy estimation
8. CAPEX estimation
9. OPEX estimation
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class Wetland:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["Wetland"]

    # =====================================================
    # AREA
    # =====================================================

    def calculate_area(self):

        hydraulic_loading = (
            self.criteria["hydraulic_loading"]
        )

        return (
            self.flow
            / hydraulic_loading
        )

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        return (
            self.calculate_area()
            * 1.2
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
            * 0.15
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

        # Fix: Route layout, excavation, and liner costs through central ECONOMICS registry
        wetland_unit_rate = ECONOMICS["civil_costs"]["wetland"]

        earthwork = area * wetland_unit_rate
        liner = area * wetland_unit_rate * 0.40
        planting = area * wetland_unit_rate * 0.15

        return (
            earthwork
            + liner
            + planting
        )

    # =====================================================
    # OPEX
    # =====================================================

    def calculate_opex(
        self,
        influent
    ):

        tariff = (
            ECONOMICS[
                "electricity_tariff"
            ]["industrial"]
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
            * ECONOMICS[
                "maintenance_factor"
            ]
        )

        # Fix: Account for the annual cleaning and handling costs of accumulated bed solids
        bed_sludge_kg_day = self.calculate_sludge(influent)
        sludge_rate = ECONOMICS["sludge_disposal"]["total"]
        sludge_disposal_cost = bed_sludge_kg_day * sludge_rate * 365

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
                "Wetland",

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

                "area_m2":
                    self.calculate_area()

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

    unit = Wetland(100)

    result = unit.design(influent)

    print("\n========== Constructed Wetland Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
