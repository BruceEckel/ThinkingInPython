> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 19_Techniques--Concurrency (2026-10-13)

I checked each claim against its listing and the chapters this one links (15, 18, 22, 23, 30, 38), read the incoming links from 03, 18, 23, 24, 38, 43, and 45 against the sections they name, and probed the pinned interpreter (3.15.0 final, uv's managed build) and `ty` 0.0.86.
Reproduced: the `asyncio.run()` nesting message, `'Future' object can't be awaited`, `TaskGroup.cancel()`, the `BoundedSemaphore` and `Lock` messages, the `counter += 1` bytecode, `serialize_iterator()`'s `send()`/`throw()`/`close()` wrapping and `concurrent_tee()`'s one-thread rule (from the 3.15 source), the shared-iterator duplicates (eight copies of nearly every ticket, three runs), the generator's seven-of-eight `ValueError` (five runs), and the solution 10 claim that `ty` passes the version without `return`.
Every timing listing registered in `timing.txt` ran three times standalone with `--numbers`; each boolean held with a wide margin (`gil_threads.py` ratios 0.98 to 1.02 against 0.9), so no threshold, loop size, or marker changed.
The four unmarked listings (`parallel_cpu.py`, `multiprocessing_raw.py`, `any_executor.py`, `mixed_await.py`) print what the prose says.
`tip verify-ch CH=19 ISOLATED=1` passes 27 of 27 before and after.
No live blocks.

## Applied directly

Chapter, structure:

- Moved "Deadlock and Livelock" from after "Are Threads Still Necessary?" to directly after "Semaphores". It depends only on `asyncio.Lock`, `gather()`, and `wait_for()`, all taught by then; next to the lock sections it reads as the failure two locks bring, where before it trailed the threads-versus-tasks conclusion. Added a lead sentence ("A lock fixes a race, but a program that takes two locks can stop altogether."). No heading or anchor changed, no other chapter links `#deadlock` or `#livelock`, and the forward link from "Bounding a Wait" still resolves. The Guidelines list keeps its order. The close alternative was after "Coordinating Threads with Queues", but both listings are `asyncio` and belong beside `async_locks.py`.

Chapter, corrections:

- "One `await`, Any Backend": "its first `submit()` spawns the workers" is true only under `fork`. Under `spawn` and `forkserver`, every platform's default since 3.14, `_adjust_process_count()` spawns one worker per `submit()` that finds no idle one. Now says so.
- "A Real Socket": "`open_connection()` opens the client side of that same socket" is a client socket connected to the server, not the listener. "Both awaits" had two candidate pairs; it is now each `await` on a reader, the one that waits for bytes.
- `subinterpreters.py` (and Solutions exercise 12): the comment "Two cores cannot give 1.5x" was false in principle (two cores allow 2x). Now "Lower on one or two cores", which is what `min(1.5, cores * 0.7)` does.
- "Livelock": "no timeout can fix it" contradicted the deadlock demo, where `wait_for()` also only reports. The point is that no lock acquisition waits, so a lock-acquisition timeout has no wait to cut short.
- "Measuring the Time": "Tasks have no equivalent ceiling" now names the ceiling tasks do have, heap memory, and the per-thread resources they skip.
- "Free Threading": "adds lock overhead the GIL never charged" implied the GIL build needs no lock for that counter. Now: every increment also acquires and releases the lock.
- Guidelines: "An iterator handed to several threads ... fails quietly" contradicted `shared_generator.py`, which fails loudly. The bullet now names both failures. "A shared lock prevents deadlock only if every user agrees on the order" now speaks of several locks, since one lock cannot deadlock.
- Exercise 6: the link text "Parallelism" pointed at `#what-a-process-pool-requires`; the text now names that section.
- Footnote `concurrency-def`: "that talk" had no antecedent until the next paragraph. The talk and its link now come first.

Chapter, prose:

- "Here, each interpreter has its own" repeated the clause before it; now "No process waits on another process's GIL".
- Figures: "`blocking_the_loop.py` turned inside out", "a pool of threads absorbs blocking calls", "a thread's remaining job is to absorb a blocking call", "strands the `TaskGroup`", "has passed an audit", "tracked by PEP 703".
- "genuinely" dropped twice; "avoiding the per-worker process cost" is "without starting a process per worker".
- "Raise `TOTAL`" and "raise the count" are "Increase", since "raise" in this book means an exception.
- "Subinterpreters work on standard Python, and do not need free threading" stated positively.
- Guideline "`asyncio` is justified if" is "`asyncio` helps when"; "the same fix a lock gives for threads" names `threading.Lock`; exercise 15's "then run it" names the file; "With threads, that point is" names the failure it points at.
- Added `threading.Barrier` and `asyncio.Barrier` (3.11) to the Barriers bullet, since the list otherwise implies Python has none.
- Split two `TaskGroup` paragraphs at their seams: scheduling from strong references, and the cancellation of `e` and `f` from why both failures reach the group.

Solutions:

- Exercise 10: the paragraph about leaving out `return` came before the listing it describes. It now follows the trace explanation.
- Exercise 13: the step label "Lock the loop body." read as advice to make the wrong fix. Now "See what the lock does cover."
- Exercise 3 hint: "I/O-Bound vs CPU-Bound ... measure overlap with `meter.peak`" was false for that section; each link now says what its section supplies.
- Exercise 6 hint: `__mp_main__` appears in the traceback, not the `RuntimeError` text.
- Exercise 9 heading: "before the failures land" is "arrive" (tier-3 word). No prose refers to this exercise by number.
- Exercise 8: a doubled "therefore"; exercise 3 hint: "while it is suspended" is "while it waits at an `await` there".

## Considered and declined

- **`task_scaling.py`'s 32-to-64 reversal.** My run on the same 32-core machine kept improving at 64 tasks (8.66x to 9.13x). The prose says "flattens or reverses" and calls the printed run one machine's output, so it stays.
- **`ProcessPoolExecutor` "does not expose" `Manager`, `Value`, or `Array`.** A `Manager` proxy can be passed to a pool's function, but the pool itself offers no such state, which is the sentence's point.
- **Solutions exercises 13 and 14 named `ch19_*.py` rather than `exercise_N.py`.** Renaming them touches generated files and the pytest uniqueness check for no reader benefit.
- Carried forward from the r1 review: exercise renumbering, the `3.8x` figure, the one-mebibyte stack sentence, `shared_iterator.py`'s local `report()`, the forward GIL link, the `Lock is not acquired` period, and the GIL history dates.

## For the session

- `tip verify-ch` regenerated `Examples/19_Techniques--Concurrency/subinterpreters.py` and `Solutions/19_Techniques--Concurrency/exercise_12.py` from the comment change; both belong in the commit.
- `tip prose CH=19` lists three stale `watch_words` baseline entries for this chapter (the lines they matched were rewritten) and one stale `internal_names` entry in chapter 15 (`banner_cm.py::banner.title`), not from this review.
