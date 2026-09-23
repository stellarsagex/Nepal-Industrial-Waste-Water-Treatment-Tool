"""
Constraint Checker (Multi-Industry Edition)

Strictly validates simulated unit effluents against the multi-industry nested 
dictionary rules established dynamically in standards.py.
"""

# Import the module directly rather than copying the variable reference
import config.standards as standards


class ConstraintChecker:

    def __init__(self):
        pass

    # =====================================================
    # EFFLUENT CHECK
    # =====================================================
    def check_effluent(self, effluent):
        failures = []

        # Pull STANDARDS dynamically from the module state
        for parameter, limit in standards.STANDARDS.items():
            if parameter not in effluent:
                continue

            value = effluent[parameter]

            # Enforce strict parsing for nested dictionary limits
            if isinstance(limit, dict):
                if "min" in limit and "max" in limit:
                    if value < limit["min"] or value > limit["max"]:
                        failures.append(
                            f"{parameter} ({value:.2f}) outside range [{limit['min']}-{limit['max']}]"
                        )
                elif "max" in limit:
                    if value > limit["max"]:
                        failures.append(
                            f"{parameter} ({value:.2f} > {limit['max']:.2f} mg/L)"
                        )
            else:
                # Primitive value fallback protection
                if value > limit:
                    failures.append(
                        f"{parameter} ({value:.2f} > {limit:.2f})"
                    )

        return failures

    # =====================================================
    # LAND CHECK
    # =====================================================
    def check_land(self, land_required, land_available):
        if land_available is None:
            return []
        if land_required > land_available:
            return [
                f"Land exceeded ({land_required:.2f} > {land_available:.2f} m²)"
            ]
        return []

    # =====================================================
    # CAPEX CHECK
    # =====================================================
    def check_capex(self, capex, capex_limit):
        if capex_limit is None:
            return []
        if capex > capex_limit:
            return [
                f"CAPEX exceeded ({capex:,.0f} NPR > {capex_limit:,.0f} NPR)"
            ]
        return []

    # =====================================================
    # OPEX CHECK
    # =====================================================
    def check_opex(self, opex, opex_limit):
        if opex_limit is None:
            return []
        if opex > opex_limit:
            return [
                f"OPEX exceeded ({opex:,.0f} NPR/year > {opex_limit:,.0f} NPR/year)"
            ]
        return []

    # =====================================================
    # MASTER CHECK
    # =====================================================
    def evaluate(
        self,
        simulation_result,
        land_available=None,
        capex_limit=None,
        opex_limit=None
    ):
        failures = []

        failures.extend(self.check_effluent(simulation_result["effluent"]))
        failures.extend(self.check_land(simulation_result["land_m2"], land_available))
        failures.extend(self.check_capex(simulation_result["capex_npr"], capex_limit))
        failures.extend(self.check_opex(simulation_result["opex_npr_year"], opex_limit))

        return {
            "feasible": len(failures) == 0,
            "reasons": failures
        }


if __name__ == "__main__":
    print("Constraint checker initialized with dynamic import references.")
