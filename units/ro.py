"""
Reverse Osmosis (RO)

Functions
---------
1. TDS removal
2. COD polishing
3. Color removal
4. Permeate production
5. Reject generation
6. Energy estimation
7. CAPEX estimation
8. OPEX estimation
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class ReverseOsmosis:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["RO"]

    # =====================================================
    # PERMEATE / REJECT FLOWS
    # =====================================================

    def calculate_permeate_flow(self):

        recovery = self.criteria["recovery"]

        return self.flow * recovery

    def calculate_reject_flow(self):

        return (
            self.flow
            - self.calculate_permeate_flow()
        )

    # =====================================================
    # MEMBRANE AREA
    # =====================================================

    def calculate_membrane_area(self):

        flux = self.criteria["flux_lmh"]

        permeate_lph = (
            self.calculate_permeate_flow()
            * 1000
            / 24
        )

        return (
            permeate_lph
            / flux
        )

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        membrane_area = (
            self.calculate_membrane_area()
        )

        return membrane_area * 0.20

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
                *
                (
                    1
                    - self.criteria["bod_removal"]
                ),

            "COD":
                influent.get("COD", 0)
                *
                (
                    1
                    - self.criteria["cod_removal"]
                ),

            "TSS":
                influent.get("TSS", 0)
                *
                (
                    1
                    - self.criteria["tss_removal"]
                ),

            "Color":
                influent.get("Color", 0)
                *
                (
                    1
                    - self.criteria["color_removal"]
                ),

            "TDS":
                influent.get("TDS", 0)
                *
                (
                    1
                    - self.criteria["tds_removal"]
                )

        }

    # =====================================================
    # SLUDGE (DRY MASS GENERATION)
    # =====================================================

    def calculate_sludge(
        self,
        influent
    ):
        # Fix: Convert the liquid brine concentrations into actual dry solid/salt mass (kg/day)
        tds_in = influent.get("TDS", 0)
        tds_out = self.calculate_removals(influent)["TDS"]
        
        # Mass balance = (mg/L removed * m3/day flow) / 1000 to convert to kg/day
        tds_removed_kg_day = ((tds_in - tds_out) * self.flow) / 1000
        return tds_removed_kg_day

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(
        self,
        influent
    ):

        specific_energy = (
            self.criteria[
                "specific_energy_kwh_m3"
            ]
        )

        return (
            self.calculate_permeate_flow()
            * specific_energy
        )

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        membrane_area = (
            self.calculate_membrane_area()
        )

        # Fix: Reference dynamic cost metrics out of global ECONOMICS definitions
        # Membrane replacement modules scale off hardware benchmark indices (e.g. pump_kw)
        membrane_cost = (
            membrane_area
            * ECONOMICS["equipment_costs"]["pump_kw"]
            * 0.08
        )

        # High pressure feed pump skids and controls scale off structural tank volumes
        skid_cost = (self.flow * 0.5) * ECONOMICS["civil_costs"]["rcc_tank"]

        return (
            membrane_cost
            + skid_cost
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

        membrane_replacement = (

            self.calculate_capex()

            * 0.10

        )

        maintenance = (

            self.calculate_capex()

            *

            ECONOMICS[
                "maintenance_factor"
            ]

        )

        # Fix: Account for the annual handling and crystallization/disposal costs of reject salts
        reject_salt_kg_day = self.calculate_sludge(influent)
        disposal_rate = ECONOMICS["sludge_disposal"]["total"]
        disposal_cost = reject_salt_kg_day * disposal_rate * 365

        return (

            electricity

            + membrane_replacement

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

        effluent["flow"] = (
            self.calculate_permeate_flow()
        )

        return effluent

    # =====================================================
    # DESIGN
    # =====================================================

    def design(
        self,
        influent
    ):

        # Guard: Guarantee process boundaries match current routing parameters
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "RO",

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

                "membrane_area_m2":
                    self.calculate_membrane_area(),

                "permeate_flow_m3_day":
                    self.calculate_permeate_flow(),

                "reject_flow_m3_day":
                    self.calculate_reject_flow()

            }

        }


if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 50,
        "COD": 250,
        "TSS": 20,
        "Color": 400,
        "TDS": 2500

    }

    unit = ReverseOsmosis(100)

    result = unit.design(influent)

    print("\n========== RO Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
