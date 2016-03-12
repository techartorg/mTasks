__author__ = 'stevet'

import  scheduler
from maya.cmds import scriptJob

_state = {
    'job': -1
}

def sj_indices():
    return set(int(i.partition(":")[0]) for i in scriptJob(lj=True))

def start():
    if _state.get('job') in sj_indices():
        # scheduler is already running
        return
    scheduler_job = scriptJob(e=('idle', scheduler.tick))
    _state['job'] = scheduler_job



def suspend():
    existing = _state.get('job')
    if existing in sj_indices():
        scriptJob(k=existing)
        _state['job'] = -1


def stop():
    '''
    stop the scheduler and release any still-active tasks
    '''
    suspend()
    scheduler.reset()