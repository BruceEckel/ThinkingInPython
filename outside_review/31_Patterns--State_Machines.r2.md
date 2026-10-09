<!-- outside review of Chapters/31_Patterns--State_Machines.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `31_Patterns--State_Machines.md` chapter:

**1. Section: Table-Driven State Machine (Prose contradicts preceding variation)**

* **Target Text:** "The each-state-decides design keeps each state's transitions inside the state class."
* **Issue:** In the preceding section ("A Table Inside Each State"), the state classes do not hold their transitions; as that section explicitly explains, circular references between states require the transition tables to be populated on state instances at the module level. Only the first variation ("One State Class per Behavior") houses transitions inside the class bodies.
* **Instruction:** Clarify that the first design associates transitions with individual state objects or classes: change "keeps each state's transitions inside the state class" to "associates transitions with each individual state (whether in `next()` or in each state's table)".

**2. Section: A Vending Machine (Unqualified transition description)**

* **Target Text:** "`Money` moves the machine to `COLLECTING` and keeps it there,"
* **Issue:** The sentence implies `Money` transitions to `COLLECTING` from any state, but in `vending_machine.py`, `Money` is only a key from `QUIESCENT` and `COLLECTING`. From `SELECTING`, `UNAVAILABLE`, and `WANT_MORE`, the table contains no transition for `Money`, so feeding `Money` in those states raises `NoTransition`.
* **Instruction:** Qualify the starting state by changing the phrase to: "From `QUIESCENT`, `Money` moves the machine to `COLLECTING` and keeps it there on additional coins,".

**3. Section: Which Design Should You Use? (Incomplete trade-off description)**

* **Target Text:** "Inside that design, `match` statements and per-state tables differ in which code handles an unrecognized input."
* **Issue:** The difference between `match` and per-state tables is not just where unhandled input is dispatched; it also directly governs where transitions are declared. With `match`, transitions are declared inside each state's class body, whereas per-state tables must be assigned at the module level after all state instances exist to resolve forward references.
* **Instruction:** Note both differences: change the sentence to: "Inside that design, `match` statements and per-state tables differ in where transitions are declared and in which code handles an unrecognized input."

## Verdicts

Second run, on the Flash model. Applied in commit 03800bd1, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The sentence was wrong for the second variation: `mouse_trap_tables.py` stores each state's transitions in its object's `transitions` dict, filled in at module level, not in the class. The opening of "Table-Driven State Machine" now says the each-state-decides design keeps each state's transitions with that state, in its `next()` or in its table.
2. Applied. A probe against the extracted `vending_machine.py` showed `Money` moves `QUIESCENT` to `COLLECTING` and raises `NoTransition` from `SELECTING`, `UNAVAILABLE`, and `WANT_MORE`, so the unqualified sentence overstated the table. It now reads "`Money` moves the machine from `QUIESCENT` to `COLLECTING`, and more `Money` keeps it there," matching the figure's two `Money` edges.
3. Rejected. The paragraph the target sentence opens already states the second difference in its closing sentence ("every state's transitions have the same shape and sit together at the bottom of the file"), and "A Table Inside Each State" explains why the tables must be filled in at module level; adding it to the topic sentence would say it twice.
