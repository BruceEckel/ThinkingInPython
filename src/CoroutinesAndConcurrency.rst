.. index::
   coroutines
   concurrency
   threads
   parallelism
   multiprocessing
   GIL: Global Interpreter Lock

********************************************************************************
Coroutines & Concurrency
********************************************************************************

Primary focus should be on:

1) Using ``yield`` to create coroutines

2) Using the new ``multiprocessing`` module

and then showing some alternative techniques.

foo bar :func:`input` baz.

Further Reading
================================================================================

    `This article
    <http://guidewiredevelopment.wordpress.com/2008/10/06/a-more-clearly-stated-version-of-my-argument/>`_
    argues that large-scale parallelism -- which is what
    ``multiprocessing`` supports -- is the more important problem to solve, and
    that functional languages don't help that much with this problem.

        