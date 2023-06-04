#!/bin/bash

## Activate your virtual environment:

. venv/bin/activate
## Create data directories.
mkdir bindata
#cd bindata
#mkdir DR3
#cd DR3
#cd ..
## Install python modules:
### Un comment your version of wx
#pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-8  wxPython # debian-8
#pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-10  wxPython   # Linux debian-10
#pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython  # Linux (K)ubuntu-20.04
#pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython  # Linux (K)ubuntu-22.04

pip3 install attrdict3
pip3 install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-23.04 wxPython  # Linux (K)ubuntu-23.04
#pip install -U wxPython # Windows and macOS

#pip3 install numpy
pip3 install wheel
pip3 install matplotlib==3.4.3
pip3 install pandas
#Next line needs rust
pip3 install astroquery
pip3 install dask
pip3 install fdb
python3 -m pip install -r requirements.txt
pip3 install astropy_healpix
pip3 install healpy
pip3 install astropy
#pip3 install sqlalchemy
pip3 install SQLAlchemy==1.4.46
