"""
OPEX Model

Operational expenditure calculations.

Includes:
    - Electricity
    - Chemicals
    - Sludge disposal
    - Labour
    - Maintenance

All costs returned in NPR/year.
"""

from config.economics import ECONOMICS


class OPEXModel:

    def __init__(self):

        self.energy_cost = 0
        self.chemical_cost = 0
        self.sludge_cost = 0
        self.labour_cost = 0
        self.maintenance_cost = 0

    # =====================================================
    # ELECTRICITY
    # =====================================================

    def add_electricity(
        self,
        energy_kwh_day
    ):

        tariff = ECONOMICS[
            "electricity_tariff"
        ]["industrial"]

        annual_energy = (
            energy_kwh_day
            * 365
        )

        self.energy_cost += (
            annual_energy
            * tariff
        )

    # =====================================================
    # CHEMICALS
    # =====================================================

    def add_chemical(
        self,
        chemical_name,
        kg_day
    ):

        chemical_database = (
            ECONOMICS["chemicals"]
        )

        if chemical_name not in chemical_database:
            return

        unit_price = (
            chemical_database[
                chemical_name
            ]
        )

        self.chemical_cost += (
            kg_day
            * unit_price
            * 365
        )

    # =====================================================
    # SLUDGE
    # =====================================================

    def add_sludge(
        self,
        sludge_kg_day
    ):

        disposal_rate = (
            ECONOMICS[
                "sludge_disposal"
            ]["total"]
        )

        self.sludge_cost += (
            sludge_kg_day
            * disposal_rate
            * 365
        )

    # =====================================================
    # LABOUR
    # =====================================================

    def add_labour(
        self,
        operators=1
    ):

        annual_salary = (
            ECONOMICS[
                "labour"
            ]["operator_salary_month"]
            * 12
        )

        self.labour_cost += (
            operators
            * annual_salary
        )

    # =====================================================
    # MAINTENANCE
    # =====================================================

    def add_maintenance(
        self,
        capex_npr
    ):

        factor = (
            ECONOMICS[
                "maintenance_factor"
            ]
        )

        self.maintenance_cost += (
            capex_npr
            * factor
        )

    # =====================================================
    # TOTAL OPEX
    # =====================================================

    def calculate(
        self,
        flow_m3_day=None
    ):

        total = (

            self.energy_cost
            + self.chemical_cost
            + self.sludge_cost
            + self.labour_cost
            + self.maintenance_cost

        )

        result = {

            "energy_npr_year":
                self.energy_cost,

            "chemicals_npr_year":
                self.chemical_cost,

            "sludge_npr_year":
                self.sludge_cost,

            "labour_npr_year":
                self.labour_cost,

            "maintenance_npr_year":
                self.maintenance_cost,

            "total_opex_npr_year":
                total
        }

        if flow_m3_day and flow_m3_day > 0:

            annual_flow = (
                flow_m3_day
                * 365
            )

            result[
                "opex_npr_m3"
            ] = (

                total
                / annual_flow

            )

        return result

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.energy_cost = 0
        self.chemical_cost = 0
        self.sludge_cost = 0
        self.labour_cost = 0
        self.maintenance_cost = 0


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    opex = OPEXModel()

    opex.add_electricity(
        energy_kwh_day=120
    )

    opex.add_chemical(
        "PAC",
        20
    )

    opex.add_sludge(
        150
    )

    opex.add_labour(
        operators=2
    )

    opex.add_maintenance(
        capex_npr=12000000
    )

    result = opex.calculate(
        flow_m3_day=100
    )

    print("\n========== OPEX ==========\n")

    for k, v in result.items():

        print(
            f"{k}: {round(v,2)}"
        )
