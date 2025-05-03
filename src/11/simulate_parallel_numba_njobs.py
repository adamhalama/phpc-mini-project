from os.path import join
import sys
import os
import numpy as np
from multiprocessing import Pool, cpu_count
import numba
from numba import njit


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

@njit
def jacobi_numba(simulation_grid, interior_mask, max_iter, tol):
    # u has shape (SIZE+2, SIZE+2)
    # interior_mask has shape (SIZE, SIZE)
    tmp = np.empty_like(simulation_grid)
    for it in range(max_iter):
        delta = 0.0
        # loop over interior points
        for i in range(1, simulation_grid.shape[0]-1):
            for j in range(1, simulation_grid.shape[1]-1):
                if interior_mask[i-1, j-1]:
                    new_val = 0.25 * (
                        simulation_grid[i-1, j] + 
                        simulation_grid[i+1, j] + 
                        simulation_grid[i, j-1] + 
                        simulation_grid[i, j+1]
                        )
                    tmp[i, j] = new_val
                    diff = abs(simulation_grid[i, j] - new_val)
                    if diff > delta:
                        delta = diff
                else:
                    tmp[i, j] = simulation_grid[i, j]
        # copy boundaries into the new grid and swap
        tmp[0, :] = simulation_grid[0, :]
        tmp[-1, :] = simulation_grid[-1, :]
        tmp[:, 0] = simulation_grid[:, 0]
        tmp[:, -1] = simulation_grid[:, -1]
        
        simulation_grid, tmp = tmp, simulation_grid
        if delta < tol:
            break
        
    return simulation_grid


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
    DATA_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(DATA_DIR, 'building_ids.txt'), 'r') as f:
        all_ids = f.read().splitlines()

    # -----------------------------------------------------------------
    # NEW: slice the list based on command-line *start* and *count*
    #      (those are injected by the array-job wrapper)
    # -----------------------------------------------------------------
    if len(sys.argv) < 3:
        print("usage: python simulate_parallel_numba.py <start_idx> <count>")
        sys.exit(1)

    start_idx  = int(sys.argv[1])
    count      = int(sys.argv[2])
    building_ids = all_ids[start_idx : start_idx + count]
    num_floorplans = len(building_ids)

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

    # Prepare tasks for parallel simulation (each floorplan is an independent task)
    simulation_tasks = [
        (initial_grid, mask, MAX_ITERATIONS, TOLERANCE)
        for initial_grid, mask in zip(all_initial_grids, all_interior_masks)
    ]

    # Parallelize the simulation using static scheduling (dividing tasks evenly among workers)
    worker_count = cpu_count()
    with Pool(processes=worker_count) as pool:
        simulation_results = pool.starmap(jacobi_numba, simulation_tasks)

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
