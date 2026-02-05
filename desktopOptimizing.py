import pandas as pd
import numpy as np
import itertools
import multiprocessing as mp
import time
from functionTesting import function_testing


# --- 1. CONFIGURATION & SCORING ---
def evaluate_setting(params):
    b, d, h, c = params

    # Progress Print
    print(f"  > Processing: Birth={b:.3f}, Death={d:.4f}, Var={h:.2f}, Crowd={c:.1f}")

    res = function_testing(
        birthChance=b,
        deathChance=d,
        harvest_std=h,
        crowding_factor=c
    )

    fail_rate = res["fail_rate"]
    avg_change = res["avg_change"]

    # --- REFINED SCORING ---
    # Target: +50 Pop, < 25% Fail
    score = 0

    # Penalty A: Failure Rate (25% threshold)
    if fail_rate > 0.25:
        score += (fail_rate * 15000)
    else:
        score += (fail_rate * 1000)

        # Penalty B: Population Drift (Target 50)
    target_growth = 50
    drift_distance = abs(avg_change - target_growth)
    score += (drift_distance ** 2)

    # Penalty C: Decline Prevention
    if avg_change < 0:
        score += abs(avg_change) * 150

    print(f"      [Done] Score: {score:8.2f} | Drift: {avg_change:6.2f} | Fail: {fail_rate:.2f}")

    return {
        "Birth": b,
        "Death": d,
        "Harvest_Var": h,
        "Crowd_Factor": c,
        "Fail_Rate": fail_rate,
        "Pop_Drift": avg_change,
        "Score": score
    }


# --- 2. EXECUTION ---
if __name__ == '__main__':
    # Broad Search Grid
    birth_options = np.arange(0.08, 0.131, 0.01)
    death_options = np.arange(0.005, 0.0071, 0.0005)
    harvest_stds = [0.30, 0.40, 0.50]
    crowding_options = [0.8, 1.0, 1.2, 1.4]

    grid = list(itertools.product(birth_options, death_options, harvest_stds, crowding_options))

    print(f"Starting 4-Variable Baseline HPO on {mp.cpu_count()} cores.")
    print(f"Testing {len(grid)} total combinations...")

    start_time = time.time()

    with mp.Pool(processes=mp.cpu_count()) as pool:
        results_list = pool.map(evaluate_setting, grid)

    end_time = time.time()

    df = pd.DataFrame(results_list)
    df = df.sort_values("Score")

    print(f"\nOptimization Complete in {round(end_time - start_time, 2)} seconds.")
    print("\n--- NEW TOP 10 SETTINGS (+50 Target) ---")
    print(df.head(10).to_string(index=False))

#   df.to_csv("broad_crowding_results.csv", index=False)