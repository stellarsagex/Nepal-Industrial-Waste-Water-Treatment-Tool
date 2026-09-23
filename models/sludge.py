"""
sludge.py

Central sludge production model.

All units send sludge generation values
to this model.

This model aggregates sludge production
and estimates annual disposal cost.
"""

from config.economics import ECONOMICS


class SludgeModel:

    def __init__(self):

        self.sludge_sources = []

    # ==================================================
    # ADD SLUDGE
    # ==================================================

    def add_sludge(
        self,
        source_name,
        sludge_kg_day
    ):

        self.sludge_sources.append({

            "source":
                source_name,

            "sludge_kg_day":
                sludge_kg_day
        })

    # ==================================================
    # TOTAL DAILY SLUDGE
    # ==================================================

    def total_daily_sludge(self):

        total = 0

        for source in self.sludge_sources:

            total += source[
                "sludge_kg_day"
            ]

        return total

    # ==================================================
    # ANNUAL SLUDGE
    # ==================================================

    def annual_sludge(self):

        return (

            self.total_daily_sludge()
            * 365
        )

    # ==================================================
    # DISPOSAL COST
    # ==================================================

    def annual_disposal_cost(self):

        disposal_rate = (
            ECONOMICS[
                "sludge_disposal"
            ]["total"]
        )

        return (

            self.annual_sludge()
            * disposal_rate
        )

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self):

        return {

            "daily_sludge_kg":
                self.total_daily_sludge(),

            "annual_sludge_kg":
                self.annual_sludge(),

            "annual_disposal_cost_npr":
                self.annual_disposal_cost(),

            "sources":
                self.sludge_sources
        }


# ======================================================
# TEST
# ======================================================

if __name__ == "__main__":

    sludge = SludgeModel()

    sludge.add_sludge(
        "Primary Clarifier",
        120
    )

    sludge.add_sludge(
        "Coagulation",
        85
    )

    sludge.add_sludge(
        "MBBR",
        40
    )

    result = sludge.summary()

    print("\nSLUDGE SUMMARY\n")

    for k, v in result.items():

        print(k, ":", v)