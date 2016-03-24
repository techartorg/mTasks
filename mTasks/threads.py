import inspect
from Queue import Queue
from threading import *

from task import task_logger
from timers import *


class AsyncTask(object):
    """
    run <thread_function> in a new thread it until it ends or has run for longer than <timeout> seconds.

    If <callback> is provided, it will be executed when the task completes or times out. The return value,
    if any, will be the final state of the task.
    """

    def __init__(self, thread_function, callback=None, timeout=0):

        self.event = Event()

        wrapped_function = self.wrap_thread(thread_function)
        self.thread = Thread(target=wrapped_function)
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
                yield
            else:
                task_logger.info("thread job timed out")
                return
        if self.callback:
            self.callback()

        task_logger.info("thread job completed")


class AsyncResultTask(AsyncTask):
    """
    run <thread_function> in a new thread it until it ends or has run for longer than <timeout> seconds.

    The thread function will be passed a Queue.queue object which it can update with results, either 
    incrementally or all at once. If <thread_function> takes no arguments, its results will be added to the
    queue object when it completes.

    if <callback> is provided, it will be called with the result queue as an argument when
    <thread_function> completes.


     It is possible to use both callbacks or either one alone.
    """

    def __init__(self, thread_function, callback=None, timeout=0):

        self.result_queue = Queue()
        super(AsyncResultTask, self).__init__(thread_function, callback, timeout)

    def wrap_thread(self, fn):

        output_fn = fn
        if not inspect.getargspec(fn).args:
            def add_queue(q):
                q.put(fn())

            output_fn = add_queue

        def signal_done():
            try:
                output_fn(self.result_queue)
            finally:
                self.event.set()

        return signal_done

    def tick(self):
        return None

    def __call__(self):
        self.thread.start()
        not_expired = self.timeout_test()

        while not self.event.isSet():
            if not_expired:
                yield self.tick()
            else:
                task_logger.info("thread job timed out")
                return
        if self.callback:
            self.callback(self.result_queue)
        task_logger.info("thread job completed")


class AsyncPollTask(AsyncResultTask):
    def __init__(self, thread_function, monitor_callback, callback=None,  timeout=0):

        self.monitor_callback = monitor_callback
        super(AsyncPollTask, self).__init__(thread_function, callback, timeout)

    def tick(self):
        return self.monitor_callback(self.result_queue)