#!/bin/sh
cd ~/rh-queue/slurm-install-files/
sudo apt install slurm-wlm
sudo mkdir /var/spool/slurm-llnl
sudo chown -R slurm.slurm /var/spool/slurm-llnl
sudo mkdir /var/run/slurm-llnl/
sudo chown -R slurm.slurm /var/run/slurm-llnl
sudo mkdir /var/spool/slurmd
sudo chown -R slurm.slurm /var/spool/slurmd
sudo usermod -a -G sudo slurm
sudo systemctl start slurmd
sudo systemctl enable slurmd
sudo cp slurm.conf /etc/slurm-llnl
sudo cp gres.conf /etc/slurm-llnl
sudo mkdir /opt/munge
sudo chown -R pmcd:pmcd /opt/munge
cp munge.key /opt/munge/
sudo chown -R root:root /opt/munge
sudo cp /opt/munge/munge.key /etc/munge/munge.key
sudo rm -rf /opt/munge/
sudo chown munge: /etc/munge/munge.key
sudo chmod 400 /etc/munge/munge.key
sudo chown -R munge: /etc/munge/ /var/log/munge/
sudo chmod 0700 /etc/munge/ /var/log/munge/
sudo systemctl start munge
sudo systemctl enable munge