> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 38_Patterns--Simulation, third review (2026-10-13)

This run follows `~38_Patterns--Simulation.r2.md` (2026-09-29) and the
sweeps since (listing-design proposals, the outside reviews, the commerce,
R29, and claim sweeps), and it reads the Solutions file as closely as the chapter.
It has no live blocks.
`tip verify-ch CH=38 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after,
on `uv run python` 3.15.0 and `ty` 0.0.86.
I reran by hand what the prose counts or asserts:
the robot's route crosses teleport `a` at `(11, 5)` and then `b` at `(3, 21)`,
the maze holds 299 rooms with no wall and 16 pieces of food,
the exercise 3 collision lands on `(5, 5)` with both rats dead-ending there,
agitation falls from 0.073 at step 100 to 8.9e-7 at step 20,000 (about five orders of magnitude),
and the exercise 8 marker printed the same three rows on three runs
(the two-decimal form the `CLAUDE.md` trap entry settled; no simulation marker moved).
Chapter 27's Builder section still names `GameBuilder`,
and its exercise 9 is the `__subclasses__()` recursion this chapter cites.

## Applied directly

Chapter:

- Rats & Mazes, the blackboard paragraph: the list of the blackboard's jobs left out the log, which `log()` and `messages` hold. Added "collects the rats' log messages".
- Contention on a Loop: "A maze with a loop closes a second path between two cells" is now "holds two paths between some pairs of cells", which says what a loop gives the rats.
- Rooms, Robots, and the Item Factory: the three-item list of what `interact()` returns gained its "and".
- The `__subclasses__()` paragraph: "The same chapter's [Simple *Factory Method*]" read as this chapter, since the Factory link sat in the previous paragraph. The link text is now "[Factory]", the form the Builder sentence uses, and "that chapter's exercise 9" now has its antecedent in the same sentence.
- The `EDGE` paragraph: "It takes `enter()` like any other room" now names the caller, "`Robot.move()` calls its `enter()` as it does any other room's".
- "The `Coord` here counts `(row, col)`" is "is `(row, col)`".
- The Model: "`amplitude()` is the standing-wave field" ignored the `abs()`, which makes the function a strength and never negative. It now "returns how strongly a square plate ringing in mode `(m, n)` vibrates at the point `(x, y)`", matching `agitation()`'s "mean vibration strength", and "The field is zero along curves" became "The vibration is zero".

Solutions:

- `robot_world.py` and its introducing paragraph sat inside exercise 3's folded Solution step, so a reader opening exercise 4 or 5 never saw the module both import, and exercise 3's shape step showed a `robot_world.py` skeleton unrelated to its exercise. Both now sit in their own unnumbered section, "## 4 and 5: the robot world", the form "## 6, 7, and 8: the Chladni plate" already uses. `tip steps` dropped the stale shape block, and exercise 4's "folded into `robot_world.py` above" still points the right way.
- Exercise 1: the fake "touches no `asyncio.create_task()`", but the chapter's `spawn()` calls `self.group.create_task()`. Now "a `TaskGroup`".
- Exercise 2: "unreachable when no path of open cells connects it to the entry, not when a wall surrounds it" set up a false contrast, since a walled-in cell is unreachable. It now says walls on four sides are the smallest case, and that the right room's cells have open neighbors and are cut off by the wall between the rooms.
- Exercise 3: "drags three more edits with it" is "forces three more edits".
- Exercise 4: "the topology changes underneath the hard-coded route" is the literal event: the route `"ee"` sends the robot through a teleporter where the coin should be.
- Exercise 5: "the room the robot just arrived at" stranded its preposition; now "the room where the robot arrived". The greedy-tour example's "and out past it again" left the reader to work out the waste; it now says the robot walks the stretch between the start and the single piece three times.
- Exercise 6: agitation reads `0.000` "from the start", not "from the first step", since it is zero before any step runs.

## Considered and declined

- The closing "one limit" paragraph ends with the exercise 7 pointer. It reads as a second concept, but "tell the physics from the rule that models it" ties it to the limit (the freezing belongs to the rule), so it stays.
- `itertools.cycle()` "constructs an infinite iterator from any nonempty finite iterable" is narrower than the function's contract (it accepts any iterable), but it describes the case where cycling means something, and the listing's two calls fit it.
- Exercise 8's "more steps than anyone wants to watch" keeps its "wants", since the subject is a person.
- The earlier reviews' declined items stand: the hand-written `__init__()` in `CountingBlackboard` and `RecordingBlackboard`, the trimmed `Rat` copies, the third-`$` case in Solutions 4, `string_maze`'s name, Solutions 2's count-and-extremes print, the `Empty` override, and the item comments in `items.py`.

## For the session

- `tip prose CH=38` reports one stale entry in the internal-names baseline, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`. It belongs to chapter 15, not this chapter, and is probably another agent's change in this sweep.
