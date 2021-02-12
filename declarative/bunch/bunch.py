# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function, unicode_literals)
from ..utilities.future_from_2 import str, object, dict, repr_compat, unicode

try:
    from collections.abc import Mapping as MappingABC
    from collections.abc import MutableSequence as MutableSequenceABC
except ImportError:
    from collections import MutableSequence as MutableSequenceABC
    from collections import Mapping as MappingABC

import numpy as np
import copy

def try_remove(d, o):
    try:
        d.remove(o)
    except ValueError:
        pass


def gen_func(mname):
    def func(self, *args, **kwargs):
        return getattr(self._mydict, mname)(*args, **kwargs)
    orig_func = getattr(dict, mname)
    if orig_func is None:
        return
    func.__name__ = orig_func.__name__
    func.__doc__  = orig_func.__doc__
    return func


class Bunch(object):
    """
    Cookbook method for creating bunches

    Often we want to just collect a bunch of stuff together, naming each
    item of the bunch; a dictionary's OK for that, but a small do-nothing
    class is even handier, and prettier to use.  Whenever you want to
    group a few variables:

      >>> point = Bunch(datum=2, squared=4, coord=12)
      >>> point.datum

    taken from matplotlib's cbook.py

    By: Alex Martelli
    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
    """
    def __init__(self, inner_dict = None, *args, **kwds):
        if inner_dict is None or args or kwds:
            if args:
                _mydict = dict(inner_dict, *args, **kwds)
            else:
                _mydict = dict(**kwds)
        else:
            _mydict = inner_dict
        self.__dict__['_mydict'] = _mydict
        return

    @classmethod
    def as_bunch(cls, data):
        if isinstance(data, cls):
            return data
        return cls(data)

    @repr_compat
    def __repr__(self):
        keys = list(self._mydict.keys())
        return '{0}({1})'.format(
            self.__class__.__name__,
            ', \n    '.join([''.join((str(k), '=', repr(self._mydict[k]))) for k in keys])
        )

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text('Bunch(<recurse>)')
        else:
            with p.group(4, 'Bunch(', ')'):
                first = True
                for k, v in sorted(self._mydict.items()):
                    if not first:
                        p.text(',')
                        p.breakable()
                    else:
                        p.breakable()
                        first = False
                    if isinstance(k, str):
                        p.text(k)
                    else:
                        p.pretty(k)
                    p.text(' = ')
                    p.pretty(v)
                if not first:
                    p.text(',')
                    p.breakable()
        return

    def __dir__(self):
        items = [k for k in self._mydict.keys() if isinstance(k, (str, unicode))]
        #items += dir(super(Bunch, self))
        return items

    def __getitem__(self, key):
        if isinstance(key, (slice, np.ndarray, MutableSequenceABC)):
            rebuild = dict()
            for vkey, val in self._mydict.items():
                if isinstance(val, np.ndarray):
                    val = val[key]
                    rebuild[vkey] = val
            if not rebuild:
                raise RuntimeError("Not holding arrays to index by {0}".format(key))
            return Bunch(rebuild)
        else:
            return self._mydict[key]

    def domain_sort(self, key):
        argsort = np.argsort(self[key])
        return self[argsort]

    def __getattr__(self, key):
        #item = super(Bunch, self).__getattribute__(key)
        try:
            item = self._mydict[key]
        except KeyError as E:
            raise AttributeError(E)
        if type(item) is dict:
            return self.__class__(item)
        return item

    def __setattr__(self, key, item):
        self._mydict[key] = item
        return

    def __delattr__(self, key):
        del self._mydict[key]

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(self._mydict, memo))

    def copy(self):
        return self.__class__(self._mydict.copy())

    __contains__ = gen_func('__contains__')
    __eq__       = gen_func('__eq__')
    __format__   = gen_func('__format__')
    __ge__       = gen_func('__ge__')
    __gt__       = gen_func('__gt__')
    __iter__     = gen_func('__iter__')
    __le__       = gen_func('__le__')
    __len__      = gen_func('__len__')
    __lt__       = gen_func('__lt__')
    __ne__       = gen_func('__ne__')
    __setitem__  = gen_func('__setitem__')
    __sizeof__   = gen_func('__sizeof__')
    __str__      = gen_func('__str__')
    clear        = gen_func('clear')
    fromkeys     = gen_func('fromkeys')
    get          = gen_func('get')
    items        = gen_func('items')
    keys         = gen_func('keys')
    pop          = gen_func('pop')
    popitem      = gen_func('popitem')
    setdefault   = gen_func('setdefault')
    update       = gen_func('update')
    values       = gen_func('values')


