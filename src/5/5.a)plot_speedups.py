import matplotlib.pyplot as plt

# Original data (plain multiprocessing)
core_counts_plain = [1, 2, 4, 8, 12]
walltimes_plain = [1561.01, 837.96, 583.71, 390.60, 205.06]

# Hyperthreading data
core_counts_ht = [1, 2, 4, 8, 12]
walltimes_ht = [1633.37, 729.38, 471.99, 246.84, 223.43]

# Calculate speed-ups relative to the 1-core baseline for each scenario
speedups_plain = [walltimes_plain[0] / t for t in walltimes_plain]
speedups_ht = [walltimes_ht[0] / t for t in walltimes_ht]

# Create a figure with two subplots: walltime and speed-up
plt.figure(figsize=(12, 5))

# Walltime vs. core count
plt.subplot(1, 2, 1)
plt.plot(core_counts_plain, walltimes_plain, marker='o', label='Plain multiprocessing')
plt.plot(core_counts_ht, walltimes_ht, marker='o', label='Hyperthreading')
plt.xlabel('Number of Cores')
plt.ylabel('Walltime (seconds)')
plt.title('Walltime vs. Core Count')
plt.legend()
plt.grid(True)

# Speed-up vs. core count
plt.subplot(1, 2, 2)
plt.plot(core_counts_plain, speedups_plain, marker='o', linestyle='--', label='Plain multiprocessing')
plt.plot(core_counts_ht, speedups_ht, marker='o', linestyle='--', label='Hyperthreading')
plt.xlabel('Number of Cores')
plt.ylabel('Speed-Up')
plt.title('Speed-Up vs. Core Count')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
