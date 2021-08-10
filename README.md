# How to install Bynary

Bynary is a python-based suitre of modules that will allow you to connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the module for this program.  Eg Bynary makes heavy use of `matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `matplotlibin` out own virtual environment we avoid that issue.

You will need a subscription to the Gaia website if you want to download new data from ESA.

You will also need a Linux-based computer running a currently supported version of Linux.
It needs a solid state hard disk with about 20GB free and at least 16GB of memory, 32GB is better.

# How to install virtualenv:

## Install pip3 first

We want pip3 for python3 modules and git to access github files

```
sudo apt-get install -y python3-venv
sudo apt-get install -y python3-pip
sudo apt-get install -y git
sudo apt-get install -y libwebkit2gtk-4.0-dev
sudo apt-get install -y unixodbc
```
Install firebird database and flamerobin to update it (if you need to).
This commented out bit between the lines is only required if the add-apt-repository fails:
*****************************************************
```
# sudo apt update
# sudo apt install -y software-properties-common
# sudo add-apt-repository ppa:mapopa/firebird3.0
```
*****************************************************
```
sudo add-apt-repository ppa:mapopa/firebird3.0
sudo apt update
# Set up with password 'masterkey'
sudo apt install -y firebird3.0-server
sudo apt-get install -y flamerobin
```
Let's make sure we have rust installed for astroquery
```
sudo apt-get install -y curl
curl https://sh.rustup.rs -sSf | sh
```
Next download the source files from git and run install (enter user name and password from git if requested):
```
git clone https://github.com/SteveBz/Bynary.git
cd Bynary
sudo chmod +777 binarydb.fdb
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
# Download & import some data
Then to download some data you'll need a star list.  The one provided is eDR3 out to 333 pc.
```
cd bindata
cd eDR3
git clone https://github.com/SteveBz/stars.git
git clone https://github.com/SteveBz/KEB-0.50pc.git
```
And load the database:
- Go into flamerobin and register binarydb.fdb with details:
-- user name = SYSDBA
-- password = masterkey
-- role = SA
-- charset = utf8
Now doubleclick and make sure you can read the details.
## Import stars
This will take a long time depending on the spec of your PC.  A 2020 PC should take a few hours. A 2015 laptop may take a few days!
```
. venv/bin/activate
python3 -convertGaiav2_8.py
```
## Import binaries
```
. venv/bin/activate
python3 -convertGaia_veDR3.1d.py
```
