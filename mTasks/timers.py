import time

class DelayTimer(object):
    """
    return True until (duration) seconds from instantiation time.  The usual idiom is

        ... do something...

        waiting = DelayTimer(2.5)
        while waiting:
            yield

        ... do more stuff ...

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
    return True until the specified time
    """

    __slots__ = 'expiry'

    def __init__(self, target_time):
        self.expiry = target_time


def delay(fn, delay_time):
    """
    returns <fn> wrapped with a built-in delay of <delay_time> seconds.  When scheduled,
    <fn> will wait for <delay_time> seconds before beginning.
    """
    return DelayTimer.create(fn, delay_time)


def after(fn, start_time):
    """
    returns <fn> wrapped with a built-in delay timer that won't fire until <start time>

    <start time> is expressed in python seconds (the same format as time.time())
    """
    return AwaitTimer.create(fn, start_time)


def repeat(fn, initial_delay, repeat_delay, repeats):
    """
    returns <fn> wrapped with a delay timer and a repeat timer.  When scheduled, <fn> will wait for
    <initial_delay> seconds and fire. When completed, it will wait for <repeat_delay> seconds before
    starting again. It will continue for <repeats> repeats.  If repeats is set to 0, the function
    will repeat forever.
    """
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