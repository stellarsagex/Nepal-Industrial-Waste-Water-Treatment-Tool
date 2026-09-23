"""
Moving Bed Biofilm Reactor (MBBR)

Functions
---------
1. BOD removal
2. COD removal
3. TSS removal
4. Reactor sizing
5. Media sizing
6. Sludge generation
7. Energy estimation
8. CAPEX estimation
9. OPEX estimation
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class MBBR:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["MBBR"]

    # =====================================================
    # REACTOR VOLUME
    # =====================================================

    def calculate_volume(self):

        hrt_hr = self.criteria["hrt_hr"]

        return (
            self.flow
            * hrt_hr
            / 24
        )

    # =====================================================
    # MEDIA VOLUME
    # =====================================================

    def calculate_media_volume(self):

        volume = self.calculate_volume()

        fill_fraction = (
            self.criteria["media_fill_fraction"]
        )

        return volume * fill_fraction

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        volume = self.calculate_volume()

        depth = self.criteria["depth_m"]

        area = volume / depth

        return area * 1.5

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

        return {

            "BOD":
                bod_in *
                (1 - self.criteria["bod_removal"]),

            "COD":
                cod_in *
                (1 - self.criteria["cod_removal"]),

            "TSS":
                tss_in *
                (1 - self.criteria["tss_removal"]),

            "Color":
                color_in *
                (1 - self.criteria["color_removal"])

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

        aeration = (
            bod_removed_kg_day
            * self.criteria[
                "aeration_kwh_per_kg_bod"
            ]
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

        # Fix: Route pricing through centralized ECONOMICS civil structures block
        civil_reactor_rate = ECONOMICS["civil_costs"]["reactor"]

        reactor_cost = (
            volume
            * civil_reactor_rate
        )

        # Fix: Plastic biofilm carriers scale with equipment indexes (using pump_kw as benchmark)
        media_cost = (
            self.calculate_media_volume()
            * ECONOMICS["equipment_costs"]["pump_kw"]
            * 0.40
        )

        # Fix: Aeration hardware scales dynamically via blowers kw cost markers
        aeration_cost = volume * ECONOMICS["equipment_costs"]["blower_kw"] * 0.12

        return (
            reactor_cost
            + media_cost
            + aeration_cost
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

        # Fix: Account for the annual cost of disposing of sloughed bio-sludge mass
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

        # Guard: Guarantee the processing boundary matches incoming streaming execution load
        if "flow" in influent:
            self.flow = max(influent["flow"], 1)

        return {

            "unit":
                "MBBR",

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

                "media_volume_m3":
                    self.calculate_media_volume(),

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
        "TDS": 2200

    }

    unit = MBBR(100)

    result = unit.design(influent)

    print("\n========== MBBR Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
