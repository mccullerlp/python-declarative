# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from collections import Mapping


class QuickBunch(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val
        return

    def __dir__(self):
        dir_lst = list(super(QuickBunch, self).__dir__())
        dir_lst = dir_lst + list(self.keys)
        dir_lst.sort()
        return dir_lst

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

    def get(self, name, *default):
        return super(QuickBunch, self).get(name, *default)

Mapping.register(QuickBunch)

