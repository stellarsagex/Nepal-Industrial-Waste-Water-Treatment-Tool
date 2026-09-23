"""
Train Generator

Generates possible WWTP treatment trains.
"""

class TrainGenerator:

    def __init__(self):

        self.pretreatment_options = [

            ["Equalization"],

            [
                "Equalization",
                "Neutralization"
            ],

            [
                "Equalization",
                "Neutralization",
                "Coagulation"
            ],

            [
                "Equalization",
                "Neutralization",
                "Coagulation",
                "Primary_Clarifier"
            ]
        ]

        self.biological_units = [

            "ABR",
            "UASB",
            "ASP",
            "MBBR",
            "SBR",
            "Wetland"
        ]

        self.tertiary_options = [

            [],

            ["Sand_Filter"],

            ["Activated_Carbon"],

            ["RO"],

            [
                "Sand_Filter",
                "Activated_Carbon"
            ],

            [
                "Sand_Filter",
                "RO"
            ],

            [
                "Activated_Carbon",
                "RO"
            ],

            [
                "Sand_Filter",
                "Activated_Carbon",
                "RO"
            ]
        ]

    # =====================================================
    # GENERATE ALL TRAINS
    # =====================================================

    def generate(self):

        trains = []

        for pre in self.pretreatment_options:

            for bio in self.biological_units:

                for tertiary in self.tertiary_options:

                    # Rule 1: Prevent heavy coagulated/primary clarifier solids from going straight to a Wetland
                    if bio == "Wetland" and "Primary_Clarifier" in pre:
                        continue

                    # Rule 2: Membrane Protection Rule - Prevent RO from running without prior Sand Filter polishing
                    if "RO" in tertiary and "Sand_Filter" not in tertiary:
                        continue

                    train = []

                    train.extend(pre)

                    train.append(bio)

                    train.extend(tertiary)

                    trains.append(train)

        return self.remove_duplicates(
            trains
        )

    # =====================================================
    # REMOVALS
    # =====================================================

    def remove_duplicates(
        self,
        trains
    ):

        unique = []

        seen = set()

        for train in trains:

            key = tuple(train)

            if key not in seen:

                seen.add(key)

                unique.append(train)

        return unique


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    generator = TrainGenerator()

    trains = generator.generate()

    print(
        f"\nGenerated {len(trains)} engineered process trains\n"
    )

    for i, train in enumerate(
        trains[:20],
        start=1
    ):

        print(
            f"{i}. "
            + " → ".join(train)
        )
