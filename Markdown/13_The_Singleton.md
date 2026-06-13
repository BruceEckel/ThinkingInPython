# The Singleton

Possibly the simplest design pattern is the *singleton*, which is a way
to provide one and only one object of a particular type. To accomplish
this, you must take control of object creation out of the hands of the
programmer. One convenient way to do this is to delegate to a single
instance of a private nested inner class:

```python
# Singleton/SingletonPattern.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg: str) -> None:
            self.val = arg

        def __str__(self) -> str:
            return repr(self) + self.val

    instance: Any = None

    def __init__(self, arg: str) -> None:
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne(arg)
        else:
            OnlyOne.instance.val = arg

    def __str__(self) -> str:
        return str(self.instance)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)


x = OnlyOne('sausage')
print(x)
y = OnlyOne('eggs')
print(y)
z = OnlyOne('spam')
print(z)
print(x)
print(y)
print(repr(x))
print(repr(y))
print(repr(z))
```

Because the inner class is named with a double underscore, it is private
so the user cannot directly access it. The inner class contains all the
methods that you would normally put in the class if it weren't going to
be a singleton, and then it is wrapped in the outer class which controls
creation by using its constructor. The first time you create an
`OnlyOne`, it initializes `instance`, but after that it just ignores
you.

Access comes through delegation, using the `__getattr__()` method
to redirect calls to the single instance. You can see from the output
that even though it appears that multiple objects have been created, the
same `__OnlyOne` object is used for both. The instances of
`OnlyOne` are distinct but they all proxy to the same `__OnlyOne`
object.

Note that the above approach doesn't restrict you to creating only one
object. This is also a technique to create a limited pool of objects. In
that situation, however, you can be confronted with the problem of
sharing objects in the pool. If this is an issue, you can create a
solution involving a check-out and check-in of the shared objects.

A variation on this technique uses the class method `__new__`
added in Python 2.2:

```python
# Singleton/NewSingleton.py
from typing import Any


class OnlyOne:
    class __OnlyOne:
        def __init__(self) -> None:
            self.val: str | None = None

        def __str__(self) -> str:
            return repr(self) + str(self.val)

    instance: Any = None

    def __new__(cls) -> Any:  # __new__ is always a classmethod
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

    def __getattr__(self, name: str) -> Any:
        return getattr(self.instance, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.instance, name, value)


x = OnlyOne()
x.val = 'sausage'
print(x)
y = OnlyOne()
y.val = 'eggs'
print(y)
z = OnlyOne()
z.val = 'spam'
print(z)
print(x)
print(y)
```

Alex Martelli makes the [observation](http://www.aleax.it/Python/5ep.html)
that what we really want with a Singleton is to have a single set of state
data for all objects. That is, you could create as many objects as you want
and as long as they all refer to the same state information then you achieve
the effect of Singleton. He accomplishes this with what he calls the
*Borg*^[From the television show *Star Trek: The Next Generation*. The Borg
are a hive-mind collective: "we are all one."] , which is accomplished by
setting all the `__dict__`s to the same static piece of storage:

```python
# Singleton/BorgSingleton.py
# Alex Martelli's 'Borg'
from typing import Any


class Borg:
    _shared_state: dict[str, Any] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state


class Singleton(Borg):
    def __init__(self, arg: str) -> None:
        Borg.__init__(self)
        self.val = arg

    def __str__(self) -> str:
        return self.val


x = Singleton('sausage')
print(x)
y = Singleton('eggs')
print(y)
z = Singleton('spam')
print(z)
print(x)
print(y)
print(repr(x))
print(repr(y))
print(repr(z))
```

This has an identical effect as `SingletonPattern.py` does, but it's
more elegant. In the former case, you must wire in *Singleton* behavior
to each of your classes, but *Borg* is designed to be easily reused
through inheritance.

A simpler version^[From Dmitry Balabanov.] of this takes advantage of the fact
that there's only one instance of a class variable:

```python
# Singleton/ClassVariableSingleton.py
from typing import Any


class SingleTone:
    val: Any
    __instance: "SingleTone | None" = None

    def __new__(cls, val: Any) -> "SingleTone":
        instance = SingleTone.__instance
        if instance is None:
            instance = object.__new__(cls)
            SingleTone.__instance = instance
        instance.val = val
        return instance
```

Two other interesting ways to define singleton^[Suggested by Chih-Chung
Chang.]  include wrapping a class and using metaclasses. The first approach
could be thought of as a *class decorator* (decorators will be defined later
in the book), because it takes the class of interest and adds functionality to
it by wrapping it in another class:

```python
# Singleton/SingletonDecorator.py
from typing import Any


class SingletonDecorator:
    def __init__(self, klass: type) -> None:
        self.klass = klass
        self.instance: Any = None

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


class Foo:
    pass


foo = SingletonDecorator(Foo)

x = foo()
y = foo()
z = foo()
x.val = 'sausage'
y.val = 'eggs'
z.val = 'spam'
print(x.val)
print(y.val)
print(z.val)
print(x is y is z)
```

{{ Description }}

The second approach uses metaclasses, a topic I do not yet understand
but which looks very interesting and powerful indeed (note that Python
2.2 has improved/simplified the metaclass syntax, and so this example
may change):

```python
# Singleton/SingletonMetaClass.py
from typing import Any


class SingletonMetaClass(type):
    def __init__(cls, name: str, bases: tuple[type, ...],
                 namespace: dict[str, Any]) -> None:
        super().__init__(name, bases, namespace)
        klass: Any = cls
        original_new = klass.__new__

        def my_new(c: Any, *args: Any, **kwds: Any) -> Any:
            if c.instance is None:
                c.instance = original_new(c)
            return c.instance

        klass.instance = None
        klass.__new__ = staticmethod(my_new)


class Bar(metaclass=SingletonMetaClass):
    def __init__(self, val: str) -> None:
        self.val = val

    def __str__(self) -> str:
        return repr(self) + self.val


x = Bar('sausage')
y = Bar('eggs')
z = Bar('spam')
print(x)
print(y)
print(z)
print(x is y is z)
```

{{ Long, detailed, informative description of what metaclasses are and
how they work, magically inserted here }}

## Exercises

1.  `SingletonPattern.py` always creates an object, even if it's never
    used. Modify this program to use *lazy initialization*, so the
    singleton object is only created the first time that it is needed.
2.  Using `SingletonPattern.py` as a starting point, create a class
    that manages a fixed number of its own objects. Assume the objects
    are database connections and you only have a license to use a fixed
    quantity of these at any one time.
3.  Modify `BorgSingleton.py` so that it uses a class `__new__()` method.
