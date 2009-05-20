.. index::
   Metaprogramming
   class decorators

********************************************************************************
Metaprogramming
********************************************************************************

..  Note:: This chapter is written using Python 2.6 syntax; it will be
    	   converted to Python 3 at a later date.

Objects are created by other objects: special objects called "classes"
that we can set up to spit out objects that are configured to our
liking. 

Classes are just objects, and they can be modified the same
way::

    >>> class Foo: pass
    ... 
    >>> Foo.field = 42
    >>> x = Foo()
    >>> x.field
    42
    >>> Foo.field2 = 99
    >>> x.field2
    99
    >>> Foo.method = lambda self: "Hi!"
    >>> x.method()
    'Hi!'

To modify a class, you perform operations on it like any other
object. You can add and subtract fields and methods, for example. The
difference is that any change you make to a class affects all the
objects of that class, even the ones that have already been instantiated.

What creates these special "class" objects? Other special objects,
called metaclasses.

The default metaclass is called ``type`` and in the vast majority of
cases it does the right thing. In some situations, however, you can
gain leverage by modifying the way that classes are produced --
typically by performing extra actions or injecting code. When this is
the case, you can use *metaclass programming* to modify the way that
some of your class objects are created.

It's worth re-emphasizing that in *the vast majority of cases, you
don't need metaclasses*, because it's a fascinating toy and the
temptation to use it everywhere can be overwhelming. Some of the
examples in this chapter will show both metaclass and non-metaclass
solutions to a problem, so you can see that there's usually another
(often simpler) approach.

Some of the functionality that was previously only available with
metaclasses is now available in a simpler form using class
decorators. It is still useful, however, to understand metaclasses,
and certain results can still be achieved only through metaclass
programming.

Basic Metaprogramming
================================================================================

So metaclasses create classes, and classes create instances. Normally
when we write a class, the default metaclass ``type`` is automatically
invoked to create that class, and we aren't even aware that it's happening. 

It's possible to explicitly code the metaclass' creation of a
class. ``type`` called with one argument produces the type information
of an existing class; ``type`` called with three arguments creates a
new class object. The arguments when invoking ``type`` are the name of the class,
a list of base classes, and a dictionary giving the namespace for the
class (all the fields and methods). So the equivalent of::

    class C: pass

is::

    C = type('C', (), {})

Classes are often referred to as "types," so this reads fairly
sensibly: you're calling a function that creates a new type based on
its arguments.

We can also add base classes, fields and methods::

    # Metaprogramming/MyList.py

    def howdy(self, you):
        print("Howdy, " + you)

    MyList = type('MyList', (list,), dict(x=42, howdy=howdy))

    ml = MyList()
    ml.append("Camembert")
    print(ml)
    print(ml.x)
    ml.howdy("John")

    print(ml.__class__.__class__)

    """ Output:
    ['Camembert']
    42
    Howdy, John
    """

Note that printing the class of the class produces the metaclass.

The ability to generate classes programmatically using ``type`` opens
up some interesting possibilities. Consider the GreenHouseLanguage.py
example in the Jython chapter -- all the subclasses in that case were
written using repetetive code. We can automate the generation of the
subclasses using ``type``::

    # Metaprogramming/GreenHouse.py

    class Event(object):
        events = [] # static

        def __init__(self, action, time):
            self.action = action
            self.time = time
            Event.events.append(self)

        def __cmp__ (self, other):
            "So sort() will compare only on time."
            return cmp(self.time, other.time)

        def run(self):
            print("%.2f: %s" % (self.time, self.action))

        @staticmethod
        def run_events():
            Event.events.sort();
            for e in Event.events:
                e.run()

    def create_mc(description):
        "Create subclass using the 'type' metaclass"
        class_name = "".join(x.capitalize() for x in description.split())
        def __init__(self, time):
            Event.__init__(self, description + " [mc]", time)
        globals()[class_name] = \
            type(class_name, (Event,), dict(__init__ = __init__))

    def create_exec(description):
        "Create subclass by exec-ing a string"
        class_name = "".join(x.capitalize() for x in description.split())
        klass = """
    class %s(Event):
        def __init__(self, time):
            Event.__init__(self, "%s [exec]", time)
    """ % (class_name, description)
        exec klass in globals()

    if __name__ == "__main__":
        descriptions = ["Light on", "Light off", "Water on", "Water off", 
                        "Thermostat night", "Thermostat day", "Ring bell"]
        initializations = "ThermostatNight(5.00); LightOff(2.00); \
            WaterOn(3.30); WaterOff(4.45); LightOn(1.00); \
            RingBell(7.00); ThermostatDay(6.00)"
        [create_mc(dsc) for dsc in descriptions]
        exec initializations in globals()
        [create_exec(dsc) for dsc in descriptions]
        exec initializations in globals()
        Event.run_events()

    """ Output:
    1.00: Light on [mc]
    1.00: Light on [exec]
    2.00: Light off [mc]
    2.00: Light off [exec]
    3.30: Water on [mc]
    3.30: Water on [exec]
    4.45: Water off [mc]
    4.45: Water off [exec]
    5.00: Thermostat night [mc]
    5.00: Thermostat night [exec]
    6.00: Thermostat day [mc]
    6.00: Thermostat day [exec]
    7.00: Ring bell [mc]
    7.00: Ring bell [exec]
    """

