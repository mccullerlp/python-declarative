# -*- coding: utf-8 -*-
"""
"""
import functools
import threading
#from builtins import object

callback_lock = threading.Lock()


class Callback(object):
    """
    Callable object dispatching its call to registered callbacks

    :param initialcall: First call for the in the sequence, also provides docstring
    :param doc: (optional) can override the docstring for this object.

    This object provides functions transparently as extendable callback hooks.

    .. automethod:: register

    """
    __slots__ = (
        'initialcall',
        'callbacks',
        '_callbacks_edit',
        '_callbacks_editting',
    )

    def __init__(self, initialcall = None, doc = None):
        self.initialcall = initialcall
        self.callbacks = {}
        self._callbacks_edit = self.callbacks
        self._callbacks_editting = 0

        if doc:
            self.__doc__ = doc
        else:
            if initialcall is not None:
                #TODO: Find why this is broken
                #self.__doc__ = initialcall.__doc__
                pass
        return

    def register(
        self,
        key      = None,
        callback = None,
        remove   = False,
        throw    = False
    ):
        """
        Register a function into the callback

        :param key: registration key for callback
        :type key: hashable
        :param callback: function to be called
        :raises: KeyError if callback key is already present (keys must be unique)
        """
        if key is None:
            key = callback
        if key is None:
            raise RuntimeError("Key or callback must be specified")
        with callback_lock:
            if (
                (self._callbacks_editting > 0) and
                (self._callbacks_editting is self.callbacks)
            ):
                #make a copy to edit on
                self._callbacks_edit = dict(self.callbacks)
            if not remove:
                if key in self._callbacks_edit:
                    raise KeyError(key)
                self._callbacks_edit[key] = callback
            else:
                try:
                    del self._callbacks_edit[key]
                except KeyError:
                    if throw:
                        raise

    def __call__(self, *args, **kwargs):
        if self.initialcall is not None:
            self.initialcall(*args, **kwargs)
        self._callbacks_editting += 1
        for callback in list(self.callbacks.values()):
            callback(*args, **kwargs)
        with callback_lock:
            self._callbacks_editting -= 1
            if self._callbacks_editting == 0:
                c_edit = self._callbacks_edit
                if c_edit is not self.callbacks:
                    self.callbacks = c_edit
        return


class callbackmethod(object):
    """
    Wraps a function into a callback

    :param fget: function to wrap as the default with docstring
    :param doc: (optional) provide this as the docstring rather than using fget's

    This wraps the method so that whenever it is called, other registered callbacks
    are called (after the instancemethod).

    This type is a :term:`descriptor(non-data)`. It is intended to be used via the
    :term:`decorator` syntax.

    Internally this works by constructing a callback object and memoizing it to preserve
    any callbacks added to it.
    """

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc if doc else fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        callback = Callback(
            initialcall = functools.partial(self.fget, obj)
        )
        #obj.__dict__[self.__name__] = callback
        setattr(obj, self.__name__, callback)
        return callback


class callbackstaticmethod(object):
    """
    Like :class:`callbackmethod`, but does not provide `self`

    :param fget: function to wrap as the default with docstring
    :param doc: (optional) provide this as the docstring rather than using fget's

    This wraps the method so that whenever it is called, other registered callbacks
    are called (after the instancemethod). Note that self is **not** automatically added
    to the method call (so any method wrapped by this becomes like a staticmethod).

    This type is a :term:`descriptor(non-data)`. It is intended to be used via the
    :term:`decorator` syntax.

    Internally this works by constructing a callback object and memoizing it to preserve
    any callbacks added to it.

    """

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc if doc else fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        callback = Callback(initialcall = self.fget)
        #obj.__dict__[self.__name__] = callback
        setattr(obj, self.__name__, callback)
        return callback


class SingleCallback(object):
    """
    Provides a callback which can only be registered to once, allowing the callback
    to provide a return value. This type uses the __call__ interface to transparently
    act as the callback registered to it.

    :param default: a default function to call if the callback is not registered.

    The default argument also provides the docstring for the descriptor attribute.

    .. automethod:: register
    """
    __slots__ = ('callback', 'default')

    def __init__(self, default = None, doc = None):
        #class sets the callback originally
        self.default = default
        self.callback = default

        if doc:
            self.__doc__ = doc
        else:
            if default is not None:
                self.__doc__ = default.__doc__
        return

    def register(self, callback, remove = False):
        """
        Register the function into the callback

        :param key: registration key for callback
        :type key: hashable
        :param callback: function to be called
        :raises: KeyError if callback key is already present or if removing and not present.
        """
        if not remove:
            if self.callback is not self.default:
                raise RuntimeError('Single Callbacks may not be registered while they contain a callback')
            self.callback = callback
        else:
            if self.callback is self.default:
                raise RuntimeError('Single Callbacks must be registered when unregister is called')
            self.callback = self.default
        return

    def __call__(self, *args, **kwargs):
        self.callback(*args, **kwargs)


class singlecallbackmethod(object):
    """
    Like :class:`callbackmethod`, but is used for singlecallbacks.

    :param fget: function to wrap as the default with docstring
    :param doc: (optional) provide this as the docstring rather than using fget's

    Wraps the decorator function with a :class:`~.SingleCallback`, providing the wrapped
    function as the default (not called once the callback is set). This is mostly useful for
    providing docstrings to callback methods.

    Internally this works by constructing a callback object and memoizing it to preserve
    any callbacks added to it.

    This type is a :term:`descriptor(non-data)`. It is intended to be used via the
    :term:`decorator` syntax.
    """

    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc if doc else fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        callback = Callback(default = functools.partial(self.fget, obj))
        #obj.__dict__[self.__name__] = callback
        setattr(obj, self.__name__, callback)
        return callback


