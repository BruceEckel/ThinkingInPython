.. index::
   decorator: Python decorators
   @: Python decorators

********************************************************************************
Decorators
********************************************************************************

.. note:: This chapter is a work in progress; it's probably better if you don't
          begin making changes until I've finished the original version, which
          is being posted as a series on my weblog.

This amazing feature appeared in the language almost apologetically and with
concern that it might not be that useful.

I predict that in time it will be seen as one of the more powerful features in
the language. The problem is that all the introductions to decorators that I
have seen have been rather confusing, so I will try to rectify that here.

Decorators vs. the Decorator Pattern
=============================================

First, you need to understand that the word "decorator" was used with some
trepidation in Python, because there was concern that it would be completely
confused with the *Decorator* pattern from the `Design Patterns book
<http://www.amazon.com/gp/product/0201633612/ref=ase_bruceeckelA/>`_. At one
point other terms were considered for the feature, but "decorator" seems to be
the one that sticks.

Indeed, you can use Python decorators to implement the *Decorator* pattern, but
that's an extremely limited use of it. Python decorators, I think, are best
equated to macros.

History of Macros
==========================

The macro has a long history, but most people will probably have had experience
with C preprocessor macros. The problems with C macros were (1) they were in a
different language (not C) and (2) the behavior was sometimes bizarre, and often
inconsistent with the behavior of the rest of C.

Both Java and C# have added *annotations*, which allow you to do some things to
elements of the language. Both of these have the problems that (1) to do what
you want, you sometimes have to jump through some enormous and untenable hoops,
which follows from (2) these annotation features have their hands tied by the
bondage-and-discipline (or as `Martin Fowler gently puts it: "Directing"
<http://martinfowler.com/bliki/SoftwareDevelopmentAttitude.html>`_) nature of
those languages.

In a slightly different vein, many C++ programmers (myself included) have noted
the generative abilities of C++ templates and have used that feature in a macro-
like fashion.

Many other languages have incorporated macros, but without knowing much about it
I will go out on a limb and say that Python decorators are similar to Lisp
macros in power and possibility.

The Goal of Macros
============================

I think it's safe to say that the goal of macros in a language is to provide a
way to modify elements of the language. That's what decorators do in Python --
they modify functions, and in the case of *class decorators*, entire classes.
This is why they usually provide a simpler alternative to metaclasses.

The major failings of most language's self-modification approaches are that they
are too restrictive and that they require a different language (I'm going to say
that Java annotations with all the hoops you must jump through to produce an
interesting annotation comprises a "different language").

Python falls into Fowler's category of "enabling" languages, so if you want to
do modifications, why create a different or restricted language? Why not just
use Python itself? And that's what Python decorators do.

What Can You Do With Decorators?
===================================

Decorators allow you to inject or modify code in functions or classes. Sounds a
bit like *Aspect-Oriented Programming* (AOP) in Java, doesn't it? Except that
it's both much simpler and (as a result) much more powerful. For example,
suppose you'd like to do something at the entry and exit points of a function
(such as perform some kind of security, tracing, locking, etc. -- all the
standard arguments for AOP). With decorators, it looks like this::

    @entryExit
    def func1():
        print("inside func1()")

    @entryExit
    def func2():
        print("inside func2()")

The ``@`` indicates the application of the decorator.

Function Decorators
==============================

A function decorator is applied to a function definition by placing it on the
line before that function definition begins. For example::

    @myDecorator
    def aFunction():
        print("inside aFunction")

When the compiler passes over this code, ``aFunction()`` is compiled and the
resulting function object is passed to the ``myDecorator`` code, which does
something to produce a function-like object that is then substituted for the
original ``aFunction()``.

What does the ``myDecorator`` code look like? Well, most introductory examples
show this as a function, but I've found that it's easier to start understanding
decorators by using classes as decoration mechanisms instead of functions. In
addition, it's more powerful.

The only constraint upon the object returned by the decorator is that it can be
used as a function -- which basically means it must be callable. Thus, any
classes we use as decorators must implement ``__call__``.

What should the decorator do? Well, it can do anything but usually you expect
the original function code to be used at some point. This is not required,
however::

    class myDecorator(object):

        def __init__(self, f):
            print("inside myDecorator.__init__()")
            f() # Prove that function definition has completed

        def __call__(self):
            print("inside myDecorator.__call__()")

    @myDecorator
    def aFunction():
        print("inside aFunction()")

    print("Finished decorating aFunction()")

    aFunction()


When you run this code, you see::

    inside myDecorator.__init__()
    inside aFunction()
    Finished decorating aFunction()
    inside myDecorator.__call__()

