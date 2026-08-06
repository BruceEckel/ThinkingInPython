[[Reviewed]]
# Deep review: 19_Concurrency.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Teach that cancellation arrives as a `BaseException`

**Kind:** teaching
**Where:** section "Structured Concurrency with `TaskGroup`" (after the `task_group.py` discussion, around line ~335)
**Problem:** The chapter shows cancellation three times (`e` and `f` cancelled by the `TaskGroup`, `task.cancelled()` returning `True`, and `t.cancel()` plus `gather(..., return_exceptions=True)` in `task_vs_thread_memory.py`) without ever saying what cancellation *is* at the language level. `asyncio.CancelledError` derives from `BaseException`, not `Exception` (verified on the pinned 3.15 build). A reader who writes the ordinary defensive `try` / `except Exception` inside a task never learns that it lets cancellation through, and a reader who writes `except BaseException` or a bare `except:` never learns that it swallows cancellation and leaves a `TaskGroup` waiting on a task that was told to stop. This is the single most common asyncio bug the chapter is currently silent about.

**Proposal:** add this paragraph after the "A partial failure cancels whatever was still in flight. / It does not erase what already succeeded." pair:

```
Cancellation reaches a task by raising `asyncio.CancelledError` inside it,
at whichever `await` it is suspended on.
That exception derives from `BaseException` rather than `Exception`,
which is deliberate.
A `try`/`except Exception` written inside a task to log and continue
does not catch cancellation,
so the task still stops the way the group intended.
The mistake runs the other way:
a bare `except:` or an `except BaseException:` around an `await`
catches the cancellation and keeps the task running,
which is how a `TaskGroup` block ends up waiting on a task that was told to stop.
If a task must clean up on the way out,
catch `asyncio.CancelledError` by name, do the cleanup, and re-raise it.
```

Also add a matching Guidelines bullet:

```
- **Cancellation is a `BaseException`, not an `Exception`.**
  `except Exception:` inside a task lets it through, which is what you want.
  Catching `asyncio.CancelledError` and not re-raising it strands the `TaskGroup`
  that asked the task to stop.
```

**Cost:** none. No listing changes, no new terms that later sections must honor. It strengthens the `except*` discussion sitting just above it.

---

## 2. Fix the free-threaded output block: `gil_threads.py` cannot print that line

**Kind:** code
**Where:** section "Free Threading" (line ~1128)
**Problem:** The text reads "Running `gil_threads.py` under a free-threaded interpreter turns the ratio around:" followed by an indented block showing `threads speedup: 3.8x`. `gil_threads.py` prints `threads no faster: {thr > seq * 0.9}` and cannot produce that line on any interpreter. A reader who installs `python3.15t` and follows the instruction sees `threads no faster: False` and concludes something is wrong with their build. The 3.8x number is real (the parenthetical says so), but the program that produced it is not the one named.

**Proposal:** replace

```
It removes the GIL, so threads run Python bytecode on separate cores at the same time.
Running `gil_threads.py` under a free-threaded interpreter turns the ratio around:
```

with

```
It removes the GIL, so threads run Python bytecode on separate cores at the same time.
Under a free-threaded interpreter `gil_threads.py`'s boolean flips to `False`.
Replacing its last line with `print(f"threads speedup: {seq / thr:.1f}x")`
reports the size of the win instead of the fact of it:
```

While here, the same paragraph is the right place to record that the build is no longer labelled experimental. Add after the `python3.15t` sentence:

```
[PEP 779](https://peps.python.org/pep-0779/) removed its "experimental" label in 3.14,
so it is a supported build now rather than a preview,
still optional and still installed alongside the default one.
```

**Cost:** none. The listing does not change, so no marker moves. The section is linked from `39_Pattern_Catalog.md` only by the parent heading `#the-gil-and-free-threading`, which stays.

---

## 3. Define the GIL before the chapter depends on it, and bridge the pivot into Parallelism

**Kind:** structure
**Where:** end of "Context That Follows the Call Chain" and opening of "Parallelism" (line ~707)
**Problem:** Two things go wrong at the same seam. First, "Parallelism" explains that `ProcessPoolExecutor` works because each process gets "its own interpreter and GIL", and that sentence carries the whole section's claim. But the GIL is not defined until "The GIL and Free Threading", 215 lines later. (Line 564 also uses "no GIL in sight" earlier still, though that one is rhetorical and survives.) A reader meeting the acronym for the first time in the sentence that explains *why processes give parallelism* cannot follow the explanation. Second, "Parallelism" opens cold: seven sections of `asyncio` end with `ContextVar`, and the next heading starts on CPU-bound work with no signpost that the chapter has turned a corner.

