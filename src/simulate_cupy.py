from os.path import join
import sys
import os
import numpy as np
import cupy as cp

def load_data(load_dir, bid):
    SIZE = 512
    u_host = np.zeros((SIZE + 2, SIZE + 2))
    u_host[1:-1, 1:-1] = np.load(join(load_dir, f"{bid}_domain.npy"))
    interior_mask_host = np.load(join(load_dir, f"{bid}_interior.npy"))

    # Transfer to GPU
    u = cp.asarray(u_host)
    interior_mask = cp.asarray(interior_mask_host)
    return u, interior_mask

def jacobi_gpu(u, interior_mask, max_iter):
    u = u.copy()  # GPU copy
    for _ in range(max_iter):
        # GPU vectorized Jacobi update
        u_new = 0.25 * (
            u[1:-1, :-2] + u[1:-1, 2:] +
            u[:-2, 1:-1] + u[2:, 1:-1]
        )
        u_interior = u[1:-1, 1:-1]
        u_interior = cp.where(interior_mask, u_new, u_interior)
        u[1:-1, 1:-1] = u_interior
        
    return u

def summary_stats_gpu(u, interior_mask):
    u_interior = u[1:-1, 1:-1][interior_mask]
    u_cpu = cp.asnumpy(u_interior)
    mean_temp = u_cpu.mean()
    std_temp = u_cpu.std()
    pct_above_18 = np.sum(u_cpu > 18) / u_cpu.size * 100
    pct_below_15 = np.sum(u_cpu < 15) / u_cpu.size * 100
    return {
        'mean_temp': mean_temp,
        'std_temp': std_temp,
        'pct_above_18': pct_above_18,
        'pct_below_15': pct_below_15,
    }

if __name__ == '__main__':
    # Load data
    LOAD_DIR = '/dtu/projects/02613_2025/data/modified_swiss_dwellings/'
    with open(join(LOAD_DIR, 'building_ids.txt'), 'r') as f:
        building_ids = f.read().splitlines()

    if len(sys.argv) < 2:
        N = 1
    else:
        N = int(sys.argv[1])
        building_ids = building_ids[:N]

    MAX_ITER = 20_000

    output_dir = "../simulation_results"
    os.makedirs(output_dir, exist_ok=True)

    print('building_id, mean_temp, std_temp, pct_above_18, pct_below_15')
    for bid in building_ids:
        u, interior_mask = load_data(LOAD_DIR, bid)
        u_final = jacobi_gpu(u, interior_mask, MAX_ITER)
        stats = summary_stats_gpu(u_final, interior_mask)
        print(f"{bid}, {stats['mean_temp']}, {stats['std_temp']}, "
              f"{stats['pct_above_18']}, {stats['pct_below_15']}")
        # Save result back to CPU
        u_host_final = cp.asnumpy(u_final)
        np.save(join(output_dir, f"{bid}_final_u.npy"), u_host_final)
