#!/bin/bash
#SBATCH --gres=gpu:titan:1 --ntasks=1 --priority=3 -o my.stdout -x titan[1,2,3,4]
export PYTHONUNBUFFERED=1
echo $PATH
python3 test.py
./test.py
# rhqemail start peter.nicolas.castenschiold.mcdaniel@regionh.dk /homes/pmcd/rh-queue/testfiles/test_venv.py 1 23 4 5
# chmod +x testfiles/test_venv.py
# srun -n1 /homes/pmcd/rh-queue/testfiles/test_venv.py 1 23 4 5
# if [$? -eq 0]; then
#         rhqemail completed peter.nicolas.castenschiold.mcdaniel@regionh.dk testfiles/test_venv.py 
#       else
#         rhqemail failed peter.nicolas.castenschiold.mcdaniel@regionh.dk testfiles/test_venv.py
#       fi
      