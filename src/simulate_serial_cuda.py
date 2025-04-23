from os.path import join
import sys
import os
import numpy as np
from multiprocessing import Pool, cpu_count

import numba
from numba import njit
from numba import cuda


def load_floorplan_data(data_dir, building_id):
    """
    Load the initial simulation grid (temperature domain) and 
    the interior mask for a given building.
    """
    GRID_SIZE = 512
    simulation_grid = np.zeros((GRID_SIZE + 2, GRID_SIZE + 2))
    simulation_grid[1:-1, 1:-1] = np.load(join(data_dir, f"{building_id}_domain.npy"))
    interior_mask = np.load(join(data_dir, f"{building_id}_interior.npy"))
    return simulation_grid, interior_mask

def jacobi_solver(simulation_grid, interior_mask, max_iterations, tolerance=1e-6):
    """
    Solve for the steady state temperature distribution using the
    Jacobi iterative method.
    """
    current_grid = np.copy(simulation_grid)
    for iteration in range(max_iterations):
        updated_grid = 0.25 * (current_grid[1:-1, :-2] +
                               current_grid[1:-1, 2:] +
                               current_grid[:-2, 1:-1] +
                               current_grid[2:, 1:-1])
        updated_interior = updated_grid[interior_mask]
        difference = np.abs(current_grid[1:-1, 1:-1][interior_mask] - updated_interior).max()
        current_grid[1:-1, 1:-1][interior_mask] = updated_interior

        if difference < tolerance:
            break
    return current_grid


@cuda.jit
def jacobi_iteration_kernel(simulation_grid, simulation_grid_new, mask):
    i, j = cuda.grid(2)
    # Only update interior points; copy boundary points unchanged
    if 1 <= i < simulation_grid.shape[0]-1 and 1 <= j < simulation_grid.shape[1]-1:
        if mask[i-1, j-1]:  
            # 4‐point stencil
            simulation_grid_new[i, j] = 0.25 * (
                simulation_grid[i-1, j] + 
                simulation_grid[i+1, j] + 
                simulation_grid[i, j-1] + 
                simulation_grid[i, j+1]
            )
        else:
            # Wall or exterior: keep fixed
            simulation_grid_new[i, j] = simulation_grid[i, j]
    # Threads with (i,j) outside grid simply do nothing

def jacobi_cuda(simulation_grid_host, mask_host, num_iterations, blockdim=(16,16)):
    # 1) Copy data to device
    d_u     = cuda.to_device(simulation_grid_host)
    d_u_new = cuda.device_array_like(simulation_grid_host)
    d_mask  = cuda.to_device(mask_host)
    
    # 2) Configure launch grid to cover SIZE+2 by SIZE+2
    ny, nx = simulation_grid_host.shape
    griddim = ((nx + blockdim[0] - 1)//blockdim[0],
               (ny + blockdim[1] - 1)//blockdim[1])
    
    # 3) Iteratively launch the kernel
    for _ in range(num_iterations):
        jacobi_iteration_kernel[griddim, blockdim](d_u, d_u_new, d_mask)
        # swap buffers for next iteration
        d_u, d_u_new = d_u_new, d_u
    
    # 4) Copy final result back to host
    return d_u.copy_to_host()


def calculate_summary_statistics(simulation_grid, interior_mask):
    """
    Compute summary statistics (mean, standard deviation, and 
    percentage of area above 18°C and below 15°C) for the interior
    region of the simulation grid.
    """
    interior_values = simulation_grid[1:-1, 1:-1][interior_mask]
    mean_temperature = interior_values.mean()
    std_temperature = interior_values.std()
    pct_above_18 = np.sum(interior_values > 18) / interior_values.size * 100
    pct_below_15 = np.sum(interior_values < 15) / interior_values.size * 100
    return {
        'mean_temp': mean_temperature,
        'std_temp': std_temperature,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }

if __name__ == '__main__':
    # Define data directory and load building IDs
    DATA_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(DATA_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    # Use a subset of floorplans if a command-line argument is given
    if len(sys.argv) < 2:
        num_floorplans = 1
    else:
        num_floorplans = int(sys.argv[1])
        building_ids = building_ids[:num_floorplans]

    # Load floorplan data into separate arrays for simulation grids and interior masks
    all_initial_grids = np.empty((num_floorplans, 514, 514))
    all_interior_masks = np.empty((num_floorplans, 512, 512), dtype='bool')
    for index, building_id in enumerate(building_ids):
        grid, mask = load_floorplan_data(DATA_DIR, building_id)
        all_initial_grids[index] = grid
        all_interior_masks[index] = mask

    # Define simulation parameters
    MAX_ITERATIONS = 20_000
    TOLERANCE = 1e-4

    # ── SEQUENTIAL GPU LOOP ──
    # No Pool, just launch your jacobi_cuda one after another:
    simulation_results = [
        jacobi_cuda(grid, mask, MAX_ITERATIONS)
        for grid, mask in zip(all_initial_grids, all_interior_masks)
    ]
    
    # Print summary statistics in CSV format
    stat_keys = ['mean_temp', 'std_temp', 'pct_above_18', 'pct_below_15']
    print('building_id, ' + ', '.join(stat_keys))
    for building_id, simulation_grid, mask in zip(building_ids, simulation_results, all_interior_masks):
        stats = calculate_summary_statistics(simulation_grid, mask)
        print(f"{building_id}, " + ", ".join(str(stats[key]) for key in stat_keys))

    # Save simulation grids for later visualization
    output_directory = "../simulation_results"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for building_id, simulation_grid in zip(building_ids, simulation_results):
        np.save(join(output_directory, f"{building_id}_final_u.npy"), simulation_grid)
