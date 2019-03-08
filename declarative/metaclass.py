#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from builtins import object
import warnings
from .utilities.future_from_2 import with_metaclass, str, unicode


class AutodecorateMeta(type):
    def __init__(cls, name, bases, dct):
        super(AutodecorateMeta, cls).__init__(name, bases, dct)

        ad_calls = []
        for base in cls.__mro__:
            ad_call = base.__dict__.get('__mc_autodecorators__', None)
            if ad_call is not None:
                ad_calls.append(ad_call)

        decorators = []
        for ad_call in ad_calls:
            decorators = ad_call.__get__(None, cls)(decorators)

        for deco in decorators:
            cls2 = deco(cls)
            if cls2 is not cls:
                raise RuntimeError("Autodecorators cannot actually replace object, modification only")
        return


class Autodecorate(with_metaclass(AutodecorateMeta)):

    ##this __init__ stub is needed or the init of 'object' is used!
    #def __init__(self, *args, **kwargs):
    #    super(Autodecorate, self).__init__(*args, **kwargs)

    @classmethod
    def __mc_autodecorators__(cls, decorators):
        return decorators


def class_expand(cls):
    cls._attributes_expand_units()
    return cls


class AttrExpandingObject(Autodecorate):
    _cls_getsetattr_expansion = dict()
    _cls_getsetattr_expansion_called = None

    @classmethod
    def __mc_autodecorators__(cls, decorators):
        decorators.append(class_expand)
        return decorators

    @classmethod
    def _attributes_expand_units(cls):
        expansion = dict()
        for k in dir(cls):
            v = getattr(cls, k)
            try:
                expand = v.__generate_virtual_descriptors__
            except AttributeError:
                continue
            expansion.update(expand())
        cls._cls_getsetattr_expansion = expansion
        cls._cls_getsetattr_expansion_called = cls
        return cls

    if __debug__:
        def __init__(self, *args, **kwargs):
            if self._cls_getsetattr_expansion_called is not self.__class__:
                self._attributes_expand_units()
                warnings.warn("Need to add class decorator \"class_expand\"")
            super(AttrExpandingObject, self).__init__(*args, **kwargs)

    def _overridable_object_inject(self, **kwargs):
        kwargs = super(AttrExpandingObject, self)._overridable_object_inject(**kwargs)
        kwargs_remaining = dict()
        while kwargs:
            k, v = kwargs.popitem()
            desc = self._cls_getsetattr_expansion.get(k, None)
            if desc is None:
                kwargs_remaining[k] = v
            else:
                desc.__set__(self, v)
        return kwargs_remaining

    def __getattr__(self, name):
        expand = self._cls_getsetattr_expansion.get(name, None)
        if expand is not None:
            genval = expand.__get__(self, self.__class__)
            self.__dict__[name] = genval
            return genval
        else:
            return super(AttrExpandingObject, self).__getattr__(name)

    def __dir__(self):
        predir = dir(super(AttrExpandingObject, self))
        predir.extend(k for k in self._cls_getsetattr_expansion.keys() if isinstance(k, (str, unicode)))
        predir.sort()
        return predir


#separated because __setattr__ is so much more advanced and awful than __getattr__ overloading
class GetSetAttrExpandingObject(AttrExpandingObject):
    def __setattr__(self, name, val):
        assert(isinstance(name, (str, unicode)))
        expand = self._cls_getsetattr_expansion.get(name, None)
        if expand is None:
            return super(GetSetAttrExpandingObject, self).__setattr__(name, val)
        else:
            return expand.__set__(self, self.__class__, val)



