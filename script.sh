#!/bin/bash
#SBATCH --gres=gpu:titan:1 --job-name=testfiles/test_timeout.py --ntasks=1 --priority=3 -o my.stdout
echo '['/usr/local/bin/rhqueue', 'queue', 'testfiles/test_timeout.py', '-a', '--kfold [0.1]', '--test']'
head -1 testfiles/test_timeout.py
printenv
export PYTHONUNBUFFERED=1
chmod +x testfiles/test_timeout.py
srun -n1 /homes/pmcd/rh-queue/testfiles/test_timeout.py --kfold [0.1]