> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 38_Patterns--Simulation

Reviewed after the six prose passes (elements-of-style, literal, positive,
straighten, cohesion, antecedents), each committed separately on
`claude/prep-38`. No `~` file existed for this chapter; `deep_review_db.md`
was read and its standing exemptions honored (the hand-written `__init__`
stand-ins in this chapter among them). The prose pass ran without the
global `~/.claude/CLAUDE.md` watch list, which is not available in a cloud
session; it used this skill's rules, `banned_phrases.py`, and the repo's
`CLAUDE.md` instead.

Every listing ran here and matched its `#:` markers. The robot's teleport
order (`a`, then `b`) was traced by replaying the solved route, and the
plate's peak amplitude (2.0) was measured to check the Solutions' kick
arithmetic.

## Applied directly

- Testing Full Coverage: the section opened "Because claiming is atomic,
  the rats always cover every cell reachable from the entry." Coverage does
  not depend on atomicity, and exercise 3 and its solution say so
  (`test_rats_and_mazes.py` passes on the broken `claim()`, since `visited`
  is a set). Rewritten: coverage follows from every claimed cell getting a
  rat that tests its four neighbors; atomicity adds one rat per cell, which
  only exercise 3's count can see.
- Order from Noise, first paragraph: the same error in the recap ("The rats
  cover every reachable cell because `claim()` is atomic") now reads "cover
  every reachable cell, one rat per cell, because `claim()` is atomic".
- Rats & Mazes: "Blackboard is a classic coordination pattern" now
  italicizes *Blackboard*, as chapter 39's catalog row does.
- Rats & Mazes: "spawns a new rat at each of the others, then yields" read
  as if a rat yields only after spawning; `run()` yields after every move.
  Split: "After every move it yields so its siblings can run."
- End of Running the Maze: "two rats call `claim()` on one unclaimed cell"
  was wrong about the ring run, where the second call finds the cell
  already claimed. Now "two rats try to claim the same new cell".
- Opening: "The chapter works the first example, the pack of rats, from end
  to end" singled out the rats although all three examples run from model
  to test to view. Now "The first example, the pack of rats, puts asyncio
  tasks ... together in one small program."
- Solutions 8: "a half-unit displacement" and "about a twentieth of the
  plate at full amplitude" ignored that `amplitude()` peaks at 2 (the same
  answer's "at most one percent" for `kick=0.005` already counted it). Now
  "up to half the plate, and the full width where the amplitude peaks" and
  "at most a tenth of the plate where the amplitude peaks".
- Solutions 4: "where a coin was meant to be" (the file's one Vale warning)
  now says the two `$` cells become a teleport pair and the robot walks
  into a teleporter where the maze should hold a coin.
- `tools/data/exercise_refs_baseline.txt`: accepted the new "exercise 3"
  reference in Testing Full Coverage and the reworded one in the `claim()`
  paragraph, both checked against "Breaking `claim()`'s atomicity".

Pass-review reverts, for the record: "ringing one wall block" went back to
"around", "You need not touch" back to "You shouldn't need to touch" (later
rewritten by the positive pass), "The other rat, not the rat itself,
claimed each rejected cell" back to "Each rat loses a cell to the other,
not to itself", and a straighten split that stated the `StrEnum` fact twice
was merged.

## Should `Blackboard` join the pattern-name gate?

Chapter 39's catalog lists `[*Blackboard*](38_Patterns--Simulation.md)` as
a pattern, and this review italicized the one place chapter 38 names it
as a pattern. `tools/data/pattern_names.txt` does not list it, so
`make pattern-names` will not catch a plain "Blackboard" written later.
Adding it would gate the name; the lowercase "blackboard" (the object the
rats share) and the `Blackboard` class in code spans stay ordinary, the
same split State and Command already live with. I would add it, but the
gate list is a book-wide file, so I left it for you.

[] Reject

## Considered and declined

- `CountingBlackboard` and `RecordingBlackboard` write an `__init__` that
  calls `super().__init__(maze)` and adds one field, where a dataclass
  subclass with `field(init=False, default=0)` would do. The plain
  subclass keeps each listing's one new thing the overridden `claim()`,
  in line with the recorded exemption for this chapter's stand-ins.
- Solutions 1 and 2 copy the chapter's `Rat` with a different comment on
  `await asyncio.sleep(0)`. Harmless, and the copies are trimmed on
  purpose.
- Solutions 4 could add that a third `$` under `Coin(Food)` stops the
  build at stage 3's `assert`. The answer's two-coin maze is what it
  describes, so it stays as is.
