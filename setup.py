#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

import sys
sys.path.insert(0, './src/')

import pamface

setup(
    name            = 'libpam-face',
    version         = pamface.__version__,
    description     = 'Face Unlocker for Linux Pluggable Authentication Module (PAM)',
    author          = 'Harishankar Sivaji',
    package_dir     = {'': 'src'},
    packages        = ['pamface'],
)
