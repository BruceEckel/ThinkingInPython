# Classes

> Data and the operations on it belong together,
> and a class binds them under one name.

You start with the `class` keyword followed by the class name and a colon.
Use `def` to create methods inside the indented class body:

```python
# simple_class.py

class Simple:
    def __init__(self, text):
        print("Inside the Simple constructor")
        self.text = text
    def show(self, msg=""):
        if msg:
            print(f"{msg}:", self.text)
        else:
            print(self.text)
    def show_twice(self):
        self.show()
        self.show()
```

```python
# demo_simple_class.py
from simple_class import Simple

x = Simple("Constructor argument")
#: Inside the Simple constructor
x.show()
#: Constructor argument
x.show("A message")
#: A message: Constructor argument
x.show_twice()
#: Constructor argument
#: Constructor argument
```

The first method of `Simple`, `__init__()`, is the *initializer*.
The double underscores on both ends make it a dunder
([Tour](02_Foundations--Tour.md#booleans-none-and-truthiness) introduces the term),
a method the language calls for you.
The `__new__()` method is the constructor, which you rarely use
([*Singleton*](23_Patterns--Singleton.md) shows a case that needs it).
Most programmers call `__init__()` the *constructor*,
since it sets up the new object's attributes,
as a constructor does in other OOP languages.
This book follows that practice.

Python calls the constructor automatically when it creates an object.
In the demo, `Simple("Constructor argument")` creates an object with what looks like a call to a function named after the class.

Ordinary methods require a reference to the current object.
When you define a method, you write the reference as the first parameter.
Python programmers traditionally name the reference `self`,
but you can use any identifier (though anything else probably confuses people).
To refer to the object's attributes or its other methods,
you must go through `self`.
Here `show()` leaves the parameter out:

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
A method defined without `self` has no parameter to receive the reference.
The "1" in the error message counts that reference.
A type checker reports the mistake before anything runs,
so the call carries a `# type: ignore` to say the mistake is deliberate.

In C++ or Java you declare object-level fields inside the class body but outside the methods.
In Python an object attribute exists once a method assigns to it through `self`
(typically in the constructor, though any method can do it).
The attributes an object carries therefore depend on which of its methods have run.
If you assign to a name in the class body, C++/Java style,
that name becomes a class-level attribute
(similar to a static field in C++/Java).

A bare annotation with no value looks most like a C++ or Java field declaration,
yet it creates neither kind of attribute.
It records the type.
[Class Attributes](09_Foundations--Class_Attributes.md#a-bare-annotation-declares-it-does-not-create)
and [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#comparing-ordinary-classes-and-data-classes)
use bare annotations.

`display_object()` is a small inspection helper built in [Metaprogramming](17_Techniques--Metaprogramming.md#building-display_object).
The helper shows the shape of an object by printing its attributes and methods:

```python
# display_simple.py
from display import display_object
from simple_class import Simple

x = Simple("Constructor argument")
#: Inside the Simple constructor
display_object(x)
#: [Attributes]
#:   • text = 'Constructor argument'
#: [Methods]
#:   • show(self, msg='')
#:   • show_twice(self)
```

The instance carries one attribute, `text`,
while the two methods belong to the class.
Because the constructor `__init__()` is a dunder,
`display_object()` hides it by default.

## Inheritance

With inheritance in C++ or Java,
you often inherit to establish a common interface.
Python is different.
Because Python is dynamically typed,
it applies an operation to an object without checking an interface first.
You therefore inherit an implementation, to reuse the code from the base class.
To name an interface,
Python uses a [`Protocol`](08_Foundations--Static_Types.md#structural-typing-with-protocols),
which lists the methods and attributes a function needs.
A class matches a protocol by defining them, whatever it inherits.

First import the base class the same way you import [any name from a module](06_Foundations--Modules_and_Packages.md#importing-names-with-from-and-as).
Then inherit by listing the base class in parentheses after the name of the inheriting class.
Python supports multiple inheritance, so you can list several classes.
[Rethinking Objects](20_Patterns--Rethinking_Objects.md#one-class-many-protocols)
argues against multiple inheritance in favor of protocols.
Here `Derived` subclasses `Simple`, imported from the `simple_class` module.
Ignore the [`@override` decorator](#marking-overrides-with-override) for now.

```python
# simple_subclass.py
from typing import override
from simple_class import Simple

class Derived(Simple):
    def __init__(self, text):
        print("Inside Derived constructor")
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
```

```python
# demo_subclass.py
from simple_subclass import Derived

x = Derived("Derived constructor argument")
#: Inside Derived constructor
#: Inside the Simple constructor
x.display()
#: Overridden show() method
#: Called from display(): Derived constructor argument
x.show_twice()  # Inherited from Simple
#: Overridden show() method
#: Derived constructor argument
#: Overridden show() method
#: Derived constructor argument
```

When you override a method but still want the base-class version,
call it through `super()`, as `Derived`'s `show()` does.

`Derived` inherits `show_twice()` from `Simple` unchanged,
yet each `self.show()` inside it runs `Derived`'s override.
The lookup starts at the class of the object,
not at the class that defines the calling method,
so base-class code reaches a method the subclass replaced.

`f()` demonstrates dynamic typing.
The class `Different` also has a method named `show()`,
but does not derive from `Simple`:

```python
# any_show.py
from simple_subclass import Derived

class Different:
    def show(self):
        print("Not derived from Simple")

def f(obj):  # Works on any obj with a show()
    obj.show()

f(Derived("Derived constructor argument"))
#: Inside Derived constructor
#: Inside the Simple constructor
#: Overridden show() method
#: Derived constructor argument
f(Different())
#: Not derived from Simple
```

An `import` inside a class body binds the imported name like any other assignment,
so importing a module-level function there makes it a method of the class.
A call through an instance then passes `self` as the function's first argument.
More than one unrelated class can import the same function this way,
but that import trick is a curiosity more than a technique.
A helper object or a module-level function is almost always clearer.

### Method Resolution Order

`super()` and ordinary attribute lookup both follow one list,
the class's *method resolution order* (MRO).
The MRO lists the classes Python searches for a name,
starting with the class and ending at `object`.
`Derived.__mro__` is `(Derived, Simple, object)`.
`super()` searches the same list,
starting with the class after the one whose method calls `super()`,
so `super().show(msg)` in `Derived` reaches `Simple`'s `show()`.

With a single base class, as in `Derived`, the order is obvious.
Python builds the list with *C3 linearization*,
which also decides the order when two base classes share an ancestor
([Rethinking Objects](20_Patterns--Rethinking_Objects.md#one-class-many-protocols) returns to that case).
When two base classes define the same name,
the MRO decides which one supplies it.
Here, `A` and `B` both define `show()`, and `C` inherits from both:

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

The bases appear in the order the `class` statement lists them.
Writing `class C(B, A)` puts `B` first.
`C().show()` then runs `B`'s version.

### Calling the Base Constructor

The base-class constructor runs because `Derived`'s constructor calls it.
C++ and Java call the base-class constructor automatically,
but when a Python class defines its own constructor,
Python runs that constructor alone.
`Broken`'s constructor leaves out the `super().__init__(text)` line,
so `show()` raises an `AttributeError` when it reads `self.text`:

```python
# missing_super.py
from exceptions import expect
from simple_class import Simple

class Broken(Simple):
    def __init__(self, text):
        pass  # Forgot super().__init__(text)

expect(AttributeError, Broken("ignored").show)
#: [AttributeError] 'Broken' object has no attribute 'text'
```

If a derived class defines no constructor,
Python runs the constructor the derived class inherits from the base class.

## Marking Overrides with `@override`

Python accepts any method name in a subclass.
If you misspell the name of a method you mean to override,
you define a new method.
Python accepts the new method.
Renaming or removing the base method later orphans the subclass method.
Python accepts the orphaned method too.
Either bug is easy to miss.

To let the type checker report either bug,
the `typing` module provides the `@override` decorator.
A line starting with `@` above a definition applies a [*decorator*](14_Techniques--Decorators.md)
to it.
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

A type checker now verifies that declaration.
The checker reports an error when a decorated method is an orphan,
whether from a misspelling or from a base method someone has since renamed or removed.
With the decorator above `shwo()` uncommented, the type checker (`ty`) reports:

```text
error[invalid-explicit-override]: Method `shwo` is decorated with
`@override` but does not override anything
```

Python runs the program either way.
Reporting the mistake takes a separate tool.
[Static Types](08_Foundations--Static_Types.md#the-type-checker-ty)
sets that tool up.

At run time `@override` returns the same function object it received.
Before returning the function,
the decorator tries to set an `__override__` attribute on it,
so that code can find overrides by introspection.
On an object that rejects the new attribute,
such as one with `__slots__` or a built-in class,
that assignment raises an `AttributeError` or a `TypeError`,
which the decorator catches and ignores.

Apply `@override` to any method that replaces an inherited method.
This book makes two exceptions: constructors,
and dunders such as `__repr__()` and `__str__()` that replace a default inherited from `object`.

## Properties

With `@property`, you can start with a plain attribute and convert it to a computed one later.
The calling code stays as it was:

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

Writing `c.area()` reads the property and then calls the `float` it produced,
which raises a `TypeError`.

### Adding a Setter

A `@property` with a getter alone rejects writes.
Assigning to it raises an `AttributeError`.
A *setter* enables writing,
and it is the place to validate the value before storing it:

```python
# property_setter.py
from exceptions import expect

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
expect(ValueError, Circle, -1)
#: [ValueError] radius cannot be negative
```

`property_setter.py` completes the conversion.
`radius` began as a plain attribute and is now a validated property.
Because code outside the class reads both versions the same way,
you can wait to convert an attribute into a property until you need the validation.

The decorators combine the two methods named `radius` into one property.
`@property` turns the getter into a property object and binds it to the name `radius` in the class body.
`@radius.setter` reads that object,
and its `setter()` method returns a new property holding both the getter and the setter.
Python binds that new property to `radius`, the name of the setter's `def`.
`@radius.setter` needs the property the getter created,
so the getter comes first.

The setter's `def` must also use the name `radius`.
Under another name, such as `def set_radius(self, value)`,
the new property binds to `set_radius`, while `radius` keeps the getter alone.
The assignment in the constructor then raises an `AttributeError` reporting that the property `radius` has no setter.

Because the class binds the name `radius` to the property,
the value goes into a separate attribute, `_radius`.
A single leading underscore marks `_radius` as internal to the class,
a convention rather than a language rule.

The separate name keeps each method from calling itself.
Inside the getter, `self.radius` calls the getter again.
Inside the setter, `self.radius = value` calls the setter again.
Either loop repeats until the interpreter raises a `RecursionError`.
Naming both the property and the backing attribute `radius` reproduces the `RecursionError`:

```python
# property_recursion.py
from exceptions import expect

class Circle:
    def __init__(self, radius):
        self.radius = radius  # Calls the setter

    @property
    def radius(self):
        return self.radius  # Calls itself again

    @radius.setter
    def radius(self, value):
        self.radius = value  # Calls itself again

expect(RecursionError, Circle, 10)
#: [RecursionError] maximum recursion depth exceeded
```

`property(fset=...)` builds a write-only property,
the reverse of a getter-only one, but write-only properties are rare.
Reading one raises an `AttributeError` reporting that the property has no getter.
A class that needs a write-only value usually takes it through a method instead.
The write is then a call, and no attribute exists to read back.

### Caching with `cached_property` {#cached-property}

A `@property` reruns its code on every access.
When the computation is slow and its answer stays the same,
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

`total` is *lazily initialized*, created on first use,
so the method runs at the first read rather than when the constructor runs.

`cached_property` stores the value in the instance's [`__dict__`](09_Foundations--Class_Attributes.md#two-dictionaries-one-lookup),
the dictionary that holds the instance's attributes.
A `@property` takes precedence over that dictionary for its name,
but the dictionary takes precedence over a `cached_property`.
A later `n.total` checks the instance first and returns the stored value before the lookup reaches the method in the class.

When a class and all its base classes declare `__slots__`,
its instances have no `__dict__` to hold the cached value.
The first read of a `cached_property` then raises a `TypeError`
([Performance](18_Techniques--Performance.md#when-slots-does-not-fit) shows the failure).
Adding a `"__dict__"` entry to `__slots__` restores the dictionary,
so `cached_property` works again.
That entry also gives every instance the per-instance dictionary that slots exist to remove.

Because `cached_property` keeps returning the stored value,
`total` becomes stale when `n.values` changes.
`del n.total` removes the stored value from `__dict__`.
Because a plain `@property` recomputes every time, its answer is always current.
Cache only answers whose inputs stay the same.

## String Representation

By default, printing an object shows its class and its address,
as in `<__main__.Point object at 0x7f2dd669cd70>`.
That display identifies the object, not the value it holds.
Two dunder methods control how an object displays.
`__str__()` is the readable form for users,
while `__repr__()` is the unambiguous form for developers:

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

`print()` and `str()` use `__str__()` when it exists and otherwise fall back to `__repr__()`.
The fallback runs in one direction.
`repr()` calls `__repr__()` in every case.
A container builds its display from the `__repr__()` of its elements,
so the list prints `Point(3, 4)` rather than `(3, 4)`.
In an f-string, `{p!r}` selects `__repr__()` and `{p!s}` selects `__str__()`.
A bare `{p}` also selects `__str__()` for a class that inherits `__format__()` from `object`.

By convention `__repr__()` returns the text of a call that rebuilds the object,
so it reads `Point(3, 4)`.
Define `__repr__()` on classes you debug,
and add `__str__()` only when users see the output.

For classes that are primarily a bundle of typed data,
[Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#data-classes)
shows how `@dataclass` writes the constructor and `__repr__()`.

## Static and Class Methods

A method that doesn't use `self` can be a `@staticmethod`.
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
    def from_fahrenheit(cls, fahrenheit):
        return cls((fahrenheit - 32) * 5 / 9)

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
so the alternative constructor returns an instance of that subclass.
Writing `return Temperature(...)` hard-codes the class.
`Reading.from_fahrenheit()` then returns a `Temperature`.

`is_freezing()` also works as a module-level function,
and that is the usual choice.
Its result depends on its `celsius` argument alone.
Make it a `@staticmethod` when it belongs with the class's interface,
where a reader looks for it,
or when a subclass should be able to replace it like any other method.

## Exercises

Try each exercise before opening its [solution](../Solutions/07_Foundations--Classes/).

1.  Add a method `shrink(self, factor)` to `Circle` in `property_setter.py` that sets `self.radius = self.radius / factor`,
    going through the existing setter.
    Confirm `shrink(2)` on a `Circle(10)` leaves the radius at `5.0`.
    Then call `shrink(-2)` on that same circle,
    which would divide the radius down to `-2.5`,
    and confirm the setter raises its `ValueError` instead of silently storing a negative radius.
2.  In `class_methods.py`, add a second alternative constructor,
    `from_kelvin(cls, kelvin)`, using `celsius = kelvin - 273.15`.
    Add a call that builds a `Temperature` both ways for the same physical temperature and confirms they agree,
    within rounding.
3.  In `simple_subclass.py`, add a third class, `MoreDerived(Derived)`,
    that overrides `show()` again,
    printing its own message before calling `super().show(msg)`.
    Predict, then confirm,
    the full chain of prints from `MoreDerived("x").show_twice()`.
4.  Add a `@cached_property` called `average` to `Numbers` in `cached_property_demo.py` that returns `self.total / len(self.values)`.
    Access `n.total` and then `n.average`,
    and confirm `average` reads the cached `total` instead of recomputing it.
5.  Give `Temperature` in `class_methods.py` a `__repr__()` that returns `Temperature(21.0)` for a temperature of 21 degrees Celsius.
    Print a single `Temperature` and a list of two of them,
    and confirm the list shows the same form for each element.
    Then add a `__str__()` returning `21.0C` and confirm which of the two `print()` uses for each case.
6.  In `override_intro.py`, rename `Base.show()` to `display()`,
    leaving `Derived.show()` and its `@override` as they are.
    Run the program and confirm it still prints `Derived.show`,
    then run the type checker
    ([Static Types](08_Foundations--Static_Types.md#the-type-checker-ty) sets one up)
    and read what it reports.
    Remove `@override` and confirm the program runs the same way while the type checker prints `All checks passed!`.
