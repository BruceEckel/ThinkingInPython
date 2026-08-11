When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/30_Observer.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/30_Observer` (9 tests), all six runnable scripts run,
and `box_view.py` is correctly skipped via `tools/data/norun.txt`. The
chapter's checker and runtime claims were probed individually on the
pinned toolchain and all hold: subscribing a `list[str]`'s `append` to
a `Thermometer` is an `invalid-argument-type` under `ty` ("`float` is
not assignable to `str`"), matching the type-parameter paragraph;
bound methods compare equal but not identical (`c.update == c.update`
is `True`, `is` is `False`, and the same holds for the builtin
`lst.append`), matching the unsubscribe discussion; and a probe of the
naive uncopied loop reproduced the silent skip the `list()`-copy
paragraph describes (removing the current element left the next one
unvisited). Incoming links from chapters 19, 21, 28, 38, 39, 41, and
44 all target anchors that still exist, both outgoing anchors into 19
and 28 resolve, `heading_links.py` passes, and
`Solutions/30_Observer.md` covers all four exercises. One factual
error surfaced (the conclusion's "One `Observable` served three jobs";
the async section defines its own `Observable`), and one
exercise-solution mismatch needs a decision (the single live block
below).

## Applied directly

- Conclusion: "One `Observable` served three jobs" is now "One design
  served three jobs". The async fan-out defines a separate
  `Observable` class in `async_observers.py`, so no single class
  served all three; the design is the constant, as the next sentence
  says.
- Exercise 1 reworded to match its solution and the chapter's thesis.
  It asked for a design "in two classes", but the solution builds one
  `Observable` plus callables and opens by saying no separate
  `Observer` class exists, the chapter's own argument. It now asks for
  the smallest `Observable`, built without looking at `observers.py`.
  The alternative, rewriting the solution into the classic two-class
  form, would practice the design the chapter spends its arc
  dismantling.
- `async_observers.py`: added `unsubscribe()` mirroring the
  synchronous class. The following prose discusses "an observer that
  unsubscribes mid-notification", and the class had no method to do
  it.
- AsyncObserver paragraph: added the reverse near-miss, an `async`
  function subscribed to the synchronous `Observable`. Probe-verified:
  `ty` rejects it (`CoroutineType` is not assignable to `None`), and
  the prose notes that a coroutine discarded without an `await` does
  nothing, the silent no-op a reader would otherwise hit at runtime.
- Flag paragraph: "a change raised during notification" is now "a
  change made during notification"; "raised" reads as an exception.
- Cut the empty frame "A few more things about Observer need saying."
  and started the paragraph at its content; "every observer after it
  never hears the change" is now "the observers after it do not hear
  the change" (watch-list "never", and "every ... after ... never" was
  doubly negated).
- Chain of Responsibility sentence: "Collecting a value from each
  observer is a different pattern" is now "Getting a value back is a
  different pattern"; Chain of Responsibility returns the first
  handler's answer, not a value from each.
- Tests intro: added "in subscription order" (the first test asserts
  the order, and the async section's "prints in subscription order"
  contrast now has a taught referent); "changes that happen after it
  subscribes" is now "changes made after it subscribes" (watch-list
  "happen"). Also unified "subscribe order" to "subscription order" in
  the async section.
- Function references get parens per house style: `notify()`,
  `asyncio.gather()`, `gather()`, `run()` in the async section's
  prose. Bare `append` stays where it names the method object being
  passed rather than a call.
- Trimmed "test the model without a GUI" from three statements to one:
  it now appears only before the test listing, where it pays; the
  section intro keeps "`tkinter` plays no part here" and the closing
  sentence keeps the second-view point.
- Ran `make reflow CH=30` over the edited prose.

## Exercise 2 and its solution implement different games

Exercise 2 says: "If any of the squares surrounding the one you
clicked is part of a contiguous patch of the same color, then all the
squares in that patch take on the color you clicked." That is a
spread-outward rule: clicking a square pushes its color into every
same-colored patch touching it. `Solutions/30_Observer.md`'s
`exercise_2.py` implements classic Flood-It instead: the player owns
the contiguous patch containing the origin, and clicking any cell
recolors the *owned* patch to that cell's color, absorbing matching
neighbors. Both are flood games and both support the exercise's
click-count scoring, but the core rule differs, and a reader comparing
their program to the book's would conclude they misread the exercise.

Two coherent fixes: reword the exercise to describe the game the
solution implements (the solution is verified working code, and the
current exercise wording, inherited from the original ColorBoxes
exercise, takes two readings to parse), or rewrite the solution to the
spread-outward rule as written. I recommend rewording the exercise,
along the lines of: "Turn `box_observer.py` into a simple game: you
own the contiguous patch of same-colored squares containing the
top-left corner, and clicking any square recolors your patch to that
square's color, absorbing neighbors that now match. Track the clicks
it takes to make the whole field one color; for competition, alternate
turns between players." Not applied because either end could be the
intended one, and the exercise text is original-book content.

[] Reject

## Considered and declined

- The heading "The Pythonic Observer: a List of Callables" keeps its
  lowercase "a" after the colon: it matches the established family
  ("The Pythonic Factory: a Dictionary" in 27, "The Caretaker: a
  Generic History" in 36).
- Repeated `*Observer*` italics stay: italic pattern names recur
  book-wide (chapter 26 has thirteen `*Proxy*`), so this is
  convention, not the italics-for-emphasis violation it resembles.
- "the *Observer* pattern amounts to nothing more than a list of
  callbacks" stays: a deliberate diminishing comparative, where the
  diminishing is the point.
- The `Observable` and `Thermometer` classes keep hand-written
  `__init__()`s rather than becoming dataclasses: they carry a mutable
  list default and a `super().__init__()` chain, and dataclass
  machinery (`field(default_factory=list)`) would add a second topic
  to listings whose one new thing is the pattern.
- The roadmap paragraph before the Pythonic section ("The rest of the
  chapter shows...") stays: three short functional sentences, and the
  chapter's three-part structure is worth announcing.
