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
the radius, present or future. `shrink(-2)` computes `10 / -2 == -5.0`
and the setter rejects it, exactly as if you had written
`c.radius = -5.0` by hand.

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
cached before `average` ever asked for it. Had `average` been accessed
first, its own body would trigger `total`'s computation the same way,
just on first use instead of in advance.
