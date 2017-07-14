#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test of the argparse library

TODO: use automated features
"""
from __future__ import (division, print_function, absolute_import)

from declarative import (
    OverridableObject,
    mproperty,
    NOARG,
)

import declarative.argparse as ARG

import pytest


oldprint = print
print_test_list = []
def print(*args):
    oldprint(*args)
    if len(args) == 1:
        print_test_list.append(args[0])
    else:
        print_test_list.append(args)


class TArgParse(ARG.OOArgParse, OverridableObject):
    """
    Runs the argparse test setup
    """
    @ARG.argument(['-a', '--abc'])
    @mproperty
    def atest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argument(['-b', '--btest'], group = '__tgroup__')
    @mproperty
    def btest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argument(['-c', '--ctest'], group = '__tgroup_ME__')
    @mproperty
    def ctest(self, val = NOARG):
        """
        Test the documentation.
        """
        if val is NOARG:
            val = 'default'
        return val

    @ARG.argument(['-d', '--dtest'], group = '__tgroup_ME__')
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

    @ARG.group(name = 'Test Group')
    @mproperty
    def __tgroup__(self, val = NOARG):
        """
        Group for testing
        """

    @ARG.group(
        name = 'Test Group2',
        mutually_exclusive = True,
    )
    @mproperty
    def __tgroup_ME__(self, val = NOARG):
        """
        Group for testing Mutual Exclusivity
        """

    @ARG.command()
    def run2(self, args):
        """
        Command Description
        """
        print("run2!", args)
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
    print_test_list[:] = []
    TArgParse.__cls_argparse__(['-a', '1234'])
    assert(
        print_test_list == [
            ("atest: ", '1234'),
            ("btest: ", 'default'),
            ("ctest: ", 'default'),
            ("dtest: ", 'default'),
        ]
    )

    print_test_list[:] = []
    TArgParse.__cls_argparse__(['-a', '1234', 'run2'])
    assert(
        print_test_list == [
            ("run2!", []),
        ]
    )

    print_test_list[:] = []
    TArgParse.__cls_argparse__(['-a', '1234', 'run2', 'a', '-b', 'c'])
    assert(
        print_test_list == [
            ("run2!", ['a', '-b', 'c']),
        ]
    )

    print_test_list[:] = []
    with pytest.raises(SystemExit):
        TArgParse.__cls_argparse__(['run_broke'])

    return

if __name__ == '__main__':
    TArgParse.__cls_argparse__()

