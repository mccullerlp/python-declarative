# -*- coding: utf-8 -*-
"""
"""
try:
    from collections.abc import Mapping as MappingABC
except ImportError:
    from collections import Mapping as MappingABC
from numbers import Number
from ..utilities.future_from_2 import repr_compat, str, unicode

from ..utilities.unique import unique_generator
NOARG = unique_generator()


class ShadowBunch(object):
    """
    """
    __slots__ = ('_dicts', '_idx', '__reduce__', '__reduce_ex__', '_abdict')
    _names = {}
    #pulls all values into the active dictionary. This shows everything that has been accessed
    _pull_full  = False

    ABOUT_KEY = unique_generator()

    #needed to not explode some serializers since this object generally "hasattr" almost anything
    #__reduce_ex__ = None
    #__reduce__    = None
    __copy__      = None
    __deepcopy__  = None

    def __init__(
        self,
        dicts,
        abdict = None,
        assign_idx = 0,
    ):
        self._dicts = tuple(dicts)
        self._idx   = assign_idx
        self._abdict = abdict
        return

    def __getitem__(self, key):
        dicts = []
        anyfull = False
        for d in self._dicts:
            try:
                item = d[key]
            except KeyError:
                continue
            if not isinstance(item, MappingABC):
                if dicts and anyfull:
                    #break returns the dictionaries already stored if suddenly one doesn't store a dict
                    #it DOES not just skip that item to return further dictionaries
                    break
                else:
                    if self._pull_full:
                        if d is not self._dicts[self._idx]:
                            self._dicts[self._idx][key] = item
                    return item
            if item:
                anyfull = True
            dicts.append(item)
        if self._abdict is not None:
            abdict = self._abdict[key]
        else:
            abdict = None
        return self.__class__(
            dicts,
            assign_idx = self._idx,
            abdict = abdict,
        )

    def useidx(self, idx):
        if not isinstance(idx, Number):
            idx = self._names[idx]
        return self.__class__(
            self._dicts,
            assign_idx = idx,
            abdict = self._abdict,
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

    def setdefault(self, key, default, about = None):
        """
        kwargs is special in the it sets one of the abdicts.
        """
        dicts = []
        anyfull = False
        if about is not None:
            if self._abdict is None:
                raise RuntimeError("abdict not specified on this ShadowBunch, so setdefault cannot have an about specifier")
            self._abdict[key][self.ABOUT_KEY] = about
        for d in self._dicts:
            try:
                item = d[key]
            except KeyError:
                continue
            if not isinstance(item, MappingABC):
                if dicts and anyfull:
                    #break returns the dictionaries already stored if suddenly one doesn't store a dict
                    #it DOES not just skip that item to return further dictionaries
                    break
                else:
                    if self._pull_full:
                        if d is not self._dicts[self._idx]:
                            self._dicts[self._idx][key] = item
                    return item
            if item:
                anyfull = True
            dicts.append(item)
        if anyfull:
            if self._abdict is not None:
                abdict = self._abdict[key]
            else:
                abdict = None
            return self.__class__(
                dicts,
                assign_idx = self._idx,
                abdict = abdict,
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
            items.extend(k for k in d.keys() if isinstance(k, (str, unicode)))
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


MappingABC.register(ShadowBunch)
