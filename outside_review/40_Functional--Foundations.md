<!-- outside review of Chapters/40_Functional--Foundations.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `40_Functional--Foundations.md` chapter:

**1. Section: Immutability (Accuracy of freezing scope)**
* **Target Text:** "Tuples, strings, `frozenset`, and frozen dataclasses are immutable. Each freezes only its own top level."
* **Issue:** Strings and `frozenset`s don't just freeze their top level. Strings contain only immutable characters, and `frozenset`s require their elements to be hashable (effectively preventing them from holding mutable collections like lists). Grouping them with tuples and dataclasses obscures the "shallow freezing" caveat that only applies to containers that can hold mutable items.
* **Instruction:** Change to: "Tuples, strings, `frozenset`, and frozen dataclasses are immutable. Tuples and frozen dataclasses freeze only their own top level."

**2. Section: Composing Functions (Valid type hint syntax)**
* **Target Text:** "and types the composed function `(int) -> str` rather than `(int) -> int`."
* **Issue:** `(int) -> str` is not valid Python syntax for type hints, as the PEP for this syntax (PEP 677) was rejected. While it works as prose shorthand, readers learning modern Python typing might try to copy it into their code and encounter a `SyntaxError`.
* **Instruction:** Change to: "and types the composed function `Callable[[int], str]` rather than `Callable[[int], int]`."

**3. Section: Putting the Pieces Together (Data model semantics)**
* **Target Text:** 
```python
@record
class Reading:
    sensor: str
    celsius: float
```
* **Issue:** The `to_fahrenheit()` function returns a new `Reading`, which means it stores a Fahrenheit value in a field explicitly named `celsius`. Storing Fahrenheit in a `celsius` field makes the data model misleading and could easily cause bugs if the returned value is passed to other functions.
* **Instruction:** Rename the `celsius` field to a neutral name like `temperature` in the `Reading` class, and update the corresponding field references in `warmer_than()`, `to_fahrenheit()`, `report()`, and the `data` list to use `r.temperature`.

**4. Section: Exercises (Clarity of constraints)**
* **Target Text:** "Then try, without a `Placeholder`, to preset `high` and leave `low` and `value` open, and explain why that is impossible."
* **Issue:** A reader could simply write a lambda or a wrapper function (e.g., `lambda low, value: clamp(low, value, 100)`) to preset `high` without using `Placeholder`. The impossibility the exercise intends to demonstrate only applies if the reader is explicitly constrained to using `functools.partial`.
* **Instruction:** Change to: "Then try, using `partial()` but without a `Placeholder`, to preset `high` and leave `low` and `value` open, and explain why that is impossible."

## Verdicts

Applied in commit 61fc2f16, after each item was tested against the chapter and run under `uv run`.

1. Rejected. A `frozenset` holds any hashable object, and a class instance with the default identity hash is hashable and mutable: `frozenset([b])` followed by `b.items.append(1)` printed `[1]` through the set. So `frozenset` freezes only its top level like a tuple, and the proposed sentence would wrongly exempt it; for a string the claim holds trivially.
2. Rejected. The arrow form is how the type checker displays a callable type: `reveal_type(compose(label, increment))` under `uv run ty` shows `(int, /) -> str`, and chapters 46 and 47 use the same `(str) -> ...` notation in prose for types, never as an annotation.
3. Applied, with a different fix. `to_fahrenheit()` does put a Fahrenheit number in the `celsius` field, but Solutions exercise 9 builds its lesson on that field name (reordering the stages makes the predicates compare Fahrenheit against a Celsius limit), so the listing keeps it. A new paragraph after the listing says the field holds Fahrenheit after that stage and that `report()` therefore converts last.
4. Applied. Exercise 5 now reads "Then try, with `partial()` and no `Placeholder`," since a lambda presets `high` with no difficulty; the Solutions quote regenerated to match.
