# -*- coding: utf-8 -*-
"""Setup file for the package"""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='yawps',
    description='Yet Another Workflow Parser for SecurityHub',
    author='Marcus Young',
    author_email='myoung34@my.apsu.edu',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['yawps'],
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'boto3==1.18.48',
        'botocore==1.21.48',
        'certifi==2022.12.7',
        'charset-normalizer==2.0.6',
        'idna==3.2',
        'jmespath==0.10.0',
        'python-dateutil==2.8.2',
        'requests==2.26.0',
        's3transfer==0.5.0',
        'six==1.16.0',
        'slacker==0.14.0',
        'urllib3==1.26.7'
    ],
)
