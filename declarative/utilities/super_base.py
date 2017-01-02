#!/usr/bin/python2
"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)


class SuperBase(object):
    """
    """
    def __init__(self, **kwargs):
        super(SuperBase, self).__init__()
        if kwargs:
            raise RuntimeError(
                (
                    "kwargs has extra items for class {0}, contains: {1}"
                ).format(self.__class__, kwargs)
            )
        return


