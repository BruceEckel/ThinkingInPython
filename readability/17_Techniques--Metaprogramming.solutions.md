> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/17_Techniques--Metaprogramming/README.md`, 2026-10-16.
This file is the applied-directly record and holds no live block.
The prose carries no Tier 1A vocabulary, no stacked transitions, and no watch-list hits beyond reflexive "itself" and one ruled-fine "only a X".
The edits split "and" joins between clauses with different subjects, fix one colon carrying two claims, give two paragraphs a seam each, and replace two phrases that misstated or blurred the mechanism ("a deeper descendant has no parent to extend", "the interpreter enforces silently").
`tip verify-ch CH=17 ISOLATED=1` passed after the edits.

## Applied directly

- 91, empty adverb: "prunes its parent automatically" -> "prunes its parent"; the next sentence, "The `Color` class stays as written", carries the no-edit point.
- 383, positive statement and clarity: "so a deeper descendant has no parent to extend" -> "so the hierarchy below a final class stays empty".
- 526, accuracy: "states the rule, which the interpreter enforces silently" -> "states the rule behind the collision"; the interpreter raises a `TypeError`, so "silently" misread, and the paragraph's "terse 'instance lay-out conflict'" keeps the contrast.
- 539, one concept per paragraph: the sentence on why the chapter's `metaclass_layout_conflict.py` keeps its `# type: ignore` is now its own paragraph, apart from the runtime-versus-static contrast.
- 598, "and" joining different subjects: "`describe()` is a module-level function, and the class that carries `unit` comes into existence later, when `type()` runs" -> "`describe()` is a module-level function, defined before `type()` creates the class that carries `unit`" (checked against `exercise_7.py`).
- 694, colon carrying two claims: "shows the same limit for the namespace: its `__init__()` writes ..., and `hasattr()` reports `False` ..." -> three sentences, "... for the namespace. Its `__init__()` writes an `added_in_init` key into `namespace`. `hasattr()` then reports `False` ..." (checked against the chapter's `new_vs_init.py`); paragraph rewrapped.
- 821, present tense and one concept per paragraph: "The injected statement ran before that lookup" -> "runs"; the sentence on restoring the `KNOWN_COMMANDS` check is now its own paragraph, apart from why the `KeyError` arrives too late.
- 908, "and" joining different subjects, twice: "`NoDuplicates` raises an exception on a repeated key, and `KeepFirst.__setitem__()` returns early instead" -> two sentences; "passes it to `__setitem__()`, and the early return discards it" -> "passes it to `__setitem__()`, where the early return discards it"; paragraph rewrapped.
- 917, "and" joining different subjects: "after its body has finished executing, and by then the body has run" -> "after its body has finished executing. By then the body has run".

## Considered and declined

- 364-368 against 321-326, §70 restatement: exercise 4's "Accept the header keyword" step repeats that the `False` default covers `Open`. Kept: the opening paragraph shows the failure without a default, and the step adds that the default keeps every other header short.
- 808-816 against 751-758, treadmill: exercise 9's "Close the second splice's string" step re-explains the `SyntaxError` and the `Y = """` opener from the paragraph above the listing. Kept: the Solutions convention opens with the mistake and then walks the listing, and the walkthrough adds the trailing `#` and the order in which the splices compile.
- 659-660, "so `Tag` stays out" after "holds `object` alone": kept, since it ties the prediction to the class the exercise moves.
- 534-536, "The runtime message tells you something collided. The static diagnostic tells you which two bases collided and why": partly restates "marks both bases to show which pair conflicts". Kept as the closing contrast, which adds the timing (typing the header against importing the module).
- 613-614, §29 echo: "**Inherit the base's arithmetic.** `Celsius` inherits `float`'s arithmetic" restates its bold label. The bold step labels are the Solutions convention, and the sentence goes on to the result type.
- 802-804, "and" in "The payload's `pass` fills the body of a class `X`, and the dedented `print(...)` after it sits at module level": two steps in describing one payload, so the "and" is additive.
- 391, "refuses only a class whose `__mro__` holds": the ruled-fine "only a X" shape, stating the restriction.
- 91, 380, "adds itself", "declared itself final": reflexive (recurring keep).
