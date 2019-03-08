# -*- coding: utf-8 -*-
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
from ..utilities.future_from_2 import with_metaclass


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
            #print('attrs2', list(self.__cls_decl_attrs__))
            for attr in attr_list:
                getattr(self, attr)
        else:
            cls = self.__class__
            attr_list = [cls]
            attrs = dir(cls)
            #print('attrs', list(attrs))
            for attr in attrs:
                acls = getattr(self.__class__, attr)
                #the attribute must be a descriptor whose class must have _declarative_instantiation
                #defined, for it to be accessed during init
                decl = getattr(acls.__class__, '_declarative_instantiation', None)
                if decl:
                    getattr(self, attr)
                    attr_list.append(attr)
                elif decl is not None and getattr(acls, '_declarative_instantiation', False):
                    #this checks if the INSTANCE of the descriptor has had _declarative_instantiation
                    #but only checks if the class has that item, so that the
                    #getattr can't fail on weird objects
                    getattr(self, attr)
                    attr_list.append(attr)
            #set to indicate the memoized list of attributes
            cls.__cls_decl_attrs__      = tuple(attr_list)
            #print('attr_list', list(self.__cls_decl_attrs__))
        #print("DECL: ", self)
        return
