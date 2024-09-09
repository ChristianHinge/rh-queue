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

Fix SLURM not finding plugin for select/cons_tres:

    sudo ln -s /usr/lib/x86_64-linux-gnu/slurm-wlm /usr/lib/slurm

Fix `/var/spool/slurmd`

    sudo mkdir /var/spool/slurmd/
    sudo chown -R slurm.slurm /var/spool/slurmd

Add slurm to root
    sudo usermod -a -G root slurm
    sudo usermod -a -G sudo slurm

ensure `$id slurm` is

    uid=64030(slurm) gid=64030(slurm) groups=64030(slurm),0(root),27(sudo)


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

copy slurm.conf and gres.conf (on all nodes):

    sudo cp slurm.conf /etc/slurm
    sudo cp gres.conf /etc/slurm

Update slurm with .conf changes (on all nodes):
    sudo systemctl restart slurmctld
    sudo systemctl restart slurmd
    sudo scontrol reconfigure

setup munge:

    sudo mkdir /opt/munge
    sudo chown -R petadmin:petadmin /opt/munge
    # mungekey -c -k ./munge.key
    cp ./munge.key /opt/munge/
    sudo chown -R root:root /opt/munge
    sudo cp /opt/munge/munge.key /etc/munge/munge.key
    sudo rm -rf /opt/munge/
    sudo chown munge: /etc/munge/munge.key
    sudo chmod 400 /etc/munge/munge.key
    sudo chown -R munge: /etc/munge/ /var/log/munge/
    sudo chmod 0700 /etc/munge/ /var/log/munge/
    sudo systemctl enable munge
    sudo systemctl start munge

Test munge setup:

    munge -n | unmunge
    munge -n | ssh titan1.petnet.rh.dk unmunge
    munge -n | ssh caai1.petnet.rh.dk unmunge

The server is now setup

Test with the following script

    srun -l -n1 /bin/hostname
