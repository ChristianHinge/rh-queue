#!/bin/bash
activate () {
    . /homes/pmcd/venv/rhqueue/bin/activate
}
case $1 in
  "install" | "update")
    cd /homes/pmcd/rh-queue
    rm -rf ./build
    python3 setup.py bdist_wheel -d /opt/rh-queue
    sudo -H -u root python3 -m pip install --upgrade /opt/rh-queue/rhqueue-1.0-py3-none-any.whl --no-cache
    rm /homes/pmcd/.local/bin/rhqueue
    rm /homes/pmcd/.local/bin/rhqemail
    ;;
  "start")
    set -e
    source /homes/pmcd/venv/rhqueue/bin/activate
    ;;
  *)
    echo $1
esac