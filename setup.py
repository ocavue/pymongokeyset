#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='pymongokeyset',
    version='0.0.2',
    keywords=('keyset', 'pymongo'),
    description='Offset-free Paging for Pymongo',
    author='ocavue',
    author_email='ocavue@gmail.com',
    url='https://github.com/ocavue/pymongokeyset',
    license='MIT License',
    packages=find_packages(),
    platforms='any',
    install_requires=['pymongo>=3.3.0'],
)
