#!/bin/sh
#BSUB -q hpc                              # Submit to the hpc queue
#BSUB -J simulate100-12cx2                       # Job name: simulate20
#BSUB -n 12                                # Request 1 core
#BSUB -R "span[hosts=2]"                  # Ensure the job runs on a single host
#BSUB -R "rusage[mem=2GB]"                # Request xGB memory per core
#BSUB -R "select[model == XeonGold6126]"  # Request a specific CPU model
#BSUB -M 3GB                              # Kill the job if it exceeds xGB per core
#BSUB -W 00:30                            # Set the walltime limit to 30 minutes
#BSUB -o simulate100_12x2_%J.out                # Standard output will be saved to a file with the job-id
#BSUB -e simulate100_12x2_%J.err                # Standard error will be saved to a file with the job-id

source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

echo "Job started on $(hostname) at $(date)"

start_time=$(date +%s)

# Run the simulation with detailed timing info
/usr/bin/time -v python simulate_parallel.py 100

end_time=$(date +%s)
runtime=$((end_time - start_time))

echo "Total runtime: ${runtime} seconds"
echo "Job finished at $(date)"
