# How to install Bynary

Bynary is a python-based suitre of modules that will allow you yo connect and download binary stars from Gaia based on an algorithm from Kareem El Badry at Berkley.  We have modified it slightly to make it more general, however you can add parameters as you like, or you can download the pre-processed catalogues.

Firstly we need a vitual environment so that any exiting python programs aren't disrupted by the module for this program.  Eg Bynary makes heavy use of `Matplotlib`, if you use an earlier or later version in another module, that could create issues.  By installing  `Matplotlibin` out own virtual environment we avoid that issue.

# How to install virtualenv:

## Install pip3 first

We want pip3.

```
sudo apt-get install python3-pip
```
## Then install virtualenv using pip3
```
pip3 install virtualenv
```
Next download the source files from git and run insstall:
```
gh repo clone https://github.com/SteveBz/Bynary.git
cd Bynary
```
## Now create a virtual environment
```
virtualenv python3 venv
install.sh
```

### NB to deactivate:
```
deactivate
```
