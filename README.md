# How to install Bynary

Bynary is a python-based suite of modules that will allow you to connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the modules for this program.  Eg Bynary makes heavy use of `matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `matplotlibin` in our own virtual environment we avoid that issue.

You will need a subscription to the Gaia website if you want to download new data from ESA.

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
```

Let's make sure we have rust installed for astroquery.  Only do this if you have problems.
```
# sudo apt-get install -y curl
# curl https://sh.rustup.rs -sSf | sh
```
Next download the source files from git and run install (enter user name and password from git if requested):
```
git clone https://github.com/SteveBz/Bynary.git
cd Bynary
```
## Now create a virtual environment, enter it and run install.
```
python3 -m venv venv
. venv/bin/activate
. install.sh
```
### (NB to deactivate the virtual environment, if necessary):
```
deactivate
```
Now doubleclick and make sure you can read the details.
## Import stars
This will take a long time depending on the spec of your PC.  A 2020 PC should take a few hours. A 2015 laptop may take a few days, in fact after a week we gave up.

Use tab 1 of the application
## Import binaries
Use tab 2 of the application
