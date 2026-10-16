> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Context Managers, Solutions

The Solutions file for chapter 15 carries no Tier 1 or Tier 2 vocabulary,
no signposting, and no significance inflation.
The seven changes below cut two repeated claims, split two "and" joins
that hid a consequence or a fresh claim, correct one verb that made
`__exit__()` the actor of propagation, and split exercise 7's closing
paragraph at the seam between the empty run and the reason `ExitStack`
exists.
Exercise 8's claim that the `finally` is the one difference from the
chapter's `no_finally.py` apart from the function's name was checked
against that listing.
This file holds no live block, so it is the record of the direct edits.
Line numbers refer to the file before the edits.

## Applied directly

- Lines 101-103, treadmill (repeated claim): "so `expected` receives one `types` argument, and `issubclass()` accepts a tuple as its second argument" -> ends at "argument."; lines 127-129 state the `issubclass()` fact in the same rung. (Close alternative: split into two sentences and keep both.)
- Lines 198-200, dangling generalization: "exit in reverse order, for any number of managers on the line" -> "exit in reverse order. The reversal holds for any number of managers on the line.", matching exercise 7's wording.
- Lines 398-399, ambiguous "then" and an "and" hiding a consequence: "A block that finishes cleanly then fails. `__exit__()` receives `None`, and `issubclass()` raises a `TypeError`." -> "In that version a block that finishes cleanly fails. `__exit__()` receives `None`, so `issubclass()` raises a `TypeError`."
- Line 439, wrong actor: "suppresses `KeyError` and propagates everything else" -> "suppresses `KeyError` and lets every other exception propagate"; `__exit__()` returns a value, and Python does the propagating.
- Lines 441-443, treadmill: "The `ValueError` block confirms the propagation." restated its own bold label; folded into "In the `ValueError` block, `ignore_missing`'s `__exit__()` returns `False`, so the exception propagates ...".
- Line 522, repeated tag: "for any number of names, zero included" -> "for any number of names"; the next paragraph covers the zero case and ends on the same "zero included".
- Lines 524-527, one concept per paragraph: split before "That degenerate case shows why `ExitStack` exists", with the pointer replaced by its noun, "The empty run shows why `ExitStack` exists."

## Considered and declined

- Lines 70-72, "The order is the same whether you write the nesting as two separate `with` statements or as one comma-separated line": restates the sentence before it in part, but it generalizes from the chapter's one-line example to the exercise's nested form.
- Line 66, "Entering is outside-in ..., and exiting is inside-out ...": "and" between different subjects, but the two halves of a contrast, which the rule keeps.
- Lines 437-439, "A truthy value suppresses the exception, and a falsy value lets it continue": the two halves of a contrast.
- Lines 445-448, "Without the test, `issubclass(None, KeyError)` would raise a `TypeError`": repeats the Solution's opening paragraph, but the bold-labeled step reads as a unit and loses its reason without it.
- Lines 626-629, "and only then does the exception propagate out of the `with` statement": two steps of one sequence; the "only" marks a real ordering restriction (recurring keep).
- Lines 633-634, "so the `print()` after the `yield` does not run": a negation that is the claim, the contrast with exercise 8's `finally`.
- Lines 265-268, "A third nested `lease()` would block forever in `get()`": "forever" states the deadlock literally.
- Lines 335-343 and others, uneven hand-wrapping around the bold step labels: rendering is unaffected, so only edited paragraphs were rewrapped.
