"""
Upflow Anaerobic Sludge Blanket (UASB)

Functions
---------
1. BOD removal
2. COD removal
3. TSS removal
4. Biogas generation
5. Sludge generation
6. CAPEX estimation
7. OPEX estimation

Standard Interface:
    unit = UASB(flow_m3_day)
    result = unit.design(influent)
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class UASB:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["UASB"]

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

        return area * 1.4

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

        bod_removal = self.criteria["bod_removal"]
        cod_removal = self.criteria["cod_removal"]
        tss_removal = self.criteria["tss_removal"]

        return {

            "BOD":
                bod_in * (1 - bod_removal),

            "COD":
                cod_in * (1 - cod_removal),

            "TSS":
                tss_in * (1 - tss_removal)

        }

    # =====================================================
    # BIOGAS
    # =====================================================

    def calculate_biogas(
        self,
        influent
    ):

        cod_in = influent.get("COD", 0)

        cod_out = (
            self.calculate_removals(
                influent
            )["COD"]
        )

        cod_removed = (
            (cod_in - cod_out)
            * self.flow
            / 1000
        )

        methane_yield = (
            self.criteria["methane_yield"]
        )

        methane = (
            cod_removed
            * methane_yield
        )

        biogas = methane / 0.65

        return biogas

    # =====================================================
    # SLUDGE
    # =====================================================

    def calculate_sludge(
        self,
        influent
    ):

        cod_in = influent.get("COD", 0)

        cod_out = (
            self.calculate_removals(
                influent
            )["COD"]
        )

        cod_removed = (
            (cod_in - cod_out)
            * self.flow
            / 1000
        )

        biomass_yield = (
            self.criteria["biomass_yield"]
        )

        return (
            cod_removed
            * biomass_yield
        )

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(self):

        pump_kw = (
            self.criteria["pump_kw"]
        )

        return pump_kw * 24

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        volume = self.calculate_volume()

        # Fix: Pull structural pricing dynamically from centralized ECONOMICS civil registry
        civil_reactor_rate = ECONOMICS["civil_costs"]["reactor"]
        civil = (
            volume
            * civil_reactor_rate
        )

        # Fix: Scale specialized internals (3-Phase GLS separators & manifolds) using equipment benchmarks
        gas_separator = volume * ECONOMICS["equipment_costs"]["pump_kw"] * 0.25
        piping = volume * ECONOMICS["equipment_costs"]["blower_kw"] * 0.10

        return (
            civil
            + gas_separator
            + piping
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
            self.calculate_energy()
            * tariff
            * 365
        )

        maintenance = (
            self.calculate_capex()
            * ECONOMICS["maintenance_factor"]
        )

        # Fix: Account for the annual hauling and treatment costs of wasted anaerobic sludge blanket mass
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

        effluent["BOD"] = removals["BOD"]
        effluent["COD"] = removals["COD"]
        effluent["TSS"] = removals["TSS"]

        effluent["Oil"] = (
            influent.get("Oil", 0)
            * 0.85
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
                "UASB",

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

                "biogas_m3_day":
                    self.calculate_biogas(
                        influent
                    ),

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

    unit = UASB(100)

    result = unit.design(
        influent
    )

    print("\n========== UASB Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
