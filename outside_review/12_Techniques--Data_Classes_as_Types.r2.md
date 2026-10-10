<!-- outside review of Chapters/12_Techniques--Data_Classes_as_Types.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `12_Techniques--Data_Classes_as_Types.md` chapter:

**1. Section: Defaults Built Fresh, Not Shared (correction of mutable default check mechanism)**

* **Target Text:** "The test is hashability, not mutability, so a mutable object of an ordinary class you wrote passes as a default and every instance shares it."
* **Issue:** `@dataclass` does not inspect hashability when detecting mutable defaults; it performs an explicit type check against three specific standard collections: `isinstance(f.default, (list, dict, set))`. An instance of a user-defined class passes as a default not because it is hashable, but because it is not a `list`, `dict`, or `set`—even an unhashable user-defined object (such as one defining `__eq__` without `__hash__`) or an unhashable built-in like `bytearray` is accepted by `@dataclass`.
* **Instruction:** Replace the sentence with: "The test is an explicit check for `list`, `dict`, and `set`, not a check for mutability or hashability, so a mutable object of an ordinary class you wrote passes as a default (even if unhashable) and every instance shares it."

**2. Section: More Data Class Tools (correction of quoted dataclass exception message)**

* **Target Text:** "`@dataclass` refuses that with `TypeError: non-default argument 'b' follows default argument 'a'`."
* **Issue:** When a non-default field follows a default field, CPython's `dataclasses` raises `TypeError: non-default argument 'b' follows default argument`. The exception message does not identify the preceding default argument `'a'`.
* **Instruction:** Change the quoted exception message to omit `'a'`: "`@dataclass` refuses that with `TypeError: non-default argument 'b' follows default argument`."

**3. Section: Data Classes (scope of `copy.replace()`)**

* **Target Text:** "[`copy.replace()`](#the-general-form-of-replace) does the same for anything immutable, not only for data classes."
* **Issue:** `copy.replace()` is not restricted to immutable objects. It works on any type implementing the `__replace__()` protocol (PEP 728 / Python 3.13), including mutable data classes (which generate `__replace__()` by default) and mutable standard library types such as `types.SimpleNamespace`.
* **Instruction:** Clarify that the protocol is not limited to immutable types: "[`copy.replace()`](#the-general-form-of-replace) does the same for any type supporting `__replace__()`, not only for data classes."

## Verdicts

Second run, on the Flash model. Applied in commit 3d837a7c, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. A probe data class whose default is an instance of a user class defining `__eq__()` and so unhashable raised `ValueError: mutable default <class 'Eq'> for field e is not allowed: use default_factory`, so the check is hashability (`__hash__ is None`, since 3.11), as the chapter says; the three-type `isinstance` the reviewer describes is the pre-3.11 code. The Pro round's `bytearray` probe rejected the same item.
2. Rejected. A probe data class with `a: int = 1` followed by `b: int` raised `TypeError: non-default argument 'b' follows default argument 'a'` on 3.15.0rc2, the message the chapter quotes with the preceding field named; the reviewer's shorter message is an older Python's.
3. Applied, with a different fix. `copy.replace()` on a plain (mutable) data class returned the changed copy and on a `types.SimpleNamespace` returned `namespace(a=2)`, so "for anything immutable" named a restriction the function lacks, and the chapter's own General Form section lists `SimpleNamespace` and "anything else that defines `__replace__()`". The sentence now reads "does the same for any object that defines `__replace__()`", the condition that section already states, in place of the reviewer's "any type supporting".
