#!/bin/sh
#BSUB -q gpuv100                              # Submit to the hpc queue
#BSUB -J simulate100_cupy                       # Job name: simulate20
#BSUB -n 4                              # Request 1 core
#BSUB -R "span[hosts=1]"                  # Ensure the job runs on a single host
#BSUB -R "rusage[mem=1GB]"                # Request xGB memory per core
#BSUB -M 2GB                              # Kill the job if it exceeds xGB per core
#BSUB -gpu "num=1"
#BSUB -W 00:30                            # Set the walltime limit to 30 minutes
#BSUB -o simulate100_cupy_%J.out      # Standard output will be saved to a file with the job-id
#BSUB -e simulate100_cupy_%J.err      # Standard error will be saved to a file with the job-id

module load cuda/11.8

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

echo "Job started on $(hostname) at $(date)"

start_time=$(date +%s)

# Run the simulation with detailed timing info
nsys profile -o cupy_profile \
    python simulate_cupy.py 100


end_time=$(date +%s)
runtime=$((end_time - start_time))

echo "Total runtime: ${runtime} seconds"
echo "Job finished at $(date)"
