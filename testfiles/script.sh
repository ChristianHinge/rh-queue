#!/bin/bash
#SBATCH --gres=gpu:titan:1 --job-name=basic_network.py --ntasks=1 --priority=3 -o my.stdout -x titan2,titan1,titan5,titan7,titan3
echo '['/homes/pmcd/.local/bin/rhqueue', 'queue', '--test', '-s', 'titan4', 'basic_network.py']'
head -1 basic_network.py
printenv
export PYTHONUNBUFFERED=1
chmod +x basic_network.py
srun -n1 /homes/pmcd/rh-queue/testfiles/basic_network.py 