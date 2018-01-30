#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import os
import sys
from os import path
from setuptools import find_packages, setup
from distutils.command.bdist import bdist
from distutils.command.sdist import sdist

version = '1.0.1.dev2'

def check_versions():
    print('versions checked')
    try:
        curpath = path.abspath(path.realpath(os.getcwd()))
        setuppath = path.abspath(path.realpath(path.split(__file__)[0]))

        if curpath != setuppath:
            sys.path.append(setuppath)
        import declarative

        modfile = path.abspath(path.realpath(path.split(declarative.__file__)[0]))
        mod_relpath = path.relpath(modfile, setuppath)
        if mod_relpath == 'declarative':
            if declarative.__version__ != version:
                print("WARNING: Stated module version different than setup.py version", file = sys.stderr)
                print("         '{0}' != '{1}'".format(declarative.__version__, version), file = sys.stderr)
                print("Fix version.py and setup.py for consistency")

        import subprocess
        try:
            git_tag = subprocess.check_output(['git', 'describe', '--tags'])
            git_tag = git_tag.strip()
            git_tag = str(git_tag)
        except subprocess.CalledProcessError:
            pass
        else:
            if git_tag != version:
                if git_tag.startswith(version):
                    print("WARNING: latex git-tag has commits since versioning", file = sys.stderr)
                    print("         '{0}' ---> '{1}'".format(version, git_tag), file=sys.stderr)
                else:
                    print("WARNING: latex git-tag different than setup.py version", file = sys.stderr)
                    print("         '{0}' != '{1}'".format(version, git_tag), file=sys.stderr)
                print("         Perhaps update versions in setup.py and declarative.version, git commit, then git tag")
                print("         otherwise fix tag if not yet git pushed to remote (see DISTRIBUTION-README.md)")

    except ImportError:
        pass


cmdclass = dict()

class check_bdist(bdist):
    def run(self):
        bdist.run(self)
        check_versions()

class check_sdist(sdist):
    def run(self):
        sdist.run(self)
        check_versions()


cmdclass['bdist'] = check_bdist
cmdclass['sdist'] = check_sdist

try:
    from wheel.bdist_wheel import bdist_wheel
    class check_bdist_wheel(bdist_wheel):
        def run(self):
            bdist_wheel.run(self)
            check_versions()
except ImportError:
    pass

cmdclass['bdist_wheel'] = check_bdist_wheel


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
        "test" : ["pytest"],
    },
    cmdclass         = cmdclass,
    zip_safe         = True,
    keywords         = 'declarative, oop, bunch, callback, attributes, metaclass',
    classifiers      = [
        'Development Status :: 3 - Alpha ',
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
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

