# Initialization and Cleanup

## Initialization

### Constructor Calls

Automatic base-class constructor calls.

Calling the base-class constructor first, how to do it using super(),
why you should always call it first even if it's optional when to call
it.

guideline: Be rigorous about calling base-class initializers as the
first step of your __init__() method. Call them using super() so
that modifications to the class hierarchy don't cause problems.

### `__new__()` vs. `__init__()`

### Static Fields

An excellent example of the subtleties of initialization is static
fields in classes:

```python
# static_fields.py
class Foo:
        x = "a"

Foo.x
f = Foo()
f.x
f2 = Foo()
f2.x
f2.x = 'b'
f.x
Foo.x = 'c'
f.x
f2.x
Foo.x = 'd'
f2.x
f.x
f3 = Foo()
f3.x
Foo.x = 'e'
f3.x
f2.x
```

If you assign, you get a new one. If it's modifiable, then unless you
assign you are working on a singleton. So a typical pattern is:

```python
# static_idiom.py
class Foo:
    something = None # Static: visible to all classes
def f(self, x):
    if not self.something:
        self.something = [] # New local version for this object
    self.something.append(x)
```

This is not a serious example because you would naturally just
initialize `something` in `Foo`'s constructor.

### Class Attributes Are Not Default Values

A static field is also called a *class attribute*, and it is easy to misread one
as a per-object default value. It is not. There is one shared variable for the
whole class, and an instance variable of the same name *shadows* it. This trips
up programmers coming from C++ or Java, where storage for such a field is
allocated per object before the constructor runs. I wrote about this confusion in
[Misunderstanding Python Class Attributes](https://www.bruceeckel.com/2022/05/11/misunderstanding-python-class-attributes/).

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

The [Data Classes as Types](05_Data_Classes_as_Types.md) chapter builds on this:
a `@dataclass` reads the class-attribute declarations as a template and generates
a constructor from them.

## Cleanup

Cleanup happens to globals by setting them to `None` (what about
locals?). Does the act of setting them to None cause __del__ to be
called, or is __del__ called by Python before a global is set to
None?

Consider the following:

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

Without the final del, you get an exception. Shouldn't the normal
cleanup process take care of this?

From the Python docs regarding `__del__`:

> Warning: Due to the precarious circumstances under which __del__()
> methods are invoked, exceptions that occur during their execution are
> ignored, and a warning is printed to sys.stderr instead. Also, when
> __del__() is invoked in response to a module being deleted (e.g.,
> when execution of the program is done), *other globals referenced by
> the __del__() method may already have been deleted*. For this
> reason, __del__() methods should do the absolute minimum needed to
> maintain external invariants.

Without the explicit call to `del`, `__del__` is only called at the end
of the program, Counter and/or count may have already been GC-ed by the
time `__del__` is called (the order in which objects are collected is
not deterministic). The exception means that Counter has already been
collectd. You can't do anything particularly fancy with __del__.

There are two possible solutions here.

1. Use an explicit finalizer method, such as `close()` for file objects.

2. Use weak references.

Here's an example of weak references, using a WeakValueDictionary and
the trick of mapping id(self) to self:

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

Now cleanup happens properly without the need for an explicit call to
`del`.

What about local variables?

## Further Reading
