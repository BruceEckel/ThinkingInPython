# Class Attributes and Cleanup

Two parts of an object's lifetime surprise programmers coming from C++ or Java:

- How class-level attributes behave
- How and when objects are cleaned up.

## Class Attributes Are Not Default Values

A field declared in the class body, outside any method, is a *class attribute*.
It is easy to misread one as a per-object default value.
It is not.
A class attribute creates one shared variable across all instances of the class.
If you then create an instance variable of the same name, that instance variable *shadows* the class attribute.
This trips up programmers coming from C++ or Java,
where storage for such a field is allocated per object before the constructor runs.

Here's an example showing why it can be confusing:

```python
# class_attribute_confusion.py

class Stars:
    rating = 5  # One value, shared by the whole class.


a = Stars()
b = Stars()
print(a.rating, b.rating)  # 5 5: Both read the class attr
a.rating = 1  # Assigning makes an instance variable on a
print(a.rating, b.rating)  # 1 5: a shadows it, b sees the class
Stars.rating = 9  # Change the shared class attr
print(a.rating, b.rating)  # 1 9: a instance variable , b class attr
```

An instance and its class each have their own attribute dictionary.
Reading an attribute checks the instance first, then falls back to the class.
Assigning always writes to the instance,
creating an instance variable the first time it is referenced.
To show this we can select the class with `vars(A)` and the instance with `vars(a)`:

```python
# inside_objects.py

class A:
    x = 100  # class attribute


a = A()
print(vars(A)["x"])  # 100: The attribute lives in the class dict
print(vars(a))  # {}: The instance has no attributes yet
a.x = 1
print(vars(a))  # {'x': 1}: Assignment created it on the instance
print(vars(A)["x"])  # Still 100
```

So a class attribute seems like a default until someone assigns to an instance variable of the same name.
Changing the class attribute makes the "default" value of `x` seem different for every object that has not shadowed it.
This produces bugs that surface far from their cause.

For real per-object defaults, write a constructor with default arguments,
or use a `@dataclass`, which turns the class-attribute syntax into instance variable defaults.
Each object then gets its own storage for instance variables:

```python
# real_defaults.py
from dataclasses import dataclass


class A:
    def __init__(self, x: int = 100) -> None:
        self.x = x  # An instance variable, one per object

@dataclass
class B:
    x: int = 100  # Constructor default, not class attribute


if __name__ == "__main__":
    a = A()
    a.x = -1
    print(a.x, A().x)  # -1 100: a's change does not leak
    print(B().x, B(7).x)  # 100 7
```

A `@dataclass` reads the class-attribute declarations as a template and generates a constructor from them.
This is detailed in [Data Classes as Types](10_Data_Classes_as_Types.md).

## Cleanup

Python manages memory for you, so most objects need no explicit cleanup.
When an object owns an outside resource (a file, a socket, a lock),
you still have to release it.
Python calls an object's `__del__()` method when it collects the object,
which looks like the place for that work:

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

This runs, but leaning on `__del__()` is fragile.
Its timing is not guaranteed,
and at interpreter shutdown the globals it refers to may already be gone.
The Python documentation warns:

> Warning: Due to the precarious circumstances under which `__del__()`
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to `sys.stderr` instead. Also, when
> `__del__()` is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the `__del__()` method may already have been deleted*. For this
> reason, `__del__()` methods should do the absolute minimum needed to
> maintain external invariants.

The explicit `del x` above forces collection while `Counter` is still intact.
Without it the cleanup fires during shutdown,
when `Counter` may already be gone.
So `__del__()` should do the minimum, and you should not depend on it.
Two approaches are sturdier.

First, an explicit finalizer such as the `close()` that file objects provide,
called from a `with` block so it runs even when an error interrupts the code.

Second, a weak reference, which tracks an object without keeping it alive.
Here a `WeakValueDictionary` counts live instances,
using `id(self)` as each object's key:

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

The count now falls on its own as objects are collected,
with no explicit `del` required.
