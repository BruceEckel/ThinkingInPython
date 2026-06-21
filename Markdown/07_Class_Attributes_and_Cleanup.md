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
However, when an object owns an outside resource (a file, a socket, a lock),
you must release it.
Python garbage collector calls an object's `__del__()` method when it collects that object.
This seems like a candidate for releasing resources:

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

    def __repr__(self):
        return f"Counter({self.name!r} {self.count})"

counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))

for c in counters:
    print(c)
    del c
print("End of delete loop")
```

For CPython, the output is:

    First created
    Second created
    Third created
    Counter('First' 3)
    Counter('Second' 3)
    Counter('Third' 3)
    End of delete loop
    Third deleted
    2 Counter objects remaining
    Second deleted
    1 Counter objects remaining
    First deleted
    Last Counter object deleted

`del c` inside the loop does not delete the object.
It only unbinds the name `c`.
Each `Counter` is still referenced by the `counters` list,
so its reference count never reaches zero during the loop.
That is why no `deleted` lines appear while the loop runs,
and why every `__repr__()` prints `3`.
Nothing has been destroyed yet, so the class attribute `count` is still `3` for all three.
The `End of delete loop` line, printed before any deletion, confirms that the loop destroys nothing.

The objects are destroyed later, at interpreter shutdown,
when the global `counters` list is torn down.
That list holds the only remaining references,
so when it goes, the objects it holds go with it.

The reverse order (`Third`, then `Second`, then `First`) comes from how CPython deallocates a list.
It releases the items from the last index down to the first,
so `Third` reaches a reference count of zero first and its `__del__()` runs first,
followed by `Second` and then `First`.
The effect is last-in, first-out.

This order, and the fact that `__del__()` runs at exit,
is a CPython reference-counting detail.
The language does not promise when, or in what order, `__del__()` runs.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order, or not run the finalizers before exit at all.

Thus, leaning on `__del__()` is fragile because the timing is not guaranteed.
At interpreter shutdown the globals it refers to may already be gone.
The Python documentation warns:

> Warning: Due to the precarious circumstances under which `__del__()`
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to `sys.stderr` instead. Also, when
> `__del__()` is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the `__del__()` method may already have been deleted*. For this
> reason, `__del__()` methods should do the absolute minimum needed to
> maintain external invariants.

In this run the deletions happen during shutdown,
exactly the precarious moment the warning describes.
`Counter` and `print` were still available, so the output came out cleanly,
but the teardown order that allowed that is not guaranteed.
So `__del__()` should do as little as possible, and you should not depend on it.

Two approaches are more reliable:

1. An explicit finalizer such as the `close()` that file objects provide,
   called from a `with` block. This runs even when an error interrupts the code.

2. A weak reference, which tracks an object without keeping it alive.
   Here, a `WeakValueDictionary` counts live instances,
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


counters = []
for name in ["First", "Second", "Third"]:
    counters.append(Counter(name))
```

The count now falls on its own as objects are collected,
with no explicit `del` required.
