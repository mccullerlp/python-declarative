#!/usr/bin/env python2
"""
"""
from __future__ import division, print_function

import YALL.declarative.argparse as ARG

from YALL.declarative import (
    OverridableObject,
    mproperty,
    NOARG,
)


class APTester(ARG.OOArgParse, OverridableObject):
    """
    Runs the argparse test setup
    """
    @ARG.argparse_arg(['-a', '--abc'])
    @mproperty
    def atest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argparse_arg(['-b', '--btest'], group = '__tgroup__')
    @mproperty
    def btest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argparse_arg(['-c', '--ctest'], group = '__tgroup_ME__')
    @mproperty
    def ctest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argparse_arg(['-d', '--dtest'], group = '__tgroup_ME__')
    @mproperty
    def dtest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.store_true(['-e', '--etest'])
    @mproperty
    def etest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argparse_group(name = 'Test Group')
    @mproperty
    def __tgroup__(self, val = NOARG):
        """
        Group for testing
        """

    @ARG.argparse_group(
        name = 'Test Group2',
        mutually_exclusive = True,
    )
    @mproperty
    def __tgroup_ME__(self, val = NOARG):
        """
        Group for testing Mutual Exclusivity
        """

    @ARG.argparse_command()
    def run2(self, args):
        """
        Command Description
        """
        print("Alternate Run Option!", args)
        return self

    def __arg_default__(self):
        """
        Print various arguments
        """
        print ("atest: ", self.atest)
        print ("btest: ", self.btest)
        print ("ctest: ", self.ctest)
        print ("dtest: ", self.dtest)
        return self


def test_args():
    APTester.__cls_argparse__(['-a', '1234'])


if __name__ == '__main__':
    APTester.__cls_argparse__()

