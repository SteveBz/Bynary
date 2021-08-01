# How to install Bynary

Bynary is a python-based suitre of modules that will allow you yo connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the module for this program.  Eg Bynary makes heavy use of `Matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `Matplotlibin` out own virtual environment we avoid that issue.

# How to install virtualenv:

## Install pip3 first

We want pip3 for python3 modules and git to access github files

```
sudo apt-get install python3-pip
sudo apt-get install git
```
Next download the source files from git and run insstall:
```
git clone https://github.com/SteveBz/Bynary.git
cd Bynary
```
## Now create a virtual environment
```
python3 -m venv venv
. venv/bin/activate
. install.sh
```

### NB to deactivate:
```
deactivate
```