**Proposal:** open "Parallelism" with a bridging sentence that also glosses the term, before the existing "A CPU-bound task cannot overlap..." line:

```
Everything so far has overlapped waiting on one thread.
Computing is the other half, and it needs a second mechanism.
A CPU-bound task cannot overlap if only a single core is available.
With several cores, it can.
`ProcessPoolExecutor` runs each call in its own process,
each with its own interpreter and its own *Global Interpreter Lock* (GIL),
the interpreter-wide lock that lets only one thread run Python bytecode at a time.
[The GIL and Free Threading](#the-gil-and-free-threading) takes the lock apart;
what matters here is that there is one per interpreter,
so the operating system can place these processes on different cores and run them at the same time:
```

Then delete the now-duplicated definition sentence at the top of "The GIL and Free Threading" or reduce it to "The standard CPython build has one GIL for the whole process."

**Alternatives:** move the whole "The GIL and Free Threading" section ahead of "Parallelism". That reads better in the abstract, but it costs more than it buys: `gil_threads.py`'s closing line ("This is why [Parallelism](#parallelism) used processes instead") becomes a forward reference, and the GIL section's `thread_compare.py` harness currently benefits from the reader having already seen `pool.map()`.

**Cost:** touches the first paragraph of two sections. Inbound anchors `#parallelism` and `#the-gil-and-free-threading` are used by `39_Pattern_Catalog.md` and `43_Functional_Assurance.md`; neither heading changes.

---

## 4. Contrast `concurrent.futures.Future` with `asyncio.Future` and `Task`

