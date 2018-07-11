# -*- coding: utf-8 -*-
"""
"""
from __future__ import (print_function, absolute_import)
from ..utilities.representations import ReprMixin
from ..utilities.unique import unique_generator
from ..properties import mproperty
_debug_loud = False


_UNIQUE = unique_generator()


class RelayBoolBase(ReprMixin):
    """
    Base class for the relay bools and their interfaces.

    All subclasses should implement :obj:`__nonzero__`

    .. automethod:: __init__

    .. automethod:: register

    .. autoattribute:: is_set
    """
    __slots__ = ('callbacks_ontoggle', '_assign_protect')
    __repr_slots__ = ('is_set', 'name')

    def __init__(self, name = '', **kwargs):
        """
        """
        super(RelayBoolBase, self).__init__(**kwargs)
        self._assign_protect = None
        self.name = name
        self.callbacks_ontoggle = {}
        return

    @property
    def is_set(self):
        """
        Returns T/F status of the bool
        """
        return bool(self)

    @property
    def value(self):
        return bool(self)

    def __nonzero__(self):
        return self.__bool__()

    def __bool__(self):
        raise NotImplementedError()

    def register(
        self,
        key            = None,
        callback       = None,
        call_immediate = False,
        assumed_value  = _UNIQUE,
        remove         = False,
    ):
        """
        """
        if key is None:
            key = callback
        if key is None:
            raise RuntimeError("Key or Callback must be specified")
        if self._assign_protect is not None:
            raise RuntimeError("Assign Assigned during assign!")
        if not remove:
            ocb = self.callbacks_ontoggle.setdefault(key, callback)
            if ocb is not callback:
                raise RuntimeError(
                    ("Same key registered to multiple callbacks key: {0}, callback {1}"
                     ).format(key, callback)
                )
            if assumed_value is not _UNIQUE:
                if bool(self) != assumed_value:
                    callback(bool(self))
            elif call_immediate:
                callback(bool(self))
        else:
            if assumed_value is not _UNIQUE:
                if bool(self) != assumed_value:
                    callback(assumed_value)
            self.callbacks_ontoggle.pop(key)
        return

    def register_via(self, reg_call, callback, key = None, remove = False, **kwargs):
        if key is None:
            key = callback
        if not remove:
            def meta_cb(bstate):
                reg_call(callback = callback, remove = not bstate, **kwargs)
            self.register(
                key = key,
                callback = meta_cb,
                assumed_value = False,
            )
        else:
            self.register(
                key = key,
                assumed_value = False,
                remove = True,
            )
        return

    @mproperty
    def notted(self):
        return RelayBoolNot(self)


class RelayBool(RelayBoolBase):
    """
    This is a raw Relay Bool value, explicitely settable

    .. automethod:: __init__

    .. automethod:: assign

    .. automethod:: toggle
    """
    __slots__ = ('state',)

    def __init__(self, initial_state, **kwargs):
        """
        :param initial_state: initial boolean state held
        """
        super(RelayBool, self).__init__(**kwargs)
        self.state = initial_state
        return

    def __bool__(self):
        return self.state

    def assign(self, value):
        return self.put(value)

    def put(self, value):
        """
        Set the value held by this instance
        """
        #python has no xor!
        if (value and not self.state) or (not value and self.state):
            self.state = not self.state
            #print repr(self.callbacks_ontoggle)
            if self._assign_protect is not None:
                raise RuntimeError("Assign Assigned during assign!")
            self._assign_protect = self.state
            try:
                for callback in list(self.callbacks_ontoggle.values()):
                    callback(self.state)
            finally:
                self._assign_protect = None
        return

    def put_valid(self, val):
        return self.put(val)

    def put_exclude_cb(self, value, key):
        """
        Set the value held by this instance
        """
        #python has no xor!
        if (value and not self.state) or (not value and self.state):
            self.state = not self.state
            #print repr(self.callbacks_ontoggle)
            if self._assign_protect is not None:
                raise RuntimeError("Assign Assigned during assign!")
            self._assign_protect = self.state
            try:
                for cb_key, callback in list(self.callbacks_ontoggle.items()):
                    if key != cb_key:
                        callback(self.state)
            finally:
                self._assign_protect = None
        return

    def put_valid_exclude_cb(self, val, key):
        return self.put_exclude_cb(val, key)

    @property
    def value(self):
        return bool(self)

    @value.setter
    def value(self, val):
        return self.put(val)

    def assign_on(self):
        """
        Set the value held by this instance
        """
        #python has no xor!
        if not self.state:
            self.state = True
            #print repr(self.callbacks_ontoggle)
            if self._assign_protect is not None:
                raise RuntimeError("Assign Assigned during assign!")
            self._assign_protect = self.state
            try:
                for callback in list(self.callbacks_ontoggle.values()):
                    callback(self.state)
            finally:
                self._assign_protect = None
        return

    def assign_off(self):
        """
        Set the value held by this instance
        """
        #python has no xor!
        if self.state:
            self.state = False
            #print repr(self.callbacks_ontoggle)
            if self._assign_protect is not None:
                raise RuntimeError("Assign Assigned during assign!")
            self._assign_protect = self.state
            try:
                for callback in list(self.callbacks_ontoggle.values()):
                    callback(self.state)
            finally:
                self._assign_protect = None
        return

    def assign_toggle(self):
        """
        Toggle the Value held by this instance
        """
        self.state = not self.state
        #print repr(self.callbacks_ontoggle)
        if self._assign_protect is not None:
            raise RuntimeError("Assign Assigned during assign!")
        self._assign_protect = self.state
        try:
            for callback in list(self.callbacks_ontoggle.values()):
                callback(self.state)
        finally:
            self._assign_protect = None
        return


