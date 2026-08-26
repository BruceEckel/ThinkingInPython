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
but you can use any identifier
(however, anything other than `self` probably confuses people).
To refer to the object's fields or its other methods,
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
The "1" in the error message is that reference;
a method that omits `self` cannot receive it.
A type checker sees the mistake without running anything,
which is why the call carries a `# type: ignore` saying it is deliberate.

The first method, `__init__()`, is the *initializer*.
The double underscores (a.k.a. "dunder") indicate a special name.
The `__new__()` method is the *constructor*, which you rarely use
([Singleton](24_Singleton.md) shows a case that needs it).
Most programmers call `__init__()` the constructor,
since it does the job of constructors in other OOP languages.
This book follows that practice.

Python calls the constructor automatically during object creation.
In the demo, creating an object looks like calling a function named after the class.

In C++ or Java you declare object-level fields inside the class body but outside of the methods.
You do not declare them this way in Python.
To create an object field, you name it, using `self`, inside a method
(typically in the constructor, but not always).
The assignment creates space for that field when the method runs.
If you assign to a name in the class body, C++/Java style,
that name becomes a class-level field instead
(similar to a static field in C++/Java).
[Class Attributes](09_Class_Attributes.md)
shows what that shared storage does when you assign to it.
A bare annotation with no value,
the form that looks most like a C++ or Java field declaration, does neither:
it stores nothing and only records the type.
[Class Attributes](09_Class_Attributes.md#declaring-shared-state-with-classvar)
and [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes) use it.

`display_object()`, a small inspection helper built in [Metaprogramming](17_Metaprogramming.md#building-display_object),
shows the shape of an object.
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
Python does have a way to name an interface without inheritance,
the `Protocol` in [Static Typing](08_Static_Typing.md),
which describes the shape a function needs instead of demanding a base class.

First import the base class the same way you import any name from a module
(see [Modules and Packages](06_Modules_and_Packages.md)).
Then inherit by listing the class
(or classes, since Python supports multiple inheritance, which [Rethinking Objects](20_Rethinking_Objects.md) argues against in favor of protocols)
in parentheses after the name of the inheriting class.
This example imports and subclasses `Simple`, from the `simple_class` module.
Ignore the `@override` decorator for now;
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

The base-class constructor runs,
but only because `Simple2`'s constructor calls it.
Unlike C++ and Java, Python never calls a base-class constructor automatically.
If you remove the `super().__init__(text)` line, nothing creates `self.s`,
so the first method that reads it raises an `AttributeError`.
A derived class that defines no constructor of its own inherits and runs the base version.
The derived class also inherits `show_twice()` unchanged.

The class `Different` also has a method named `show()`,
but this class does not derive from `Simple`.
The `f()` function in the demo demonstrates dynamic typing.
All it cares about is that it can call `show()` on `obj`,
with no other type requirements.
Thus, `f()` works equally on an object of a class derived from `Simple` and one that isn't,
as long as the `obj` argument has a `show()`.

## Composing Methods with `import`

You can compose methods into a class using `import`.
More than one class can reuse a method defined this way:

```python
# utility.py

def f(self):
    print(f"utility.f() called on {self.name}")
```

This example composes that method into two unrelated classes:

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
This is a curiosity more than a technique.
It works because `import` inside a class body binds like any other assignment,
but a helper object or a module-level function is almost always a clearer choice.

## Marking Overrides with `@override`

When you override a method,
nothing requires the name to match a method in the base class.
A typo, or a base method that someone later renames or removes,
silently produces a new method instead of an override.
This bug is easy to miss.

The `@override` decorator from the `typing` module closes that gap.
A line starting with `@` above a definition applies a *decorator* to it;
[Decorators](14_Decorators.md) shows how they work,
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

A type checker now verifies the claim.
If a decorated method does not override anything in a base class,
because you misspelled the name or the base method no longer exists,
the type checker reports an error.
If you uncomment the decorator on `Typo.shwo`, it says:

```text
error[invalid-explicit-override]: Method `shwo` is decorated with
`@override` but does not override anything
```

Python runs the program either way.
Catching the mistake takes a separate tool,
which [Static Typing](08_Static_Typing.md) sets up.

At run time `@override` adds no wrapper.
It returns the same function object,
after trying to set an `__override__` attribute on it (some callables refuse it)
so that code can find overrides by introspection.

Apply `@override` to any method that replaces an inherited method.
Two kinds stay undecorated by convention: constructors,
and dunders such as `__repr__()` and `__str__()` that replace a default inherited from `object`.

## Properties

You can expose a plain attribute and convert it to a computed one later,
without changing the calling code, using `@property`:

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
and the call site cannot tell them apart.

The default `@property` rejects writes:
assigning to it raises an `AttributeError`.
To enable writing, add a *setter*,
which lets you validate the value before storing it:

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

The section opened with a conversion, and this listing carries it out.
`radius` began as a plain attribute and is now a validated property,
and the two lines that read `c.radius` and `c.area` are the ones from the first listing,
unchanged.
Nothing outside the class can tell which version it holds,
which is why you do not add getters and setters before you need them.

The property owns the name `radius` on the class,
so the value goes into a separate attribute.
A single leading underscore marks `_radius` as internal to the class,
a convention rather than a language rule.
The name matters: reading `self.radius` inside the getter,
or assigning to it inside the setter, calls that method again, and again,
until the interpreter raises a `RecursionError`.

The getter and setter are independent,
so you choose the access you want by defining one or both.
A write-only property is possible but rare.
A plain method expresses the intent.

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
The stored value lives in the instance's `__dict__`,
so a class that suppresses that dictionary,
as [Rethinking Objects](20_Rethinking_Objects.md) does with `slots=True`,
cannot use `cached_property`.

`cached_property` trades freshness for speed, so if `n.values` changes,
`total` becomes stale, as appending `20` above shows.
A plain `@property` recomputes every time, so its answer is always current.
Cache only what cannot change.

## String Representation

By default, printing an object shows its class and its address,
as in `<__main__.Point object at 0x7f2dd669cd70>`,
which says nothing about the value the object holds.
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
print(p)  # Falls back to __repr__
#: Point(3, 4)
print([p, p])
#: [Point(3, 4), Point(3, 4)]
```

Adding `__str__()` to the same class separates the two forms:

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
The fallback runs one way only, so `repr()` never consults `__str__()`.
A container builds its own display from the `__repr__()` of its elements,
which is why the list prints `Point(3, 4)` rather than the shorter form.
In an f-string, `{p}` selects `__str__()` and `{p!r}` selects `__repr__()`.
By convention `__repr__()` returns the call that would rebuild the object,
so it reads `Point(3, 4)`.

Define `__repr__()` on classes you debug,
and add `__str__()` only when users see the output.

For classes that are primarily a bundle of typed data,
[Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)
shows how `@dataclass` writes the constructor and `__repr__()`.

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
    # An alternative constructor
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_freezing(celsius):  # Needs no self or cls
        return celsius <= 0

t = Temperature.from_fahrenheit(212)
print(round(t.celsius))
#: 100
print(Temperature.is_freezing(-4))
#: True
```

`from_fahrenheit()` builds its result with `cls(...)` rather than `Temperature(...)`.
When you call it on a subclass, `cls` is that subclass,
so the alternative constructor produces the right kind of object,
and a subclass inherits it unchanged.
Naming the class directly would hard-code `Temperature` into every subclass.

`is_freezing()` would also work as a module-level function.
Defining it in the class keeps it where a reader looks for it,
and lets a subclass replace it the way it replaces any other method.

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
    then run the type checker ([Static Typing](08_Static_Typing.md) sets one up)
    and read what it says.
    Remove `@override` and confirm the type checker goes quiet while the program's behavior does not change.
