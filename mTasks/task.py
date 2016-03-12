import inspect

__author__ = 'stevet'
import logging
task_logger = logging.getLogger('mTask')


class Task(object):
    __slots__ = ('id', 'fn', 'state', 'callback')
    _next_id = 0

    def __init__(self, fn, callback=None):
        assert inspect.isgeneratorfunction(fn) or hasattr(fn, "__call__")
        Task._next_id += 1
        self.id = Task._next_id
        self.fn = fn()
        self.state = None
        if callable(callback) and not inspect.getargspec(callback).args:
            def cb(_):
                callback()

            self.callback = cb
        else:
            self.callback = callback

    def tick(self, signal):
        """
        advance this task's coroutine by one tick.

        If it excepts or complete on this step, return false
        Otherwise, return true
        """
        alive = False
        try:
            self.state = self.fn.send(signal)

        except StopIteration:
            if self.callback:
                try:
                    self.callback(self.state)
                except Exception as exc:
                    task_logger.critical("callback raised exception")
                    task_logger.exception(exc)
            task_logger.debug("task %s completed" % self)
        except Exception as exc:
            # we don't propagate so a failed task
            # does not crash the system
            task_logger.exception(exc)
            self.state = exc

        else:
            alive = True

        finally:
            return alive

    def __repr__(self):
        return "{0}@{1}".format(self.fn.__name__, self.id)