Notice that the constructor for ``myDecorator`` is executed at the point of
decoration of the function. Since we can call ``f()`` inside ``__init__()``, it
shows that the creation of ``f()`` is complete before the decorator is called.
Note also that the decorator constructor receives the function object being
decorated. Typically, you'll capture the function object in the constructor and
later use it in the ``__call__()`` method (the fact that decoration and calling
are two clear phases when using classes is why I argue that it's easier and more
powerful this way).

When ``aFunction()`` is called after it has been decorated, we get completely
different behavior; the ``myDecorator.__call__()`` method is called instead of
the original code. That's because the act of decoration *replaces* the original
function object with the result of the decoration -- in our case, the
``myDecorator`` object replaces ``aFunction``. Indeed, before decorators were
added you had to do something much less elegant to achieve the same thing::

    def foo(): pass
    foo = staticmethod(foo)

With the addition of the ``@`` decoration operator, you now get the same result
by saying::

    @staticmethod
    def foo(): pass

This is the reason why people argued against decorators, because the ``@`` is
just a little syntax sugar meaning "pass a function object through another
function and assign the result to the original function."

The reason I think decorators will have such a big impact is because this little
bit of syntax sugar changes the way you think about programming. Indeed, it
brings the idea of "applying code to other code" (i.e.: macros) into mainstream
thinking by formalizing it as a language construct.

Slightly More Useful
========================

Now let's go back and implement the first example. Here, we'll do the more
typical thing and actually use the code in the decorated functions::

    class entryExit(object):

        def __init__(self, f):
            self.f = f

        def __call__(self):
            print("Entering", self.f.__name__)
            self.f()
            print("Exited", self.f.__name__)

    @entryExit
    def func1():
        print("inside func1()")

    @entryExit
    def func2():
        print("inside func2()")

    func1()
    func2()

The output is::

    Entering func1
    inside func1()
    Exited func1
    Entering func2
    inside func2()
    Exited func2

You can see that the decorated functions now have the "Entering" and "Exited"
trace statements around the call.

The constructor stores the argument, which is the function object. In the call,
we use the ``__name__`` attribute of the function to display that function's
name, then call the function itself.

Using Functions as Decorators
=====================================

The only constraint on the result of a decorator is that it be callable, so it
can properly replace the decorated function. In the above examples, I've
replaced the original function with an object of a class that has a
``__call__()`` method. But a function object is also callable, so we can rewrite
the previous example using a function instead of a class, like this::

    def entryExit(f):
        def new_f():
            print("Entering", f.__name__)
            f()
            print("Exited", f.__name__)
        return new_f

    @entryExit
    def func1():
        print("inside func1()")

    @entryExit
    def func2():
        print("inside func2()")

    func1()
    func2()
    print(func1.__name__)

``new_f()`` is defined within the body of ``entryExit()``, so it is created and
returned when ``entryExit()`` is called. Note that ``new_f()`` is a *closure*,
because it captures the actual value of ``f``.

Once ``new_f()`` has been defined, it is returned from ``entryExit()`` so that
the decorator mechanism can assign the result as the decorated function.

The output of the line ``print(func1.__name__)`` is ``new_f``, because the
``new_f`` function has been substituted for the original function during
decoration. If this is a problem you can change the name of the decorator
function before you return it::

    def entryExit(f):
        def new_f():
            print("Entering", f.__name__)
            f()
            print("Exited", f.__name__)
        new_f.__name__ = f.__name__
        return new_f

The information you can dynamically get about functions, and the modifications
you can make to those functions, are quite powerful in Python.

Review: Decorators without Arguments
=========================================

If we create a decorator without arguments, the function to be decorated is
passed to the constructor, and the ``__call__()`` method is called whenever the
decorated function is invoked::

    class decoratorWithoutArguments(object):

        def __init__(self, f):
            """
            If there are no decorator arguments, the function
            to be decorated is passed to the constructor.
            """
            print("Inside __init__()")
            self.f = f

        def __call__(self, *args):
            """
            The __call__ method is not called until the
            decorated function is called.
            """
            print("Inside __call__()")
            self.f(*args)
            print("After self.f(*args)")

    @decoratorWithoutArguments
    def sayHello(a1, a2, a3, a4):
        print('sayHello arguments:', a1, a2, a3, a4)

    print("After decoration")

    print("Preparing to call sayHello()")
    sayHello("say", "hello", "argument", "list")
    print("After first sayHello() call")
    sayHello("a", "different", "set of", "arguments")
    print("After second sayHello() call")

Any arguments for the decorated function are just passed to ``__call__()``. The
output is::

    Inside __init__()
    After decoration
    Preparing to call sayHello()
    Inside __call__()
    sayHello arguments: say hello argument list
    After self.f(*args)
    After first sayHello() call
    Inside __call__()
    sayHello arguments: a different set of arguments
    After self.f(*args)
    After second sayHello() call

Notice that ``__init__()`` is the only method called to perform decoration, and
``__call__()`` is called every time you call the decorated ``sayHello()``.