class RelayBoolNot(RelayBoolBase):
    """
    Is true iff state_label's state is the state given

    .. automethod:: __init__

    .. automethod:: register
    """
    __slots__ = ('sub_bool',)

    def __init__(self, sub_bool, **kwargs):
        """
        :param sub_bool: RelayBool this value takes the negation of
        """
        super(RelayBoolNot, self).__init__(**kwargs)
        self.sub_bool = sub_bool
        return

    def __bool__(self):
        return not self.sub_bool

    def _monitor_callback(self, value):
        if self._assign_protect is not None:
            raise RuntimeError("Assign Assigned during assign!")
        self._assign_protect = not self.sub_bool
        try:
            for callback in list(self.callbacks_ontoggle.values()):
                callback(not value)
        finally:
            self._assign_protect = None
        return

    def register(
        self,
        key            = None,
        callback       = None,
        call_immediate = False,
        assumed_value  = _UNIQUE,
        remove         = False
    ):
        """
        Register a function for callback when this bool's state changes.

        :param callback: function to register
        :param call_immediate: call as the function is added
        :param remove: (False) set to remove a callback
        :raises: :exc:`KeyError` on missing callback

        The function should have the signature

        .. function:: callback(bool_state):

            :param bool_state: state of the RelayBool's **new** value

        """
        if not remove:
            if not self.callbacks_ontoggle:
                self.sub_bool.register(self, self._monitor_callback)
            super(RelayBoolNot, self).register(
                key            = key,
                callback       = callback,
                assumed_value  = assumed_value,
                call_immediate = call_immediate,
                remove         = remove
            )
        else:
            super(RelayBoolNot, self).register(
                key            = key,
                callback       = callback,
                assumed_value  = assumed_value,
                call_immediate = call_immediate,
                remove         = remove
            )
            if not self.callbacks_ontoggle:
                self.sub_bool.register(self, self._monitor_callback, remove = True)
        return


