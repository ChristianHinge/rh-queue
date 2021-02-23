# EXAMPLE INIT

source /homes/claes/python-virtual-environments/conda.bashrc
export PATH=/usr/local/cuda-10.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-10.1/lib64:$LD_LIBRARY_PATH


rhqueue queue main_v4_mGPUDATASET.py --args test 5 2 --script-name TEST9 -e claes.noehr.ladefoged@regionh.dk -o out9 -s titan5 -c powerai --INITBASH BASHFIL.sh
