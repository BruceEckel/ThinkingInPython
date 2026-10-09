<!-- outside review of Chapters/29_Patterns--Changing_the_Interface.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `29_Patterns--Changing_the_Interface.md` chapter:

**1. Section: Three Places for the Adaptation (Robust delegation in `op()`)**

* **Target Text:**
```python
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                ProxyAdapter(item).f()
```
* **Issue:** By calling `.f()` directly on the `ProxyAdapter`, the `WhatIHave` case bypasses `super().op()`. If the base class method ever added more logic alongside calling `.f()`, this override would silently drop that logic for adapted objects.
* **Instruction:** Pass the adapted object to `super().op()` instead, so both cases run the same underlying logic:
```python
        match item:
            case WhatIWant():
                super().op(item)
            case WhatIHave():
                super().op(ProxyAdapter(item))
```

**2. Section: Adapter in Python (Static typing loss with `__getattr__`)**

* **Target Text:** "`getattr_adapter.py` shows the idiomatic Python adapter: a thin wrapper, not a hierarchy. With no base class above it, `Adapter` is a record."
* **Issue:** While a `__getattr__` wrapper is elegant at runtime, it hides the adaptee's interface from static type checkers. A checker infers the type of any forwarded method as `Any` (the return type of `__getattr__`), meaning callers lose autocomplete and signature validation for the adaptee's original interface.
* **Instruction:** Add a sentence noting the static typing trade-off: "However, this convenience costs you static typing: a type checker types every forwarded attribute as `Any`, so callers lose autocomplete and signature checks for the adaptee's methods."

**3. Section: Adapter in Python (`__getattr__` and attribute writes)**

* **Target Text:** "Because `__getattr__()` runs only for attributes Python does not find normally, `f()` uses the adapter's own version while everything else falls through to the adaptee."
* **Issue:** `__getattr__` only intercepts attribute reads (method lookups or property gets). If the adapted interface requires callers to assign to properties or attributes (e.g., `adapter.value = 5`), a slotted wrapper will raise an `AttributeError` unless it also forwards writes.
* **Instruction:** Add a brief caveat about writes: "This only covers reads. If callers need to assign to the adaptee's properties through the adapter, you must also write a forwarding `__setattr__()`."

**4. Section: Façade (Explicit re-exports in `__init__.py`)**

* **Target Text:** "A package's `__init__.py` re-exports a curated set of names from private submodules, the same underscore convention, applied to modules instead of classes."
* **Issue:** For strict type checkers to recognize names imported into `__init__.py` as part of the public API (rather than rejecting them as private usage), the file must explicitly declare them in `__all__` or use redundant aliases (`import X as X`), as specified by PEP 484.
* **Instruction:** Clarify the type checker requirement for re-exports: "A package's `__init__.py` re-exports a curated set of names from private submodules (using `__all__` or explicit `as` imports so type checkers recognize them as public), applying the same underscore convention to modules instead of classes."

## Verdicts

Applied in commit 39d6f8da, after each item was tested against the chapter and run under `uv run`.

1. Applied. Approach 2's `WhatIHave` case called `ProxyAdapter(item).f()` and skipped the inherited `op()`, while the prose says the union keeps the override the same operation; the case now calls `super().op(ProxyAdapter(item))`, the sentence after the listing says both cases reach the inherited `op()`, and Solutions 29 exercise 5's `Renamed` and `WhatIUse2` copies follow. `verify-ch` passes with every `#:` marker unchanged.
2. Rejected. The claim is right (`ty` reveals `Any` for both `a.g` and a misspelled `a.gg` on the `Adapter`), but the chapter already sends the reader to *Surrogate* for the limits of `__getattr__()` forwarding ("The limits *Surrogate* lists for `__getattr__()` apply to this forwarding too"), and chapter 26 states this one first: "Because `__getattr__()` resolves `p.f()` and returns `Any`, the checker cannot verify that call."
3. Rejected. Chapter 26's "Forwarding Writes" section, one of the limits the chapter points to, covers it ("Delegation using `__getattr__()` forwards reads but not writes"); and `Adapter` is a frozen record, so `a.value = 5` raises a `FrozenInstanceError` whatever forwarding it had, and the listing never writes through it.
4. Rejected. The rule is about stub files and installed `py.typed` libraries, not a package's own `__init__.py`: a probe package whose `__init__.py` holds `from ._engine import total`, with no `__all__` and no `as total`, checked clean under `ty` 0.0.84 and Pyright, which typed `shop.total(1.0)` as `float` and `from shop import total` as `(x: float) -> float`. The paragraph before also names `__all__` already.
