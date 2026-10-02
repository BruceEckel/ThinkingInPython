# Changing the Interface: Solutions

## 1. A dict-style lookup over a list of pairs

> Write a `PairsAdapter` that wraps a list of `(key, value)` tuples,
> following the shape of `getattr_adapter.py`.
> Give it a dictionary-style `__getitem__()` that finds a value by key,
> and forward every other attribute to the wrapped list with `__getattr__()`.
> Confirm `adapter["name"]` finds a value while `adapter.append(...)` still reaches the underlying list.
> Then call `len(adapter)` and explain the result.

```python
# exercise_1.py
from typing import Any
from exceptions import expected
from record import record

@record
class PairsAdapter:
    pairs: list[tuple[str, Any]]

    def __getitem__(self, key: str) -> Any:
        for k, v in self.pairs:
            if k == key:
                return v
        raise KeyError(key)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.pairs, name)

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
with expected(KeyError):
    adapter["missing"]
#: [KeyError] 'missing'
with expected(TypeError):
    len(adapter)  # type: ignore
#: [TypeError] object of type 'PairsAdapter' has no len()
```

The adapter adds the one method the caller wants, `__getitem__()`,
and forwards everything else to the wrapped list through
`__getattr__()`, the same shape as `getattr_adapter.py`.
The adapter defines no `append()`, so the lookup falls through to
the list, and both the adapter and the original `pairs` name see
the new entry.
The record is frozen, and the list it holds is not: `append()`
changes the list and assigns nothing to the adapter.

`len(adapter)` fails although the list has a `__len__()`.
Python looks up a special method on the class, not on the instance,
so the lookup skips `__getattr__()` and finds no `__len__()` on
`PairsAdapter`.
`adapter[key]` works because the class defines `__getitem__()`.
An adapter that must support `len()` defines `__len__()` and forwards
it by hand.

The lookup is a linear scan.
If the pairs are many and the lookups frequent, convert to a real
`dict` once (`dict(pairs)` does it) and adapt only when the object
must keep being a list to someone else.

## 2. Deprecating the class instead of the method

> In `deprecating.py`,
> deprecate the whole `Report` class instead of the method,
> and show that constructing a `Report` warns while calling `render()` does not.

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
`caught`, so code that already holds a `Report` runs without a
warning.
That is the right split: `TextReport` replaces the type, not the
method. A caller who wants to act on the warning must change where
the object comes from, not where they call it.

The type checker reports both lines, so both carry `# type: ignore`. The
subclass warning fires at class-creation time, so it arrives on
import rather than on any call. A library that subclasses a
deprecated class emits the warning as soon as Python imports that
library.

## 3. `facade.py` as a module

> Rewrite `facade.py` as a module façade.
> Put its classes behind leading-underscore names in one module,
> expose functions that build them, and import only those from a second file.
> Compare what a caller can see in each version.

```python
# shop.py
from record import record

@record
class _Engine:
    def start(self) -> None:
        print("_Engine.start()")

@record
class _FuelPump:
    engine: _Engine

    def prime(self) -> None:
        print("_FuelPump.prime()")
        self.engine.start()

@record
class _Ignition:
    pump: _FuelPump

    def turn_key(self) -> None:
        print("_Ignition.turn_key()")
        self.pump.prime()

def start_car() -> _Ignition:
    ignition = _Ignition(_FuelPump(_Engine()))
    ignition.turn_key()
    return ignition
```

```python
# exercise_3.py
import shop
from shop import start_car

start_car()
#: _Ignition.turn_key()
#: _FuelPump.prime()
#: _Engine.start()
print([name for name in vars(shop)
       if not name.startswith("_")])
#: ['record', 'start_car']
```

