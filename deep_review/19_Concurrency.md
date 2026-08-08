[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Line 102-108, opening: "The second big shift" promises something Python does not do.**

The paragraph closes the chapter's introduction with:

> The second big shift was in language-level control of parallelism.
> Mapping every parallel task onto its own OS thread worked,
> but it pushed all scheduling decisions onto the OS and needed extra machinery
> (thread pools, pinning, tuning) to perform well.
> Languages and runtimes responded by taking on more of that scheduling,
> multiplexing many lightweight,
> language-managed tasks onto a smaller number of OS threads.

That last clause describes M:N green-thread scheduling: Go's goroutines,
Java's virtual threads, Erlang's processes. Python has no such thing.
`asyncio` multiplexes tasks onto *one* thread, not "a smaller number" of them,
and the chapter's two genuinely parallel in-process answers
(subinterpreters and free threading) are not lightweight tasks on a thread pool
either. A reader who takes this paragraph as a promise about the chapter
spends the rest of it waiting for a Python M:N scheduler that never arrives.

The paragraph is also the only place in the chapter that mentions "the second
big shift," so nothing later cashes it in. Proposed rewrite, keeping the
historical point but not implying Python implements it:

> The second big shift was in where parallelism gets decided.
> Mapping every parallel task onto its own OS thread worked,
> but it pushed all scheduling decisions onto the OS and needed extra machinery
> (thread pools, pinning, tuning) to perform well.
> Languages and runtimes responded by taking scheduling back:
> Go and Java multiplex lightweight tasks onto a pool of OS threads,
> while Python gives each parallel worker its own interpreter,
> in a separate process or, since 3.12, inside the current process.

The alternative is to cut the paragraph entirely. It is doing less work than
the coroutine paragraph above it, and "I/O-Bound vs CPU-Bound" restates the
same split two lines later in terms the chapter actually uses.

---

[] Reject

**Line 146-148, `asyncio.run()`: the most common beginner error is not named.**

The numbered list says `asyncio.run()` "is the entry point, called once to run
the program," which is correct but reads as advice rather than a rule. What a
reader plausibly writes instead is `asyncio.run()` inside an `async def`, to
"run" a helper coroutine from a coroutine. Verified on 3.15.0b2:

    RuntimeError: asyncio.run() cannot be called from a running event loop

with a `RuntimeWarning: coroutine 'inner' was never awaited` trailing it,
so the reader gets two messages for one mistake.

Proposed addition to item 4, one sentence:

>    Calling it from inside a coroutine raises
>    `RuntimeError: asyncio.run() cannot be called from a running event loop`;
>    inside an `async def`, `await` the coroutine directly.

Not implemented because the chapter is already the longest in the book and
each added near-miss costs a paragraph the author may not want here. If it
lands anywhere, this is the spot: it is the first place `asyncio.run()`
appears, and the mistake happens on a reader's first program.

---

[] Reject

**Line 416, end of the `gather()`/`TaskGroup` comparison: `TaskGroup.cancel()` is new in 3.15.**

The section ends with "`TaskGroup` has no such mode. Keeping siblings alive
past a failure means catching exceptions inside each task yourself." That is
still exactly true of the partial-failure case. But 3.15 added
`TaskGroup.cancel()` (gh-127214), which covers the adjacent case the chapter
does not mention: stopping a group early because the work is done, not because
something failed. Before 3.15 that required an extra task raising a private
exception that you then suppressed on the way out.

Since the book targets 3.15, a one-line note would earn its place:

> A `TaskGroup` can also be stopped deliberately.
> `tg.cancel()` (3.15) cancels every task in the group,
> which is what you want when the answer arrives before the batch finishes
> and the rest of the work is no longer worth doing.

Reported rather than implemented because it introduces a new API in a section
whose subject is failure handling, and whether that belongs here or nowhere is
the author's call.

---

[] Reject

**Line 624, "A Single Thread Still Races" → line 1866, "Locks": a 1,242-line forward reference.**

"A Single Thread Still Races" ends with:

> A read-modify-write that spans an `await` needs `asyncio.Lock`,
> just as the same race between threads needs a `threading.Lock`.
> [Locks](#locks) returns to this listing and adds one.

The reader is shown a broken program, told the fix by name, and then sent
1,242 lines downstream to see it. Nine sections intervene. "Locks, Semaphores,
and Failure Modes" then has to spend its first paragraph re-establishing what
`async_race.py` was, which is the classic tell that an answer is sitting too
far from its question.

Two ways to close the gap, in order of preference:

1. Move the "Locks" subsection (`async_locks.py`, five lines of code and one
   paragraph) up to directly follow `async_race.py`, and leave Semaphores,
   Deadlock and Livelock where they are. The later section then opens on
   semaphores with the lock already in hand, which is the order it teaches in
   anyway ("A *semaphore* generalizes a lock ..."). Cost: the sentence at
   line 1932 ("`peak` tracks the same live-count idea as `Meter` ...") and the
   opening paragraph of "Locks, Semaphores, and Failure Modes" both need
   rewording, and `#locks` becomes an anchor inside the async section, so the
   two inbound links from `Chapters/24_Singleton.md` (line 174) and this
   chapter's own line 624 must be checked. Nothing else in the book links to
   `#locks`.
2. Leave the order and say plainly that the wait is deliberate: "The fix is
   short, but it belongs with the other coordination primitives, so
   [Locks](#locks) is where this listing gets one." That costs one sentence
   and no restructuring.

Not implemented: the skill is explicit that moving a section stays a proposal.

---

[] Reject

**Line 776, Parallelism point 1, and Exercise 6: the error the reader actually sees is not `RuntimeError`.**

Point 1 says of the missing `if __name__ == "__main__"` guard:

> If you leave it out,
> Python detects the runaway spawning and raises `RuntimeError`.

Exercise 6 then tells the reader to delete the guard and "Read the error."
On this Linux/3.15.0b2 build (default start method `forkserver`), what
terminates the reader's own process is:

    concurrent.futures.process.BrokenProcessPool: A process in the process
    pool was terminated abruptly while the future was running or pending.

The `RuntimeError("An attempt has been made to start a new process before the
current process has finished its bootstrapping phase...")` is real, but it is
raised in the *worker*, and appears above that as a nested traceback through
`multiprocessing/forkserver.py` and `multiprocessing/spawn.py`. A reader
following Exercise 6 literally reads the last line of the traceback and finds
`BrokenProcessPool`, not the explanatory `RuntimeError`, and the exercise's
"explain it with the import mechanics" then has nothing to hook onto.

Proposed change to point 1's last sentence:

>    If you leave it out, each worker re-runs the block, tries to build a pool
>    of its own, and dies with
>    `RuntimeError: An attempt has been made to start a new process before the
>    current process has finished its bootstrapping phase`.
>    The parent sees the worker's death as `BrokenProcessPool`,
>    with the worker's `RuntimeError` nested in the traceback above it.

and a matching clause in Exercise 6: "Read the error (the useful part is the
nested `RuntimeError`, not the `BrokenProcessPool` at the bottom) ...".

Verified by running the guard-free listing directly; the Solutions entry for
Exercise 6 may need the same adjustment.

---

[] Reject

**Line 902-905, `task_scaling.py`: the description contradicts the sample output printed 12 lines below it.**

The paragraph before the output says:

> Wall time drops sharply as the split grows from one task to one task per core,
> then keeps dropping a little past that point as smaller,
> more numerous chunks balance the load better across workers,
> before flattening out.

The sample run immediately after shows the opposite past the core count:
32 tasks at 0.103s, 64 tasks at 0.111s. Slower, not "dropping a little." The
paragraph at line 921-925 then describes the data correctly ("then flattens or
even reverses past it, as doubling from 32 to 64 tasks did here"), so the
chapter says two different things about the same seven numbers, twelve lines
apart.

Note also that the sweep cannot resolve the shape the first paragraph claims:
with `CORE_MULTIPLIER = 2` there is exactly one sample point past the core
count, so "keeps dropping a little, then flattens out" is three phases fitted
to one measurement.

Recommended fix, rewriting the earlier paragraph to match the data and let the
later one stand:

> Wall time drops sharply as the split grows toward one task per core.
> Past that point the curve flattens,
> and can turn back upward once the cost of one more chunk to pickle
> outweighs the better load balancing.

The alternative, if the author has runs where finer splitting past the core
count really does help, is to keep the first paragraph and raise
`CORE_MULTIPLIER` so the sweep shows the intermediate points that support it.
I recommend the first: it is the smaller change and it agrees with both the
printed run and Amdahl's Law as the next subsection presents it.

---

[] Reject

**Line 1119: "Since 3.11" should be "Since 3.10".**

> Since 3.11 the interpreter only switches threads at a function call or at
> the jump that closes a loop iteration,
> so this particular sequence is no longer interrupted in practice.

The described behavior arrived in 3.10, not 3.11. Mark Shannon's
[gh-18334](https://github.com/python/cpython/pull/18334) ("Only check
evalbreaker after calls and on backwards edges", bpo-29988) merged 2021-03-24,
before the 3.10 feature freeze; its own description is "Checking `eval_breaker`
on backward edges ensures that they are always handled eventually. Checking
after every explicit call ensures that they are handled promptly in most
cases," which is the sentence's claim verbatim.

3.11 is a defensible date only if the intended referent is the `RESUME`
instruction, which is where the check physically lives from 3.11 onward. The
observable rule, though, is a 3.10 change, and the sentence is about observable
behavior. Reported rather than edited because the version may have been chosen
deliberately in the PyCon material this section condenses.

---

[] Reject

**Line 1254, `subinterpreters.py`: the 1.5x threshold is not portable to a small machine.**

`print(f"subinterpreters at least 1.5x faster: {t_seq > t_sub * 1.5}")`

On the 2-core Linux container this review ran in, the marker check produced
`False` on 5 of 5 runs, and instrumenting the same script to print the raw
ratio gave 1.51, 1.34 and 1.98 on three consecutive runs. The boolean is not
wrong on the author's machine; the point is that its margin is *the core count*.
On two cores the theoretical ceiling is 2.0x, so a 1.5x assertion is asking for
75% of the best case a two-core box can possibly deliver, and it straddles the
line.

Per `CLAUDE.md`'s standing rule for `gil_threads.py`, I did not widen or narrow
the band, and I did not touch the marker. Two ways to make it portable, both
for the author to choose:

1. Harden the measurement rather than the threshold: take `min` of three
   `timeit` runs for each side, the same treatment `CLAUDE.md` suggests for
   `thread_compare.py`'s `compare()`. This removes the scheduling noise but not
   the two-core ceiling.
2. [[do this]] Scale the claim to the machine: compare against `os.cpu_count()`, e.g.
   assert the speedup clears `min(1.5, cores * 0.7)`. This says what the
   listing actually means ("several interpreters really do run at once")
   without pretending a two-core box can show a 1.5x win reliably.

If neither is wanted, the honest option is a note in the prose that the boolean
needs at least four cores, so a reader on a small laptop is not left thinking
subinterpreters do not work.

---

[] Reject

**Line 1294-1295, `priority_queue.py`: the listing does the thing the chapter warns about 500 lines earlier.**

    with ThreadPoolExecutor(max_workers=2) as pool:
        pool.submit(enqueue, [(3, "backup"), (1, "page oncall")])
        pool.submit(enqueue, [(2, "rotate logs"), (1, "alert")])

Both `Future` objects are discarded. Parallelism's point 3 (line 787-792) says
of exactly this: "a worker's exception is re-raised in the calling process when
you consume that worker's result ... That third point is true of every
`Executor`, not only a process pool." Here nothing consumes either result, so
an exception inside `enqueue()` would vanish and the drain loop would silently
print fewer jobs.

Nothing in this listing can raise, so it is correct as written; the problem is
that it models the pattern the chapter told the reader not to use, in the
section a reader is most likely to copy from (a producer/consumer skeleton).

Smallest fix that keeps the listing dense:

    with ThreadPoolExecutor(max_workers=2) as pool:
        producers = [
            pool.submit(enqueue, [(3, "backup"), (1, "page oncall")]),
            pool.submit(enqueue, [(2, "rotate logs"), (1, "alert")]),
        ]
    for p in producers:
        p.result()  # Surface any producer failure

with one prose sentence tying it back: "Collecting the futures and calling
`result()` is what turns a producer's exception into one you can see, as
[Parallelism](#parallelism)'s third point describes."

Reported rather than applied: it adds four lines and a comment to a listing
whose subject is priority ordering, which is the "one new thing per listing"
trade the author should make, not me.

---

[] Reject

**Line 1362-1366, `asyncio.Queue`: the thread-safety warning should cover `asyncio.Lock` and `asyncio.Semaphore` too.**

The chapter is careful about `asyncio.Queue`:

> That guarantee holds only within the event loop's own thread.
> If you call it from another thread, nothing protects it,
> which is why the class is not thread-safe.

The identical caveat applies to `asyncio.Lock` and `asyncio.Semaphore`, which
the chapter introduces 500 lines later without it. That matters more than for
the queue, because the reader has just been taught `asyncio.to_thread()` and
the natural next thought is "the worker thread and the coroutine both touch
this, so I will put the `asyncio.Lock` around both." That does not work: an
`asyncio.Lock` protects tasks from each other, never a task from a thread.

Proposed one-line addition at the end of the "Locks" subsection (after line 1901):

> An `asyncio.Lock` is not thread-safe either, for the same reason
> `asyncio.Queue` is not.
> It orders tasks on one event loop; a worker thread reached through
> `asyncio.to_thread()` needs a `threading.Lock`.

Reported rather than applied because it may read as piling caveats onto a
subsection whose job is to show the fix working.

---

[] Reject

**Line 1780-1789, `task_vs_thread_memory.py`: two `#:` markers are machine-specific and will churn.**

    print(f"average bytes per task: {task_cost:.0f}")
    #: average bytes per task: 1350
    print(f"tasks fitting in one thread's stack: {tasks_per_stack:.0f}")
    #: tasks fitting in one thread's stack: 777

On this Linux/3.15.0b2 build the values are 1341 and 782, stable across 6
consecutive standalone runs. They are not flaky; they are simply a different
machine's numbers. Because `make verify` runs `validate_output.py --update`,
every cross-machine run rewrites both markers, so this listing will appear in
`git diff Chapters/` forever, and every such diff has to be read and dismissed
by hand, which is exactly the habit `CLAUDE.md` says not to build.

I left both markers alone (writing this container's numbers into the book would
just move the churn to the author's machine) and instead decoupled the prose
from them: "could instead hold roughly 777 suspended tasks" is now "could
instead hold hundreds of suspended tasks," so at least the surrounding text no
longer contradicts a marker that self-heals.

For the markers themselves, the durable fix is to print a figure that is coarse
enough to be the same everywhere while still making the point:

    print(f"bytes per task under 4 KiB: {task_cost < 4096}")
    #: bytes per task under 4 KiB: True
    print(f"tasks fitting in one thread's stack: {tasks_per_stack > 200}")
    #: tasks fitting in one thread's stack: True

That loses the concrete numbers, which is a real cost for a section titled
"Measuring the Difference." The middle option is to keep the two exact prints
but move the listing's real assertion into the existing
`holds over 200 tasks: True` line and mark the exact ones as illustrative in
the prose ("your numbers will differ; the ratio will not"). Author's call.

---

[] Reject

**Line 2136: "pierced to tatters" is a mixed metaphor.**

> The comfortable abstraction provided by normal programming is pierced to
> tatters by concurrency.

Piercing makes holes; tatters come from tearing. The two images fight, and the
passive voice puts the actor last. It is also the only sentence in a plainly
written closing section that reaches for a figure of speech.

Proposed:

> Concurrency tears through the comfortable abstraction that normal programming
> provides.

Reported rather than applied because it is the author's voice in the chapter's
closing argument, and a flourish there may be deliberate.

---

[] Reject

**Exercises: three sections have no exercise, and one of them is the chapter's newest material.**

Mapping the twelve exercises to sections:

| Exercise | Section |
| --- | --- |
| 1, 2 | `async def`, `await`, and the Event Loop |
| 3, 4 | Overlapping the Waits |
| 5 | Locks / Semaphores (the working case only) |
| 6 | Parallelism |
| 7 | The GIL Does Not Prevent Races |
| 8 | Coordinating Threads with Queues |
| 9 | Structured Concurrency with `TaskGroup` |
| 10 | `gather(return_exceptions=True)` |
| 11 | Context That Follows the Call Chain |
| 12 | Subinterpreters |

Nothing exercises:

- **Sharing an Iterator Between Threads** (three listings, three APIs that are
  new in 3.15 and that no reader has met before). This is the section a reader
  is least able to check their understanding of from prior knowledge, and it
  has the highest chance of being misremembered as "wrap the loop in a lock,"
  which the section explicitly warns against.
- **One Task, Many Backends**, including the
  `concurrent.futures.Future` / `asyncio.Future` distinction, which is the one
  lookalike pair in this chapter a reader will hit in real code within a week.
- **Deadlock and Livelock.** Exercise 5 touches `Lock`/`Semaphore` but nothing
  makes the reader reason about acquisition order.

Two proposed exercises, both answerable from the chapter alone:

> 13. In `shared_iterator.py`, replace the `threading.serialize_iterator()`
>     call with a `threading.Lock` acquired inside `report()`'s loop body,
>     as in the "tempting fix" listing in
>     [Sharing an Iterator Between Threads](#sharing-an-iterator-between-threads).
>     Predict whether `duplicates` becomes `False` before running it,
>     and explain which call the lock does and does not cover.
> 14. In `async_deadlock.py`, change the second `worker()` call to
>     `worker(lock_a, lock_b)` so both tasks acquire in the same order.
>     Predict what the program prints before running it,
>     then say which of the four deadlock conditions the change breaks.

Not implemented: `Solutions/19_Concurrency.md` needs matching entries and the
brief puts `Solutions/` out of scope for this review. If exercise 14 is
accepted, note that the program then prints nothing at all (both workers
complete inside the timeout), so the solution should say so explicitly or the
exercise should ask the reader to add a success print.

---

[] Reject

**Prose nits, four small ones, listed together because each is one word.**

- **Line 10:** "early operating systems (OS) were basically just program
  loaders." Two hedges stacked. "were little more than program loaders" says
  the same thing once.
- **Line 100:** "This shift in control of context switching greatly simplifies
  writing and reasoning about the program." Drop "greatly"; the sentence is
  stronger flat, and the claim is doing the work already.
- **Line 1311:** "`get()` blocks until an item is available, so an idle
  consumer simply waits." Drop "simply." The point is that waiting is all it
  does, which "so an idle consumer waits" already carries.
- **Line 1692:** "The remaining role for threads is in creating bridges to code
  that doesn't cooperate with an event loop." "is in creating bridges to"
  → "is bridging to", or plainer, "Threads remain for one job: reaching code
  that doesn't cooperate with an event loop."

## Cross-chapter

[] Reject

**`Chapters/39_Pattern_Catalog.md`, line 72: the Future/Promise row points at the wrong section of this chapter.**

    | [Future / Promise](19_Concurrency.md#parallelism) | Represent a result that will become available later. |

`#parallelism` is the `ProcessPoolExecutor` section; it never uses the word
`Future`. Chapter 19's actual treatment of futures is in **One Task, Many
Backends** (line 1598-1607 of the current file), which contrasts
`concurrent.futures.Future` (blocking `result()`, not awaitable) with
`asyncio.Future` (awaitable, `Task` is a subclass) and names
`loop.run_in_executor()` as the bridge. That is precisely "a result that will
become available later."

Exact change I would make in `Chapters/39_Pattern_Catalog.md`:

    | [Future / Promise](19_Concurrency.md#one-task-many-backends) | Represent a result that will become available later. |

The anchor `#one-task-many-backends` is the pandoc auto-slug of `## One Task,
Many Backends` and already resolves; `heading_links.py` passes with it.

I did not make this edit: it is outside the one chapter this review owns.

[] Reject

**`Chapters/39_Pattern_Catalog.md`, line 73: Thread-Specific Storage could link into this chapter.**

    | Thread-Specific Storage | Give each thread its own copy of a value. |

Chapter 19 covers `threading.local` directly, in **Context That Follows the
Call Chain** (line 719-725), where it explains why `ContextVar` replaced it for
async code. Every other row in that table that the book covers is linked, so
this one reads as an oversight.

Suggested change in `Chapters/39_Pattern_Catalog.md`:

    | [Thread-Specific Storage](19_Concurrency.md#context-that-follows-the-call-chain) | Give each thread its own copy of a value. |

That heading carries an explicit `{#context-that-follows-the-call-chain}` id in
chapter 19, so the anchor is stable against retitling.

Lower confidence than the row above: the section's subject is `ContextVar`, and
`threading.local` appears there only as the thing being displaced, so the link
may set the wrong expectation. Author's call.
