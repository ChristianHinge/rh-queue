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

The server is now setup

Test with the following script

    srun -l -n1 /bin/hostname