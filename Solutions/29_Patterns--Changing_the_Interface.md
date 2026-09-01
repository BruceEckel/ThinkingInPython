# Changing the Interface: Solutions

## 1. A dict-style lookup over a list of pairs

```python
# exercise_1.py
from typing import Any

class PairsAdapter:
    ("Gives a list of (key, value) pairs"
     " a dict-style lookup.")
    def __init__(
        self, pairs: list[tuple[str, Any]]
    ) -> None:
        self._pairs = pairs

    def __getitem__(self, key: str) -> Any:
        for k, v in self._pairs:
            if k == key:
                return v
        raise KeyError(key)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._pairs, name)

pairs = [("name", "Alice"), ("age", 30)]
adapter = PairsAdapter(pairs)
print(adapter["name"], adapter["age"])
#: Alice 30
# Reaches the list
adapter.append(("city", "Crested Butte"))
print(adapter["city"])
#: Crested Butte
print(len(pairs))  # The wrapped list itself grew
#: 3
try:
    adapter["missing"]
except KeyError as e:
    print("KeyError:", e)
#: KeyError: 'missing'
```

The adapter adds the one method the caller wants, `__getitem__()`,
and forwards everything else to the wrapped list through
`__getattr__()`, the same shape as `getattr_adapter.py`.
The adapter defines no `append()`, so the lookup falls through to
the list, and both the adapter and the original `pairs` name see
the new entry.
The lookup is a linear scan.
If the pairs are many and the lookups frequent, convert to a real
`dict` once (`dict(pairs)` does it) and adapt only when the object
must keep being a list to someone else.

## 2. Deprecating the class instead of the method

```python
# exercise_2.py
import warnings

@warnings.deprecated("Report is replaced by TextReport")
class Report:
    def render(self) -> str:
        return "report"

with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    report = Report()  # type: ignore
    class Detailed(Report):  # type: ignore
        pass
print(report.render())
#: report
for entry in caught:
    print(entry.category.__name__, entry.message)
#: DeprecationWarning Report is replaced by TextReport
#: DeprecationWarning Report is replaced by TextReport
```

Decorating the class moves the warning to the two places where a
caller commits to the type: constructing an instance and subclassing.
`render()` runs outside the recording block and adds nothing to
`caught`, so code that already holds a `Report` runs without a word.
That is the right split: `TextReport` replaces the type, not the
method. A caller who wants to act on the warning must change where
the object comes from, not where they call it.

`ty` reports both lines, so both carry `# type: ignore`. The
subclass warning fires at class-creation time, so it arrives on
import rather than on any call. A library that subclasses a
deprecated class emits the warning as soon as Python imports that
library.

## 3. `facade.py` as a module

```python
# shop.py
from dataclasses import dataclass

@dataclass(frozen=True)
class _A:
    x: object

@dataclass(frozen=True)
class _B:
    x: object

def make_a(x: object) -> _A:
    return _A(x)

def make_b(x: object) -> _B:
    return _B(x)
```

```python
# exercise_3.py
import shop
from shop import make_a, make_b

print(make_a(1), make_b(2))
#: _A(x=1) _B(x=2)
print([name for name in vars(shop)
       if not name.startswith("_")])
#: ['dataclass', 'make_a', 'make_b']
```

The caller sees two functions. `shop._A` and `shop._B` still reach
the classes, because Python enforces nothing. The underscore marks
them as private, and `from shop import *` skips them. The listing
prints the module's public names to make that concrete. `dataclass`
appears because an import binds a name in the module too. A real
module therefore either sets
[`__all__`](../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
or imports as `import dataclasses` and writes `@dataclasses.dataclass`.

The class version differs in one way that matters. `Facade` is a
namespace the language does not treat as one: `Facade.make_a` and
`shop.make_a` read identically at the call site, but you must define
the class, import it, and carry it around. `@staticmethod` exists
only to stop Python passing `self` to functions that never wanted it.
The module was already a namespace before anyone asked, and it comes
with the underscore convention, `__all__`, and one-time initialization
built in.

A caller sees nearly the same names in both versions, and that is
the point worth taking away. Neither version enforces anything. The
difference is how much ceremony you pay to express the same intent,
and the module version pays none.

## 4. Classifying three wrappers

**The logging wrapper is a Decorator.** Its interface is the wrapped
object's, unchanged, and it adds behavior on the way through. Remove
it and every call still reaches the same method with the same
arguments and returns the same result. What you lose is the log. That
is the Decorator row: same interface, added behavior, and the behavior
is what disappears.

**The `read()` wrapper is an Adapter.** Its interface is not the
wrapped object's. The caller asks for `read()`, and the wrapped
object offers only `next_chunk()`, so the wrapper exists to make one
type fit a caller that expects another. Remove it and you lose only
the fit, which is enough: the call no longer resolves. An Adapter
adds no behavior, and that is the test that separates the Adapter
from the Decorator. Both wrappers forward, and only this one changes
the name the caller uses.

**The flag-checking wrapper is a Proxy.** Its interface is the wrapped
object's, and it adds no behavior to a call that goes through. What it
adds is a decision about whether the call goes through at all. Remove
it and every call reaches the implementation, including the ones the
proxy should have refused, so what you lose is control over when and
whether the call happens. This wrapper is the
[protection proxy](../Chapters/26_Patterns--Surrogate.md#what-proxy-solves).

None of the three is a Façade, because a Façade narrows many objects
to a few names and each of these wraps one object. The lesson is that
the classification never turns on the code: all three could be the
same `__getattr__()` forwarder. What separates them is the answer to
"what breaks if I delete this," and a name chosen from that answer
tells the next reader why the wrapper is there.
