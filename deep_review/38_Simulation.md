[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

**`blackboard.py`, `explore()`: the `while`/`gather()` loop contradicts the book's own
guideline, and `TaskGroup` produces byte-identical output.**

```python
async def explore(self) -> None:
    start = self.maze.entry()
    self.claim(*start)
    self.spawn(*start)
    # Wait for every rat, including ones spawned while we wait
    while pending := [t for t in self.tasks if not t.done()]:
        await asyncio.gather(*pending)
```

Three things collide here.
`thinking-in-python-skill.md` says
"For concurrent awaits, prefer `asyncio.TaskGroup` (3.11+) over `asyncio.gather()`."
Chapter 19's Guidelines say the same thing at more length, and 19 is the chapter this
one links to in its first paragraph.
And the loop's mechanism is never explained:
the prose says only "then awaits every task, including the ones spawned along the way,"
which restates the comment.
A reader who just finished 19 will write `await asyncio.gather(*self.tasks)`,
get a program that returns before the maze is mapped, and have nothing in the chapter
to tell them why.

Two ways out. I recommend the first.

**Option A (recommended): use a `TaskGroup`.**
Verified on the pinned build: `ty`, `ruff`, `pytest` and the demo all pass,
and `rats_and_mazes.py`'s output is byte-for-byte identical to the current listing
(same map, same `9 rats mapped 139 cells`), so no `#:` marker changes.

```python
class Blackboard:
    group: asyncio.TaskGroup

    def __init__(self, maze: Maze) -> None:
        ...

    def spawn(self, x: int, y: int) -> None:
        rat = Rat(self, x, y)
        self.tasks.append(self.group.create_task(rat.run()))

    async def explore(self) -> None:
        start = self.maze.entry()
        self.claim(*start)
        async with asyncio.TaskGroup() as group:
            self.group = group
            self.spawn(*start)
```

with prose along the lines of:

> A `TaskGroup` does not close until every task inside it has finished,
> including tasks created after the block was entered,
> which is exactly the shape this problem has: each rat can create more rats.
> A single `asyncio.gather(*self.tasks)` would not work,
> because `gather()` fixes its argument list at the moment it is called.

The cost is the `group` attribute, which is only valid while `explore()` is running,
and it is the same kind of declaration-without-assignment the chapter already teaches
for `Robot.room` in the next section, so it can lean on that.

**Option B: keep the loop and explain it.**
Add two sentences saying that `gather()` fixes its argument list when called,
that the loop therefore re-collects unfinished tasks after each `gather()` returns
and stops when a pass finds none,
and that `TaskGroup` would absorb the new tasks by itself but would put a live group
object on the blackboard.
This keeps the listing but leaves the book recommending one thing in 19 and doing
another in 38.

[] Reject

---

**Exercise 3 cannot be done as written, and doing it literally leaves a green test.**

> 3.  Break the atomicity of `claim()`.
>     Insert an `await asyncio.sleep(0)` between the membership test and
>     `self.visited.add(...)`,
>     then run `test_rats_and_mazes.py` several times.

Three problems, all verified on the pinned build.

`claim()` is a plain `def`, so no `await` can go inside it.
Following the instruction means making `claim()` an `async def`,
which also means changing the `Recorder` protocol,
`Rat.run()`'s comprehension (`if await self.blackboard.claim(*pos)`),
`explore()`'s own call, and `RecordingBlackboard.claim()`.
The exercise mentions none of that, and it is most of the work.

"Run it several times" implies flakiness that cannot happen.
`asyncio` schedules deterministically, so every run of the broken version is identical.

Worst: with the change made exactly as described, `test_rats_and_mazes.py` passes,
three runs out of three.
It asserts `blackboard.visited == flood(maze, maze.entry())`,
and double-claiming a cell does not change the *set* of visited cells.
I instrumented it: on the test's `LAYOUT` maze the broken `claim()` returns `True`
25 times for 24 distinct cells, so the collision is real and completely invisible to
the assertion.
On `amaze.txt` there is no collision at all (139 successes, 139 cells),
so the full demo's output does not change either.
A reader who follows the exercise sees a passing test and concludes atomicity does
not matter.

Proposed replacement:

> 3.  Break the atomicity of `claim()`.
>     Make `claim()` an `async def`, which pulls the `Recorder` protocol,
>     `Rat.run()`'s comprehension and `explore()` along with it,
>     and put `await asyncio.sleep(0)` between the membership test and
>     `self.visited.add(...)`.
>     Then count how many calls return `True` and compare that count with
>     `len(blackboard.visited)`.
>     `test_rats_and_mazes.py` still passes, because `visited` is a set:
>     the guarantee that broke is "one rat per cell", not "every cell is reached".
>     What does the extra success cost the rats,
>     and why does the original `claim()`, with no `await` inside it, need no lock?

`Solutions/38_Simulation.md` exercise 3 already answers the rewritten version better
than the current one, since it demonstrates a standalone `BrokenBlackboard` rather
than running the chapter's test. See the cross-chapter block below for the one
sentence in it that needs correcting.

[] Reject

---

**Chapter intro (lines 1-8): the chapter's real claim arrives on the last page.**

The opening defines a simulation and then describes only the first example:

> A simulation models a set of objects that act on their own and interact through shared state.
> The first example, a pack of rats mapping a maze, is worked from end to end.

The reader has no idea a robot or a plate of sand is coming,
and no idea why three examples rather than one.
The argument that actually organizes the chapter is stated at line 1125,
after the last listing:

> The three simulations form a progression.
> The rats cooperate through a blackboard.
> The robot follows a script.
> The grains know nothing.
> The less the agents understand, the more the run can tell you.

That is the chapter's claim, and it is the most convincing thing in it.
Held to the end it does no work,
because a reader who does not know the progression exists reads three unrelated programs.

Proposed change: add two or three sentences to the intro that name the three examples and the arc,
without spoiling the Chladni result.
Something like:

> Three simulations follow, each giving its agents less to work with than the last.
> A pack of rats coordinates through a shared blackboard,
> a single robot walks a maze where each object it meets decides what happens,
> and a plate of vibrating sand runs on grains that know nothing at all.
> The first two confirm a design you can predict from the code.
> The third does not, which is simulation's other purpose.

Cost of the change: none structurally.
It does duplicate the "confirm versus discover" beat that currently opens
"Order from Noise" (lines 861-868),
so that paragraph would want a light trim to avoid saying it twice.
Reported rather than applied because it changes the chapter's pacing.

[] Reject

---

**"Other Maze Resources" (line 1134 in the edited file) buries the chapter's payoff.**

The chapter's closing insight is the last paragraph of `### Watching It Happen`:

> This is *emergence*: global order arising from local rules that never mention it. ...
> When behavior emerges, reading the code is not enough. Run it.

Two sentences later the reader is instead reading

> A discussion of [algorithms to create mazes](...).
> A discussion of algorithms for collision detection and [steering behavior ...](...).

Two sentence fragments about mazes, arriving after the chapter has moved on from
mazes entirely, standing between the chapter's conclusion and the exercises.
Every neighbouring pattern chapter ends on a named closing section
(25 now, 26 "One Surrogate, Two Intents", 27 "Which Factory Should You Use?",
30 "What Stayed Constant"), and this one ends on a link dump.

Proposed change, two parts:

1.  Move "Other Maze Resources" up to the end of "A Robot in a Maze",
    where mazes are still the subject, or fold its two links into that section's
    last paragraph.
2.  Promote the closing paragraph (from "The chapter began by defining a simulation")
    out of `### Watching It Happen` into its own `##` section, so it reads as the
    chapter's conclusion rather than as commentary on the tkinter view.
    A title such as `## The Less the Agents Know` earns its place by naming the
    progression rather than restating "Simulation".

Cost: one new `##` anchor, unreferenced from anywhere.
The `### Watching It Happen` text above the moved paragraph still stands on its own,
since it ends at "It belongs to the field on which they sit."

While you are in there: the second resource link is `http://`, not `https://`,
and its text promises "collision detection" that the linked page (Craig Reynolds on
steering behaviors) does not really cover.

[] Reject

---

**"Rats & Mazes" is the only `##` section with no subsections.**

"A Robot in a Maze" has three `###` headings and "Order from Noise" has four.
"Rats & Mazes" runs about 380 lines flat, covering the rat, the maze,
the blackboard, the data file, the demo, the test, and the GUI view.
A reader scanning the chapter's table of contents sees one opaque block
followed by two well-signposted ones.

Proposed change: three `###` headings inside it, mirroring the other two sections:
`### The Rat and the Blackboard` before `rat.py`,
`### Testing Full Coverage` before `test_rats_and_mazes.py`,
and `### Watching the Pack` before `rats_view.py`.
Cost: three new anchors, none of them referenced from anywhere
(I checked; only `#a-robot-in-a-maze` is linked from outside, by 08, 09 and 27).
Reported rather than applied because adding headings changes the chapter's pacing.

[] Reject

---

**`### Rooms, Robots, and the Item Factory` sits after the commentary it names.**

The heading falls between the `items.py` listing and the prose that explains
`items.py`.
Everything from "`world.py` imports `Item`, `Robot`, and `Urge`" through
"using the class hierarchy as the registry" discusses the *previous* listing:
`TYPE_CHECKING`, `Robot`'s two attributes, `item_factory()`.
Only at "A `Room` holds one item" does the section's own subject start.
So a reader who uses headings to navigate finds the `items.py` explanation filed
under a heading for `world.py`.

Proposed change: move the `### Rooms, Robots, and the Item Factory` heading up,
to just above the `items.py` listing.
The title then covers both listings honestly, since `Robot` and `item_factory()`
live in `items.py` and `Room` in `world.py`,
and the `## A Robot in a Maze` prose above it becomes the section's introduction,
the same shape "Order from Noise" already uses before `### The Model`.
Cost: nothing links to `#rooms-robots-and-the-item-factory` (checked),
and the anchor does not change since the title does not change.

Alternative if you prefer smaller sections: leave the heading where it is and
rename it `### Rooms and Doors`, moving the `items.py` commentary above it.
That changes the anchor, which nothing references.

[] Reject

---

**`rat.py`: the `Recorder` protocol is named for its least important method.**

`Recorder` declares `claim()`, `spawn()`, `log()` and `next_number()`.
Only `log()` records anything;
`claim()` is the atomic test-and-set the chapter calls "the heart of the program".
The prose one line above the listing describes the protocol correctly and never uses
the name: "an object that can claim a cell, spawn a rat, record a message, and hand
out a number."

Proposed change: rename it to something naming the role, `Coordinator` or `Board`.
Cost: three occurrences in `rat.py` (the class, the annotation on `Rat.blackboard`,
the `Protocol` import stays), one in the exercise-1 wording,
and `Solutions/38_Simulation.md` exercise 1, which names `Recorder` in its fake.
Low value on its own; worth doing only if you are already touching `rat.py`.

[] Reject

---

**`rats_and_mazes.py`: `blackboard.messages` is collected and never read,
and printing it is the chapter's cheapest teaching win.**

`Rat.__post_init__()` logs a start line, `Rat.run()` logs a dead-end line,
`Blackboard.log()` appends both to `self.messages`,
`Recorder` declares `log()` so exercise 1's fake must implement it,
and nothing anywhere prints a single message.
It is dead state in the chapter's central program.

It is also the mechanism the demo never shows.
The current output is one finished map and one summary line,
from which a reader cannot narrate how rats spawn, interleave and die.
The log can:

```python
for message in blackboard.messages[:8]:
    print(message)
#: Rat 1 starts at (1, 1).
#: Rat 2 starts at (6, 3).
#: Rat 1 dead-ends at (7, 5).
#: Rat 3 starts at (6, 1).
#: Rat 2 dead-ends at (3, 3).
#: Rat 4 starts at (18, 1).
#: Rat 3 dead-ends at (15, 1).
#: Rat 5 starts at (12, 13).
```

Those eight lines say more about cooperative tasks than the map does:
rat 1 spawns rat 2 and then dies before rat 2 does,
numbers are handed out in spawn order rather than completion order,
and the whole run is 18 messages for 9 rats.
Verified deterministic: three consecutive runs on the pinned build produce the
identical eight lines, and `len(blackboard.messages)` is 18 every time.

Proposed change: print the first eight messages before the map,
with a sentence saying the log is a trace of the run and that the rest of the chapter
never needs it.
Reported rather than applied because it adds output and `#:` markers to an existing
listing, and because you may prefer `blackboard.messages[:8]` versus all 18.

[] Reject

---

**`game.py` is a library and a demo in one file, which the house style forbids
and the chapter's other two examples already avoid.**

`thinking-in-python-skill.md`:
"Importable modules carry no top-level demo.
If a module is both a library and a demonstration, split it:
a demo-free library module plus a separate runnable file that imports it and holds
the demo."
`game.py` defines `GameBuilder`, `string_maze` and `solution`,
then at module level builds the game, prints the maze, runs the solution and prints
again.
`test_robot.py` imports from it and `maze_view.py` imports from it,
so both trigger the whole demo on import;
running `maze_view.py` prints two full mazes to the console before the window opens.

The chapter already does the right thing twice.
`chladni.py` is a demo-free library and `chladni_demo.py` holds the demo.
`blackboard.py` is a demo-free library and `rats_and_mazes.py` holds the demo.
`robot_explorer` is the one that does not, with no prose acknowledging it.

Proposed change: split `game.py` into

- `robot_explorer/game.py`: the header comment, the imports, `class GameBuilder`,
  `string_maze` and `solution`, stopping at the end of `solution`.
- `robot_explorer/robot_demo.py`: a new listing holding exactly the code and `#:`
  markers that currently follow `solution`, prefaced by
  `from game import GameBuilder, solution, string_maze`.

`test_robot.py` and `maze_view.py` need no change,
since they already import only names that stay in `game.py`.
The prose "Running it prints the maze before and after the walk" moves to sit under
the new listing.
`Examples/38_Simulation/robot_explorer/robot_demo.py` appears on the next `make sync`.
Reported rather than applied because it places a new listing.

[] Reject

---

**`blackboard.py`: `Blackboard.__init__()` only assigns parameters and defaults,
so the house rule makes it a `@dataclass`.**

`thinking-in-python-skill.md`:
"A class whose `__init__()` only assigns parameters or defaults to fields is a
`@dataclass` ... Write the manual form only when the code is teaching it ...
and then say why in an adjacent comment or prose."
`Blackboard.__init__()` assigns one parameter and four defaults and nothing else,
and no prose explains the deviation.
The contrast is loud inside the chapter itself,
because `Rat` twenty lines earlier *is* a dataclass and is used to teach
`field(init=False)` and `__post_init__`.

The dataclass form:

```python
@dataclass
class Blackboard:
    maze: Maze
    visited: set[Coord] = field(default_factory=set)
    tasks: list[asyncio.Task[None]] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)
    _numbers: Iterator[int] = field(
        init=False, default_factory=lambda: itertools.count(1))
```

`RecordingBlackboard` in `rats_view.py` still works unchanged,
since the generated `__init__` still takes `maze` alone.

Recommendation: I am not certain this is an improvement.
`field(init=False, default_factory=lambda: itertools.count(1))` is harder to read
than `self._numbers = itertools.count(1)`,
and this listing is the one the reader studies hardest.
Either [[convert it]], or add one clause of prose saying why the manual form stays
(for example, that the four collections are internal bookkeeping rather than
constructor parameters, so putting them in the signature would misdescribe them).
The one thing not to leave is silence, since the book's own style rule is being broken
in a flagship listing.

The same rule catches two smaller classes in `world.py`,
`Doors` (one default, no parameters) and `Room` (one parameter plus
`self.doors = Doors()`).
`Room` has a real reason, a hand-written `__repr__` that prints the occupant rather
than the field list, and `Doors` has none.
Both are minor next to `Blackboard`.

[] Reject

---

**Exercise 5's hint under-describes the search.**

> Write a function that takes a `GameBuilder` and searches the rooms for a path from
> the robot's room to the `EndGame` room,
> the way `flood()` searches maze cells in `test_rats_and_mazes.py`.

`flood()` tests `maze.is_open(x, y)`.
The room graph has no equivalent: passability is a property of the *occupant*,
so the search has to refuse rooms whose occupant is a `Wall` or an `Edge`,
and it has to turn a room-to-room path back into `n`/`s`/`e`/`w` characters, which
means tracking which `Urge` produced each step.
Neither is hard, but neither is implied by "the way `flood()` does".

Also worth telling the reader: I verified the `!` room is reachable from the robot's
start through ordinary doors alone,
so a plain breadth-first search finds a path and the exercise is answerable,
but that path will be shorter than the chapter's hard-coded `solution` and will not
pass through the teleports.
A reader who expects to reproduce `solution` will think they have failed.
Suggest adding one sentence: "Your path will be shorter than the hard-coded
`solution` and need not use the teleports; assert only that the robot finishes."

[] Reject

---

**Exercise 4 should say "direct subclass of `Item`".**

> Define a `Coin` subclass with the symbol `$` whose `interact()` removes itself the
> way `Food` does

"the way `Food` does" invites `class Coin(Food)`, which is the natural design.
`Item.__subclasses__()` returns only direct subclasses, so `item_factory("$")` then
falls through and returns `Teleport("$")`, silently.
That also leaves an odd number of teleport rooms, so Stage 3's `zip(pairs, pairs)`
drops one and its `target_room` is never set, and the failure finally surfaces as an
`AttributeError` far from its cause.
Verified: with `class Coin(Food)` defined,
`Item.__subclasses__()` is `['Robot', 'Wall', 'Food', 'Teleport', 'Empty', 'Edge',
'EndGame']` and `type(item_factory("$")).__name__` is `Teleport`.

The chapter now warns about this in prose (applied in this pass),
but the exercise should be unambiguous too:
change "Define a `Coin` subclass" to "Define a `Coin` subclass of `Item`",
and consider adding "What happens if you derive it from `Food` instead?" as the
follow-up question, since the answer is the point.

[] Reject

---

## Cross-chapter

**`Solutions/38_Simulation.md`, exercise 3: one claim in the explanation is false.**

The solution says the broken `claim()`

> can leave some other reachable cell unclaimed entirely,
> since one of the two rats that collided on `(2, 2)` would otherwise
> have gone on to claim a different cell instead.

It cannot.
Every cell a rat claims is either kept by the claimer or handed to a rat spawned on
it, so no claimed cell goes unexplored, and no open neighbour of an explored cell
goes unclaimed.
Two rats colliding on one cell both proceed from that cell; they duplicate work, they
do not skip anything.
Empirically: the broken version visits all 139 cells of `amaze.txt` and all 24 of the
test's `LAYOUT`, and `test_rats_and_mazes.py` passes every time.

Change I would make: replace that clause with the true consequence,
that two rats now occupy the same cell and repeat each other's work while the
`visited` set stays correct, which is exactly why the chapter's test does not catch
it.
If exercise 3 is rewritten as proposed above, this paragraph should also pick up the
`True`-count-versus-`len(visited)` measurement.
I did not touch `Solutions/`, per the scope rules.

[] Reject

---

**`Chapters/27_Factory.md`, the Builder section (around line 854): `GameBuilder`'s
three stages are described wrongly.**

27 says:

> `GameBuilder` in [Simulation](38_Simulation.md#a-robot-in-a-maze) qualifies.
> It assembles a maze in three stages, creating rooms, connecting doors,
> then placing the robot,
> and each stage relies on what the previous stage established.

The robot is placed in stage 1, inside the same loop that creates the rooms.
Stage 3 pairs the teleports.
Change I would make in `Chapters/27_Factory.md`:
"creating rooms, connecting doors, then pairing the teleports that share a target
letter".
I did not touch chapter 27, per the scope rules.

[] Reject

---

## Manifest: applied to `Chapters/38_Simulation.md` in this pass

*(Not a proposal. This block records what was already changed, so the edits are
findable in the diff. All gates re-run and green: `extract_examples`,
`validate_output` (no marker rewrites), `ruff`, `ty`, `pytest` (5 passed),
`heading_links`, `banned_phrases`.)*

1.  "Rats & Mazes", blackboard paragraph: "The blackboard is a classic coordination
    technique." to "Blackboard is a classic coordination pattern.", so the chapter
    names the pattern that `39_Pattern_Catalog.md` links here for.
2.  "Rats & Mazes", rat paragraph: "When the last rat dies, the maze is fully mapped."
    to "... every cell reachable from the entry has been mapped.", which is what the
    program guarantees and what exercise 2 depends on.
3.  Blackboard paragraph: rewrote the confusing "This is the read-modify-write hazard
    ... avoided by construction" sentence so `claim()` is not the subject of "is the
    hazard", and so the sentence says where the atomicity comes from.
    Also changed "(exercise 3 inserts one and watches the guarantee fail)" to
    "looks at what breaks", since the guarantee that fails is not the one the test
    checks.
4.  Blackboard paragraph: added a sentence naming `itertools.count()` at first use,
    linked to [Iterators](23_Iterators.md#reusable-algorithms).
    It was previously used on line 176 and explained on line 1114.
5.  `amaze.txt` paragraph: "The loader skips blank lines and the path comment" to a
    statement of what the code does, since "the path comment" was undefined jargon
    appearing nowhere else in the book.
6.  `rats_view.py` paragraph: added the model-view split and a named link to
    [Observer](30_Observer.md#a-visual-example-of-observers), with the contrast that
    no model here notifies anybody, so each view drives or replays its model.
7.  "A Robot in a Maze" intro: "No `if` or `elif` on the type of occupant appears
    anywhere" to "... in the movement code", because `GameBuilder` stage 1 has two
    `isinstance` tests 200 lines later.
8.  `game.py` discussion: added a paragraph saying why stage 1's `isinstance` tests
    are not the type switch polymorphism removed.
9.  `item_factory()` paragraph: added the direct-subclasses-only caveat, linked to
    [Simple Factory Method](27_Factory.md#simple-factory-method), and named the
    `class Coin(Food)` failure it causes (exercise 4's likely first attempt).
10. `Room`/`Doors` paragraph: named `EDGE` as a
    [Null Object](20_Rethinking_Objects.md#null-object).
    Chapter 20's Null Object section already cites this maze; the thread had only one
    end.
11. After `world.py`: added a note that its `Coord` is `(row, col)` while the rats
    example's is `(column, row)`, and why.
12. "Building the Maze in Stages": added the reciprocal link to
    [Builder](27_Factory.md#builder), which names `GameBuilder` as a genuine Builder.
13. End of "A Robot in a Maze": "Two patterns from earlier chapters" to "Three ideas",
    with named links for polymorphism, the factory and the Null Object, replacing the
    bare relative phrase.
14. Chladni demo lead-in: "displays the agitation as it happens" to "printing
    agitation at four checkpoints along the way", which is what the listing does.

[] Reject
