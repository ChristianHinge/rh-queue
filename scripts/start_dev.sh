rhqinstall() {
  cd /homes/pmcd/rh-queue
  rm -rf ./build
  python3 setup.py bdist_wheel -d /opt/rh-queue
  sudo -H -u root python3 -m pip install --upgrade /opt/rh-queue/*.whl --no-cache
  rm /homes/pmcd/.local/bin/rhqueue
  rm /homes/pmcd/.local/bin/rhqemail
  rm /opt/rh-queue/*.whl
}
rhqtest() {
  cd ~/rh-queue/testfiles
  deactivate
  for var in "$@"; do
    python3 "run_${var}_tests.py"
  done
  rhqstart
}
rhqstart() {
  source ~/venv/rhqueue/bin/activate
  cd ~/rh-queue
  pip3 install -e .
}
rhqstop() {
  deactivate
}
