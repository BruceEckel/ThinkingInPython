When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/38_Simulation.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, `ty`, ruff, and pytest are clean on
`build/examples/38_Simulation` (5 tests), all ten runnable scripts
run, and the three windowed views are correctly skipped via
`tools/data/norun.txt`. The rats trace is deterministic (six runs,
identical output), and its claims were probe-verified: the full log
is 18 messages over 9 rats, rat 1 does spawn rat 2 (at `(6, 3)`) and
dead-ends before it, deaths arrive out of number order (1, 2, 3, 5,
6, 9, 8, 7, 4), and the 139 mapped cells equal both the maze's open
cells and a flood fill from the entry. The robot demo was probed the
same way: the teleports fire as `a` then `b`, 10 of the 16 food cells
are eaten (the prose's "the food along its path" is accurate), and
`amaze.txt` on disk really does carry the `#` header line the loader
prose says it drops. Chladni checks out: 1787 is right for the sand
figures, the `cos`-difference field is the standard free-plate
approximation, and `bounce()`'s single reflection suffices even at
exercise 8's `kick=0.5` (maximum displacement 1.0). Inbound anchors
(`#a-robot-in-a-maze` from 06, 08, 09, and 27; bare links from 19,
20, and 39) are untouched, and the `EDGE` Null Object link back to
chapter 20 is intact. One factual error surfaced (the `Blackboard`
field/signature claim, below), and two Solutions listings did not
match what the chapter teaches or what their exercise asks; both are
rewritten. No live blocks remain: every finding had one defensible
answer.

## Applied directly

- `Blackboard` listing: `visited`, `tasks`, and `messages` now carry
  `field(init=False, ...)`. The prose claimed these fields "carry
  `default_factory` instead of appearing in the signature", which was
  false: a `default_factory` field without `init=False` is still a
  constructor parameter with a default. The code now matches the
  stated intent (`Blackboard(maze)` is the whole signature), and the
  prose says what `init=False` and `default_factory` each contribute.
- Intro reordered: the three-simulation overview now opens the
  chapter and the rats/end-to-end/asyncio paragraph follows. Before,
  "Three simulations follow" trailed a paragraph about the first of
  those three, so "follow" pointed backward at its own subject. Also
  "grains that know nothing at all" is now "grains that know
  nothing".
- Trace paragraph reworded: "The first eight log messages come first,
  a trace of the run that nothing else in the chapter needs" needed
  two readings; now it states the print order and closes with
  "eighteen messages, two per rat" (probe-verified).
- The `group` paragraph's pointer at `Robot.room` now says "the robot
  example later in this chapter", marking the forward reference.
- `TYPE_CHECKING` paragraph: cut "which is `Room`'s sole purpose
  here", whose antecedent read as the checker rather than the import;
  the next sentence ("Every use of `Room` below is an annotation")
  already carries that content.
- Teaching addition (mechanism): after the `Coord`-order paragraph, a
  short narration of the move chain ("One move is one chain:
  `doors.open(urge)` ... becomes `robot.room`"), since `Robot.move()`
  is the game's whole loop and no prose walked it.
- Teaching addition: the stage-1 paragraph now explains
  `Room(Empty())`: the robot is the one item that does not become an
  occupant, so its cell behaves like any other empty room once it
  moves away, and `show_maze()` draws `R` by comparing rooms. A
  reader hits that line in `GameBuilder` with no explanation
  otherwise.
- itertools paragraph after the Chladni view trimmed:
  `itertools.cycle()` keeps its explanation (first use in the book),
  but `itertools.count()` was being re-taught argument by argument
  after this same chapter already used it for rat numbers with a link
  to [Iterators]; now a one-line pointer back to that counter.
- Style repairs: "it only names concepts `Maze` uses" is now "it
  names concepts only `Maze` uses" (the modifier sat on the wrong
  verb); dropped "already" from the `__post_init__` paragraph;
  "raises `AttributeError`" is now "raises an `AttributeError`"; "You
  can create a GUI demonstration using the same model" is now "The
  same model drives a GUI demonstration"; "What is missing here is
  the subscription" is now "The missing piece is the subscription";
  serial comma in exercise 3's list of pulled-along signatures.
- `Solutions/38_Simulation.md` exercise 2 rewritten to mirror the
  chapter's classes: dataclass `Rat` and `Blackboard`, and
  `explore()` opening an `asyncio.TaskGroup`. The old solution used
  `asyncio.create_task` plus a while-pending `gather()` loop, the
  shape the chapter argues against ("A single `gather(*self.tasks)`
  would not do"), plus hand-written field-assigning `__init__`s.
  Marker output is unchanged. `layout_with_a_moat` renamed
  `two_rooms` (it holds two rooms and no moat), and a short paragraph
  notes what the trim removed (numbers, logging, file loader).
- Solutions exercise 3 rewritten to do what the exercise asks: the
  rats program with `claim()` as an `async def` (sleep in the gap),
  the `Recorder` protocol declaring it `async`, `await` inside
  `Rat.run()`'s comprehension, an awaited `explore()`, and the
  requested count of `True` returns against `len(visited)`: 25 vs 24
  on the chapter's own test maze, deterministic across runs. The old
  solution was a standalone two-coroutine demo (`StubMaze`,
  `BrokenBlackboard`, one `gather()` of two claims) that skipped
  every propagation step the exercise names and contained no rats.
  The closing no-lock prose is kept, tightened ("precisely because"
  dropped; "A coroutine only ever yields control at an `await`" is
  now "A coroutine yields control only at an `await`").
- Ran `make reflow` on the chapter (2 paragraphs).

## Considered and declined

- `Room`, `Doors`, and `Robot` keep their hand-written `__init__`s.
  The `Item` hierarchy is behavior-first (a `ClassVar` symbol and
  `interact()` overrides), `Room`'s custom `__repr__` would fight a
  generated one, and `Doors` holds one dict. Dataclassing any of them
  buys nothing a reader would notice.
- The blackboard intro's "so the design needs no lock" states the
  conclusion three listings before `claim()` shows the mechanism.
  Kept: it is a preview the `claim()` paragraph then earns, with the
  race chapter linked at that point.
- Exercise 5's "need not use the teleports" is accurate as written:
  the solution's BFS may traverse them, and the sentence's job is to
  justify asserting only the endpoint.
- The "Rats & Mazes" heading's ampersand produces an awkward
  auto-slug, but nothing links to that anchor; left alone.
- `Blackboard.render()`'s third branch (a space for an unvisited open
  cell) can produce no output for `amaze.txt`, where all 139 open
  cells are reachable. Not flagged in prose: exercise 2 is where
  unreachable cells appear, and the branch earns its place there.
- "adapted from my *Atomic Kotlin* book" was not independently
  verified (no copy at hand); left to the author's memory.
