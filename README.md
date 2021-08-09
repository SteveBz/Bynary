# How to install Bynary

Bynary is a python-based suitre of modules that will allow you to connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the module for this program.  Eg Bynary makes heavy use of `Matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `Matplotlibin` out own virtual environment we avoid that issue.

You will need a subscription to the gaia website if you want to download new data from esa.

You will also need a Linux-based computer running a currently supported version of Linux.

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
This next bit between the asterisks is only required if the add-apt-repository fails:
*****************************************************
```
# sudo apt update
# sudo apt install -y software-properties-common
```
*****************************************************
```
sudo apt update
sudo apt install -y software-properties-common
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
# Download data
Then to download some data you'll need a star list.  The one provided is eDR3 out to 333 pc.
```
cd bindata
cd eDR3
git clone https://github.com/SteveBz/stars.git
git clone https://github.com/SteveBz/KEB-0.50pc.git
```
And load the data:
# Go ito flamerobin and register binarydb.fdb with details user = SYSDBA
password = matserkey
utf8
SA
# chmod +777 Binaries-DB-30.fdb
