#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
from setuptools import setup

name='pyruter'
description='Utility for accessing subway information in Oslo, Norway.'
version='1'

author='Benedicte Emilie Brækken'
author_email='b@brkn.io'

packages=['ruter']
install_requires=['requests', 'dateutils']

scripts=[]

setup(name=name,
      version=version,
      description=description,
      author=author,
      author_email=author_email,
      packages=packages,
      install_requires=install_requires,
      scripts=scripts)
