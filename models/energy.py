"""
energy.py

Central energy calculation model.

All treatment units report their direct
energy consumption.

This model aggregates energy usage and
converts it into annual operating cost.
"""

from config.economics import ECONOMICS


class EnergyModel:

    def __init__(self):

        self.energy_sources = []

    # ==================================================
    # ADD ENERGY CONSUMPTION
    # ==================================================

    def add_energy(
        self,
        source_name,
        energy_kwh_day
    ):

        self.energy_sources.append({

            "source":
                source_name,

            "energy_kwh_day":
                energy_kwh_day
        })

    # ==================================================
    # TOTAL DAILY ENERGY
    # ==================================================

    def total_daily_energy(self):

        total = 0

        for source in self.energy_sources:

            total += source[
                "energy_kwh_day"
            ]

        return total

    # ==================================================
    # ANNUAL ENERGY
    # ==================================================

    def annual_energy(self):

        return (

            self.total_daily_energy()
            * 365
        )

    # ==================================================
    # ELECTRICITY COST
    # ==================================================

    def annual_energy_cost(self):

        tariff = (
            ECONOMICS[
                "electricity_tariff"
            ]["industrial"]
        )

        return (

            self.annual_energy()
            * tariff
        )

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):

        return {

            "daily_energy_kwh":
                self.total_daily_energy(),

            "annual_energy_kwh":
                self.annual_energy(),

            "annual_energy_cost_npr":
                self.annual_energy_cost(),

            "sources":
                self.energy_sources
        }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    model = EnergyModel()

    model.add_energy(
        "MBBR Aeration",
        120
    )

    model.add_energy(
        "Pumps",
        25
    )

    model.add_energy(
        "Mixers",
        10
    )

    result = model.summary()

    print("\nENERGY SUMMARY\n")

    for k, v in result.items():

        print(k, ":", v)