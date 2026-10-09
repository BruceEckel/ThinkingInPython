<!-- outside review of Chapters/38_Patterns--Simulation.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `38_Patterns--Simulation.md` chapter:

**1. Section: Rooms, Robots, and the Item Factory (clarification of mechanism)**

* **Target Text:** "`Doors.connect()` links each room to its neighbors on the grid. Teleports add links that cross the grid. Two rooms whose `Teleport` items share a target letter lead to each other."
* **Issue:** Placing "Teleports add links that cross the grid" directly between `Doors.connect()` and the graph diagram implies that `Doors` stores or manages teleport connections. In the code, `Doors` is strictly a 4-neighbor grid mapping; teleport transitions bypass `Doors` entirely and are resolved by `Teleport.interact()` returning `target_room`.
* **Instruction:** Clarify that `Doors` connects only adjacent grid neighbors, whereas teleports cross the grid via `Teleport.interact()` returning `target_room`. For example: "`Doors.connect()` links each room to its adjacent neighbors on the grid. Teleports link across the grid through `Teleport.interact()`, where each occupant returns its paired `target_room` instead of using `Doors`."

**2. Section: The Rat and the Blackboard (unstated mechanism)**

* **Target Text:** "`group` carries `field(init=False)` and no default, so a new blackboard has no `group` attribute until `explore()` assigns one. A `spawn()` before then raises an `AttributeError`. The declaration gives the type checker the attribute's type with no `None` placeholder to check. The robot example later in this chapter declares `Robot.room` for the same reason, with a bare annotation."
* **Issue:** The comparison to `Robot.room` leaves unexplained why `Blackboard` cannot also use a bare annotation `group: asyncio.TaskGroup`. Because `Blackboard` is a `@dataclass`, a bare annotation is captured as a required field in the generated `__init__()`, whereas in an ordinary class like `Robot`, bare annotations remain purely type-level declarations and do not alter instance construction.
* **Instruction:** Add a brief explanation noting that a bare annotation in a `@dataclass` would become a required parameter in `__init__()`, which is why `field(init=False)` is required here. For example: "The robot example later in this chapter declares `Robot.room` for the same reason with a bare annotation; `Blackboard` must use `field(init=False)` because in a `@dataclass`, a bare annotation would become a required parameter in the generated `__init__()`."

**3. Section: Contention on a Loop (precision of explanation)**

* **Target Text:** "Seven of the nine rejections are backtracking. Each rat tests the cell from which it came, once per cell other than the entry, and `len(blackboard.visited) - 1` counts those cells."
* **Issue:** The phrase "once per cell other than the entry" can be misread as meaning the entry cell is never tested during backtracking. In fact, both Rat 1 (from `(1, 2)`) and Rat 2 (from `(2, 1)`) backtrack into the entry cell `(1, 1)`, accounting for two of the seven rejections, while the two terminal cells `(2, 3)` and `(3, 3)` are never backtracked into. The count `len(blackboard.visited) - 1` equals 7 because there are 7 cell transitions/arrivals after the entry across all rats, each prompting one backward check.
* **Instruction:** Clarify that the count corresponds to each rat testing backward from each newly entered cell. For example: "Seven of the nine rejections are backtracking. Across both rats, each step into a new cell prompts a check back toward the cell the rat arrived from, and the 7 non-entry cells in `len(blackboard.visited) - 1` count those moves."

**4. Section: Choosing the Path (missing caveat in search abstraction)**

* **Target Text:** "A new kind of item that blocks the robot or moves it needs a branch in `landing()` as well as its own `interact()`."
* **Issue:** The prose states that only an item that "blocks the robot or moves it" requires modifying `landing()`. However, `landing()` also dereferences teleports directly (`return beyond.occupant.target_room`), meaning any item that transports the robot to another room without occupying it in the standard sense must be handled in `landing()` so BFS tracks the landing room rather than the threshold room.
* **Instruction:** Clarify the dual responsibility of `landing()` by stating that any item affecting transit—whether blocking, rerouting, or teleporting the robot—must be reflected in `landing()`. For example: "A new kind of item that blocks the robot, relocates it, or changes which room it lands in needs a branch in `landing()` as well as its own `interact()`."

## Verdicts

Second run, on the Flash model. Applied in commit c65266cc, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The chapter already separates the two kinds of link: the section opens with "a teleport returns its paired room", the `Doors.connect()` sentence says "neighbors on the grid", the paragraph after `world.py` says whatever room `interact()` returns becomes `robot.room`, and the figure labels "doors to grid neighbors" apart from "Teleport: enter one b, land on the other".
2. Applied. A probe data class with a bare `group: asyncio.TaskGroup` after `init=False` fields had the signature `(maze: str, group: TaskGroup)`, and `Board("m")` raised `TypeError: missing 1 required positional argument: 'group'`. After the `Robot.room` comparison, the chapter now says `Robot` is an ordinary class and that in a data class a bare annotation adds a parameter to the generated `__init__()`, so `group` needs `field(init=False)`.
3. Applied, with a different fix. Tracing `ring_contention.py` confirms the reviewer's count: rats 1 and 2 each test the entry `(1, 1)` once, and no rat tests `(2, 3)` or `(3, 3)` as a backtrack, so the old order ("the cell from which it came, once per cell other than the entry") let "other than the entry" attach to the tested cell. The sentence now puts the rat's position first: "In every cell but the entry, the rat standing there tests the cell from which it came."
4. Rejected. "Moves it" already covers a teleport, the one existing item that sends the robot to another room, and the paragraph above `solver.py` lists the `Teleport` branch ("for a `Teleport` the target room"). An item's `interact()` either returns its own room, which the default branch handles, blocks, or sends the robot elsewhere, so "blocks the robot or moves it" names every case that needs a branch.