The ``Event`` base class is the same. The classes are created
automatically using the ``create_mc()`` function, which takes its
``description`` argument and generates a class name from it. Then it
defines an ``__init__()`` method, which it puts into the namespace
dictionary for the ``type`` call, producing a new subclass of
``Event``. Note that the resulting class must be inserted into the
global namespace, otherwise it will not be seen.

This approach works fine, but then consider the subsequent
``create_exec()`` function, which accomplishes the same thing by
calling ``exec`` on a string defining the class. This will be much
easier to understand by the vast majority of the people reading your
code: those who do not understand metaclasses.

The Metaclass Hook
================================================================================

So far, we've only used the ``type`` metaclass directly. Metaclass
programming involves hooking our own operations into the creation of
class objects. This is accomplished by:

      1. Writing a subclass of the metaclass ``type``.
      2. Inserting the new metaclass into the class creation process
         using the *metaclass hook*.

In Python 2.x, the metaclass hook is a static field in the class
called ``__metaclass__``. In the ordinary case, this is not assigned
so Python just uses ``type`` to create the class. But if you define
``__metaclass__`` to point to a callable, Python will call
``__metaclass__()`` after the initial creation of the class object,
passing in the class object, the class name, the list of base classes
and the namespace dictionary.

Python 2.x also allows you to assign to the global ``__metaclass__``
hook, which will be used if there is not a class-local
``__metaclass__`` hook (is there an equivalent in Python 3?).

Thus, the basic process of metaclass programming looks like this::

    # Metaprogramming/SimpleMeta1.py
    # Two-step metaclass creation in Python 2.x

    class SimpleMeta1(type):
        def __init__(cls, name, bases, nmspc):
            super(SimpleMeta1, cls).__init__(name, bases, nmspc)
            cls.uses_metaclass = lambda self : "Yes!"

    class Simple1(object):
        __metaclass__ = SimpleMeta1
        def foo(self): pass
        @staticmethod
        def bar(): pass

    simple = Simple1()
    print([m for m in dir(simple) if not m.startswith('__')])
    # A new method has been injected by the metaclass:
    print simple.uses_metaclass()

    """ Output:
    ['bar', 'foo', 'uses_metaclass']
    Yes!
    """

By convention, when defining metaclasses ``cls`` is used rather than
``self`` as the first argument to all methods except ``__new__()``
(which uses ``mcl``, for reasons explained later). ``cls``
is the class object that is being modified.

Note that the practice of calling the base-class constructor first (via
``super()``) in the derived-class constructor should be followed with
metaclasses as well.

``__metaclass__`` only needs to be callable, so in Python
2.x it's possible to define ``__metaclass__`` inline::

    # Metaprogramming/SimpleMeta2.py
    # Combining the steps for metaclass creation in Python 2.x

    class Simple2(object):
        class __metaclass__(type):
            def __init__(cls, name, bases, nmspc):
                # This won't work:
                # super(__metaclass__, cls).__init__(name, bases, nmspc)
                # Less-flexible specific call:
                type.__init__(cls, name, bases, nmspc)
                cls.uses_metaclass = lambda self : "Yes!"

    class Simple3(Simple2): pass
    simple = Simple3()
    print simple.uses_metaclass()

    """ Output:
    Yes!
    """

