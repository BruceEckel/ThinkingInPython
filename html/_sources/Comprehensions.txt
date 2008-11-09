.. index::
   pair: list; comprehension
   pair: generator; comprehension

********************************************************************************
Comprehensions
********************************************************************************

History: where did they come from?

They require a mind shift.

What makes them so compelling (once you 'get it')?

A two-level list comprehension using ``os.walk()``::

    # Comprehensions/os_walk_comprehension.py
    import os
    restFiles = [os.path.join(d[0], f) for d in os.walk(".")
                 for f in d[2] if f.endswith(".rst")]
    for r in restFiles:
        print(r)

