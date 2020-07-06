# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import sys
import collections
import inspect
import warnings

from ..utilities.future_from_2 import str, unicode

#unique element to indicate a default argument
_NOARG = lambda : _NOARG
NOARG = ("NOARG", _NOARG)

try:
    getargspec = inspect.getfullargspec
except AttributeError:
    getargspec = inspect.getargspec


def simple_setter(self, val):
    return val


#TODO, make __set_name__ work via metaclass in python <3.6
class DepBunch(object):
    #just a unique object to prevent setting
    TAG_NO_SET = ("Don't Set the value", Exception)

    def __build__(self, _args = None, **kwargs):
        return

    #this adds in a metaclass-like hack to give python2 access to the __set_name__
    if sys.version_info < (3, 6):
        def __new__(cls, *args, **kwargs):
            attrsetup = '__hack_meta_{}_setup__'.format(cls.__name__)
            try:
                getattr(cls, attrsetup)
            except AttributeError:
                for aname in dir(cls):
                    aval = getattr(cls, aname)
                    try:
                        acall = aval.__set_name__
                    except AttributeError:
                        pass
                    else:
                        acall(cls, aname)
                #now flag the class
                setattr(cls, attrsetup, True)
            obj = super(DepBunch, cls).__new__(cls, *args, **kwargs)
            return obj

    def __init__(
        self,
        _args       = None,
        copy        = None,
        lightweight = True,
        **kwargs
    ):
        super(DepBunch, self).__setattr__('_current_func', None)
        super(DepBunch, self).__setattr__('_current_autodep', False)
        #to hold currently executing values
        super(DepBunch, self).__setattr__('_value_dependencies_inv',  {})

        if copy is None:
            super(DepBunch, self).__setattr__('_current_mark', 0)
            super(DepBunch, self).__setattr__('_values', dict())
            super(DepBunch, self).__setattr__('_values_computed', dict())
            super(DepBunch, self).__setattr__('_values_mark', dict())
            super(DepBunch, self).__setattr__('_value_dependencies', collections.defaultdict(set))

            super(DepBunch, self).__setattr__('_generators', dict())
            super(DepBunch, self).__setattr__('_setters', dict())
            super(DepBunch, self).__setattr__('_copiers', dict())

            super(DepBunch, self).__setattr__('_autodeps_setters', dict())
            super(DepBunch, self).__setattr__('_autodeps_generators', dict())

        else:
            #fix all of these for setattr
            super(DepBunch, self).__setattr__('_value_dependencies', collections.defaultdict(set))
            super(DepBunch, self).__setattr__('_current_mark', copy._current_mark)
            if not lightweight:
                super(DepBunch, self).__setattr__('_values', dict(copy._values))
                super(DepBunch, self).__setattr__('_values_computed', dict(copy._values_computed))
                super(DepBunch, self).__setattr__('_values_mark', dict(copy._values_mark))
                #have to copy individually
                for k, v in copy._value_dependencies.items():
                    self._value_dependencies[k] = set(v)
            else:
                super(DepBunch, self).__setattr__('_values', dict())
                super(DepBunch, self).__setattr__('_values_computed', dict())
                super(DepBunch, self).__setattr__('_values_mark', dict())
                for k, v in copy._values_computed.items():
                    if not v:
                        copier = copy._copiers.get(k, None)
                        if not copier:
                            self._values[k] = copy._values[k]
                            self._values_computed[k] = v
                            self._values_mark[k] = copy._values_mark[k]
                            #TODO, should actually purge the deps that weren't copied, but that could be "expensive"
                            self._value_dependencies[k] = set(copy._value_dependencies[k])
                        else:
                            self._values[k] = copier(self, copy._values[k])
                            self._values_computed[k] = v
                            self._values_mark[k] = copy._values_mark[k]
                            #TODO, should actually purge the deps that weren't copied, but that could be "expensive"
                            self._value_dependencies[k] = set(copy._value_dependencies[k])
                for k, v in copy._value_dependencies.items():
                    self._value_dependencies[k] = set(copy._value_dependencies[k])

            super(DepBunch, self).__setattr__('_generators', dict(copy._generators))
            super(DepBunch, self).__setattr__('_setters', dict(copy._setters))
            super(DepBunch, self).__setattr__('_copiers', dict(copy._copiers))

            super(DepBunch, self).__setattr__('_autodeps_setters', dict(copy._autodeps_setters))
            super(DepBunch, self).__setattr__('_autodeps_generators', dict(copy._autodeps_generators))

        if copy is None:
            self.__build__(_args = _args, **kwargs)
        return

    def copy(self, lightweight = True):
        return self.__class__(
            copy        = self,
            lightweight = lightweight,
        )

    def __dir__(self):
        dir1 = list(super(DepBunch, self).__dir__())
        dir1.extend(k for k in self._generators.keys() if isinstance(k, (str, unicode)))
        dir1.extend(k for k in self._generators.keys() if isinstance(k, (str, unicode)))
        dir1.extend(k for k in self._generators.keys() if isinstance(k, (str, unicode)))
        #dir1.sort()
        return dir1

    def set_raw(self, name, val, setter = None, autodep = None):
        self.clear(name)
        if setter is not None and autodep is None:
            autodep = True
        return self._assign(name, val, setter = setter, autodep = autodep)

    def get_raw(self, name, default = NOARG):
        val = self._values.get(name, default)
        if val is NOARG:
            return self._compute(name)
        return val

    def get_default(self, name, default):
        return self._values.get(name, default)

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val
        return

    def __getitem__(self, name):
        if name in self._values:
            if self._current_autodep and self._current_func is not None:
                self.dependencies_for(self._current_func, name)
            return self._values[name]
        else:
            return self._compute(name)

    def __setitem__(self, name, val):
        setter = self._setters.get(name, None)

        #check if it is in a descriptor property
        if setter is None:
            desc = getattr(self.__class__, name, None)
            if isinstance(desc, DepBunchDescriptor):
                desc.install(self, name)
                setter = self._setters[name]

        if setter is None:
            self._values[name] = val
            self._values_computed[name] = False
            self._values_mark[name] = self._current_mark
            ret = val
            self._clear_dependent(name, self._current_mark)
        else:
            current_mark = self._current_mark
            super(DepBunch, self).__setattr__('_current_mark', current_mark + 1)
            ret = self._assign(name, val)
            self._clear_dependent(name, current_mark)
        return ret

    def __delitem__(self, name):
        self.clear(name)

    def __delattr__(self, name):
        self.clear(name)

    def _compute(self, name, gen_func = None):
        if gen_func is None:
            gen_func = self._generators.get(name, None)

        #install it from the descriptor
        if gen_func is None:
            desc = getattr(self.__class__, name, None)
            if isinstance(desc, DepBunchDescriptor):
                desc.install(self, name)
                gen_func = self._generators.get(name, None)
            elif desc is None:
                raise RuntimeError("Unrecognized attribute {}".format(name))
            else:
                raise RuntimeError("attribute does not have a generator {}".format(name))

        if self._current_autodep and self._current_func is not None:
            self.dependencies_for(self._current_func, name)

        prev_cf               = self._current_func
        prev_adcf             = self._current_autodep
        super(DepBunch, self).__setattr__('_current_autodep', self._autodeps_generators[name])
        super(DepBunch, self).__setattr__('_current_func',  name)

        #calls with no arguments except self
        ideps = self._value_dependencies_inv.get(name, None)
        #print(name, ideps)
        if ideps is not None:
            #TODO, better error
            raise RuntimeError("Must be infinitely recursive! {} has apparent dependencies {}".format(name, ideps))

        try:
            ideps = set()
            self._value_dependencies_inv[name] = ideps

            newval                      = gen_func(self)

            self._values[name]          = newval
            self._values_computed[name] = True
            self._values_mark[name]     = self._current_mark
            for dep in ideps:
                self._value_dependencies[dep].add(name)
            #print(name, 'del')
        finally:
            del self._value_dependencies_inv[name]
            super(DepBunch, self).__setattr__('_current_autodep', prev_adcf)
            super(DepBunch, self).__setattr__('_current_func',  prev_cf)
        return newval

    def _assign(self, name, val, setter = None, autodep = None):
        if setter is None:
            setter = self._setters[name]

        if setter is None:
            desc = getattr(self.__class__, name, None)
            if isinstance(desc, DepBunchDescriptor):
                desc.install(self, name)
                setter = self._setters[name]
            elif desc is None:
                raise RuntimeError("Unrecognized attribute {}".format(name))
            else:
                raise RuntimeError("attribute does not have a setter {}".format(name))

        prev_cf               = self._current_func
        prev_adcf             = self._current_autodep
        if autodep is None:
            super(DepBunch, self).__setattr__('_current_autodep', self._autodeps_setters[name])
        else:
            super(DepBunch, self).__setattr__('_current_autodep', autodep)
        super(DepBunch, self).__setattr__('_current_func',  name)

        try:
            ideps = self._value_dependencies_inv.get(name, None)
            #print(name, ideps)
            if ideps is not None:
                #TODO, better error
                raise RuntimeError("Must be infinitely recursive!")
            ideps = set()
            self._value_dependencies_inv[name] = ideps

            #Where the magic happens
            newval = setter(self, val)

            if newval is self.TAG_NO_SET:
                pass
            else:
                self._values[name]          = newval
                self._values_computed[name] = False
                self._values_mark[name] = self._current_mark
                for dep in ideps:
                    self._value_dependencies[dep].add(name)
        finally:
            del self._value_dependencies_inv[name]
            super(DepBunch, self).__setattr__('_current_autodep', prev_adcf)
            super(DepBunch, self).__setattr__('_current_func',  prev_cf)
        return newval

    def clear(self, name):
        #print('clear', name)
        doneset = set([])
        self._clear(name, doneset, mark = self._current_mark)

    def _clear(self, name, doneset, mark):
        #print("CLEAR: ", name)
        if name in doneset:
            return False
        doneset.add(name)
        if name in self._values:
            #TODO should be >=?
            if not (self._values_mark[name] > mark):
                del self._values[name]
                del self._values_computed[name]
                retval = True
                #print("DEL: ", name)
            else:
                #this assumes that the deps were already triggered on the set that put this mark on
                return False
        else:
            retval = True

        if name not in self._value_dependencies:
            return retval
        deps = self._value_dependencies[name]
        for dep in list(deps):
            if self._clear(dep, doneset, mark = mark):
                #print("REMOVE: ", name, dep)
                deps.remove(dep)
        return retval

    def _clear_dependent(self, name, mark = None):
        #print('_clear_d', name)
        doneset = set([name])

        if name not in self._value_dependencies:
            return True
        deps = self._value_dependencies[name]
        for dep in list(deps):
            if self._clear(dep, doneset, mark = mark):
                #print('REMOVE_D:', name, dep)
                deps.remove(dep)
        return True

    def add_setter(
            self,
            name     = None,
            func     = None,
            autodeps = True,
            clear    = True
    ):
        if name is None:
            name = func.__name__
        elif func is None:
            #ok, then we were only given a name
            if callable(name):
                func = name
                name = func.__name__
            else:
                #if name is a string, then we just _assign a simple setter
                func = simple_setter

        self._autodeps_setters[name] = autodeps
        self._setters[name] = func
        if clear is None or clear:
            self.clear(name)
        return func

    def deco_setter(
        self,
        name = None,
        **kwargs
    ):
        if callable(name):
            #name is a func but the call handles that
            return self.add_setter(name = name, **kwargs)
        else:
            def deco_grab(func):
                return self.add_setter(
                    name     = name,
                    func     = func,
                    **kwargs
                )
            return deco_grab

    def add_generator(
            self,
            name     = None,
            func     = None,
            autodeps = True,
            clear    = True
    ):
        if name is None:
            name = func.__name__
        elif func is None:
            if callable(name):
                func = name
                name = func.__name__
            else:
                raise RuntimeError("Must Specify Function for generator")
                #ok, then we were only given a name

        self._autodeps_generators[name] = autodeps
        self._generators[name] = func
        if clear is None or clear:
            self.clear(name)
        return func

    def deco_generator(
        self,
        name = None,
        **kwargs
    ):
        if callable(name):
            #name is a func but the call handles that
            return self.add_generator(name = name, **kwargs)
        else:
            def deco_grab(func):
                return self.add_generator(
                    name     = name,
                    func     = func,
                    **kwargs
                )
            return deco_grab

    def add_gensetter(
        self,
        name     = None,
        func     = None,
        autodeps = True,
        clear    = True,
    ):
        self.add_generator(
            name     = name,
            func     = func,
            autodeps = autodeps,
            clear    = clear,
        )
        self.add_setter(
            name     = name,
            func     = func,
            autodeps = autodeps,
            clear    = clear,
        )

    def deco_gensetter(
        self,
        name = None,
        **kwargs
    ):
        if callable(name):
            #name is a func but the call handles that
            return self.add_gensetter(name = name, **kwargs)
        else:
            def deco_grab(func):
                return self.add_gensetter(
                    name     = name,
                    func     = func,
                    **kwargs
                )
            return deco_grab

    def add_copier(
            self,
            name     = None,
            func     = None,
    ):
        if name is None:
            name = func.__name__
        elif func is None:
            #ok, then we were only given a name
            if callable(name):
                func = name
                name = func.__name__
            else:
                raise RuntimeError("Must provide copier function (not just a name)")

        self._copiers[name] = func
        return func

    def deco_copier(
        self,
        name = None,
        **kwargs
    ):
        if callable(name):
            #name is a func but the call handles that
            return self.add_copier(name = name, **kwargs)
        else:
            def deco_grab(func):
                return self.add_copier(
                    name     = name,
                    func     = func,
                    **kwargs
                )
            return deco_grab

    def dependencies(self, *args):
        if self._current_func is None:
            raise RuntimeError('dependencies only callable from inside a setter or generator (use dependencies_for perhaps)')
        self.dependencies_for(self._current_func, *args)

    def dependencies_for(self, name, *args):
        ideps = self._value_dependencies_inv.get(name, None)
        if ideps is not None:
            ideps.update(args)
        for dep in args:
            #uses the assumption that _value_dependencies is a defaultdict
            #print("DEP: ", name, dep)
            self._value_dependencies[dep].add(name)

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)


