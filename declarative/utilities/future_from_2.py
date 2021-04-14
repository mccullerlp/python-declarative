# -*- coding: utf-8 -*-
"""
Pulls in the future library requirement if running on python2
"""
from __future__ import (absolute_import, division, print_function)
import sys
import warnings

warnings.warn("Compatibility support for python2 has been dropped", DeprecationWarning, stacklevel=2)

if sys.version_info < (3, 0, 0):
    #requires the future library
    from builtins import (
        super,
        object,
        ascii,
        bytes,
        chr,
        dict,
        filter,
        hex,
        input,
        int,
        map,
        next,
        oct,
        open,
        pow,
        range,
        round,
        str,
        zip,
        unicode,
    )

    from future.standard_library import install_aliases
    install_aliases()

    #decode any unicode repr functions as py27 cannot handle them
    def repr_compat(func):
        def __repr__(self, *args, **kwargs):
            return repr(func(self, *args, **kwargs).encode('utf-8').decode('utf-8'))
        #wrap it
        __repr__.__name__ = func.__name__
        __repr__.__doc__ = func.__doc__
        return __repr__
else:
    super   = super
    object  = object
    ascii   = ascii
    bytes   = bytes
    chr     = chr
    dict    = dict
    filter  = filter
    hex     = hex
    input   = input
    int     = int
    map     = map
    next    = next
    oct     = oct
    open    = open
    pow     = pow
    range   = range
    round   = round
    str     = str
    zip     = zip
    unicode = str

    def repr_compat(func):
        return func

PY3 = (sys.version_info[0] == 3)

if PY3:
    from .future3 import (
        raise_from_with_traceback,
    )
else:
    raise NotImplementedError("Support for python2 compatibility has been dropped")

def with_metaclass(meta, *bases):
    """
    Function from jinja2/_compat.py (as included in python-future). License: BSD.
    * Jinja2 (BSD licensed: see https://github.com/mitsuhiko/jinja2/blob/master/LICENSE)

    Use it like this::

        class BaseForm(object):
            pass

        class FormType(type):
            pass

        class Form(with_metaclass(FormType, BaseForm)):
            pass

    This requires a bit of explanation: the basic idea is to make a
    dummy metaclass for one level of class instantiation that replaces
    itself with the actual metaclass.  Because of internal type checks
    we also need to make sure that we downgrade the custom metaclass
    for one level to something closer to type (that's why __call__ and
    __init__ comes back from type etc.).

    This has the advantage over six.with_metaclass of not introducing
    dummy classes into the final MRO.
    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})


object

if PY3:
    object = object
