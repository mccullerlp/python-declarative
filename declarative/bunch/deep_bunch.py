# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
from ..utilities.future_from_2 import repr_compat, object, str, unicode
try:
    from collections.abc import Mapping as MappingABC
except ImportError:
    from collections import Mapping as MappingABC

#use local noarg to not conflict with others
_NOARG = lambda : _NOARG
NOARG = (_NOARG,)


class DeepBunch(object):
    """
    """
    __slots__     = ('_dict', '_vpath',)
    #needed to not explode some serializers since this object generally "hasattr" almost anything
    __reduce_ex__ = None
    __reduce__    = None
    __copy__      = None
    __deepcopy__  = None

    def __init__(
        self,
        mydict = None,
        writeable = None,
        _vpath = None,
    ):
        if mydict is None:
            mydict = dict()
        #access through super is necessary because of the override on __setattr__ can't see these slots
        if not isinstance(mydict, dict):
            mydict = dict(mydict)
        super(DeepBunch, self).__setattr__('_dict', mydict)

        if _vpath is None:
            if writeable is None:
                writeable = True
            if writeable:
                _vpath = (),

        if _vpath is True:
            _vpath = ()
        elif _vpath is False:
            pass
        elif _vpath is not None:
            _vpath = tuple(_vpath)
        assert(_vpath is not None)
        #self.__dict__['_vpath'] = vpath
        super(DeepBunch, self).__setattr__('_vpath', _vpath)
        return

    def _resolve_dict(self):
        if not self._vpath:
            return self._dict
        try:
            mydict = self._dict
            for idx, gname in enumerate(self._vpath):
                mydict = mydict[gname]
                #TODO: make better assert
                assert(isinstance(mydict, MappingABC))
        except KeyError:
            if idx != 0:
                self._dict = mydict
                self._vpath = self._vpath[idx:]
            return None
        self._dict = mydict
        self._vpath = ()
        return mydict

    @property
    def mydict(self):
        return self._resolve_dict()

    @property
    def _mydict_resolved(self):
        d = self._resolve_dict()
        if d is None:
            return dict()
        return d

    def _require_dict(self):
        if not self._vpath:
            return self._dict
        mydict = self._dict
        for gname in self._vpath:
            mydict = mydict.setdefault(gname, {})
            #TODO: make better assert
            assert(isinstance(mydict, MappingABC))
        self._vpath = ()
        self._dict = mydict
        return mydict

    def __getitem__(self, key):
        mydict = self._resolve_dict()
        if mydict is None:
            if self._vpath is False:
                raise RuntimeError("This DeepBunch cannot index sub-dictionaries which do not exist.")
            return self.__class__(
                mydict = self._dict,
                _vpath = self._vpath + (key,),
            )
        try:
            item = mydict[key]
            if isinstance(item, MappingABC):
                return self.__class__(
                    mydict = item,
                    _vpath = self._vpath,
                )
            return item
        except KeyError as E:
            if self._vpath is not False:
                return self.__class__(
                    mydict = self._dict,
                    _vpath = self._vpath + (key,),
                )
            if str(E).lower().find('object not found') != -1:
                raise KeyError("key '{0}' not found in {1}".format(key, self))
            raise

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError("'{1}' not in {0}".format(self, key))

    def __setitem__(self, key, item):
        mydict = self._require_dict()
        try:
            mydict[key] = item
            return
        except TypeError:
            raise TypeError("Can't insert {0} into {1} at key {2}".format(item, mydict, key))

    def __setattr__(self, key, item):
        if key in self.__slots__:
            return super(DeepBunch, self).__setattr__(key, item)
        return self.__setitem__(key, item)

    def __delitem__(self, key):
        mydict = self._resolve_dict()
        if mydict is None:
            return
        del self._dict[key]

    def __delattr__(self, key):
        return self.__delitem__(key)

    def get(self, key, default = NOARG):
        mydict = self._resolve_dict()
        if mydict is None:
            if default is not NOARG:
                return default
            else:
                raise KeyError("key '{0}' not found in {1}".format(key, self))
        try:
            return mydict[key]
        except KeyError:
            if default is not NOARG:
                return default
            raise

    def setdefault(self, key, default):
        mydict = self._require_dict()
        return mydict.setdefault(key, default)

    def __contains__(self, key):
        mydict = self._resolve_dict()
        if mydict is None:
            return False
        return key in mydict

    def has_key(self, key):
        mydict = self._resolve_dict()
        if mydict is None:
            return False
        return key in mydict

    def require_deleted(self, key):
        mydict = self._resolve_dict()
        if mydict is None:
            return
        try:
            del self._dict[key]
        except KeyError:
            pass
        return

    def update_recursive(self, db = None, **kwargs):
        if self._vpath is False:
            def recursive_op(to_db, from_db):
                for key, val in list(from_db.items()):
                    if isinstance(val, MappingABC):
                        try:
                            rec_div = to_db[key]
                        except KeyError:
                            rec_div = dict()
                        recursive_op(rec_div, val)
                        if rec_div:
                            to_db[key] = rec_div
                    else:
                        to_db[key] = val
        else:
            def recursive_op(to_db, from_db):
                for key, val in list(from_db.items()):
                    if isinstance(val, MappingABC):
                        recursive_op(to_db[key], val)
                    else:
                        to_db[key] = val

        if db is not None:
            recursive_op(self, db)

        if kwargs:
            recursive_op(self, kwargs)
        return

    @classmethod
    def ensure_wrap(cls, item):
        if isinstance(item, cls):
            return item
        return cls(item)

    def __dir__(self):
        items = [k for k in self._dict.keys() if isinstance(k, (str, unicode))]
        items += ['mydict']
        #items.sort()
        #items += dir(super(Bunch, self))
        return items

    @repr_compat
    def __repr__(self):
        if self._vpath is False:
            vpath = 'False'
        elif self._vpath == ():
            vpath = 'True'
            return (
                '{0}({1})'
            ).format(
                self.__class__.__name__,
                self._dict,
            )
        else:
            vpath = self._vpath
        return (
            '{0}({1}, vpath={2},)'
        ).format(
            self.__class__.__name__,
            self._dict,
            vpath,
        )

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text(self.__class__.__name__ + '(<recurse>)')
        else:
            with p.group(4, self.__class__.__name__ + '(', ')'):
                first = True
                for k, v in sorted(list(self._dict.items())):
                    if not first:
                        p.text(',')
                        p.breakable()
                    else:
                        p.breakable()
                        first = False
                    p.pretty(k)
                    p.text(' = ')
                    p.pretty(v)
                if not first:
                    p.text(',')
                    p.breakable()
        return

    def __eq__(self, other):
        try:
            return self._mydict_resolved == other._mydict_resolved
        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __iter__(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return iter(())
        return iter(mydict)

    def __len__(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return 0
        return len(mydict)

    def clear(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return
        for key in list(mydict.keys()):
            del mydict[key]
        return

    def keys(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return iter(())
        return iter(list(mydict.keys()))

    def values(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return
        for key in list(mydict.keys()):
            yield self[key]
        return

    def items(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return
        for key in list(mydict.keys()):
            yield key, self[key]
        return

    def __bool__(self):
        mydict = self._resolve_dict()
        if mydict is None:
            return False
        return bool(mydict)

    def __call__(self):
        raise RuntimeError("DeepBunch cannot be called, perhaps you are trying to call a function on something which should be contained by the parent deepbunch")

MappingABC.register(DeepBunch)

class DeepBunchSingleAssign(DeepBunch):
    def __setitem__(self, key, item):
        mydict = self._require_dict()
        try:
            mydict.setdefault(key, item)
            return
        except TypeError:
            raise TypeError("Can't insert {0} into {1} at key {2}".format(item, mydict, key))

    #def ctree_through(self, obj, **kwargs):
    #    for k, v in kwargs.iteritems():
    #        self[k] = v
    #        setattr(obj, k, self[k])
    #    return
