# Initialization and Cleanup

A constructor sets up an object, and you saw `__init__()` do that above. Two
parts of an object's lifetime surprise programmers coming from C++ or Java: how
class-level attributes behave, and how and when objects are cleaned up.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*. It
is easy to misread one as a per-object default value. It is not. There is one
shared variable for the whole class, and an instance variable of the same name
*shadows* it. This trips up programmers coming from C++ or Java, where storage for
such a field is allocated per object before the constructor runs.

Simple use looks exactly like a default value, which is the trap:

```python
# class_attribute_confusion.py
# A class attribute looks like a per-object default, but it is one
# shared value, and an instance variable of the same name shadows it.
class Stars:
    rating = 5  # One value, shared by the whole class.


a = Stars()
b = Stars()
print(a.rating, b.rating)  # 5 5: both read the class attribute
a.rating = 1  # Assigning makes an instance variable on a.
print(a.rating, b.rating)  # 1 5: a shadows it, b sees the class
Stars.rating = 9  # Now change the shared class attribute.
print(a.rating, b.rating)  # 1 9: a keeps its own, b follows
```

The reason is that an instance and its class each have their own attribute
dictionary. Reading an attribute checks the instance first, then falls back to
the class. Assigning always writes to the instance, creating the variable there
the first time:

```python
# inside_objects.py
# An instance and its class each have their own attribute dictionary.
# Reading falls back to the class; assigning writes to the instance.
class A:
    x = 100  # class attribute


a = A()
print(vars(A)["x"])  # 100: the attribute lives in the class dict
print(vars(a))  # {}: the instance has no attributes yet
a.x = 1
print(vars(a))  # {'x': 1}: assignment created it on the instance
```

So a class attribute behaves like a default only until someone assigns to the
instance. Changing the class attribute then reaches into every object that has
not shadowed it yet. That produces bugs that surface far from their cause.

For real per-object defaults, write a constructor with default arguments, or use
a `@dataclass`, which turns the class-attribute syntax into exactly that. Each
object then gets its own storage:

```python
# real_defaults.py
# For per-object defaults, write a constructor, or use a @dataclass,
# which turns the class-attribute syntax into exactly that.
from dataclasses import dataclass


class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # an instance variable, one per object


@dataclass
class B:
    x: int = 100  # a constructor default, not a shared value


if __name__ == "__main__":
    a = A()
    a.x = -1
    print(a.x, A().x)  # -1 100: a's change does not leak
    print(B().x, B(7).x)  # 100 7
```

The [Data Classes as Types](10_Data_Classes_as_Types.md) chapter builds on this:
a `@dataclass` reads the class-attribute declarations as a template and generates
a constructor from them.

## Cleanup

Python manages memory for you, so most objects need no explicit cleanup. When an
object owns an outside resource (a file, a socket, a lock), you still have to
release it. Python calls an object's `__del__()` method when it collects the
object, which looks like the place for that work:

```python
# cleanup.py
class Counter:
    count: int = 0   # Number of objects of this class

    def __init__(self, name: str) -> None:
        self.name = name
        print(name, 'created')
        Counter.count += 1

    def __del__(self) -> None:
        print(self.name, 'deleted')
        Counter.count -= 1
        if Counter.count == 0:
            print('Last Counter object deleted')
        else:
            print(Counter.count, 'Counter objects remaining')


x = Counter("First")
del x
```

This runs, but leaning on `__del__()` is fragile. Its timing is not guaranteed,
and at interpreter shutdown the globals it refers to may already be gone. The
Python documentation warns:

> Warning: Due to the precarious circumstances under which __del__()
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to sys.stderr instead. Also, when
> __del__() is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the __del__() method may already have been deleted*. For this
> reason, __del__() methods should do the absolute minimum needed to
> maintain external invariants.

The explicit `del x` above forces collection while `Counter` is still intact.
Without it the cleanup fires during shutdown, when `Counter` may already be gone.
So `__del__()` should do the minimum, and you should not depend on it. Two
approaches are sturdier.

First, an explicit finalizer such as the `close()` that file objects provide,
called from a `with` block so it runs even when an error interrupts the code.

Second, a weak reference, which tracks an object without keeping it alive. Here a
`WeakValueDictionary` counts live instances, using `id(self)` as each object's
key:

```python
# weak_value.py
from weakref import WeakValueDictionary


class Counter:
    _instances: WeakValueDictionary[int, Counter] = (
        WeakValueDictionary())

    @property
    def count(self) -> int:
        return len(self._instances)

    def __init__(self, name: str) -> None:
        self.name = name
        self._instances[id(self)] = self
        print(name, 'created')

    def __del__(self) -> None:
        print(self.name, 'deleted')
        if self.count == 0:
            print('Last Counter object deleted')
        else:
            print(self.count, 'Counter objects remaining')


x = Counter("First")
```

The count now falls on its own as objects are collected, with no explicit `del`
required.

