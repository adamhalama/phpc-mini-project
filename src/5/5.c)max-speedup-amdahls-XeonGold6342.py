import numpy as np

core_counts = np.array([1, 24])
walltimes_plain = np.array([1619, 151])

# Compute speed-ups relative to 1-core baseline
speedups_plain = walltimes_plain[0] / walltimes_plain

# Parallel fraction estimates (from previous calculation)
# core num 2,4,8,12
P_plain_estimates = np.array([0.946])
P_mean = P_plain_estimates.mean()

# Theoretical maximum speed-up according to Amdahl's Law
S_max_theoretical = 1 / (1 - P_mean)

# Observed maximum speed-up and corresponding core count
max_speedup_observed = speedups_plain.max()
cores_for_max_observed = core_counts[speedups_plain.argmax()]

# Fraction of theoretical achieved
achievement_ratio = max_speedup_observed / S_max_theoretical

# Print results
print(f"Average parallel fraction (P): {P_mean:.3f}")
print(f"Theoretical maximum speed-up (1/(1-P)): {S_max_theoretical:.2f}")
print(f"Observed maximum speed-up: {max_speedup_observed:.2f} on {cores_for_max_observed} cores")
print(f"Achieved {achievement_ratio:.2%} of theoretical maximum")
    