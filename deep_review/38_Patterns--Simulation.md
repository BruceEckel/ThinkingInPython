> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 38_Patterns--Simulation, second review (2026-09-29)

This run follows the completed review of 2026-09-25 (`~38_Patterns--Simulation.md`) and the six commits made since.
Nothing here needs your decision, so the file has no live blocks.
The commits since the first review left no damage: the log paragraph moved below its listing intact,
and the `ClassVar` restatement reached every `symbol` in both files.
What this run found was in the chapter before either review.

I checked each claim by running it: the full eighteen-message rat log,
an edge count of `amaze.txt` (139 cells, 138 edges, so a tree),
a `Blackboard` read before `explore()`, the solver with teleports blocked,
a grandchild of `Food` through `item_factory()`, agitation out to 20,000 steps,
and the plate rendered at `kick=0.5` under four seeds.
The stepping logic of `maze_view.py` ran against a mocked `tkinter` (199 frames, robot finished).
Both external links resolve.
`tip verify-ch CH=38` passes 24 of 24.

## Applied directly

Chapter, corrections:

- Running the Maze, the log paragraph: "Rat 1 spawns rat 2 and then dead-ends before rat 2 does" was offered as evidence that numbers follow spawn order "rather than completion order", but rats 1 and 2 finish in number order, so the example showed no difference. The full log has one: the rats dead-end in the order 1, 2, 3, 5, 6, 9, 8, 7, 4. The paragraph now cites rat 4, which starts in the sixth message (visible in the listing) and dead-ends last.
- Rats & Mazes, the maze definition: "it reports whether each neighboring cell is a wall or an opening" described work the rat does. `is_open()` answers for the one coordinate it receives, and `Rat.run()` computes the neighbors. Now "whether that cell".
- The Rat and the Blackboard, the `group` paragraph: "declares `Robot.room` the same way" was wrong about the mechanism, since `group` is a dataclass field with `init=False` and `room` is a bare annotation. The paragraph now says what the two share (no attribute until something assigns it, an `AttributeError` before then, no `None` in the type) and names the bare annotation as the robot's form.
- Rooms, Robots, and the Item Factory: "the loop falls through to its last line" named the loop's last line; the `Teleport` comes from the function's last line, after the loop. Reworded.
- Choosing the Path: "as the test does with `game.run("e")`" pointed at a listing the reader has not seen. Now "as `test_robot.py` does in the next section".
- Testing the Walk: the lead-in credited `show_maze()` for both tests, and only the second calls it. It now says what each test does. The imperative list ("Build the maze, search it...") became a description of the first test.
- What the Numbers Show: "until a random step crosses a quiet line" is not what stops a grain; a step that crosses a line ends on the far side. The step size depends on where the grain is, so it now reads "lands near a quiet line".
- Exercise 3: making `claim()` an `async def` does not force "the same change" on the comprehension and `explore()`; they gain an `await`. Now "matching changes".
- Running the Maze: the loader skips empty lines, not blank ones (`if line` keeps a line of spaces, which is a row of open cells).

Chapter, teaching:

- "Perfect maze" appeared twice (Contention on a Loop, exercise 3) and was never defined. The sentence that stated the property without the name now introduces the term.
- Choosing the Path: added the cost of `landing()`. The chapter's claim is that polymorphism removes the type switch, and `landing()` is a type switch over the same rules. The new sentences say why the search cannot call `interact()` (it acts: `Food` replaces itself, `EndGame` sets `finished`) and what the copy costs (a new blocking or moving item needs a branch in `landing()` too).
- The `TYPE_CHECKING` paragraph now says why an annotation is never a runtime lookup (Python evaluates it only when something reads it), and contrasts the rats, which avoid the same cycle with the `Recorder` `Protocol` and no import. The two techniques sat in one chapter with no sentence connecting them.
- `TaskGroup` had no link to where the book teaches it. Added the link to chapter 19's "Structured Concurrency with `TaskGroup`".
- Watching the Pack: "Concurrency here" followed the view's listing, where "here" reads as the view. Now "In the rats model". In the same paragraph "a single-threaded worklist" contrasted with a design that is also single-threaded (now "synchronous"), and "What it adds is the event loop" read as a second benefit (now "The cost is").

Chapter, listings:

