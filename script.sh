#!/bin/bash
#SBATCH --gres=gpu:titan:1 --ntasks=1 --priority=3 -o my.stdout
export PYTHONUNBUFFERED=1
chmod +x ./testfiles/test_create_file.py
srun -n1 -l ./testfiles/test_create_file.py