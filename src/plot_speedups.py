import matplotlib.pyplot as plt

# Core counts and measured walltimes in seconds
core_counts = [1, 2, 4, 8]
walltimes = [1725.36, 837.96, 583.71, 390.60]

# Compute speed-ups relative to the 1 core baseline
baseline_time = walltimes[0]
speed_ups = [baseline_time / t for t in walltimes]

# Plot walltime vs. core count
plt.figure(figsize=(10, 4))

plt.subplot(1, 2, 1)
plt.plot(core_counts, walltimes, marker='o')
plt.xlabel('Number of Cores')
plt.ylabel('Walltime (seconds)')
plt.title('Walltime vs. Core Count')
plt.grid(True)

# Plot speed-up vs. core count
plt.subplot(1, 2, 2)
plt.plot(core_counts, speed_ups, marker='o', linestyle='--', color='green')
plt.xlabel('Number of Cores')
plt.ylabel('Speed-Up')
plt.title('Speed-Up vs. Core Count')
plt.grid(True)

plt.tight_layout()
plt.show()
