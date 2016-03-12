import time

class DelayTimer(object):
    """
    return false until (duration) seconds from instantiation time
    """
    __slots__ = 'expiry'

    def __init__(self, delay):
        self.expiry = time.time() + delay

    def __nonzero__(self):
        return self.expiry > time.time()

    @classmethod
    def create(cls, duration, fn):
        def wrapper():
            timer = cls(duration)
            while timer:
                yield
            inner = fn()
            inner.next()
            while True:
                yield inner.next()

        wrapper.func_name = "{0} ({1})".format(fn.func_name, cls.__name__)
        return wrapper


class AwaitTimer(DelayTimer):
    """
    return false until the specified time
    """

    __slots__ = 'expiry'

    def __init__(self, target_time):
        self.expiry = target_time


def delay(fn, delay_time):
    return DelayTimer.create(fn, delay_time)


def after(fn, start_time):
    return AwaitTimer.create(fn, start_time)


def repeat(fn, initial_delay, repeat_delay, repeats):
    def wrapper():
        # have to make new values here, 'repeats'
        # can't be reassigned in a closure!
        repetitions = int(repeats)
        forever = repeats == 0

        start_delay = DelayTimer(initial_delay)
        while start_delay:
            yield

        while repetitions or forever:
            inner = fn()
            inner.next()
            try:
                yield inner.next()
            except StopIteration:
                wait_again = DelayTimer(repeat_delay)
                while wait_again:
                    yield

            if repetitions:
                repetitions -= 1

    wrapper.func_name = "{0} ({1})".format(fn.func_name, 'Repeater')
    return wrapper


__all__ = 'delay repeat after DelayTimer AwaitTimer'.split()