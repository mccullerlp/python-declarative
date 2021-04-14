#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import sys
from setuptools import find_packages, setup
import setup_helper

version = '1.3.0'

cmdclass = setup_helper.version_checker(version, 'declarative')

extra_install_requires = []
if sys.version_info < (3, 0):
    extra_install_requires.append('future')

setup(
    name             = 'declarative',
    version          = version,
    url              = 'https://github.com/mccullerlp/python-declarative',
    author           = 'Lee McCuller',
    author_email     = 'Lee.McCuller@gmail.com',
    license          = 'Apache v2',
    packages         = find_packages(exclude = ['docs']),
    description      = (
        'Collection of decorators and base classes to allow a declarative style of programming. Excellent for event-loop task registration.'
        'Also included are nesting attribute-access dictionaries (Bunches) as well as value storage with callbacks. Relatively Magic-Free.'
    ),
    install_requires =[] + extra_install_requires,
    extras_require   ={
        "hdf" : ["h5py"],
    },
    tests_require=['pytest'],
    test_suite   = 'pytest',
    cmdclass         = cmdclass,
    zip_safe         = True,
    keywords         = [
        'declarative',
        'oop',
        'bunch',
        'callback',
        'attributes',
        'metaclass',
    ],
    classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

