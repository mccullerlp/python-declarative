# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
try:
    from collections.abc import Mapping as MappingABC
except ImportError:
    from collections import Mapping as MappingABC
from ..utilities.future_from_2 import str, unicode


class QuickBunch(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val
        return

    def __dir__(self):
        dir_lst = list(super(QuickBunch, self).__dir__())
        dir_lst = dir_lst + list(k for k in self.keys() if isinstance(k, (str, unicode)))
        dir_lst.sort()
        return dir_lst

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def get(self, name, *default):
        return super(QuickBunch, self).get(name, *default)

MappingABC.register(QuickBunch)

