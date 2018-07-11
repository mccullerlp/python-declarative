# -*- coding: utf-8 -*-
"""
"""
import math

from .relay import (
    RelayValueCoerced,
    RelayValueRejected,
)


def min_max_validator_int(min_val, max_val):
    def validator(val):
        #put limits on motion
        try:
            val = int(val)
            if val < min_val:
                val = min_val
            elif val > max_val:
                val = max_val
            if val != val:
                raise RelayValueCoerced(val)
            return
        #catch NaN's hitting the int
        except ValueError:
            raise RelayValueRejected()
        return val
    return validator


def min_max_validator(
    min_val,
    max_val,
    min_ne = False,
    max_ne = False,
    allow_nan = False
):
    if not min_ne:
        if not max_ne:
            def validator(val):
                if not math.isfinite(val):
                    if allow_nan:
                        return
                    else:
                        raise RelayValueRejected()
                #put limits on motion
                if val < min_val:
                    raise RelayValueCoerced(min_val)
                elif val > max_val:
                    raise RelayValueCoerced(max_val)
                return val
        else:
            def validator(val):
                if not math.isfinite(val):
                    if allow_nan:
                        return
                    else:
                        raise RelayValueRejected()
                #put limits on motion
                if val < min_val:
                    raise RelayValueCoerced(min_val)
                elif val >= max_val:
                    raise RelayValueRejected()
                return val
    else:
        if not max_ne:
            def validator(val):
                if not math.isfinite(val):
                    if allow_nan:
                        return
                    else:
                        raise RelayValueRejected()
                #put limits on motion
                if val <= min_val:
                    raise RelayValueRejected()
                elif val > max_val:
                    raise RelayValueCoerced(max_val)
                return val
        else:
            def validator(val):
                if not math.isfinite(val):
                    if allow_nan:
                        return
                    else:
                        raise RelayValueRejected()
                #put limits on motion
                if val <= min_val:
                    raise RelayValueRejected()
                elif val >= max_val:
                    raise RelayValueRejected()
                return val
    return validator


