import numpy as np

# Given data for plain multiprocessing
total_floorplans = 4571            # Total number of floorplans in the dataset
subset_count = 20                 # Number of floorplans used in timing experiments
time_subset =  237

# Extrapolate to total_floorplans
time_all_parallel = time_subset * (total_floorplans / subset_count)

# Convert to hours, minutes, and seconds
hours = int(time_all_parallel // 3600)
minutes = int((time_all_parallel % 3600) // 60)
seconds = time_all_parallel % 60

print(f"Time for {subset_count} floorplans: {time_subset:.1f} seconds")
print(f"Estimated total time: {time_all_parallel:.1f} seconds")
print(f"Which is approximately: {hours}h {minutes}m {seconds:.0f}s")
