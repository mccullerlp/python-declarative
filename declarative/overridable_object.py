"""
"""
import types

from .properties import HasDeclaritiveAttributes

from .utils.representations import SuperBase


class OverridableObject(HasDeclaritiveAttributes, SuperBase, object):
    _overridable_object_save_kwargs = False
    _overridable_object_kwargs = None

    def _overridable_object_inject(self, **kwargs):
        kwargs_unmatched = {}
        for key, obj in list(kwargs.items()):
            try:
                parent_desc = getattr(self.__class__, key)
            except AttributeError:
                kwargs_unmatched[key] = obj
                continue

            if isinstance(
                parent_desc, (
                    types.MethodType,
                    staticmethod,
                    classmethod
                )
            ):
                #vim_open_first_non_init()
                raise AttributeError(
                    (
                        "Can only redefine non-method descriptors, {0} a method of class {1}"
                    ).format(key, self.__class__.__name__)
                )
            setattr(self, key, obj)
        return kwargs_unmatched

    def __init__(self, **kwargs):
        if self._overridable_object_save_kwargs:
            self._overridable_object_kwargs = kwargs
        kwargs_unmatched = self._overridable_object_inject(**kwargs)
        if kwargs_unmatched:
            #vim_open_first_non_init()
            raise AttributeError(
                (
                    "Can only redefine class-specified attributes, class {0} does not have elements {1}"
                ).format(self.__class__.__name__, list(kwargs_unmatched.keys()))
            )
        try:
            super(OverridableObject, self).__init__()
        except RuntimeError as E:
            E._tagged_already_opened_in_vim = True
            #vim_open_first_non_init()
            raise
        self._post_init()
        return

    def _post_init(self):
        return

