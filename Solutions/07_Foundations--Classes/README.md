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

[Adding a Setter](../../Chapters/07_Foundations--Classes.md#adding-a-setter)
shows the `@radius.setter` that validates every assignment to `radius`.
Write `shrink()` so it assigns to the public `radius` property instead of the underscore attribute.
The setter then runs on the computed value.
`expect()` catches the setter's `ValueError`.

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
<summary>Done when</summary>

your `Circle(10)` prints `5.0` after `shrink(2)`,
and `shrink(-2)` on that same circle raises the setter's `ValueError`,
`radius cannot be negative`.
Reading `radius` after the failed call still gives `5.0`.

<details>
<summary>Solution</summary>

If you write `shrink()` to assign `self._radius`,
the assignment bypasses the setter.
`shrink(-2)` then stores `-2.5`.
`expect()` fails with `AssertionError: no exception raised`.
The solution assigns to `self.radius`,
so the setter checks every change to the radius.

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

**Route the change through the setter.**
Because `shrink()` assigns to `self.radius` rather than `self._radius`,
the assignment calls the `@radius.setter` method.
The existing validation then applies to every method that changes the radius this way.

**Confirm the setter rejects a negative result.**
The setter rejects the computed `-2.5`,
just as it rejects a direct `c.radius = -2.5`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A second alternative constructor, `from_kelvin()`

> In `class_methods.py`, add a second alternative constructor,
> `from_kelvin(cls, kelvin)`, using `celsius = kelvin - 273.15`.
> Add a call that builds a `Temperature` both ways for the same physical temperature and confirms they agree,
> within rounding.

<details>
<summary>Where to look</summary>

[Static and Class Methods](../../Chapters/07_Foundations--Classes.md#static-and-class-methods)
shows `from_fahrenheit()` as a `@classmethod` that converts its argument and returns `cls(...)`.
Write `from_kelvin()` the same way with the formula from the exercise.
Compare the two results with `round()`,
since floating-point arithmetic can be off in the last digit.
`310.0 - 273.15` gives `36.85000000000002`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
class Temperature:
    def __init__(self, celsius):
        ...

    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        ...

    @classmethod
    def from_kelvin(cls, kelvin):
        ...

    @staticmethod
    def is_freezing(celsius):
        ...
```

<details>
<summary>Done when</summary>

`Temperature.from_fahrenheit(212)` and `Temperature.from_kelvin(373.15)` both print `100.0` when you round each `celsius` to two places.
A second pair, `from_fahrenheit(80.6)` and `from_kelvin(300.15)`,
prints `27.0` both ways after rounding, though the unrounded values differ.

<details>
<summary>Solution</summary>

```python
# exercise_2.py

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @classmethod
    def from_fahrenheit(cls, fahrenheit):
        return cls((fahrenheit - 32) * 5 / 9)

    @classmethod
    def from_kelvin(cls, kelvin):
        return cls(kelvin - 273.15)

    @staticmethod
    def is_freezing(celsius):
        return celsius <= 0

t1 = Temperature.from_fahrenheit(212)
t2 = Temperature.from_kelvin(373.15)
print(round(t1.celsius, 2), round(t2.celsius, 2))
#: 100.0 100.0
```

**Compare the results within rounding.**
212°F, 373.15 K, and 100°C are the same temperature (water's boiling point),
so both alternative constructors produce `100.0`.
The exercise asks for agreement within rounding,
so the `print()` call passes each `celsius` through `round()`.
For these inputs the unrounded values compare equal,
but other inputs produce a floating-point rounding error.
`from_kelvin(300.15)` stores `27.0`, while `from_fahrenheit(80.6)`,
the same temperature, stores `26.999999999999996`.
Rounded to two places, both print `27.0`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[Inheritance](../../Chapters/07_Foundations--Classes.md#inheritance)
shows `Derived.show()` printing a message and then calling `super().show(msg)`.
Give `MoreDerived` a `show()` with the same shape and its own message.
`MoreDerived` inherits `show_twice()`, which calls `self.show()`,
so the lookup starts at the class of `self`.
Each `super()` call then runs the base class's `show()`.

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
<summary>Done when</summary>

`MoreDerived("x").show_twice()` prints `MoreDerived show() method`,
`Overridden show() method`, and `x`, then the same three lines again,
and the run matches the prediction you wrote first.
In `simple_subclass.py` the two constructor lines print ahead of those six.

<details>
<summary>Solution</summary>

If you leave `super().show(msg)` out of `MoreDerived.show()`,
the chain stops at `MoreDerived`.
`show_twice()` then prints two lines, both `MoreDerived show() method`.
Python runs a base-class method only when an override calls it,
the same rule [Calling the Base Constructor](../../Chapters/07_Foundations--Classes.md#calling-the-base-constructor)
shows for `__init__()`.
Each override in the solution therefore calls its base-class method with `super()`.

```python
# exercise_3.py
from typing import override

class Simple:
    def __init__(self, text):
        self.text = text

    def show(self, msg=""):
        if msg:
            print(f"{msg}:", self.text)
        else:
            print(self.text)

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

This solution copies `Simple` and `Derived` without their constructor `print()` calls and without `display()`,
so the trace shows only the `show()` chain.
If you add `MoreDerived` to `simple_subclass.py`, as the exercise says,
the two constructor lines print first.

**Dispatch on the object's class.**
The lookup for `self.show()` starts at the class of the object,
and `self` is a `MoreDerived`,
so each call resolves to `MoreDerived.show()` first.

**Pass each call up the chain.**
Each `super()` call runs the `show()` of the class one step closer to `Simple`,
so the messages appear in derived-to-base order, twice.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. A second `cached_property` that reads the first

> Add a `@cached_property` called `average` to `Numbers` in `cached_property_demo.py` that returns `self.total / len(self.values)`.
> Access `n.total` and then `n.average`,
> and confirm `average` reads the cached `total` instead of recomputing it.

<details>
<summary>Where to look</summary>

[Caching with `cached_property`](../../Chapters/07_Foundations--Classes.md#cached-property)
shows `total` computed once and then stored on the instance.
Decorate `average` with `@cached_property` and read `self.total` in its body.
Inside `average`, `self.total` is an ordinary attribute access that returns the stored value,
so the `summing` message should print once.

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
<summary>Done when</summary>

accessing `n.total` and then `n.average` on `Numbers([5, 10, 15])` prints `30` and then `10.0`,
and the `summing 3 values` line appears once in the whole run, before the `30`.

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

**Reuse the cached value.**
The `"summing"` message appears once,
because the `n.total` access computes and caches `total` before `average` reads it.
If you access `average` first,
its read of `self.total` computes and caches `total` at that moment.
`"summing"` still appears once.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
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

[String Representation](../../Chapters/07_Foundations--Classes.md#string-representation)
shows which method `print()` calls, `__repr__()` or `__str__()`,
and which one a list calls for its elements.
Define `__repr__()` first and print one object and a list,
then add `__str__()` and print both again.

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
<summary>Done when</summary>

with `__repr__()` alone,
`print(t)` and the printed list both show `Temperature(21.0)`.
After you add `__str__()`,
`print(t)` shows `21.0C` while the list keeps the `Temperature(21.0)` form for each element.

<details>
<summary>Solution</summary>

If you define `__str__()` alone, `print(t)` shows `21.0C`,
but the list shows the default `<__main__.Temperature object at 0x...>` for each element.
A container formats its elements with `repr()`,
which calls `__repr__()` and leaves `__str__()` unused.
The solution defines `__repr__()` for the form a container shows and adds `__str__()` for the readable one.

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

**Supply the fallback form.**
With `__repr__()` defined and no `__str__()`,
`print(t)` and the printed list both show `Temperature(21.0)`.
`print()` calls the `__str__()` that `Temperature` inherits from `object`,
and that method calls `__repr__()`.

**Add a readable form for users.**
Adding `__str__()` makes `print(t)` and the printed list differ.
The list keeps showing `Temperature(21.0)` for each element,
because a container formats its elements with `repr()`, not `str()`.
`{t!r}` calls `repr()`,
producing the same `Temperature(21.0)` form inside an f-string.

The two forms serve different readers.
`Temperature(21.0)` is the expression that rebuilds this object,
the form you want in a traceback or a debugger.
`21.0C` is the value with its unit, the form you want in output a user reads.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. A renamed base method, with and without the decorator

> In `override_intro.py`, rename `Base.show()` to `display()`,
> leaving `Derived.show()` and its `@override` as they are.
> Run the program and confirm it still prints `Derived.show`,
> then run the type checker
> ([Static Types](../../Chapters/08_Foundations--Static_Types.md#the-type-checker-ty) sets one up)
> and read what it reports.
> Remove `@override` and confirm the program runs the same way while the type checker prints `All checks passed!`.

<details>
<summary>Where to look</summary>

[Marking Overrides with `@override`](../../Chapters/07_Foundations--Classes.md#marking-overrides-with-override)
shows the decorator from `typing` on a method that replaces a base-class method.
The renamed base orphans `Derived.show()`.
The program never calls `display()`, so its output stays the same.
The decorator is for the type checker,
so run the checker with and without `@override` and compare.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
class Base:
    def display(self):
        ...

class Derived(Base):
    # @override  # Uncomment (and import) to see it complain
    def show(self):
        ...
```

<details>
<summary>Done when</summary>

your renamed program prints `Derived.show` at every step,
and `uv run ty check` on your file reports `invalid-explicit-override` on `Derived.show()` while `@override` is present.
With the decorator removed, `uv run ty check` prints `All checks passed!`.

<details>
<summary>Solution</summary>

```python
# exercise_6.py

class Base:
    def display(self):
        print("Base.display")

class Derived(Base):
    # @override  # Uncomment (and import) to see it complain
    def show(self):
        print("Derived.show")

Derived().show()
#: Derived.show
```

**Rename the base-class method.**
`Derived` defines `show()` itself,
so `Derived().show()` finds it there and the lookup stops before reaching `Base`.
The rename turns the override into an unrelated new method.
Python accepts any method name in a subclass and keeps no record of which ones you meant as overrides.

**Declare the intended override.**
With `from typing import override` added and the decorator uncommented,
the program still prints `Derived.show`,
because at run time the decorator returns the method it receives.
The type checker reports the mismatch:

```text
error[invalid-explicit-override]: Method `show` is decorated with
`@override` but does not override anything
info: No `show` definitions were found on any superclasses of `Derived`
```

If you remove the decorator, the type checker reports no error,
since the code no longer states an intention for it to verify.
The feature has three parts: `@override` states an intention,
the type checker verifies it, and the running program ignores it.

In a real codebase the base class and its overrides often sit in different files,
so a rename slips past a reader.
With `@override` on every overriding method,
the type checker reports each method whose name the rename removed from the base class.
A decorator that changes no behavior at run time is worth writing when a tool reads it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
