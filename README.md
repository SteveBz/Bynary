# How to install Bynary

Bynary is a python-based suite of modules that will allow you to connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the modules for this program.  Eg Bynary makes heavy use of `matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `matplotlibin` in our own virtual environment we avoid that issue.

You will need a subscription to the Gaia website to download data from ESA.

You will also need a Linux-based computer running a currently supported version of Linux with Python 3.8+. We are both using Kubuntu 20.04.  It needs a solid state hard disk with about 20GB free and at least 16GB of memory, 32GB is better.  One of us uses an i7 the other uses an i9x2.  Both are adequate.  The i9x2 is good.  However, downloading stuff from Gaia still take an appreciable time, maybe several hours per download (to execute on Gaia and download).  

# How to install virtualenv:

## Install pip3 first

We want pip3 for python3 modules and git to access github files

```
sudo apt-get install -y python3-venv
sudo apt-get install -y python3-pip
sudo apt-get install -y git
sudo apt-get install -y libwebkit2gtk-4.0-dev
#sudo apt-get install -y unixodbc
sudo apt-get install -y sqlite3
```

Let's make sure we have rust installed for astroquery.  Only do this if you have problems.
```
# sudo apt-get install -y curl
# curl https://sh.rustup.rs -sSf | sh
```
Next download the source files from git and run install (enter user name and password from git if requested):
```
git clone https://github.com/SteveBz/Bynary.git <dir name>
cd <dir name>
```
## Now create a virtual environment, enter it and run install.
```
python3 -m venv venv
. venv/bin/activate
. install.sh
```

## To execute the application:
```
cd <dir name>
. venv/bin/activate
python3 wxBinary_v2_09.py
```
### (NB to deactivate the virtual environment, if necessary):
```
deactivate
```
Now doubleclick and make sure you can read the details.
## Import stars and star attributes from Gaia
This will take a long time depending on the spec of your PC.  A 2020 PC should take a few hours. A 2015 laptop may take a few days, in fact after a week we gave up.

Use tab 1 of the application to download lists of stars and their attributes from Gaia (eg RA/DEC, Parallax, proper motion, magnitudes at different wavelengths, RUWE, binary probablility, mass and age calculated from the Gaia FLAME spectrometer etc etc etc).

This is stored on your local database in SQLite.
## Import lists of binary pairs from Gaia
Use tab 2 of the application.  This is also stored on your local datbase in a catalogue.  You can create and download many catalogues according to different selection criteria.
## Load to memory
Use tab 3 of the application to load a catalogue into memory.  Bynary uses Pandas dataframes to speed up the processing af large amounts of data.  Much processing takes place at dataframe level and not at item (star or binary pair) level.
## Filter to clean up catalogues.
Use tab 4 of the application to apply various filters (eg signal to noise ratios) to your catalogue.  You can quickly reduce a catalogue of several million pairs to a few hundred very clean pairs.

## Remaining tabs
The remaining tabs allow you to create various plots and even more second order filters to obtain further information about the downloaded selection of binaries.  The final tab links to Aladin Lite in Strasborg to view a specified, selected binary to validate assumptions.  For instance, you can see if the stellar neighbourhood is clear and uninfluenced by other stars or is a busy area in the plane of the Milky Way or star cluster.
