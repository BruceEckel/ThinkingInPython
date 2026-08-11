When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/19_Concurrency.md` in the
clean-slate sweep. The previous round's review (recoverable at
`ce118d4:deep_review/~19_Concurrency.md`) had every block accepted,
and each of those changes is verified present in the current text.
The mechanical layer is sound: all `#:` markers validate, `ty` and
ruff are clean on `build/examples/19_Concurrency`, and all 30 scripts
run. Every timing boolean held under repetition with sibling
worktrees loading the machine: 5 of 5 runs for `gil_threads`
(untouched, per the standing rule), `io_threads`,
`blocking_the_loop`, and `to_thread`; 3 of 3 for `subinterpreters`,
`thread_vs_task_speed`, `task_vs_thread_memory`, `gil_race`,
`shared_iterator`, and `shared_generator`. The twelve
ordering-sensitive traces (`task_group.py`'s cancellation demo among
them) were byte-identical across three runs each, and `make verify`
left no marker diff anywhere. Probes on the pinned 3.15.0b4 confirmed
the quoted messages verbatim (`asyncio.run() cannot be called from a
running event loop`, `'Future' object can't be awaited`) and the API
claims: `TaskGroup.cancel()`, `threading.serialize_iterator()`,
`synchronized_iterator()`, and `concurrent_tee()` all exist, a stray
`Semaphore.release()` really does raise the limit from one to two,
and the default start method here is `spawn`. The BOCPY and rsloop
footnote links resolve and match their descriptions.
`resources/images/concurrency_models.svg` exists, `assert_never` and
PEP 798 unpacking are both taught before this chapter uses them
(chapters 8/13 and 16), and no listing carries a hand-written
`__init__`.

## Applied directly

- Deadlock section: `asyncio.wait_for()` was the one construct the
  chapter used without teaching it. "Here, the timeout ensures that
  the example terminates" now says what the function does: when its
  deadline passes, it cancels the `gather()` and raises a
  `TimeoutError`, so the example reports the deadlock instead of
  hanging.
- Added exercise 15 and its Solutions entry: awaiting `pool.submit()`
  directly in `mixed_await.py`. It covers the chapter's one
  unexercised lookalike pair (`concurrent.futures.Future` against
  `asyncio.Future`), which the previous review called the pair a
  reader hits in real code within a week. Verified both halves by
  running the broken variant (the `TypeError` arrives wrapped in an
  `ExceptionGroup`, reinforcing the `TaskGroup` lesson) and by `ty`
  (`invalid-await`).
- `multiprocessing_raw.py`: both bare `mp.Queue` annotations are now
  `mp.Queue[tuple[int, int]]`. Every other queue in the chapter is
  parameterized; verified at runtime (lazy annotations keep the
  subscript unevaluated) and under `ty`, and the `def` line is
  exactly 70 columns, inside ruff's limit.
- Overlapping the Waits: cut the cleft from "which is what let all
  five `io_price` tasks overlap."
- Deadlock definition: "*Deadlock* happens when..." is now "In a
  *deadlock*, two or more tasks each hold a resource the other
  needs..." (watch-list "happen").
- Solutions 6: the closing paragraph framed the missing guard as a
  Windows/macOS portability problem, contradicting the chapter's
  "Since 3.14 no platform forks by default." It now names the 3.14
  Linux `forkserver` default and says every platform's default
  requires the guard.
- Ran `make reflow CH=19`.

## Considered and declined

- "Context switching between threads is as efficient as possible,
  but it still has overhead": reads oddly at first but is coherent
  (even at maximal efficiency, the cost remains); left alone.
- The chapter quotes the lock message as `RuntimeError: Lock is not
  acquired`; the actual message carries a trailing period. Left as
  is: the chapter already truncates the bootstrapping-phase message
  the same way.
- The intro's "The second big shift changed who decides to use
  parallelism" differs from the wording the previous review
  proposed, so it is the author's own rewording; left alone.
- `shared_iterator.py` defines a local `report()` while neighboring
  listings import `benchmark.report()`: self-contained, no import
  collision, and renaming would make the listing wordier; left.
- The 1990/1991/1992 dates in "Why Python Has a GIL" come from the
  author's own PyCon material and were not re-verified against
  outside sources.
