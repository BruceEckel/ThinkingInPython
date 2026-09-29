> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 19_Techniques--Concurrency (2026-09-29)

I checked each claim against its listing, the chapters this one links (15, 18, 22, 23, 30, 38), the chapters that link here, the pinned interpreter (3.15.0rc2), a free-threaded 3.15.0b4 already installed under uv, `ty` 0.0.84, and the 3.15 documentation.
Every quoted error message, the `counter += 1` bytecode, the unguarded process pool, the `lambda` pickling failure, and exercise 15's two errors were reproduced.
The review ran while twenty other reviews loaded the machine, so I changed no threshold, loop size, sleep margin, or timing marker.
`tip verify-ch CH=19` passes 24 of 24.
One block needs your decision.

## Applied directly

Chapter, corrections:

- "Free Threading": the indented `threads speedup: 3.8x` had lost its source. Commit 20788226 cut the sentence that said where the line comes from, as metadiscourse, and `gil_threads.py` prints no such line. Restored: "Replacing its last line with `print(f"threads speedup: {seq / thr:.1f}x")` reports the size of the gain:".
- "Free Threading": the single-threaded penalty was "roughly five to fifteen percent". The 3.15 free-threading HOWTO gives an average of about 1% (macOS aarch64) to 8% (x86-64 Linux) on `pyperformance`. The sentence now carries those figures, and the "should improve in future releases" forecast is gone.
- "Bounding a Wait": "which cancels both children" was wrong, since the 0.01-second task finished long before the 0.05-second deadline. Now the group cancels the slow task, its one child still running.
- "Bounding a Wait": "Every delay in this chapter so far is a fixed `asyncio.sleep()`" was false after `fetch_demo.py` moved to `sleep_until()`. Now "has a fixed length".
- After the comprehension warning: "The task bodies execute only after `gather()` suspends" described `gather()` as a coroutine. It is a function that returns an awaitable, and `main()` is what suspends. Rewritten.
- "Locks": "The only change from `async_race.py` is `async with lock`" omitted the module-level `lock`, and the two listings' comments differed ("Release control" against "Yield"). The sentence names both changes and the comments now match.
- "Deadlock": "whichever gets there first finishes and releases that lock before the other waits" had the order backward. The second task does wait, holding nothing, while the first finishes.
- "Parallelism": "`ProcessPoolExecutor` runs each call in its own process" contradicted "It reuses a pool of workers instead of spawning one process per call" two sections later. Now "in one of its worker processes".
- "Measuring the Memory": `threading.stack_size()` "reports" the stack size, but it returns `0` until a size is set. The sentence says so.
- "Concurrency Is Not Easy": Rob Pike is a co-creator of Go (with Griesemer and Thompson).

Chapter, teaching:

- "Deadlock": the sentence about the OS scheduler did not say why the listing needs its `sleep(0.01)`. Added the mechanism: a task switches only at an `await`, acquiring a free lock does not suspend, and without the sleep the first task takes and releases both locks before the second starts (probed: both finish, nothing prints).
- "Semaphores": the over-release hazard had no remedy. Added `asyncio.BoundedSemaphore`, which raises a `ValueError` on a `release()` beyond its starting count. The Solutions file's exercise 5 names it too.
- `utils/fetch_demo.py` followed a paragraph about `gather()` with no lead-in. Added "The next two listings run the same six fetches, which a shared module defines:".
- The four-item list before `async_mechanics.py` ended on a colon that belonged to item 4 alone. The list now ends with a period, and "This listing uses all four:" introduces the listing.

Chapter, prose:

- Bare "raise": "`c` and `d` both raise before" is "raise their exceptions before", and the comment in `task_vs_thread_memory.py` says the `CancelledError` "propagates".
- Figures of speech replaced with what happens: "never lands in a timed result", "not worth the surgery", "`gil_race.py` wearing a different hat", "takes the lock apart".
- Dropped "exactly the way" and "`time.sleep()` itself".
- `io_price`, `consumer`, and `producer` take empty parentheses where they name the function.
- "claimed" is "claims", "As this chapter has shown" is "shows", "Only `gather()` or `TaskGroup` schedule" is "schedules", and the heading "Concurrency is Not Easy" capitalizes "Is" as the book's other headings do (the anchor is unchanged).
- The `ContextVar` paragraph's "writing `handle(name)`'s value into a parameter" is "Passing the value as a parameter, with no global and no `ContextVar`".

Solutions:

- Exercise 6: "A spawned worker imports the module under its real name, `parallel_cpu`" was false. A probe prints `__mp_main__` from each worker. Corrected.
- Exercise 8 solved an older `priority_queue.py`: raw `threading.Thread` objects and a `while not tasks.empty()` drain, the polling the chapter advises against. It now edits the current listing (`enqueue()`, `consume()`, `ShutDown`) with a third `pool.submit()` and `max_workers=4`.
- Exercise 10 carried its own `fetch()` built on `asyncio.sleep()`, so its claim that `d` fails "in the same tick" as `c` depended on two timers set microseconds apart. It now imports `PAIRS` and `fetch()` from `fetch_demo`, as `gather_with_exceptions.py` does, and the shared deadline makes the claim hold.
- Exercise 7 used raw threads where `gil_race.py` uses a pool, and had no slug. It is now `exercise_7.py`, the chapter listing minus the sleep, with the marker `#: lost updates: False` (five of five runs), so the gate checks the claim. The prose says "on the standard build" and adds what a free-threaded interpreter changes.
- Exercise 12 hand-rolled `--numbers`. It now calls `report()` from `benchmark`, and the prose says `t_thr * target`, the expression in the listing.
- Exercises 1 through 5 had no annotations. They now match their chapter listings, including `PriceTask`.
- Prose: "lesson lands", "increments land", "lands in `main()`'s own context", "walks the same path through an empty field", five uses of "exactly" as an intensifier, a bare "raises", and the imperative-plus-consequence sentence in exercise 7.

Outside the chapter:

- `tools/data/timing.txt`: registered `thread_vs_task_speed.py`. Its marker is a wall-clock threshold boolean, the kind that file exists for, and it was the chapter's one unregistered case. The measured ratio is 40 to 60 against a threshold of 5.

## Move the basics ahead of structured concurrency

The chapter teaches `gather()` in "`async def`, `await`, and the Event Loop", then goes straight to "Structured Concurrency with `TaskGroup`", "Failures as Values", and "Bounding a Wait".
Those three sections introduce exception groups, `except*`, cancellation, weak references to tasks, `loop.call_at()`, and timer ordering within one loop turn.
"Overlapping the Waits" comes next and returns to the first principle: tasks overlap waiting and not computing.
It opens by restating how `await` hands control to the event loop, which a reader learned four sections earlier.
"`time.sleep()` Stops the Loop", "A Real Socket", and "Escaping to a Thread" follow at the same introductory level.

I would move "Overlapping the Waits" (with its two subsections) and "Escaping to a Thread" to sit directly after the event-loop section, ahead of "Structured Concurrency with `TaskGroup`".
The difficulty then rises in one direction: mechanics, what overlaps, what blocks, a real socket, the thread escape, and then failure, cancellation, and timeouts.
"A Single Thread Still Races" would follow "Bounding a Wait".

The move breaks nothing I can find.
The four sections use `gather()` alone, and the first listing after them that needs `TaskGroup` is `context_var.py`.
No heading changes, so the links from chapters 14, 16, 30, 38, 44, and 45 keep working.
"Every listing so far stands in for network I/O with `asyncio.sleep()`" in "A Real Socket" becomes more accurate, since `fetch_demo.py`'s `sleep_until()` would come later.
The Simulation and *Observer* paragraph that closes "Escaping to a Thread" would move with it, and it reads correctly in either place.
Exercises 3 and 4 would then sit in chapter order; 9 and 10 already trail their sections and would continue to.

The case for the current order is the opening of the `TaskGroup` section, "What happens if `gather()` encounters a failure?", which follows `gather()` closely.
I left the order alone because the arrangement of the argument is yours, and the diff would touch a third of the chapter.

`[] Reject`

## Considered and declined

- **Renumbering the exercises into chapter order.** Exercises 9, 10, and 11 cover sections that precede those of exercises 5 through 8. No prose refers to a chapter 19 exercise by number, so the renumbering is safe, but it rewrites fifteen Solutions headings for a small gain.
- **The `3.8x` free-threaded figure.** Three runs on the free-threaded 3.15.0b4 gave 4.0x, 4.3x, and 4.5x, with the boolean `False` each time. The chapter calls its number one machine's output, and my runs were made under load, so the figure stays.
- **"A common default across platforms is on the order of one mebibyte."** Windows reserves 1 MiB, glibc 8 MiB, and macOS 512 KiB for a secondary thread. "On the order of" covers the spread, and the next paragraph says the listing stipulates the figure.
- **`shared_iterator.py`'s local `report()`** shares a name with `benchmark.report()`, which eight other listings in the chapter import. Renaming it would also rename exercise 13's copy, and no reader is misled: the listing defines the function in view.
- **The forward link to the GIL** in "A Single Thread Still Races" uses the term before "Parallelism" defines it. The link is there, and moving the definition would split the GIL material.
- **`RuntimeError: Lock is not acquired`**: the real message ends with a period. The chapter omits it and the Solutions file includes it; both read correctly.
- **The GIL history dates** (1990, 1991, 1992, the 1996 patch) come from your own talk, and nothing in the repo can check them.
