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
`append()` is not defined on the adapter, so the lookup falls
through to the list, and the growth shows both through the adapter
and through the original name.
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
That is the right split. The method is not what was replaced, the
type is, and a caller who wants to act on the warning has to change
where the object comes from, not where it is used.

`ty` reports both lines, so both carry `# type: ignore`. The
subclass warns at class-creation time, which means it fires on
import rather than on any call, so a library that subclasses a
deprecated class hears about it as soon as it is loaded.

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

The caller sees two functions. `_A` and `_B` are still reachable
through `shop._A`, because Python enforces nothing, but the underscore
says they are not part of the deal and `from shop import *` skips
them. The listing prints the module's public names to make that
concrete. `dataclass` appears because an import binds a name in the
module too, which is why a real module either sets
[`__all__`](../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
or imports as `import dataclasses` and writes `@dataclasses.dataclass`.

The class version differs in one way that matters. `Facade` is a
namespace the language does not treat as one: `Facade.make_a` and
`shop.make_a` read identically at the call site, but the class has to
be defined, imported, and carried around, and `@staticmethod` exists
only to stop Python passing `self` to functions that never wanted it.
The module was already a namespace before anyone asked, and it comes
with the underscore convention, `__all__`, and one-time initialization
built in.

What a caller can see is nearly the same in both versions, which is
the point worth taking away. Neither is enforcement. The difference
is how much ceremony you pay to express the same intent, and the
module version pays none.

## 4. Classifying three wrappers

**The logging wrapper is a Decorator.** Its interface is the wrapped
object's, unchanged, and it adds behavior on the way through. Remove
it and every call still reaches the same method with the same
arguments and returns the same result. What you lose is the log. That
is the Decorator row: same interface, added behavior, and the behavior
is what disappears.

**The `read()` wrapper is an Adapter.** Its interface is not the
wrapped object's. The caller asks for `read()` and the object behind
it has only `next_chunk()`, so the wrapper exists to make one type fit
a caller that expects another. Remove it and nothing is lost except
the fit, which is enough: the call no longer resolves at all. An
Adapter adds no behavior, and that is the test that separates it from
the Decorator. Both wrappers forward, and only this one changes the
name the caller uses.

**The flag-checking wrapper is a Proxy.** Its interface is the wrapped
object's, and it adds no behavior to a call that goes through. What it
adds is a decision about whether the call goes through at all. Remove
it and every call reaches the implementation, including the ones that
should have been refused, so what you lose is control over when and
whether the call happens. The [protection proxy](../Chapters/26_Patterns--Surrogate.md#what-proxy-solves)
is this wrapper.

None of the three is a Façade, because a Façade narrows many objects
to a few names and each of these wraps one object. The classification
never turned on the code, which is the lesson: all three could be the
same `__getattr__()` forwarder. What separates them is the answer to
"what breaks if I delete this," and a name chosen from that answer
tells the next reader why the wrapper is there.
