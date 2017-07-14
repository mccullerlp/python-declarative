# -*- coding: utf-8 -*-
"""
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
)
#from builtins import object


from ..utilities.unique import (
    NOARG,
    unique_generator
)


from .bases import (
    InnerException,
    PropertyTransforming,
)

from .utilities import (
    raise_attrerror_from_property,
    raise_msg_from_property,
    try_name_file_line,
)

from .memoized import AccessError

_UNIQUE_local = unique_generator()


class MemoizedAdvDescriptor(object):
    def __init__(
        self,
        fgenerate,
        name = None,
        doc  = None,
        declarative = None,
    ):
        if name is None:
            self.__name__ = fgenerate.__name__
        else:
            self.__name__ = name

        if doc is None:
            self.__doc__ = fgenerate.__doc__
        else:
            self.__doc__ = doc

        if declarative is not None:
            self._declarative_instantiation = declarative

        self.fconstruct_warg = None
        self.fconstruct_narg = None

        fgenerate(self)

        if self.fconstruct_warg is None and self.fconstruct_narg is None:
            raise RuntimeError("Must Specify a function")
        return

    def construct(self, fconstruct):
        #TODO wrap the function call appropriately
        self.fconstruct_narg = fconstruct
        self.fconstruct_warg = fconstruct

    def construct_narg(self, fconstruct):
        self.fconstruct_narg = fconstruct

    def construct_warg(self, fconstruct):
        self.fconstruct_warg = fconstruct

    def fsetter(self, arg, arg_prev):
        raise RuntimeError("Setting not supported on {0}".self(__name__))

    def fdeleter(self, arg_prev):
        raise RuntimeError("Deleting not supported on {0}".self(__name__))

    def __get__(self, obj, cls):
        try:
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
                        result = self.fconstruct_narg(obj)
                    except TypeError as e:
                        raise_msg_from_property(
                            ("Property attribute {name} of {orepr} accessed with no initial value. Needs an initial value, or"
                             " to be declared with a default argument at file:"
                             "\n{filename}"
                             "\nline {lineno}."),
                            AccessError, self, obj, e,
                            if_from_file = __file__,
                            **try_name_file_line(self.fconstruct_narg)
                        )
                        raise
                    except AttributeError as e:
                        raise_attrerror_from_property(self, obj, e)
                else:
                    try:
                        result = self.fconstruct_warg(obj, result)
                    except TypeError as e:
                        raise_msg_from_property(
                            ("Property attribute {name} of {orepr} accessed with no initial value. Needs an initial value, or"
                             " to be declared with a default argument at file:"
                             "\n{filename}"
                             "\nline {lineno}."),
                            AccessError, self, obj, e,
                            if_from_file = __file__,
                            **try_name_file_line(self.fconstruct_warg)
                        )
                        raise
                    except AttributeError as e:
                        raise_attrerror_from_property(self, obj, e)
                if __debug__:
                    if result is NOARG:
                        raise InnerException("Return result was NOARG")

                if isinstance(result, PropertyTransforming):
                    result = result.construct(
                        parent = obj,
                        name = self.__name__,
                    )

                obj.__dict__[self.__name__] = result
            return result
        except AttributeError as e:
            raise RuntimeError(e)

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
            try:
                revalue = self.fsetter(obj, value, oldvalue)
            except AttributeError as e:
                raise_attrerror_from_property(self, obj, e)
            if revalue is not NOARG:
                obj.__dict__[self.__name__] = revalue
            else:
                del obj.__dict__[self.__name__]
        return

    def __delete__(self, obj):
        oldvalue = obj.__dict__.get(self.__name__, _UNIQUE_local)
        if oldvalue is _UNIQUE_local:
            raise InnerException("Value never initialized")
        else:
            #the new value shows up in the object BEFORE the exchanger is called
            if __debug__:
                import inspect
                args, _, _, _ = inspect.getargspec(self.fget)
                if len(args) < 3:
                    raise RuntimeError("The memoized member ({0}) does not support value exchange".format(self.__name__))
            del obj.__dict__[self.__name__]
            try:
                revalue = self.fdeleter(obj, oldvalue)
            except AttributeError as e:
                raise_attrerror_from_property(self, obj, e)
            if revalue is not NOARG:
                obj.__dict__[self.__name__] = revalue
        return


def mproperty_adv(
        __func = None,
        **kwargs
):
    def wrap(func):
        desc = MemoizedAdvDescriptor(
            func, **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap


def dproperty_adv(
        __func = None,
        declarative = True,
        **kwargs
):
    return mproperty_adv(
        __func = __func,
        declarative = declarative,
        **kwargs
    )

