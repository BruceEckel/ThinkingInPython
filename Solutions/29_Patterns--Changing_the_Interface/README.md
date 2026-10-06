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

[Adapter in Python](../../Chapters/29_Patterns--Changing_the_Interface.md#adapter-in-python) shows `__getattr__()` forwarding every attribute the adapter does not define.
Add `__getitem__()` to the class for the lookup, then try `len()` on the result.
Python finds special methods on the class, not through `__getattr__()`, which explains what `len()` does.

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

**Forward the rest to the list.** The adapter adds the one method the caller needs, `__getitem__()`,
and forwards everything else to the wrapped list through
`__getattr__()`, the same shape as `getattr_adapter.py`.
The adapter defines no `append()`, so the lookup falls through to
the list, and both the adapter and the original `pairs` name see
the new entry.
The record is frozen, and the list it holds is not. `append()`
changes the list and assigns nothing to the adapter.

**Show what forwarding misses.** `len(adapter)` fails although the list has a `__len__()`.
Python looks up a special method on the class, not on the instance,
so the lookup skips `__getattr__()` and finds no `__len__()` on
`PairsAdapter`.
`adapter[key]` works because the class defines `__getitem__()`.
An adapter that must support `len()` defines a `__len__()` that
returns `len(self.pairs)`.

The lookup is a linear scan.
If the pairs are many and the lookups frequent, convert to a real
`dict` once with `dict(pairs)`, and adapt only when the list must
stay a list for some other caller.

</details>
</details>
</details>

## 2. Deprecating the class instead of the method

> In `deprecating.py`,
> deprecate the whole `Report` class instead of the method,
> and show that constructing a `Report` warns while calling `render()` does not.

<details>
<summary>Where to look</summary>

[Deprecating the Old Interface](../../Chapters/29_Patterns--Changing_the_Interface.md#deprecating-the-old-interface) marks a method with `warnings.deprecated()`.
The same decorator accepts a class.
Record warnings with `warnings.catch_warnings(record=True)`, and compare what constructing the class and calling its method add to the list.

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

**Move the warning to the type.** Decorating the class moves the warning to the two places where a
caller commits to the type: constructing an instance and subclassing.
`render()` runs outside the recording block and adds nothing to
`caught`, so code that holds a `Report` runs without a
warning.
That is the right split. `TextReport` replaces the type, not the
method. A caller who wants to act on the warning must change where
they get the `Report`, not where they call `render()`.

**Use the deprecated class on purpose.** The type checker reports both the construction and the subclass, so
both lines carry `# type: ignore`.

The subclass warning fires at class-creation time, so it arrives on
import rather than on any call. A library that subclasses a
deprecated class emits the warning as soon as Python imports that
library.

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

[Façade](../../Chapters/29_Patterns--Changing_the_Interface.md#façade) builds the *Façade* as a class of static methods.
A module is already a namespace, so the classes can stay in it behind leading-underscore names.
Expose a function that assembles them, import only that function elsewhere, and list the module's public names with `vars()`.

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

start_car()
#: _Ignition.turn_key()
#: _FuelPump.prime()
#: _Engine.start()
print([name for name in vars(shop)
       if not name.startswith("_")])
#: ['record', 'start_car']
```

**Hide the classes behind a function.** The caller sees one function, and `start_car()` keeps the assembly
order, `_Ignition(_FuelPump(_Engine()))`, inside the module.
`shop._Engine` and `shop._FuelPump` still reach the classes, because
Python enforces nothing. The underscore marks them as private, and
`from shop import *` skips them.

**List what a caller can see.** The listing prints the module's
public names, the ones `from shop import *` binds. `record` appears because an
import binds a name in the module too. A real module therefore
either sets
[`__all__`](../../Chapters/06_Foundations--Modules_and_Packages.md#what-a-module-exports)
or imports as `import record` and writes `@record.record`.

The class version differs in one way that matters. `Facade` is a
namespace the language does not treat as one. `Facade.start_car` and
`shop.start_car` read identically at the call site, but you must
define the class, import it, and carry it around. `@staticmethod`
exists only to stop Python passing `self` to functions that do not
use it.
The module is a namespace from the start, and it comes
with the underscore convention, `__all__`, and one-time initialization
built in.

A caller sees nearly the same names in both versions. Neither
version enforces anything. The difference is how much ceremony you
pay to express the same intent, and the module version pays none.

</details>
</details>
</details>

## 4. Classifying three wrappers

> Consider three wrappers: one logs each call and forwards it unchanged,
> one exposes a `read()` over an object whose one method is `next_chunk()`,
> and one refuses calls unless you set a flag.
> Classify each as *Proxy*, *Decorator*, *Adapter*,
> or *Façade* using the "remove it and you lose" test from the table,
> and say what you lose in each case.

<details>
<summary>Where to look</summary>

[Distinguishing the Wrappers](../../Chapters/29_Patterns--Changing_the_Interface.md#distinguishing-the-wrappers) gives the table that separates *Proxy*, *Decorator*, *Adapter*, and *Façade*.
For each wrapper, imagine deleting it and ask what breaks.
Check whether the wrapper changes the interface, adds behavior to each call, or controls whether the call proceeds.

<details>
<summary>Solution</summary>

**The logging wrapper is a *Decorator*.** Its interface is the wrapped
object's, unchanged, and it adds behavior on the way through. If you
remove it, every call still reaches the same method with the same
arguments and returns the same result. What you lose is the log. That
is the *Decorator* row: same interface, added behavior, and the
behavior disappears.

**The `read()` wrapper is an *Adapter*.** Its interface is not the
wrapped object's. The caller asks for `read()`, and the wrapped object
offers `next_chunk()` instead, so the wrapper exists to make one type
fit a caller that expects another. If you remove it, you lose only the
fit, and without the fit the call no longer resolves. An *Adapter*
adds no behavior, and that is the test that separates the *Adapter*
from the *Decorator*. Both wrappers forward, and only the *Adapter*
changes the name the caller uses.

**The flag-checking wrapper is a *Proxy*.** Its interface is the
wrapped object's, and it adds no behavior to a call that goes through.
What it adds is a decision about whether the call proceeds. If you
remove it, every call reaches the implementation, including the ones
the proxy refuses, so what you lose is control over when and whether a
call proceeds. This wrapper is the
[protection proxy](../../Chapters/26_Patterns--Surrogate.md#protection-proxy).

None of the three is a *Façade*, because a *Façade* narrows many objects
to a few names and each of these wraps one object.

The code does not decide the classification. All three could be the
same `__getattr__()` forwarder. What separates them is the answer to
"what breaks if I delete this," and a name chosen from that answer
tells the next reader why the wrapper is there.

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

[What an Override May Change](../../Chapters/29_Patterns--Changing_the_Interface.md#what-an-override-may-change) explains which parts of a signature a subclass may alter.
The `/` keeps a parameter's name out of the interface, so without it callers can rely on the name.
Call through a `WhatIUse` variable, so the checker sees only the base class, and give the override the base parameter's name.

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
    what_i_have: WhatIHave

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
<summary>Solution</summary>

If you fix the override by adding a `/` to `WhatIUse2.op()` and keeping the name `item`,
the override refuses the keyword that every `WhatIUse` caller may pass.
`ty` reports `invalid-method-override` because the parameter is positional-only,
and `run(WhatIUse2())` raises a `TypeError` for the unexpected keyword `what_i_want`.
The solution gives the parameter the base class's name instead,
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

**Reproduce the broken override.** `Renamed` is `WhatIUse2` from `adapter_variations.py`, unchanged.
Without the `/`, `what_i_want` is a name callers can pass by keyword,
and `run()` does. `ty` rejects the override:

```text
error[invalid-method-override]: Invalid override of
method `op`
info: the parameter named `item` does not match
`what_i_want` (and can be used as a keyword parameter)
info: This violates the Liskov Substitution Principle
```

**Call through the base type.** The `# type: ignore` silences that report so the listing can show
what the checker prevents. `run()` accepts any `WhatIUse`, and a
`Renamed` is one, so the type checker reports nothing about the call
inside `run()`. At runtime `Renamed.op()` has no parameter named
`what_i_want`, and the call raises a `TypeError`. The override broke
a caller that does not mention `Renamed`.

**Keep the base parameter's name.** The fix keeps the base class's parameter name, `what_i_want`.
`WhatIUse2.op()` still widens
the type to the union, which an override may do, and it accepts the
keyword every `WhatIUse` caller uses. The last call passes a
`WhatIHave` by that keyword and reaches the adapter.

With the `/` in place, as in `adapter.py`, no caller can pass the
parameter by name, so the override is free to call it `item`.
A positional-only parameter keeps its name out of the interface,
and an override can then change the name.

</details>
</details>
</details>
