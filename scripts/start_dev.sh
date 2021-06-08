Servers=("titan1" "titan2" "titan3" "titan4" "titan5" "titan7")
export RHQLOCATION="/homes/pmcd/rh-queue"
export VENVSLOCATION="/homes/pmcd/venv"
rhqbuild() {
    cd $RHQLOCATION
    rm -rf ./build
    python3 setup.py bdist_wheel -d /opt/rh-queue
}

rhqinstall() {
    rhqbuild
    sudo -H -u root python3 -m pip install --upgrade /opt/rh-queue/*.whl --no-cache
    rm /opt/rh-queue/*.whl
}

rhqtest() {
    cd $RHQLOCATION/testfiles
    for var in "$@"; do
        python3 "run_${var}_tests.py"
    done
}

rhqstart() {
    source $VENVSLOCATION/rhqueue/bin/activate
    cd $RHQLOCATION
    python setup.py develop
}

rhqstop() {
    deactivate
}

rhqcheck-version() {
    for server in "${Servers[@]}"; do
        echo $server
        ssh $server -q -t "rhqueue -V"
    done
}

slurm-update-conf() {
    cd $RHQLOCATION/slurm-install-files/
    sudo cp slurm.conf /etc/slurm
    sudo cp gres.conf /etc/slurm
    sudo cp cgroup.conf /etc/slurm
    cd $OLDPWD
}

slurm-state() {
    sudo systemctl $1 slurmctld
    sudo systemctl $1 slurmd
}

slurm-update-service() {
    cd $RHQLOCATION/slurm-install-files/
    sudo cp slurmctld.service /etc/systemd/system/
    sudo cp slurmd.service /etc/systemd/system
    sudo systemctl daemon-reload
    cd $OLDPWD
}

_prep-prerequisites() {
    sudo apt-get update
    sudo apt-get install -y git gcc make ruby ruby-dev libpam0g-dev libmunge-dev libmunge2 munge
    cd /opt
    sudo gem install fpm
}

_build-slurm-deb() {
    _prep-prerequisites
    sudo mkdir -p /opt/slurm /opt/slurm-src
    sudo chown -R pmcd.pmcd /opt/slurm /opt/slurm-src
    local slurmBuild="/opt/slurm"
    cd /opt/slurm-src
    local slurmFile="slurm-$1-latest"
    echo "Downloading version $slurmFile"
    wget "https://download.schedmd.com/slurm/$slurmFile.tar.bz2"
    tar xvjf "$slurmFile.tar.bz2"
    rm "$slurmFile.tar.bz2"
    local slurmdEndVersion=$(ls -d */)
    local slurmdEndVersion=${slurmdEndVersion[0]::-1}
    echo "files ${slurmdEndVersion}"
    cd $slurmdEndVersion
    local pamLocation=$(find /lib -name '*pam_cap.so' -printf '%h\n')
    ./configure --prefix=/opt/slurm --sysconfdir=/etc/slurm --enable-pam --with-pam_dir=$pamLocation --without-shared-libslurm
    # powerpc64le-unknown-linux-gnu
    # x86_64-pc-linux-gnu
    make -j4
    make contrib -j4
    make install -j4
    cd ..
    cp $RHQLOCATION/slurm-install-files/*.sh $slurmBuild
    fpm -s dir -t deb -v ${slurmdEndVersion#slurm-}-1.0 -n slurm-rhqueue --prefix=/usr --config-files=/opt/slurm -C /opt/slurm .
}

_rhqaddtorepo() {
    cd /tmp/slurm
    local slurmdEndVersion=$(ls *.deb)
    local slurmdEndVersion=${slurmdEndVersion[0]}
    echo "adding $slurmdEndVersion to repository"
    sudo cp $slurmdEndVersion /var/www/html/debian
    cd /var/www/html/debian/
    sudo sh -c "dpkg-scanpackages . | gzip -c9  > Packages.gz"
}

install-slurm() {
    sudo apt remove slurm-wlm slurmd slurmctld slurm-wlm-basic-plugins slurm-client
    cp ~/slurm-rhqueue_20.11.5-1.0_amd64.deb /tmp
    sudo apt install /tmp/slurm-rhqueue_20.11.5-1.0_amd64.deb
    _post-install
}

_post-install() {
    sudo mkdir -p /etc/slurm /etc/slurm/prolog.d /etc/slurm/epilog.d /var/spool/slurmctld /var/spool/slurmd /var/log/slurm /run/slurm/
    sudo chown -R slurm.slurm /etc/slurm /etc/slurm/prolog.d /etc/slurm/epilog.d /var/spool/slurm/ctld /var/spool/slurm/d /var/log/slurm /run/slurm/ /var/spool/slurmctld /var/spool/slurmd
    cd $RHQLOCATION/slurm-install-files/
    sudo cp *.conf /etc/slurm/
    # workaround for copying to munge
    cp *.key /tmp
    sudo cp /tmp/*.key /etc/munge
    sudo cp *.service /etc/systemd/system/
    sudo cp *.service /lib/systemd/system/
    sudo systemctl unmask slurmd
    sudo systemctl unmask slurmctld
}

_run_inplace() {
    local startLoc=$PWD
    "$@"
    cd $startLoc
}

build-slurm-deb() {
    _run_inplace _build-slurm-deb "$@"
}

rhqaddtorepo() {
    _run_inplace _rhqaddtorepo "$@"
}

post-install() {
    _run_inplace _post-install "$@"
}
