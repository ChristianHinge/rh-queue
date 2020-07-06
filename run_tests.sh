#!/bin/bash
pip install --no-cache .
cd testfiles/
python3 tests.py
rm *.stdout
cd ..