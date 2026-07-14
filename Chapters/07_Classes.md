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
            print(msg + ":", self.s)
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

Python methods require a reference to the current object.
When you *define* a method you must explicitly specify the reference as the first parameter.
Python programmers traditionally name the reference `self`,
but you can use any identifier
(however, anything other than `self` will probably confuse people).
To refer to the object's fields or its other methods,
you must go through `self`.

When you call a method for an object, as in `x.show()`,
Python passes the object reference automatically.

The first method, `__init__()`, is the *initializer*.
The double underscores (a.k.a. "dunder") indicate a special name.
The `__new__()` method is the *constructor*, but we hardly ever use that.
It has become common practice to call `__init__()` the constructor,
since it does the job of constructors in other OOP languages.
We follow that practice in this book.

Python calls the constructor automatically during object creation.
At the bottom of the example you can see that the creation of an object looks like a function call,
but using the class name.

In C++ or Java you declare object-level fields inside the class body but outside of the methods.
You do not declare them this way in Python.
To create an object field, you name it, using `self`, inside a method
(typically in the constructor, but not always).
This creates space for that field when the method runs.
If you declare fields using the C++/Java style,
they implicitly become class-level fields
(similar to static fields in C++/Java).

You can see the shape of an object with `display_object()`,
a small inspection helper built in [Metaprogramming](17_Metaprogramming.md#the-inspect-module).
It prints an object's attributes and methods:

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

Because Python is dynamically typed, it doesn't really care about interfaces.
All it cares about is applying operations to objects.
With inheritance in C++ or Java,
you often inherit only to establish a common interface.
Python is different.
You inherit an implementation, to reuse the code from the base class.

First import the base class the same way you import any name from a module
(see [Modules and Packages](06_Modules_and_Packages.md)).
Then inherit by listing the class
(or classes, since Python supports multiple inheritance)
in parentheses after the name of the inheriting class.
Here, we import and subclass `Simple`, from the `simple_class` module:

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
The next section explains the `@override` decorator on `show()`.

The demo shows that the base-class constructor runs.
You can also see that the inherited `show_twice()` method is available in the derived class.

The class `Different` also has a method named `show()`,
but this class does not derive from `Simple`.
The `f()` function in the demo demonstrates dynamic typing.
All it cares about is that it can call `show()` on `obj`,
with no other type requirements.
Thus, `f()` works equally on an object of a class derived from `Simple` and one that isn't,
as long as the `obj` argument has a `show()`.

## Marking Overrides with `@override`

When you override a method,
nothing requires the name to match a method in the base class.
A typo, or a base method that someone later renames or removes,
silently produces a new method instead of an override.
This bug is easy to miss.

The `@override` decorator from the `typing` module closes that gap.
It declares that a method is meant to replace one from a base class:

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

Derived().show()
#: Derived.show
```

A type checker now verifies the claim.
If `Derived.show` does not actually override a method in a base class,
because the name is misspelled or the base method is gone,
the checker reports an error.

At runtime `@override` does nothing but return the method unchanged.
All the verification happens in the type checker, before the program runs.

Apply `@override` to any method that replaces an inherited method,
except constructors, which are undecorated by convention.

## Properties

You can expose a plain attribute and convert it to a computed one later,
without changing the calling code, using `@property`:

```python
# properties.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # A plain attribute

    @property
    def area(self):           # Used like an attribute, not a call
        return 3.14159 * self.radius ** 2

c = Circle(10)
print(c.radius)
#: 10
print(c.area)  # Properties don't use parentheses
#: 314.159
```

Because the change is invisible at the call site,
do not preemptively add getters and setters.
You can always add them later when you discover you need the logic.

The default `@property` is *read-only*.
It is only a getter.
Assigning to it raises an `AttributeError`.
To enable writing, add a *setter*,
which allows you to validate the value before storing it:

```python
# property_setter.py

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Goes through the setter below

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

c = Circle(10)
c.radius = 5      # The setter validates, then stores
print(c.radius)
#: 5
try:
    Circle(-1)
except ValueError as e:
    print(f"Failed: {e}")
#: Failed: radius cannot be negative
```

The getter and setter are independent,
so you choose the access you want by defining one or both.
A write-only property is possible but rare.
A plain method is a better expression of the intent.

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
print(n.total)  # Second access: stored value, no recomputation
#: 30
```

The first access runs the method.
The second access produces the same result from the stored value.
The attribute is *lazily initialized*, created on first use,
so there's no cost if the attribute is not accessed.
The stored value lives on the instance.
`del n.total` discards it, and the next access recomputes.

`cached_property` trades freshness for speed, so if `n.values` changed,
`total` would be stale.
A plain `@property` recomputes every time and is never wrong.
Cache only what cannot change.

## String Representation

Two special methods control the way an object displays.
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
print(p)       # Falls back to __repr__
#: Point(3, 4)
print([p, p])
#: [Point(3, 4), Point(3, 4)]
```

Define `__repr__()` on classes you debug.

## Static and Class Methods

A method that doesn't use `self` can be a `@staticmethod`.
A method that needs the class rather than an instance can be a `@classmethod`.
This receives the class as its first argument, conventionally named `cls`:

```python
# class_methods.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, f):    # An alternative constructor
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):        # Needs no self or cls
        return celsius <= 0

t = Temperature.from_fahrenheit(212)
print(round(t.celsius))
#: 100
print(Temperature.is_freezing(-4))
#: True
```

For classes that are primarily a bundle of typed data,
[Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)
shows how `@dataclass` writes the constructor and `__repr__()` for you.

## Composing Methods with `import`

You can compose methods into a class using `import`.
Multiple classes can reuse a method defined this way:

```python
# utility.py

def f(self):
    print(f"utility.f() called on {self}")
```

Here we compose that method into a class:

```python
# compose.py

class Compose:
    from utility import f

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Compose({self.name!r})"

Compose("example").f()
#: utility.f() called on Compose('example')
```

Because `f` is now an ordinary method, its first parameter is `self`,
the `Compose` instance.
This is a curiosity more than a technique.
It works because `import` inside a class body binds like any other assignment,
but composition, mixins,
or a plain module-level function are almost always a clearer choice.
You will rarely, if ever, want this in your own code.

## Exercises

1.  Add a method `shrink(self, factor)` to `Circle` in `property_setter.py` that sets `self.radius = self.radius / factor`,
    going through the existing setter.
    Confirm `shrink(2)` on a `Circle(10)` leaves the radius at `5`,
    then confirm `shrink(-2)`, which would divide the radius down to `-5`,
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
