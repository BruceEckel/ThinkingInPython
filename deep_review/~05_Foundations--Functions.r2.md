> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 05_Foundations--Functions (2026-10-13)

No live blocks: every finding had one sensible fix, so all of them are applied below.
I checked each claim against its listing and the sections it links (chapters 2, 8, 14, 15, 17, 40, 44), on Python 3.15.0 (uv's managed build) and `ty` 0.0.86.
Probed and left as written: both quoted `SyntaxError` messages, `def f(*, a=1, b):` compiling, `dict.get`'s signature `(self, key, default=None, /)`, `sentinel("M") is sentinel("M")` being `False`, `*` unpacking a set and a string, `operator.itemgetter(-1)` matching the lambda's order, `ty` reporting both deliberate misuses in `param_markers.py` through `expect()`, and `ty` accepting a renamed positional-only parameter in an override while reporting `invalid-method-override` for the same rename without the `/`.
`tip verify-ch CH=05 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after; `tip prose CH=05` reports nothing new.

## Applied directly

Chapter:

- "Default Arguments", opening: "keyword arguments let callers pass them by name" could read as passing the default values; now "pass arguments by name".
- "The Mutable Default Trap": "Underneath, a parameter is ..." opened on a figure with no stated link to the trap. Now "The trap follows from how Python passes arguments.", and the paragraph ends on the sentence `mutating_arguments.py` demonstrates ("A caller that passes a mutable object sees the changes the function makes:") instead of on `bad_append()`, so the lead-in introduces the listing that follows it.
- "Sentinel Values", after `sentinel_default.py`: "`None` cannot also mean 'not supplied'" gave the stored `None` as the reason, which bears on what `get()` returns, not on the default parameter. Now the stored `None` means a `None` from `get()` cannot also mean "no such key", and a new sentence says the `MISSING` test leaves `None` free as a real default, the case the section's lead-in names.
- "Unpacking Arguments": the paragraph after `unpacking_arguments.py` held two concepts (the forwarding shape, with `expect()` and Decorators, and functions as first-class objects). Split at that seam.
- After `forwarding_collision.py`: "spreads `args`, which holds the items of `nums`, positionally" held its adverb a clause away from its verb. Now "passes the items of `nums` positionally", split into two sentences. Added that the error arriving one level down is why `calling report` prints before the `TypeError`, so the reader can read the mechanism from the output.
- "Positional-Only and Keyword-Only Parameters", last paragraph: split the `**kwargs` point from the override point, and replaced "instead of clashing with the parameter" with what happens without the `/` (the keyword gives `trace()`'s own `func` a second value and the call raises a `TypeError`; probed).
- "Lambdas": split the single-expression limit from the assigned-lambda paragraph (two concepts).
- Exercise 10 added: `trace(report, "point", func="f")` with and without a `/` after `func`. The `/`-frees-the-name claim was the one claim in its section with no listing and no exercise. Added at the end, so no number moves.

Solutions:

- Exercise 7: "So `"Bob"` goes into `facts`" is "So `facts` collects `name="Bob"`"; the dictionary holds the key `name`, not a bare `"Bob"`.
- Exercise 10: new, with a hint, a listing that runs both versions (`positional_trace()` for the second so both run in one file), and an opening that contrasts it with `forwarding_collision.py`: here `TypeError` comes from binding `trace()`'s own arguments, so no `calling report` line prints. `ty` reports the deliberate clash (`parameter-already-assigned`), so the line carries `# type: ignore` (probed both ways).

## Considered and declined

- "Rebinding one does not." after `mutating_arguments.py` is a negative, but it is half of a real contrast with the sentence before it. Kept.
- The chapter prose could point at exercise 10 with "(see exercise 10)". Left out: the new paragraph states the claim, and the exercise is where the reader sees the missing `calling report` line.
- Solutions exercise 6's hint says the section shows `*` "spreading a sequence", where the chapter now says "any iterable". Left: the section's examples are a list and a tuple, and the hint describes what it shows.

## For the session

- `tip verify-ch` generated `Solutions/05_Foundations--Functions/exercise_10.py` (untracked), the extracted copy of the new solution listing. It is correct; commit it with the README.
- No new exercise-refs or quoted-diagnostics hits. Nothing found in other chapters.
