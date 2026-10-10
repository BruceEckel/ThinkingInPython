<!-- outside review of Chapters/12_Techniques--Data_Classes_as_Types.md, model gemini-3.1-pro-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `12_Techniques--Data_Classes_as_Types.md` chapter:

**1. Section: `check()` and `TypeFailure` (Missing base exception initialization)**

* **Target Text:**
```python
    subject: str
    reason: str = ""

    def __str__(self) -> str:
```
* **Issue:** `TypeFailure` inherits from `ValueError`, but its generated `__init__()` skips the base constructor, leaving standard properties like `Exception.args` empty. This breaks standard exception behavior (like serialization and the default `repr()`), and perfectly demonstrates the exact inheritance pitfall the chapter later warns about in "Inheritance and the Generated `__init__()`".
* **Instruction:** Add a `__post_init__` to properly initialize the base exception:
```python
    subject: str
    reason: str = ""

    def __post_init__(self) -> None:
        super().__init__(self.subject, self.reason)

    def __str__(self) -> str:
```

**2. Section: Defaults Built Fresh, Not Shared (Incorrect rejection mechanism)**

* **Target Text:** "The test is hashability, not mutability, so a mutable object of an ordinary class you wrote passes as a default and every instance shares it."
* **Issue:** The `@dataclass` decorator does not check hashability to reject mutable defaults. It uses a hardcoded type check specifically for instances of `list`, `dict`, and `set`, which is why unhashable mutable types like `bytearray` or custom data structures bypass the defense and silently share state.
* **Instruction:** Change to: "The test is a hardcoded check for `list`, `dict`, and `set`, not mutability, so a mutable object of an ordinary class you wrote passes as a default and every instance shares it."

**3. Section: Frozen and Plain Data Classes Do Not Mix (Inaccurate subclass behavior)**

* **Target Text:** "A plain subclass of a frozen class is half writable, its own fields assignable and the inherited ones not."
* **Issue:** A frozen data class generates a `__setattr__` that unconditionally raises a `FrozenInstanceError` for any attribute assignment, without checking if the field belongs to the base class or the subclass. A plain subclass inherits this method and therefore rejects all assignments, making the subclass entirely frozen despite lacking the flag.
* **Instruction:** Change to: "A plain subclass of a frozen class inherits a `__setattr__` that rejects all assignments, making the subclass entirely frozen despite lacking the flag."

## Verdicts

No item was applied. Each was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. `BaseException.__new__()` stores the constructor arguments before any `__init__()` runs, so with the listing's `TypeFailure("x", "bad")` a probe gave `e.args == ('x', 'bad')` and `repr(e) == "TF(subject='x', reason='bad')"` with no `__post_init__()`; the "empty `args`" premise is false, and the chapter's later inheritance section is about a base `__init__()` that does work, which `BaseException`'s does not here.
2. Rejected. A probe of `buf: bytearray = bytearray()` as a data class default raised `ValueError: mutable default <class 'bytearray'> for field buf is not allowed`, so the check is the hashability test the chapter names (`__hash__ is None`, since 3.11), not a list of three types; the reviewer's own counterexample disproves the item. An instance of an ordinary class, hashable by default, passed and was shared, as the sentence says.
3. Rejected. The generated `__setattr__()` raises `FrozenInstanceError` when `type(self)` is the frozen class or the name is one of its fields, and lets other names through to `object.__setattr__()`. A probe with a plain subclass of a frozen data class assigned `h.b = 2` successfully and got `FrozenInstanceError` on `h.a = 5`, the inherited field: "half writable, its own fields assignable and the inherited ones not" is the exact behavior, and the reviewer's "rejects all assignments" is wrong.
