"""
This module acts as the task scheduler.  Coroutine functions can be spawned, joined or killed
"""
import Queue
import collections

from .task import Task

__author__ = 'stevet'

_ready_queue = Queue.Queue()
_job_registry = {}
_signal_list = {}
_join_list = collections.defaultdict(list)


def spawn(coroutine, callback=None):
    """
    add a new task for function <coroutine>, with optional <callback> function

    returns the id of the new task
    """
    new_task = Task(coroutine, callback)
    _job_registry[new_task.id] = new_task
    _ready_queue.put(new_task)
    return new_task.id


def kill(task_id):
    """
    remove task <task_id> from the systems
    """

    result = _job_registry.pop(task_id, None)
    _signal_list.pop(task_id, None)
    if result:
        waiters = _join_list.pop(result.id, tuple())
        for task_id in waiters:
            _ready_queue.put(task_id)
            _job_registry[task_id.id] = task_id
    return result


def join(existing_task, coroutine, callback=None):
    """
    spawn a new task for function <coroutine> which will be triggered on the completion of task with id <existing_task>
    """
    if not existing_task in _job_registry:
        raise RuntimeError("No active task: %s" % existing_task)
    joined = Task(coroutine, callback)
    _join_list[existing_task].append(joined)
    return joined.id


def signal(task_id, message):
    """
    queues a message to send to the task at id <task_id>.  The signal will be passed to the
    task on its next time slice
    """
    if task_id in _job_registry:
        _signal_list[task_id] = message


def tick():
    """
    execute one time slice
    """
    if _job_registry:
        task = _ready_queue.get()
        if task and task.id in _job_registry:
            message = _signal_list.pop(task.id, None)
            if task.tick(message):
                _ready_queue.put(task)
            else:
                kill(task.id)


def list_jobs():
    """
    lists all of the jobs in the scheduler
    """
    return _job_registry.items()


def list_waiting():
    """
    list all the jobs waiting on other jobs
    """
    return _join_list.items()


def run():
    """
    run through all of the jobs in the scheduler
    """
    while _job_registry:
        tick()


def reset():
    """
    wipe all of the existing tasks and jobs. This will be
    """
    _ready_queue = Queue.deque()
    _job_registry = {}
    _signal_list = {}
    _join_list = collections.defaultdict(list)


__all__ = 'spawn kill join signal tick run reset wait_list job_list'.split()
