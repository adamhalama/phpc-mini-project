import numpy as np

# Given data
core_counts = np.array([1, 24])
walltimes_plain = np.array([1619, 151])

# Compute speed-ups relative to 1-core baseline
speedups_plain = walltimes_plain[0] / walltimes_plain

# Function to estimate parallel fraction P using Amdahl's law
def estimate_parallel_fraction(core_counts, speedups):
    # Ignore the 1-core case (division by zero issue)
    P_estimates = []
    for N, S in zip(core_counts[1:], speedups[1:]):
        P = (1 - 1/S) / (1 - 1/N)
        P_estimates.append(P)
    return np.array(P_estimates)

# Estimate P for both scenarios
P_plain = estimate_parallel_fraction(core_counts, speedups_plain)

# Print results
print("Core Count | Walltime (plain) | Speedup (plain) | P estimate (plain)")
for N, t, S, P in zip(core_counts[1:], walltimes_plain[1:], speedups_plain[1:], P_plain):
    print(f"{N:>10} | {t:>17.2f} | {S:>15.2f} | {P:>17.3f}")

print(f"\nAverage parallel fraction (plain): {P_plain.mean():.3f}")
