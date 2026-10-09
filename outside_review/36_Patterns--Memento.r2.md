<!-- outside review of Chapters/36_Patterns--Memento.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `36_Patterns--Memento.md` chapter:

**1. Section: A Deleted Field Leaves a Ghost (Technical accuracy: mechanism of slotted pickling)**

* **Target Text:** "A slotted record pickles its field values as a list in field order, and the load assigns that list to the current class's fields by position. When the deleted field is the last one, the load drops its value. A field deleted from the middle shifts every later value into the wrong field, so a `title`, `strokes`, `color` record that loses `strokes` loads the old strokes tuple as its `color`, and the load still raises nothing."
* **Issue:** Python's pickle protocol (PEP 307) does not serialize slot state as a positional list. For classes with `__slots__` and no `__dict__`, default state serialization produces a dictionary mapping slot names to values (`{slot_name: value}`), and unpickling assigns them by attribute name via `setattr()`. When a slot has been deleted from the target class, unpickling fails with `AttributeError` because the class lacks that slot descriptor and has no `__dict__`; it does not silently drop trailing values or shift middle values into subsequent fields.
* **Instruction:** Replace the description of positional list serialization with the actual slotted behavior: explain that slotted records serialize slot state by attribute name, and unpickling bytes containing a removed slot raises `AttributeError` because the target class has neither a descriptor for that name nor an instance `__dict__`.

**2. Section: Restoring Part of a State (Technical accuracy: supported types for `copy.replace`)**

* **Target Text:** "`NamedTuple`, `datetime`, and any class defining `__replace__()` all accept `copy.replace()`."
* **Issue:** `copy.replace()` (added in Python 3.13 via PEP 712) delegates exclusively to an object's `__replace__()` method. Neither `typing.NamedTuple` (which provides `_replace()`) nor `datetime` types (which provide `.replace()`) define `__replace__()` in Python 3.13 through 3.15. Passing an instance of `NamedTuple` or `datetime` to `copy.replace()` raises a `TypeError`.
* **Instruction:** Remove the references to `NamedTuple` and `datetime`, and state that `copy.replace()` requires `__replace__()` (supported by dataclasses and `@record` types).

**3. Section: A Snapshot Is Not a Reference (Clarity: antecedent in prose describing code output)**

* **Target Text:** "The later `todo[0].append("jam")` changes `todo`'s inner list, and `deep`'s keeps its three elements."
* **Issue:** In `nested_mutation.py`, `deep` itself is a two-element outer list (`[['eggs', 'milk', 'cheese'], ['bread']]`), while its first element is an inner list of three elements. Saying "`deep`'s keeps its three elements" has an ambiguous elided noun that can mislead a reader into thinking the outer container has three items.
* **Instruction:** Clarify the reference to specify the nested list: change the clause to "and `deep`'s first inner list keeps its three elements."

## Verdicts

Second run, on the Flash model. Applied in commit 934f8bed, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The claim is false on 3.15.0rc2: `T.__getstate__()` on a frozen slotted data class returned the list `['a', (), 'b']`, and loading a `title`, `strokes`, `color` pickle into a class without `strokes` printed `T(title='Duck', color=('circle',))` with no exception, so the chapter's positional description is right. The Pro run's verdict on its item 2 found the same.
2. Rejected. `copy.replace(P(1, 2), y=5)` on a `NamedTuple` printed `P(x=1, y=5)`, `copy.replace()` on a `datetime` and a `date` returned the replaced values, and `hasattr()` reported `__replace__` on both classes, so the sentence naming them is right.
3. Applied, with a different fix. The elided noun in "`deep`'s keeps its three elements" makes the reader supply "inner list", and `deep` itself holds two elements. The sentence now names the indexed lists: "grows `todo[0]` to four elements, and `deep[0]` keeps its three."
