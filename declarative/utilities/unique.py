# -*- coding: utf-8 -*-
"""
"""
#make noarg a VERY unique value. Was using empty tuple, but python caches it, this should be quite unique
def unique_generator():
    def UNIQUE_CLOSURE():
        return UNIQUE_CLOSURE
    return ("<UNIQUE VALUE>", UNIQUE_CLOSURE,)


NOARG = unique_generator()
