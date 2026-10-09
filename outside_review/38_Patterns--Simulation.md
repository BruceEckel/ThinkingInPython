<!-- outside review of Chapters/38_Patterns--Simulation.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `38_Patterns--Simulation.md` chapter:

**1. The Rat and the Blackboard (Caveat)**
* **Target Text:** "The missing `await`, not a lock, makes `claim()` atomic."
* **Issue:** Atomicity without a lock relies on the `asyncio` event loop running in a single thread, which prevents two tasks from executing synchronous code simultaneously. If the tasks were running across a thread pool, the missing `await` would not prevent a race condition.
* **Instruction:** Change to: "Because `asyncio` tasks run in a single thread, the missing `await`, not a lock, makes `claim()` atomic."

**2. The Rat and the Blackboard (Technical Detail)**
* **Target Text:** "When a rat claims more than one neighbor, it keeps the first for itself and spawns a new rat at each of the others."
* **Issue:** Because the list comprehension evaluates `claim()` on all neighbors sequentially before reaching the `await asyncio.sleep(0)`, a rat greedily reserves every open branch in a single turn. It locks out competing rats from those cells before the spawned siblings even begin to run.
* **Instruction:** Add a sentence after the target text: "Because the comprehension evaluates every neighbor before the task yields, the rat greedily reserves all those branches at once, locking out other rats before the siblings even spawn."

**3. Rooms, Robots, and the Item Factory (Caveat)**
* **Target Text:** "A new kind of item registers itself. Once you define the subclass with its symbol, the factory finds it."
* **Issue:** The factory instantiates items using `item_type()` with zero arguments. If a reader defines a new item subclass whose `__init__` requires arguments (as `Teleport` does, though its empty symbol hides it), the factory will crash with a `TypeError` when it attempts to build that item.
* **Instruction:** Add a caveat: "Because the factory calls `item_type()` with no arguments, any new item subclass must either take no arguments or provide defaults for all of them."

**4. Building the Maze in Stages (Edge Case)**
* **Target Text:** "A typo that gives a letter one room, or three, fails here at build time, naming the offending letter."
* **Issue:** If a maze layout contains exactly two identical unrecognized characters (such as two stray punctuation marks or letters), `item_factory` falls back to `Teleport` for both. The builder will successfully pair them up and silently create a working teleport instead of failing at build time.
* **Instruction:** Add a clarifying sentence after the target text: "If exactly two identical typos exist, the factory silently pairs them as a valid teleport, which can cause baffling jumps during the run."

## Verdicts

Applied in commit 798bd19b, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The chapter already states the single-thread premise where it introduces the blackboard: "The rats run as cooperative `asyncio` tasks. They take turns, one at a time, and each rat finishes its update before the next one runs, so the blackboard needs no lock." The `claim()` paragraph builds on that and links the single-thread race in chapter 19, so a thread-pool caveat restates it.
2. Rejected. The chapter already says the rat calls `claim()` on each of the four neighbors and that claiming reserves a cell, and the reviewer's sentence is wrong on the order: a probe maze with a fork logged "Rat 2 starts at (3, 1)." before rat 1 yielded, because `spawn()` builds each sibling `Rat` in the same synchronous turn as the claims; only the siblings' tasks wait for the `await`.
3. Applied, with a different fix. A probe `Item` subclass with symbol `$` and a required `__init__()` argument made `item_factory("$")` raise `TypeError: Gem.__init__() missing 1 required positional argument: 'value'`. The paragraph on `item_factory()` now says the factory calls `item_type()` with no arguments, so a new item's `__init__()` must accept none, and explains why `Teleport`, which requires a target letter, never reaches that call: a one-character maze string never equals its empty `symbol`.
4. Rejected. `GameBuilder("#%R%#")` builds, and moving east from `R` lands on the far `%`, but that is the format's rule rather than a gap: `item_factory()` comments "Anything else is a teleport target", and the assert enforces two rooms per target letter, which a matched pair obeys. The chapter's maze holds no stray characters, so a warning about accidental pairs guards a case the listing's input never exercises.
