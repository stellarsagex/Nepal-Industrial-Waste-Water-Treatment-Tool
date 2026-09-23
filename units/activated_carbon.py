"""
Activated Carbon Filter
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class ActivatedCarbon:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["Activated_Carbon"]

    # =====================================================
    # BED VOLUME
    # =====================================================

    def calculate_bed_volume(self):

        ebct_hr = self.criteria["ebct_hr"]

        hourly_flow = self.flow / 24

        return hourly_flow * ebct_hr

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        bed_volume = self.calculate_bed_volume()

        depth = self.criteria["bed_depth_m"]

        area = bed_volume / depth

        return area * 2.0

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
                * (
                    1 -
                    self.criteria["bod_removal"]
                ),

            "COD":
                influent.get("COD", 0)
                * (
                    1 -
                    self.criteria["cod_removal"]
                ),

            "TSS":
                influent.get("TSS", 0)
                * (
                    1 -
                    self.criteria["tss_removal"]
                ),

            "Color":
                influent.get("Color", 0)
                * (
                    1 -
                    self.criteria["color_removal"]
                )

        }

    # =====================================================
    # CARBON CONSUMPTION
    # =====================================================

    def calculate_carbon_usage(
        self,
        influent
    ):

        cod_removed = (

            influent.get("COD", 0)

            -

            self.calculate_removals(
                influent
            )["COD"]

        )

        cod_removed_kg_day = (

            cod_removed
            * self.flow
            / 1000

        )

        adsorption_capacity = (
            self.criteria[
                "adsorption_capacity"
            ]
        )

        return (
            cod_removed_kg_day
            / adsorption_capacity
        )

    # =====================================================
    # SLUDGE
    # =====================================================

    def calculate_sludge(
        self,
        influent
    ):

        return self.calculate_carbon_usage(
            influent
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

        bed_volume = (
            self.calculate_bed_volume()
        )

        # Fix: Route vessel costs dynamically through centralized ECONOMICS 
        # (Using 'rcc_tank' or an equipment-matched cost benchmark)
        vessel_unit_cost = ECONOMICS["civil_costs"]["rcc_tank"]

        vessel_cost = (
            bed_volume
            * vessel_unit_cost
        )

        carbon_inventory = (

            bed_volume

            *

            self.criteria[
                "carbon_density_kg_m3"
            ]

        )

        carbon_cost = (

            carbon_inventory

            *

            ECONOMICS[
                "chemicals"
            ]["Activated_Carbon"]

        )

        return (
            vessel_cost
            + carbon_cost
        )

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

        carbon_cost = (

            self.calculate_carbon_usage(
                influent
            )

            *

            ECONOMICS[
                "chemicals"
            ]["Activated_Carbon"]

            * 365

        )

        maintenance = (

            self.calculate_capex()

            *

            ECONOMICS[
                "maintenance_factor"
            ]

        )

        # Fix: Account for the cost of throwing away the spent saturated carbon sludge
        spent_carbon_kg_day = self.calculate_sludge(influent)
        disposal_rate = ECONOMICS["sludge_disposal"]["total"]
        disposal_cost = spent_carbon_kg_day * disposal_rate * 365

        return (

            electricity

            + carbon_cost

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

        # Guard: Guarantee the processing flow matches the incoming array parameter
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "Activated Carbon",

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

            "chemicals": {

                "Activated_Carbon":

                    self.calculate_carbon_usage(
                        influent
                    )

            },

            "design": {

                "bed_volume_m3":
                    self.calculate_bed_volume()

            }

        }


if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 80,
        "COD": 300,
        "TSS": 30,
        "Color": 500

    }

    unit = ActivatedCarbon(100)

    result = unit.design(influent)
    
    print("\n========== Activated Carbon Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
