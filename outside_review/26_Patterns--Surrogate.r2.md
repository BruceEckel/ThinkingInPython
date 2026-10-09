<!-- outside review of Chapters/26_Patterns--Surrogate.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the 26_Patterns--Surrogate.md chapter:

**1. Section: A Surrogate Is Not Its Implementation (Factual error regarding `isinstance` workarounds)**

* **Target Text:** "Two workarounds make `isinstance()` return `True`,\nand neither verifies anything:\n\n-   `Service.register(Proxy)` tells the ABC machinery to answer `True` for every `Proxy`,\n    without looking at its methods.\n-   A `__class__` property returning the implementation's class makes `isinstance()` see that class rather than `Proxy`.\n\nBoth satisfy the runtime check and neither satisfies a type checker."
* **Issue:** Neither workaround satisfies `isinstance()` at runtime for the classes in `proxy_identity.py`. `@runtime_checkable` Protocols inspect attributes structurally via `inspect.getattr_static()` and bypass the ABC registry, so `Service.register(Proxy)` still results in `False`. Furthermore, Python's `isinstance()` inspects the instance's underlying C-level type (`Py_TYPE`), ignoring a `__class__` property, so `isinstance(p, Implementation)` also returns `False`.
* **Instruction:** Replace the passage to clarify that neither workaround works here: "Neither workaround makes `isinstance()` return `True` here: `@runtime_checkable` Protocols inspect attributes directly and ignore `register()`, while `isinstance()` checks the underlying type and ignores a `__class__` property (only direct assignment to `__class__` mutates that type)."

**2. Section: Special Methods Bypass `__getattr__()` (Imprecise explanation of failed lookup fallback)**

* **Target Text:** "`p.__len__()` and `len(p)` look interchangeable and are not.\n`p.__len__()` is ordinary attribute access,\nso the failed instance lookup falls through to `__getattr__()`, which delegates."
* **Issue:** Ordinary attribute access does not fall through to `__getattr__()` solely because instance lookup fails; it also checks the class hierarchy. `p.__len__()` falls through because neither `Proxy` nor `object` defines `__len__()`, whereas an explicit access like `p.__str__()` resolves to `object.__str__` on the class and never triggers `__getattr__()`.
* **Instruction:** Reword the sentence to explain the class-level check: "`p.__len__()` is ordinary attribute access; because neither the instance nor `Proxy` (including `object`) defines `__len__()`, the failed lookup falls through to `__getattr__()`, which delegates."

**3. Section: State (Unverified claim about type narrowing on annotated variables)**

* **Target Text:** "`ty` narrows `first` to `Implementation1` despite its `Behavior` declaration,\nand rejects `b.change_to(second)`."
* **Issue:** Under PEP 526, an explicit type annotation (`first: Behavior = Implementation1()`) sets the static type of `first` to `Behavior`, and type checkers do not narrow annotated variables to their initial assignment values. If confirming whether `ty` actually narrows an annotated variable here requires a tool run, let the author run it; this inference failure typically occurs only when `first` is unannotated (`first = Implementation1()`).
* **Instruction:** Adjust the wording to distinguish annotated and unannotated variables: "If `first` is unannotated, `ty` infers `T` as `Implementation1` and rejects `b.change_to(second)`. Declaring `first: Behavior` avoids narrowing `T` to `Implementation1`, but requires every caller to write the union or protocol explicitly."

**4. Section: Protection Proxy (Mischaracterization of `hasattr` failure)**

* **Target Text:** "`guest.__getattr__()` raises `PermissionError` instead,\nso `hasattr(guest, "erase")` raises `PermissionError` too,\nwhere a missing name on an ordinary object returns `False`."
* **Issue:** `erase` is an existing method on `Document` rather than a missing name. Because `hasattr()` only catches `AttributeError`, raising `PermissionError` causes `hasattr(guest, ...)` to crash both when probing unauthorized methods and when querying genuinely nonexistent attributes, violating `hasattr()`'s boolean contract.
* **Instruction:** Revise the sentence to read: "`guest.__getattr__()` raises `PermissionError` instead, so `hasattr(guest, "erase")` raises `PermissionError` too; because `hasattr()` swallows only `AttributeError`, raising any other exception crashes attribute checks for unauthorized and nonexistent names alike."

## Verdicts

Second run, on the Flash model. Applied in commit 2d3e8ac5, after each item was tested against the chapter and run under `uv run`.

1. Rejected. A probe reproducing `proxy_identity.py` printed `True` for `isinstance(p, Service)` after `Service.register(Proxy)` (a `Protocol` keeps the ABC registry, which `isinstance()` consults before the structural check), and `True` for `isinstance(cp, Implementation)` on a proxy with a `__class__` property, since `isinstance()` falls back to `__class__` when `type()` does not match. Both workarounds work as the chapter says.
2. Applied, with a different fix. The point is right: `p.__len__()` falls through because neither the instance nor `Proxy` (through `object`) has a `__len__()`, and a probe confirmed an explicit `p.__str__()` finds `object.__str__()` and never calls `__getattr__()`. "The failed instance lookup" now reads "That lookup searches the instance and `Proxy`, finds no `__len__()`, and falls through to `__getattr__()`"; the paragraph after it already covers the dunders `object` defines.
3. Rejected. With `class Surrogate[T]` and `first: Behavior = Implementation1()`, `ty` 0.0.84 reveals `first` as `Implementation1`, infers `Surrogate[Implementation1]`, and rejects `b.change_to(second)` with "Expected `Implementation1`, found `Implementation2`", so the chapter's claim that `ty` narrows despite the declaration holds. The Pro run's verdict 1 recorded the same result.
4. Rejected. A probe confirmed `hasattr(guest, "nope")` also raises `PermissionError` for a guest, but the chapter's next sentence already states the general rule: "A surrogate whose `__getattr__()` can raise something other than `AttributeError` breaks `hasattr()`." The listing probes no nonexistent name, so the added clause repeats that rule.
