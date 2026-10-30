# Performance

> Most programs are fast enough as written, and the rest are slow in one place.
> Performance work is finding that place before changing anything.

Performance means at least two things in computing:

1. Application development speed
2. Execution speed

Python addresses the first issue with clear syntax and extensive power and flexibility.
As to the second issue, Python has a reputation for slowness.

## Is It Too Slow?

Computer programming projects have a long history of *premature optimization*:
optimizing before any measurement shows where the time goes.
Often people decide ahead of time, based on biases,
that runtime performance will be insufficient.
They then build elaborate designs that solve nonexistent problems.

A program coded in the most straightforward way can often run fast enough for your needs,
with performance left out of the design.
Before assuming that a simply written program will be too slow, try it out.
It might be fine.

The opposite assumption fails just as often.
A program that is fast in the small can be slow at scale.
A run over a hundred records is a poor guide to a million,
because costs grow at different rates.
An algorithm that revisits its data looks instant at one size and takes hours at another.
Every layer of abstraction also hides work that only a realistic load reveals,
such as a copy per call or a query behind an attribute.
So "try it out" means try it at the size you expect in production,
not at the size that is convenient to type.

## Profilers

A *profiler* measures where a program spends its time,
so you know where to focus.
You may think you "have a pretty good idea where the slowdown is,"
but programmers turn out to be bad at guessing.
A profiler tells you for sure.

The standard library includes two profilers,
the classic `cProfile` and a sampling profiler new in Python 3.15.
`cProfile` is a deterministic tracing profiler that arrived in 2006 and records every function call and return.
Its numbers are exact, but the instrumentation slows the program,
sometimes enough to inflate the times of functions that make many small calls.
You run `cProfile` on a script from the command line:

    uv run python -m cProfile -s cumulative my_program.py

### Reading a `cProfile` Report

`cProfile`'s report is a table, one row per function.
This section's report profiles a small script.
The script has one obvious hot spot,
and one generator expression that `cProfile` counts as a call per element:

```python
# prof_demo.py
def helper() -> int:
    return sum(i * i for i in range(10_000))

def slow() -> None:
    total = 0
    for i in range(2_000_000):
        total += i
    helper()

if __name__ == "__main__":
    slow()
```

Running it under the profiler prints a table like this one
(the exact times vary by machine, so treat these as one sample run, not a value the book asserts):

    $ uv run python -m cProfile -s cumulative prof_demo.py
       ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            1    0.000    0.000    0.077    0.077 {built-in method builtins.exec}
            1    0.000    0.000    0.077    0.077 prof_demo.py:1(<module>)
            1    0.074    0.074    0.077    0.077 prof_demo.py:5(slow)
            1    0.000    0.000    0.003    0.003 prof_demo.py:2(helper)
            1    0.002    0.002    0.003    0.003 {built-in method builtins.sum}
        10001    0.001    0.000    0.001    0.000 prof_demo.py:3(<genexpr>)

`tottime` is the time spent inside that function alone.
`cumtime` adds the time spent in everything it called.
Sorting by `cumtime` puts `exec` and `<module>` on top,
as it does for every program.
They call everything, so they contain everything.
Scan down to the first row where `tottime` is large: here, `slow()`.
That is the function to speed up, since its own loop, not anything it calls,
takes most of the time.

`ncalls` tells you what kind of change a function needs.
`slow()` spends most of the total in a single call,
so it needs a better algorithm.
`<genexpr>`'s ten thousand calls show `helper()` spending its time on per-element overhead,
where fewer calls help more than a faster body.

### The Sampling Profiler

