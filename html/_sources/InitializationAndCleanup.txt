
*******************************************************************************
Initialization and Cleanup
*******************************************************************************

Initialization
===========================================================================

Constructor Calls
-------------------------------------------------------------------------------

Automatic base-class constructor calls.

Calling the base-class constructor first, how to do it using super(), why you
should always call it first even if it's optional when to call it.

.. guideline: Be rigorous about calling base-class initializers as the
.. first step of your __init__() method. Call them using super() so
.. that modifications to the class hierarchy don't cause problems.

**__new__()** vs. **__init__()**
-------------------------------------------------------------------------------

Static Fields
-------------------------------------------------------------------------------

An excellent example of the subtleties of initialization is static fields
in classes.

::
	>>> class Foo(object):
	...   x = "a"
	...
	>>> Foo.x
	'a'
	>>> f = Foo()
	>>> f.x
	'a'
	>>> f2 = Foo()
	>>> f2.x
	'a'
	>>> f2.x = 'b'
	>>> f.x
	'a'
	>>> Foo.x = 'c'
	>>> f.x
	'c'
	>>> f2.x
	'b'
	>>> Foo.x = 'd'
	>>> f2.x
	'b'
	>>> f.x
	'd'
	>>> f3 = Foo()
	>>> f3.x
	'd'
	>>> Foo.x = 'e'
	>>> f3.x
	'e'
	>>> f2.x
	'b'

If you assign, you get a new one. If it's modifiable, then unless you
assign you are working on a singleton. So a typical pattern is::

       class Foo:
           something = None # Static: visible to all classes
	   def f(self, x):
	       if not self.something:
	       	   self.something = [] # New local version for this object
	       self.something.append(x)

This is not a serious example because you would naturally just
initialize ``something`` in ``Foo``\'s constructor.

Cleanup
===========================================================================

Cleanup happens to globals by setting them to ``None`` (what about locals?).
Does the act of setting them to None cause __del__ to be called, or is
__del__ called by Python before a global is set to None?

Consider the following::

    class Counter:
        Count = 0   # This represents the count of objects of this class
        def __init__(self, name):
            self.name = name
            print name, 'created'
            Counter.Count += 1
        def __del__(self):
            print self.name, 'deleted'
            Counter.Count -= 1
            if Counter.Count == 0:
                print 'Last Counter object deleted'
            else:
                print Counter.Count, 'Counter objects remaining'

    x = Counter("First")
    del x

Without the final del, you get an exception. Shouldn't the normal cleanup
process take care of this?

From the Python docs regarding **__del__**:

    Warning: Due to the precarious circumstances under which __del__()
    methods are invoked, exceptions that occur during their execution are
    ignored, and a warning is printed to sys.stderr instead. Also, when
    __del__() is invoked in response to a module being deleted (e.g., when
    execution of the program is done), *other globals referenced by the
    __del__() method may already have been deleted*. For this reason,
    __del__() methods should do the absolute minimum needed to maintain
    external invariants.

Without the explicit call to ``del``, ``__del__`` is only called at the end
of the program, Counter and/or Count may have already been GC-ed by the
time ``__del__`` is called (the order in which objects are collected is not
deterministic). The exception means that Counter has already been collectd.
You can't do anything particularly fancy with __del__.

There are two possible solutions here.

    1. Use an explicit finalizer method, such as ``close()`` for file
    objects.

    2. Use weak references.

Here's an example of weak references, using a WeakValueDictionary and the
trick of mapping id(self) to self::

    from weakref import WeakValueDictionary

    class Counter:
        _instances = WeakValueDictionary()
        @property
        def Count(self):
            return len(self._instances)

        def __init__(self, name):
            self.name = name
            self._instances[id(self)] = self
            print name, 'created'

        def __del__(self):
            print self.name, 'deleted'
            if self.Count == 0:
                print 'Last Counter object deleted'
            else:
                print self.Count, 'Counter objects remaining'

    x = Counter("First")

Now cleanup happens properly without the need for an explicit call to
``del``.

.. What about local variables?

Further Reading
===========================================================================

