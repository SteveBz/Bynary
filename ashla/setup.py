import pathlib

from setuptools import setup

__version__ = '0.2.1'

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ashla",
    version=__version__,
    author='zachary.plummer@hotmail.co.uk',
    url="",
    package_data={'ashla': ['vis_app/assets/*']},
    #license='',
    long_description=README,
    long_description_content_type="text/markdown",
    description="A package for researching Wide Binary stars.",
    install_requires=["dash", "numpy", "pandas", "astropy", "astroquery", "plotly"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
