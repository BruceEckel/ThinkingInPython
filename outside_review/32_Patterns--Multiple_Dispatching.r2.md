<!-- outside review of Chapters/32_Patterns--Multiple_Dispatching.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `32_Patterns--Multiple_Dispatching.md` chapter:

**1. Section: Operators Dispatch Twice (Correction of contradictory claim regarding operand decline)**

* **Target Text:** "`Meters.__add__()` runs and declines the string, and `str` defines no `__radd__()`. Python raises the `TypeError` once both sides have declined."
* **Issue:** The sentence directly contradicts itself. Because `str` does not define `__radd__()`, the right operand is never called and never declines; Python raises `TypeError` because the left operand returned `NotImplemented` and the right operand provides no reflected method to retry. Line 37 of `radd_dispatch.py` makes the same mistake in its comment (`# Both sides decline`).
* **Instruction:** In `radd_dispatch.py` line 37, change `# Both sides decline` to `# Left declines; str defines no __radd__`. In the prose, change "Python raises the `TypeError` once both sides have declined." to "Python raises the `TypeError` because the left operand declined and the right operand has no `__radd__()` to retry with."

**2. Section: Operators Dispatch Twice (Ambiguous phrasing of operand position)**

* **Target Text:** "The fallback is how a type written decades after `int` can add itself to an `int` on the left."
* **Issue:** The phrase "add itself to an `int` on the left" can be misread as meaning the new type is positioned on the left (`Meters(3) + 4`). When the new type is on the left, its own `__add__()` handles the operation on the first dispatch; the fallback `__radd__()` only comes into play when the new type is on the right of an `int` (`4 + Meters(3)`).
* **Instruction:** Clarify the position by revising the sentence to: "The fallback is how a type written decades after `int` can be added to an `int` that sits on the left."

**3. Section: The `singledispatchmethod` Trap (Clarification of dispatcher mechanism)**

* **Target Text:** "`functools.singledispatchmethod` combines the two dispatches in one decorator. It dispatches once on `self` through ordinary method resolution, then again on its first argument through `singledispatch`."
* **Issue:** The `@singledispatchmethod` decorator itself does not combine two dispatches in one decorator; it only wraps `singledispatch` so that dispatch inspects the first argument after `self`. Describing it as combining both dispatches in one decorator obscures the trap: declaring it once on a base class fails precisely because that single decorator does not dispatch on `self` across subclasses, requiring each subclass to define its own distinct `@singledispatchmethod`.
* **Instruction:** Change the target text to: "`functools.singledispatchmethod` enables double dispatch when combined with method overriding. Ordinary method resolution dispatches first on `self`, and the method's decorator then dispatches on the first argument through `singledispatch`."

**4. Section: Methods or Table (Omission of mechanism for subclass override)**

* **Target Text:** "`DampPaper`'s own result against `Rock` comes from `Rock.eval_paper()`, a method `DampPaper` cannot change, so its `compete()` answers before making that call."
* **Issue:** Earlier in the section, the prose argued that double dispatch eliminates the `isinstance()` ladder inside `compete()`. However, `paper_scissors_rock_subclass.py` uses `if isinstance(item, Rock):` inside `DampPaper.compete()`. The text explains why `compete()` must answer early, but leaves unnamed the fact that answering before double dispatch forces the subclass back to an explicit type test because `Rock` has no `eval_damp_paper()` method.
* **Instruction:** Add a clarifying sentence directly after the target text: "`DampPaper.compete()` must test `isinstance(item, Rock)` by hand because `Rock` knows only `eval_paper()`, so double dispatch cannot resolve a subclass interaction without editing the existing classes."

## Verdicts

Second run, on the Flash model. Applied in commit 759044bc, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. A probe showed `hasattr(str, "__radd__")` is `False`, and `M() + "four"` called `M.__add__()` alone before the `TypeError`, while a `str` subclass with `__radd__()` got the reflected call, so the right operand never declines here. The prose now says Python raises the `TypeError` with the left operand declining and no reflected method to try, and the listing comment reads `# Left declines; no str.__radd__()`, since the reviewer's wording runs the line to 64 columns.
2. Applied, with a different fix. "add itself to an `int` on the left" can attach "on the left" to the new type, the reverse of the case `__radd__()` serves. The sentence now says the new type "can sit to the right of an `int` in a sum."
3. Applied, with a different fix. A probe showed `compete` lives in `Item.__dict__` and every subclass reaches that one descriptor, so the decorator supplies the second dispatch alone and method resolution supplies the first, which is the trap the section shows. The sentence now says `singledispatchmethod` supplies the second dispatch for a method, with ordinary method resolution dispatching on `self`, and names the first argument after `self` (chapter 41's wording); the reviewer's "enables double dispatch when combined with method overriding" was left out, since the decorator needs no overriding to dispatch.
4. Applied, with a different fix. The section says both patterns replace the `isinstance()` ladder, and `DampPaper.compete()` then tests `isinstance(item, Rock)` with no comment. One sentence now names that test as one rung of the ladder, needed because `Rock` has no `eval_damp_paper()` to dispatch to. The reviewer's claim that double dispatch cannot resolve a subclass interaction without editing the existing classes is wrong for the listing: `DampPaper.eval_rock()` resolves the other order of the same duel with no edit to `Rock`, and `Rock().compete(DampPaper())` prints `draw`.
