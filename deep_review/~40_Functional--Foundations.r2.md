> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 40_Functional--Foundations, second round (2026-09-29)

This run follows the completed review of 2026-09-25 (`~40_Functional--Foundations.md`).
I read that file and `deep_review_db.md` first and re-proposed nothing in either.
Nothing here needs your decision, so the file has no live blocks.

Five commits touched the chapter after the first review closed.
Two of them left damage, both from cut lead-ins, and both are repaired below.

Probed on `ty` 0.0.84 and the pinned interpreter:

- The `Placeholder` gap is still open.
  `partial(clamp, 0, Placeholder, 100)` draws `invalid-argument-type`
  (expected `int`, found `_PlaceholderType`),
  the result reveals `partial[() -> int]`,
  and each call draws `too-many-positional-arguments`.
  The chapter's paragraph holds as written.
- `p.x = 5` on the record draws `invalid-assignment`, and `setattr(p, "x", 5)` draws nothing.
- `MAX_SIZE = 200` and `values.append(4)` are both rejected; `CONFIG.append(3)` on a `Final[list[int]]` is accepted.
- Solutions 6's two quoted diagnostics match today's text.
- `compose(label, increment_then_double)` reveals `(int, /) -> str`.
- Every `#:` marker matches, and every anchored link resolves to a section that covers what the sentence credits it with.

`tip verify-ch CH=40` passes 24 of 24.

## Applied directly

Damage from edits made after the first review:

- Higher-Order Functions: the fix triage cut "The lambdas above exist to show the machinery."
  The next sentence, "For these cases Python offers a lookalike," then pointed at the `sorted()` and `list.sort()` paragraph.
  It now opens "When you would write a fresh lambda for `map()` or `filter()`".
- Leaving a Gap with `Placeholder`: the same triage cut "which the paragraph after it explains",
  so the lead-in announced two `# type: ignore` comments and gave no reason.
  The reason now comes first: "The type checker does not follow `Placeholder`, so the listing carries two `# type: ignore` comments".

Corrections:

- Pure Functions: "If you delete the second `total = 0`" named the wrong line.
  `why_pure.py` has three such lines, and deleting the second one changes nothing, because `total` is still 0 from the first.
  The sentence now says "the last", and gives the reason the assertion fails (`total` is still 5, so the call returns 10).
- Closures: "The type checker's report is the more useful one" gave no reason, and `ty`'s message names the missing declaration no better than the runtime's does.
  What `ty` adds is timing, so the sentence now reads "The type checker finds the same mistake before the program runs."
- Higher-Order Functions: the lambda paragraph's example was `key=lambda w: w.lower()`,
  a lambda around a function that exists.
  Four paragraphs later the chapter tells the reader to pass the existing function in that case.
  The example is now `key=lambda w: (len(w), w)`, which has no named equivalent.

Teaching additions:

- Immutability: after `immutability.py`, a pointer to `copy.replace()` in chapter 12.
  The listing restates every field to build `moved`, which does not scale past a few fields, and the chapter never named the idiom.
- A Stable Hash: a frozen record that holds a `list` is still unhashable.
  The section said freezing a data class gives it a hash, and a reader who then keys a dictionary with a record holding a list gets a `TypeError`.
  Three sentences and a link to chapter 20's `frozen_leaky.py`, which demonstrates it.
- Closures, `make_counter.py`: the prose said each call builds an independent counter, and the listing built one.
  It now builds a second, `fresh`, which prints 1 after `tally` has reached 3.
  `tally` is still called three times, so the `{'count': 3}` reading in the privacy paragraph holds.
- Closures: `global` against `nonlocal`.
  The chapter uses `global` in `pure_functions.py` and `nonlocal` here and never contrasted them,
  while chapter 05 sends the reader to this section for `nonlocal`.
  The `nonlocal` paragraph now links back to "Names Inside a Function" and says what `global count` does in its place (a `NameError`, probed).

Prose:

- Opening: "is already safe to run in parallel" followed "already correct" one sentence earlier. The second "already" is gone.
- Dispatch: "The dispatch code itself never changes" is now "stays the same", and "a plain `KeyError`" lost "plain" in the prose and in the listing's comment.

Solutions:

- Exercise 5: the listing carried a `# type: ignore` that the prose never mentioned.
  A new paragraph says `ty` reports `positional-only-parameter-as-kwarg` where the partial is built, while the runtime waits for the call.
- Exercise 2: cut "exactly the way" and "really is just adding one row ... as the chapter claims".
- Exercise 7: "its `__repr__` has nothing to report" is now the mechanism: the iterator has computed nothing, so `repr()` shows the type and an address.
- Exercise 9: "the one-argument callable `filter()` wants" is now "requires".

## Considered and declined

- `ty`'s message is ``Name `count` used when not defined``, with backticks,
  and the chapter and Solutions 8 quote it with apostrophes inside a code span.
  Quoting it faithfully needs a double-backtick span, and no chapter uses one.
- Putting the Pieces Together says you can "cache" the report.
  `functools.cache` on `report()` raises a `TypeError` when the argument is a `list`, and works with a tuple.
  The sentence is about what an unchanged input allows, and the hashing section already says a cache entry is normally a tuple or a record.
- The rule of thumb on `map()` against a comprehension is stated twice, two paragraphs apart.
  The second statement closes the paragraph about return types, where it reads as a summary.
- The `Placeholder` paragraph says "a type checker limitation" and then names `ty`.
  Pyright reports the same mismatch, since both read the same stub, so the general wording is right.
- Exercise 3's solution confirms independence by printing three results.
  `inspect.getclosurevars()` would show the three `factor` values directly, but the chapter's listing already does that.
