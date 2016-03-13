# mTasks
simple, unthreaded multitasking  with a Maya twist

This module provides a limited form of coroutine based multi-tasking. 

It's not intended as a substitute for 'real' threads, but it does allow you to create the illusion of multiple, simultaneous processes without crossing thread
boundaries.  This is particularly important in Maya, where only the main thread is allowed to touch the contents of the Maya scene or the GUI. It can also be useful
in other applications where you'd like concurrent behavior without worrying about the memory-security issues associated with multiple threads.

Basics
------

The way it works is quite simple. Everything you want to run 'simultaneously' is a a function which uses Python's built-in `yield` keyword to release control.
`mTasks` keeps a list of your functions and loops through the list, running each until it his a yield and then switching to the next. Here's a basic example:

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
    


Scheduling
----------

The `spawn` function adds a callable to the mTasks system, starting it immediately (see `tick()`, below).  You can also queue up functions to to run when other functions
complete.  For example:

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
    join(h, goodbye)
    run()
    
    # hello
    # world
    # !
    # goodbye cruel world
    

    
This idea was pioneered by [David Beazley](http://www.dabeaz.com/generators/).
