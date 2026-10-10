<!-- outside review of Chapters/13_Techniques--Pattern_Matching.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `13_Techniques--Pattern_Matching.md` chapter:

**1. Section: Keyword Patterns (Correction of object vs. class scoping)**

* **Target Text:** "Keyword patterns also work on any object with the named attributes, data class or not, and let you match a subset of attributes while ignoring the rest:"
* **Issue:** A class pattern always performs an `isinstance()` check against the class named in the pattern before inspecting attributes. A pattern like `Point(x=0)` will never match an arbitrary object simply because it has an `x` attribute. The intended distinction is that keyword patterns work on instances of *any class* (data class or not) without needing `__match_args__`.
* **Instruction:** Change "work on any object with the named attributes, data class or not," to "work on instances of any class with the named attributes, data class or not,".

**2. Section: Mapping Patterns (Correction of mapping capture semantics)**

* **Target Text:** "A `**rest` at the end binds whatever keys the pattern did not mention,"
* **Issue:** In a mapping pattern, `**rest` binds a `dict` containing the remaining key-value pairs, not just the unmentioned keys. Describing it as binding "whatever keys" suggests that `rest` receives a collection of keys (such as a list or set), which misleads readers comparing it to sequence patterns where `*rest` captures elements.
* **Instruction:** Change "binds whatever keys the pattern did not mention," to "binds the remaining key-value pairs into a dictionary,".

**3. Section: The Expression Problem (Syntax error in proposed pattern)**

* **Target Text:** "and the type checker flags `assert_never()` in both `render()` and `cost()` until you add a `case Webhook(...)` to each."
* **Issue:** Python's pattern matching syntax does not support `...` (ellipsis) inside a class pattern; writing `case Webhook(...)` raises `SyntaxError: invalid syntax`. In addition, `cost()` uses zero-argument class patterns like `case Email():`, whereas `render()` extracts attributes like `case Email(subject):`.
* **Instruction:** Change "until you add a `case Webhook(...)` to each." to "until you add a `case Webhook(url)` to `render()` and a `case Webhook()` to `cost()`."

**4. Section: Exercises (Clarification of Exercise 5 requirements)**

* **Target Text:** "Then write it a second time with one `case` per sign combination, using `|` alternations and no guards, and say which version reads better."
* **Issue:** Coordinates of a `Point` cannot be checked for signs without guards unless the coordinates are pre-computed into signs (such as with the `sign(x), sign(y)` pattern introduced in [Sequence Patterns](#sequence-patterns)). Furthermore, writing "one `case` per sign combination" contradicts using `|` alternations, which combine multiple possibilities into a single case rather than giving each combination its own case.
* **Instruction:** Clarify that the second version transforms the coordinates via `sign()` and uses `|` alternations to combine axis cases. Change the sentence to: "Then write it a second time matching on `sign(p.x), sign(p.y)` with no guards, using `|` alternations to combine axis cases, and say which version reads better."

## Verdicts

Second run, on the Flash model. The batch's attempt ended with a server error (`INTERNAL (code 500)`) and a reply cut short, which the script then treated as final; this file is from a separate `tip outside-review CH=13` run, whose first attempt exceeded the output token limit, whose second was empty after a denied tool call, and whose third answered. Applied in commit d78cf154, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied, with a different fix. A probe matched a `Q()` with `x == 0` against `case P(x=0):` and fell through to `case _`, so the class pattern's `isinstance()` test comes before the attribute test and "any object with the named attributes" overstated it. The sentence now reads "an instance of any class with the named attributes, data class or not", singular where the reviewer wrote "instances".
2. Applied, with a different fix. A probe `case {"type": "click", **rest}:` bound `rest` to `{'x': 1, 'y': 2}`, a `dict`, so "binds whatever keys" named the wrong thing. The sentence now says it binds "the pairs whose keys the pattern did not mention, as a `dict`", keeping the chapter's "did not mention" and the sequence-counterpart clause that follows.
3. Applied, with a different fix. `compile()` of `case Webhook(...):` raised `SyntaxError: invalid syntax`, and `notifications_match.py`'s `render()` uses `case Email(subject):` while `cost()` uses `case Email():`. The sentence now says "until you add a `Webhook` case to each" and then gives the two cases, `case Webhook(url):` in `render()` and `case Webhook():` in `cost()`, with `url` the field exercise 4 specifies.
4. Applied, with a different fix. The Solutions answer matches on `sign(p.x), sign(p.y)` with one `case` per quadrant and `case (0, _) | (_, 0):` for the axes, so the statement's "one `case` per sign combination, using `|` alternations" described neither the per-quadrant cases nor the single alternation. The exercise now says to match on `sign(p.x), sign(p.y)` "with one `case` per quadrant, a `|` alternation for the axes, and no guards"; the generated statement in the Solutions file followed in the same commit.
