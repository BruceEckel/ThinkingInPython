# Performance

Performance means at least two things when it comes to computing:

1. The speed at which an application is developed.
2. The speed at which that application executes.

Python addresses the first issue through its clear syntax and extensive power and flexibility.
As to the second issue, Python is commonly considered to be slow.

## Is it Actually Too Slow?

Computer programming projects have a long history of *premature optimization*,
when the designers decide ahead of time, based on their biases,
that runtime performance will be insufficient.
This results in elaborate designs that generate excessive costs.

Python can be surprising.
A program coded in the most straightforward way, without concern for performance,
can often run fast enough for your needs.
Do not automatically assume that a simply-written program will be too slow.
Try it out first. It could be just fine.

If it is too slow, use Occam's Razor: try the simplest approach first.
That might be enough, and if it is, you might save a lot of time and money.

What follows is an approach to solving performance problems,
starting with the simplest techniques and getting successively more complex.

## Try a Faster Platform

There are alternative interpreters for Python, notably PyPy which boasts a 4x to 10x speedup.

How much does a hardware upgrade cost compared to paying programmers to solve the performance problem?
If it's noticeably less, then buying new hardware might be a quick win.

## Profilers

A *profiler* looks for the slow spots in your code, so you know where to focus.
Although it is tempting to think you "have a pretty good idea where the slowdown is," we turn out to be very bad at guessing this.
A profiler tells you for sure, and keeps you from wasting your time.

I am currently most impressed with [Scalene](https://github.com/plasma-umass/scalene).

If you can narrow the problem down to a particular function, there may be techniques that speed up the algorithm used in that function.

## Benchmark Alternatives with `timeit`

[[`timeit` times small snippets, so you can compare two ways of writing the same thing once a profiler has pointed you at a hot spot]]

## Choose Better Algorithms and Data Structures

[[Usually the largest win: a better Big-O, and the right container for the job, such as `set` or `dict` for membership and lookup, `deque` for queues, and `bisect` or `heapq` for ordered data]]

## Write Idiomatic Python

[[Let the interpreter do the work: built-in functions and comprehensions instead of hand-written loops, the C-implemented standard library (`itertools`, `collections`, `functools`), `str.join` instead of `+=` in a loop, and hoisting repeated attribute or global lookups into locals]]

## Lazy Evaluation with Generators

[[Stream values with generators and `itertools` instead of building large intermediate lists, so work happens on demand and memory stays flat]]

## Caching

## Reduce Memory Overhead

[[`__slots__` shrinks each instance and speeds attribute access; `array` and `memoryview` hold large homogeneous data compactly]]

## Vectorize with NumPy

[[Move numeric loops into whole-array operations. NumPy is a fast library you call, not a compiled extension you write]]

## JIT Compilation with Numba

[[`@njit` compiles numeric Python to machine code in place, a lighter step than Rust when the hot spot is number-crunching]]

## Concurrency: I/O-Bound vs CPU-Bound

[[Choose the tool by the bottleneck: async or threads overlap I/O-bound work, while separate processes give CPU-bound work real parallelism]]

## ASYNCIO

## Parallelism

## The GIL and Free Threading

[[The GIL serializes CPU-bound threads, which is why the parallelism above reaches for processes. The free-threaded (no-GIL) builds available since 3.13 lift this and change when threads alone are enough]]

## Converting a Slow Function to Rust

## Choosing a Strategy

[[Recap: measure first, then work down this list from the cheapest change to the most involved, stopping as soon as the program is fast enough]]
