# Classes

Like most things in Python, class definitions use minimal syntax.
You start with the `class` keyword followed by the class name and a colon.
Use `def` to create methods inside the indented class body:

```python
# simple_class.py

class Simple:
    def __init__(self, str):
        print("Inside the Simple constructor")
        self.s = str
    # Two methods:
    def show(self, msg=""):
        if msg:
            print(msg + ':', self.s)
        else:
            print(self.s)
    def show_twice(self):
        self.show()  # Calling another method
        self.show()

if __name__ == "__main__":
    # Create an object:
    x = Simple("Constructor argument")
    x.show()
    x.show("A message")
    x.show_twice()
```

Python methods require a reference to the current object.
When you *define* a method you must explicitly specify the reference as the first argument.
Traditionally, the reference is called `self` but you can use any identifier you want (if you do not use `self` you will probably confuse people).
To refer to fields in the object or other methods in the object,
you must use `self` in the expression.

When you call a method for an object, as in `x.show()`, the object reference is passed automatically.

The first method, `__init__()`,
defines the constructor; the double underscores (a.k.a. "dunder") indicate a special name.
The constructor is automatically called during object creation.
At the bottom of the example you can see that the creation of an object looks just like a function call using the class name.

In C++ or Java you declare object level fields inside the class body but outside of the methods.
You do not declare them this way in Python.
To create an object field, you just name it, using `self`,
inside a method (typically in the constructor, but not always).
This creates space for that field when the method runs.
If you declare fields using the C++/Java style,
they implicitly become class level fields (similar to static fields in C++/Java).

## Inheritance

Because Python is dynamically typed, it doesn't really care about interfaces.
All it cares about is applying operations to objects.
With inheritance in C++ or Java, you often inherit only to establish a common interface.
Python is different: you inherit an implementation, to re-use the code from the base class.

First import the base class the same way you import any name from a module (see [Modules and Packages](05_Modules_and_Packages.md)).
Then inherit by listing the class (or classes, since Python supports multiple inheritance) in parentheses after the name of the inheriting class.
Here, we import and subclass `Simple`, from the `simple_class` module:

```python
# simple2.py
from typing import override

from simple_class import Simple


class Simple2(Simple):  # Simple2 inherits Simple
    def __init__(self, str):
        print("Inside Simple2 constructor")
        # Call the base-class constructor with super():
        super().__init__(str)
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

if __name__ == "__main__":
    x = Simple2("Simple2 constructor argument")
    x.display()
    x.show()
    x.show_twice()  # Inherited from Simple
    def f(obj): obj.show() # Local/nested function
    f(x)
    f(Different())
```

`Simple2` inherits from `Simple`.
In the constructor, the base-class constructor is called with `super().__init__()`.
In `display()`, `show()` can be called as a method of `self`.
When you override a method but still want the base-class version,
call it through `super()`, as the overridden `show()` does.
The `@override` decorator on `show()` is explained in the next section.

`__main__` demonstrates that the base-class constructor is called.
You can also see that the inherited `show_twice()` method is available in the derived class.

The class `Different` also has a method named `show()`,
but this class is not derived from `Simple`.
The `f()` method defined in `__main__` demonstrates dynamic typing:
all it cares about is that `show()` can be applied to `obj`,
with no other type requirements.
Thus, `f()` can be applied equally to an object of a class derived from `Simple` and one that isn't,
as long as the `obj` argument has a `show()`.

## Marking Overrides with `@override`

When you override a method, nothing requires the name to match a method in the base class.
A typo, or a base method that someone later renames or removes,
silently produces a *new* method instead of an override.
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
```

A type checker now verifies the claim.
If `Derived.show` does not actually override a method in a base class,
because the name is misspelled or the base method is gone,
the checker reports an error.
This is the same kind of safety that Java's `@Override` annotation provides.

At runtime `@override` does nothing but return the method unchanged,
so it provides a free validation that you've overridden the method correctly.

Apply `@override` to any method that replaces an inherited method,
except constructors which are undecorated by convention.

## Properties

Python lets you expose a plain attribute and convert it to a computed one later,
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
print(c.radius)  # 10
print(c.area)    # 314.159: Properties don't use parentheses
```

Because the change is invisible at the call site,
do not preemptively add getters and setters in advance.
You can always add them later when you discover you need the logic.

The default `@property` is *read-only*: it is only a getter.
Assigning to it raises an `AttributeError`.
To allow writing, add a *setter*,
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
print(c.radius)   # 5
```

The getter and setter are independent,
so you choose the access you want by defining one or both.
A write-only property is possible but rare:
a plain method is a better expression of the intent.

## String Representation

Two special methods control the way an object displays.
`__str__` is the readable form for users,
and `__repr__` is the unambiguous form for developers:

```python
# representation.py

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(p)       # Point(3, 4): falls back to __repr__
print([p, p])  # [Point(3, 4), Point(3, 4)]
```

Define `__repr__` on classes you debug.

## Static and Class Methods

A method that ignores `self` can be a `@staticmethod`.
One that needs the class rather than an instance can be a `@classmethod`,
which receives the class as its first argument, conventionally named `cls`:

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
print(round(t.celsius))             # 100
print(Temperature.is_freezing(-4))  # True
```

For classes that are primarily a bundle of typed data,
the [Data Classes as Types](10_Data_Classes_as_Types.md) chapter shows a much shorter path that writes the constructor and `__repr__` for you.

## Composing Methods with `import`

You can compose classes using `import`.
This method can then be reused by multiple classes:

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
```

Because `f` is now an ordinary method, its first parameter is `self`,
the `Compose` instance.
The output shows it displaying that object:

    utility.f() called on Compose('example')
