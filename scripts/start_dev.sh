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

slurm-update-conf() {
    cd $RHQLOCATION/slurm-install-files/
    sudo cp slurm.conf /etc/slurm-llnl
    sudo cp gres.conf /etc/slurm-llnl
    cd $OLDPWD
}

rhqcheck-version() {
    for server in "${Servers[@]}"; do
        echo $server
        ssh $server -t "rhqueue -V"
    done
}

_prep-prerequisites() {
    sudo apt-get update
    sudo apt-get install -y git gcc make ruby ruby-dev libpam0g-dev libmunge-dev libmunge2 munge
    cd /opt
    sudo gem install fpm
}

_build-slurm-deb() {
    _prep-prerequisites
    rhqbuild
    mkdir -p /tmp/slurm /opt/slurm
    cd /tmp/slurm
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
    ./configure --prefix=/tmp/slurm-build --sysconfdir=/etc/slurm --enable-pam --with-pam_dir=$pamLocation --without-shared-libslurm
    make -j4
    make contrib -j4
    make install -j4
    cd ..
    fpm -s dir -t deb -v ${slurmdEndVersion#slurm-} -n slurm --prefix=/usr -C /tmp/slurm-build .
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