The compiler won't accept the ``super()`` call because it says
``__metaclass__`` hasn't been defined, forcing us to use the specific
call to ``type.__init__()``. 

Because it only needs to be callable, it's even possible to define
``__metaclass__`` as a function::

    # Metaprogramming/SimpleMeta3.py
    # A function for __metaclass__ in Python 2.x

    class Simple4(object):
        def __metaclass__(name, bases, nmspc):
            cls = type(name, bases, nmspc)
            cls.uses_metaclass = lambda self : "Yes!"
            return cls

    simple = Simple4()
    print simple.uses_metaclass()

    """ Output:
    Yes!
    """

As you'll see, Python 3 doesn't allow the syntax of these last two
examples. Even so, the above example makes it quite clear what's
happening: the class object is created, then modified, then returned.

.. Note:: Or does it allow that syntax?


The Metaclass Hook in Python 3
----------------------------------------------------------------------

Python 3 changes the metaclass hook. It doesn't disallow the
``__metaclass__`` field, but it ignores it. Instead, you use a keyword
argument in the base-class list::

    class Simple1(object, metaclass = SimpleMeta1):
	...

This means that none of the (clever) alternative ways of defining
``__metaclass__`` directly as a class or function are available in
Python 3 [[check this]]. All metaclasses must be defined as separate
classes. This is probably just as well, as it makes metaclass programs
more consistent and thus easier to read and understand.

.. Possible example: simplification of XML creation via operator
   overloading.

Example: Self-Registration of Subclasses
================================================================================

It is sometimes convienient to use inheritance as an organizing
mechanism -- each sublclass becomes an element of a group that you
work on. For example, in **CodeManager.py** in the **Comprehensions**
chapter, the subclasses of **Language** were all the languages that
needed to be processed. Each **Language** subclass described specific
processing traits for that language.

To solve this problem, consider a system that automatically keeps a
list of all of its "leaf" subclasses (only the classes that have no
inheritors). This way we can easily enumerate through all the
subtypes::

    # Metaprogramming/RegisterLeafClasses.py

    class RegisterLeafClasses(type):
        def __init__(cls, name, bases, nmspc):
            super(RegisterLeafClasses, cls).__init__(name, bases, nmspc)
            if not hasattr(cls, 'registry'):
                cls.registry = set()
            cls.registry.add(cls)
            cls.registry -= set(bases) # Remove base classes
        # Metamethods, called on class objects:
        def __iter__(cls):
            return iter(cls.registry)
        def __str__(cls):
            if cls in cls.registry:
                return cls.__name__
            return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])

    class Color(object):
        __metaclass__ = RegisterLeafClasses

    class Blue(Color): pass
    class Red(Color): pass
    class Green(Color): pass
    class Yellow(Color): pass
    print(Color)
    class PhthaloBlue(Blue): pass
    class CeruleanBlue(Blue): pass
    print(Color)
    for c in Color: # Iterate over subclasses
        print(c)

    class Shape(object):
        __metaclass__ = RegisterLeafClasses

    class Round(Shape): pass
    class Square(Shape): pass
    class Triangular(Shape): pass
    class Boxy(Shape): pass
    print(Shape)
    class Circle(Round): pass
    class Ellipse(Round): pass
    print(Shape)

    """ Output:
    Color: Red, Blue, Green, Yellow
    Color: Red, CeruleanBlue, Green, PhthaloBlue, Yellow
    Red
    CeruleanBlue
    Green
    PhthaloBlue
    Yellow
    Shape: Square, Round, Boxy, Triangular
    Shape: Square, Ellipse, Circle, Boxy, Triangular
    """

Two separate tests are used to show that the registries are
independent of each other. Each test shows what happens when another
level of leaf classes are added -- the former leaf becomes a base
class, and so is removed from the registry.

This also introduces *metamethods*, which are defined in the metaclass
so that they become methods of the class. That is, you call them on
the class rather than object instances, and their first argument is
the class object rather than ``self``.

Using Class Decorators
--------------------------------------------------------------------------------

Using the **inspect** module
--------------------------------------------------------------------------------

(As in the Comprehensions chapter)

Example: Making a Class "Final"
================================================================================

