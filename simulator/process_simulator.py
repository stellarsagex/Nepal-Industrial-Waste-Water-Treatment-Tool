"""
Process Simulator

Runs a treatment train sequentially.
"""

from units.equalization import Equalization
from units.neutralization import Neutralization
from units.coagulation import Coagulation
from units.clarifier import PrimaryClarifier

from units.abr import ABR
from units.uasb import UASB
from units.asp import ASP
from units.mbbr import MBBR
from units.sbr import SBR
from units.wetland import Wetland

from units.sand_filter import SandFilter
from units.activated_carbon import ActivatedCarbon
from units.ro import ReverseOsmosis

from units.daf import DAF
from units.aop import AOP

# =====================================================
# UNIT REGISTRY
# =====================================================

UNIT_REGISTRY = {

    "Equalization": Equalization,

    "Neutralization": Neutralization,

    "Coagulation": Coagulation,

    "Primary_Clarifier": PrimaryClarifier,

    "ABR": ABR,

    "UASB": UASB,

    "ASP": ASP,

    "MBBR": MBBR,

    "SBR": SBR,

    "Wetland": Wetland,

    "Sand_Filter": SandFilter,

    "Activated_Carbon": ActivatedCarbon,

    "RO": ReverseOsmosis,

    "DAF": DAF,

    "AOP": AOP

}


# =====================================================
# PROCESS SIMULATOR
# =====================================================

class ProcessSimulator:

    def __init__(self):

        pass

    # =================================================
    # RUN SINGLE UNIT
    # =================================================

    def run_unit(
        self,
        unit_name,
        wastewater
    ):

        flow = wastewater.get(
            "flow",
            1
        )

        unit_class = UNIT_REGISTRY[
            unit_name
        ]

        unit = unit_class(flow)

        result = unit.design(
            wastewater
        )

        return result

    # =================================================
    # SIMULATE COMPLETE TRAIN
    # =================================================

    def simulate_train(
        self,
        train,
        influent
    ):

        current = influent.copy()

        history = []

        total_land = 0

        total_energy = 0

        total_sludge = 0

        total_capex = 0

        total_opex = 0

        chemicals = {}

        for unit_name in train:

            result = self.run_unit(

                unit_name,

                current

            )

            history.append({

                "unit":
                    unit_name,

                "influent":
                    current.copy(),

                "effluent":
                    result["effluent"].copy()

            })

            current = result[
                "effluent"
            ]

            total_land += result.get(
                "land_m2",
                0
            )

            total_energy += result.get(
                "energy_kwh_day",
                0
            )

            total_sludge += result.get(
                "sludge_kg_day",
                0
            )

            total_capex += result.get(
                "capex_npr",
                0
            )

            total_opex += result.get(
                "opex_npr_year",
                0
            )

            unit_chems = result.get(
                "chemicals",
                {}
            )

            for chem, qty in unit_chems.items():

                chemicals[chem] = (

                    chemicals.get(
                        chem,
                        0
                    )

                    + qty

                )

        return {

            "influent":
                influent,

            "effluent":
                current,

            "history":
                history,

            "land_m2":
                total_land,

            "energy_kwh_day":
                total_energy,

            "sludge_kg_day":
                total_sludge,

            "capex_npr":
                total_capex,

            "opex_npr_year":
                total_opex,

            "chemicals":
                chemicals

        }

    # =================================================
    # REPORT
    # =================================================

    def print_report(
        self,
        result
    ):

        print("\n")

        print("=" * 60)

        print(
            "WWTP SIMULATION REPORT"
        )

        print("=" * 60)

        print("\nFINAL EFFLUENT")

        for key, value in result[
            "effluent"
        ].items():

            # Fix: Guard format boundaries against trailing strings or nested metadata properties
            if isinstance(value, (int, float)):
                print(f"{key}: {round(value, 2)}")
            else:
                print(f"{key}: {value}")

        print("\n")

        print(
            f"Land Required : "
            f"{result['land_m2']:.2f} m²"
        )

        print(
            f"Energy : "
            f"{result['energy_kwh_day']:.2f} kWh/day"
        )

        print(
            f"Sludge : "
            f"{result['sludge_kg_day']:.2f} kg/day"
        )

        print(
            f"CAPEX : NPR "
            f"{result['capex_npr']:,.0f}"
        )

        print(
            f"OPEX : NPR "
            f"{result['opex_npr_year']:,.0f}/year"
        )

        print("\nPROCESS HISTORY")

        for step in result[
            "history"
        ]:

            print(
                f"\n{step['unit']}"
            )

            print(
                f"BOD In  : "
                f"{step['influent'].get('BOD',0):.1f}"
            )

            print(
                f"BOD Out : "
                f"{step['effluent'].get('BOD',0):.1f}"
            )


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    influent = {

        "flow": 100,

        "BOD": 1200,

        "COD": 3500,

        "TSS": 1800,

        "Color": 2500,

        "TDS": 2200,

        "Oil": 45,

        "pH": 9.5

    }

    train = [

        "Equalization",

        "Neutralization",

        "Coagulation",

        "Primary_Clarifier",

        "MBBR",

        "Sand_Filter",

        "Activated_Carbon"

    ]

    simulator = ProcessSimulator()

    result = simulator.simulate_train(

        train,

        influent

    )

    simulator.print_report(
        result
    )