Decorators with Arguments
====================================

The decorator mechanism behaves quite differently when you pass arguments to the
decorator.

Let's modify the above example to see what happens when we add arguments to the
decorator::

    class decoratorWithArguments(object):

        def __init__(self, arg1, arg2, arg3):
            """
            If there are decorator arguments, the function
            to be decorated is not passed to the constructor!
            """
            print("Inside __init__()")
            self.arg1 = arg1
            self.arg2 = arg2
            self.arg3 = arg3

        def __call__(self, f):
            """
            If there are decorator arguments, __call__() is only called
            once, as part of the decoration process! You can only give
            it a single argument, which is the function object.
            """
            print("Inside __call__()")
            def wrapped_f(*args):
                print("Inside wrapped_f()")
                print("Decorator arguments:", self.arg1, self.arg2, self.arg3)
                f(*args)
                print("After f(*args)")
            return wrapped_f

    @decoratorWithArguments("hello", "world", 42)
    def sayHello(a1, a2, a3, a4):
        print('sayHello arguments:', a1, a2, a3, a4)

    print("After decoration")

    print("Preparing to call sayHello()")
    sayHello("say", "hello", "argument", "list")
    print("after first sayHello() call")
    sayHello("a", "different", "set of", "arguments")
    print("after second sayHello() call")

From the output, we can see that the behavior changes quite significantly::

    Inside __init__()
    Inside __call__()
    After decoration
    Preparing to call sayHello()
    Inside wrapped_f()
    Decorator arguments: hello world 42
    sayHello arguments: say hello argument list
    After f(*args)
    after first sayHello() call
    Inside wrapped_f()
    Decorator arguments: hello world 42
    sayHello arguments: a different set of arguments
    After f(*args)
    after second sayHello() call

Now the process of decoration calls the constructor and then immediately invokes
``__call__()``, which can only take a single argument (the function object) and
must return the decorated function object that replaces the original. Notice
that ``__call__()`` is now only invoked once, during decoration, and after that
the decorated function that you return from ``__call__()`` is used for the
actual calls.

Although this behavior makes sense -- the constructor is now used to capture the
decorator arguments, but the object ``__call__()`` can no longer be used as the
decorated function call, so you must instead use ``__call__()`` to perform the
decoration -- it is nonetheless surprising the first time you see it because
it's acting so much differently than the no-argument case, and you must code the
decorator very differently from the no-argument case.

Decorator Functions with Decorator Arguments
==================================================

Finally, let's look at the more complex decorator function implementation, where
you have to do everything all at once::

    def decoratorFunctionWithArguments(arg1, arg2, arg3):
        def wrap(f):
            print("Inside wrap()")
            def wrapped_f(*args):
                print("Inside wrapped_f()")
                print("Decorator arguments:", arg1, arg2, arg3)
                f(*args)
                print("After f(*args)")
            return wrapped_f
        return wrap

    @decoratorFunctionWithArguments("hello", "world", 42)
    def sayHello(a1, a2, a3, a4):
        print('sayHello arguments:', a1, a2, a3, a4)

    print("After decoration")

    print("Preparing to call sayHello()")
    sayHello("say", "hello", "argument", "list")
    print("after first sayHello() call")
    sayHello("a", "different", "set of", "arguments")
    print("after second sayHello() call")

Here's the output::

    Inside wrap()
    After decoration
    Preparing to call sayHello()
    Inside wrapped_f()
    Decorator arguments: hello world 42
    sayHello arguments: say hello argument list
    After f(*args)
    after first sayHello() call
    Inside wrapped_f()
    Decorator arguments: hello world 42
    sayHello arguments: a different set of arguments
    After f(*args)
    after second sayHello() call

The return value of the decorator function must be a function used to wrap the
function to be decorated. That is, Python will take the returned function and
call it at decoration time, passing the function to be decorated. That's why we
have three levels of functions; the inner one is the actual replacement
function.

Because of closures, ``wrapped_f()`` has access to the decorator arguments
``arg1``, ``arg2`` and ``arg3``, *without* having to explicitly store them as in
the class version. However, this is a case where I find "explicit is better than
implicit," so even though the function version is more succinct I find the class
version easier to understand and thus to modify and maintain.

Further Reading
==================================================

    http://wiki.python.org/moin/PythonDecoratorLibrary
        More examples of decorators. Note the number of these examples that
        use classes rather than functions as decorators.

    http://scratch.tplus1.com/decoratortalk
        Matt Wilson's *Decorators Are Fun*.

    http://loveandtheft.org/2008/09/22/python-decorators-explained
        Another introduction to decorators.

    http://www.phyast.pitt.edu/~micheles/python/documentation.html
        Michele Simionato's decorator module wraps functions for you. The page
        includes an introduction and some examples.