It is sometimes convenient to prevent a class from being inherited::

    # Metaprogramming/Final.py
    # Emulating Java's 'final'

    class final(type):
        def __init__(cls, name, bases, namespace):
            super(final, cls).__init__(name, bases, namespace)
            for klass in bases:
                if isinstance(klass, final):
                    raise TypeError(str(klass.__name__) + " is final")

    class A(object):
        pass

    class B(A):
        __metaclass__= final

    print B.__bases__
    print isinstance(B, final)

    # Produces compile-time error:
    class C(B):
        pass

    """ Output:
    (<class '__main__.A'>,)
    True
    ...
    TypeError: B is final
    """

During class object creation, we check to see if any of the bases are
derived from ``final``. Notice that using a metaclass makes the new
type an instance of that metaclass, even though the metaclass doesn't
show up in the base-class list.

Because this process of checking for finality must be installed to
happen as the subclasses are created, rather than afterwards as
performed by class decorators, it appears that this is an example of
something that requires metaclasses and can't be accomplished with
class decorators.


Using ``__init__`` vs. ``__new__`` in Metaclasses
================================================================================

It can be confusing when you see metaclass examples that appear to
arbitrarily use ``__new__`` or ``__init__`` -- why choose one over the other?

``__new__`` is called for the creation of a new class, while
``__init__`` is called after the class is created, to perform
additional initialization before the class is handed to the caller::

    # Metaprogramming/NewVSInit.py
    from pprint import pprint

    class Tag1: pass
    class Tag2: pass
    class Tag3:
        def tag3_method(self): pass

    class MetaBase(type):
        def __new__(mcl, name, bases, nmspc):
            print('MetaBase.__new__\n')
            return super(MetaBase, mcl).__new__(mcl, name, bases, nmspc)

        def __init__(cls, name, bases, nmspc):
            print('MetaBase.__init__\n')
            super(MetaBase, cls).__init__(name, bases, nmspc)

    class MetaNewVSInit(MetaBase):
        def __new__(mcl, name, bases, nmspc):
            # First argument is the metaclass ``MetaNewVSInit``
            print('MetaNewVSInit.__new__')
            for x in (mcl, name, bases, nmspc): pprint(x)
            print('')
            # These all work because the class hasn't been created yet:
            if 'foo' in nmspc: nmspc.pop('foo')
            name += '_x'
            bases += (Tag1,)
            nmspc['baz'] = 42
            return super(MetaNewVSInit, mcl).__new__(mcl, name, bases, nmspc)

        def __init__(cls, name, bases, nmspc):
            # First argument is the class being initialized
            print('MetaNewVSInit.__init__')
            for x in (cls, name, bases, nmspc): pprint(x)
            print('')
            if 'bar' in nmspc: nmspc.pop('bar') # No effect
            name += '_y' # No effect
            bases += (Tag2,) # No effect
            nmspc['pi'] = 3.14159 # No effect
            super(MetaNewVSInit, cls).__init__(name, bases, nmspc)
            # These do work because they operate on the class object:
            cls.__name__ += '_z'
            cls.__bases__ += (Tag3,)
            cls.e = 2.718

    class Test(object):
        __metaclass__ = MetaNewVSInit
        def __init__(self):
            print('Test.__init__')
        def foo(self): print('foo still here')
        def bar(self): print('bar still here')

    t = Test()
    print('class name: ' + Test.__name__)
    print('base classes: ', [c.__name__ for c in Test.__bases__])
    print([m for m in dir(t) if not m.startswith("__")])
    t.bar()
    print(t.e)

    """ Output:
    MetaNewVSInit.__new__
    <class '__main__.MetaNewVSInit'>
    'Test'
    (<type 'object'>,)
    {'__init__': <function __init__ at 0x7ecf0>,
     '__metaclass__': <class '__main__.MetaNewVSInit'>,
     '__module__': '__main__',
     'bar': <function bar at 0x7ed70>,
     'foo': <function foo at 0x7ed30>}

    MetaBase.__new__

    MetaNewVSInit.__init__
    <class '__main__.Test_x'>
    'Test'
    (<type 'object'>,)
    {'__init__': <function __init__ at 0x7ecf0>,
     '__metaclass__': <class '__main__.MetaNewVSInit'>,
     '__module__': '__main__',
     'bar': <function bar at 0x7ed70>,
     'baz': 42}

    MetaBase.__init__

    Test.__init__
    class name: Test_x_z
    ('base classes: ', ['object', 'Tag1', 'Tag3'])
    ['bar', 'baz', 'e', 'tag3_method']
    bar still here
    2.718
    """