The caller sees one function, and `start_car()` keeps the assembly
order, `_Ignition(_FuelPump(_Engine()))`, inside the module.
`shop._Engine` and `shop._FuelPump` still reach the classes, because
Python enforces nothing. The underscore marks them as private, and
`from shop import *` skips them. The listing prints the module's
public names to make that concrete. `record` appears because an
import binds a name in the module too. A real module therefore
either sets
[`__all__`](../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
or imports as `import record` and writes `@record.record`.

The class version differs in one way that matters. `Facade` is a
namespace the language does not treat as one: `Facade.start_car` and
`shop.start_car` read identically at the call site, but you must
define the class, import it, and carry it around. `@staticmethod`
exists only to stop Python passing `self` to functions that never
wanted it.
The module is already a namespace before anyone asked, and it comes
with the underscore convention, `__all__`, and one-time initialization
built in.

A caller sees nearly the same names in both versions, and that is
the point worth taking away. Neither version enforces anything. The
difference is how much ceremony you pay to express the same intent,
and the module version pays none.

## 4. Classifying three wrappers

> Consider three wrappers: one logs each call and forwards it unchanged,
> one exposes a `read()` over an object that has only `next_chunk()`,
> and one refuses calls unless you set a flag.
> Classify each as *Proxy*, *Decorator*, *Adapter*,
> or *Façade* using the "remove it and you lose" test from the table,
> and say what you lose in each case.

**The logging wrapper is a *Decorator*.** Its interface is the wrapped
object's, unchanged, and it adds behavior on the way through. Remove
it and every call still reaches the same method with the same
arguments and returns the same result. What you lose is the log. That
is the *Decorator* row: same interface, added behavior, and the behavior
is what disappears.

**The `read()` wrapper is an *Adapter*.** Its interface is not the
wrapped object's. The caller asks for `read()`, and the wrapped
object offers only `next_chunk()`, so the wrapper exists to make one
type fit a caller that expects another. Remove it and you lose only
the fit, which is enough: the call no longer resolves. An *Adapter*
adds no behavior, and that is the test that separates the *Adapter*
from the *Decorator*. Both wrappers forward, and only this one changes
the name the caller uses.

**The flag-checking wrapper is a *Proxy*.** Its interface is the wrapped
object's, and it adds no behavior to a call that goes through. What it
adds is a decision about whether the call goes through at all. Remove
it and every call reaches the implementation, including the ones the
proxy refuses, so what you lose is control over when and whether the
call happens. This wrapper is the
[protection proxy](../Chapters/26_Patterns--Surrogate.md#protection-proxy).

None of the three is a *Façade*, because a *Façade* narrows many objects
to a few names and each of these wraps one object. The lesson is that
the classification never turns on the code: all three could be the
same `__getattr__()` forwarder. What separates them is the answer to
"what breaks if I delete this," and a name chosen from that answer
tells the next reader why the wrapper is there.

## 5. Renaming a keyword-capable parameter

> Copy the classes from `adapter.py` and remove the `/` from `WhatIUse.op()`.
> Add `WhatIUse2` from `adapter_variations.py` unchanged,
> and call `op()` on each class with the keyword `what_i_want=`.
> Explain what `ty` reports and what happens at runtime.
> Then fix `WhatIUse2.op()` without restoring the `/`.

```python
# exercise_5.py
from typing import override
from exceptions import expect
from record import record

class WhatIHave:
    def g(self) -> None:
        print("WhatIHave.g()")
    def h(self) -> None:
        print("WhatIHave.h()")

class WhatIWant:
    __slots__ = ()
    def f(self) -> None: ...

@record
class ProxyAdapter(WhatIWant):
    what_i_have: WhatIHave

    @override
    def f(self) -> None:
        self.what_i_have.g()
        self.what_i_have.h()

class WhatIUse:
    def op(self, what_i_want: WhatIWant) -> None:
        what_i_want.f()

class Renamed(WhatIUse):
    @override
    def op(  # type: ignore
        self, item: WhatIWant | WhatIHave
    ) -> None:
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                ProxyAdapter(item).f()

class WhatIUse2(WhatIUse):
    @override
    def op(
        self, what_i_want: WhatIWant | WhatIHave
    ) -> None:
        match what_i_want:
            case WhatIWant():
                super().op(what_i_want)
            case WhatIHave():
                ProxyAdapter(what_i_want).f()

def run(user: WhatIUse) -> None:
    user.op(what_i_want=ProxyAdapter(WhatIHave()))

run(WhatIUse())
#: WhatIHave.g()
#: WhatIHave.h()
expect(TypeError, run, Renamed())
#: [TypeError] Renamed.op() got an unexpected keyword
#: argument 'what_i_want'
run(WhatIUse2())
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(what_i_want=WhatIHave())
#: WhatIHave.g()
#: WhatIHave.h()
```

`Renamed` is `WhatIUse2` from `adapter_variations.py`, unchanged.
Without the `/`, `what_i_want` is a name callers can pass by keyword,
and `run()` does. `ty` rejects the override:

```text
error[invalid-method-override]: Invalid override of
method `op`
info: the parameter named `item` does not match
`what_i_want` (and can be used as a keyword parameter)
info: This violates the Liskov Substitution Principle
```

The `# type: ignore` silences that report so the listing can show
what the checker prevents. `run()` accepts any `WhatIUse`, and a
`Renamed` is one, so the type checker reports nothing about the call
inside `run()`. At runtime `Renamed.op()` has no parameter named
`what_i_want`, and the call raises a `TypeError`. The override broke
a caller that does not mention `Renamed`.

The fix keeps the base class's name. `WhatIUse2.op()` still widens
the type to the union, which an override may do, and it accepts the
keyword every `WhatIUse` caller uses. The last call passes a
`WhatIHave` by that keyword and reaches the adapter.

With the `/` in place, as in `adapter.py`, no caller can pass the
parameter by name, so the override is free to call it `item`.
A positional-only parameter keeps its name out of the interface,
and an override can then change the name.
