__author__ = 'stevet'
import logging
logging.basicConfig()

import sys
from mTasks.scheduler import *

def days():
    for item in 'monday tuesday wednesday thursday friday saturday sunday'.split():
        sys.stdout.write( item )
        yield


def dates():
    for item in range (30):
        sys.stdout.write( '\t')

        sys.stdout.write( str(item + 1))
        sys.stdout.write( '\n')
        yield

def done():

    spawn(days)
    yield
    
d = spawn(days)
dd = spawn(dates)
j = defer_spawn(done)
join(d, j)

run()