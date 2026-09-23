"""
Ranking Engine (Multi-Industry Edition)

Ranks feasible WWTP solutions using multi-attribute decision metrics.
Dynamically tracks standards via runtime module inspection.
"""

import config.standards as standards


class RankingEngine:

    def __init__(self):

        self.weights = {

            "capex": 0.30,

            "opex": 0.25,

            "land": 0.15,

            "energy": 0.10,

            "effluent": 0.20

        }

    # =====================================================
    # EFFLUENT QUALITY SCORE
    # =====================================================

    def effluent_score(
        self,
        effluent
    ):

        score = 0
        count = 0

        # Fix: Inspect STANDARDS dynamically from the active module state
        for parameter, limit in standards.STANDARDS.items():

            if parameter not in effluent:
                continue

            value = effluent[parameter]

            # Parse standardized criteria blocks accurately without causing a TypeError
            if isinstance(limit, dict):

                if "min" in limit and "max" in limit:
                    target = (limit["min"] + limit["max"]) / 2
                    score += abs(value - target)
                    count += 1

                elif "max" in limit:
                    # Lower ratio is better (closer to zero implies cleaner effluent)
                    max_limit = max(limit["max"], 1)
                    score += (value / max_limit)
                    count += 1

            else:
                max_limit = max(limit, 1)
                score += (value / max_limit)
                count += 1

        if count == 0:
            return 999999

        return score / count

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(
        self,
        value,
        minimum,
        maximum
    ):

        if maximum == minimum:
            return 0

        return (
            value - minimum
        ) / (
            maximum - minimum
        )

    # =====================================================
    # RANK
    # =====================================================

    def rank(
        self,
        solutions
    ):

        if len(solutions) == 0:
            return []

        capex_values = [
            s["capex_npr"]
            for s in solutions
        ]

        opex_values = [
            s["opex_npr_year"]
            for s in solutions
        ]

        land_values = [
            s["land_m2"]
            for s in solutions
        ]

        energy_values = [
            s["energy_kwh_day"]
            for s in solutions
        ]

        effluent_values = [
            self.effluent_score(
                s["effluent"]
            )
            for s in solutions
        ]

        capex_min = min(capex_values)
        capex_max = max(capex_values)

        opex_min = min(opex_values)
        opex_max = max(opex_values)

        land_min = min(land_values)
        land_max = max(land_values)

        energy_min = min(energy_values)
        energy_max = max(energy_values)

        effluent_min = min(effluent_values)
        effluent_max = max(effluent_values)

        ranked = []

        for i, solution in enumerate(
            solutions
        ):

            capex_score = self.normalize(
                solution["capex_npr"],
                capex_min,
                capex_max
            )

            opex_score = self.normalize(
                solution["opex_npr_year"],
                opex_min,
                opex_max
            )

            land_score = self.normalize(
                solution["land_m2"],
                land_min,
                land_max
            )

            energy_score = self.normalize(
                solution["energy_kwh_day"],
                energy_min,
                energy_max
            )

            effluent_score = self.normalize(
                effluent_values[i],
                effluent_min,
                effluent_max
            )

            total_score = (
                self.weights["capex"] * capex_score
                + self.weights["opex"] * opex_score
                + self.weights["land"] * land_score
                + self.weights["energy"] * energy_score
                + self.weights["effluent"] * effluent_score
            )

            solution["ranking_score"] = total_score
            ranked.append(solution)

        ranked.sort(
            key=lambda x: x["ranking_score"]
        )

        return ranked

    # =====================================================
    # BEST SOLUTION
    # =====================================================

    def best_solution(
        self,
        ranked_solutions
    ):

        if len(ranked_solutions) == 0:
            return None

        return ranked_solutions


if __name__ == "__main__":
    print("Ranking engine initialized with dynamic import references.")
