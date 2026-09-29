> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 10_Foundations--Cleanup (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I ran every listing and every solution directly on 3.15.0rc2, with stderr visible.
I checked the quoted `__del__()` warning word for word against the 3.15 data-model page,
and the `finalize()` claims (`atexit` default, at-most-once, the bound-method warning) against the 3.15 `weakref` page.
I read the five sentences other chapters write about this one (4, 15, 26, 30, 35); all five hold.
`tip verify-ch CH=10` passes 24 of 24, and `tip verify` passes in the worktree.

## Applied directly

Chapter, corrections:

- `del_swallows.py` paragraph: "no `finally` runs" is false as written.
  A `finally` around the `del` runs on the normal path.
  The clause is gone; "no caller can catch it" carries the point.
- "Reference Cycles Delay Destruction" opened with "Unpredictable timing is one of two problems with `__del__()`",
  after a section that lists four (when, whether, vanished globals, swallowed exceptions).
  Now "A reference cycle postpones `__del__()` too."
  The closing "Cycles are a second reason" became "one more reason" for the same count.
- `finalize_trap.py` paragraph: the `atexit` sentence said turning `atexit` off makes `False True` answer "whether the collector reclaimed each object".
  `False True` prints with `atexit` on or off.
  With it on, a probe prints `L closed` after the program's last line.
  The paragraph now says that, and says the listing turns `atexit` off so its output ends at `False True`.
- Last paragraph of "Watching Objects Without Holding Them":
  "The `__del__()` version in `cleanup.py` waits for interpreter shutdown" blamed `__del__()` for a delay the `counters` list causes.
  A `Counter` popped from the list runs its `__del__()` at once.
  The contrast is now what the count depends on: `__del__()` running and succeeding, against a registry that runs none of your code.
- Exercise 5: "make `close()` print `name, "closed"`" names a variable `close()` does not have. Now `self.name`.
- The HTML comment over the shutdown transcript now says 3.15.0rc2, the build I checked the order on.
  The checker-order claim also holds: a simulated checker run finalizes First, Second, Third.

Chapter, teaching:

- `__slots__` appears in "A Slotted Class Needs `__weakref__`" eight chapters before chapter 18 teaches it.
  Added a one-sentence definition and a link to `18_Techniques--Performance.md#slots`.
- `closable.py` used `__enter__()` and `__exit__()` without saying what calls them.
  The lead-in now links chapter 4's `with` section, and one sentence after the listing gives the mechanism:
  `with` calls `__enter__()` at the top, `__exit__()` on the way out, and `__exit__()` calls `close()`.
- `faulty_init.py`: the advice "acquire the resource in `__enter__()`" left out the near-miss.
  `__exit__()` runs only after `__enter__()` returns, so an `__enter__()` that fails after acquiring leaks the same way.
  The paragraph now says so, points to exercise 7, and states the rule that covers both methods.
  The paragraph's first two lines repeated the lead-in before the listing almost word for word; cut.
- New exercise 7 and its solution (`exercise_7.py`, `Faulty` and `Guarded`).
  The `close()`/`with` half of the chapter had no exercise, while `weak_value.py` had three.
  `tools/data/exercise_refs_baseline.txt` gained the one reference, after a read against the title.
- `finalize_trap.py`: nothing said why `gc.collect()` fails on `Leaky`, right after a section that taught `gc.collect()` as the cure for a cycle.
  Added: the object is reachable through `finalize()`'s registry, so it is not an unreachable cycle.
- `resource_warning.py`: one sentence on why `gc.collect()` follows `del f`.

Chapter, prose:

- Heading "A Raising `__init__()` Leaks the Resource" is now "An `__init__()` That Fails Leaks the Resource".
  The anchor `#raising-init-leaks` is explicit and unchanged; nothing links to it.
- "re-raising" now has its object ("re-raising the exception").
- The `gc.get_referrers()` sentence ran 28 words with "without collecting or destroying anything" attached to the wrong verb. Split.
- "Freeing it takes the cyclic garbage collector": "it" was five sentences from the node. Now "Freeing the node".
- "The second is `weakref.finalize()`" sits two subsections after "The first". Now "The second reliable approach".
- "at `a`'s destruction" is now "when the `Connection` is destroyed"; the listing registers one finalizer per connection.
- The `id(self)` sentence ("one then displaces the other") now says which key causes the collision and which object is displaced.

Solutions:

- Exercise 3: the `#:` markers sat in one clump at the listing's end. They now follow the statements that print them, as in `cleanup.py`.
- Exercise 1: "both spellings" is now "both forms"; "the moment a second name enters the picture" is now "once a second name refers to the list".
- Exercise 4: "the registry itself is what keeps them all alive" is now "the registry keeps them all alive".
- Exercises 5 and 6: three "exactly" intensifiers dropped.

## Considered and declined

- **`closable.py`, `faulty_init.py`, and `exercise_7.py` keep `try`/`except` that prints the exception.**
  The house rule prefers `expect()`, but `expected()` is a context manager,
  and wrapping `with Socket("B")` in `with expected(RuntimeError)` puts a second context manager in the listing that introduces the first.
- **The PEP 442 sentence stays.**
  It reads like the version history the standing rejection bars, but it is language history from 2014, not a tool caveat,
  and a reader who meets the old advice ("a cycle with `__del__()` leaks forever") needs to know it expired.
- **No opening paragraph before the first heading.**
  The blockquote opener is the Part I convention, and the first section starts with the motivation.
- **`self_link()` keeps its name in solution 6**, though it builds a two-object cycle: the exercise says to change that function.
- **Three exercises still use `weak_value.py`.**
  Each asks a different question (rebinding, reading the registry, a strong registry). Exercise 7 fixes the coverage gap without removing one.
- **"That was one run on one machine" and the sentence about the book's output checker stay.**
  The checker claim is true, and it is the chapter's one demonstration that the order varies.
