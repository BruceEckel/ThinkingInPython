# Classes

Class definitions use minimal syntax.
You start with the `class` keyword followed by the class name and a colon.
Use `def` to create methods inside the indented class body:

```python
# simple_class.py

class Simple:
    def __init__(self, text):
        print("Inside the Simple constructor")
        self.s = text
    # Two methods:
    def show(self, msg=""):
        if msg:
            print(f"{msg}:", self.s)
        else:
            print(self.s)
    def show_twice(self):
        self.show()  # Calling another method
        self.show()
```

```python
# demo_simple_class.py
from simple_class import Simple

x = Simple("Constructor argument")  # Create an object
#: Inside the Simple constructor
x.show()
#: Constructor argument
x.show("A message")
#: A message: Constructor argument
x.show_twice()
#: Constructor argument
#: Constructor argument
```

Ordinary methods require a reference to the current object.
When you define a method you must explicitly specify the reference as the first parameter.
Python programmers traditionally name the reference `self`,
but you can use any identifier (though anything else probably confuses people).
To refer to the object's attributes or its other methods,
you must go through `self`.

```python
# forgot_self.py

class Oops:
    def show():  # Missing the self parameter
        print("never runs")

try:
    Oops().show()  # type: ignore
except TypeError as e:
    print(e)
#: Oops.show() takes 0 positional arguments but 1 was given
```

When you call a method for an object, as in `x.show()`,
Python passes the object reference automatically.
The "1" in the error message is that reference,
and a method defined without `self` has no parameter to receive it.
A type checker sees the mistake before anything runs,
so the call carries a `# type: ignore` to say the mistake is deliberate.

The first method, `__init__()`, is the *initializer*.
The double underscores on both ends make it a *dunder*,
Python's name for a method the language itself calls.
The `__new__()` method is the *constructor*, which you rarely use
([Singleton](24_Patterns--Singleton.md) shows a case that needs it).
Most programmers call `__init__()` the constructor,
since it does the job of constructors in other OOP languages.
This book follows that practice.

Python calls the constructor automatically during object creation.
In the demo, creating an object looks like calling a function named after the class.

