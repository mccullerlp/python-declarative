
from YALL.utilities.callbacks import Callback, callbackmethod


def message(message):
    print(('message', message))

class TestCallback(object):

    def __init__(self):
        self.callback = Callback()

    @callbackmethod
    def callbackmethod(message):
        print(('callbackmethod', message))

T = TestCallback()
T.callback.register(message, message)
T.callbackmethod.register(message, message)

T.callback('hello')
T.callbackmethod('world')


