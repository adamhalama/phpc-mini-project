import numpy as np

# Given data
core_counts = np.array([1, 2, 4, 8, 12])
walltimes_plain = np.array([1561.01, 837.96, 583.71, 390.60, 205.06])
walltimes_ht = np.array([1633.37, 729.38, 471.99, 246.84, 223.43])

# Compute speed-ups relative to 1-core baseline
speedups_plain = walltimes_plain[0] / walltimes_plain
speedups_ht = walltimes_ht[0] / walltimes_ht

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
P_ht = estimate_parallel_fraction(core_counts, speedups_ht)

# Print results
print("Core Count | Walltime (plain) | Speedup (plain) | P estimate (plain)")
for N, t, S, P in zip(core_counts[1:], walltimes_plain[1:], speedups_plain[1:], P_plain):
    print(f"{N:>10} | {t:>17.2f} | {S:>15.2f} | {P:>17.3f}")

print("\nCore Count | Walltime (HT)    | Speedup (HT)    | P estimate (HT)")
for N, t, S, P in zip(core_counts[1:], walltimes_ht[1:], speedups_ht[1:], P_ht):
    print(f"{N:>10} | {t:>17.2f} | {S:>15.2f} | {P:>17.3f}")

print(f"\nAverage parallel fraction (plain): {P_plain.mean():.3f}")
print(f"Average parallel fraction (HT):    {P_ht.mean():.3f}")
