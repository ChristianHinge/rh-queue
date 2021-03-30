#!/bin/bash
#SBATCH --job-name=testfiles/test_timeout.py --ntasks=1 -o my.stdout --priority=3
echo '['/homes/pmcd/venv/rhqueue/bin/rhqueue', 'queue', 'testfiles/test_timeout.py', '--test']'
head -1 testfiles/test_timeout.py
printenv
export PYTHONUNBUFFERED=1
export SLURM_OUTPUT_FILE='my.stdout'
export SLURM_SCRIPT='/homes/pmcd/rh-queue/testfiles/test_timeout.py'
export SLURM_SCRIPT_ARGS=''
export SLURM_SCRIPT_EMAIL='peter.nicolas.castenschiold.mcdaniel@regionh.dk'
rhqemail start
chmod +x testfiles/test_timeout.py
source /homes/pmcd/venv/rhqueue/bin/activate
srun -n1 /homes/pmcd/rh-queue/testfiles/test_timeout.py 
deactivate
if [[ $? -eq 0 ]]; then
  rhqemail completed
else
 rhqemail failed
fi
