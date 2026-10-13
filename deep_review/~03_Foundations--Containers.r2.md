> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 03_Foundations--Containers (2026-10-13)

Nothing here needs your decision, so the file has no live blocks.
I read the chapter and its Solutions file against the 2026-09-29 review (`~03_Foundations--Containers.md`) and `deep_review_db.md`, on Python 3.15.0 (uv's managed build) and `ty` 0.0.86.
Probes confirmed slice clipping (`xs[3:99]` is `[40, 50]`, `xs[99]` raises an `IndexError`), that updating a `dict`'s values during iteration raises no exception, that `for k in list(d)` deletes cleanly, that a keys view shows a later insertion, both `remove()` exceptions, and Solutions 10's `cannot use 'dict' as a dict key` message.
Stripping each `# type: ignore` in the four immutability listings drew one `ty` error per line, so the rewritten type-checker sentence holds.
The timing listings ran three times each with `--numbers`: list/deque ratio 64, 95, 90 against the `* 20` threshold; membership gaps 1,137 to 1,538 small and 12,652 to 14,210 large (8.7 to 12 times); Solutions 1 at `n = 2_000`, about 9 to 10 times.
`tip verify-ch CH=03 ISOLATED=1` passed 27 of 27 before and after.

## Applied directly

Chapter, teaching:

- Sets, after `membership_cost.py`: O(n) and O(1) were used with no definition, and this is the first chapter to use them. Added a two-sentence definition before the first use.
- Same paragraph: "At ten times the size the ratio is bigger rather than the same" gave no reason. Now says the `list` search takes roughly ten times as long while the `set` search holds, which the measured gaps bear out. The "probe value is missing on purpose" point became its own paragraph.
- Dictionaries: "A `dict` has three views" used *view* with no definition, and `MappingProxyType` italicized it later as a new term. *View* is now defined here (reads the current contents, not a copy). "Iterating over the `dict` iterates over `keys()`" joined the `items()`-slip paragraph it sets up.
- `slicing.py`: added `xs[3:99]` and a sentence contrasting slice clipping with an index's `IndexError`, the near-miss a reader expects.
- After `dict_iteration_trap.py`: a reader would conclude that any change during iteration fails. Added that updating an existing key's value keeps the size and is safe, and that `for k in list(d):` deletes as you go, matching the `xs[:]` advice for lists.
- Sets: `remove()` raising a `KeyError` now names the lookalike, `list.remove()`'s `ValueError`.
- `deque`: the `deque.py` lead-in ended "A `list` is fast only at its append end:" before a listing with no `list` in it. Moved the point to the `list_as_deque.py` follow-up (`append()`/`pop()` O(1), left end O(n)), gave `deque_timing.py` a lead-in, and said after it what the `* 20` comparison checks.
- `deque`: the closing paragraph mixed queue advice with `maxlen`. `maxlen` is now its own paragraph and points back to `deque.py`'s `window`.
- Immutability: the `MappingProxyType` sentence sat in the trio paragraph two listings before its section. Moved into the `mapping_proxy.py` lead-in, which now says it is read-only without being immutable and ties it to the `dict` views.

Chapter, prose:

- "The first line creates a `list`" became "The literal `[1, 3, 5]` creates a `list`"; "The last two lines use both directions" names `first, *rest = evens` (positional pointers).
- `dict_ops.py`: "The last line feeds `dict()`..." rewritten to show what `zip("abc", [1, 2, 3])` yields, then what `dict()` accepts.
- "Only the `list` hides the mistake. The `dict` and the `set` both report it." became one contrast sentence.
- "Modifying an immutable container is a type error as well as a runtime error" read as `TypeError` beside an `AttributeError` listing. Now says the type checker reports the attempt before the program runs.
- "A `frozendict` owns its contents" is now literal: it holds its own entries, copied in when you build it.
- "Four of these show up consistently" became "Four of them come up often".

Solutions:

- Exercise 10: "The runtime exception is the point of the listing" was false for a four-step listing. Now says why the line carries `# type: ignore`.

## Considered and declined

- **Solutions 5's title, "Four slices of one list."** The exercise asks for three slices; the solution shows four expressions (two forms of the reversed middle). The title counts the expressions, and retitling would turn every exercise-5 reference NEW in `exercise_refs`.
- **Solutions 4's `str(e).partition(" (")[0]`.** It looks incidental, but the full message is 63 columns as a marker, over the 60 limit.
- **Solutions 1's "several times faster" at `n = 2_000`.** Measured about nine times here. "Several" is safe across machines.
- **"`*_` discards a run of elements."** It binds a list to `_`, but "discards" states the convention's intent, and the sentence opens with "By convention".
- **"A dictionary key must be hashable, though it need not be immutable."** Still unexplained; the 2026-09-29 review declined the example it needs (chapter 07 material).

## For the session

- `tip prose CH=03` now reports stale baseline entries for this chapter: watch words (`A CODE is fast only at its append end`, `Only the CODE hides the mistake`, `is a read-only *view* onto...`), stranded (`so changes to that CODE still show through`), positional (`The first line`, `The last line`). All were removed by the edits above; no new hits.
- `verify-ch` resynced `Examples/03_Foundations--Containers/slicing.py`.
