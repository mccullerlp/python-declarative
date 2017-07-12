"""
"""
from __future__ import (division, print_function, absolute_import)
#from builtins import object

from declarative.callbacks import (Callback, callbackmethod)

from declarative import (
    OverridableObject,
    mproperty,
    NOARG,
)


oldprint = print
print_test_list = []
def print(*args):
    oldprint(*args)
    if len(args) == 1:
        print_test_list.append(args[0])
    else:
        print_test_list.append(args)


def message(message):
    print(message)

class TCallback(object):

    def __init__(self):
        self.callback = Callback()

    @callbackmethod
    def callbackmethod(self, message):
        print(('callbackmethod', message))

T = TCallback()
T.callback.register(callback = print, key = print)
T.callbackmethod.register(callback = message, key = message)

T.callback('hello')
T.callbackmethod('world')


