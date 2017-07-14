# -*- coding: utf-8 -*-
"""
.. autoclass:: ReprMixin

.. autofunction:: bool_string_interpret
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import repr_compat
from .super_base import SuperBase


class ReprMixin(SuperBase):
    """
        A :term:`mixin` class inherited in front of/instead of object which gives
        any object a decent __repr__ function. The object can additionally define a list in one of
        __slots__ or __repr_slots__ which gives attributes for this repr function to report.

        If __repr_slots__ is given, it will take precedence over any __slots__. For extended inheritance
        heirerarchies, the attributes are stacked, with superclass attributes listed before subclass
        attributes.

        .. attribute:: __repr_slots__

            This is a list of the attribute names for the repr to display. One should be placed in
            any subclass using this mixin that needs specific members displayed.

        .. automethod:: __repr__
    """
    __slots__      = ()
    __repr_slots__ = ()

    @repr_compat
    def __repr__(self):
        attr_names = []
        attr_names_set = set()

        #find the list of attributes to use
        for parent_class in self.__class__.__mro__:
            if hasattr(parent_class, "__repr_slots__"):
                attr_names.extend((attrname for attrname in parent_class.__repr_slots__ if attrname not in attr_names_set))
                attr_names_set.update(parent_class.__repr_slots__)
            elif hasattr(parent_class, "__slots__"):
                attr_names.extend((attrname for attrname in parent_class.__slots__ if attrname not in attr_names_set))
                attr_names_set.update(parent_class.__slots__)

        #extract the attributes, allowing missing ones
        items = []
        for attrname in attr_names:
            attr_value = self
            try:
                for subattr in attrname.split('.'):
                    attr_value = getattr(attr_value, subattr)
            except AttributeError:
                attr_value = ':unset:'
            items.append((attrname, repr(attr_value)))

        #paste the attributes together
        attr_listing = ', '.join(("%s=%s" % attr_descr for attr_descr in items))
        return "%s(%s)" % (self.__class__.__name__, attr_listing)


def bool_string_interpret(val_str, default_value = None):
    """
    Interprets
    """
    if val_str.upper() in ('T', 'TRUE', '1', 'Y', 'YES', 'AFFIRMATIVE'):
        return True
    elif val_str.upper() in ('F', 'FALSE', '0', 'N', 'NO', 'NEGATORY'):
        return False
    elif default_value is None:
        raise ValueError('Bool Value unrecognized {0}'.format(val_str))
    return default_value




