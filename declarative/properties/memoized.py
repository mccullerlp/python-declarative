# -*- coding: utf-8 -*-
"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
#from builtins import object


from functools import partial

from ..utilities.unique import (
    NOARG,
    unique_generator
)

from .utilities import (
    raise_attrerror_from_property,
    raise_msg_from_property,
    try_name_file_line,
)

from .bases import (
    InnerException,
    PropertyTransforming,
)

_UNIQUE_local = unique_generator()


class AccessError(Exception):
    pass


class ClassMemoizedDescriptor(object):

    """
    Works like a combination of :obj:`property` and :obj:`classmethod` as well as :obj:`~.memoized_property`
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        result = self.fget(cls)
        setattr(cls, self.__name__, result)
        return result


memoized_class_property = ClassMemoizedDescriptor


class MemoizedDescriptor(object):
    """
    wraps a member function just as :obj:`property` but saves its value after evaluation
    (and is thus only evaluated once)
    """
    _declarative_instantiation = False
    transforming = True
    simple_delete = False

    def __init__(
        self,
        fget,
        name = None,
        doc = None,
        declarative = None,
        transforming = None,
        simple_delete = False,
        original_callname = None,
    ):
        self.fget = fget
        if name is None:
            self.__name__ = fget.__name__
        else:
            self.__name__ = name
        if doc is None:
            self.__doc__ = fget.__doc__
        else:
            self.__doc__ = doc
        if declarative is not None:
            self._declarative_instantiation = declarative
        if transforming is not None:
            self.transforming = transforming
        if simple_delete:
            self.simple_delete = simple_delete
        if original_callname is not None:
            self.original_callname = original_callname
        else:
            self.original_callname = self.__class__.__name__
        return

    def __get__(self, obj, cls):
        if obj is None:
            return self
        result = obj.__dict__.get(self.__name__, _UNIQUE_local)
        if result is _UNIQUE_local:
            #bd = obj.__boot_dict__
            bd = getattr(obj, '__boot_dict__', None)
            if bd is not None:
                result = bd.pop(self.__name__, _UNIQUE_local)
                if not bd:
                    del obj.__boot_dict__
            if result is _UNIQUE_local:
                try:
                    result = self.fget(obj)
                except TypeError as e:
                    raise_msg_from_property(
                        ("Property attribute {name} of {orepr} accessed with no initial value. Needs an initial value, or"
                         " to be declared with a default argument at file:"
                         "\n{filename}"
                         "\nline {lineno}."),
                        AccessError, self, obj, e,
                        if_from_file = __file__,
                        **try_name_file_line(self.fget)
                    )
                    raise
                except AttributeError as e:
                    raise_attrerror_from_property(self, obj, e)
            else:
                try:
                    result = self.fget(obj, result)
                except TypeError as e:
                    raise_msg_from_property(
                        ("Property attribute {name} of {orepr} accessed with an initial value. Needs no initial value, or"
                         "to be declared taking an argument at file:"
                         "\n{filename}"
                         "\nline {lineno}."),
                        AccessError, self, obj, e,
                        if_from_file = __file__,
                        **try_name_file_line(self.fget)
                    )
                    raise
                except AttributeError as e:
                    raise_attrerror_from_property(self, obj, e)

            if __debug__:
                if result is NOARG:
                    raise InnerException("Return result was NOARG (usu)")

            if self.transforming and isinstance(result, PropertyTransforming):
                try:
                    result = result.construct(
                        parent = obj,
                        name = self.__name__,
                    )
                except Exception as e:
                    raise
                    raise_msg_from_property((
                        "Property attribute {name} of {orepr} failed constructing a Transforming object"),
                        RuntimeError, self, obj, e,
                    )

            #print("SET Value for attr ({0}) in {1}".format(self.__name__, id(obj)))
            obj.__dict__[self.__name__] = result
        return result

    def __set__(self, obj, value):
        oldvalue = obj.__dict__.get(self.__name__, _UNIQUE_local)
        if oldvalue is _UNIQUE_local:
            bd = getattr(obj, '__boot_dict__', None)
            if bd is not None:
                oldv = bd.setdefault(self.__name__, value)
                if oldv is not value:
                    d = dict(
                        name = self.__name__,
                    )
                    try:
                        d['orepr'] = repr(obj)
                    except Exception:
                        d['orepr'] = '<object of {0}>'.format(obj.__class__.__name__)
                    raise RuntimeError(
                        "Initial set for attribute {name} on object {orepr} must be unique".format(**d)
                    )
            else:
                obj.__boot_dict__ = {self.__name__ : value}
        else:
            #the new value shows up in the object BEFORE the exchanger is called
            if oldvalue is value:
                return
            obj.__dict__[self.__name__] = value
            try:
                revalue = self.fget(obj, value, oldvalue)
            except TypeError as e:
                raise_msg_from_property(
                    ("Property attribute {name} of {orepr} set, replacing an initial value with a new. Either setting not allowed, or"
                     "must be declared taking 2 arguments at file:"
                     "\n{filename}"
                     "\nline {lineno}."),
                    AccessError, self, obj, e,
                    if_from_file = __file__,
                    **try_name_file_line(self.fget)
                )
                raise
            if revalue is not NOARG:
                obj.__dict__[self.__name__] = revalue
            else:
                del obj.__dict__[self.__name__]
        return

    def __delete__(self, obj):
        oldvalue = obj.__dict__.get(self.__name__, _UNIQUE_local)
        if oldvalue is _UNIQUE_local:
            raise InnerException("Value for attr ({0}) in {1}({2}) never initialized before delete".format(self.__name__, obj, id(obj)))
        else:
            if self.simple_delete:
                del obj.__dict__[self.__name__]
            else:
                #the new value shows up in the object BEFORE the exchanger is called
                del obj.__dict__[self.__name__]
                try:
                    revalue = self.fget(obj, NOARG, oldvalue)
                except TypeError as e:
                    raise_msg_from_property(
                        ("Property attribute {name} of {orepr} deleted, replacing an initial value with NOARG. Either deleting not allowed, or"
                         "must be declared taking 2 arguments at file:"
                         "\n{filename}"
                         "\nline {lineno}."),
                        AccessError, self, obj, e,
                        if_from_file = __file__,
                        **try_name_file_line(self.fget)
                    )
                    raise
                if revalue is not NOARG:
                    obj.__dict__[self.__name__] = revalue
        return


class MemoizedDescriptorFNoSet(object):
    """
    wraps a member function just as :obj:`property` but saves its value after evaluation
    (and is thus only evaluated once)
    """
    _declarative_instantiation = False
    _force_boot_dict = True

    def __init__(
        self,
        fget,
        name = None,
        doc = None,
        declarative = None,
        original_callname = None,
    ):
        self.fget = fget
        if name is None:
            self.__name__ = fget.__name__
        else:
            self.__name__ = name
        if doc is None:
            self.__doc__ = fget.__doc__
        else:
            self.__doc__ = doc
        if declarative is not None:
            self._declarative_instantiation = declarative
        if original_callname is not None:
            self.original_callname = original_callname
        else:
            self.original_callname = self.__class__.__name__
        return

    def __get__(self, obj, cls):
        if obj is None:
            return self
        result = obj.__dict__.get(self.__name__, _UNIQUE_local)
        if result is _UNIQUE_local:
            #bd = obj.__boot_dict__
            bd = getattr(obj, '__boot_dict__', None)
            if bd is not None:
                result = bd.pop(self.__name__, _UNIQUE_local)
                if not bd:
                    del obj.__boot_dict__
            if result is _UNIQUE_local:
                try:
                    result = self.fget(obj)
                except TypeError as e:
                    raise_msg_from_property(
                        ("Property attribute {name} of {orepr} accessed with no initial value. Needs an initial value, or"
                         "to be declared with a default argument at file:"
                         "\n{filename}"
                         "\nline {lineno}."),
                        AccessError, self, obj, e,
                        if_from_file = __file__,
                        **try_name_file_line(self.fget)
                    )
                    raise
                except AttributeError as e:
                    raise_attrerror_from_property(self, obj, e)
            else:
                try:
                    result = self.fget(obj, result)
                except TypeError as e:
                    raise_msg_from_property(
                        ("Property attribute {name} of {orepr} accessed with an initial value. Needs no initial value, or"
                         "to be declared taking an argument at file:"
                         "\n{filename}"
                         "\nline {lineno}."),
                        AccessError, self, obj, e,
                        if_from_file = __file__,
                        **try_name_file_line(self.fget)
                    )
                    raise
                except AttributeError as e:
                    raise_attrerror_from_property(self, obj, e)

            if __debug__:
                if result is NOARG:
                    raise InnerException("Return result was NOARG")
            #obj.__dict__[self.__name__] = result

            if isinstance(result, PropertyTransforming):
                result = result.construct(
                    parent = obj,
                    name = self.__name__,
                )

            #use standard (or overloaded! setter since this will assign to __dict__ by default
            #when this descriptor object is missing __set__)
            setattr(obj, self.__name__, result)
            #in case the setattr transformed the object
            result = getattr(obj, self.__name__)
        return result


def mproperty(
        __func = None,
        original_callname = 'mproperty',
        **kwargs
):
    def wrap(func):
        desc = MemoizedDescriptor(
            func,
            original_callname = original_callname,
            **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap


def dproperty(
        __func = None,
        declarative = True,
        original_callname = 'dproperty',
        **kwargs
):
    return mproperty(
        __func = __func,
        declarative = declarative,
        original_callname = original_callname,
        **kwargs
    )


def mproperty_plain(
        __func = None,
        original_callname = 'mproperty_plain',
        **kwargs
):
    def wrap(func):
        desc = MemoizedDescriptorFNoSet(
            func,
            original_callname = original_callname,
            **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap


def dproperty_plain(
        __func = None,
        declarative = True,
        original_callname = 'dproperty_plain',
        **kwargs
):
    return mproperty_plain(
        __func = __func,
        declarative = declarative,
        original_callname = original_callname,
        **kwargs
    )


if __debug__:
    mproperty_fns = mproperty
    dproperty_fns = dproperty
else:
    mproperty_fns = mproperty_plain
    dproperty_fns = dproperty_plain


class MemoizeFunction(object):
    """cache the return value of a method

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached on the instance whose method
    was invoked. All arguments passed to a method decorated with memoize must
    be hashable.

    If a memoized method is invoked directly on its class the result will not
    be cached. Instead the method will be invoked like a static method:
    class Obj(object):
        @memoize
        def add_to(self, arg):
            return self + arg
    Obj.add_to(1) # not enough arguments
    Obj.add_to(1, 2) # returns 3, result is not cached

    from Daniel Miller on Active State
    http://code.activestate.com/recipes/577452-a-memoize-decorator-for-instance-methods/
    MIT Licenced
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]
        try:
            cache = obj.__cache
        except AttributeError:
            cache = obj.__cache = {}
        key = (self.func, args[1:], frozenset(list(kw.items())))
        try:
            res = cache[key]
        except KeyError:
            res = cache[key] = self.func(*args, **kw)
        return res

mfunction = MemoizeFunction
