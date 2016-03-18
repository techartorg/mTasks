# mTasks
simple, unthreaded multitasking  with a Maya twist

This module provides a limited form of coroutine based multi-tasking. 

It's not intended as a substitute for 'real' threads, but it does allow you to create the illusion of multiple, simultaneous processes without crossing thread boundaries.  This is particularly important in Maya, where only the main thread is allowed to touch the contents of the Maya scene or the GUI. It can also be useful in other applications where you'd like concurrent behavior without worrying about the memory-security issues associated with multiple threads.  For Maya programming it allows a degree of interacivity which is otherwise complicated hard to create with scriptJobs or threads and `executeDeferred()` -- and it also makes it easy to avoid the kinds of baffling behaviors and random crashes that are so common when trying to work with threads.

Basics
------

The way it works is quite simple. Everything you want to run 'simultaneously' is a a function which uses Python's built-in `yield` keyword to release control. `mTasks` keeps a list of your functions and loops through the list, running each until it his a yield and then switching to the next. Here's a basic example:

    def hello():
        print "hello"
        yield
        
    def world():
        print "world"
        yield
        
    def exclaim():
        print "!"
        yield
        
    spawn(hello)
    spawn(world)
    spawn(exclaim)
    
    run()
    
    # hello
    # world
    # !
    
If you just used `yield` in place of `return`, this would be the same as collecting the functions in a and running them in turn. However `yield`
 *does not have to end a function*. So you could rewrite the previous example like this:
 
    def hello():
        print "hello"
        yield
        print "word"
        yield
        print "!"
        yield
        
    spawn(hello)
    run()
    
    # hello
    # world
    # !

Any number of functions containing yields can run at the saem time, and their results will be interleaved:

    def numbers():
        for n in range (10):
            print "number: ", n
            yield
            
    def letters():
        for a in 'abcdefghijklmnopqrstuvwxyz':
            print "letter: ", a
            yield
            
    spawn(numbers)
    spawn(letters)
    run()
    
    # number: 1
    # letter: a
    # number: 2
    # letter: b
    
    # and so... until numbers runs out, but letters keeps going:
    
    # letter: l
    # letter: m
    # letter: n
    
Running tasks
----------
All of the tasks are owned by the `scheduler` module.  The scheduler will step through each task in turn, executing until it finds a `yield` or the task terminates. The scheduler's `tick()` methods fires the next function/yield step -- in Maya the tick is usually hooked up to a Maya scriptJob that advances it on every Maya idle event.  In a non-Maya context you can set the schedulder to run until all tasks are exhausted with the `run()` method. You generally **don't** want to call `run()` in Maya because it will act like a blocking function call until all of the queued tasks are done.

Monitoring and killing tasks
----------

You can find all of the running tasks with `list_jobs()`.  Each job is assigned an integer id when spawned. It can be killed using the `kill()` command.  

    print list_jobs()
    # {1 : <sometask@1>, 8: <__wrapped__@8> }
    kill (8)



Scheduling
----------

The `spawn` function adds a callable to the mTasks system, starting it immediately (see `tick()`, below).  You can also queue up functions to to run when other functions complete by using `defer_spawn()` -- which creates a task without running it -- and `join()`, which like a traditional thread join, waits for one task to finish before starting another.  For example:

    def hello():
        print "hello"
        yield
        print "word"
        yield
        print "!"
        yield
        
    def goodbye():
        print "goodby cruel world"
        yield
        
    h = spawn(hello)
    g = defer_spawn(goodbye)
    join(h, g)
    run()
    
    # hello
    # world
    # !
    # goodbye cruel world
    
A task can join any number of other tasks and will only execute after they have all completed.

It's often useful to defer an action for a set amount of time.  In traditional threaded programming you would use `time.sleep()` to pause a thread.  However you _don't_ want to do that in an `mTask`, since the entire system is running in the main thread! Instead you can use a `DelayTimer` or an `AwaitTimer` to defer execution by just yielding until its time to run:

    
    from mTasks.timers import DelayTimer
    
    def wait_five_seconds():
        delay = DelayTimer(5)
        while delay:
            yield
        print "5 seconds have elapsed!"
    
    
The `AwaitTimer` works the same way except you pass it an absolute time to begin, instead of a relative time.  

There are convenience functions to add a delay or wait to a regular function:

    delay(your_function, 5)  #add a 5 second delay to your_function
    await(your_function, 1483185599)  # wait until midnight on new years eve 2016



    
This idea was pioneered by [David Beazley](http://www.dabeaz.com/generators/).
