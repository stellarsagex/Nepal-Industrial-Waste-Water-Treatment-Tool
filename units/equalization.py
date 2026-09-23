"""
Equalization Tank

Functions
---------
1. Flow balancing
2. Shock load dampening
3. Initial mixing
4. Equalization volume estimation
5. CAPEX estimation
6. OPEX estimation

Standard Interface:
    unit = Equalization(flow_m3_day)
    result = unit.design(influent)
"""

from config.design_criteria import DESIGN_CRITERIA
from config.economics import ECONOMICS


class Equalization:

    def __init__(self, flow_m3_day):

        self.flow = max(flow_m3_day, 1)

        self.criteria = DESIGN_CRITERIA["Equalization"]

    # =====================================================
    # VOLUME
    # =====================================================

    def calculate_volume(self):

        hrt_hr = self.criteria["hrt_hr"]

        volume = (
            self.flow
            * hrt_hr
            / 24
        )

        return volume

    # =====================================================
    # LAND
    # =====================================================

    def calculate_land(self):

        volume = self.calculate_volume()

        depth = self.criteria["depth_m"]

        area = volume / depth

        allowance_factor = 1.5

        return area * allowance_factor

    # =====================================================
    # ENERGY
    # =====================================================

    def calculate_energy(self):

        mixing_power_kw_m3 = (
            self.criteria["mixing_power_kw_m3"]
        )

        volume = self.calculate_volume()

        power_kw = (
            volume
            * mixing_power_kw_m3
        )

        energy_kwh_day = (
            power_kw
            * 24
        )

        return energy_kwh_day

    # =====================================================
    # SLUDGE
    # =====================================================

    def calculate_sludge(
        self,
        influent
    ):
        # Fix: Account for the 3% TSS reduction mass balancing into generated sludge
        tss_in = influent.get("TSS", 0)
        tss_removed = tss_in * 0.03
        
        sludge_kg_day = (
            tss_removed 
            * self.flow 
            / 1000
        )
        return sludge_kg_day

    # =====================================================
    # CAPEX
    # =====================================================

    def calculate_capex(self):

        volume = self.calculate_volume()

        # Fix: Pull dynamic unit rate pricing directly out of global economics registry
        civil_tank_rate = ECONOMICS["civil_costs"]["rcc_tank"]

        civil = (
            volume 
            * civil_tank_rate
        )

        # Fix: Scale mixer hardware system dynamically using the mixer_kw rate benchmark
        mixer_kw = volume * self.criteria["mixing_power_kw_m3"]
        equipment = mixer_kw * ECONOMICS["equipment_costs"]["mixer_kw"]

        return civil + equipment

    # =====================================================
    # OPEX
    # =====================================================

    def calculate_opex(
        self,
        influent
    ):

        energy = self.calculate_energy()

        tariff = (
            ECONOMICS["electricity_tariff"]
            ["industrial"]
        )

        electricity_cost = (
            energy
            * tariff
            * 365
        )

        maintenance = (
            self.calculate_capex()
            * ECONOMICS["maintenance_factor"]
        )

        # Fix: Add annual disposal cost for the tracked settled tank bottom sediment
        sludge_kg_day = self.calculate_sludge(influent)
        sludge_rate = ECONOMICS["sludge_disposal"]["total"]
        sludge_disposal_cost = sludge_kg_day * sludge_rate * 365

        return (
            electricity_cost
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

        # Equalization mainly balances flow.
        # Small settling effect assumed.
        effluent["TSS"] = (
            influent.get("TSS", 0)
            * 0.97
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

        effluent = (
            self.calculate_effluent(
                influent
            )
        )

        return {

            "unit":
                "Equalization",

            "influent":
                influent,

            "effluent":
                effluent,

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

                "hrt_hr":
                    self.criteria["hrt_hr"]

            }

        }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    influent = {

        "flow": 100,
        "BOD": 1000,
        "COD": 2500,
        "TSS": 1200,
        "Color": 2000,
        "TDS": 1800,
        "Oil": 50,
        "pH": 10

    }

    unit = Equalization(100)

    result = unit.design(
        influent
    )

    print("\n========== Equalization Tank Solution ==========\n")
    for k, v in result.items():
        if k != "influent" and k != "effluent" and k != "design":
            print(f"{k}: {v}")
