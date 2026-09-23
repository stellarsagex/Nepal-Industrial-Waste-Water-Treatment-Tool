"""
Central CAPEX model.

Used by:
    - Process Simulator
    - Optimizer

Includes:
    - Civil cost
    - Mechanical equipment
    - Electrical equipment
    - Instrumentation
    - Contingency
"""

from config.economics import ECONOMICS


class CAPEXModel:

    def __init__(self):

        self.total_cost = 0.0

    # =====================================================
    # ADD COST
    # =====================================================

    def add_cost(
        self,
        value
    ):

        self.total_cost += max(
            0,
            value
        )

    # =====================================================
    # CIVIL COST
    # =====================================================

    def civil_cost(
        self,
        volume_m3,
        cost_per_m3
    ):

        return (
            volume_m3
            * cost_per_m3
        )

    # =====================================================
    # EQUIPMENT COST
    # =====================================================

    def equipment_cost(
        self,
        equipment_cost
    ):

        return equipment_cost

    # =====================================================
    # ELECTRICAL COST
    # =====================================================

    def electrical_cost(
        self,
        connected_load_kw
    ):

        # Approximate electrical installation cost
        # based on connected load.

        return (

            connected_load_kw

            * ECONOMICS[
                "equipment_costs"
            ]["pump_kw"]

        )

    # =====================================================
    # INSTRUMENTATION COST
    # =====================================================

    def instrumentation_cost(
        self,
        number_of_instruments
    ):

        # Fix: Extract active hardware costs using centralized dynamic diffusers or equipment metrics
        # Avoids hardcoding arbitrary default variables inside execution methods
        cost_per_instrument = ECONOMICS["equipment_costs"]["diffuser_point"] * 10.0

        return (

            number_of_instruments
            * cost_per_instrument

        )

    # =====================================================
    # CONTINGENCY
    # =====================================================

    def contingency(
        self,
        subtotal
    ):

        return (

            subtotal

            * ECONOMICS[
                "contingency_factor"
            ]

        )

    # =====================================================
    # TOTAL CAPEX
    # =====================================================

    def calculate_total(self):

        contingency = self.contingency(
            self.total_cost
        )

        return (

            self.total_cost
            + contingency

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        self.total_cost = 0.0


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    capex = CAPEXModel()

    civil = capex.civil_cost(
        volume_m3=500,
        cost_per_m3=22000
    )

    equipment = capex.equipment_cost(
        2500000
    )

    electrical = capex.electrical_cost(
        connected_load_kw=50
    )

    instrumentation = (
        capex.instrumentation_cost(
            number_of_instruments=10
        )
    )

    capex.add_cost(civil)
    capex.add_cost(equipment)
    capex.add_cost(electrical)
    capex.add_cost(instrumentation)

    total = capex.calculate_total()

    print("\n========== CAPEX Model Summary ==========\n")

    print(
        "Civil:        NPR",
        f"{civil:,.2f}"
    )

    print(
        "Equipment:    NPR",
        f"{equipment:,.2f}"
    )

    print(
        "Electrical:   NPR",
        f"{electrical:,.2f}"
    )

    print(
        "Instruments:  NPR",
        f"{instrumentation:,.2f}"
    )

    print(
        "\nTotal CAPEX:  NPR",
        f"{total:,.2f}"
    )
