sudo useradd slurm
sudo mkdir -p /etc/slurm /etc/slurm/prolog.d /etc/slurm/epilog.d /var/spool/slurm/ctld /var/spool/slurm/d /var/log/slurm /var/run/slurm/
sudo chown slurm.slurm /var/spool/slurmctld /var/spool/slurmd /var/log/slurm /var/run/slurm/
echo "made files setup last files"