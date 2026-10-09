<!-- outside review of Chapters/19_Techniques--Concurrency.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `19_Techniques--Concurrency.md` chapter:

**1. Section: Measuring the Speedup (Test methodology correction)**

* **Target Text:** `list(pool.map(work_chunk, [1]))`
* **Issue:** `ProcessPoolExecutor` spawns worker processes on demand up to its maximum worker limit. Passing an iterable with a single item `[1]` only spawns one worker process, meaning the remaining workers will be spawned during the first timed run, which adds process-startup overhead and artificially inflates the baseline measurement.
* **Instruction:** Change the list to supply enough tasks to force the pool to spawn all of its workers: `list(pool.map(work_chunk, [1] * cores))`

**2. Section: Livelock (Semantic correction)**

* **Target Text:** `for _ in range(3):`
* **Issue:** The loop only runs for three iterations, meaning the tasks successfully finish and exit. This contradicts the prose stating that "none of them makes progress" and "nothing finishes". To properly demonstrate a livelock without hanging the book's automated test runner, the tasks should run indefinitely but be bounded by a timeout from the caller.
* **Instruction:** Change `for _ in range(3):` to `while True:`. In `main()`, replace the `await asyncio.gather(...)` and `print(...)` lines with a `try`/`except TimeoutError` block that awaits `asyncio.wait_for(asyncio.gather(giver("a"), giver("b")), timeout=0.1)` and prints `"livelock detected"` in the except block (exactly as you did for the deadlock example).

**3. Section: The GIL Does Not Prevent Races (Technical correction)**

* **Target Text:** `LOAD_SMALL_INT  1        # Push the constant 1`
* **Issue:** CPython bytecode does not have a `LOAD_SMALL_INT` opcode. The instruction for pushing a literal constant value like 1 onto the stack is `LOAD_CONST`.
* **Instruction:** Change `LOAD_SMALL_INT` to `LOAD_CONST`.

## Verdicts

Applied in commit 96eedb2c, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. A probe of the listing showed one worker after the `[1]` warm-up and the pool still starting workers inside the timed runs (8 at 8 tasks, 24 at 64); the item's `[1] * cores` started 12 of 32, because quick tasks free their workers while the pool is still starting the rest. The warm-up now maps `time.sleep()` over `[1] * cores`, which started all 32, a new paragraph says why, and the sample output is a fresh run (8.57x at 32 tasks, against 5.85x when startup sat in the timings).
2. Applied, with a different fix. A probe of the item's `while True` under a 0.1-second `wait_for()` printed 49,993, 49,993, and 48,511 lines in three runs, so the `#:` marker could not hold. The "nothing finishes" sentence describes a real livelock, and the prose now says, as the deadlock section does for its timeout, that a real livelock repeats forever and `range(3)` stops the listing after three rounds.
3. Rejected. `dis.dis()` of a function doing `counter += 1` on 3.15.0rc2 shows `LOAD_SMALL_INT 1` between `LOAD_GLOBAL` and `BINARY_OP 13 (+=)`, so the opcode exists and the chapter's listing matches.
