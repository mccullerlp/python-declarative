# -*- coding: utf-8 -*-
"""
TODO: get licences from python-future
A selection of cross-compatible functions for Python 2 and 3.

This module exports useful functions for 2/3 compatible code:

    * bind_method: binds functions to classes
    * ``native_str_to_bytes`` and ``bytes_to_native_str``
    * ``native_str``: always equal to the native platform string object (because
      this may be shadowed by imports from future.builtins)
    * lists: lrange(), lmap(), lzip(), lfilter()
    * iterable method compatibility:
        - iteritems, iterkeys, itervalues
        - viewitems, viewkeys, viewvalues

        These use the original method if available, otherwise they use items,
        keys, values.

    * types:

        * text_type: unicode in Python 2, str in Python 3
        * binary_type: str in Python 2, bythes in Python 3
        * string_types: basestring in Python 2, str in Python 3

    * bchr(c):
        Take an integer and make a 1-character byte string
    * bord(c)
        Take the result of indexing on a byte string and make an integer
    * tobytes(s)
        Take a text string, a byte string, or a sequence of characters taken
        from a byte string, and make a byte string.
    
    * raise_from()
    * raise_with_traceback()

This module also defines these decorators:

    * ``python_2_unicode_compatible``
    * ``with_metaclass``
    * ``implements_iterator``

Some of the functions in this module come from the following sources:

    * Jinja2 (BSD licensed: see
      https://github.com/mitsuhiko/jinja2/blob/master/LICENSE)
    * Pandas compatibility module pandas.compat
    * six.py by Benjamin Peterson
    * Django
"""
from __future__ import (absolute_import, division, print_function)
import sys

def raise_from_with_traceback(exc, cause = None, traceback = Ellipsis):
    """
    Equivalent to:

        raise EXCEPTION from CAUSE

    on Python 3. (See PEP 3134).

    Raise exception with existing traceback.
    If traceback is not passed, uses sys.exc_info() to get traceback.
    """
    if cause is not None:
        # Is either arg an exception class (e.g. IndexError) rather than
        # instance (e.g. IndexError('my message here')? If so, pass the
        # name of the class undisturbed through to "raise ... from ...".
        if isinstance(exc, type) and issubclass(exc, Exception):
            e = exc()
            # exc = exc.__name__
            # execstr = "e = " + _repr_strip(exc) + "()"
            # myglobals, mylocals = _get_caller_globals_and_locals()
            # exec(execstr, myglobals, mylocals)
        else:
            e = exc
        e.__suppress_context__ = False
        if isinstance(cause, type) and issubclass(cause, Exception):
            e.__cause__ = cause()
            e.__suppress_context__ = True
        elif cause is None:
            e.__cause__ = None
            e.__suppress_context__ = True
        elif isinstance(cause, BaseException):
            e.__cause__ = cause
            e.__suppress_context__ = True
        else:
            raise TypeError("exception causes must derive from BaseException")
        e.__context__ = sys.exc_info()[1]

    if traceback == Ellipsis:
        _, _, traceback = sys.exc_info()
    raise exc, None, traceback

# listvalues and listitems definitions from Nick Coghlan's (withdrawn)
# PEP 496:
def listvalues(d):
    return d.values()
def listitems(d):
    return d.items()

