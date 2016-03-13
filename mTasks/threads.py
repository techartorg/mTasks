
from threading import *
from task import task_logger
from timers import *

from Queue import Queue

class ExternalTask(object):

    def __init__(self, thread_function, callback = None, timeout = 0):

        self.event = Event()

        wrapped_function = self.wrap_thread(thread_function)
        self.thread = Thread(target = wrapped_function)
        self.thread.daemon = True
        self.timeout = timeout
        self.callback = callback

    def timeout_test(self):
        if self.timeout:
            return DelayTimer(self.timeout)
        else:
            return True

    def wrap_thread(self, fn):
        def signal_done():
            try:
                fn()
            finally:
                self.event.set()
        return signal_done

    def __call__(self):
        self.thread.start()
        not_expired = self.timeout_test()

        while not self.event.isSet():
            if not_expired:
                if self.callback:
                    yield self.callback()
                else:
                    yield
            else:
                task_logger.info( "thread job timed out")
                break

        task_logger.info("thread job completed")


class ExternalResultTask(ExternalTask):
    def __init__(self, thread_function, item_callback = None, result_callback = None, timeout = 0):

        self.result_queue = Queue()
        self.result_callback = result_callback
        super(ExternalResultTask, self).__init__(thread_function, item_callback, timeout )

    def wrap_thread(self, fn):
        def signal_done():
            try:
                fn(self.result_queue)
            finally:
                self.event.set()
        return signal_done

    def __call__(self):
        self.thread.start()
        not_expired = self.timeout_test()

        while not self.event.isSet():
            if not_expired:
                if self.callback:
                    yield self.callback(self.result_queue)
                else:
                    yield
            else:
                task_logger.info( "thread job timed out")
                break
        if self.result_callback:
            self.result_callback(self.result_queue)
        task_logger.info("thread job completed")