Python 3.15 gathers the profilers into a single `profiling` package
([PEP 799](https://peps.python.org/pep-0799/)).
The deterministic tracing profiler becomes `profiling.tracing`,
and `cProfile` remains an alias.
3.15 deprecates the old pure-Python `profile` module, and 3.17 removes it,
so use `profiling.tracing` or `cProfile` for tracing.

The sampling profiler is `profiling.sampling`.
Instead of tracing every call, it takes periodic snapshots of the call stack,
so the overhead is near zero and the program runs at full speed while you watch.
You invoke it like this:

    uv run python -m profiling.sampling run my_program.py

The new profiler can also attach to a running process, using the process ID.
Attaching makes it the tool for a slowdown that appears in the running process and disappears in a fresh run:

    uv run python -m profiling.sampling attach 12345

Either form prints a table ranked by sample count.
Its rows are source lines, where `cProfile`'s rows are functions,
so a hot loop shows up as the line inside it.
The table has `tottime` and `cumtime` columns, estimated from the samples,
and no `ncalls` column.
A sampling profiler records which line is running at each snapshot,
so the calls made between snapshots go uncounted.
When the call count is the question, use the tracing profiler.

Beyond the standard library, [Scalene](https://github.com/plasma-umass/scalene)
separates Python time from native time and profiles memory line by line.

## Measuring One Function with `sys.monitoring` {#measuring-one-function-with-sys-monitoring}

A profiler answers a broad question about the whole program.
Sometimes you have a narrow one.
How many times does this function run during a request,
and does that branch run?
A counter added to the function changes the code you study,
and a full profiler times every function to answer a question about one.

`sys.monitoring` ([PEP 669](https://peps.python.org/pep-0669/))
is the interpreter's own instrumentation mechanism,
on which profilers and debuggers now build.
You claim a tool identifier, register a callback for an event,
and specify the code to which the event applies.

The interpreter instruments only the code that has an event attached.
Everything else keeps its specialized bytecode and runs at full speed.
`sys.settrace()`, by contrast, slows every Python function its thread runs,
since its trace function runs on each call,
and the local trace function it returns runs on each line.
The listing below attaches a call counter to `fib()` alone:

```python
# monitoring_counts.py
import sys
from collections import Counter
from types import CodeType
from typing import Final

monitoring = sys.monitoring
TOOL: Final[int] = monitoring.PROFILER_ID
PY_START: Final[int] = monitoring.events.PY_START
NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS
counts: Counter[str] = Counter()

def on_start(code: CodeType, offset: int) -> None:
    counts[code.co_name] += 1

def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def square(n: int) -> int:
    return n * n

monitoring.use_tool_id(TOOL, "call counter")
monitoring.register_callback(TOOL, PY_START, on_start)
monitoring.set_local_events(TOOL, fib.__code__, PY_START)
print(fib(10), square(4))
#: 55 16
monitoring.set_local_events(TOOL, fib.__code__, NO_EVENTS)
monitoring.free_tool_id(TOOL)
print(counts)
#: Counter({'fib': 177})
```

`fib()` and `square()` stay untouched.
`on_start()` does the counting outside them,
and the interpreter calls it each time a monitored Python function begins.

`set_local_events()` is the narrow instrument.
It attaches the event to one code object,
so `square()` is absent from the count although it ran.
The event stays on that one code object,
so a helper that `fib()` invokes goes uncounted as well.
The global form is `set_events()`,
which turns the event on for every Python function in the process.
When one function is the question,
`set_events()` collects data you discard and slows the run you are measuring.

Tool identifiers are a shared resource.
`PROFILER_ID`, `DEBUGGER_ID`,
and `COVERAGE_ID` carry the names of their intended users.
Claiming one that another tool holds raises a `ValueError`,
so a second tool gets an exception instead of silently replacing the first tool's callbacks.

For an answer you need once rather than continuously,
the callback can turn its event off:

```python
# monitoring_coverage.py
import sys
from collections import Counter
from types import CodeType
from typing import Final

monitoring = sys.monitoring
TOOL: Final[int] = monitoring.COVERAGE_ID
PY_START: Final[int] = monitoring.events.PY_START
NO_EVENTS: Final[int] = monitoring.events.NO_EVENTS
calls: Counter[str] = Counter()

def on_start(code: CodeType, offset: int) -> object:
    calls[code.co_name] += 1
    return monitoring.DISABLE

def used(n: int) -> int:
    return n + 1

def unused(n: int) -> int:
    return n - 1

monitoring.use_tool_id(TOOL, "coverage")
monitoring.register_callback(TOOL, PY_START, on_start)
monitoring.set_events(TOOL, PY_START)
results = [used(n) for n in range(1000)]
monitoring.set_events(TOOL, NO_EVENTS)
monitoring.free_tool_id(TOOL)
print(len(results), calls["used"], calls["unused"])
#: 1000 1 0
```

Returning `monitoring.DISABLE` tells the interpreter to stop reporting this event at this location until someone calls `restart_events()`.
`used()` ran a thousand times.
The callback ran for it once.

`DISABLE` keeps coverage measurement fast.
The question is "was this reached,"
so the first report from a location answers it,
and after the first hit the monitored code runs at full speed again.

A profiler gives you a ranked table with no code to write.
`sys.monitoring` gives you the counts you request, about the code you choose.
It is the better tool when you already know which function to measure and the profiler's overhead changes the answer.

## Benchmark Alternatives with `timeit`

A profiler tells you where the time goes.
Once you discover a hot spot, `timeit` tells you which rewrite runs faster.
It runs a small snippet many times and reports the total,
so one-time setup and the clock's granularity become a small share of the measurement.

Timings differ from machine to machine,
so the following example prints a comparison instead of raw numbers.
The numbers are one flag away.
Run any measured listing in this book with [`--numbers`](#numbers-on-your-machine)
to see what your machine does.

A `list` tests membership by scanning.
`target in as_list` walks the list from the start,
comparing each element until it finds a match or reaches the end.
A `set` tests membership through hashing.
`target in as_set` computes a hash of `target` and checks the bucket that hash selects.
Scanning gets slower as the list grows.
Hashing stays fast however many elements the set holds:

```python
# membership.py
import timeit
from benchmark import report

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n - 1  # Worst case: the last element in the list

t_list = timeit.timeit(
    lambda: target in as_list, number=100
)
t_set = timeit.timeit(lambda: target in as_set, number=100)
report(list_scan=t_list, set_lookup=t_set,
       ratio=t_list / t_set)
print(f"set at least 100x faster: {t_set * 100 < t_list}")
#: set at least 100x faster: True
```

`timeit.timeit()` calls its first argument repeatedly and returns the total elapsed time in seconds for every call combined,
not the time for one call.
`number` sets how many times `timeit` calls the lambda, 100 in this case.
`number` defaults to a million calls.
A million suits a microsecond snippet and is a long wait for anything slower,
so always set `number` for a function you are timing for the first time.

`membership.py` passes `timeit.timeit()` a `lambda` rather than a string of code,
since a `lambda` can close over `target`, `as_list`, and `as_set`,
while a string needs a `setup` argument or `globals` to reach them.
Each timing includes the cost of calling the lambda.
A set lookup takes nanoseconds, so that call is a sizable share of `t_set`,
and the ratio understates how much faster the set is.
When a snippet is that small and the ratio matters,
pass `timeit` a string of code with `globals=globals()`.
`timeit` compiles the string into the body of its timing loop,
so each pass runs the snippet inline.

One machine measured the `set` at about 14,000 times faster than the list scan.
A single lookup takes little time either way.
A million lookups is the difference between instant and minutes.

### Trusting a Measurement

A single measurement includes whatever else the machine is doing.
`timeit.repeat(f, number=100, repeat=5)` returns a list of five such totals.
The smallest of them is the run with the least interference.
Report `min(...)`, not the mean.
A slow run means another process held the CPU for part of the run,
so averaging adds that interruption to your answer.
The fastest run is the closest you get to measuring your code alone.

The timer most readers write first is a hand-rolled one:
`start = time.time()` before one call and a subtraction after it.
`time.time()` reads the wall clock,
which can jump when the system corrects its time.
One call is also one sample, with all of its interference.
`timeit` times with `time.perf_counter()`,
a high-resolution clock that moves forward steadily.
When you write your own timing code, use that clock and repeat the run.

`timeit` also has a command-line form for one-off questions:

    uv run python -m timeit -s "s = set(range(100_000))" "99_999 in s"

The command-line form chooses `number`, trying 1, 2, 5, 10, 20, 50,
and so on until one batch takes at least 0.2 seconds.
Since 3.15, `--target-time` (`-t`) sets that threshold,
so `-t 1` picks a `number` large enough for each batch to run about a second.

`timeit` also turns the garbage collector off while it measures,
so its runs stay repeatable.
For a benchmark that allocates heavily,
the measurement then leaves out the collection pauses a production run includes.
Pass `setup="gc.enable()"` when collection pauses are part of what you compare.

Benchmark with data shaped like production data.
A `list` of ten elements can beat a `set`.
An optimization tuned to toy input can behave badly in production.

### Numbers on Your Machine {#numbers-on-your-machine}

Nearly every measured listing in this book prints a threshold rather than a measurement,
so the book's output is the same on your machine as on mine.
Each listing still takes its measurements, and one flag prints them:

```python
# utils/benchmark.py
import sys
import tracemalloc
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Final

NUMBERS: Final[bool] = "--numbers" in sys.argv

def report(**measured: float) -> None:
    # Print each measurement, but only under --numbers:
    if not (NUMBERS and measured):
        return
    width = max(len(name) for name in measured)
    for name, value in measured.items():
        if isinstance(value, int):
            shown = f"{value:,}"  # Byte counts stay whole
        else:
            shown = f"{value:,.6f}"
        print(f"  {name:<{width}} {shown}")

@dataclass
class Traced:
    current: int = 0
    peak: int = 0

@contextmanager
def traced() -> Generator[Traced]:
    measured = Traced()
    tracemalloc.start()
    try:
        yield measured
    finally:
        current, peak = tracemalloc.get_traced_memory()
        measured.current, measured.peak = current, peak
        tracemalloc.stop()
```

`report()` prints when the flag is present and stays silent otherwise,
so the listing's own output, the line the book shows, stays the same.
Running `membership.py` with the flag, as `tip membership --numbers`,
adds the measurements above that line:

      list_scan  0.041807
      set_lookup 0.000003
      ratio      13,935.560574
    set at least 100x faster: True

The names are the keyword arguments at the call site,
so each listing labels its measurements.
Your ratio differs from the one above.

`traced()` measures memory instead of time.
It wraps the `tracemalloc` calls that `lazy_pipeline.py` makes in [Lazy Evaluation with Generators](#lazy-evaluation-with-generators):
`start()` before the `with` block,
then `get_traced_memory()` and `stop()` after it.
The `Traced` object it yields fills in when the block ends.
`current` holds the bytes still allocated at that point,
and `peak` holds the most the block allocated at once.
`tee.py` in [Iterators](22_Patterns--Iterators.md#what-tee-buffers)
measures each of its three cases with `traced()`.

## Try a Faster Platform

If your program is too slow, try the simplest remedy first.
That might be enough, and if it is, you save time and money.

The simplest platform change is a newer CPython.
3.11 alone measured 1.25x faster than 3.10 across the `pyperformance` suite,
with gains from 10% to 60% depending on the workload.
Later releases have continued that work.

Two more speedups work on the code you have: the tail-calling interpreter,
and the experimental just-in-time compiler inside CPython.

Alternative interpreters for Python exist, notably PyPy,
whose site reports it about four times faster than CPython 3.11 on average.
PyPy trails CPython's newest language version
(it supports Python 3.12 while CPython is at 3.15),
so confirm it supports the features and third-party packages you need.

For a parallel, CPU-bound workload,
the [free-threaded build](19_Techniques--Concurrency.md#free-threading)
is the largest platform-level speedup available in 3.15,
since it removes the lock that otherwise serializes Python bytecode across threads.

Since 3.14, the free-threaded build runs the specializing adaptive interpreter
([PEP 659](https://peps.python.org/pep-0659/)),
which the 3.13 free-threaded build had switched off.
That change cut the build's single-threaded penalty to roughly 5-10% in 3.14,
so a single-threaded timing still depends on which build took it.

How much does a hardware upgrade cost compared to paying programmers to solve the performance problem?
If it's noticeably less,
buying new hardware might solve the problem sooner and for less money.

## The Tail-Calling Interpreter

The tail-calling interpreter is a build-time choice that holds for every run of that build.
A standard build dispatches every bytecode instruction through one large C `switch`.
Since 3.14, a CPython build can make each instruction a small C function that ends by calling the function for the next instruction.
The C compiler turns each of those calls into a jump,
so the loop that runs Python bytecode gets faster.
The tail call is in C, inside the interpreter.
It is a separate mechanism from [tail-call optimization of Python functions](41_Functional--Toolkits.md#recursion),
which CPython does not do.

The tail-calling interpreter runs your program as written,
so your program behaves the same under either dispatch.
No `sys` function reports it, and the documentation calls it an internal detail.
The python.org Windows 64-bit binaries for 3.15 use it,
as do the python-build-standalone 3.15 builds that `uv` installs,
including the interpreter that runs this book's listings.
A source build needs `--with-tail-call-interp` and a compiler with the `preserve_none` calling convention:
Clang 19 or newer, or Visual Studio 2026.

The speedup is a percentage, not a multiple.
On Windows x86-64, 3.15 measures 15-20% faster on the `pyperformance` geometric mean than the same source built with the `switch`,
with individual programs from 14% to 40%.
The 3.14 figure, with Clang 19,
is 3-5%.^[The 3.14 announcement said 10-15%. Nelson Elhage's [March 2025 analysis](https://blog.nelhage.com/post/cpython-tail-call/)
traced most of that to the baseline.
LLVM 19 had capped its tail-duplication pass,
which collapsed the old interpreter's 332 dispatch jumps into 3,
so the comparison was against a compiler regression rather than a fast interpreter.
With LLVM fixed, the gain was 1-5%, and the What's New now says 3-5%.
The advice under [Numbers on Your Machine](#numbers-on-your-machine)
applies to CPython's own developers as well as to you.]

The JIT in the next section adds its speedup to the tail-calling interpreter's speedup.
The JIT compiles the hot paths,
and the tail-calling interpreter runs everything else faster.
The macOS figure in that section uses a tail-calling build as its baseline.

## The CPython JIT

CPython includes an experimental just-in-time compiler.
[PEP 744](https://peps.python.org/pep-0744/) added it in 3.13,
and 3.15 rebuilt much of it.
The JIT counts how often each path through a program's bytecode runs,
and once a path runs often enough, it compiles that path to machine code.
Your code stays as you wrote it.
The same file runs, and the interpreter runs its busiest paths as machine code.

Your program runs that machine code only when three conditions hold:

1. The interpreter must include the JIT,
   compiled in through the `--enable-experimental-jit` configuration option.
   Building it needs LLVM.
   Running the result does not.
2. The process must enable it, through the `PYTHON_JIT` environment variable.
3. The code must get hot.
   A script that runs briefly exits before it reaches the threshold,
   so the JIT compiles none of its code.

Since 3.14, the official python.org Windows and macOS binaries use `--enable-experimental-jit=yes-off`.
That option compiles the JIT in and leaves it switched off,
so `PYTHON_JIT=1` turns it on.
Plain `yes` builds start with the JIT running,
and there `PYTHON_JIT=0` turns it off.
Other distributions decide for themselves,
so the first question is not "is the JIT on?" but "which build am I running?"
`sys._jit` answers it:

```python
# jit_status.py
import sys

def jit_state() -> str:
    if not sys._jit.is_available():
        return "no JIT in this build"
    if not sys._jit.is_enabled():
        return "JIT built in, switched off"
    return "JIT enabled"

assert sys._jit.is_available() or not sys._jit.is_enabled()
print(jit_state())
```

`is_enabled()` implies `is_available()`,
so testing `is_available()` first and `is_enabled()` second distinguishes a build's three possible states.
The `assert` checks that implication, which holds on every build.

Most listings in this book print the same line on every machine.
This listing's output changes with your interpreter,
so its output appears below the listing instead of in a `#:` line.
The book's build has no JIT compiled in,
so `tip jit_status` reports the first state:

    no JIT in this build

A python.org binary prints `JIT built in, switched off` until you set `PYTHON_JIT=1`.

A third function, `sys._jit.is_active()`,
reports whether the stack frame that called it is running compiled code.
The documentation warns against branching on its result,
since a tracing compiler can give different answers to the same call.

The speedup is again a percentage,
and a smaller one than the tail-calling interpreter's 15-20% on Windows.
On the `pyperformance` suite,
3.15 measures 7-8% faster on x86-64 Linux against the standard optimized build,
and 11-12% faster on AArch64 macOS against the tail-calling interpreter.
Those geometric means, from the 3.15 What's New, cover dozens of benchmarks.
That report sets aside one microbenchmark, `unpack_sequence`.
The rest range from roughly 15% slower to more than twice as fast,
so the mean predicts your program poorly.
To measure your own program,
time the workload with `PYTHON_JIT` set to `1` and to `0`,
and hold everything else the same.

Numba's [`@njit`](#jit-compilation-with-numba) is also a just-in-time compiler.
The two compilers take opposite approaches.
The CPython JIT works on your code as written,
applies to whatever code turns out to be hot, and speeds it up by percentages.
`@njit` applies only to numeric functions, requires a decorator,
pauses to compile on the first call, and speeds code up by multiples.
Neither one changes a quadratic algorithm's growth rate.

[PEP 836](https://peps.python.org/pep-0836/)
sets the speedups the JIT must reach: 5% over the interpreter alone for 3.16,
then 20% for the JIT combined with [free threading](19_Techniques--Concurrency.md#free-threading)
by 3.17.
The PEP calls that the minimum for continuing to develop the JIT inside CPython.
Meeting it does not turn the JIT on by default.
That step needs separate approval from the release manager.

## Write Idiomatic Python

The interpreter is a C program.
A built-in like `sum()` runs its loop in C, so the more of your loop runs in C,
the less bytecode runs per element.
The idiomatic version of a loop is usually also the fast one:

```python
# builtin_sum.py
import timeit
from benchmark import report

numbers = list(range(100_000))

def hand_written() -> int:
    total = 0
    for n in numbers:
        total += n
    return total

assert hand_written() == sum(numbers)
t_loop = timeit.timeit(hand_written, number=50)
t_sum = timeit.timeit(lambda: sum(numbers), number=50)
report(hand_written=t_loop, builtin_sum=t_sum)
print(f"sum() at least twice as fast: {t_sum * 2 < t_loop}")
#: sum() at least twice as fast: True
```

One machine measured `sum()` at about five times faster than the hand-written loop.

Other examples:

- For string concatenation, `"".join(parts)` is faster than `+=` in a loop
  (one linear pass instead of repeated reallocation).
- A comprehension is faster than an `append()` loop,
  though the margin is now small
  (one bytecode appends the element, instead of an attribute lookup and a call).
  Write it for the readability.
  The speed is a rounding error.
- The C-implemented standard library's [`itertools`](22_Patterns--Iterators.md#reusable-algorithms),
  `collections`, and `functools` are faster than hand-rolled equivalents.

As a last resort in a proven hot loop,
hoist a repeated attribute or global lookup into a local,
as in `append = out.append`.
That is a micro-optimization, so let a measurement justify it:

```python
# hoist_attribute_lookup.py
import timeit
from benchmark import report

n = 100_000

def with_attribute_lookup() -> list[int]:
    out: list[int] = []
    for i in range(n):
        out.append(i)
    return out

def with_hoisted_local() -> list[int]:
    out: list[int] = []
    append = out.append
    for i in range(n):
        append(i)
    return out

assert with_attribute_lookup() == with_hoisted_local()
t_attr = min(timeit.repeat(
    with_attribute_lookup, number=100, repeat=5
))
t_local = min(timeit.repeat(
    with_hoisted_local, number=100, repeat=5
))
report(attribute_lookup=t_attr, hoisted_local=t_local)
print(f"hoisting did not halve the time: "
      f"{t_local * 2 > t_attr}")
#: hoisting did not halve the time: True
```

Here the hoist at best ties the attribute lookup, and it can slow the loop.
`out.append(i)` compiles to a method load that pushes the function and its `self` separately,
so the call passes `self` straight to the function.
`append = out.append` builds a bound method,
and every call then goes through it.
One machine measured the hoisted version five percent slower, another twenty.
Measure it on your own machine before believing either direction.

The threshold is deliberately loose.
Timing noise on a busy machine easily reaches ten or twenty percent,
so a claim about a small difference is a claim about the noise.
A hoist worth writing speeds the loop up by more than that margin.
The measurement catches a "classic" optimization that no longer works,
just as readily as it catches one that does.

## Choose Better Algorithms and Data Structures

The biggest speedups usually come from a better algorithm.
Choosing an algorithm with lower Big-O complexity beats micro-optimizing a slow one.
Often the better algorithm is a better container.
Use a `set` or `dict` for membership and lookup instead of scanning a `list`.
Use a [`deque`](03_Foundations--Containers.md#deque)
when you add and remove at both ends.

The [immutable containers](03_Foundations--Containers.md#immutability)
are not a speed upgrade.
A `frozenset` looks up just as fast as a `set`,
a `frozendict` behaves like a `dict`, and a `tuple` scans like a `list`.
In CPython each one uses its mutable partner's lookup,
a hash table for the two frozen containers and an element-by-element scan for `tuple`.
Choose immutability for correctness and safe sharing.
Immutable values are hashable,
so they can serve as dictionary keys and as arguments to the caches below.

### Bisect

For data kept in sorted order,
the `bisect` module finds the insertion point using binary search:

```python
# bisect_search.py
import bisect
from typing import Final

scores = [60, 70, 75, 90]  # Must stay sorted
i = bisect.bisect(scores, 78)  # Where 78 goes
print(i)
#: 3
bisect.insort(scores, 78)  # Insert and keep it sorted
print(scores)
#: [60, 70, 75, 78, 90]

CUTOFFS: Final[list[int]] = [60, 70, 80, 90]
LETTERS: Final[str] = "FDCBA"

def grade(score: int) -> str:
    return LETTERS[bisect.bisect(CUTOFFS, score)]

print([grade(s) for s in (55, 65, 85, 95)])
#: ['F', 'D', 'B', 'A']
```

`bisect()` is an alias for `bisect_right()`,
and `insort()` is likewise an alias for `insort_right()`.
`bisect_left()` and `bisect_right()` both answer "where does this go."
Their answers differ when the list holds the target.
`bisect_left()` returns the position before any elements equal to the target,
which is the target's index.
`bisect_right()` returns the position after them.
A membership test must therefore use `bisect_left()`,
as `search_comparison.py` does below.

`grade()` uses `bisect()` for a range lookup.
The insertion point of a score in `CUTOFFS` counts the cutoffs that score reaches,
and that count indexes `LETTERS`.
A score of 80 falls after the 80 cutoff, so it gets a B.

Because `scores` stays sorted, `bisect` locates a position in O(log n)
instead of the O(n) scan a `list` needs.
The speed is in the search alone.
`insort()` still shifts everything after the insertion point.
Under heavy insert traffic, when the smallest item is all you read,
consider a [heap](#heap) instead.

### Scan, Bisect, or Hash

You now have three ways to answer the same membership question: scan a `list`,
binary-search a sorted `list` with `bisect`,
or hash the value and check its bucket in a `set`.

```python
# search_comparison.py
import bisect
import timeit
from benchmark import report

n = 100_000
as_list = list(range(n))
as_set = set(as_list)
target = n // 2

def scan() -> bool:
    return target in as_list

def binary_search() -> bool:
    i = bisect.bisect_left(as_list, target)
    return i < len(as_list) and as_list[i] == target

def hashed() -> bool:
    return target in as_set

assert {scan(), binary_search(), hashed()} == {True}
t_scan = timeit.timeit(scan, number=1000)
t_search = timeit.timeit(binary_search, number=1000)
t_hashed = timeit.timeit(hashed, number=1000)
report(scan=t_scan, binary_search=t_search, hashed=t_hashed)
print(f"binary search at least 100x faster than scan: "
      f"{t_search * 100 < t_scan}")
#: binary search at least 100x faster than scan: True
print(f"hashing at least 3x faster than binary search: "
      f"{t_hashed * 3 < t_search}")
#: hashing at least 3x faster than binary search: True
```

The scan is by far the slowest,
since it walks roughly half the `list` before reaching `target`.
`bisect` narrows that to a handful of comparisons,
one per halving of the remaining range.
Here that means about 17 comparisons against about 50,000, so the move from O(n)
to O(log n) shows up as orders of magnitude rather than a modest improvement.
Hashing is faster than `bisect` too,
since it needs one hash and one equality check however large `as_set` grows.
One machine measured `bisect` at about 2,000 times faster than the scan,
and hashing at about five times faster than `bisect`.

### Heap

When you repeatedly need the smallest or largest item,
a *heap* keeps that item at the front, where reading it is O(1)
and removing it is O(log n).
The `heapq` module treats a `list` as a binary heap:

```python
# heap_queue.py
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)  # Rearrange into a min-heap in place
print(nums)  # The smallest stays at the front
#: [1, 2, 8, 3, 5]
heapq.heappush(nums, 7)
print(nums)
#: [1, 2, 7, 3, 5, 8]
print(heapq.heappop(nums))  # Remove and return the smallest
#: 1
print(nums)
#: [2, 3, 7, 8, 5]
values = [5, 1, 8, 3, 2]
print(heapq.nsmallest(3, values))
#: [1, 2, 3]
print(heapq.nlargest(2, values))
#: [8, 5]
print(values)  # Neither call reorders its argument
#: [5, 1, 8, 3, 2]
```

Through Python 3.13, `heapq` built only min-heaps.
Getting a max-heap meant negating every value going in and out.
Python 3.14 added `_max` variants that keep the largest item at index 0:
`heapify_max()`, `heappush_max()`, `heappop_max()`, and others.
A max-heap now stores its values as they are:

```python
# max_heap_queue.py
import heapq

max_nums = [5, 1, 8, 3, 2]
# Rearrange into a max-heap in place
heapq.heapify_max(max_nums)
print(max_nums)  # The largest stays at the front
#: [8, 3, 5, 1, 2]
heapq.heappush_max(max_nums, 9)
print(max_nums)
#: [9, 3, 8, 1, 2, 5]
# Remove and return the largest
print(heapq.heappop_max(max_nums))
#: 9
print(max_nums)  # Heap ordering is maintained
#: [8, 3, 5, 1, 2]
```

The output shows the list in the order the [heap-management algorithm](https://docs.python.org/3.15/library/heapq.html#priority-queue-implementation-notes)
keeps it, which is not sorted order.

Use the heap version of every operation.
The list's own `pop(0)` returns the smallest value the first time,
but it also shifts every remaining element down one index.
That shift breaks the heap ordering,
so `heap[0]` holds 6 while 4 is still in the list:

```python
# heap_corruption.py
from heapq import heapify

heap = [10, 9, 8, 7, 6, 5, 4, 3]
heapify(heap)  # In-place
print(heap)
#: [3, 6, 4, 7, 10, 5, 8, 9]
print(heap.pop(0))  # Smallest
#: 3
print(heap)  # 'heap[0]' no longer smallest
#: [6, 4, 7, 10, 5, 8, 9]
print(heap[0], min(heap))
#: 6 4
```

For a priority queue shared across threads,
[`queue.PriorityQueue`](19_Techniques--Concurrency.md#coordinating-threads-with-queues)
wraps the same heap in a lock.

### Heap Versus Sort

A heap answers a different question than a hash-based container.
A `set` tells you whether a value is present in O(1),
but it arranges its items by hash,
so finding the smallest values still means scanning or sorting every item.
A heap keeps the smallest item at index 0 as you push and pop,
so removing it takes O(log n) each time, however many times you repeat it.
For "give me the 100 smallest," the heap's competitor is `sorted(data)[:100]`,
not a scan, so the listing times the heap against `sorted()`:

```python
# heap_vs_sort.py
import heapq
import random
import timeit
from benchmark import report

n = 10_000
data = list(range(n))
random.seed(0)
random.shuffle(data)  # Neither side gets a free ride

def heap_min_extractions() -> list[int]:
    heap = data.copy()
    heapq.heapify(heap)
    return [heapq.heappop(heap) for _ in range(100)]

def sorted_min_extractions() -> list[int]:
    return sorted(data)[:100]

assert heap_min_extractions() == sorted_min_extractions()
t_heap = min(timeit.repeat(
    heap_min_extractions, number=50, repeat=5
))
t_sorted = min(timeit.repeat(
    sorted_min_extractions, number=50, repeat=5
))
report(heap=t_heap, sorted_slice=t_sorted)
print(f"heap beats sorted() by 1.5x+ on shuffled "
      f"data: {t_heap * 1.5 < t_sorted}")
#: heap beats sorted() by 1.5x+ on shuffled data: True
```

`sorted(data)` orders every element up front, costing O(n log n)
however few items you then take.
`heapify()` takes O(n) once, then each `heappop()` takes O(log n),
so the same 100 extractions cost roughly O(n + 100 log n).
That total stays below sorting's O(n log n)
whenever you extract a small fraction of the data.
One machine measured the heap at about 3 times faster here.

The comparison holds only when the input order gives neither side an advantage.
On descending data, the kind `heap_corruption.py` uses,
Timsort detects the existing run, so `sorted()` is the faster of the two.
Which one wins depends on the data,
so measure with data shaped like production data.

`heapq.nsmallest(100, data)` answers this top-N question in one call.
`heap_queue.py` introduced `nsmallest()`,
and `nsmallest()` is the tool to use before hand-rolling either version here.
The heap fits a different shape of problem:
pushes and pops interleaved over time, on data that arrives a piece at a time.
Re-sorting after every insertion costs far more than one incremental `heappush()`/`heappop()` pair.

## Lazy Evaluation with Generators

A list-building pipeline materializes every intermediate result.
A [generator pipeline](16_Techniques--Comprehensions.md#generator-expressions)
computes one item at a time, on demand.
Its memory use stays flat as the source grows,
and its work ends where the consumer stops.
`tracemalloc` measures the difference:

```python
# lazy_pipeline.py
import tracemalloc
from itertools import islice
from benchmark import report

n = 1_000_000

def eager_first_evens() -> list[int]:
    squares = [x * x for x in range(n)]
    evens = [s for s in squares if s % 2 == 0]
    return evens[:5]

def lazy_first_evens() -> list[int]:
    squares = (x * x for x in range(n))
    evens = (s for s in squares if s % 2 == 0)
    return list(islice(evens, 5))

tracemalloc.start()
eager = eager_first_evens()
_, eager_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
lazy = lazy_first_evens()
_, lazy_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(eager, eager == lazy)
#: [0, 4, 16, 36, 64] True
report(eager_peak_bytes=eager_peak,
       lazy_peak_bytes=lazy_peak)
print(f"lazy peak under 1% of eager: "
      f"{lazy_peak * 100 < eager_peak}")
#: lazy peak under 1% of eager: True
```

`get_traced_memory()` returns two byte counts,
the current allocation and the peak since `start()`,
and the listing keeps the peak.
Each function runs inside its own `start()`/`stop()` pair,
so the lazy peak measures the lazy pipeline alone.

The eager version builds a million-element list and a half-million-element list to get them.
The lazy one computes nine squares,
enough for `islice()` to collect the first five evens.
`islice()` replaces the eager version's `evens[:5]`.
A generator has no `__getitem__()`,
so slicing one raises `TypeError: 'generator' object is not subscriptable`.

When the consumer needs every element and the data fits in memory,
a list is fine, and you can iterate over it twice.
One pass exhausts a generator.

Fitting the whole data set in memory gives you more than a second pass.
Random access, sorting,
and the `bisect` searches in `bisect_search.py` all need an indexable structure,
not a stream of values that arrive once and disappear.
NumPy's [vectorized arithmetic](#vectorize-with-numpy) needs the same thing:
a whole array in memory.

The risk is at the limit of that memory.
Performance holds steady as the data approaches available RAM,
then drops sharply once the data exceeds it.
A data set that fits runs at full speed.
A data set that outgrows memory forces the operating system to swap pages to disk,
turning microseconds into milliseconds, a thousandfold slowdown.
Past that point the process fails outright, with `MemoryError` or an OS kill.

That sudden drop is the argument for laziness.
If a data set can outgrow memory, stream it from the start,
like `lazy_first_evens()`.

## Caching

If you call a [pure function](40_Functional--Foundations.md#pure-functions)
repeatedly with the same arguments,
the fastest way to get the answer is to reuse the result of an earlier call.
`functools.cache` stores each result the first time and returns the stored result after that.
The classic demonstration is the naive recursive Fibonacci,
which recomputes the same subproblems exponentially many times:

```python
# cache_speedup.py
from functools import cache

calls = 0

def fib_plain(n: int) -> int:
    global calls
    calls += 1
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)

@cache
def fib_cached(n: int) -> int:
    if n < 2:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

print(fib_plain(25), calls)
#: 75025 242785
print(fib_cached(25), fib_cached.cache_info().misses)
#: 75025 26
```

`cache_info().misses` counts the calls that ran the body to compute a new result,
one for each `n` from 0 through 25.
Each step up in `n` multiplies `fib_plain()`'s count by about 1.6 and adds one to the cached count,
so the gap widens as `n` grows.

`cache` holds every result forever,
but `functools.lru_cache(maxsize=n)` bounds the memory by discarding the least recently used entry.
The arguments must be hashable,
which is another reason to prefer immutable containers.

Caching is correct only when the function is pure.
Caching a function with side effects returns the stored answer but skips the effects.
Caching a function that reads outside state can return a stale answer.

A method is the usual trap.
`@cache` keys on every argument including `self`,
so the cache holds a reference to each instance it has seen and keeps every one of them alive.
For a value computed once per object,
use [`functools.cached_property`](07_Foundations--Classes.md#cached-property),
which stores the result on the instance,
so the collector reclaims the result along with the instance.
A class whose `__slots__` leaves out `__dict__` [cannot use `cached_property`](#when-slots-does-not-fit).

## Reduce Memory Overhead

With millions of objects, per-object overhead can dominate performance.
A smaller instance means fewer bytes for the allocator and garbage collector to manage,
more instances fitting in the CPU cache at once, and,
for `__slots__` specifically,
attribute access through a known offset instead of a `__dict__` lookup.
Slots and `array` reduce per-object overhead, `memoryview` avoids copies,
and the byte counts below show what each tool saves.
Over a million instances,
a saving of a few hundred bytes each is a few hundred megabytes.

### Slots

By default each instance stores its attributes in a `__dict__`.
Declaring `__slots__` replaces that dict with a closed set of fields,
which shrinks each instance:

```python
# slots.py
from exceptions import expected

class Point:
    __slots__ = ("x", "y")  # No per-instance __dict__
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)
#: 1 2
with expected(AttributeError):
    # z is not one of the declared slots:
    p.z = 3  # type: ignore
#: [AttributeError] 'Point' object has no attribute 'z' and
#: no __dict__ for setting new attributes
```

The failed assignment prints through `expected()`,
which wraps the long slotted message onto a second line.

A data class can generate the slots.
`@dataclass(slots=True)` turns the field declarations into `__slots__` and still writes `__init__()`,
`__repr__()`, and `__eq__()`:

```python
# slots_dataclass.py
from dataclasses import dataclass

@dataclass(slots=True)
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
print(Point.__slots__)
#: ('x', 'y')
```

If a class can be a data class,
prefer `slots=True` over a hand-written class with `__slots__`.
`@dataclass(slots=True)` both shrinks the instances and writes the methods.
The slotted class's instances then accept only the declared attributes.

`frozen=True` and `slots=True` are independent.
Frozen blocks every attribute assignment, new fields included,
so a frozen instance cannot gain attributes,
the same restriction `slots` gives you.
But frozen enforces that restriction by overriding `__setattr__()`.
The instance keeps its `__dict__` underneath.
`slots=True` removes that `__dict__`,
so pairing it with `frozen=True` gives you the same immutability in a fraction of the space.
That makes the pair the natural default:

```python
# frozen_vs_slotted.py
import sys
from dataclasses import dataclass
from benchmark import report
from exceptions import expected

@dataclass(frozen=True)
class FrozenPoint:
    x: int
    y: int

@dataclass(frozen=True, slots=True)
class FrozenSlottedPoint:
    x: int
    y: int

fp = FrozenPoint(1, 2)
with expected(AttributeError):
    # Frozen prevents new attributes, not just reassignment:
    fp.z = 3  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'z'

frozen_bytes = (sys.getsizeof(fp)
                + sys.getsizeof(fp.__dict__))
slotted_bytes = sys.getsizeof(FrozenSlottedPoint(1, 2))
report(frozen_bytes=frozen_bytes,
       slotted_bytes=slotted_bytes)
print(f"slots at least 5x smaller: "
      f"{slotted_bytes * 5 < frozen_bytes}")
#: slots at least 5x smaller: True
```

`expected(AttributeError)` catches the frozen error because `FrozenInstanceError` subclasses `AttributeError`.
`sys.getsizeof()` reports an object's own size, not what it references,
so `frozen_bytes` adds the dict's size on top.
One machine measured 344 bytes against 48, roughly seven to one.
The exact byte counts vary by platform and Python build,
so the listing prints a comparison that holds anywhere rather than numbers that hold here.

### A Decorator for the Default {#record}

`@dataclass(frozen=True, slots=True)` is a long line to repeat on every value class.
`slots=True` is the half you drop, because the class works either way.
A decorator of your own can apply both.
[`@dataclass_transform`](17_Techniques--Metaprogramming.md#dataclass-transform)
tells the type checker that the result is a frozen data class:

```python
# utils/record.py
from collections.abc import Callable
from dataclasses import dataclass
from typing import dataclass_transform, overload

@overload
def record[T](cls: type[T], /) -> type[T]: ...
@overload
def record[T](
    *, slots: bool = True
) -> Callable[[type[T]], type[T]]: ...
@dataclass_transform(frozen_default=True)
def record[T](
    cls: type[T] | None = None, /, *, slots: bool = True
) -> type[T] | Callable[[type[T]], type[T]]:
    def apply(c: type[T]) -> type[T]:
        return dataclass(frozen=True, slots=slots)(c)
    return apply if cls is None else apply(cls)
```

The name follows Java and C#,
where a *record* is an immutable class defined by its fields.
Written bare, `@record` is `model()` from `kept_transform.py` with `slots=True` added.
The called form, `@record(slots=False)`,
is for the class that must keep a `__dict__`.
Dropping the slots then takes a visible flag.
Under `@dataclass`, leaving out `slots=True` drops them.

The two forms follow [Decorators With Optional Parentheses](14_Techniques--Decorators.md#decorators-with-optional-parentheses).
`cls` is `None` when you call the decorator with arguments.
The two `@overload` declarations tell the checker which form it reads.
The test is `cls is None` rather than `callable(cls)`,
since a class is callable.

A class decorated with `@record` behaves like any frozen data class,
and its instances carry no `__dict__`:

```python
# point_record.py
from exceptions import expected
from record import record

@record
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)
#: Point(x=1, y=2)
print(p == Point(1, 2), hasattr(p, "__dict__"))
#: True False
with expected(AttributeError):
    p.x = 3  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'x'
```

`frozen_default=True` is the reason the assignment carries a `# type: ignore`.
The checker treats `Point` as frozen and reports `p.x = 3` before the program runs.
`@dataclass_transform` has no parameter that describes slots,
so the checker cannot tell that `Point` has slots.
On a record the checker still reaches the right verdict,
because it rejects every assignment to an instance.

A class whose base declares no `__slots__` writes `@record(slots=False)`.
The base gives every instance its `__dict__` back,
so slots on the subclass leave the `__dict__` in place.
The flag states that at the class.
That form is for a base someone else owns, such as a library class,
and for the rare class whose code reads the instance dict on purpose.
When the base is yours,
an empty `__slots__ = ()` on it keeps the records under it slotted,
as `shapes_oo.py` in [Rethinking Objects](20_Patterns--Rethinking_Objects.md#abstract-base-classes)
does.

When a class needs an option that `record()` lacks,
it keeps `@dataclass` written out: `order=True`,
or `weakref_slot=True` for a weak reference.

### When Slots Does Not Fit {#when-slots-does-not-fit}

`__slots__` changes more than where an instance keeps its fields.
A slotted instance has no `__dict__`, no `__weakref__` slot,
and a set memory layout, and each of the three breaks a feature:

```python
# slots_limits.py
import weakref
from dataclasses import dataclass
from functools import cached_property
from exceptions import expect, expected

@dataclass(slots=True)
class Node:
    value: int

    @cached_property
    def doubled(self) -> int:
        return self.value * 2

node = Node(3)
with expected(TypeError):
    # cached_property needs a __dict__ to write into:
    print(node.doubled)
#: [TypeError] No '__dict__' attribute on 'Node' instance to
#: cache 'doubled' property.

@dataclass(slots=True)
class Slotted:
    x: int

# No __weakref__ slot unless you declare one:
expect(TypeError, weakref.ref, Slotted(1))
#: [TypeError] cannot create weak reference to 'Slotted'
#: object

@dataclass(slots=True)
class OtherSlotted:
    y: int

with expected(TypeError):
    # Two nonempty slot layouts cannot combine:
    class Both(  # type: ignore
        Slotted, OtherSlotted
    ):
        pass
#: [TypeError] multiple bases have instance lay-out conflict
```

`cached_property` writes its cached value into the instance's `__dict__`,
so a slotted class needs a `"__dict__"` entry of its own in `__slots__` before `cached_property` works.
That entry gives back the per-instance dict that `slots=True` exists to remove.
The same is true of weak references,
as [Cleanup](10_Foundations--Cleanup.md#slotted-class-needs-weakref) shows.
Add `"__weakref__"` to `__slots__` if some other object needs to hold one
(`weakref_slot=True` adds it to a data class).

Since 3.15, `"__dict__"` and `"__weakref__"` work in the `__slots__` of any class,
including subclasses of `int`, `bytes`, and `tuple`,
which raised a `TypeError` for every non-empty `__slots__` through 3.14.
A subclass of `tuple`, or of a `namedtuple()` class,
goes further and accepts slots of any name.

Multiple inheritance is more restrictive than `cached_property` or weak references.
Python lays out a slotted instance as a block of storage with a set layout.
When two unrelated classes both declare non-empty `__slots__`,
each claims its own layout, the two layouts conflict,
and a class cannot inherit from both.
A class can inherit from one slotted base as long as its other bases declare no slots of their own.

A subclass that declares no `__slots__` of its own silently gets a `__dict__` back,
undoing the saving for every instance of that subclass (see exercise 6).

### Array Instead of List

A `list` of numbers stores full Python objects, each with its own header.
The `array` module packs numbers into a single block of C values:

```python
# compact_array.py
import sys
from array import array
from benchmark import report
from exceptions import expected

a = array("d", [1.0, 2.0, 3.0])  # "d" means C double
a.append(4.0)
print(a)
#: array('d', [1.0, 2.0, 3.0, 4.0])
print(a[1], a.typecode, a.itemsize)
#: 2.0 d 8
with expected(TypeError):
    # The value must match the type code:
    a.append("x")  # type: ignore
#: [TypeError] must be real number, not str

nums = [float(i) for i in range(10_000)]
list_bytes = sys.getsizeof(nums) + sum(
    sys.getsizeof(x) for x in nums
)
packed = array("d", nums)
array_bytes = sys.getsizeof(packed)
report(list_bytes=list_bytes, array_bytes=array_bytes)
print(f"array at least 3x smaller: "
      f"{array_bytes * 3 < list_bytes}")
#: array at least 3x smaller: True
```

The type code sets one type for every element,
so `array` stores them compactly and rejects values of the wrong type.
The size comparison shows the cost of boxing.
The `list` holds an 8-byte pointer to a 24-byte `float` object per element,
while the `array` uses 8 bytes per element total,
roughly a four-to-one difference
(one machine measured 325,176 bytes against 80,080).

### Memory View

A `memoryview` exposes another object's memory without copying it.
Slicing a large `bytes` or `bytearray` through a view avoids duplicating the data:

```python
# memory_view.py
data = bytearray(b"ABCDEF")
view = memoryview(data)  # No copy of the underlying bytes
chunk = view[1:4]
print(bytes(chunk))
#: b'BCD'
view[0] = ord("z")  # Writes through to the original
print(data)
#: bytearray(b'zBCDEF')
```

`bytes(chunk)` copies, but only to print the slice.
The view and `chunk` share `data`'s memory.

A view can also read fields out of a buffer without copying it,
the way a real protocol parser reads a header:

```python
# memory_view_traps.py
from exceptions import expect, expected

data = bytearray(b"\x01\x02XYZ")
view = memoryview(data)
kind, version, payload = view[0], view[1], view[2:]
print(kind, version, bytes(payload))
#: 1 2 b'XYZ'
print(payload.obj is data)  # No copy: same buffer
#: True

# An open view blocks resizing the buffer:
expect(BufferError, data.append, 1)
#: [BufferError] Existing exports of data: object cannot be
#: re-sized

readonly = memoryview(b"ABCDEF")
with expected(TypeError):
    # bytes is immutable, so a view over it stays read-only:
    readonly[0] = ord("z")
#: [TypeError] cannot modify read-only memory
```

`payload` is a second `memoryview`, not a copy of `data`.
`payload.obj` refers to the buffer from which it reads,
and that buffer is `data`.

Sharing the buffer is also the trap.
`memoryview(data)` keeps an export open on `data` for as long as `view` stays alive.
A slice of `view`, such as `payload`, holds the export open too.
`bytearray.append()` needs to resize the buffer,
so it raises a `BufferError` while an export is open.
`data.append(1)` fails here because `view` and `payload` are both still alive.
Release every view before resizing the buffer it reads,
either with `view.release()` or by letting the views go out of scope.

The second trap is about direction, not lifetime.
A `memoryview` over immutable `bytes` supports reading and slicing,
but writing through it raises a `TypeError` regardless of whether anything else has it open.
`memory_view.py` above writes through a view of a `bytearray`, which is mutable.

A view's own size stays fixed however much of the buffer it covers:

```python
# memory_view_size.py
import sys
from benchmark import report

big = bytearray(1_000_000)
copied = big[:500_000]
viewed = memoryview(big)[:500_000]
copy_bytes = sys.getsizeof(copied)
view_bytes = sys.getsizeof(viewed)
report(copy_bytes=copy_bytes, view_bytes=view_bytes)
print(f"view under 1% of copy: "
      f"{view_bytes * 100 < copy_bytes}")
#: view under 1% of copy: True
print(viewed.nbytes)
#: 500000
```

The slice copies half a megabyte.
The view addresses the same half megabyte while occupying a couple of hundred bytes,
because it holds a pointer and a shape rather than the data.

## Vectorize with NumPy

When the hot spot is arithmetic over a large collection of numbers,
the biggest improvement comes from removing the Python loop.
[NumPy](https://numpy.org/)
stores numbers unboxed in contiguous arrays like `array` does,
and executes whole-array expressions in compiled loops.
The plain-Python version repeats one expression per element.
The NumPy version states it once for the whole array:

```python
# vectorize_numpy.py
import timeit
import numpy as np
from benchmark import report

n = 1_000_000
as_list = list(range(n))
as_array = np.arange(n, dtype=np.float64)

def pure_python() -> list[float]:
    return [3.0 * x + 1.0 for x in as_list]

def vectorized() -> np.ndarray:
    return 3.0 * as_array + 1.0

assert vectorized().tolist() == pure_python()
t_loop = timeit.timeit(pure_python, number=5)
t_numpy = timeit.timeit(vectorized, number=5)
report(python_loop=t_loop, numpy=t_numpy,
       ratio=t_loop / t_numpy)
print(f"NumPy at least 3x faster: {t_numpy * 3 < t_loop}")
#: NumPy at least 3x faster: True
```

`np.arange(n, dtype=np.float64)` is NumPy's version of the `list(range(n))` line above it.
Both build the same sequence of `n` numbers (it's `arange`, not `arrange`).
`list(range(n))` boxes each one as a Python `int`.
`np.arange()` packs them into one contiguous block of C doubles,
the same layout `array` uses in `compact_array.py`.
`dtype=np.float64` chooses the element type, as `array`'s `"d"` type code does.

NumPy runs `vectorized()`'s expression as one compiled pass over contiguous memory instead of a million individual Python-level steps.
That whole-array expression is the declarative style [Confidence](43_Functional--Confidence.md#a-confidence-spectrum)
examines: describe the whole-array result and let the engine arrange the steps.

NumPy is a fast library you call, not a compiled extension you write.
You keep NumPy's speedup only while the data stays inside NumPy.
Calling a Python function on each element,
or converting arrays to lists and back,
puts a Python-level step back on every element.

One machine measured the vectorized pass at about 11x faster than the loop.
The 3x threshold sits far below any multiple you should see.

## JIT Compilation with Numba

Sometimes the loop cannot become an array expression,
because each step depends on the previous one, or the control flow is irregular.
The `@njit` decorator from [Numba](https://numba.pydata.org/)
compiles such a function to machine code on its first call:

```python
# count_primes_numba.py
import timeit
from benchmark import report
from numba import njit

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                break
        else:
            count += 1
    return count

fast_count_primes = njit(count_primes)
assert fast_count_primes(1_000) == count_primes(1_000)
limit = 200_000
t_python = timeit.timeit(
    lambda: count_primes(limit), number=1)
t_numba = timeit.timeit(
    lambda: fast_count_primes(limit), number=1)
report(python_loop=t_python, numba=t_numba,
       ratio=t_python / t_numba)
print(f"Numba at least 3x faster: {t_numba * 3 < t_python}")
#: Numba at least 3x faster: True
```

`njit(count_primes)` is the call that `@njit` above the `def` makes.
The function-call form keeps the original `count_primes()` as the Python baseline.
Numba compiles `fast_count_primes()` at its first call.
The `assert` makes that first call on a small input, before the timing starts.
That call compiles `fast_count_primes()` and checks its answer against the Python version's answer,
so the timed calls measure steady-state speed.

On numeric code over simple types and NumPy arrays,
Numba often runs nearly as fast as C.
The first call stops to compile.
Numba also rejects code that uses general Python objects,
such as custom classes.
When the hot spot is number-crunching, `@njit` needs one decorator,
where rewriting in another language needs a second toolchain and a build step.

One machine measured the compiled `count_primes()` at about 12x faster than the loop.
The 3x threshold sits far below any multiple you should see.

## Combine NumPy and Numba

NumPy and Numba solve different halves of the same problem,
and a single function often uses both.
NumPy gives you a compact array.
When the work per element depends on the element's value and no single vectorized expression fits,
`@njit` compiles a loop that walks the array.
The [Collatz conjecture](https://en.wikipedia.org/wiki/Collatz_conjecture)
is such a case.
From `n`, halve an even value or triple-and-increment an odd one,
and repeat until you reach 1.
The number of steps differs for every starting value,
so no single array expression produces it:

```python
# collatz_numba.py
import timeit
import numpy as np
from benchmark import report
from numba import njit

def collatz_lengths(values: np.ndarray) -> np.ndarray:
    lengths = np.empty(len(values), dtype=np.int64)
    for i in range(len(values)):
        n = int(values[i])
        steps = 0
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        lengths[i] = steps
    return lengths

fast_collatz_lengths = njit(collatz_lengths)
values = np.arange(1, 50_000, dtype=np.int64)
sample = values[:100]
assert np.array_equal(
    fast_collatz_lengths(sample), collatz_lengths(sample))
t_python = timeit.timeit(
    lambda: collatz_lengths(values), number=1)
t_numba = timeit.timeit(
    lambda: fast_collatz_lengths(values), number=1)
report(python_loop=t_python, numba=t_numba,
       ratio=t_python / t_numba)
print(f"Numba at least 3x faster: {t_numba * 3 < t_python}")
#: Numba at least 3x faster: True
```

As in `count_primes_numba.py`,
the `assert` compiles `fast_collatz_lengths()` on the first hundred values and checks it against the Python version before the timing starts.

`collatz_lengths()` takes a NumPy array and returns one,
so it composes with vectorized NumPy code on either side.
Compiling changes the loop's interior alone.
The same Python source runs as machine code instead of as bytecode over boxed `int` objects.

In practice, NumPy and Numba divide the work.
Use a vectorized NumPy expression wherever the shape of the computation allows it,
and write a `@njit` loop for the steps that need one,
keeping the array as the shared data structure throughout.

The same machine measured the compiled `collatz_lengths()` at about 38x faster than the loop,
so the 3x threshold leaves a wide margin here too.

## Converting a Slow Function to Rust

Moving the hot function into a compiled language runs it as machine code instead of as bytecode.
Rust fits because two tools, described below,
generate the binding code and build the package for you.
If you ask your AI to convert the hot Python function,
it can walk you through the rest of the process.
Once you're done, you import a module that looks from the outside like any other Python module,
except that it runs faster.

[PyO3](https://pyo3.rs) generates the Python bindings,
and [Maturin](https://www.maturin.rs)
builds and installs the result as an ordinary Python package.
`maturin new --bindings pyo3 fastcount` scaffolds the project.
In the crate, the `#[pyfunction]` attribute turns a Rust function into a Python function.

```rust
// fastcount/src/lib.rs
use pyo3::prelude::*;

#[pyfunction]
fn count_primes(limit: u64) -> u64 {
    let mut count = 0;
    for n in 2..limit {
        let mut d = 2;
        let mut prime = true;
        while d * d <= n {
            if n % d == 0 {
                prime = false;
                break;
            }
            d += 1;
        }
        if prime {
            count += 1;
        }
    }
    count
}

#[pyfunction]
fn collatz_lengths(values: Vec<u64>) -> Vec<u64> {
    values
        .into_iter()
        .map(|start| {
            let mut n = start;
            let mut steps = 0;
            while n != 1 {
                n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
                steps += 1;
            }
            steps
        })
        .collect()
}

#[pymodule]
fn fastcount(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(count_primes, m)?)?;
    m.add_function(wrap_pyfunction!(collatz_lengths, m)?)?;
    Ok(())
}
```

`maturin develop --release` compiles and installs `fastcount`.
The `--release` flag selects Cargo's optimized profile.
`maturin develop` alone builds the unoptimized debug profile,
the wrong build to time.
Python imports `fastcount` as a normal module with both functions attached:

```python
# rust/fastcount/demo.py
import timeit
from collections.abc import Callable
import fastcount

def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit):
        for d in range(2, int(n**0.5) + 1):
            if n % d == 0:
                break
        else:
            count += 1
    return count

def collatz_lengths(values: list[int]) -> list[int]:
    lengths: list[int] = []
    for start in values:
        n = start
        steps = 0
        while n != 1:
            n = n // 2 if n % 2 == 0 else 3 * n + 1
            steps += 1
        lengths.append(steps)
    return lengths

def speedup[T, R](
    name: str, slow: Callable[[T], R],
    fast: Callable[[T], R], arg: T,
) -> None:
    assert fast(arg) == slow(arg)
    t_slow = timeit.timeit(lambda: slow(arg), number=1)
    t_fast = timeit.timeit(lambda: fast(arg), number=1)
    print(f"{name} Rust speedup: {t_slow / t_fast:.1f}x")

speedup("count_primes", count_primes,
        fastcount.count_primes, 200_000)
# Sample run: count_primes Rust speedup: 12.3x
speedup("collatz_lengths", collatz_lengths,
        fastcount.collatz_lengths, list(range(1, 50_000)))
# Sample run: collatz_lengths Rust speedup: 36.0x
```

With Rust added, the options are one baseline and three faster alternatives,
listed here by how much work each takes rather than by speed.
The plain Python loop, timed in the Numba listings and in `demo.py`,
is the baseline.
NumPy alone runs the parts of a problem that reduce to whole-array arithmetic,
in compiled loops.
`@njit` compiles a loop that no array expression can replace,
at its first call and from inside Python.
Rust compiles that loop ahead of time,
and requires a second language and a build step.

In one machine's runs, measured 2026-10-13,
Numba and Rust ran at nearly the same speed:
12.2x against 12.3x on `count_primes`,
and 38.4x against 36.0x on `collatz_lengths`.
Rust offers something else: no warm-up call, no Numba dependency at runtime,
and compiled code for functions Numba cannot compile,
such as those over general Python objects.

Keep the interface coarse.
A single call that does significant work keeps the overhead of crossing between Python and Rust small beside that work.
A million calls that each do a little lose the speedup to that crossing overhead.
Passing millions of small Python objects across the boundary has the same effect,
since PyO3 converts each object as it crosses.
Numbers, strings, bytes, and NumPy arrays cross with little overhead.

`collatz_lengths()` takes a list of nearly 50,000 integers and returns a list of the same length,
so that many integers cross the boundary each way.
That traffic sounds like the thing to avoid.
But a hundred-odd loop iterations of real work follow each integer,
so the conversion cost is small beside that work.
The question is not the object count on its own but the work done per object crossed.

The repository's `rust/README.md` explains how to build and run `fastcount` yourself.
`uv run tip rust-all` compiles both functions, installs the module,
and runs the comparison in `demo.py`, printing your machine's own numbers.
The main book build skips this step.
Only `tip rust-all` needs the Rust toolchain.

## Concurrency

Sometimes the fix is not a faster function but a different architecture.
When the slowdown comes from waiting on the outside world, use `asyncio`.
If the work parallelizes (pure functions make this easy),
you can spread it across multiple cores or multiple processes.
That is a design decision with its own chapter,
[Concurrency](19_Techniques--Concurrency.md).

## Choosing a Strategy

Measure first.
A profiler finds the slow spots without guessing.
It also tells you whether the program spends its time computing or waiting,
and which strategy fits depends on that answer.
A program mostly waiting on a database, a socket, or a subprocess is I/O-bound.
Steps 2 through 9 below help it little.
Skip to step 10 and restructure around `asyncio` instead.
A program mostly consuming CPU is compute-bound.
The list below targets that case, simplest change first.

Every performance optimization adds effort, complexity, or dependencies.
Work down this list from the simplest change to the most involved,
stopping when the program is fast enough:

1. Run the straightforward version.
   It may be fast enough.
2. Try a faster platform: a newer CPython, a tail-calling build, its JIT, PyPy,
   or better hardware.
3. Write idiomatic Python and let built-ins like `sum()` run the loop in C.
4. Fix the algorithm and the data structures.
   This can produce order-of-magnitude improvements.
5. Make pipelines lazy with generators.
6. Cache the pure functions.
7. Reduce memory overhead with `slots=True`, `array`, and `memoryview`.
8. Vectorize with NumPy, or JIT-compile the loop with Numba.
9. Rewrite the proven-hot function in Rust.
10. Restructure for [async or parallelism](19_Techniques--Concurrency.md).

After every change, measure again.
Optimizations interact, the bottleneck moves,
and yesterday's hot spot may be irrelevant today.
The goal is not the fastest possible program.
It is a program that is fast enough and gives up as little clarity as possible.

Step 4 on that list, fixing the algorithm, usually gives the biggest speedup,
because it changes which curve your program follows,
not just where it sits on that curve:

![Big O growth rates vs. input size n](_images/big_o_growth)

## Exercises

Try each exercise before opening its [solution](../Solutions/18_Techniques--Performance/).

1.  `membership.py` sets `target` to the worst case, the last element.
    Measure the average case by timing lookups of many random targets,
    and see whether the conclusion changes.
2.  Use `timeit` to find the collection size below which the `list` scan beats the `set` lookup on your machine.
3.  Rewrite `eager_first_evens()` as a single list comprehension and measure its peak with `tracemalloc`.
    How close can an eager version get to the lazy one?
4.  Apply `@cache` to a function that prints as a side effect,
    and demonstrate that repeated calls skip the printing.
    Explain why caching suits only pure functions.
5.  In `heap_corruption.py`, replace `heap.pop(0)` with `heappop(heap)`.
    Pop three times, printing the heap after each one,
    and confirm `heap[0]` is the smallest remaining value every time.
    Why does the list still look unsorted after a correct pop?
6.  In `slots.py`, add `class Point3D(Point)` that declares no `__slots__` of its own.
    Confirm that an instance accepts `p.z = 3`,
    which `Point` rejects with an `AttributeError`,
    and find what provides the storage for `z`.
7.  In `monitoring_counts.py`,
    swap `set_local_events()` for `set_events()` and say which entry in the `Counter` is new and why.
    Then get the same two counts back using two local attachments instead,
    and explain what the two versions stop agreeing about in a larger program.
8.  Profile a script of your own with `uv run python -m cProfile -s cumulative`.
    Name the function with the largest `tottime` and the one with the largest `cumtime`,
    and explain why they are usually not the same function.
9.  `compact_array.py` compares an `array` against a `list` of the same floats.
    Time an element-by-element sum over each with `timeit`.
    The `array` uses a quarter of the memory.
    Is iterating over the `array` also faster, and why not?
10. Time `"".join(parts)` against `+=` in a loop for 10,000 short strings,
    then repeat at 100 strings.
    At which size does the difference stop mattering,
    and which of the two would you write regardless?
11. `bisect_search.py` uses `bisect()` and `search_comparison.py` uses `bisect_left()`.
    Build a sorted list with duplicates,
    run both against a value that appears three times,
    and explain which one you need to find the first occurrence and which one you need to insert after the last.
12. Run `jit_status.py` on your own interpreter and say which of the three states it reports.
    If it reports the second,
    run `membership.py` under `PYTHON_JIT=1` and `PYTHON_JIT=0` with the `--numbers` flag,
    and compare the two `ratio` lines.
    Explain why a listing this small is a poor test of the JIT.
