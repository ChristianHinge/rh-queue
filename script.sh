#!/bin/bash
#SBATCH --gres=gpu:titan:1 --job-name=testfiles/test_timeout.py --ntasks=1 --priority=3 -o my.stdout
printenv
export PYTHONUNBUFFERED=1
chmod +x testfiles/test_timeout.py
srun -n1 /homes/pmcd/rh-queue/testfiles/test_timeout.py 