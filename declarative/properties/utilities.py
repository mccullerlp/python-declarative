"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
import sys

from .bases import (
    PropertyAttributeError,
)

from ..utilities.future import (
    raise_from_with_traceback,
)

def raise_attrerror_from_property(prop, obj, exc):
    """
    Because the exception calls some methods for better error reporting, those methods could be inside of unstable objects, so
    the call itself is wrapped
    """
    _, _, traceback = sys.exc_info()
    try:
        msg = str(exc) + " (within declarative.property named {0} of {1})".format(prop.__name__, repr(obj))
    except Exception:
        msg = str(exc) + " (within declarative.property named {0})".format(prop.__name__)
    raise_from_with_traceback(
        PropertyAttributeError(msg),
        cause = exc,
        traceback = traceback,
    )


def try_name_file_line(func):
    """
        Trashes current exception
    """
    d = dict()
    try:
        d['filename'] = func.__code__.co_filename
    except Exception:
        d['filename'] = '<unknown>'

    try:
        d['lineno'] = func.__code__.co_firstlineno,
    except Exception:
        d['lineno'] = '<unknown>',
    return d


def raise_msg_from_property(msg, t_exc, prop, obj, oldexc = None, **kwargs):
    """
    """
    _, _, traceback = sys.exc_info()
    d = dict(
        name = prop.__name__
    )
    try:
        d['orepr'] = repr(obj)
    except Exception:
        d['orepr'] = '<object of {0}>'.format(obj.__class__.__name__)
    d.update(**kwargs)

    msg = msg.format(**d)

    raise_from_with_traceback(
        t_exc(msg),
        cause = oldexc,
        traceback = traceback,
    )
