#!/bin/bash

## Activate your virtual environment:

. venv/bin/activate
## Create data directories.
mkdir bindata
cd bindata
mkdir eDR3
cd eDR3
cd ../..
## Install python modules:

pip3 install numpy
pip3 install matplotlib
pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
pip3 install pandas
pip3 install astroquery
pip3 install dask
pip3 install fdb
