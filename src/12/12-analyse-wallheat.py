#!/usr/bin/env python3
"""
Post-process all *_final_u.npy files in simulation_results/ and
write:
  • stats.csv           (one row per building)
  • histogram.png       (distribution of mean temps)
  • summary.txt         (answers for 12b – 12e)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RESULT_DIR = Path("../simulation_results")
files = sorted(RESULT_DIR.glob("*_final_u.npy"))
if not files:
    raise SystemExit("No result grids found in simulation_results/")

records = []
for f in files:
    bid = int(f.stem.split("_")[0])      
    u   = np.load(f)

    core = u[1:-1, 1:-1]
    mask = (core > 0) & (core != 5) & (core != 25)
    vals = core[mask]
    if vals.size == 0:
        continue

    records.append(dict(
        building_id   = bid,
        mean_temp     = vals.mean(),
        std_temp      = vals.std(),
        pct_above_18  = (vals > 18).mean()*100,
        pct_below_15  = (vals < 15).mean()*100
    ))

df = pd.DataFrame(records).sort_values("building_id")
df.to_csv("stats.csv", index=False)

# Histogram for 12a
plt.figure(figsize=(6,4))
plt.hist(df["mean_temp"], bins=25, edgecolor="k")
plt.title("Distribution of mean interior temperatures")
plt.xlabel("Mean temperature (°C)")
plt.ylabel("Number of buildings")
plt.tight_layout()
plt.savefig("histogram_mean_temp.png", dpi=150)

# Text summary for 12b–e
summary_lines = [
    f"Buildings analysed: {len(df)}",
    f"Average mean temperature:      {df['mean_temp'].mean():.2f} °C",
    f"Average temperature std-dev:   {df['std_temp' ].mean():.2f} °C",
    f"≥50 % of area above 18 °C:      {(df['pct_above_18']>=50).sum()} buildings",
    f"≥50 % of area below 15 °C:      {(df['pct_below_15']>=50).sum()} buildings",
]
Path("summary.txt").write_text("\n".join(summary_lines))
print("\n".join(summary_lines))
