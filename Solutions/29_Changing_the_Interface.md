# Changing the Interface: Solutions

## 1. A dict-style lookup over a list of pairs

```python
# exercise_1.py
from typing import Any

class PairsAdapter:
    "Gives a list of (key, value) pairs a dict-style lookup."
    def __init__(self, pairs: list[tuple[str, Any]]) -> None:
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
adapter.append(("city", "Crested Butte"))  # Reaches the list
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

@dataclass
class _A:
    x: object

@dataclass
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
print([name for name in vars(shop) if not name.startswith("_")])
#: ['dataclass', 'make_a', 'make_b']
```

The caller sees two functions. `_A` and `_B` are still reachable
through `shop._A`, because Python enforces nothing, but the underscore
says they are not part of the deal and `from shop import *` skips
them. The listing prints the module's public names to make that
concrete; `dataclass` appears because an import binds a name in the
module too, which is why a real module either sets `__all__` or
imports as `import dataclasses` and writes `@dataclasses.dataclass`.

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
