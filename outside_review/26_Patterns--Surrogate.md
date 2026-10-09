<!-- outside review of Chapters/26_Patterns--Surrogate.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `26_Patterns--Surrogate.md` chapter:

**1. State: State (Generics for Type Safety)**
* **Target Text:** "Every annotation in `state_surrogate.py` that carries the implementation is `Any`, which the book's typing guidance treats as a last resort."
* **Issue:** The text explains that explicit annotations on `change_to()` would permanently restrict the surrogate to a single protocol, justifying `Any`. However, Python 3.12 generics (PEP 695) resolve this exact dilemma by allowing the class to enforce type consistency between `__init__()` and `change_to()` without hardcoding the protocol itself.
* **Instruction:** Update `state_surrogate.py` to `class Surrogate[T]:` and annotate both parameters with `T`. Update the prose to explain how this generic type guarantees safe swaps while leaving the choice of protocol to the caller (noting that `test_state.py` would then need `Surrogate[StateA | StateB]` or a shared protocol to accept the swap).

**2. Proxy: The Recursion Trap (Overbroad Guard Caveat)**
* **Target Text:** "The fix is a guard at the top of `__getattr__()` that raises `AttributeError` for any name that starts with an underscore:"
* **Issue:** While checking `name.startswith("_")` prevents recursion from missing proxy state or unpickling lookups, it is overbroad: it actively blocks the proxy from forwarding any legitimate protected methods or attributes (like `_helper()`) to the implementation. This is a severe limitation for a generic surrogate meant to transparently pass calls.
* **Instruction:** Add a brief caveat noting that this broad guard breaks forwarding for the implementation's own protected attributes. Suggest that a production surrogate often handles this by explicitly checking only for its own state names (like `name == "_implementation"`) or catching `AttributeError` locally, rather than rejecting all underscored names.

**3. Proxy: Forwarding Writes (Mutable Proxy State Caveat)**
* **Target Text:** "Now every assignment after `__init__()` reaches the implementation via the new `__setattr__()`, so the proxy and the implementation report the same value."
* **Issue:** The text correctly demonstrates forwarding writes, but misses a critical structural consequence: unconditional `__setattr__` forwarding prevents the proxy from mutating its own local state. If a reader tries to combine this with the `CountingProxy` logic to track writes, a statement like `self.calls += 1` will fail because it silently writes to the implementation instead of updating the proxy's counter.
* **Instruction:** Add a warning that forwarding all writes means the proxy cannot easily update its own state variables after initialization. Explain that to maintain local mutable state (like a call counter) while forwarding writes, `__setattr__` must intercept specific attribute names and store them directly on the proxy using `object.__setattr__()`.

## Verdicts

Applied in commit 7af02dde, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. With `class Surrogate[T]`, `ty` 0.0.84 infers `T` from the first implementation's class, so `Surrogate(StateA())` rejects `change_to(StateB())`, and the same swap to `state_demo.py`'s surrogate rejects `b.change_to(second)` (`Expected Implementation1, found Implementation2`), since `ty` narrows `first: Behavior` to `Implementation1`; only an explicit `Surrogate[StateA | StateB]` passes. The listing keeps `Any` (and exercise 7 still asks why the checker cannot see the swap), and a new paragraph at the end of *State* names the generic alternative and that cost.
2. Applied. A probe showed the `startswith("_")` guard turns `p._helper()` and an explicit `p.__len__()` into `AttributeError`, while a guard on `name == "_implementation"` forwards both and survives `copy.copy()` and `pickle` but lets a `self._imp` typo raise a `RecursionError` again. A paragraph after `getattr_guard.py` now states that trade.
3. Rejected. The chapter already says `__setattr__()` "intercepts every assignment, including the one in `__init__()`" and shows `object.__setattr__()` storing the proxy's own state; no listing combines `WriteProxy` with `CountingProxy`'s counter, so the warning guards a case the chapter never builds.
