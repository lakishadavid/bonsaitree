from setuptools import setup, find_packages, Extension

NAME = "bonsaitree"
VERSION = "3.0.0"  # Manual versioning - v3 with BAGG modifications
DESCRIPTION = "Python package for building pedigrees."

README = open("README.md", 'r').read()
LICENSE = open("LICENSE.txt", 'r').read()

setup(
    name=NAME,
    version=VERSION,
    author="23andMe Engineering",
    author_email="ejewett@23andme.com",
    description=DESCRIPTION,
    license=LICENSE,
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={NAME: ["models/*.json"]},
    include_package_data=True,
    url="https://github.com/lakishadavid/" + NAME,
    zip_safe=True,
    install_requires=["funcy", "numpy", "scipy", "six"],
    #ext_modules=[
    #    Extension("bonsaitree.copytools", sources=["bonsaitree/copytools.pyx"])
    #],
)
