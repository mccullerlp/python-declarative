# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import collections


class QuickBunch(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val
        return


def simple_setter(self, val):
    return val


class DepBunch(object):
    #just a unique object to prevent setting
    TAG_NO_SET = ("Don't Set the value", Exception)

    def __build__(self, *args, **kwargs):
        return

    def __init__(
        self,
        _args       = None,
        copy        = None,
        lightweight = True,
        **kwargs
    ):
        super(DepBunch, self).__setattr__('_current_func', None)
        super(DepBunch, self).__setattr__('_current_autodep', False)

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
            self.__build__(_args, **kwargs)
        return

    def copy(self, lightweight = True):
        return self.__class__(
            copy        = self,
            lightweight = lightweight,
        )

    def __dir__(self):
        dir1 = list(super(DepBunch, self).__dir__())
        dir1.extend(self._generators.keys())
        dir1.extend(self._setters.keys())
        dir1.extend(self._values.keys())
        dir1.sort()
        return dir1

    def set_raw(self, name, val, setter = None):
        self.clear(name)
        return self._assign(name, val, setter = setter)

    def get_raw(self, name):
        if name in self._values:
            return self._values[name]
        return self.compute(name)

    def get_default(self, name, default):
        if name in self._values:
            return self._values[name]
        return default

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

    def _compute(self, name):
        if self._current_autodep and self._current_func is not None:
            self.dependencies_for(self._current_func, name)

        prev_cf               = self._current_func
        prev_adcf             = self._current_autodep
        super(DepBunch, self).__setattr__('_current_autodep', self._autodeps_generators[name])
        super(DepBunch, self).__setattr__('_current_func',  name)
        try:
            gen_func                    = self._generators[name]
            newval                      = gen_func(self)
            self._values[name]          = newval
            self._values_computed[name] = True
            self._values_mark[name]     = self._current_mark
        finally:
            super(DepBunch, self).__setattr__('_current_autodep', prev_adcf)
            super(DepBunch, self).__setattr__('_current_func',  prev_cf)
        return newval

    def _assign(self, name, val, setter = None):
        prev_cf               = self._current_func
        prev_adcf             = self._current_autodep
        super(DepBunch, self).__setattr__('_current_autodep', self._autodeps_setters[name])
        super(DepBunch, self).__setattr__('_current_func',  name)
        try:
            if setter is None:
                setter = self._setters[name]
            newval   = setter(self, val)

            if newval is self.TAG_NO_SET:
                return

            self._values[name]          = newval
            self._values_computed[name] = False
            self._values_mark[name] = self._current_mark
        finally:
            super(DepBunch, self).__setattr__('_current_autodep', prev_adcf)
            super(DepBunch, self).__setattr__('_current_func',  prev_cf)
        return newval

    def clear(self, name):
        #print('clear', name)
        doneset = set([name])
        self._clear(name, doneset, mark = self._current_mark)

    def _clear(self, name, doneset, mark):
        #print('_clear', name)
        if name in doneset:
            return False
        doneset.add(name)
        if name in self._values:
            if not (self._values_mark[name] > mark):
                #print('del ', name)
                del self._values[name]
                del self._values_computed[name]
            else:
                #this assumes that the deps were already triggered on the set that put this mark on
                return False

        if name not in self._value_dependencies:
            return True
        deps = self._value_dependencies[name]
        for dep in list(deps):
            if self._clear(dep, doneset, mark = mark):
                deps.remove(dep)
        return True

    def _clear_dependent(self, name, mark = None):
        #print('_clear_d', name)
        doneset = set([name])

        if name not in self._value_dependencies:
            return True
        deps = self._value_dependencies[name]
        for dep in list(deps):
            if self._clear(dep, doneset, mark = mark):
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
        for dep in args:
            #uses the assumption that _value_dependencies is a defaultdict
            self._value_dependencies[dep].add(name)

    def __getstate__(self):
        return self.__dict__.copy()

    def __setstate__(self, state):
        self.__dict__.update(state)

