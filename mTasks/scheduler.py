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
_await_list = collections.defaultdict(list)


def spawn(coroutine, callback=None):
    """
    add a new task for function <coroutine>, with optional <callback> function
    if defer is True, the task will not be started immediately

    returns the id of the new task
    """
    new_task = Task(coroutine, callback)
    _job_registry[new_task.id] = new_task
    _ready_queue.put(new_task)
    return new_task.id

def defer_spawn(coroutine, callback=None):
    """
    Create a task without starting it -- used to create tasks for joins
    """
    new_task = Task(coroutine, callback)
    _job_registry[new_task.id] = new_task
    return new_task.id


def kill(task_id):
    """
    remove task <task_id> from the systems
    """
    result = _job_registry.pop(task_id, None)
    _signal_list.pop(task_id, None)

    if result:
        deferred_tasks = _join_list.pop(result.id, tuple())
        for deferred_task in deferred_tasks:
            _await_list[deferred_task].remove(task_id)
            if not _await_list[deferred_task]:
                _await_list.pop(deferred_task)
                waiting_task = _job_registry.get(deferred_task)
                _ready_queue.put(waiting_task)
    return result



def join(existing_task, joining_task):
    """
    make task with id <joining task> dependent on task with id <existing task>.  Returns the ids
    of all the tasks on which <joining task> depends
    """
    if not existing_task in _job_registry:
        raise RuntimeError("No active task: %s" % existing_task)
    if not joining_task  in _job_registry:
        raise RuntimeError("No active task: %s" % joining_task)

    _join_list[existing_task].append(joining_task)
    _await_list[joining_task].append(existing_task)

    return _await_list[joining_task]


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


__all__ = 'spawn defer_spawn kill join signal tick run reset list_jobs list_waiting'.split()
