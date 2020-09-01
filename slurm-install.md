# Guide for setting up on new server

first:

    sudo apt install slurm-wlm


update the chown for the folders created:

Create slurm spool directory

    sudo mkdir /var/spool/slurm-llnl
    sudo chown -R slurm.slurm /var/spool/slurm-llnl

Create slurm pid directory
    
    sudo mkdir /var/run/slurm-llnl/
    sudo chown -R slurm.slurm /var/run/slurm-llnl

Fix `/var/spool/slurmd`

    sudo chown -R slurm.slurm /var/spool/slurmd

Add slurm to root
    sudo usermod -a -G root slurm
    sudo usermod -a -G sudo slurm

ensure `$id slurm` is

    uid=64030(slurm) gid=64030(slurm) groups=64030(slurm),0(root),27(sudo)

Add the user to the service file

    sudo vim /lib/systemd/system/slurmd.service

Add to file under `[Service]`

    User=slurm


Start and enable the slurm manager on boot (Controller Node)
    
    sudo systemctl start slurmctld
    sudo systemctl enable slurmctld

Start slurmd and enable on boot (Compute Node)
    
    sudo systemctl start slurmd
    sudo systemctl enable slurmd

Get info with:
    
    slurmd -C

Add new info to all slurm conf files

update gres files

cups are the number of cores

copy slurm.conf and gres.conf:

    sudo cp slurm.conf /etc/slurm-llnl
    sudo cp gres.conf /etc/slurm-llnl

setup munge:

    sudo chown munge: /etc/munge/munge.key
    sudo chmod 400 /etc/munge/munge.key
    sudo chown -R munge: /etc/munge/ /var/log/munge/
    sudo chmod 0700 /etc/munge/ /var/log/munge/
    sudo systemctl enable munge
    sudo systemctl start munge

Test munge setup:

    munge -n | unmunge
    munge -n | ssh somehost unmunge
ControlMachine=caai1

MpiDefault=none
ProctrackType=proctrack/pgid
ReturnToService=1
SlurmctldPidFile=/var/run/slurm-llnl/slurmctld.pid
SlurmdPidFile=/var/run/slurm-llnl/slurmd.pid
SlurmdSpoolDir=/var/spool/slurmd
SlurmUser=slurm
StateSaveLocation=/var/spool/slurm-llnl
SwitchType=switch/none
TaskPlugin=task/affinity

# SCHEDULING
SchedulerType=sched/backfill
SelectType=select/cons_res
SelectTypeParameters=CR_Core

# LOGGING AND ACCOUNTING
AccountingStorageType=accounting_storage/none
ClusterName=cluster
JobAcctGatherType=jobacct_gather/none

# COMPUTE NODES
GresTypes=gpu
NodeName=DEFAULT Gres=gpu:titan:1
NodeName=titan1 NodeAddr=172.16.78.179 CPUs=8 RealMemory=32066 CoresPerSocket=4 ThreadsPerCore=2
#NodeName=titan2 NodeAddr=titan2.petnet.rh.dk Gres=gpu:titan:1 CPUs=48 Boards=1 SocketsPerBoard=2 CoresPerSocket=12 ThreadsPerCore=2 RealMemory=128554
NodeName=titan3 NodeAddr=172.16.78.156 CPUs=4 Boards=1 SocketsPerBoard=1 CoresPerSocket=4 ThreadsPerCore=1 RealMemory=32067
NodeName=titan4 NodeAddr=172.16.78.180 CPUs=8 Boards=1 SocketsPerBoard=2 CoresPerSocket=4 ThreadsPerCore=1 RealMemory=15954
NodeName=titan5 NodeAddr=172.16.78.184 CPUs=8 RealMemory=31821 CoresPerSocket=4 ThreadsPerCore=2
NodeName=titan7 NodeAddr=172.16.78.188 CPUs=8 Boards=1 SocketsPerBoard=1 CoresPerSocket=4 ThreadsPerCore=2 RealMemory=31819
PartitionName=main Nodes=titan[1,3,4,5,7] Default=YES MaxTime=INFINITE State=UP

The server is now setup

Test with the following script

    srun -l -n1 /bin/hostname