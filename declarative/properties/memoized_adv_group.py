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
    raise_attrerror_from_property
)


_UNIQUE_local = unique_generator()


class MemoizedGroupDescriptorBase(object):
    def __get__(self, obj, cls):
        try:
            if obj is None:
                return self
            result = obj.__dict__.get(self.__name__, _UNIQUE_local)
            if result is _UNIQUE_local:
                bd = getattr(obj, '__boot_dict__', None)
                if bd is None:
                    bd = {}
                    obj.__boot_dict__ = bd
                storage = bd.get(self.root, None)
                if storage is None:
                    try:
                        self.root._build(obj, cls)
                    except AttributeError as e:
                        raise_attrerror_from_property(self, obj, e)
                    except Exception as E:
                        print(("Exception in: ", self.__name__, " of: ", obj))
                        raise
                    storage = obj.__boot_dict__[self.root]

                bd = getattr(obj, '__boot_dict__', None)
                if bd is not None:
                    result = bd.pop(self.__name__, _UNIQUE_local)
                    if not bd:
                        del obj.__boot_dict__

                kwargs = dict()
                for rname, rdict in self.root.registries.items():
                    val = rdict.get(self.__name__, _UNIQUE_local)
                    if val is not _UNIQUE_local:
                        kwargs[rname] = val

                try:
                    if result is _UNIQUE_local:
                        result = self.func(
                            obj,
                            storage = storage,
                            group = self.root.group,
                            **kwargs
                        )
                    else:
                        result = self.func(
                            obj,
                            result,
                            storage = storage,
                            group = self.root.group,
                            **kwargs
                        )
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
        except Exception as E:
            print(E)
            raise

    def __set__(self, obj, value):
        bd = getattr(obj, '__boot_dict__', None)
        if bd is None:
            bd = {}
            obj.__boot_dict__ = bd

        storage = bd.get(self.root, _UNIQUE_local)
        if storage is _UNIQUE_local:
            bdp = bd.get(self.root.__name__, _UNIQUE_local)
            if bdp is _UNIQUE_local:
                bdp = dict()
                bd[self.root.__name__] = bdp
            oldv = bdp.setdefault(self.__name__, value)
            if oldv is not value:
                raise RuntimeError("Initial set on object must be unique")
        else:
            raise NotImplementedError("Resetting not currently implemented")
        return

    def __delete__(self, obj):
        raise RuntimeError("Not Implemented")
        return


class MemoizedGroupDescriptorRoot(MemoizedGroupDescriptorBase):
    def __init__(
        self,
        fgenerate,
        name = None,
        doc = None,
        declarative = None,
    ):
        self.registries = dict()
        self.group = dict()
        self._stems = None
        self.root = self

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

        fgenerate(self)
        return

    def stems(self, *args):
        self._stems = args
        return

    def setup(self, func):
        #TODO wrap the function call appropriately
        self._setup = func

    def _setup(self, storage, group, **kwargs):
        return

    def default(self, func):
        #TODO wrap the function call appropriately
        self.func = func

    def func(self, obj, group, storage, **kwargs):
        return None
        #raise RuntimeError("Should specify")
        #return

    def __generate_virtual_descriptors__(self):
        return self.group

    def name_change(self, name):
        self.__name__ = name

    def mproperty(
            self,
            __func      = None,
            name        = None,
            stem        = None,
            declarative = None,
            **kwargs
    ):
        def wrap(func):
            if name is None and stem is None:
                names = [func.__name__]
            elif stem is None:
                names = [name]
            else:
                if name is not None:
                    names = [name]
                else:
                    names = []
                for stem_fmt in self._stems:
                    names.append(stem.format(stem = stem_fmt, name = name, **kwargs))
            principle_name = names[0]

            for k, v in kwargs.items():
                inner = self.registries.get(k, None)
                if inner is None:
                    inner = dict()
                    self.registries[k] = inner
                inner[principle_name] = v

            if self.__name__ in names:
                desc = self
                self.func = func
            else:
                desc = MemoizedGroupDescriptor(
                    func        = func,
                    name        = principle_name,
                    root        = self.root,
                    declarative = declarative,
                )
            for usedname in names:
                self.root.group[usedname] = desc
            return desc
        if __func is not None:
            return wrap(__func)
        else:
            return wrap

    def dproperty(
            self,
            __func = None,
            declarative = True,
            **kwargs
    ):
        return self.mproperty(
            __func,
            declarative = declarative,
            **kwargs
        )

    def _build(self, obj, cls):
        bd = getattr(obj, '__boot_dict__', None)
        if bd is None:
            bd = {}
            obj.__boot_dict__ = bd
        result = bd.get(self, _UNIQUE_local)
        if result is _UNIQUE_local:
            #bd = obj.__boot_dict__
            bd = getattr(obj, '__boot_dict__', None)
            if bd is not None:
                sources = bd.pop(self.__name__, _UNIQUE_local)
            else:
                sources = _UNIQUE_local

            if sources is _UNIQUE_local:
                sources = dict()

            #the method should modify the sources values if it needs
            result = self._setup(
                obj,
                sources = sources,
                group = self.group,
                **self.registries
            )

            #inject the values into the boot_dict
            if bd is None:
                bd = dict()
                obj.__boot_dict__ = bd
            for k, v in sources.items():
                bd[k] = v

            if __debug__:
                if result is NOARG:
                    raise InnerException("Return result was NOARG")

            if isinstance(result, PropertyTransforming):
                result = result.construct(
                    parent = obj,
                    name = self.__name__,
                )

            bd = getattr(obj, '__boot_dict__', None)
            if bd is None:
                bd = {}
                obj.__boot_dict__ = bd
            bd[self] = result
            return


class MemoizedGroupDescriptor(MemoizedGroupDescriptorBase):
    """
    wraps a member function just as :obj:`property` but saves its value after evaluation
    (and is thus only evaluated once)
    """
    _declarative_instantiation = False

    def __init__(
        self,
        func,
        root,
        name = None,
        doc = None,
        declarative = None,
    ):
        self.root = root
        self.func = func

        if name is None:
            self.__name__ = func.__name__
        else:
            self.__name__ = name

        if doc is None:
            self.__doc__ = func.__doc__
        else:
            self.__doc__ = doc

        if declarative is not None:
            self._declarative_instantiation = declarative
        return


def mproperty_adv_group(
        __func = None,
        **kwargs
):
    def wrap(func):
        desc = MemoizedGroupDescriptorRoot(
            func, **kwargs
        )
        return desc
    if __func is not None:
        return wrap(__func)
    else:
        return wrap


def dproperty_adv_group(
        __func = None,
        declarative = True,
        **kwargs
):
    return mproperty_adv_group(
        __func = __func,
        declarative = declarative,
        **kwargs
    )

group_dproperty = dproperty_adv_group
group_mproperty = mproperty_adv_group
