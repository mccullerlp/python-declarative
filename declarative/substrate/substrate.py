# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, absolute_import
#from builtins import object
from functools import wraps

from ..properties import (
    PropertyTransforming,
    mproperty,
    dproperty,
    NOARG,
)

from ..overridable_object import (
    OverridableObject,
)

from ..metaclass import (
    AttrExpandingObject,
)

from ..bunch import (
    DeepBunchSingleAssign,
    DeepBunch,
    ShadowBunch,
)

from ..utilities.future_from_2 import (
    raise_from_with_traceback,
)

if __debug__:
    mproperty_check = dproperty
else:
    mproperty_check = mproperty


class ShadowBunchN(ShadowBunch):
    _names = {
        'full' :      0,
        'immed' :     1,
        'immediate' : 1,
        'prev' :      2,
        'previous' :  2,
    }


class ShadowBunchView(ShadowBunch):
    _names = {
        'new' :      0,
        'prev' :     1,
    }


class ElementConstructorInternal(object):
    __slots__ = (
        '_new',
        '_cls',
        '_args',
        '_kwargs',
    )
    def __init__(self, new, cls, args, kwargs):
        self._new    = new
        self._cls    = cls
        self._args   = args
        self._kwargs = kwargs

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust_safe(
            self,
            name_child = None,
            parent = None,
            **kwargs
    ):
        for aname, aval in kwargs.items():
            prev = self._kwargs.setdefault(aname, aval)
            if prev != aval:
                raise RuntimeError("Assigning Constructor item {0}, to {1}, but previously assigned {2}".format(aname, aval, prev))

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust_defer(
            self,
            name_child   = None,
            parent = None,
            **kwargs
    ):
        for aname, aval in kwargs.items():
            self._kwargs.setdefault(aname, aval)

    #the "None" parameters are to prevent accidental override of these from the kwargs
    def adjust(
            self,
            name_child   = None,
            parent = None,
            **kwargs
    ):
        for aname, aval in kwargs.items():
            self._kwargs[aname] = aval

    def construct(
            self,
            parent,
            name,
            **kwargs_stack
    ):
        kwargs = dict(self._kwargs)
        kwargs.update(kwargs_stack)
        args   = self._args
        cls    = self._cls
        kwargs.setdefault('name_child',   name)
        kwargs.setdefault('parent',       parent)
        inst = self._new(
            cls,
            *args,
            **kwargs
        )
        #because of the deferred construction, the __init__ function must be explicitely called
        try:
            inst.__init__(
                *args,
                **kwargs
            )
        except TypeError as e:
            #print("ERROR: ", e)
            #print(inst)
            raise_from_with_traceback(
                BadInitCallError("Init Call for " + repr(inst.__class__.__name__) + " " + str(e)),
                #cause = e,
            )
        return inst

    def __getattr__(self, aname):
        try:
            return super(ElementConstructorInternal, self).__getattr__(aname)
        except AttributeError as e:
            raise AttributeError(
                "Instance of {0} not fully constructed, but be immediately bound into appropriate object"
                " before accessing attribute {1}".format(self._cls, aname)
            )


class BadInitCallError(TypeError):
    pass


PropertyTransforming.register(ElementConstructorInternal)


class ElementBase(object):
    """
    Physical elements MUST be assigned to a sled, even if it is the root sled.
    They have special object creation semantics such that the class does not fully
    create the object, it's creation is completed only on the sled
    """
    _defer_build = True

    def __new__(
        cls, *args, **kwargs
    ):
        if cls._defer_build:
            #TODO make this a class returned that gives sane error messages
            #for users not realizing the dispatch must happen
            constr = ElementConstructorInternal(
                new = super(ElementBase, cls).__new__,
                cls = cls,
                args = args,
                kwargs = kwargs,
            )
            return constr
        else:
            inst = super(ElementBase, cls).__new__(
                cls,
                *args,
                **kwargs
            )
            #the __init__ function must not be explicitely called because python does this for us
            return inst

    def __init__(
            self,
            **kwargs
    ):
        super(ElementBase, self).__init__(**kwargs)

    def __repr__(self):
        if self.name is not None:
            return self.name
        return self.__class__.__name__ + '(<unknown>)'

    if __debug__:
        def __setattr__(self, name, item):
            if isinstance(item, PropertyTransforming):
                if not hasattr(self.__class__, name):
                    raise RuntimeError("Cannot directly assign sub-elements, use ...{cname}.own.{name} = ... instead".format(cname = self.name_child, name = name))
            return super(ElementBase, self).__setattr__(name, item)


def invalidate_auto(func):
    @wraps(func)
    def wrap_func(self, *args, **kwargs):
        retval = func(self, *args, **kwargs)
        #print(func.__name__)
        #self._registry_invalidate
        self._registry_invalidate[func.__name__] = None
        return retval
    return wrap_func


