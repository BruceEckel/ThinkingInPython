# Changing the Interface: Solutions

## 1. A dict-style lookup over a list of pairs

> Write a `PairsAdapter` that wraps a list of `(key, value)` tuples,
> following the shape of `getattr_adapter.py`.
> Give it a dictionary-style `__getitem__()` that finds a value by key,
> and forward every other attribute to the wrapped list with `__getattr__()`.
> Confirm `adapter["name"]` finds a value while `adapter.append(...)` still reaches the underlying list.
> Then call `len(adapter)` and explain the result.

<details>
<summary>Where to look</summary>

[*Adapter* in Python](../../Chapters/29_Patterns--Changing_the_Interface.md#adapter-in-python)
shows `__getattr__()` forwarding every attribute the adapter does not define.
Add `__getitem__()` to the class for the lookup,
then try `len()` on the adapter.
Python finds special methods on the class, not through `__getattr__()`.
That rule explains what `len()` does.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Any
from exceptions import expected
from record import record

@record
class PairsAdapter:
    pairs: list[tuple[str, Any]]

    def __getitem__(self, key: str) -> Any:
        ...

    def __getattr__(self, name: str) -> Any:
        ...
```

<details>
<summary>Done when</summary>

`adapter["name"]` returns the value,
`adapter.append(...)` makes the original list one entry longer,
and `adapter["missing"]` raises a `KeyError`.
`len(adapter)` raises `TypeError: object of type 'PairsAdapter' has no len()`,
and you can say why `__getattr__()` never sees that call.

<details>
<summary>Solution</summary>

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

**Forward the rest to the list.**
The adapter defines no `append()`, so the lookup falls through to the list.

**Grow the shared list.**
The record is frozen, but the list it holds stays mutable.
The adapter's `pairs` field refers to the same list as before.

**Show what `__getattr__()` cannot forward.**
`len(adapter)` raises a `TypeError` although the list has a `__len__()`.
Python looks up a special method on the class, not on the instance,
so the lookup searches `PairsAdapter` for `__len__()` and skips `__getattr__()`.
[Special Methods Bypass `__getattr__()`](../../Chapters/25_Patterns--Surrogate.md#special-methods-bypass-getattr)
in *Surrogate* covers that lookup rule.
`adapter[key]` works because the class defines `__getitem__()`.
An adapter that must support `len()` defines a `__len__()` that returns `len(self.pairs)`.

The key lookup in `__getitem__()` is a linear scan.
For a long list and frequent lookups, convert the list once with `dict(pairs)`.
Keep the adapter when some other caller needs the list to stay a list.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Deprecating the class instead of the method

> In `deprecating.py`,
> deprecate the whole `Report` class instead of the method,
> and show that constructing a `Report` warns while calling `render()` does not.

<details>
<summary>Where to look</summary>

[Deprecating the Old Interface](../../Chapters/29_Patterns--Changing_the_Interface.md#deprecating-the-old-interface)
marks a method with `warnings.deprecated()`.
The same decorator accepts a class.
Record warnings with `warnings.catch_warnings(record=True)`,
and compare what constructing the class and calling its method add to the recorded warnings.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
import warnings

@warnings.deprecated("Report is replaced by TextReport")
class Report:
    def render(self) -> str:
        ...
```

<details>
<summary>Done when</summary>

inside `warnings.catch_warnings(record=True)`,
constructing a `Report` adds one `DeprecationWarning` carrying your message,
and calling `render()` on that instance prints `report` and leaves the recorded count unchanged.
`uv run ty check` reports `deprecated` on the construction until you mark it `# type: ignore`.

<details>
<summary>Solution</summary>

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

**Move the warning to the type.**
Decorating the class moves the warning to the two operations that build something from the class:
constructing an instance and subclassing.
`render()` runs inside the recording block, yet `caught` holds two entries:
one for the construction and one for the subclass.
Code that holds a `Report` therefore calls its methods silently.

`TextReport` replaces the type, not the method,
so warning on the type alone matches the replacement.
A caller who wants to act on the warning must change where they get the `Report`,
not where they call `render()`.

**Use the deprecated class on purpose.**
The type checker reports both the construction and the subclass,
so both lines carry `# type: ignore`.

Python issues the subclass warning when the `class` statement runs,
so for a module-level subclass the warning appears at import, before any call.
A library that subclasses a deprecated class emits the warning as soon as Python imports that library.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. `facade.py` as a module

> Rewrite `facade.py` as a module façade.
> Put its classes behind leading-underscore names in one module,
> expose functions that build them, and import only those from a second file.
> Compare what a caller can see in each version.

<details>
<summary>Where to look</summary>

[*Façade*](../../Chapters/29_Patterns--Changing_the_Interface.md#façade)
builds the *Façade* as a class of static methods.
A module is already a namespace,
so the classes can stay in it behind leading-underscore names.
Expose a function that assembles them, import only that function elsewhere,
and list the module's public names with `vars()`.

<details>
<summary>The shape</summary>

```python
# The shape of shop.py
from record import record

@record
class _Engine:
    def start(self) -> None:
        ...

@record
class _FuelPump:
    engine: _Engine

    def prime(self) -> None:
        ...

@record
class _Ignition:
    pump: _FuelPump

    def turn_key(self) -> None:
        ...

def start_car() -> _Ignition:
    ...
```

<details>
<summary>Done when</summary>

running your second file prints the three calls in `facade.py`'s order,
ignition, pump, engine, under underscore names, and then the assembled object.
Listing the module's names without a leading underscore through `vars()` shows your builder function,
and you can explain each other name that appears.

<details>
<summary>Solution</summary>

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

print(start_car())
#: _Ignition.turn_key()
#: _FuelPump.prime()
#: _Engine.start()
#: _Ignition(pump=_FuelPump(engine=_Engine()))
print([name for name in vars(shop)
       if not name.startswith("_")])
#: ['record', 'start_car']
```

**Hide the classes behind a function.**
The caller uses one function.
`shop._Engine` and `shop._FuelPump` still reach the classes,
because Python lets any caller read a module attribute, underscore or not.
The underscore marks them as private, so `from shop import *` skips them.

**List what a caller can see.**
The listing prints the module's public names,
the ones `from shop import *` binds.
`record` appears because an import binds a name in the module too.
A real module therefore either sets [`__all__`](../../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
or imports the decorator under a private name,
`from record import record as _record`, and writes `@_record`.

`Facade` is a class used as a namespace,
and the module around it is a namespace too.
`Facade.start_car()` and `shop.start_car()` read identically at the call site,
but the class version adds a `class` statement and a `@staticmethod` on each function.
None of these functions uses `self`.
`@staticmethod` makes Python call each one with the caller's arguments alone,
even through an instance.
A module is a namespace as soon as Python creates it.
It supports the underscore convention and `__all__`.

A caller of `facade.py` sees `Engine`, `FuelPump`, `Ignition`,
and `Facade` as public names.
A caller of `shop` sees `start_car`.
Both also see `record`.
Neither version enforces privacy.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Classifying three wrappers

> Consider three wrappers: one logs each call and forwards it unchanged,
> one exposes a `read()` over an object whose one method is `next_chunk()`,
> and one refuses calls unless you set a flag.
> Classify each as *Proxy*, *Decorator*, *Adapter*,
> or *Façade* using the table's "What removing it loses" column,
> and say what you lose in each case.

<details>
<summary>Where to look</summary>

[Distinguishing the Wrappers](../../Chapters/29_Patterns--Changing_the_Interface.md#distinguishing-the-wrappers)
gives the table that separates *Proxy*, *Decorator*, *Adapter*, and *Façade*.
For each wrapper, imagine deleting it and ask what breaks.
Check whether the wrapper changes the interface, adds behavior to each call,
or controls whether the call proceeds.

<details>
<summary>Done when</summary>

you have one pattern per wrapper, no two the same, and none is *Façade*.
For each, you can finish "deleting it loses..." with one thing: the log,
the translation from `read()` to `next_chunk()`,
or the decision whether a call proceeds.

<details>
<summary>Solution</summary>

**The logging wrapper is a *Decorator*.**
Its interface is the wrapped object's interface, unchanged,
and it adds behavior around each call it forwards.
If you remove it, every call still reaches the same method with the same arguments and returns the same result.
What you lose is the log.
That is the *Decorator* row: same interface, added behavior,
and the behavior disappears.

**The `read()` wrapper is an *Adapter*.**
Its interface differs from the wrapped object's interface.
The caller asks for `read()`.
The wrapped object offers `next_chunk()`.
The wrapper exists to translate the caller's `read()` into a `next_chunk()` call.
If you remove it, you lose that translation.
The caller's `read()` then raises an `AttributeError`,
because `next_chunk()` is the wrapped object's one method.

An *Adapter* leaves each call's behavior as it was,
which separates the *Adapter* from the *Decorator*.
Both wrappers forward.
Only the *Adapter* changes the name the caller uses.

**The flag-checking wrapper is a *Proxy*.**
Its interface is the wrapped object's interface.
A call that goes through behaves as it would on the wrapped object.
What the proxy adds is a decision about whether the call proceeds.
If you remove it, every call reaches the implementation,
including the ones the proxy refuses.
What you lose is control over when and whether a call proceeds.
This wrapper is the [protection proxy](../../Chapters/25_Patterns--Surrogate.md#protection-proxy).

None of the three is a *Façade*,
because a *Façade* narrows many objects to a few names,
while each of these wraps one object.

Purpose, not code, decides the classification.
All three could be the same `__getattr__()` forwarder.
What separates them is the answer to "what breaks if I delete this."
A name chosen from that answer tells the next reader why the wrapper is there.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. Renaming a keyword-capable parameter

> Copy the classes from `adapter.py` and remove the `/` from `WhatIUse.op()`.
> Add `WhatIUse2` from `adapter_variations.py` unchanged,
> and call `op()` on each class with the keyword `what_i_want=`.
> Explain what `ty` reports and what each call does at runtime.
> Then fix `WhatIUse2.op()` without restoring the `/`.

<details>
<summary>Where to look</summary>

[What an Override May Change](../../Chapters/29_Patterns--Changing_the_Interface.md#what-an-override-may-change)
explains which parts of a signature a subclass may alter.
The `/` keeps a parameter's name out of the interface,
so removing it lets callers pass the argument by name.
Call through a `WhatIUse` variable,
so the checker verifies the call against the base class's signature.
Then give the override the base parameter's name.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from typing import override
from exceptions import expect
from record import record

class WhatIHave:
    def g(self) -> None:
        ...
    def h(self) -> None:
        ...

class WhatIWant:
    __slots__ = ()
    def f(self) -> None: ...

@record
class ProxyAdapter(WhatIWant):
    adaptee: WhatIHave

    @override
    def f(self) -> None:
        ...

class WhatIUse:
    def op(self, what_i_want: WhatIWant) -> None:
        ...

class Renamed(WhatIUse):
    @override
    def op(  # type: ignore
        self, item: WhatIWant | WhatIHave
    ) -> None:
        ...

class WhatIUse2(WhatIUse):
    @override
    def op(
        self, what_i_want: WhatIWant | WhatIHave
    ) -> None:
        ...

def run(user: WhatIUse) -> None:
    ...
```

<details>
<summary>Done when</summary>

before your fix, `uv run ty check` reports `invalid-method-override` on `WhatIUse2.op()`
(the parameter `item` does not match `what_i_want`),
and the keyword call raises a `TypeError` for `what_i_want`.
After it, `ty` passes,
and `WhatIUse2().op(what_i_want=WhatIHave())` prints `WhatIUse2.op() wraps it` then the adapter's three lines.

<details>
<summary>Solution</summary>

If you add a `/` to `WhatIUse2.op()` and keep the name `item`,
the override rejects the keyword that every `WhatIUse` caller may pass.
`ty` reports `invalid-method-override` because the parameter is positional-only,
and `run(WhatIUse2())` raises a `TypeError` for the unexpected keyword `what_i_want`.
The solution gives the parameter the base class's name,
so the override accepts every call the base accepts.

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
    adaptee: WhatIHave

    @override
    def f(self) -> None:
        print("ProxyAdapter.f()")
        self.adaptee.g()
        self.adaptee.h()

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
                print("WhatIUse2.op() wraps it")
                super().op(ProxyAdapter(item))

class WhatIUse2(WhatIUse):
    @override
    def op(
        self, what_i_want: WhatIWant | WhatIHave
    ) -> None:
        match what_i_want:
            case WhatIWant():
                super().op(what_i_want)
            case WhatIHave():
                print("WhatIUse2.op() wraps it")
                super().op(ProxyAdapter(what_i_want))

def run(user: WhatIUse) -> None:
    user.op(what_i_want=ProxyAdapter(WhatIHave()))

run(WhatIUse())
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
expect(TypeError, run, Renamed())
#: [TypeError] Renamed.op() got an unexpected keyword
#: argument 'what_i_want'
run(WhatIUse2())
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
WhatIUse2().op(what_i_want=WhatIHave())
#: WhatIUse2.op() wraps it
#: ProxyAdapter.f()
#: WhatIHave.g()
#: WhatIHave.h()
```

**Reproduce the broken override.**
`Renamed` is `WhatIUse2` from `adapter_variations.py`, unchanged.
With the `/` removed, `what_i_want` becomes a name callers can pass by keyword.
`ty` rejects the override:

```text
error[invalid-method-override]: Invalid override of
method `op`
info: the parameter named `item` does not match
`what_i_want` (and can be used as a keyword parameter)
info: This violates the Liskov Substitution Principle
```

**Call through the base type.**
The `# type: ignore` suppresses that report so the listing can show what the checker prevents.
A `Renamed` is a `WhatIUse`,
so the type checker accepts the call inside `run()`.
The override breaks `run()`, a caller written against `WhatIUse` alone.

**Keep the base parameter's name.**
`WhatIUse2.op()` names its parameter `what_i_want`, as the base class does,
so it accepts the keyword every `WhatIUse` caller may pass.
It still widens the type to the union, which an override may do.

With the `/` in place, as in `adapter.py`,
every caller must pass the parameter by position,
so the override is free to call it `item`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