- `maze_view.py`: `queue = list("".join(moves.split()))` with `queue.pop(0)` became `route = iter(moves)` with `next(route, None)`, the form `rats_view.py` uses. `solve()` returns no whitespace, so the `split()` did nothing, and `pop(0)` on a list is the cost chapter 3 measures.
- `ring_contention.py`: `RING` is now `RING: Final[str]`, as `LAYOUT` is in the test beside it.
- `items.py` (and the Solutions copy): the comment on `Teleport.symbol` said "Set per target letter", and nothing sets it. `__str__()` returns `target`. Now "Shown as its target letter".

Chapter, style:

- Dunder methods and functions named in prose take parentheses, as in chapter 12: `__init__()`, `__post_init__()`, `__eq__()`, `isinstance()`, `gather()`, `run()`.
- "hold nothing but a position" and "store nothing but their own" are "only"; "inherit from `Item` itself" is "inherit directly from `Item`"; "The curves themselves" lost the reflexive; "a plain stack" lost "plain".
- "define the subclass with its symbol, and the factory finds it" (imperative plus consequence) is now "once you define the subclass with its symbol, the factory finds it".
- "splitting them into labeled passes keeps each stage separate" said one thing twice. Now "each runs as its own labeled pass".
- "serve the type checker as much as safety" now says what the asserts do for each.
- "asyncio tasks" in the opening takes code font like every other mention.

Solutions:

- Exercise 1 asks you to assert what the rat kept and spawned, and the solution printed instead. It is now a test, `test_ch38_fake_blackboard.py`, which also asserts the two log messages. The prose gained the step that makes the rat stop (the script runs out, so `claim()` answers `False`). `SolutionsCode/.../exercise_1.py` is removed and the test file added.
- Exercise 8, `kick=0.5`: "Grains accumulate in whichever quiet regions they land in first, mostly the corners" and "three blobs" did not match the run. Under seeds 1, 2, 3, and 42 all but zero to two of the 2000 grains end in two corners, `(0, 0)` and `(1, 1)`, about half in each. The paragraph now says so and gives the reason: the field is zero and flat there (near `(0, 0)` it grows as `x² - y²`), so it is weak over a patch, not a strip. "Three blobs" is "two blobs". The paragraph also held one unwrapped 140-character line.
- Exercise 5: "A single search at the start plans a route to a piece of food and then eats, on the way, some of the food it is going to visit later" describes something breadth-first search cannot do, since the path to the nearest food passes no other food. Replaced with the reason that holds: a path planned from the entry is no use from another room. "A few hundred rooms" is now the count, 299.
- Exercise 5: "which is all breadth-first search promises" is "guarantees"; "the maze punishes that" is "makes that costly".
- Exercise 4: "the reason is the search order rather than the inheritance" blamed the order, and the cause is which classes `__subclasses__()` lists. Reworded. Two "at all" cut.
- Exercises 6 and 8: dropped "exactly where" and "simply". The "exactly `0.0`" in exercise 6 stays, since it is a float-equality claim.

## Considered and declined

- `string_maze` is a module constant in lowercase without `Final`. Renaming it reaches four chapter listings and the Solutions copy, the name comes from the *Atomic Kotlin* original, and Solutions 2 has a lowercase `two_rooms: Final[str]`, so the book has no single form to conform to.
- The closing reflections of the rats and robot sections ("In the rats model, concurrency organizes the code...", "Three ideas from earlier chapters...") sit under the "Watching..." headings, after the view listings. A heading of their own would make three more headings for six sentences. The pointer fix above handles the one place the placement misled.
- The chapter's `Empty` overrides `interact()` with the body `Item` already supplies, and the Solutions copy omits the override. The chapter's form keeps "each type of occupant defines its own" true of the listing, and the Solutions copy is trimmed like the others.
- "So every `claim()` the run above rejects on an open cell is a rat testing a cell already claimed" is close to a tautology before its colon. The list after the colon carries the point, and a rewrite would replace a literal sentence with a figure ("looking back").
- Solutions 2 prints a count and the two extremes of the unreached set where the exercise says to print the cells. Nine coordinates do not fit a 60-column marker, and the prose names the room.
- Item comments in `items.py` ("Eaten", "Cannot pass: stay put") explain what prose could. They are short, the first review left them, and each sits on the line that makes the rule.
- The previous review's declined items stand: the hand-written `__init__()` in `CountingBlackboard` and `RecordingBlackboard`, the trimmed `Rat` copies, and the third-`$` case in Solutions 4.
