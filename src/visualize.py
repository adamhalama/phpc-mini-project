import os
import numpy as np
import matplotlib.pyplot as plt

# Directory containing simulation outputs
results_dir = "../simulation_results"

# Directory to save visualization plots
plot_dir = "../simulation_plots"
if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

# List all simulation files (assuming they end with "_final_u.npy")
files = [f for f in os.listdir(results_dir) if f.endswith("_final_u.npy")]
files.sort()  # sort files to process them in order

for file in files:
    filepath = os.path.join(results_dir, file)
    # Extract building ID from the filename (e.g., "10000")
    building_id = file.split("_")[0]
    
    # Load the simulation grid (temperature field)
    u = np.load(filepath)
    
    # Create a heatmap of the simulation result
    plt.figure(figsize=(8, 6))
    plt.imshow(u, cmap='hot', origin='lower')
    plt.colorbar(label='Temperature (°C)')
    plt.title(f"Simulation Result for Building {building_id}")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    
    # Save the plot to the plot_dir with building id in the name
    output_file = os.path.join(plot_dir, f"{building_id}_plot.png")
    plt.savefig(output_file)
    plt.close()
    print(f"Saved plot for building {building_id} to {output_file}")
