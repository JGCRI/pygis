"""
@author   Chris R. Vernon
@email:   chris.vernon@pnnl.gov
@Project: pygis
License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2017, Battelle Memorial Institute
"""
import sys


class VersionError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

try:
    from setuptools import setup, find_packages
except ImportError:
    raise("Must have setuptools installed to run setup.py. Please install and try again.")


def readme():
    with open('README.md') as f:
        return f.read()


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().split()


setup(
    name='pygis',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/JGCRI/pygis.git',
    license='BSD 2-Clause',
    author='Chris R. Vernon',
    author_email='chris.vernon@pnnl.gov',
    description='Python-based Geographic Information System (GIS) utilities',
    long_description=readme(),
    install_requires=get_requirements()
)