class DepBunchDescriptor(object):
    """
    wraps a member function just as :obj:`property` but saves its value after evaluation
    (and is thus only evaluated once)
    """

    def __init__(
        self,
        fgetset,
        doc = None,
        autodeps = True,
        original_callname = None,
    ):
        self.fget = fgetset

        aspec = getargspec(fgetset)
        #must have self and one other for it to be a setter
        if len(aspec.args) > 1:
            self.fset = fgetset
        else:
            self.fset = simple_setter

        self.autodeps = autodeps

        if doc is None:
            self.__doc__ = fgetset.__doc__
        else:
            self.__doc__ = doc

        if original_callname is not None:
            self.original_callname = original_callname
        else:
            self.original_callname = self.__class__.__name__

        return

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return obj[self.__name__]

    def __set__(self, obj, value):
        obj[self.__name__] = value

    def __delete__(self, obj):
        del obj[self.__name__]
        return

    def install(self, obj, name):
        if name != self.__name__:
            warnings.warn(
                'Depbunch, depB_property name not the same as install name'
            )
        #print('install', name, self.autodeps)
        obj.add_generator(name, self.fget, autodeps = self.autodeps, clear = False)
        obj.add_setter(name, self.fset, autodeps = self.autodeps, clear = False)
        return


#depB_property = DepBunchDescriptor


def depB_property(
    fgetset = None,
    **kwargs
):
    if fgetset is not None:
        #name is a func but the call handles that
        return DepBunchDescriptor(fgetset, **kwargs)
    else:
        def deco_grab(func):
            return DepBunchDescriptor(func, **kwargs)
        return deco_grab

def depB_lambda(
    fgetset = None,
    **kwargs
):
    """
    For lambda function usage
    """
    return DepBunchDescriptor(fgetset, **kwargs)

def depB_extract(aname, vname, **kwargs):
    def fgetset(self):
        return getattr(self, aname)[vname]
    return DepBunchDescriptor(fgetset, name = vname, **kwargs)

def depB_value(fvalue, **kwargs):
    def fgetset(self, value = fvalue):
        return value
    return DepBunchDescriptor(fgetset, **kwargs)

depBe = depB_extract
depBv = depB_value
depBl = depB_lambda
depBp = depB_property