The primary difference is that when overriding ``__new__()`` you can change
things like the 'name', 'bases' and 'namespace' arguments before you
call the super constructor and it will have an effect, but doing the
same thing in ``__init__()`` you won't get any results from the constructor
call.

One special case in ``__new__()`` is that you can
manipulate things like ``__slots__``, but in ``__init__()`` you can't.

Note that, since the base-class version of ``__init__()`` doesn't make any
modifications, it makes sense to call it first, then perform any
additional operations. In C++ and Java, the base-class constructor
*must* be called as the first operation in a derived-class
constructor, which makes sense because derived-class constructions can
then build upon base-class foundations.

In many cases, the choice of ``__new__()`` vs ``__init__()`` is a style issue and
doesn't matter, but because ``__new__()`` can do everything and ``__init__()`` is
slightly more limited, some people just start using ``__new__()`` and stick with
it. This use can be confusing -- I tend to hunt for the reason that
``__init__()`` has been chosen, and if I can't find it wonder whether
the author knew what they were doing. I prefer to only use ``__new__()``
when it has meaning -- when you must in order to change things that
only ``__new__()`` can change. 

Class Methods and Metamethods
================================================================================

A metamethod can be called from either the metaclass or from the
class, but not from an instance. A classmethod can be called from
either a class or its instances, but is not part of the metaclass.

(Is a similar relationship true with attributes, or is it different?)

Intercepting Class Creation
--------------------------------------------------------------------------------

This example implements *Singleton* using metaclasses, by overriding the
``__call__()`` metamethod, which is invoked when a new instance is
created::

    # Metaprogramming/Singleton.py

    class Singleton(type):
        instance = None
        def __call__(cls, *args, **kw):
            if not cls.instance:
                 cls.instance = super(Singleton, cls).__call__(*args, **kw)
            return cls.instance

    class ASingleton(object):
        __metaclass__ = Singleton

    a = ASingleton()
    b = ASingleton()
    assert a is b
    print(a.__class__.__name__, b.__class__.__name__)

    class BSingleton(object):
        __metaclass__ = Singleton

    c = BSingleton()
    d = BSingleton()
    assert c is d
    print(c.__class__.__name__, d.__class__.__name__)
    assert c is not a

    """ Output:
    ('ASingleton', 'ASingleton')
    ('BSingleton', 'BSingleton')
    """

By overriding ``__call__()`` in the metaclass, the creation of
instances are intercepted. Instance creation is bypassed if one
already exists.

Note the dependence upon the behavior of static class fields. When
``cls.instance`` is first read, it gets the static value of
``instance`` from the metaclass, which is ``None``. However, when the
assignment is made, Python creates a local version for the particular
class, and the next time ``cls.instance`` is read, it sees that local
version. Because of this behavior, each class ends up with its own
class-specific ``instance`` field (thus ``instance`` is not somehow
being "inherited" from the metaclass).

A Class Decorator Singleton
--------------------------------------------------------------------------------

::

    # Metaprogramming/SingletonDecorator.py

    def singleton(klass):
        "Simple replacement of object creation operation"
        def getinstance(*args, **kw):
            if not hasattr(klass, 'instance'):
                klass.instance = klass(*args, **kw)
            return klass.instance
        return getinstance

    def singleton(klass):
        """
        More powerful approach: Change the behavior
        of the instances AND the class object.
        """
        class Decorated(klass):
            def __init__(self, *args, **kwargs):
                if hasattr(klass, '__init__'):
                    klass.__init__(self, *args, **kwargs)
            def __repr__(self) : return klass.__name__ + " obj"
            __str__ = __repr__
        Decorated.__name__ = klass.__name__
        class ClassObject:
            def __init__(cls):
                cls.instance = None
            def __repr__(cls): 
                return klass.__name__
            __str__ = __repr__
            def __call__(cls, *args, **kwargs):
                print str(cls) + " __call__ "
                if not cls.instance:
                    cls.instance = Decorated(*args, **kwargs)
                return cls.instance
        return ClassObject()

    @singleton
    class ASingleton: pass

    a = ASingleton()
    b = ASingleton()
    print(a, b)
    print a.__class__.__name__
    print ASingleton
    assert a is b

    @singleton
    class BSingleton:
        def __init__(self, x):
            self.x = x

    c = BSingleton(11)
    d = BSingleton(22)
    assert c is d
    assert c is not a

    """ Output:
    ASingleton __call__ 
    ASingleton __call__ 
    (ASingleton obj, ASingleton obj)
    ASingleton
    ASingleton
    BSingleton __call__ 
    BSingleton __call__ 
    """


