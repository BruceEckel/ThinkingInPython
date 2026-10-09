<!-- outside review of Chapters/36_Patterns--Memento.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `36_Patterns--Memento.md` chapter:

**1. Section: Immutability (Return type accuracy)**

* **Target Text:** `def draw(self, stroke: str) -> Drawing:`
* **Issue:** Using the base class `Drawing` as the return type means that if the class is ever subclassed, type checkers will incorrectly infer that the method returns the base class rather than the subclass. Since `dataclasses.replace()` returns an instance of the exact runtime class of `self`, annotating with `Self` accurately models the return type and is the modern standard for fluent methods.
* **Instruction:** Change the method signature to `def draw(self, stroke: str) -> Self:` and add `from typing import Self` to the module imports in `frozen_sketch.py`.

**2. Section: A Deleted Field Leaves a Ghost (Slotted class protection)**

* **Target Text:** "The deleted-field drift raises nothing, and the data is wrong."
* **Issue:** This silent failure happens because the simulation explicitly disables slots (`slots=False`). If the class uses slots (the default for the book's `@record`), `pickle.loads()` bypasses `__dict__` and assigns directly to the slots. When it encounters the dropped name in the saved state, it finds no slot and safely raises an `AttributeError` at load time, preventing the silent corruption.
* **Instruction:** Add a sentence immediately after the target text: "If the class uses slots (the default for `@record`), this drift is caught immediately: `pickle.loads()` finds no slot for the dropped name and raises an `AttributeError` at load time."

**3. Section: Immutability (Efficient bounded history)**

* **Target Text:** "For a field that grows with every edit, bound the history's depth (see exercise 2), coalesce edits before `History` stores them,"
* **Issue:** When implementing a bounded history depth, discarding the oldest state from a standard `list` requires an `O(N)` operation (`list.pop(0)`) to shift all remaining elements. Recommending `collections.deque` provides the reader with the correct standard library tool to enforce an efficient `O(1)` bounded history.
* **Instruction:** Change the text to: "For a field that grows with every edit, bound the history's depth with a tool like `collections.deque(maxlen=n)` (see exercise 2), coalesce edits before `History` stores them,"

## Verdicts

Applied in commit 44240ccd, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The type is right in general: `ty` reveals `Drawing` for `draw()` called on a `@record` subclass of `Drawing` while the runtime type is the subclass, and `-> Self` with `replace()` checks clean and reveals the subclass. But nothing in the chapter or its Solutions subclasses `Drawing`, so the annotation guards a case the listings never exercise, and the change would ripple into six Solutions copies of `draw()`.
2. Applied, with a different fix. The claim is false: a probe with slotted records showed `pickle.loads()` raising no exception for a deleted field, because a frozen slotted data class pickles a list of values and `_dataclass_setstate()` zips it with the current fields by position. Deleting a middle field of a `title`, `strokes`, `color` record loaded `T(title='Duck', color=('circle',))`. A new paragraph after `ghost_field.py` says why the listings use `@record(slots=False)` and what a slotted record does instead.
3. Rejected. The sentence points to exercise 2 for the bound, and naming `deque(maxlen=n)` in the chapter gives away the exercise's implementation. The `O(n)` cost of `list.pop(0)` is real but small here, since the list never exceeds the bound.
