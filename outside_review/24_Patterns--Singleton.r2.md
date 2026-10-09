<!-- outside review of Chapters/24_Patterns--Singleton.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `24_Patterns--Singleton.md` chapter:

**1. Section: Lazy Creation (error about static type-checking of mangled attributes)**

* **Target Text:** "`OnlyOne.__OnlyOne`, written from outside the class, asks for an attribute that does not exist under that name, so it fails at runtime with `AttributeError`, not at type-checking time."
* **Issue:** Static type checkers (including `ty`, Pyright, and mypy) recognize private name mangling and flag attempts to access names with double leading underscores from outside the class as unknown or inaccessible attributes. The access fails both at type-checking time and at runtime.
* **Instruction:** Remove "not at type-checking time" and state that the unmangled access is caught both statically and at runtime: "`OnlyOne.__OnlyOne`, written from outside the class, asks for an attribute that does not exist under that name, so it fails both at type-checking time and at runtime with `AttributeError`."

**2. Section: Singleton by Class Decorator (misdescription of construction bypass in metaclass singleton)**

* **Target Text:** "Its metaclass overrides `__call__()`, and that override skips `__init__()` on every later construction, so the first call's arguments win."
* **Issue:** When a metaclass overrides `__call__()` to cache an instance, returning the cached instance skips calling `super().__call__()`, which means it bypasses the entire construction pipeline—skipping both `__new__()` and `__init__()`, not just `__init__()`.
* **Instruction:** Clarify that the metaclass override skips construction entirely: "Its metaclass overrides `__call__()`, and that override skips `__new__()` and `__init__()` on every later construction, so the first call's arguments win."

**3. Section: Singleton by Class Decorator (misattributed rationale for appending behavior)**

* **Target Text:** "That listing puts its work inside `__new__()`, so later calls append to the shared instance instead of overwriting it."
* **Issue:** Placing initialization inside `__new__()` does not inherently make repeat calls append; `singleton_class_variable.py` appends because its code explicitly calls `.append(arg)` rather than assigning `self.val = arg`. The actual role of `__new__()` in that listing is to ensure that the method runs on every call (since `type.__call__()` always invokes `__new__()`), while avoiding a standard `__init__()` that would unconditionally reinitialize instance fields on every construction.
* **Instruction:** Revise the sentence to clarify that `__new__()` runs on each call and chooses to append to the shared list rather than reinitializing the instance: "That listing handles the arguments inside `__new__()` and explicitly appends to the shared list, avoiding an `__init__()` that would reinitialize and overwrite the instance on every call."

**4. Section: Singleton by Class Decorator (unexplained runtime exception for `isinstance`)**

* **Target Text:** "`isinstance(first, Registry)` and `class Sub(Registry)` both raise a `TypeError`:"
* **Issue:** The paragraphs following this sentence explain in detail why `class Sub(Registry)` raises a runtime `TypeError` (passing four arguments to `singleton.__init__()` when acting as a metaclass), but leave the reader without an explanation for why `isinstance(first, Registry)` fails. An experienced programmer needs the mechanism named: `@singleton` replaces `Registry` with an instance of `singleton`, which is not an instance of `type` (or a tuple/union of types), violating `isinstance`'s second-argument contract.
* **Instruction:** Add a brief explanation of `isinstance`'s failure right before or alongside the explanation of `Sub`: "`isinstance(first, Registry)` fails because decoration rebinds `Registry` to an instance of `singleton`, which is not an instance of `type`."

## Verdicts

Second run, on the Flash model. Applied in commit 05388656, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The claim about the type checkers is wrong. A probe that appended `print(OnlyOne.__OnlyOne)` to `singleton_pattern.py` drew no diagnostic from `ty` 0.0.84 or Pyright, which do not model name mangling outside a class; both flagged the mangled `OnlyOne._OnlyOne__OnlyOne` instead, and the run raised the `AttributeError` the chapter names, so "not at type-checking time" stays.
2. Applied. Chapter 17's `singleton.py` returns the cached instance without calling `type.__call__()`, and that chapter says the repeat call "does not reach `__new__()` or `__init__()`". The sentence now says the override skips `__new__()` and `__init__()`, which also makes the next sentence's contrast ("`__new__()` still runs on every call, unlike the metaclass form") follow.
3. Applied, with a different fix. The old "puts its work inside `__new__()`, so later calls append" credited the placement with the appending, and "instead of overwriting it" contrasted with an `__init__()` the passage never mentions. The sentence now says what the listing's `__new__()` does (creates `val` on the first call, appends on every call) and contrasts it with the metaclass form just described: each later argument joins the shared list instead of being discarded. The reviewer's wording about avoiding an `__init__()` was not used.
4. Applied. A probe of `isinstance(Registry("p"), Registry)` printed `isinstance() arg 2 must be a type, a tuple of types, or a union`, and the chapter explained the `Sub` failure at length but left the `isinstance()` one to the test's `match` string. The sentence before the test listing now says `isinstance()` requires a class, a tuple of classes, or a union as its second argument, and `Registry` names a `singleton` object.
