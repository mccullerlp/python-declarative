# -*- coding: utf-8 -*-
"""
"""
import signal
import logging
import sys



if sys.version_info > (3,4):
    import threading
    def is_main_thread():
        return threading.current_thread() == threading.main_thread()
else:
    import threading
    def is_main_thread():
        return isinstance(threading.current_thread(), threading._MainThread)


class DelayedKeyboardInterrupt(object):
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.getsignal(signal.SIGINT)
        #only needed from main thread, and only main thread can handle signals
        if is_main_thread():
            signal.signal(signal.SIGINT, self.handler)

    def handler(self, signal, frame):
        self.signal_received = (signal, frame)
        logging.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        if is_main_thread():
            signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)



