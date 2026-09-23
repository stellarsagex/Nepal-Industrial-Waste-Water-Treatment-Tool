"""
Diagnostic Script to find constraint violations.
"""
from main import main
from optimizer.optimizer import WWTPOptimizer

influent = {
    "flow": 100,
    "BOD": 1200,
    "COD": 3500,
    "TSS": 1800,
    "Color": 2500,
    "TDS": 2200,
    "Oil": 45,
    "pH": 10.5
}

optimizer = WWTPOptimizer()
# We bypass the flat output by forcing the full envelope generation out of optimize manually
trains = optimizer.generator.generate()

print("\n========== REJECTION ANALYSIS ==========\n")
sample_reasons = {}

for train in trains:
    try:
        result = optimizer.simulator.simulate_train(train, influent)
        evaluation = optimizer.checker.evaluate(result)
        if not evaluation["feasible"]:
            for reason in evaluation["reasons"]:
                # Group by parameter name to see the most frequent culprit
                param = reason.split()[0]
                sample_reasons[param] = sample_reasons.get(param, 0) + 1
    except Exception as e:
        pass

for param, count in sample_reasons.items():
    print(f"Constraint Category '{param}' caused rejections in {count} trains.")
