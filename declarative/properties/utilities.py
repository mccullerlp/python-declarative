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
