#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
import os
import sys
from distutils.sysconfig import get_python_lib

from setuptools import find_packages, setup


version = '1.0.0dev1'


#TODO, must warn packagers about future2.py and future3.py



setup(
    name='declarative',
    version=version,
    url='',
    author='Lee McCuller',
    author_email='Lee.McCuller@gmail.com',
    description=(
        'Collection of decorators and base classes to allow a declarative style of programming. Excellent for event-loop task registration.'
        'Also included are nesting attribute-access dictionaries (Bunches) as well as value storage with callbacks. Relatively Magic-Free.'
    ),
    license='Apache v2',
    packages=find_packages(exclude=['doc']),
    #include_package_data=True,
    #scripts=[''],
    #entry_points={'console_scripts': ['',]},
    install_requires=[],
    extras_require={
        "hdf" : ["h5py"],
        "test" : ["pytest"],
    },
    zip_safe=False,
    keywords = 'declarative oop bunch callback attributes metaclass',
    classifiers=[
        'Development Status :: 3 - Alpha ',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        #'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.4',
        #'Programming Language :: Python :: 3.5',
        #'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

