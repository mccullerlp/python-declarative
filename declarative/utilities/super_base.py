#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
#from builtins import object


class SuperBase(object):
    """
    """
    def __new__(cls, *args, **kwargs):
        return super(SuperBase, cls).__new__(cls)

    def __init__(self, **kwargs):
        super(SuperBase, self).__init__()
        if kwargs:
            raise RuntimeError(
                (
                    "kwargs has extra items for class {0}, contains: {1}"
                ).format(self.__class__, kwargs)
            )
        return


