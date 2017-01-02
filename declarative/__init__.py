#!/usr/bin/env python2
"""
"""
from .properties import (
    HasDeclaritiveAttributes,
    mproperty,
    dproperty,
    mproperty_fns,
    dproperty_fns,
    mproperty_plain,
    dproperty_plain,
    NOARG,
    mfunction,
    PropertyTransforming,
    group_dproperty,
    group_mproperty,
    mproperty_adv,
    dproperty_adv,
)

from .callbacks import (
    callbackmethod,
    Callback,
    RelayBool,
    RelayBoolAny,
    RelayBoolAll,
    RelayBoolNotAny,
    RelayBoolNotAll,
    RelayBoolNot,
    RelayValue,
    RelayValueRejected,
    RelayValueCoerced,
    min_max_validator,
    min_max_validator_int,
)

from .utils.lazy import lazy
from .bunch import (
    Bunch,
    DeepBunch,
    TagBunch,
)

from .overridable_object import (
    OverridableObject,
)

from .parent_carriers import (
    ParentCarrier,
    ParentRoot,
    recurse_down_parents_for,
)

from .metaclass import (
    AutodecorateMeta,
    Autodecorate,
    AttrExpandingObject,
    GetSetAttrExpandingObject,
)

def first_non_none(*args):
    for a in args:
        if a is not None:
            return a
    return None

FNN = first_non_none