class RelayBoolGate(RelayBoolBase, ReprMixin):
    """
    Base class to implement the logic needed for syncronous action of logic gates of RelayBools.

    These gates are all based on monitoring sub-bools using a count. Subclasses set the values of

    .. attribute:: _input_not

    .. attribute:: _output_not

    .. automethod:: register
    """
    __slots__ = ('monitored_bools_count', 'monitored_bools')

    _input_not = False
    _output_not = False

    def __init__(self, relay_bools = (), **kwargs):
        """
        :param relay_bools: iterable of Relays Bools to set up initial gate value
        """
        super(RelayBoolGate, self).__init__(**kwargs)
        #None means monitoring is off
        self.monitored_bools_count = None
        self.monitored_bools = dict()
        iitems = None
        try:
            iitems = iter(list(relay_bools.items()))
        except AttributeError:
            pass
        if iitems:
            for b, name in iitems:
                self.monitored_bools[b] = [name]
        else:
            for b in relay_bools:
                self.monitored_bools[b] = [None]

        #self._monitor_value_start()

    def __contains__(self, subbool):
        return subbool in self.monitored_bools

    def __bool__(self):
        if not self._output_not:
            if self.monitored_bools_count is None:
                return bool(self._compute_count())
            else:
                return bool(self.monitored_bools_count)
        else:
            if self.monitored_bools_count is None:
                return (not self._compute_count())
            else:
                return (not self.monitored_bools_count)
        #can't reach
        raise

    def _compute_count(self):
        if not self._input_not:
            return sum(bool(monbool) for monbool in self.monitored_bools)
        else:
            return sum((not monbool) for monbool in self.monitored_bools)

    def bool_register(self, relay_bool, name = None, remove = False):
        if remove:
            return self.bool_unregister(relay_bool)
        name_list = self.monitored_bools.setdefault(relay_bool, [])
        if name_list:
            #Already a relay bool, just adding a name to it
            name_list.append(name)
            return
        #wasn't already inserted, so add the name and register it through the callbacks
        name_list.append(name)
        if self.monitored_bools_count is not None:
            relay_bool.register(self, self._monitor_callback_deb(relay_bool, name))
            if not self._input_not:
                add_val = bool(relay_bool)
            else:
                add_val = not bool(relay_bool)
            if add_val:
                self.monitored_bools_count += 1
                if self.monitored_bools_count == 1:
                    if self._assign_protect is not None:
                        raise RuntimeError("Assign Assigned during assign!")
                    self._assign_protect = bool(self)
                    try:
                        for callback in list(self.callbacks_ontoggle.values()):
                            callback(not self._output_not)
                    finally:
                        self._assign_protect = None
            return

    def bool_unregister(self, relay_bool, name = None):
        if relay_bool not in self.monitored_bools:
            raise RuntimeError("Missing Bool Registry!")
        name_list = self.monitored_bools[relay_bool]
        name_list.remove(name)
        if name_list:
            #still registered bools for this name, so don't delete it
            return
        del self.monitored_bools[relay_bool]
        if self.monitored_bools_count is not None:
            relay_bool.register(self, None, remove = True)
            if not self._input_not:
                sub_val = bool(relay_bool)
            else:
                sub_val = not bool(relay_bool)
            if sub_val:
                self.monitored_bools_count -= 1
                if self.monitored_bools_count == 0:
                    if self._assign_protect is not None:
                        raise RuntimeError("Assign Assigned during assign!")
                    self._assign_protect = bool(self)
                    try:
                        for callback in list(self.callbacks_ontoggle.values()):
                            callback(self._output_not)
                    finally:
                        self._assign_protect = None
        return

    def _monitor_callback_deb(self, rbool, bname):
        if __debug__ and _debug_loud:
            print(("has added {0} - {1}, {2}".format(
                repr(self),
                repr(rbool),
                bname,
            )))
            def deb(value):
                print(("{0} at count {cnt}, {1}, {2}, {3}".format(
                    repr(self),
                    repr(rbool),
                    bname,
                    value,
                    cnt = self.monitored_bools_count,
                )))
                self._monitor_callback(value)
            return deb
        else:
            return self._monitor_callback

    def _monitor_callback(self, value):
        #xor with the input not
        if (self._input_not and not value) or (not self._input_not and value):
            self.monitored_bools_count += 1
            if self.monitored_bools_count == 1:
                #no longer are all of them on
                if self._assign_protect is not None:
                    raise RuntimeError(self)
                self._assign_protect = bool(self)
                try:
                    for callback in list(self.callbacks_ontoggle.values()):
                        callback(not self._output_not)
                finally:
                    self._assign_protect = None
        else:
            self.monitored_bools_count -= 1
            if self.monitored_bools_count == 0:
                #no longer are all of them off
                if self._assign_protect is not None:
                    raise RuntimeError()
                self._assign_protect = bool(self)
                try:
                    for callback in list(self.callbacks_ontoggle.values()):
                        callback(self._output_not)
                finally:
                    self._assign_protect = None
        return

    def _monitor_value_start(self):
        """
        """
        assert(self.monitored_bools_count is None)
        self.monitored_bools_count = 0
        for monbool, bname in list(self.monitored_bools.items()):
            #monbool.register(self, self._monitor_callback)
            monbool.register(self, self._monitor_callback_deb(monbool, bname))
            #add the xor
            self.monitored_bools_count += ((not self._input_not and bool(monbool)) or (self._input_not and not bool(monbool)))

        return

    def _monitor_value_stop(self):
        """
        """
        assert(self.monitored_bools_count is not None)
        for monbool in self.monitored_bools:
            monbool.register(key = self, callback = self._monitor_callback, remove = True)
        self.monitored_bools_count = None
        return

    def register(
        self,
        key            = None,
        callback       = None,
        assumed_value  = _UNIQUE,
        call_immediate = False,
        remove         = False
    ):
        """
        Register a function for callback when this bool's state changes.

        :param callback: function to register
        :param call_immediate: call as the function is added
        :param remove: (False) set to remove a callback
        :raises: :exc:`KeyError` on missing callback

        The function should have the signature

        .. function:: callback(bool_state):

            :param bool_state: state of the RelayBool's **new** value

        """
        if not remove:
            try:
                super(RelayBoolGate, self).register(
                    key            = key,
                    callback       = callback,
                    call_immediate = call_immediate,
                    assumed_value  = assumed_value,
                )
            except:
                raise
            else:
                if self.monitored_bools_count is None:
                    self._monitor_value_start()
            if call_immediate:
                callback(bool(self))
        else:
            try:
                super(RelayBoolGate, self).register(
                    key           = key,
                    callback      = callback,
                    assumed_value = assumed_value,
                    remove        = True
                )
            except:
                raise
            else:
                if (
                    (not self.callbacks_ontoggle) and
                    (self.monitored_bools_count is not None)
                ):
                    self._monitor_value_stop()
        return


class RelayBoolAny(RelayBoolGate):
    """
    Or/Any gate for a collection of RelayBools
    """
    _input_not = False
    _output_not = False


class RelayBoolAll(RelayBoolGate):
    """
    And/All gate for a collection of RelayBools
    """
    _input_not = True
    _output_not = True


class RelayBoolNotAny(RelayBoolGate):
    """
    Nor/Not Any gate for a collection of RelayBools
    """
    _input_not = False
    _output_not = True


class RelayBoolNotAll(RelayBoolGate):
    """
    Nand/Not All gate for a collection of RelayBools
    """
    _input_not = True
    _output_not = False


