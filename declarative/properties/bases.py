"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
#from builtins import object

import abc

from ..utilities import SuperBase
from ..utilities.future import with_metaclass


class PropertyTransforming(with_metaclass(abc.ABCMeta, object)):
    @abc.abstractmethod
    def construct(
        self,
        parent,
        name,
    ):
        return


#TODO rename PropertyException
class InnerException(Exception):
    """
    Exception holder class that allows one to see inside of the functional properties when they throw and error,
    even if outer logic is catching exceptions.

    These should never be caught as they always indicate bugs
    """
    pass


class PropertyAttributeError(Exception):
    """
    Exception indicating an AttributeError inside of a declarative property. AttributeError is masked so
    that it is not confused with the property name itself being a missing attribute.
    """
    pass


class HasDeclaritiveAttributes(SuperBase):
    """
    This base class allows class instances to automatically constructs instance objects declared using
    the :obj:`~.declarative_instantiation`. Declarations using that decorator and this subclass have an advantage
    in that instantiation order doesn't matter, because instantiation happens as needed via the memoization
    quality of declarative_instantiation attributes, and all attributes are instantiated via the qualities of
    this class.

    .. note:: Subclasses must use cooperative calls to `super().__init__`
    """
    __boot_dict__ = None
    __cls_decl_attrs__ = (object,)
    def __init__(self, **kwargs):
        #TODO memoize this list
        super(HasDeclaritiveAttributes, self).__init__(**kwargs)
        attr_list = iter(self.__cls_decl_attrs__)
        #check that the first item is this class, if not then it must have pulled a parent's list
        if next(attr_list) == self.__class__:
            for attr in attr_list:
                getattr(self, attr)
        else:
            cls = self.__class__
            attr_list = [cls]
            attrs = dir(cls)
            for attr in attrs:
                if getattr(getattr(self.__class__, attr), '_declarative_instantiation', False):
                    getattr(self, attr)
                    attr_list.append(attr)
            #set to indicate the memoized list of attributes
            cls.__cls_decl_attrs__      = tuple(attr_list)
        return