**Kind:** teaching
**Where:** section "One Task, Many Backends", after the "`asyncio` does not fit here" paragraph (line ~1554)
**Problem:** This is the chapter's clearest unteached lookalike pair, and it sits directly under the paragraph that raises it. `pool.submit()` returns a `concurrent.futures.Future`; `tg.create_task()` returns an `asyncio.Task`; `loop.run_in_executor()` returns an `asyncio.Future`. Three objects, two of them called "Future", one awaitable set and one not. The near-miss a reader writes is `await pool.submit(f)`, which fails with `TypeError: 'Future' object can't be awaited` (verified). `mixed_await.py` uses `run_in_executor()` two paragraphs later precisely to cross this boundary, and the prose never says that is what it is for. `39_Pattern_Catalog.md` line 72 also points its "Future / Promise" row at this chapter, which currently mentions `Future` once in passing.

**Proposal:** add after "It is a suspended function that runs only when the event loop resumes it.":

```
The two models give their result-that-arrives-later the same name,
which invites one specific mistake.
`pool.submit()` hands back a `concurrent.futures.Future`,
and you wait on it by calling `result()`, which blocks the calling thread.
Awaiting it raises `TypeError: 'Future' object can't be awaited`.
`asyncio` has its own `Future`, and `Task` is a subclass of it,
so both are awaitable and neither blocks anything.
`loop.run_in_executor()` is the bridge between the two:
it submits to the executor and returns an `asyncio.Future`
that resolves when the executor's own future does.
That is why `process_price()` below calls it instead of `pool.submit()`.
```

**Cost:** none. No new listing; it explains a call `mixed_await.py` already makes.

---

## 5. Point forward from the race to the lock that fixes it

**Kind:** structure
**Where:** end of "A Single Thread Still Races" (line ~602) and opening of "Locks" (line ~1801)
**Problem:** "A Single Thread Still Races" closes by naming `asyncio.Lock` as the fix and then does not show one for 1,200 lines. The reader's question arrives at line 602 and is answered at line 1814. The tell the deep-review procedure names is present at the other end: "Locks, Semaphores, and Failure Modes" opens by re-establishing `async_race.py` from eight sections back.

**Proposal:** change the closing sentence of "A Single Thread Still Races" from

```
A read-modify-write that spans an `await` needs `asyncio.Lock`,
just as the same race between threads needs a `threading.Lock`.
```

to

```
A read-modify-write that spans an `await` needs `asyncio.Lock`,
just as the same race between threads needs a `threading.Lock`.
[Locks](#locks) returns to this listing and adds one.
```

**Cost:** none. `#locks` already exists as an anchor and is already linked from `24_Singleton.md`.

**Alternatives:** move the Locks subsection up to follow "A Single Thread Still Races". That is a real improvement to the arc but expensive: the Semaphore listing leans on `Meter` from "Overlapping the Waits", the Deadlock and Livelock subsections belong with it, and moving the whole four-subsection block leaves the second half of the chapter without its failure-modes finish. Not recommended.

---

## 6. Broaden the exercise set past the first three sections

**Kind:** exercise
**Where:** section "Exercises" (line ~2110)
**Problem:** Eight exercises draw on six listings, and five of the eight come from the chapter's first 600 lines (`async_mechanics.py` twice, `peak_concurrency.py` twice, `async_locks.py`). Nothing exercises `TaskGroup` or `gather(return_exceptions=True)`, which is one of the chapter's two biggest sections; nothing exercises `ContextVar`, subinterpreters, the three new 3.15 iterator wrappers, deadlock, or livelock. The chapter's main claims are not covered by its practice.

**Proposal:** add four exercises. Suggested wording:

```
9.  In `task_group.py`, change `("e", 0.2)` in `PAIRS` to `("e", 0.005)`
    so `e` finishes before `c` and `d` fail.
    Predict which of the six report `cancelled` and which report a result,
    then run it and explain what a `TaskGroup` can and cannot undo.
10. In `gather_with_exceptions.py`, delete `return_exceptions=True`
    and wrap the `await` in `try`/`except ValueError`.
    Predict how many `fetched` lines still print, and explain what
    became of the tasks the `gather()` call never reported on.
11. In `context_var.py`, move `request_id.set(name)` out of `handle()`
    and into `main()` above the `TaskGroup`.
    Predict what each task prints, then explain the result with
    "every task starts with a copy of the context that created it."
12. In `subinterpreters.py`, replace `InterpreterPoolExecutor`
    with `ThreadPoolExecutor`.
    The assertion still passes and the printed boolean flips.
    Explain both, using [The GIL and Free Threading](#the-gil-and-free-threading).
```

**Cost:** none, if the numbering stays sequential. Exercise 9 edits `utils/fetch_demo.py`, which `gather_with_exceptions.py` also imports, so it is worth saying "change it back afterward" if you keep it.

**Alternatives:** if four is too many, exercises 9 and 12 carry the most weight (the `TaskGroup` contract and the subinterpreter/GIL connection). Exercise 11 is the only one that would exercise `ContextVar` at all.

---

## 7. Warn that a bare `create_task()` needs a strong reference

**Kind:** teaching
**Where:** section "Structured Concurrency with `TaskGroup`" (near line ~313, where `tg.create_task()` is introduced)
**Problem:** The chapter introduces `create_task()` only inside a `TaskGroup`, which holds strong references for you, and inside `task_vs_thread_memory.py`, which binds the list. A reader who takes `create_task()` out of those settings writes `asyncio.create_task(handle(req))` and discards the result. The event loop keeps only a weak reference (still documented as such in the 3.15 docs), so such a task can be garbage-collected mid-execution and vanish with no error. It is a silent failure, which makes it worth naming even though every listing in the chapter happens to avoid it.

**Proposal:** add after "`tg.create_task()` schedules a task immediately, so all six are in flight together.":

```
Holding the task objects is not optional bookkeeping.
The event loop keeps only weak references to its tasks,
so a task whose last strong reference is discarded can be collected mid-execution
and stop with nothing printed and nothing raised.
A `TaskGroup` holds its own references until the block exits.
Outside one, keep the returned task in a variable or a set that outlives it.
```

**Cost:** none.

---

## 8. Say that `Executor.map()` defers its exceptions to iteration

**Kind:** teaching
**Where:** section "Parallelism", in the two-item list after `parallel_cpu.py` (line ~740), or in "One Task, Many Backends" near `any_executor.py`
**Problem:** `list(pool.map(...))` appears in five listings. `map()` returns a generator and raises nothing itself; a worker's exception surfaces only when the corresponding result is consumed (verified). Readers who have just been taught that `gather()` and `TaskGroup` differ in exactly how they surface failures will assume `Executor.map()` has a policy too, and the chapter never states it. It also explains why every listing wraps the call in `list()`.

**Proposal:** add a third numbered item to the list after `parallel_cpu.py`:

```
3. `pool.map()` raises nothing itself.
   It returns a generator, and a worker's exception is re-raised
   in the calling process when you consume that worker's result.
   `list(...)` around the call is what turns a failure in any worker
   into an exception here, at a point you can catch it.
```

**Cost:** the surrounding prose says "Two issues separate a process pool from every in-process tool in this chapter, and both surface in this short listing." That sentence needs to become "Three issues...", and the third one is not process-specific (it is true of every `Executor`), so the sentence may need rewording, or the item may belong in "One Task, Many Backends" instead.

---

## 9. Note that the `__main__` guard is now required on every platform

**Kind:** teaching
**Where:** section "Parallelism", item 1 after `parallel_cpu.py` (line ~742)
**Problem:** The explanation ("the operating system starts a fresh Python interpreter, and that interpreter *imports* this module") is correct today, but it became correct for Linux only in 3.14, when the default start method stopped being `fork` on every platform (`forkserver` on Linux, `spawn` on Windows and macOS). A large body of existing advice, and a lot of reader muscle memory, says the guard is a Windows requirement. Readers carrying that belief will read the paragraph as describing someone else's platform.

**Proposal:** append to item 1:

```
   This used to be a Windows and macOS concern only,
   because Linux forked the parent process instead of importing anything.
   Since 3.14 no platform forks by default,
   so the guard is required everywhere.
```

**Cost:** none. Verify the wording against the 3.15 `multiprocessing` docs before implementing, since the default may keep moving.

---

## 10. Version-tag the `ContextVar` token context manager

**Kind:** teaching
**Where:** section "Context That Follows the Call Chain" (line ~664)
**Problem:** The chapter tags versions carefully everywhere else: `TaskGroup` (3.11), subinterpreters (3.12), `InterpreterPoolExecutor` (3.14), the three iterator wrappers (3.15). `with request_id.set(name):` is 3.14 and carries no tag, and the sentence that follows ("Before the token grew this protocol you wrote `token = var.set(x)` and a matching `var.reset(token)` in a `finally`") tells the reader there was a before without saying when it ended. On 3.13 the `with` form raises an `AttributeError`.

**Proposal:** change "Setting a variable for part of a call and restoring it afterward is common enough that `set()` returns a token usable as a context manager:" to "...that `set()` returns a token usable as a context manager (3.14):" and change "Before the token grew this protocol" to "Before 3.14".

**Cost:** none.

---

## 11. Give the iterator-sharing section a Guidelines bullet

**Kind:** structure
**Where:** section "Guidelines" (line ~2012)
**Problem:** The Guidelines list has eleven bullets and covers every section except "Sharing an Iterator Between Threads" and "Context That Follows the Call Chain". The iterator section is the chapter's only coverage of three APIs new in 3.15, and it ends on the most misleading failure in the chapter (duplicated work with a correct-looking distinct count). A reader skimming the Guidelines for what to remember gets no signal that the section exists.

**Proposal:** add two bullets, after the queue bullet:

```
- **An iterator handed to several threads is not thread-safe,
  and it fails quietly.**
  Wrap one you have with `threading.serialize_iterator()`,
  wrap the generator function that makes them with
  `threading.synchronized_iterator()`,
  and use `threading.concurrent_tee()` when every worker needs the whole stream.
  A lock inside the loop body guards the wrong thing:
  the `for` statement calls `next()` outside it.
- **Pass request-scoped values in a `ContextVar`, not a global.**
  Each task starts from a copy of the context that created it,
  and `asyncio.to_thread()` carries that copy into the worker thread.
```

**Cost:** none.

---

## 12. Minor items

**Kind:** prose | code
**Where:** various
**Problem / Proposal:** small enough to list together. Strike any line to reject it.

- Line ~1354, `shared_iterator.py`: `Tickets` carries a docstring, `"Hands out each number once: read, pause, write back."` The house rule is that chapter listings explain themselves in the surrounding prose, not in a docstring. Move the sentence into the paragraph after the listing, or leave it if the docstring is deliberate here (it is the only one in the chapter).
- Lines ~1692-1693, `task_vs_thread_memory.py`: `TASKS = 5_000` and `STACK_SIZE = 1024 * 1024` are the chapter's only `UPPER_CASE` constants without the `Final[T]` form (`TOTAL`, `CORE_MULTIPLIER`, `LIMIT`, and `READERS` all have it). I did **not** apply this one: adding `from typing import Final` to that file measurably shifts the `tracemalloc` result, moving the marker `tasks fitting in one thread's stack: 777` to `776` and making the prose's "roughly 777 suspended tasks" stale. Verified deterministic across five runs each way; a bare extra comment line does not move it, only the `typing` import does. Accepting this means updating the marker and the prose sentence too.
- Line ~219: `it wraps and *schedules* every coroutine as a task` uses italics for emphasis rather than to introduce a term. Drop the italics.
- Line ~224: "Each runs until its first `await`, which the `a: started`, etc., lines in the trace show." Three commas and a mid-sentence "etc." Suggest: "Each runs until its first `await`, which is what the `started` lines in the trace record." (or reword to taste).
- Lines ~910 and ~2036: "buys real gains" and "sometimes buys a little more". "buy" is on the avoid-if-possible list. "yields real gains" and "sometimes yields a little more" both work.
- Line ~2169: "are where STM actually succeeded as a practical, widely used tool." Drop "actually"; the contrast with the preceding Python sentences already carries it.

**Cost:** none, except the second bullet, which moves an output marker and one sentence of prose.

---

## Already fixed directly (no decision needed)

- line ~127: `Two other approaches appear later in this chapter. each running inside a single process.` was a sentence-break typo; changed the period to a comma.
- line ~598: "landing at points the interpreter picks" used `land` in the metaphorical sense on the don't-use list; changed to "occurring at points the interpreter picks".
- line ~1059: "so workarounds shipped instead" used `ship` in the metaphorical sense on the don't-use list; changed to "so workarounds appeared instead".
- line ~1145: "Immortality landed in 3.12" changed to "Immortality arrived in 3.12", same reason.
- line ~1879: "a preemptive switch could land between them" changed to "could fall between them", same reason.
- line ~747: "the guard keeps each worker from running `main()`" named a function that does not exist in `parallel_cpu.py`; changed to "from running the guarded block".
- line ~2133, exercise 6: "Remove the `if __name__ == "__main__"` guard from `parallel_cpu.py`, calling `main()` unconditionally" instructed the reader to call a function the listing does not define; changed to "so its body runs unconditionally".
- line ~1755, `thread_vs_task_speed.py`: `COUNT = 3000` became `COUNT: Final[int] = 3000` with `from typing import Final` added, matching the `Final[T]` form the chapter's other constants use. Verified: runs clean, output marker unchanged, `ruff` and `ty` pass.
- line ~242, `utils/fetch_demo.py`: `PAIRS = [...]` became `PAIRS: Final[list[tuple[str, float]]] = [...]` with `from typing import Final` added, same reason. Verified: `task_group.py` and `gather_with_exceptions.py` both still reproduce their markers exactly, and `ty` passes.

## Verified, no change needed

Ran every listing in `build/examples/19_Concurrency` against its `#:` markers; all match. The four listings flagged in `CLAUDE.md` as flaky were run repeatedly under concurrent load from the sibling review agents: `task_group.py` (16/16 lines stable), `gil_threads.py` (`True` on every run), `task_vs_thread_memory.py` (identical output on nine runs), and `shared_iterator.py` / `shared_generator.py` / `concurrent_tee.py` (identical on five runs each). `ruff check` and `ty check` both pass on the chapter. The `counter += 1` disassembly at line ~1072 matches what 3.15 actually emits, including `LOAD_SMALL_INT` and `BINARY_OP 13`. All nine inbound anchors from other chapters (`#locks`, `#asyncio-mechanics`, `#parallelism`, `#the-gil-and-free-threading`, `#coordinating-threads-with-queues`, `#a-single-thread-still-races`, `#structured-concurrency-with-taskgroup`, `#sharing-an-iterator-between-threads`, `#context-that-follows-the-call-chain`) resolve, as do all seven outbound links. `threading.serialize_iterator`, `synchronized_iterator`, and `concurrent_tee` are confirmed present on the pinned 3.15 build and confirmed to be 3.15 additions.
