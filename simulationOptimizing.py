import pandas as pd
import itertools
from functionTesting import function_testing

birth_options = [0.08, 0.10, 0.12]
death_options = [0.004, 0.005, 0.006]
harvest_stds = [0.35, 0.50]

grid = list(itertools.product(birth_options, death_options, harvest_stds))
results_list = []

print(f"Starting HPO: Testing {len(grid)} combinations...")

for b, d, h in grid:
    print(f"Testing Birth:{b} Death:{d} Var:{h}...", end=" ")

    res = function_testing(
        birthChance=b,
        deathChance=d,
        harvest_std=h,
    )

    score = (res["fail_rate"] * 500) + abs(res["avg_change"])
    if res["fail_rate"] > 0.38:
        score += 5000
    if res["avg_change"] > 70:
        score += 5000
    if res["avg_change"] < 0:
        score += abs(res["avg_change"]) * 2

    print(f"Score: {score:.2f}")

    results_list.append({
        "Birth": b,
        "Death": d,
        "Harvest_Var": h,
        "Fail_Rate": res['fail_rate'],
        "Pop_Drift": res['avg_change'],
        "Score": score
    })

df = pd.DataFrame(results_list)
df = df.sort_values("Score")

print("\n--- TOP 5 STABLE SETTINGS ---")
print(df.head(5))

#df.to_csv("optimization_results.csv", index=False)