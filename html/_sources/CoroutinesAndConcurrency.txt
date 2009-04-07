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
