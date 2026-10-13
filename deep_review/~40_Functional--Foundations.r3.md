> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 40_Functional--Foundations, third round (2026-10-13)

This run follows `~40_Functional--Foundations.r2.md` (2026-09-29).
I read it, the first-round file, and `deep_review_db.md`,
and re-proposed nothing any of them settled.
Since round two, the chapter took the Gemini outside-review fixes,
the commerce sweep, and the listing-design change that gave `placeholder.py`
a declared `Callable[[int], int]` and one `# type: ignore`.
No live blocks: every finding had one sensible answer and is applied below.

Probed on `ty` 0.0.86 and Python 3.15.0 (`uv run`):

- `placeholder.py`: with the comment removed, `ty` reports `invalid-assignment`
  (`partial[() -> int]` to `(int, /) -> int`) and `invalid-argument-type`,
  both on the assignment line, as the prose says;
  `percent()` with no argument draws `missing-argument`.
- `p.x = 5` draws `invalid-assignment`, and `setattr()` passes;
  `MAX_SIZE = 200` and `values.append(4)` are rejected;
  `CONFIG.append(3)` on `Final[list[int]]` passes.
- Deleting `nonlocal` draws ``Name `count` used when not defined``;
  `global count` raises a `NameError`; `cell_contents = 100` rewrites the counter.
- `compose(label, increment_then_double)` reveals `(int, /) -> str`.
- Solutions 5's `positional-only-parameter-as-kwarg` and Solutions 6's two quoted diagnostics match.
- Every `#:` marker matches, and each linked section supports the sentence that cites it.

`tip verify-ch CH=40 ISOLATED=1` passed 27 of 27 before and after.

## Applied directly

Chapter:

- Pure Functions: "That line is the fixture" pointed two sentences back; now "The reset at `[1]` is the fixture".
- Immutability: "An immutable value stays what you last read" followed the `([1], 2)` example, which shows a tuple whose contents change.
  Now "A value that is immutable all the way down, such as a tuple of strings, stays what you last read", and the guarantee sentence stands on its own.
- Immutability, cost paragraph: "A large structure that changes often copies the whole value on every change" restated the sentence two lines up.
  Now it gives the consequence: "those copies add up in time and memory."
- Higher-Order Functions: the `list.sort()` link pointed at the top of Containers; it now targets `#growing-shrinking-and-sorting`, the section that shows `sort()` returning `None`.
- Closures: "The last two lines read the captured values" was a positional pointer; now "The two `inspect.getclosurevars()` calls read the captured values."
- Closures: "Nothing changes `factor` after capture" repeated the sentence two lines up.
  The `withdraw()` contrast now names what the two share and where they differ: `withdraw()` also reads an outside name, but each call changes it, so each result depends on every call before it.
- Placeholder: cut "A `Placeholder` reserves the position and leaves the value to the caller", a near-verbatim repeat of the definition above the listing.

Solutions:

- Exercise 3: "each `factor` is reachable only through the one function that captured it" contradicted the chapter, which shows `inspect.getclosurevars()` and `__closure__` reaching it.
  Now "has a name only inside", the chapter's own claim.
- Exercise 6: "reports one error here, not two, and the one it reports is the assignment" is now "reports the reassignment and accepts the append".

## Considered and declined

- "Python's immutable types share no structure" could be read as wrong, since a rebuilt tuple shares its element objects.
  In context it means persistent-structure sharing, which the same paragraph names, so it stays.
- The Immutability cost paragraph holds both the sharing benefit and the copying cost.
  The benefit is two sentences that set up "That safety requires copying", a claim and its consequence, so it was not split.
- "Returning a function is the other half of the definition" after `higher_order.py` points forward with no location.
  The section's last paragraph opens "A higher-order function can also return a function", so the reader meets it within the section.
- "a closure is one way to let exactly one function change it": the "exactly" is a count, which the style rule allows.

## For the session

- `tip watch-words` reports a stale baseline entry for Solutions 40 exercise 3
  ("because each CODE is reachable only through the one function that captured it"); my rewrite removed that sentence.
  The entry in `tools/data/` can be dropped.
- Nothing in another chapter needed a fix.
