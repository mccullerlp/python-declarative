"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)


from functools import partial

from .unique import (
    NOARG,
    unique_generator
)

from .bases import (
    InnerException,
    PropertyTransforming,
)

_UNIQUE_local = unique_generator()


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

class_memoized_property = ClassMemoizedDescriptor


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
            try:
                if result is _UNIQUE_local:
                    result = self.fget(obj)
                else:
                    result = self.fget(obj, result)
            except TypeError as e:
                print ("TE:", e)
                print("BOOBOO ON: ", obj.__class__, self.__name__)
                raise
            if __debug__:
                if result is NOARG:
                    raise InnerException("Return result was NOARG")

            if self.transforming and isinstance(result, PropertyTransforming):
                try:
                    result = result.construct(
                        parent = obj,
                        name = self.__name__,
                    )
                except Exception as E:
                    print("BOOBOO CONSTRUCTING: {0}, in {1}".format(self.__name__, repr(self)))
                    raise

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
                    raise RuntimeError("Initial set on object must be unique")
            else:
                obj.__boot_dict__ = {self.__name__ : value}
        else:
            #the new value shows up in the object BEFORE the exchanger is called
            if oldvalue is value:
                return
            if __debug__:
                import inspect
                args, _, _, _ = inspect.getargspec(self.fget)
                if len(args) < 3:
                    raise RuntimeError("The memoized member ({0}) does not support value exchange".format(self.__name__))
            obj.__dict__[self.__name__] = value
            revalue = self.fget(obj, value, oldvalue)
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
                if __debug__:
                    import inspect
                    args, _, _, _ = inspect.getargspec(self.fget)
                    if len(args) < 3:
                        raise RuntimeError("The memoized member ({0}) does not support value exchange".format(self.__name__))
                del obj.__dict__[self.__name__]
                revalue = self.fget(obj, NOARG, oldvalue)
                if revalue is not NOARG:
                    obj.__dict__[self.__name__] = revalue
        return


class MemoizedDescriptorFNoSet(object):
    """
    wraps a member function just as :obj:`property` but saves its value after evaluation
    (and is thus only evaluated once)
    """
    _declarative_instantiation = False

    def __init__(
        self,
        fget,
        name = None,
        doc = None,
        declarative = None,
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
                result = self.fget(obj)
            else:
                result = self.fget(obj, result)
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
        **kwargs
):
    def wrap(func):
        desc = MemoizedDescriptor(
            func, **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap

def dproperty(
        __func = None,
        declarative = True,
        **kwargs
):
    return mproperty(
        __func = __func,
        declarative = declarative,
        **kwargs
    )

def mproperty_plain(
        __func = None,
        **kwargs
):
    def wrap(func):
        desc = MemoizedDescriptorFNoSet(
            func, **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap

def dproperty_plain(
        __func = None,
        declarative = True,
        **kwargs
):
    return mproperty_plain(
        __func = __func,
        declarative = declarative,
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
