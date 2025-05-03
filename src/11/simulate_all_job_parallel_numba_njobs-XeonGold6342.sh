#!/bin/sh
#BSUB -q hpc                              # Submit to the hpc queue
#BSUB -J simulate_all_numba_njobs_c[1-10]                       # Job name: simulate20
#BSUB -n 16                                # Request 1 core
#BSUB -R "span[hosts=1]"                  # Ensure the job runs on a single host
#BSUB -R "rusage[mem=1GB]"                # Request xGB memory per core
#BSUB -R "select[model == XeonGold6226R]"  # Request a specific CPU model
#BSUB -M 2GB                              # Kill the job if it exceeds xGB per core
#BSUB -W 00:30                            # Set the walltime limit to 30 minutes
#BSUB -o simulate_all_numba_njobs_%I%_J.out      # Standard output will be saved to a file with the job-id
#BSUB -e simulate_all_numba_njobs_%I_%J.err      # Standard error will be saved to a file with the job-id

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

# ----------------- tunables -----------------
TOTAL_PLANS=4571          # full dataset
JOBS=10                    # same number as in -J 
PLANS_PER_JOB=$(( (TOTAL_PLANS + JOBS - 1) / JOBS ))  # ceiling divide
# --------------------------------------------

# Compute start offset for *this* array element
# LSB_JOBINDEX is 1-based
START=$(( (LSB_JOBINDEX - 1) * PLANS_PER_JOB ))
COUNT=$PLANS_PER_JOB

echo "Array index $LSB_JOBINDEX handles $COUNT plans starting at $START"
start_time=$(date +%s)

# Warm-up to compile Numba once (saves JIT cost in each process)
python - <<EOF
import numpy as np, numba, simulate_parallel_numba as mod
grid = np.zeros((514,514),dtype=np.float64)
mask = np.zeros((512,512),dtype=np.bool_)
mod.jacobi_numba(grid, mask, 1, 1e-4)
EOF

# Run the actual slice
/usr/bin/time -v python simulate_parallel_numba_njobs.py ${START} ${COUNT}

end_time=$(date +%s)
echo "Elapsed \$((end_time-start_time)) s"
