
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='kash-cookie',
    version='0.1.0',
    description='Generic stock time series',
    long_description=readme,
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')))


