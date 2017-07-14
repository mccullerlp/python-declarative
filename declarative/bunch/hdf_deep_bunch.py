# -*- coding: utf-8 -*-
"""
Requires h5py to interface
"""
from __future__ import print_function
from ..utilities.future_from_2 import repr_compat
import h5py
import numpy as np
from collections import Mapping

from ..utilities.unique import NOARG
from ..utilities.interrupt_delay import DelayedKeyboardInterrupt


def hdf_group_is(item):
    return isinstance(item, (h5py.File, h5py.Group))


def hdf_data_is(item):
    return isinstance(item, (h5py.Dataset, str))


def hdf_assert_grouplike(hdf):
    if hdf_data_is(hdf):
        raise RuntimeError(
            "HDFDeepBunch virtual-path mutated in file to"
            "become a dataset, python can't deal with this"
            "dataset creation should happen before virtual paths"
            "can be created. Dataset: {0}".format(hdf)
        )
    return


class HDFDeepBunch(object):
    """
    """
    __slots__ = ('_hdf', '_vpath', '_overwrite')

    def __init__(
        self,
        hdf = None,
        vpath = None,
        writeable = False,
        overwrite = False,
    ):
        if isinstance(hdf, str):
            if writeable:
                hdf = h5py.File(hdf, 'a')
                if vpath is None:
                    vpath = True
            else:
                hdf = h5py.File(hdf, 'r')

        #access through super is necessary because of the override on __setattr__ can't see these slots
        super(HDFDeepBunch, self).__setattr__('_hdf', hdf)
        super(HDFDeepBunch, self).__setattr__('_overwrite', overwrite)

        if hdf.file.mode not in ('r+', 'a', 'a+', 'w', 'w+'):
            if vpath is not None:
                raise RuntimeError("Can't open file for writing, virtual paths should not be used")

        if vpath is True:
            vpath = ()
        elif vpath is False:
            vpath = None
        elif vpath is not None:
            vpath = tuple(vpath)
        #self.__dict__['_vpath'] = vpath
        super(HDFDeepBunch, self).__setattr__('_vpath', vpath)
        return

    def _resolve_hdf(self):
        """
        Returns the hdf object stored at the currently-referenced group.
        If the current reference is virtual, then the hdf is indexed and may throw if the groups do not exist.
        """
        if not self._vpath:
            return self._hdf
        try:
            hdf = self._hdf
            for idx in range(len(self._vpath)):
                gname = self._vpath[idx]
                hdf = hdf[gname]
                hdf_assert_grouplike(hdf)
        except KeyError:
            if idx != 0:
                self._hdf = hdf
                self._vpath = self._vpath[idx:]
            return None
        self._hdf = hdf
        self._vpath = ()
        return hdf

    @property
    def hdf(self):
        return self._resolve_hdf()

    @property
    def overwrite(self):
        return self.__class__(
            self._hdf,
            vpath = self._vpath,
            overwrite = True,
        )

    @property
    def safewrite(self):
        return self.__class__(
            self._hdf,
            vpath = self._vpath,
            overwrite = False,
        )

    def _require_hdf(self):
        if not self._vpath:
            return self._hdf
        hdf = self._hdf
        for gname in self._vpath:
            hdf = hdf.require_group(gname)
            hdf_assert_grouplike(hdf)
        self._vpath = ()
        self._hdf = hdf
        return hdf

    def __getitem__(self, key):
        hdf = self._resolve_hdf()
        if hdf is None:
            return self.__class__(
                self._hdf,
                self._vpath + (key,),
                self._overwrite,
            )
        try:
            item = hdf[key]
            if hdf_group_is(item):
                return self.__class__(
                    item,
                    vpath = self._vpath,
                    overwrite = self._overwrite,
                )
            elif isinstance(item, (h5py.Dataset)):
                arr = np.asarray(item)
                if item.dtype.kind == 'V':
                    return arr
                if arr.shape == ():
                    return arr.item()
                return arr
            if item == '<none>':
                return None
            return item
        except KeyError as E:
            if self._vpath is not None:
                return self.__class__(
                    self._hdf,
                    self._vpath + (key,),
                    self._overwrite,
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
        hdf = self._require_hdf()
        try:
            if item is None:
                hdf[key] = '<none>'
            else:
                hdf[key] = item
            return
        except TypeError:
            print((item, type(item)))
            raise TypeError("Can't insert {0} into {1} at key {2}".format(item, hdf, key))
        except (RuntimeError, ValueError) as E:
            if str(E).lower().find('name already exists') != -1 and self._overwrite:
                del hdf[key]
                hdf[key] = item
            else:
                raise TypeError("Can't insert {0} into {1} at key {2} error: {3}".format(item, hdf, key, E))

    def __setattr__(self, key, item):
        if key in self.__slots__:
            return super(HDFDeepBunch, self).__setattr__(key, item)
        return self.__setitem__(key, item)

    def update_recursive(
        self,
        data_dict,
        groups_overwrite  = False,
        hdf_internal_link = False,
        hdf_external_link = False,
        hdf_copy          = False,
    ):
        """
        Provide a recursive dictionary or collections.Mapping compatible object as the first argument. This dictionary is "injected" into the hdf file.
        Sub-mappings become groups and non-mappings become data arrays.

        If the bunch is in overwrite-mode, then data may be overwritten with new data or groups.

        If the groups_overwrite is specified, then even groups may be overwritten

        If the dictionary provided contains some elements which are themselves HDF Files, Groups or other HDFDeepBunch objects, then the keywords
        hdf_internal_link = False
        hdf_external_link = False
        hdf_copy          = False
        are used to determine if links should be used or if the data should be copied.
        hdf_internal_link acts if the referenced file is the same as the one receiving the update_from_dict_recursive call.
        Otherwise hdf_external_link will create a file link (currently not implemented and throws NotImplementedError).
        If hdf_copy is specified and the appropriate link option is false, then the hdf groups are copied.
        """
        self._require_hdf()
        def apply_hdf(subref, key, hdf):
            refhdf = subref._require_hdf()
            try:
                subval = refhdf[key]
                if hdf_group_is(subval):
                    if not groups_overwrite:
                        raise RuntimeError("Won't Overwrite groups")
                    else:
                        del refhdf[key]
                else:
                    if not self._overwrite:
                        raise RuntimeError("Won't Overwrite data")
                    else:
                        del refhdf[key]
            except KeyError:
                pass
            if (refhdf.file == hdf.file):
                if hdf_internal_link:
                    refhdf[key] = hdf
                elif hdf_copy:
                    refhdf.copy(hdf, key)
                else:
                    raise RuntimeError("Object provided is an internal HDF group or bunch, but neither hdf_copy nor hdf_internal_link specified")
            else:
                if hdf_external_link:
                    raise NotImplementedError()
                elif hdf_copy:
                    refhdf.copy(hdf, key)
                else:
                    raise RuntimeError("Object provided is an external HDF group or bunch, but neither hdf_copy nor hdf_external_link specified")

        def recursive_action(subref, data_dict):
            for key, value in list(data_dict.items()):
                if isinstance(value, Mapping):
                    if groups_overwrite:
                        self.require_deleted(key)
                        subsubref = subref[key]
                    else:
                        subsubref = subref[key]
                        if not isinstance(subsubref, HDFDeepBunch):
                            if self._overwrite:
                                del subref[key]
                                subsubref = subref[key]
                            else:
                                raise RuntimeError("Won't Overwrite data")
                    recursive_action(subsubref, value)
                elif hdf_group_is(value):
                    apply_hdf(subref, key, value)
                elif isinstance(value, HDFDeepBunch):
                    value = value.hdf
                    apply_hdf(subref, key, value)
                else:
                    subref[key] = value
        with DelayedKeyboardInterrupt():
            recursive_action(self, data_dict)
        return

    def __delitem__(self, key):
        hdf = self._resolve_hdf()
        if hdf is None:
            return
        del self._hdf[key]

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

    def __contains__(self, key):
        hdf = self._resolve_hdf()
        if hdf is None:
            return False
        return key in hdf

    def has_key(self, key):
        hdf = self._resolve_hdf()
        if hdf is None:
            return False
        return key in hdf

    def require_deleted(self, key):
        hdf = self._resolve_hdf()
        if hdf is None:
            return
        try:
            del self._hdf[key]
        except KeyError:
            pass
        return

    @classmethod
    def ensure_wrap(cls, item):
        if isinstance(item, cls):
            return item
        return cls(item)

    def __dir__(self):
        items = sorted(self._hdf.keys())
        items += ['overwrite', 'safewrite', 'hdf']
        #items += dir(super(Bunch, self))
        return items

    @repr_compat
    def __repr__(self):
        if self._vpath is None:
            vpath = 'False'
        elif self._vpath == ():
            vpath = 'True'
        else:
            vpath = self._vpath
        return (
            '{0}({1}, vpath={2}, overwrite={3})'
        ).format(
            self.__class__.__name__,
            self._hdf,
            vpath,
            self._overwrite
        )

    def __iter__(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return iter(())
        return iter(hdf)

    def __len__(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return 0
        return len(hdf)

    def clear(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return
        for key in list(hdf.keys()):
            del hdf[key]
        return

    def keys(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return iter(())
        return iter(list(hdf.keys()))

    def values(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return
        for key in list(hdf.keys()):
            yield self[key]
        return

    def items(self):
        hdf = self._resolve_hdf()
        if hdf is None:
            return
        for key in list(hdf.keys()):
            yield key, self[key]
        return

Mapping.register(HDFDeepBunch)