The ``__prepare__()`` Metamethod
================================================================================

One of the things you *can't* do with class decorators is to replace
the default dictionary. In Python 3 this is enabled with the
``__prepare__()`` metamethod::

    @classmethod
    def __prepare__(mcl, name, bases):
        return odict()

For an example of using both ``__prepare__()`` and ``__slots__`` in
metaclasses, see `Michele Simionato's article <http://www.artima.com/weblogs/viewpost.jsp?thread=236260>`_.

Module-level ``__metaclass__`` Assignment
================================================================================

(Does this work in Python 3? If not is there an alternative?)

Metaclass Conflicts
================================================================================

Note that the ``metaclass`` argument is singular -- you can't attach
more than one metaclass to a class. However, through multiple
inheritance you can *accidentally* end up with more than one
metaclass, and this produces a conflict which must be resolved.

http://code.activestate.com/recipes/204197/

Further Reading
================================================================================

    Excellent step-by-step introduction to metaclasses:
        http://cleverdevil.org/computing/78/

    Metaclass intro and comparison of syntax between Python 2.x and 3.x:
        http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/

    David Mertz's metaclass primer:
        http://www.onlamp.com/pub/a/python/2003/04/17/metaclasses.html

    Three-part in-depth coverage of metaclasses on IBM Developer Works. Quite useful and authoritative:
      - http://www.ibm.com/developerworks/linux/library/l-pymeta.html
      - http://www.ibm.com/developerworks/linux/library/l-pymeta2/
      - http://www.ibm.com/developerworks/linux/library/l-pymeta3.html

    Michele Simionato's articles on Artima, with special emphasis on the difference between Python 2.x and 3.x metaclasses:
      - http://www.artima.com/weblogs/viewpost.jsp?thread=236234
      - http://www.artima.com/weblogs/viewpost.jsp?thread=236260

    Once you understand the foundations, you can find lots of examples
    by searching for "metaclass" within the Python Cookbook:
    http://code.activestate.com/recipes/langs/python/

    The printed version of the Python Cookbook has far fewer examples
    than the online version, but the print version has been filtered
    and edited and so tends to be more authoritative.

    Ian Bicking writes about metaclasses:
      - http://blog.ianbicking.org/a-conservative-metaclass.html
      - http://blog.ianbicking.org/metaclass-fun.html
      - http://blog.ianbicking.org/A-Declarative-Syntax-Extension.html
      - http://blog.ianbicking.org/self-take-two.html

    Lots of good information about classes, types, metaclasses, etc.,
    including historical stuff in the Python 2.2 docs (is this
    duplicated in later versions of the docs):
      - http://www.python.org/download/releases/2.2/descrintro/

    For more advanced study, the book `Putting Metaclasses to Work
    <http://www.pearsonhighered.com/educator/academic/product/0,,0201433052,00%2ben-USS_01DBC.html>`_.

.. Examples: http://www.python.org/doc/essays/metaclasses/
.. http://www.python.org/download/releases/2.2/descrintro/#metaclasses
.. http://www.python.org/download/releases/2.2/descrintro/#__new__
.. http://jurjanpaul.blogspot.com/2009/01/small-metaclass-for-strongly-typed.html
.. Tracking instances

.. Simple example: a @main decorator so you don't have to say if __name__ == '__main__':

.. @precondition and @postcondition (possibly also @invariant?)

.. Clever uses (and bad examples) for metaclasses:
.. http://blog.tplus1.com/index.php/2009/04/20/i-submitted-my-proposal-for-pyohio-2009/
.. Note the Python Magazine article of the same name -- find that.
