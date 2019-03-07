# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import os
import sys
from os import path
from distutils.command.bdist import bdist
from distutils.command.sdist import sdist

def version_checker(version_string, module_name):

    def check_versions():
        import importlib
        print('versions checked')
        try:
            curpath = path.abspath(path.realpath(os.getcwd()))
            setuppath = path.abspath(path.realpath(path.split(__file__)[0]))

            if curpath != setuppath:
                sys.path.append(setuppath)

            module = importlib.import_module(module_name)

            modfile = path.abspath(path.realpath(path.split(module.__file__)[0]))
            mod_relpath = path.relpath(modfile, setuppath)
            if mod_relpath == module_name:
                if module.__version__ != version_string:
                    print("WARNING: Stated module version different than setup.py version", file = sys.stderr)
                    print("         '{0}' != '{1}'".format(module.__version__, version_string), file = sys.stderr)
                    print("Fix version.py and setup.py for consistency")

            import subprocess
            try:
                git_tag = subprocess.check_output(['git', 'describe', '--tags'])
                git_tag = git_tag.strip()
                git_tag = str(git_tag.decode('utf-8'))
            except subprocess.CalledProcessError:
                pass
            else:
                if git_tag != version_string:
                    if git_tag.startswith(version_string):
                        print("WARNING: latex git-tag has commits since versioning", file = sys.stderr)
                        print("         '{0}' ---> '{1}'".format(version_string, git_tag), file=sys.stderr)
                    else:
                        print("WARNING: latex git-tag different than setup.py version", file = sys.stderr)
                        print("         '{0}' != '{1}'".format(version_string, git_tag), file=sys.stderr)
                    print("         Perhaps update versions in setup.py and module.version, git commit, then git tag")
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
    else:
        cmdclass['bdist_wheel'] = check_bdist_wheel

    return cmdclass

