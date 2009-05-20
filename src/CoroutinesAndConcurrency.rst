.. index::
   coroutines
   concurrency
   threads
   parallelism
   multiprocessing
   GIL: Global Interpreter Lock

********************************************************************************
Coroutines, Concurrency & Distributed Systems
********************************************************************************

Primary focus should be on:

1) Using ``yield`` to create coroutines

2) Using the new ``multiprocessing`` module

and then showing some alternative techniques.

foo bar :func:`input` baz.

Multiprocessing
===============================================================================

Example by Michele Simionato in comp lang python.
Here is an example of using multiprocessing (which is included
in Python 2.6 and easy_installable in older Python versions)
to print a spin bar while a computation is running::

    import sys, time
    import multiprocessing
    DELAY = 0.1
    DISPLAY = [ '|', '/', '-', '\\' ]
    def spinner_func(before='', after=''):
        write, flush = sys.stdout.write, sys.stdout.flush
        pos = -1
        while True:
            pos = (pos + 1) % len(DISPLAY)
            msg = before + DISPLAY[pos] + after
            write(msg); flush()
            write('\x08' * len(msg))
            time.sleep(DELAY)
    def long_computation():
        # emulate a long computation
        time.sleep(3)
    if __name__ == '__main__':
        spinner = multiprocessing.Process(
            None, spinner_func, args=('Please wait ... ', ''))
        spinner.start()
        try:
            long_computation()
            print 'Computation done'
        finally:
            spinner.terminate()


On the Erlang mail list, four years ago, Erlang expert Joe Armstrong posted this:

    In Concurrency Oriented (CO) programming you concentrate on the concurrency and the messages between the processes. There is no sharing of data.

    [A program] should be thought of thousands of little black boxes all doing things in parallel - these black boxes can send and receive messages. Black boxes can detect errors in other black boxes - that's all.
    ...
    Erlang uses a simple functional language inside the [black boxes] - this is not particularly interesting - *any* language that does the job would do - the important bit is the concurrency.

On the Squeak mail list in 1998, Alan Kay had this to say:

    ...Smalltalk is not only NOT its syntax or the class library, it is not even about classes. I'm sorry that I long ago coined the term "objects" for this topic because it gets many people to focus on the lesser idea.

    The big idea is "messaging" -- that is what the kernal of Smalltalk/Squeak is all about... The key in making great and growable systems is much more to design how its modules communicate rather than what their internal properties and behaviors should be. Think of the internet -- to live, it (a) has to allow many different kinds of ideas and realizations that are beyond any single standard and (b) to allow varying degrees of safe interoperability between these ideas.

    If you focus on just messaging -- and realize that a good metasystem can late bind the various 2nd level architectures used in objects -- then much of the language-, UI-, and OS based discussions on this thread are really quite moot.


Further Reading
================================================================================

    `This article
    <http://guidewiredevelopment.wordpress.com/2008/10/06/a-more-clearly-stated-version-of-my-argument/>`_
    argues that large-scale parallelism -- which is what
    ``multiprocessing`` supports -- is the more important problem to solve, and
    that functional languages don't help that much with this problem.

    http://jessenoller.com/2009/02/01/python-threads-and-the-global-interpreter-lock/

.. Good introduction to Twisted:
.. http://jessenoller.com/2009/02/11/twisted-hello-asynchronous-programming/

.. Also
.. http://jessenoller.com/2009/02/02/an-interview-with-adam-olsen-author-of-safe-threading-completely-different/

.. Generators and coroutines:
.. http://groups.google.com/group/comp.lang.python/browse_thread/thread/aacd809829d6b6ce/

.. ShowMeDo: Scientific and Parallel Computing Using IPython:
.. http://blog.showmedo.com/2009/05/05/scientific-and-parallel-computing-using-ipython/
