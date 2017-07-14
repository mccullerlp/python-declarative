#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, absolute_import
import sys
import importlib

if __name__ == '__main__':
    script = sys.argv[1]
    args = sys.argv[2:]

    split_idx = script.rfind('.')
    mod   = script[:split_idx]
    t_obj = script[split_idx+1:]
    print("Importing module: ", mod)
    module = importlib.import_module(mod)
    print("Getting Class: ", t_obj)

    cls = getattr(module, t_obj)

    cls.__cls_argparse__(
        args,
        __usage_prog__ = 'python -m declarative.run {0}'.format(script),
    )