class BaseGetattr(object):
    def __getattr__(self, name):
        raise AttributeError(name)

class Element(
    ElementBase,
    AttrExpandingObject,
    OverridableObject,
    BaseGetattr,
):

    @mproperty_check
    def name_child(self, arg):
        return arg

    @mproperty_check
    def name(self, arg = NOARG):
        if arg is NOARG:
            #TODO, make this output the shortest unique root name
            arg = self.name_system
        return arg

    def generate_child_system_name(self, name):
        return self.name_system + "." + name

    @mproperty_check
    def name_system(self):
        return self.parent.generate_child_system_name(self.name_child)

    def generate_child_ctree(self, name, child):
        return self.ctree[name]

    @mproperty_check
    def ctree(self, arg = NOARG):
        if arg is NOARG:
            arg = self.parent.generate_child_ctree(self.name_child, self)
        return arg

    @dproperty
    def parent(self, arg = NOARG):
        if arg is NOARG:
            raise RuntimeError("Must Specify")
        if arg is self:
            raise RuntimeError("Should be None, probably")
        arg.child_register(self.name_child, self)
        return arg

    @dproperty
    def root(self):
        #TODO: remove this root reference
        return self.parent.root

    @mproperty
    def inst_prototype(self, arg = NOARG):
        if arg is NOARG:
            if self.parent is None:
                return None
            pre = self.parent.inst_prototype
            if pre is None:
                arg = None
            else:
                try:
                    arg = pre[self.name_child]
                except KeyError:
                    arg = None
        else:
            if isinstance(arg, str):
                arg = self.root[arg]
            else:
                raise NotImplementedError()
        return arg

    @mproperty_check
    def inst_prototype_t(self, arg = NOARG):
        #TODO: clean up prototype name semantics
        if arg is NOARG:
            if self.inst_prototype is not None:
                pproto_t = self.parent.inst_prototype_t
                if pproto_t == 'base':
                    arg = 'full'
                else:
                    arg = 'base'
            else:
                arg = None
        return arg

    @mproperty_check
    def inst_preincarnation(self, arg = NOARG):
        if arg is NOARG:
            if self.parent is None:
                return None
            pre = self.parent.inst_preincarnation
            if pre is None:
                arg = None
            else:
                try:
                    arg = pre[self.name_child]
                except KeyError:
                    arg = None
        return arg

    @mproperty
    def _registry_inserted_pre(self):
        #make a copy
        pre = dict()

        #use the inst_prototype's if not otherwise defined
        if self.inst_prototype is not None:
            pre.update(self.inst_prototype._registry_inserted)

        if self.inst_preincarnation is not None:
            pre.update(self.inst_preincarnation._registry_inserted)

        return pre

    @mproperty
    def _registry_invalidate(self):
        return dict()

    @mproperty
    def _registry_inserted(self):
        return dict()

    _is_completed = False
    def _complete(self):
        if self._is_completed:
            return True
        self._is_completed = True
        registry = self._registry_inserted_pre
        while registry:
            k, v = registry.popitem()
            if k not in self._registry_children:
                #insert to registry regardless of if building
                self._registry_inserted[k] = v
                #and insert
                self.insert(obj = v, name = k)
        for k, v in self._registry_children.items():
            v._complete()
        return False

    def invalidate(self):
        #assert(False)
        #print("Invalidate")
        self._is_completed = False
        reg = self._registry_invalidate
        while reg:
            meth, call = reg.popitem()
            if call is None:
                delattr(self, meth)
            else:
                call(meth)
        for cname, child in self._registry_children.items():
            child.invalidate()
        return

    @mproperty
    def _registry_children(self):
        return dict()

    def __getitem__(self, name):
        try:
            return self._registry_children[name]
        except KeyError:
            #only on key error should we check for dot-splitting. It is faster.
            spl = name.split('.')
            if len(spl) > 1:
                pl = self
                for k in spl:
                    pl = pl[k]
                return pl
            else:
                item = self._registry_inserted_pre.pop(name)
                return self.insert(obj = item, name = name)

    def __getattr__(self, name):
        try:
            return super(Element, self).__getattr__(name)
        except AttributeError as E:
            try:
                if name in self._registry_children or name in self._registry_inserted_pre:
                    return self[name]
                else:
                    #TODO this logic is broken for dotted indexes
                    #print("RAISING: ", repr(self), name)
                    raise
            except KeyError as k:
                if k.message != name:
                    raise
                #raise the previous exception as that one is easier to understand and may include a
                #wider variety of issues than this final dictionary key check
                #TODO cleanup for release
                print(repr(self), name)
                raise
                raise AttributeError(k.message)
        return

    def __dir__(self):
        directory = super(Element, self).__dir__()
        directory.extend(list(self._registry_children.keys()))
        return directory

    def child_register(self, name, child):
        #print("CHILD REG", self.name, name)
        if '.' in name:
            raise RuntimeError("\".\" not allowed in names (for python consistency)")
        self._registry_children[name] = child

    @mproperty
    def building(self):
        return self.parent.building

    @mproperty
    def own(self):
        return SubElementBridge(
            parent = self,
        )

    def insert(self, obj, name = None, invalidate = True):
        #print("INSERT", self.name, name, obj)
        if invalidate:
            self.root.invalidate()
        if not self.building:
            assert(name is not None)
            self._registry_inserted[name] = obj
        if isinstance(obj, PropertyTransforming):
            with self.building:
                kwargs = dict()
                if name is not None:
                    kwargs['name'] = name
                child = obj.construct(
                    parent = self,
                    **kwargs
                )
                return child
        else:
            return obj

    _overridable_object_save_kwargs = True
    _overridable_object_kwargs = None
    def replica_generate(self, **kwargs):
        kwargs_gen = dict(self._overridable_object_kwargs)
        kwargs_gen.update(kwargs)
        #print("REPLICA:", self, kwargs_gen)
        #must delete these so that the constructor is called
        del kwargs_gen['name_child']
        del kwargs_gen['parent']
        return self.__class__(
            inst_prototype = self.name_system,
            inst_prototype_t = 'base',
            **kwargs_gen
        )

    def environment_query_local(self, query):
        return None

    def environment_query(self, query):
        #TODO document environment_query
        ret = self.environment_query_local(query)
        #TODO memoize? or possibly make this non-recursive
        if ret is None:
            return self.parent.environment_query(query)
        else:
            return ret


