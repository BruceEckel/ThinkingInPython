.. index::
   Metaclasses
   class decorators

********************************************************************************
Metaclasses
********************************************************************************

Objects are created by other objects: special objects called "classes"
that we can set up to spit out objects that are configured to our
liking. What creates these special "class" objects, though? Class
objects are created by other special objects, called metaclasses.

The default metaclass is called ``type`` and in the vast majority of
cases it does the right thing. In some situations, however, you can
gain leverage by modifying the way that classes are produced --
typically by performing extra actions or injecting code. When this is
the case, you can use *metaclass* programming to modify the way that
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

Basic Metaclasses
================================================================================

So metaclasses create classes, and classes create instances. Normally
when we write a class, the default metaclass ``type`` is automatically
invoked to create that class, and we aren't even aware that it's happening. 

It's possible to explicitly code the metaclass' creation of the
class. The arguments when invoking ``type`` are the name of the class,
a list of base classes, and a dictionary giving the namespace for the
class (all the fields and methods). So the equivalent of::

    class C: pass

is::

    C = type('C', (), {})

Classes are often referred to as "types," so this reads fairly
sensibly: you're calling a function that creates a new type based on
its arguments.

The ability to generate classes programmatically using ``type`` opens
up some interesting possibilities. Consider the GreenHouseLanguage.py
example in the Jython chapter -- all the subclasses in that case were
written using repetetive code. We can automate the generation of the
subclasses using ``type``::

    # Metaclasses/GreenHouse.py

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

The ``Event`` base class is the same. The classes are created
automatically using the ``create_mc()`` function, which takes its
``description`` argument and generates a class name from it. Then it
defines an ``__init__()`` method, which it puts into the namespace
dictionary for the ``type`` call, producing a new subclass of
``Event``. Note that the resulting class must be inserted into the
global namespace, otherwise it will not be seen.

This approach works fine, but then consider the following
``create_exec()`` function, which accomplishes the same thing by
calling ``exec`` on a string defining the class. This will be much
easier to understand by the vast majority of the people reading your
code -- those who do not understand metaclasses.

Python 3 metaclasses (and does the Python 2 syntax still work in 3?)

example: Autogeneration of the "event" sublclasses in the greenhouse
example using type(), and metaclass programming. Alternative, show
class decorator if possible. Or even exec?

.. Possible example: simplification of XML creation via operator
   overloading.

>>> C = type('C', (object,), {})
>>> c = C()
>>> C


Example: Self-Registration of Subclasses
================================================================================

It is sometimes convienient to use inheritance as an organizing
mechanism -- each sublclass become an element of a group that you work
on. For example, in the **CodeManager.py** example in the
**Comprehensions** chapter, the subclasses of **Language** were all
the languages that needed to be processed.

To achieve this, you need to somehow keep a list of all the subclasses
that are inherited from your base class, so you can iterate through
and perform processing for each one. One way of keeping track
automatially is to use metaclasses.

untested, will require rewriting::

    class Base(object):
        registry = []
        class __metaclass__(type):
            def __init__(cls, name, bases, dict):
		cls.registry.append(cls)
	def __new__(cls, a):
	    if cls != Base:
		return object.__new__(cls, a)
	    for subcls in cls.registry:
		if subcls == Base:
		    continue
		try:
		    return subcls(a)
		except ValueError:
		    pass
	    raise ValueError("No subclass found")
	def __init__(self, input):
	    super(Base, self).__init__(input)
	    self.data = input

    class Derived1(Base):
	def __init__(self, s):
	    s = int(s)
	    super(Derived1, self).__init__(s)
	    self.s = s

    class Derived2(Base):
	def __init__(self, s):
	    if ',' not in s:
		raise ValueError("Not a list")
	    super(Derived2, self).__init__(s)
	    self.s = s.split(',')

    class Derived3(Base):
	pass 

Here's another version which seems a lot simpler::

    class LeafClassesMeta(type):
        """
        A metaclass for classes that keeps track of all of them that
        aren't base classes.
        """

        registry = set()

        def __init__(cls, name, bases, attrs):
            cls.registry.add(cls)
            # remove any base classes
            cls.registry -= set(bases)

But it also seems like you can do it more simply with the denser syntax::

    class Base(object):
        """
        A metaclass for classes that keeps track of all of them that
        aren't base classes.
        """

        registry = set()

        def __metaclass__(name, bases, attrs):
            cls.registry.add(cls)
            # remove any base classes
            cls.registry -= set(bases)

Apparently, ``__metaclass__`` just needs to be callable, so it doesn't
matter whether it's a class with an __init__ or a function. Of course
this won't work in Python 3 where the ``__metaclass__`` field is ignored.

Using Class Decorators
--------------------------------------------------------------------------------

Using the **inspect** module
--------------------------------------------------------------------------------

(As in the Comprehensions chapter)


Class Methods and Metamethods
================================================================================

A metamethod can be called from either the metaclass or from the
class, but not from an instance. A classmethod can be called from
either a class or its instances, but is not part of the metaclass.

(Is a similar relationship true with attributes, or is it different?)

Further Reading
================================================================================

    http://cleverdevil.org/computing/78/ -- an excellent step-by-step
    introduction to metaclasses.
        
    http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/ --
    Metaclass intro and comparison of syntax between Python 2.x and
    3.x.

    http://www.ibm.com/developerworks/linux/library/l-pymeta.html
    http://www.ibm.com/developerworks/linux/library/l-pymeta2/
    http://www.ibm.com/developerworks/linux/library/l-pymeta3.html
    Three-part in-depth coverage of metaclasses on IBM Developer
    Works. Quite useful and authoritative.

    Michele Simionato's articles on Artima, with special emphasis on
    the difference between Python 2.x and 3.x metaclasses:
    http://www.artima.com/weblogs/viewpost.jsp?thread=236234
    http://www.artima.com/weblogs/viewpost.jsp?thread=236260

    For more advanced study, the book `Putting Metaclasses to Work
    <http://www.pearsonhighered.com/educator/academic/product/0,,0201433052,00%2ben-USS_01DBC.html>`_
    .

