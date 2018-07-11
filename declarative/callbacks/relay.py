# -*- coding: utf-8 -*-
"""
"""
from ..utilities.representations import ReprMixin
from ..properties import mproperty
import numpy as np

_UNIQUE = ("UNIQUE",)


class RelayValueRejected(Exception):
    pass


class RelayValueCoerced(RelayValueRejected):
    def __init__(self, preferred):
        self.preferred = preferred


class RelayValue(ReprMixin):
    """
    """
    __slots__ = ('callbacks', '_value')
    __repr_slots__ = ('_value',)

    @staticmethod
    def validator(val):
        return val

    def __init__(
        self,
        initial_value,
        validator = None,
        **kwargs
    ):
        """
        """
        super(RelayValue, self).__init__(**kwargs)
        self.callbacks = {}
        if validator is not None:
            self.validator = validator
        initial_value = self.validator(initial_value)
        self._value = initial_value
        return

    def register(
        self,
        key            = None,
        callback       = None,
        assumed_value  = _UNIQUE,
        call_immediate = False,
        remove         = False,
    ):
        """
        """
        if key is None:
            key = callback
        if key is None:
            raise RuntimeError("Key or Callback must be specified")
        if not remove:
            self.callbacks[key] = callback
            if assumed_value is not _UNIQUE:
                if self._value != assumed_value:
                    callback(self._value)
            elif call_immediate:
                callback(self._value)
        else:
            if assumed_value is not _UNIQUE:
                if self._value != assumed_value:
                    callback(assumed_value)
            del self.callbacks[key]
        return

    def validator_assign(self, validator, remove = False):
        if not remove:
            if self.validator is not self.__class__.validator:
                raise RuntimeError("Can not set multiple validators")
            self.validator = validator
        else:
            del self.validator
        return

    def put(self, val):
        if np.any(val != self._value):
            val = self.validator(val)
            self._value = val
            for cb in list(self.callbacks.values()):
                cb(val)
        return

    def put_exclude_cb(self, val, key):
        if val != self._value:
            val = self.validator(val)
            self._value = val
            for cb_key, cb in list(self.callbacks.items()):
                if cb_key is not key:
                    cb(val)
        return

    def put_coerce(self, val):
        if np.any(val != self._value):
            try:
                val = self.validator(val)
                retval = True
            except RelayValueCoerced as E:
                val = E.preferred
                retval = False
            self._value = val
            for cb in list(self.callbacks.values()):
                cb(val)
            return retval
        return True

    def put_coerce_exclude_cb(self, val, key):
        if val != self._value:
            try:
                val = self.validator(val)
                retval = True
            except RelayValueCoerced as E:
                val = E.preferred
                retval = False
            self._value = val
            for cb_key, cb in list(self.callbacks.items()):
                if cb_key is not key:
                    cb(val)
            return retval
        return True

    def put_valid(self, val):
        if val != self._value:
            self._value = val
            for cb in list(self.callbacks.values()):
                cb(val)
        return

    def put_valid_exclude_cb(self, val, key):
        if val != self._value:
            self._value = val
            for cb_key, cb in list(self.callbacks.items()):
                if cb_key is not key:
                    cb(val)
        return

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if np.any(val != self._value):
            val = self.validator(val)
            self._value = val
            for cb in list(self.callbacks.values()):
                cb(val)
        return

    @mproperty
    def shadow(self):
        return self.__class__(self.value, validator = self.validator)

    def shadow_from(self):
        self.put_valid(self.shadow._value)
        return

    def shadow_to(self):
        self.shadow.put_valid(self._value)
        return


