<!-- outside review of Chapters/19_Techniques--Concurrency.md, model gemini-3.8-flash-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `19_Techniques--Concurrency.md` chapter:

**1. Section: What a Process Pool Requires (inaccurate claim about default start methods)**

* **Target Text:** "Since 3.14 no platform forks by default, so every platform requires the guard."
* **Issue:** In Python 3.14, Linux's default start method changed from `fork` to `forkserver`, while macOS and Windows default to `spawn`. The `forkserver` method still uses `fork()` (from a dedicated pre-forked server process) rather than creating fresh processes from scratch. Stating that "no platform forks by default" conflates the elimination of the direct parent-process `fork` default on Linux with `spawn`.
* **Instruction:** Clarify the distinction between `spawn` and `forkserver` while preserving the point about the `if __name__ == "__main__"` guard: "Since 3.14 no platform uses raw parent-process forking by default (Linux defaults to `forkserver`, while macOS and Windows default to `spawn`), so every platform requires the guard."

**2. Section: The GIL Does Not Prevent Races (version accuracy on thread switching)**

* **Target Text:** "Since 3.10 the interpreter switches threads only at a function call or at the jump that closes a loop iteration, so nothing interrupts this particular sequence in practice."
* **Issue:** Moving the periodic check for pending signals and thread switching (`eval_breaker`) from every bytecode instruction to backward branches (`JUMP_BACKWARD`) and function calls was introduced in Python 3.11 as part of PEP 659 (the Faster CPython interpreter overhaul), not in Python 3.10. In 3.10, thread switches could still occur across arbitrary bytecode instruction boundaries when the switch interval elapsed.
* **Instruction:** Update "Since 3.10" to "Since 3.11".

**3. Section: Structured Concurrency with TaskGroup (contradictory description of task bookkeeping)**

* **Target Text:** "Holding the task objects is essential bookkeeping. The event loop keeps only weak references to its tasks, so a task that loses its last strong reference can disappear mid-execution, printing nothing and raising no exception. A `TaskGroup` holds its own references until the block exits."
* **Issue:** The paragraph claims that storing the return values of `tg.create_task()` in `tasks = {...}` is essential bookkeeping to keep tasks from being garbage-collected mid-execution, but then immediately notes that `TaskGroup` holds its own references until the block exits. Because `TaskGroup` retains strong references to all of its tasks, keeping the `tasks` dictionary in `task_group.py` is only necessary to inspect individual results and exceptions after the group exits. The warning about unreferenced tasks vanishing mid-run applies to tasks spawned directly via `asyncio.create_task()`.
* **Instruction:** Reframe the paragraph to distinguish inspecting outcomes from preventing task garbage collection: "Holding the task objects lets you inspect each outcome after the group exits. Outside a `TaskGroup`, holding the returned task object is also essential bookkeeping against garbage collection: the event loop keeps only weak references to its tasks, so an unreferenced task can disappear mid-execution. A `TaskGroup` holds its own strong references to its tasks until the block exits."

**4. Section: `async def`, `await`, and the Event Loop (prose contradicts subsequent explanation of `gather()` execution)**

* **Target Text:** "`gather()` wraps each coroutine in a *task*, the event loop's unit of scheduling, and starts the tasks in the order given. Each runs until it reaches its `await`, so the started lines print as a, b, c."
* **Issue:** Calling `asyncio.gather(...)` creates and schedules the tasks on the event loop, but it does not execute any task bodies. As the section itself notes two paragraphs later ("Scheduling does not mean running. `gather()` returns an awaitable without running any task body. The bodies execute after `main()` suspends at its `await`"), the tasks begin running only when `main()` yields control at `await asyncio.gather(...)`. Saying earlier that `gather()` "starts the tasks in the order given" and that "Each runs until it reaches its `await`" misstates what `gather()` does upon invocation and contradicts the explanation below it.
* **Instruction:** Revise the sentence to reflect that `gather()` schedules the work rather than executing it synchronously: "`gather()` wraps each coroutine in a *task*, the event loop's unit of scheduling, and schedules the tasks in the order given. When `main()` suspends at its `await`, the event loop runs each task until its own `await`, printing the started lines as a, b, c."

## Verdicts

Second run, on the Flash model. Applied in commit 20e0dc63, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. In the WSL clone, `multiprocessing.get_start_method()` on 3.15.0rc2 printed `forkserver`, and a guarded three-worker pool printed the module's top-level line once as `__main__` and once as `__mp_main__`, so the server imports the module once and forks the workers from it; an unguarded copy still died with a `RuntimeError` and `BrokenProcessPool`. The prose now says no platform forks the parent by default, names `forkserver` for Linux and `spawn` for macOS and Windows, and says what each does.
2. Rejected. A four-thread `counter += 1` loop under `sys.setswitchinterval(1e-6)` lost 2,504,216 increments on 3.9.25 and none on 3.10.21 or 3.11.16, so the switch-point change arrived in 3.10 (bpo-29988), as the chapter says.
3. Applied. `len(tg._tasks)` printed 3 inside a block that kept no reference to its three tasks, after a `gc.collect()`, and all three finished, so the group's own references keep its tasks alive. The paragraph now says the `tasks` dict exists so the loop after the block can read each outcome, and ties the weak-reference warning to the `TaskGroup`'s strong references instead of to the dict.
4. Applied, with a different fix. "starts the tasks in the order given" did contradict the later "Scheduling does not mean running" paragraph. That paragraph's explanation moved up to replace the contradicting sentence ("schedules the tasks"), and its remaining lines, which repeated the comprehension paragraph above them, were dropped rather than duplicated.
