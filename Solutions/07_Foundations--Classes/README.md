# Classes: Solutions

## 1. `shrink()` still goes through the setter's validation

> Add a method `shrink(self, factor)` to `Circle` in `property_setter.py` that sets `self.radius = self.radius / factor`,
> going through the existing setter.
> Confirm `shrink(2)` on a `Circle(10)` leaves the radius at `5.0`.
> Then call `shrink(-2)` on that same circle,
> which would divide the radius down to `-2.5`,
> and confirm the setter raises its `ValueError` instead of silently storing a negative radius.

<details>
<summary>Where to look</summary>

[Adding a Setter](../../Chapters/07_Foundations--Classes.md#adding-a-setter) shows the `@radius.setter` that validates every assignment to `radius`.
Write `shrink()` so it assigns to the public `radius` property instead of the underscore attribute.
The setter then runs on the computed value, and the test catches its `ValueError`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from exceptions import expect

class Circle:
    def __init__(self, radius):
        ...

    @property
    def radius(self):
        ...

    @radius.setter
    def radius(self, value):
        ...

    def shrink(self, factor):
        ...
```

<details>
<summary>Solution</summary>

If you write `shrink()` to assign the underscore attribute `self._radius` directly,
the setter does not run.
`shrink(-2)` then stores `-2.5` without complaint,
and `expect()` fails with `AssertionError: no exception raised`.
The solution assigns to `self.radius`,
so every change to the radius passes the setter's check.

```python
# exercise_1.py
from exceptions import expect

class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

    def shrink(self, factor):
        self.radius = self.radius / factor

c = Circle(10)
c.shrink(2)
print(c.radius)
#: 5.0
expect(ValueError, c.shrink, -2)
#: [ValueError] radius cannot be negative
```

**Route the change through the setter.** `shrink()` does not touch `self._radius`. It assigns to
`self.radius`, which goes through `@radius.setter`, so the
existing validation applies to every method that changes the radius
this way.

**Confirm the setter rejects a negative result.** `shrink(-2)` runs after `shrink(2)` has brought the radius
to `5.0`, so it computes `5.0 / -2 == -2.5` and the setter rejects
`-2.5`, the same as it rejects `c.radius = -2.5` written by hand.

</details>
</details>
</details>

## 2. A second alternative constructor, `from_kelvin()`

> In `class_methods.py`, add a second alternative constructor,
> `from_kelvin(cls, k)`, using `celsius = k - 273.15`.
> Add a call that builds a `Temperature` both ways for the same physical temperature and confirms they agree,
> within rounding.

<details>
<summary>Where to look</summary>

[Static and Class Methods](../../Chapters/07_Foundations--Classes.md#static-and-class-methods) shows `from_fahrenheit()` as a `@classmethod` that converts its argument and returns `cls(...)`.
Write `from_kelvin()` the same way with the formula from the exercise.
Compare the two results with `round()`, since floating-point arithmetic can miss by a last digit: `310.0 - 273.15` gives `36.85000000000002`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
class Temperature:
    def __init__(self, celsius):
        ...

    @classmethod
    def from_fahrenheit(cls, f):
        ...

    @classmethod
    def from_kelvin(cls, k):
        ...

    @staticmethod
    def is_freezing(celsius):
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_2.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, k):
        return cls(k - 273.15)

    @staticmethod
    def is_freezing(celsius):
        return celsius <= 0

t1 = Temperature.from_fahrenheit(212)
t2 = Temperature.from_kelvin(373.15)
print(round(t1.celsius, 2), round(t2.celsius, 2))
#: 100.0 100.0
```

**Convert, then construct.** Both class methods end with `return cls(...)`, so
`from_kelvin()` builds a `Temperature` the way `from_fahrenheit()`
does, with a different formula for `celsius`.

**Compare the results within rounding.** 212°F, 373.15 K, and 100°C are the same temperature (water's boiling
point), so both alternative constructors produce `100.0`. The exercise
asks for agreement within rounding, so the `print()` call passes each
`celsius` through `round()`.
These inputs carry no floating-point noise (the unrounded values compare equal),
but other inputs do: `from_kelvin(300.15)` stores `27.0`, while
`from_fahrenheit(80.6)`, the same temperature, stores `26.999999999999996`.
Rounded to two places, both print `27.0`.

</details>
</details>
</details>

## 3. A third override in the chain, `MoreDerived`

> In `simple_subclass.py`, add a third class, `MoreDerived(Derived)`,
> that overrides `show()` again,
> printing its own message before calling `super().show(msg)`.
> Predict, then confirm,
> the full chain of prints from `MoreDerived("x").show_twice()`.

<details>
<summary>Where to look</summary>

[Inheritance](../../Chapters/07_Foundations--Classes.md#inheritance) shows `Derived.show()` printing a message and then calling `super().show(msg)`.
Give `MoreDerived` a `show()` with the same shape and its own message.
`show_twice()` is inherited and calls `self.show()`, so the lookup starts at the class of the object and each `super()` call moves one class up.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import override

class Simple:
    def __init__(self, text):
        ...

    def show(self, msg=""):
        ...

    def show_twice(self):
        ...

class Derived(Simple):
    @override
    def show(self, msg=""):
        ...

class MoreDerived(Derived):
    @override
    def show(self, msg=""):
        ...
```

<details>
<summary>Solution</summary>

If you leave `super().show(msg)` out of `MoreDerived.show()`,
the chain stops at `MoreDerived`.
`show_twice()` then prints `MoreDerived show() method` twice,
and neither `Derived`'s message nor `x` appears.
Python calls no base-class method on its own,
as [Calling the Base Constructor](../../Chapters/07_Foundations--Classes.md#calling-the-base-constructor) shows for `__init__()`,
so each override in the solution passes the call up with `super()`.

```python
# exercise_3.py
from typing import override

class Simple:
    def __init__(self, text):
        self.s = text

    def show(self, msg=""):
        if msg:
            print(f"{msg}:", self.s)
        else:
            print(self.s)

    def show_twice(self):
        self.show()
        self.show()

class Derived(Simple):
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        super().show(msg)

class MoreDerived(Derived):
    @override
    def show(self, msg=""):
        print("MoreDerived show() method")
        super().show(msg)

MoreDerived("x").show_twice()
#: MoreDerived show() method
#: Overridden show() method
#: x
#: MoreDerived show() method
#: Overridden show() method
#: x
```

This solution copies `Simple` and `Derived` without their constructor
`print()` calls, so the trace shows only the `show()` chain. If you add
`MoreDerived` to `simple_subclass.py`, as the exercise says, the two
constructor lines print first.

**Dispatch on the object's class.** `MoreDerived` inherits `show_twice()` unchanged from `Simple`, and
`show_twice()` calls `self.show()` twice. Because `self` is a
`MoreDerived`, each call resolves to `MoreDerived.show()` first (the lookup
starts at the class of the object).

**Pass each call up the chain.** `MoreDerived.show()` prints its own
message, then calls `super().show(msg)`, which runs `Derived.show()`.
`Derived.show()` prints its message and calls `super().show(msg)`
again, which runs `Simple.show()`, and `Simple.show()` finally prints
`x`. Each `super()` call hands off to the next class up the chain, so
the messages appear in derived-to-base order, twice.

</details>
</details>
</details>

## 4. A second `cached_property` that reads the first

> Add a `@cached_property` called `average` to `Numbers` in `cached_property_demo.py` that returns `self.total / len(self.values)`.
> Access `n.total` and then `n.average`,
> and confirm `total` is not recomputed when `average` uses it.

<details>
<summary>Where to look</summary>

[Caching with `cached_property`](../../Chapters/07_Foundations--Classes.md#cached-property) shows `total` computed once and then stored on the instance.
Decorate `average` with `@cached_property` and read `self.total` in its body.
A cached property is an ordinary attribute access from inside another property, so look for the `summing` message to print only once.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from functools import cached_property

class Numbers:
    def __init__(self, values):
        ...

    @cached_property
    def total(self):
        ...

    @cached_property
    def average(self):
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from functools import cached_property

class Numbers:
    def __init__(self, values):
        self.values = values

    @cached_property
    def total(self):
        print("summing", len(self.values), "values")
        return sum(self.values)

    @cached_property
    def average(self):
        print("computing average")
        return self.total / len(self.values)

n = Numbers([5, 10, 15])
print(n.total)
#: summing 3 values
#: 30
print(n.average)
#: computing average
#: 10.0
```

**Compute on first access.** Accessing `n.total` first runs its body once, prints the `"summing"`
message, and stores `30` on the instance.

**Reuse the cached value.** `average`'s body then
reads `self.total` and gets that stored value directly. No second
`"summing"` message appears, because `total` is already computed and
cached before `average` asks for it. If you access `average`
first, its own body triggers `total`'s computation the same way,
just on first use instead of in advance.

</details>
</details>
</details>

## 5. `__repr__()` and `__str__()` on `Temperature`

> Give `Temperature` in `class_methods.py` a `__repr__()` that returns `Temperature(21.0)` for a temperature of 21 degrees Celsius.
> Print a single `Temperature` and a list of two of them,
> and confirm the list shows the same form for each element.
> Then add a `__str__()` returning `21.0C` and confirm which of the two `print()` uses for each case.

<details>
<summary>Where to look</summary>

[String Representation](../../Chapters/07_Foundations--Classes.md#string-representation) shows `print()` and a list choosing between `__repr__()` and `__str__()`.
Define `__repr__()` first and print one object and a list, then add `__str__()` and print both again.
Notice which method `print()` uses for the object and which one the list uses for its elements.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
class Temperature:
    def __init__(self, celsius):
        ...

    def __repr__(self):
        ...

    def __str__(self):
        ...
```

<details>
<summary>Solution</summary>

If you define only `__str__()`, `print(t)` shows `21.0C`,
but the list shows the default `<__main__.Temperature object at 0x...>` for each element.
A container formats its elements with `repr()`, which ignores `__str__()`.
The solution defines `__repr__()` for that form and adds `__str__()` for the readable one.

```python
# exercise_5.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius})"

    def __str__(self):
        return f"{self.celsius}C"

t = Temperature(21.0)
print(t)
#: 21.0C
print([t, Temperature(0.0)])
#: [Temperature(21.0), Temperature(0.0)]
print(f"{t} is {t!r}")
#: 21.0C is Temperature(21.0)
```

**Supply the fallback form.** With only `__repr__()` defined, `print(t)` and the printed list both
show `Temperature(21.0)`: `print()` finds no `__str__()` and falls
back to `__repr__()`.

**Add a readable form for users.** Adding `__str__()` makes the two outputs differ.
`print(t)` and `f"{t}"` take the readable form, while the list keeps
showing `Temperature(21.0)` for each element, because a container
formats its elements with `repr()` and never with `str()`. `{t!r}`
asks for the same `Temperature(21.0)` form inside an f-string.

The two forms answer different questions. `Temperature(21.0)` says
what rebuilds this object, the form you want in a traceback or a
debugger. `21.0C` says what the value means, the form you want
in output a user reads.

</details>
</details>
</details>

## 6. A misspelled override, with and without the decorator

> In `override_intro.py`, misspell `Derived`'s method as `shwo()`,
> keeping the `@override` decorator.
> Run the program and confirm it now prints `Base.show`,
> then run the type checker
> ([Static Types](../../Chapters/08_Foundations--Static_Types.md#the-type-checker-ty) sets one up)
> and read what it says.
> Remove `@override` and confirm the type checker goes quiet while the program's behavior does not change.

<details>
<summary>Where to look</summary>

[Marking Overrides with `@override`](../../Chapters/07_Foundations--Classes.md#marking-overrides-with-override) shows the decorator from `typing` on a method that replaces a base-class method.
Python compares no method names between a subclass and its base, so the misspelling creates a new method and `show()` resolves to `Base`.
The decorator is for the type checker: run it with and without `@override` and compare.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
class Base:
    def show(self):
        ...

class Derived(Base):
    # @override  # Uncomment (and import) to see it complain
    def shwo(self):
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    # @override  # Uncomment (and import) to see it complain
    def shwo(self):
        print("Derived.shwo")

Derived().show()
#: Base.show
```

**Miss the base-class method.** The program prints `Base.show`. Nothing overrides anything: `shwo()` is
a new method in the subclass, and `show()` resolves up the chain to
`Base`. Python does not check whether a subclass method was meant to
replace a base-class method, so the misspelling is not an error.
`shwo()` is a second method that nothing calls.

**Declare the intended override.** With `from typing import override` added and the decorator
uncommented, the program still prints `Base.show`,
because the decorator adds no wrapper and changes no behavior. The
type checker is where the difference shows:

```text
error[invalid-explicit-override]: Method `shwo` is decorated with
`@override` but does not override anything
info: No `shwo` definitions were found on any superclasses of `Derived`
```

Without the decorator the type checker goes quiet, and the program's
behavior is the same at every step of the exercise. The feature has
three parts: `@override` states an intention, the type checker
verifies it, and the running program ignores it.

The value of `@override` is in what the type checker catches later.
The typo is easy to spot in a listing this short. The same failure
arrives silently when someone renames or deletes `Base.show()` a year
from now. With `@override` on every overriding method in the codebase,
that rename becomes a list of locations to fix. A decorator that
does nothing at run time is worth writing when a tool reads it.

</details>
</details>
</details>
