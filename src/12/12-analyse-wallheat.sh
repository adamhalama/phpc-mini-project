#!/bin/sh
#BSUB -q hpc
#BSUB -J wallheat_stats
#BSUB -n 1                       
#BSUB -R "span[hosts=1]"                  
#BSUB -R "rusage[mem=2GB]"
#BSUB -M 2GB                              # Kill the job if it exceeds xGB per core
#BSUB -W 00:30
#BSUB -o wallheat_stats_%J.out
#BSUB -e wallheat_stats_%J.err

echo "Started on $(hostname) at $(date)"


source /dtu/projects/02613_2025/conda/conda_init.sh
conda activate 02613

/usr/bin/time -v python 12-analyse-wallheat.py

echo "Finished at $(date)"
