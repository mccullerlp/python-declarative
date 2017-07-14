# -*- coding: utf-8 -*-
"""
"""
from collections import Mapping
from numbers import Number
from ..utilities.future_from_2 import repr_compat

from ..utilities.unique import unique_generator
NOARG = unique_generator()


class ShadowBunch(object):
    """
    """
    __slots__ = ('_dicts', '_idx', '__reduce__', '__reduce_ex__')
    _names = {}

    #needed to not explode some serializers since this object generally "hasattr" almost anything
    #__reduce_ex__ = None
    #__reduce__    = None
    __copy__      = None
    __deepcopy__  = None

    def __init__(
        self,
        dicts,
        assign_idx = 0,
    ):
        self._dicts = tuple(dicts)
        self._idx   = assign_idx
        return

    def __getitem__(self, key):
        dicts = []
        anyfull = False
        for d in self._dicts:
            try:
                item = d[key]
            except KeyError:
                continue
            if not isinstance(item, Mapping):
                if dicts and anyfull:
                    #break returns the dictionaries already stored if suddenly one doesn't store a dict
                    #it DOES not just skip that item to return further dictionaries
                    break
                else:
                    return item
            if item:
                anyfull = True
            dicts.append(item)
        return self.__class__(
            dicts,
            assign_idx = self._idx,
        )

    def useidx(self, idx):
        if not isinstance(idx, Number):
            idx = self._names[idx]
        return self.__class__(
            self._dicts,
            assign_idx = idx,
        )

    def extractidx(self, idx, default = NOARG):
        if not isinstance(idx, Number):
            idx = self._names[idx]
        try:
            return self._dicts[idx]
        except IndexError:
            if default is NOARG:
                raise
            return default

    def __getattr__(self, key):
        try:
            return super(ShadowBunch, self).__getattr__(key)
        except AttributeError:
            pass
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError("'{0}' not in {1}".format(key, self))

    def __setitem__(self, key, item):
        self._dicts[self._idx][key] = item

    def __setattr__(self, key, item):
        if key in self.__slots__:
            return super(ShadowBunch, self).__setattr__(key, item)
        return self.__setitem__(key, item)

    def __delitem__(self, key):
        del self._dicts[self._idx][key]

    def __delattr__(self, key):
        return self.__delitem__(key)

    def get(self, key, default = NOARG):
        if key in self:
            return self[key]
        elif default is not NOARG:
            return default
        raise KeyError(key)

    def setdefault(self, key, default):
        dicts = []
        anyfull = False
        for d in self._dicts:
            try:
                item = d[key]
            except KeyError:
                continue
            if not isinstance(item, Mapping):
                if dicts and anyfull:
                    #break returns the dictionaries already stored if suddenly one doesn't store a dict
                    #it DOES not just skip that item to return further dictionaries
                    break
                else:
                    return item
            if item:
                anyfull = True
            dicts.append(item)
        if anyfull:
            return self.__class__(
                dicts,
                assign_idx = self._idx,
            )
        else:
            self[key] = default
            return default

    def __contains__(self, key):
        for d in self._dicts:
            if key in d:
                return True
        return False

    def has_key(self, key):
        return key in self

    def __dir__(self):
        items = list(super(ShadowBunch, self).__dir__())
        for d in self._dicts:
            items.extend(d.keys())
        items.sort()
        return items

    @repr_compat
    def __repr__(self):
        return (
            '{0}({1}, idx={2})'
        ).format(
            self.__class__.__name__,
            self._dicts,
            self._idx,
        )

    def _repr_pretty_(self, p, cycle):
        if cycle:
            p.text(self.__class__.__name__ + '(<recurse>)')
        else:
            with p.group(4, self.__class__.__name__ + '([', '])'):
                first = True
                for d in self._dicts:
                    p.pretty(d)
                    p.breakable()
                if not first:
                    p.text(',')
                    p.breakable()
        return

    #def __eq__(self, other):
    #    return
    #
    #def __ne__(self, other):
    #    return not (self == other)

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        ks = set()
        for d in self._dicts:
            ks.update(d.keys())
        return len(ks)

    def __bool__(self):
        for d in self._dicts:
            if d:
                return True
        else:
            return False

    def keys(self):
        ks = set()
        for d in self._dicts:
            ks.update(d.keys())
        return iter(ks)

    def values(self):
        for key in self.keys():
            yield self[key]
        return

    def items(self):
        for key in self.keys():
            yield key, self[key]
        return


Mapping.register(ShadowBunch)
