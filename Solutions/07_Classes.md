# Classes: Solutions

## 1. `shrink()` still goes through the setter's validation

```python
# exercise_1.py
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
try:
    c.shrink(-2)
except ValueError as e:
    print("caught:", e)
#: caught: radius cannot be negative
```

`shrink()` never touches `self._radius` directly. It assigns to
`self.radius`, which still goes through `@radius.setter`, so the
existing validation applies automatically to every new way of changing
the radius, present or future. `shrink(-2)` runs after `shrink(2)` has already
brought the radius to `5.0`, so it computes `5.0 / -2 == -2.5` and the
setter rejects that, exactly as if you had written `c.radius = -2.5` by
hand.

## 2. A second alternative constructor, `from_kelvin()`

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

212°F, 373.15 K, and 100°C are the same temperature (water's boiling
point), so both alternative constructors agree once each result is
rounded to hide floating-point noise. Both classmethods end with
`return cls(...)`, so `Temperature.from_kelvin` builds a `Temperature`
exactly like `from_fahrenheit` does, only with a different formula for
`celsius`.

## 3. A third override in the chain, `Simple3`

```python
# exercise_3.py
from typing import override

class Simple:
    def __init__(self, text):
        self.s = text

    def show(self, msg=""):
        if msg:
            print(msg + ":", self.s)
        else:
            print(self.s)

    def show_twice(self):
        self.show()
        self.show()

class Simple2(Simple):
    @override
    def show(self, msg=""):
        print("Overridden show() method")
        super().show(msg)

class Simple3(Simple2):
    @override
    def show(self, msg=""):
        print("Simple3 show() method")
        super().show(msg)

Simple3("x").show_twice()
#: Simple3 show() method
#: Overridden show() method
#: x
#: Simple3 show() method
#: Overridden show() method
#: x
```

This solution strips the constructor `print()` calls from
`simple2.py`, so the trace shows only the `show()` chain. If you add
`Simple3` to `simple2.py` itself, the two constructor lines print
first.

`show_twice()` is inherited unchanged from `Simple`, and it calls
`self.show()` twice. Because `self` is a `Simple3`, each call resolves
to `Simple3.show()` first (Python always starts from the most derived
class), which prints its own message, then calls `super().show(msg)`,
running `Simple2.show()`, which prints its message and calls
`super().show(msg)` again, running `Simple.show()`, which finally
prints `x`. Each `super()` call hands off to the next class up the
chain, so the messages appear in derived-to-base order, twice.

## 4. A second `cached_property` that reads the first

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

Accessing `n.total` first runs its body once, prints the `"summing"`
message, and stores `30` on the instance. When `average`'s body then
reads `self.total`, it hits that stored value directly. No second
`"summing"` message appears, because `total` was already computed and
cached before `average` ever asked for it. If `average` is accessed
first, its own body triggers `total`'s computation the same way,
just on first use instead of in advance.

## 5. `__repr__()` and `__str__()` on `Temperature`

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

With only `__repr__()` defined, both lines show
`Temperature(21.0)`: `print()` finds no `__str__()` and falls back.
Adding `__str__()` splits them. `print(t)` and `f"{t}"` take the
readable form, while the list keeps showing `Temperature(21.0)` for
each element, because a container formats its elements with `repr()`
and never with `str()`. `{t!r}` asks for the same developer form
inside an f-string.

The two forms answer different questions. `Temperature(21.0)` says
what would rebuild this object, which is what you want in a traceback
or a debugger. `21.0C` says what the value means, which is what you
want in output a user reads.

## 6. A misspelled override, with and without the decorator

```python
# exercise_6.py

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    # @override  # Uncomment this and the import to see it complain
    def shwo(self):
        print("Derived.shwo")

Derived().show()
#: Base.show
```

The program prints `Base.show`. Nothing overrode anything: `shwo()` is
a new method that happens to sit in a subclass, and `show()` resolves
up the chain to `Base` as it always would. Python has no opinion about
whether a subclass method was meant to replace one, so the misspelling
is not an error, it is a third method nobody calls.

Add `from typing import override`, uncomment the decorator,
and the program still prints `Base.show`,
because the decorator adds no wrapper and changes no behavior. The
checker is where the difference shows:

```text
error[invalid-explicit-override]: Method `shwo` is decorated with
`@override` but does not override anything
info: No `shwo` definitions were found on any superclasses of `Derived`
```

Remove the decorator again and the checker goes quiet, while the
program's behavior never changed at any point in the exercise. That is
the whole shape of the feature: `@override` states an intention, the
checker verifies it, and the runtime is indifferent.

The value is in what it catches later. The typo is easy to spot in six
lines; the same failure arrives silently when someone renames or
deletes `Base.show` a year from now, and every `@override` in the
codebase turns that rename into a list of exact locations to fix. A
decorator that does nothing at runtime is worth writing when a tool
reads it.
