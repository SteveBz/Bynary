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
### Un comment your version of wx
#pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-8  wxPython
pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-10  wxPython
#pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython
pip3 install numpy
pip3 install matplotlib
pip3 install pandas
#Next line needs rust
pip3 install astroquery
pip3 install dask
#pip3 install fdb
python3 -m pip install -r requirements.txt