In C++ or Java you declare object-level fields inside the class body but outside the methods.
In Python an object attribute comes into being when a method assigns to it through `self`
(typically in the constructor, but not always).
The assignment creates space for that attribute when the method runs.
If you assign to a name in the class body, C++/Java style,
that name becomes a class-level attribute instead
(similar to a static field in C++/Java).
[Class Attributes](09_Foundations--Class_Attributes.md)
shows what that shared storage does when you assign to it.
A bare annotation with no value looks most like a C++ or Java field declaration,
yet it creates neither kind of attribute.
It records the type and nothing else.
[Class Attributes](09_Foundations--Class_Attributes.md#declaring-shared-state-with-classvar)
and [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#data-classes)
use it.

`display_object()`, a small inspection helper built in [Metaprogramming](17_Techniques--Metaprogramming.md#building-display_object),
shows the shape of an object by printing its attributes and methods:

```python
# display_simple.py
from display import display_object
from simple_class import Simple

x = Simple("Constructor argument")
#: Inside the Simple constructor
display_object(x)
#: [Attributes]
#:   • s = 'Constructor argument'
#: [Methods]
#:   • show(self, msg='')
#:   • show_twice(self)
```

The instance carries one attribute, `s`,
while the two methods belong to the class.
The constructor `__init__()` is a dunder,
so `display_object()` hides it by default.

## Inheritance

Because Python is dynamically typed,
it applies an operation to an object and never checks an interface first.
With inheritance in C++ or Java,
you often inherit only to establish a common interface.
Python is different.
You inherit an implementation, to reuse the code from the base class.
Python can still name an interface without inheritance: a `Protocol`
([Static Types](08_Foundations--Static_Types.md))
describes the shape a function needs, with no base class to inherit.

First import the base class the same way you import any name from a module
(see [Modules and Packages](06_Foundations--Modules_and_Packages.md)).
Then inherit by listing the base class in parentheses after the name of the inheriting class.
Python supports multiple inheritance, so you can list several classes,
though [Rethinking Objects](20_Patterns--Rethinking_Objects.md)
argues against it in favor of protocols.
`simple2.py` imports and subclasses `Simple`, from the `simple_class` module.
Ignore the `@override` decorator for now.
[Marking Overrides with `@override`](#marking-overrides-with-override)
explains it:

```python
# simple2.py
from typing import override
from simple_class import Simple

class Simple2(Simple):  # Simple2 inherits Simple
    def __init__(self, text):
        print("Inside Simple2 constructor")
        # Call the base-class constructor with super():
        super().__init__(text)
    def display(self):
        self.show("Called from display()")
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        # Call the base-class method from inside
        # the overridden method:
        super().show(msg)

class Different:
    def show(self):
        print("Not derived from Simple")
```

```python
# demo_simple2.py
from simple2 import Different, Simple2

x = Simple2("Simple2 constructor argument")
#: Inside Simple2 constructor
#: Inside the Simple constructor
x.display()
#: Overridden show() method
#: Called from display(): Simple2 constructor argument
x.show()
#: Overridden show() method
#: Simple2 constructor argument
x.show_twice()  # Inherited from Simple
#: Overridden show() method
#: Simple2 constructor argument
#: Overridden show() method
#: Simple2 constructor argument
def f(obj):  # Works on any obj with a show()
    obj.show()
f(x)
#: Overridden show() method
#: Simple2 constructor argument
f(Different())
#: Not derived from Simple
```

`Simple2` inherits from `Simple`.
In the constructor, `super().__init__()` calls the base-class constructor.
In `display()`, you can call `show()` as a method of `self`.
When you override a method but still want the base-class version,
call it through `super()`, as the overridden `show()` does.

`super()` and ordinary attribute lookup both follow one list,
the class's *method resolution order* (MRO):
the classes Python searches for a name,
starting with the class itself and ending at `object`.
`Simple2.__mro__` is `(Simple2, Simple, object)`.
With a single base class the order is obvious.
With several, the MRO decides which base supplies a name that more than one of them defines.
`A` and `B` below both define `show()`, and `C` inherits from both:

```python
# mro_conflict.py

class A:
    def show(self):
        print("A.show")

class B:
    def show(self):
        print("B.show")

class C(A, B):
    pass  # Defines no show() of its own

print([c.__name__ for c in C.__mro__])
#: ['C', 'A', 'B', 'object']
C().show()  # A comes first in the MRO
#: A.show
```

`C.__mro__` visits `A` before `B`, so `C().show()` runs `A`'s version,
not `B`'s.

The base-class constructor runs because `Simple2`'s constructor calls it.
Unlike C++ and Java, Python never calls a base-class constructor on its own.
If you remove the `super().__init__(text)` line, nothing creates `self.s`,
so the first method that reads it raises an `AttributeError`.
Dropping the call and then calling `show()` confirms it:

```python
# missing_super.py
from simple_class import Simple

class Broken(Simple):
    def __init__(self, text):
        pass  # Forgot super().__init__(text)

try:
    Broken("ignored").show()
except AttributeError as e:
    print(e)
#: 'Broken' object has no attribute 's'
```

A derived class that defines no constructor of its own inherits and runs the base version.
The derived class also inherits `show_twice()` unchanged.

The class `Different` also has a method named `show()`,
but does not derive from `Simple`.
`f()` in `demo_simple2.py` demonstrates dynamic typing:
it requires one thing of `obj`, a `show()` it can call,
so it accepts a `Simple2` and a `Different` alike.

## Composing Methods with `import`

You can compose methods into a class using `import`.
More than one class can reuse a method defined this way:

```python
# utility.py

def f(self):
    print(f"utility.f() called on {self.name}")
```

`compose.py` composes that method into two unrelated classes:

```python
# compose.py

class Compose:
    from utility import f

    def __init__(self, name):
        self.name = name

class Other:
    from utility import f

    def __init__(self, name):
        self.name = name

Compose("example").f()
#: utility.f() called on example
Other("second").f()
#: utility.f() called on second
```

Because `f` is now an ordinary method, its first parameter is `self`,
whichever class imported it.
The import works because `import` inside a class body binds a name like any other assignment,
but it is a curiosity more than a technique:
a helper object or a module-level function is almost always the clearer choice.

## Marking Overrides with `@override`

When you override a method,
nothing requires the name to match a method in the base class.
A typo, or a base method that someone later renames or removes,
silently produces a new method instead of an override,
and that bug is easy to miss.

The `@override` decorator from the `typing` module catches it.
A line starting with `@` above a definition applies a *decorator* to it.
[Decorators](14_Techniques--Decorators.md) shows how they work,
and this chapter only applies existing ones.
`@override` declares that a method replaces one from a base class:

```python
# override_intro.py
from typing import override

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    @override
    def show(self):
        print("Derived.show")

class Typo(Base):
    # @override  # "shwo" does not override anything
    def shwo(self):
        print("Typo.shwo")

Derived().show()
#: Derived.show
```

A type checker now verifies that claim.
A decorated method that matches nothing in a base class,
because of a misspelling or a base method that no longer exists, is an error.
Uncomment the decorator on `Typo.shwo`, and the checker reports:

```text
error[invalid-explicit-override]: Method `shwo` is decorated with
`@override` but does not override anything
```

Python runs the program either way.
Catching the mistake takes a separate tool,
and [Static Types](08_Foundations--Static_Types.md) sets that tool up.

At run time `@override` returns the same function object it received,
with no wrapper.
Before returning it,
the decorator tries to set an `__override__` attribute on it,
so that code can find overrides by introspection;
some callables refuse the attribute, and the decorator lets that pass.

Apply `@override` to any method that replaces an inherited method.
Two kinds stay undecorated by convention: constructors,
and dunders such as `__repr__()` and `__str__()` that replace a default inherited from `object`.

## Properties

With `@property`, you can expose a plain attribute and convert it to a computed one later,
without changing the calling code:

```python
# properties.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # A plain attribute

    @property
    def area(self):  # Used like an attribute, not a call
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)
#: 10
print(c.area)  # Properties don't use parentheses
#: 314.159
```

`radius` is a plain attribute here and `area` a computation,
and the call site reads both the same way.

A `@property` with a getter alone rejects writes:
assigning to it raises an `AttributeError`.
A *setter* enables writing,
and it is the place to validate the value before storing it:

```python
# property_setter.py

class Circle:
    def __init__(self, radius):
        # Goes through the setter below
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

    @property
    def area(self):  # Unchanged from the version above
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)  # The same two lines as before
#: 10
print(c.area)
#: 314.159
c.radius = 5  # Now the setter validates, then stores
print(c.radius)
#: 5
try:
    Circle(-1)
except ValueError as e:
    print(f"Failed: {e}")
#: Failed: radius cannot be negative
```

`property_setter.py` does what the section opened with:
`radius` began as a plain attribute and is now a validated property.
The two lines that read `c.radius` and `c.area` are the ones from `properties.py`,
unchanged.
Code outside the class reads both versions the same way,
and that is why you can wait to add a setter until you need one.

The property owns the name `radius` on the class,
so the value goes into a separate attribute.
A single leading underscore marks `_radius` as internal to the class,
a convention rather than a language rule.
The separate name matters: `self.radius` inside the getter,
or `self.radius = value` inside the setter, calls that same method again,
and again, until the interpreter raises a `RecursionError`.
Naming both the property and the backing attribute `radius` reproduces it:

```python
# property_recursion.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Calls the setter

    @property
    def radius(self):
        return self.radius  # Calls itself again

    @radius.setter
    def radius(self, value):
        self.radius = value  # Calls itself again

try:
    Circle(10)
except RecursionError as e:
    print(type(e).__name__)
#: RecursionError
```

The getter and setter are independent,
so you choose the access you want by defining one or both.
A write-only property is possible but rare;
a plain method expresses that intent better.

A `@property` reruns its code on every access.
When the computation is expensive and the answer cannot change,
`functools.cached_property` runs it once, on first access,
and stores the result:

```python
# cached_property_demo.py
from functools import cached_property

class Numbers:
    def __init__(self, values):
        self.values = values

    @cached_property
    def total(self):
        print("summing", len(self.values), "values")
        return sum(self.values)

n = Numbers([5, 10, 15])
print(n.total)
#: summing 3 values
#: 30
# Second access: stored value, no recomputation
print(n.total)
#: 30
n.values.append(20)
print(n.total)  # Still the old sum: the cache is stale
#: 30
del n.total  # Discard the cached value
print(n.total)
#: summing 4 values
#: 50
```

The first access runs the method.
The second access produces the same result from the stored value.
The attribute is *lazily initialized*, created on first use,
so it costs nothing until something reads it.
The stored value lives in the instance's `__dict__`.
A class declared with `slots=True`
([Performance](18_Techniques--Performance.md#slots) uses it) has no `__dict__`,
so `cached_property` has nowhere to store the value.

`cached_property` trades freshness for speed, so if `n.values` changes,
`total` becomes stale, as the appended `20` in `cached_property_demo.py` shows.
A plain `@property` recomputes every time, so its answer is always current.
Cache only what cannot change.

## String Representation

By default, printing an object shows its class and its address,
as in `<__main__.Point object at 0x7f2dd669cd70>`,
and that says nothing about the value the object holds.
Two dunder methods control how an object displays.
`__str__()` is the readable form for users,
and `__repr__()` is the unambiguous form for developers:

```python
# representation.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # Falls back to __repr__
#: Point(3, 4)
print([p, p])
#: [Point(3, 4), Point(3, 4)]
```

A `__str__()` on the same class separates the two forms:

```python
# representation_str.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

p = Point(3, 4)
print(p)  # print() prefers __str__
#: (3, 4)
print(repr(p))
#: Point(3, 4)
print([p])
#: [Point(3, 4)]
```

`print()` and `str()` use `__str__()` when it exists and fall back to `__repr__()` when it does not.
The fallback runs in one direction: `repr()` never consults `__str__()`.
A container builds its own display from the `__repr__()` of its elements,
and that is why the list prints `Point(3, 4)` rather than the shorter form.
In an f-string, `{p}` selects `__str__()` and `{p!r}` selects `__repr__()`.
By convention `__repr__()` returns the call that would rebuild the object,
so it reads `Point(3, 4)`.

Define `__repr__()` on classes you debug,
and add `__str__()` only when users see the output.

For classes that are primarily a bundle of typed data,
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#data-classes)
shows how `@dataclass` writes the constructor and `__repr__()`.

## Static and Class Methods

A method that never touches `self` can be a `@staticmethod`.
A method that needs the class rather than an instance can be a `@classmethod`.
A class method receives the class as its first argument,
conventionally named `cls`:

```python
# class_methods.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    # An alternative constructor
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):  # Needs no self or cls
        return celsius <= 0

class Reading(Temperature):
    pass  # Adds nothing; inherits from_fahrenheit()

t = Temperature.from_fahrenheit(212)
print(round(t.celsius))
#: 100
print(Temperature.is_freezing(-4))
#: True
r = Reading.from_fahrenheit(212)
print(type(r).__name__)
#: Reading
```

`from_fahrenheit()` builds its result with `cls(...)` rather than `Temperature(...)`.
Called on a subclass, `from_fahrenheit()` receives that subclass as `cls`,
so the alternative constructor produces the right kind of object,
and a subclass inherits it unchanged.
`Reading.from_fahrenheit(212)` proves it: `cls` is `Reading` there,
not `Temperature`, so `type(r).__name__` reports `'Reading'`.
Naming the class directly, `return Temperature(...)`,
would hard-code `Temperature` into every subclass, including `Reading`.

`is_freezing()` would also work as a module-level function.
Inside the class it sits where a reader looks for it,
and a subclass can replace it the way it replaces any other method.

## Exercises

1.  Add a method `shrink(self, factor)` to `Circle` in `property_setter.py` that sets `self.radius = self.radius / factor`,
    going through the existing setter.
    Confirm `shrink(2)` on a `Circle(10)` leaves the radius at `5.0`,
    then confirm that calling `shrink(-2)` on that same circle,
    which would divide the radius down to `-2.5`,
    still raises the setter's `ValueError` instead of silently storing a negative radius.
2.  In `class_methods.py`, add a second alternative constructor,
    `from_kelvin(cls, k)`, using `celsius = k - 273.15`.
    Add a call that builds a `Temperature` both ways for the same physical temperature and confirms they agree,
    within rounding.
3.  In `simple2.py`, add a third class, `Simple3(Simple2)`,
    that overrides `show()` again,
    printing its own message before calling `super().show(msg)`.
    Predict, then confirm,
    the full chain of prints from `Simple3("x").show_twice()`.
4.  Add a `@cached_property` called `average` to `Numbers` in `cached_property_demo.py` that returns `self.total / len(self.values)`.
    Access `n.total` and then `n.average`,
    and confirm `total` is not recomputed when `average` uses it.
5.  Give `Temperature` in `class_methods.py` a `__repr__()` that returns `Temperature(21.0)` for a temperature of 21 degrees Celsius.
    Print a single `Temperature` and a list of two of them,
    and confirm the list shows the same form for each element.
    Then add a `__str__()` returning `21.0C` and confirm which of the two `print()` uses for each case.
6.  In `override_intro.py`, misspell `Derived`'s method as `shwo()`,
    keeping the `@override` decorator.
    Run the program and confirm it still prints `Base.show`,
    then run the type checker
    ([Static Types](08_Foundations--Static_Types.md) sets one up)
    and read what it says.
    Remove `@override` and confirm the type checker goes quiet while the program's behavior does not change.