class RootElement(Element):
    _defer_build = False

    def __init__(self, *args, **kwargs):
        with self.building:
            super(RootElement, self).__init__(*args, **kwargs)

    @mproperty_check
    def building(self):
        return BuildingCounter()

    @mproperty_check
    def root(self):
        return self

    @mproperty_check
    def parent(self):
        return None

    @mproperty_check
    def name_child(self):
        return None

    @mproperty_check
    def inst_preincarnation(self, arg = NOARG):
        if arg is NOARG:
            arg = None
        return arg

    @mproperty_check
    def name(self, arg = NOARG):
        if arg is NOARG:
            arg = self.name_child
        return arg

    def generate_child_system_name(self, name):
        return name

    @dproperty
    def name_system(self):
        return self.name_child

    @mproperty
    def ctree(self, arg = NOARG):
        #if it is a view (as generated by ctree_shadow), then extract only the new elements
        if isinstance(arg, ShadowBunchView):
            arg = arg.extractidx('new')

        full = DeepBunchSingleAssign()
        immed = DeepBunchSingleAssign()
        dicts = [full, immed, ]
        if arg is not NOARG:
            dicts.append(arg)
        return ShadowBunchN(dicts)

    def ctree_shadow(self):
        new = DeepBunch()
        return ShadowBunchView(
            dicts = [
                new,
                self.ctree,
            ]
        )

    _overridable_object_save_kwargs = True
    _overridable_object_kwargs = None

    def regenerate(self, ctree = None, **kwargs):
        usekwargs = dict(self._overridable_object_kwargs)
        if ctree is not None:
            usekwargs['ctree'] = ctree
        usekwargs.update(kwargs)
        usekwargs['inst_preincarnation'] = self
        return self.__class__(
            **usekwargs
        )


class SubElementBridge(object):
    __slots__ = ('_parent',)

    def __init__(self, parent):
        self._parent = parent

    def __setitem__(self, name, item):
        try:
            item = self._dict.setdefault(name, item)
            setattr(self._parent, name, item)
            return item
        except TypeError:
            raise TypeError("Can't insert {0} into {1} at name {2}".format(item, self._dict, name))

    def __setattr__(self, name, item):
        if name in self.__slots__:
            return super(SubElementBridge, self).__setattr__(name, item)
        return self._parent.insert(obj = item, name = name)

    def __getitem__(self, name):
        return self._parent[name]

    def __getattr__(self, name):
        try:
            return super(SubElementBridge, self).__getattr__(name)
        except AttributeError:
            pass
        try:
            return self._parent[name]
        except KeyError as E:
            raise AttributeError(str(E))

    def __dir__(self):
        directory = super(SubElementBridge, self).__dir__()
        directory.extend(list(self._parent._registry_children.keys()))
        return directory


class BuildingCounter(object):
    def __init__(self):
        self.building_count = 0

    def __enter__(self):
        self.building_count += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.building_count -= 1

    def __bool__(self):
        return bool(self.building_count)

    def __nonzero__(self):
        return bool(self.building_count)

