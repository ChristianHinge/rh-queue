cd /homes/pmcd/rh-queue
rm -rf ./build
sudo -H -u root pip3 uninstall -y rhqueue
python3 setup.py bdist_wheel -d /opt/rh-queue
sudo -H -u root python3 -m pip install /opt/rh-queue/rhqueue-1.0-py3-none-any.whl --no-cache
rm /homes/pmcd/.local/bin/rhqueue
rm /homes/pmcd/.local/bin/rhqemail
# rm *.whl