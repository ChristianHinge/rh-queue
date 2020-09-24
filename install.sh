sudo -H -u root pip3 uninstall -y rhqueue
python3 setup.py bdist_wheel -d /opt/rh-queue
cd /opt/rh-queue
sudo -H -u root python3 -m pip install rhqueue-0.6-py3-none-any.whl
# rm *.whl