class WriteCheckBunch(object):
    def __setitem__(self, key, item):
        prev = self._mydict.setdefault(key, item)
        if prev != item:
            raise RuntimeError("Inconsistent Data")
        return

    def __setattr__(self, key, item):
        prev = self._mydict.setdefault(key, item)
        if prev != item:
            raise RuntimeError("Inconsistent Data")
        return


class FrozenBunch(Bunch):
    """
    """
    def __init__(self, inner_dict = None, *args, **kwds):
        if inner_dict is None or args or kwds:
            if args:
                _mydict = dict(inner_dict, *args, **kwds)
            else:
                _mydict = dict(**kwds)
        else:
            _mydict = dict(inner_dict)
        self.__dict__['_mydict'] = _mydict
        return

    @classmethod
    def as_bunch(cls, data):
        if isinstance(data, cls):
            return data
        return cls(data)

    def __hash__(self):
        try:
            return self.__dict__['__hash']
        except KeyError:
            pass
        l = tuple(sorted(self._mydict.items()))
        self.__dict__['__hash'] = hash(l)
        return self.__dict__['__hash']

    def __pop__(self, key):
        raise RuntimeError("Bunch is Frozen")

    def __popitem__(self, key):
        raise RuntimeError("Bunch is Frozen")

    def __clear__(self, key):
        raise RuntimeError("Bunch is Frozen")

    def __setitem__(self, key, item):
        raise RuntimeError("Bunch is Frozen")

    def __setattr__(self, key, item):
        raise RuntimeError("Bunch is Frozen")

    def __delattr__(self, key):
        raise RuntimeError("Bunch is Frozen")

    def __deepcopy__(self, memo):
        return self.__class__(copy.deepcopy(self._mydict, memo))


MappingABC.register(Bunch)
MappingABC.register(FrozenBunch)
MappingABC.register(WriteCheckBunch)

class HookBunch(Bunch):

    def __init__(
            self,
            inner_dict = None,
            insert_hook = None,
            replace_hook = None,
            delete_hook = None,
            *args,
            **kwds
    ):
        super(HookBunch, self).__init__(inner_dict = inner_dict, *args, **kwds)
        self.__dict__['insert_hook']  = insert_hook
        self.__dict__['replace_hook'] = replace_hook
        self.__dict__['delete_hook']  = delete_hook
        return

    def __getattr__(self, key):
        #item = super(Bunch, self).__getattribute__(key)
        try:
            item = self[key]
        except KeyError as E:
            raise AttributeError(E)
        if type(item) is dict:
            return self.__class__(item)
        return item

    def __setattr__(self, key, item):
        self[key] = item
        return

    def __delattr__(self, key):
        del self[key]

    def __setitem__(self, key, item):
        try:
            prev = self._mydict[key]
        except KeyError:
            if self.insert_hook is None:
                raise RuntimeError("Insertion not allowed (hook not defined).")
            self.insert_hook(key, item)
            self._mydict[key] = item
        else:
            #triggers without exception
            if prev is not item:
                if self.replace_hook is None:
                    raise RuntimeError("Replacement not allowed (hook not defined).")
                self.replace_hook(key, prev, item)
                self._mydict[key] = item
        return

    def __delitem__(self, key):
        if self.delete_hook is None:
            raise RuntimeError("Deletion not allowed (hook not defined).")
        self.delete_hook(key, self._mydict[key])
        del self._mydict[key]

    def clear(self):
        if self.delete_hook is None:
            raise RuntimeError("Deletion not allowed (hook not defined).")
        for k, v in self._mydict.items():
            self.delete_hook(k, v)
        self._mydict.clear()
        return

    def setdefault(self, key, value):
        try:
            prev = self._mydict[key]
            return prev
        except KeyError:
            if self.insert_hook is None:
                raise RuntimeError("Insertion not allowed (hook not defined)")
            self.insert_hook(key , value)
            self._mydict[key] = value
        return

    def pop(self, key):
        if self.delete_hook is None:
            raise RuntimeError("Deletion not allowed (hook not defined).")
        v = self._mydict[key]
        self.delete_hook(key, v)
        del self._mydict[key]
        return v

    def popitem(self):
        if self.delete_hook is None:
            raise RuntimeError("Deletion not allowed (hook not defined).")
        k, v = self._mydict.popitem()
        self.delete_hook(k, v)
        return k, v

    def update(self, E = None, **kwargs):
        if E is not None:
            try:
                #test if the keys method exists
                keys = E.keys
            except AttributeError:
                for k, v in E:
                    self[k] = v
            else:
                for k in keys():
                    self[k] = E[k]
            for k, v in kwargs.items():
                self[k] = v
            return


MappingABC.register(HookBunch)

