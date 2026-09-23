"""
WWTP Optimizer (Multi-Industry Optimization Engine)

Main optimization engine featuring fallback non-compliance target attainment 
tracking for cost-constrained scenarios.
"""

from optimizer.train_generator import TrainGenerator
from optimizer.constraint_checker import ConstraintChecker
from optimizer.ranking import RankingEngine
from simulator.process_simulator import ProcessSimulator


class WWTPOptimizer:

    def __init__(self):
        self.generator = TrainGenerator()
        self.simulator = ProcessSimulator()
        self.checker = ConstraintChecker()
        self.ranking = RankingEngine()

    def _calculate_attainment_efficiency(self, result):
        """
        Calculates what percentage of standard environmental discharge limits 
        were successfully hit by a train.
        """
        from config.standards import STANDARDS
        effluent = result.get("effluent", {})
        
        passed_parameters = 0
        total_parameters = 0
        
        for parameter, limit in STANDARDS.items():
            if parameter not in effluent:
                continue
            
            total_parameters += 1
            value = effluent[parameter]
            
            if isinstance(limit, dict):
                if "min" in limit and "max" in limit:
                    if limit["min"] <= value <= limit["max"]:
                        passed_parameters += 1
                elif "max" in limit:
                    if value <= limit["max"]:
                        passed_parameters += 1
            else:
                if value <= limit:
                    passed_parameters += 1
                    
        if total_parameters == 0:
            return 0.0
        return (passed_parameters / total_parameters) * 100.0

    # =====================================================
    # OPTIMIZATION
    # =====================================================
    def optimize(
        self,
        influent,
        land_available=None,
        capex_limit=None,
        opex_limit=None,
        verbose=True
    ):
        trains = self.generator.generate()
        feasible = []
        rejected = []
        total = len(trains)

        if verbose:
            print(f"\nGenerated {total} treatment trains\n")

        for index, train in enumerate(trains, start=1):
            if verbose:
                print(f"[{index}/{total}] " + " → ".join(train))

            try:
                result = self.simulator.simulate_train(train=train, influent=influent)
                evaluation = self.checker.evaluate(
                    simulation_result=result,
                    land_available=land_available,
                    capex_limit=capex_limit,
                    opex_limit=opex_limit
                )

                result["train"] = train
                result["constraint_result"] = evaluation
                
                # Calculate what % efficiency was achieved relative to environmental targets
                result["attainment_efficiency"] = self._calculate_attainment_efficiency(result)

                if evaluation["feasible"]:
                    feasible.append(result)
                else:
                    rejected.append(result)

            except Exception as e:
                if verbose:
                    print(f"ERROR: {str(e)}")

        ranked_feasible = self.ranking.rank(feasible)

        # --- FALLBACK MECHANISM FOR UNFEASIBLE CONFIGURATIONS ---
        # Find trains that respect Land, CAPEX, and OPEX caps but failed environmental cleanup
        financially_valid_fallbacks = []
        for r in rejected:
            reasons = r["constraint_result"]["reasons"]
            
            # Filter out records that violated financial limits
            cost_failure = any("exceeded" in text.lower() for text in reasons)
            if not cost_failure:
                financially_valid_fallbacks.append(r)
                
        # Sort fallbacks so the train getting closest to 100% environmental compliance appears first
        financially_valid_fallbacks.sort(key=lambda x: x["attainment_efficiency"], reverse=True)

        # Fix: Ensure optimization dictionaries isolate lists from flat scalar structures correctly
        optimization_result = {
            "feasible": ranked_feasible,
            "rejected": rejected,
            "fallbacks": financially_valid_fallbacks,
            "total": total
        }

        return optimization_result

    def print_summary(self, optimization_result, top_n=10):
        print("\nOptimization completed.")
