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
PY3 = sys.version_info[0] == 3

if PY3:
    from .future3 import (
        raise_from_with_traceback,
    )
else:
    from .future2 import (
        raise_from_with_traceback,
    )

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
    class object:
        pass
