sudo pip3 uninstall -y rhqueue
python3 setup.py bdist_wheel -d /opt/rh-queue
cd /opt/rh-queue
sudo pip3 install rhqueue-0.5-py3-none-any.whl
rm *.whl