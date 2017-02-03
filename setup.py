from setuptools import setup, find_packages

with open('README.rst') as f:
    README = f.read()

with open('LICENSE') as f:
    LICENSE = f.read()

setup(
    name='kash-cookie',
    version='0.1.0',
    description='Generic stock time series',
    long_description=README,
    author='Kin Wong',
    author_email='kinhangwong@gmail.com',
    url='',
    license=LICENSE,
    packages=find_packages(exclude=('tests', 'docs')))


