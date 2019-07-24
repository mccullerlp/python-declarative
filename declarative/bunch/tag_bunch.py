# -*- coding: utf-8 -*-
"""
"""
try:
    from collections.abc import Mapping as MappingABC
except ImportError:
    from collections import Mapping as MappingABC
from ..utilities.future_from_2 import str, object, repr_compat, unicode
from ..utilities.unique import NOARG

from .deep_bunch import DeepBunch


class TagBunch(object):
    """
    """
    __slots__ = ('_dict', '_tag_dicts',)

    def __init__(
        self,
        write_dict = None,
        gfunc = None,
        **kwargs
    ):
        if write_dict is None:
            write_dict = DeepBunch()
        self._dict = write_dict
        self._tag_dicts = kwargs
        if gfunc is True:
            self.require_tag('gfunc')
        elif gfunc is not None:
            self.set_tag('gfunc', gfunc)
        return

    @property
    def _gfunc(self):
        return self.get_tag('gfunc')

    def __getitem__(self, key):
        gfunc = self._tag_dicts.get('gfunc', None)
        if gfunc is not None and (key not in self._dict):
            gval = gfunc.get(key, None)
            if gval is not None:
                item = gval()
                self._dict[key] = item

        item = self._dict[key]
        if isinstance(item, MappingABC):
            subtags = {}
            for tagkey, tagdict in list(self._tag_dicts.items()):
                if isinstance(tagdict, MappingABC):
                    try:
                        subtags[tagkey] = tagdict[key]
                    except KeyError:
                        continue
            item = self.__class__(item, **subtags)
        return item

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError("'{0}' not in {1}".format(key, self))

    def __setitem__(self, key, item):
        self._dict[key] = item

    def __setattr__(self, key, item):
        if key in self.__slots__:
            return super(TagBunch, self).__setattr__(key, item)
        return self.__setitem__(key, item)

    def __delitem__(self, key):
        del self._dict[key]

    def __delattr__(self, key):
        return self.__delitem__(key)

    def get(self, key, default = NOARG):
        try:
            return self[key]
        except KeyError:
            if default is not NOARG:
                return default
            raise

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def get_tag(self, tagkey, default = NOARG):
        try:
            return self._tag_dicts[tagkey]
        except KeyError:
            if default is not NOARG:
                return default
            raise

    def has_tag(self, key):
        return key in self._tag_dicts

    def require_tag(self, tagkey):
        if tagkey not in self._tag_dicts:
            self._tag_dicts[tagkey] = DeepBunch({})
        return

    def set_tag(self, tagkey, obj):
        self._tag_dicts[tagkey] = obj
        return

    def __contains__(self, key):
        return (key in self._dict)

    def has_key(self, key):
        return key in self

    def __dir__(self):
        items = list(k for k in self._dict.keys() if isinstance(k, (str, unicode)))
        items.sort()
        #items += dir(super(Bunch, self))
        return items

    @repr_compat
    def __repr__(self):
        return (
            '{0}({1}, {2})'
        ).format(
            self.__class__.__name__,
            self._dict,
            self._tag_dicts,
        )

    #def __eq__(self, other):
    #    return
    #
    #def __ne__(self, other):
    #    return not (self == other)

    def __iter__(self):
        return iter(list(self.keys()))

    def __len__(self):
        return len(self._dict)

    def iterkeys(self):
        return iter(list(self._dict.keys()))

    def keys(self):
        return list(self._dict.keys())

    def itervalues(self):
        for key in list(self.keys()):
            yield self[key]
        return

    def values(self):
        return list(self.values())

    def iteritems(self):
        for key in list(self.keys()):
            yield key, self[key]
        return

    def items(self):
        return list(self.items())


MappingABC.register(TagBunch)
