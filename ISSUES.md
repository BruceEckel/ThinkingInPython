<!-- loop progress: complete. Chapters 02-35 all reviewed; make verify passes. -->
<!-- Checked items from the review pass have been applied and removed; the items below remain open. -->
# Issues

## Chapter 19: Performance

- Chapter is an unfinished draft: `[[...]]` author notes remain at the top and in the "Benchmark Alternatives with `timeit`", "Write Idiomatic Python", "Lazy Evaluation with Generators", "Caching", "Vectorize with NumPy", "JIT Compilation with Numba", "The GIL and Free Threading", and "Choosing a Strategy" sections, and "Converting a Slow Function to Rust" is an empty heading.
- [ ] "For a priority queue shared across threads, `queue.PriorityQueue` wraps `heapq` with locking, covered with concurrency below." Nothing below covers `PriorityQueue`. Suggested fix: drop "covered with concurrency below" (or cover it when the concurrency sections are finished).
- [ ] `bisect_search.py` (`def grade(score):`) and `slots.py` (`def __init__(self, x, y):`) are untyped, unlike the rest of the book's examples. Suggested fix: add type hints (`def grade(score: int) -> str:`, `def __init__(self, x: int, y: int) -> None:`).

## Chapter 23: Singleton

- [ ] `class_variable_singleton.py` names its class `SingleTone`, which reads as a typo for `Singleton` (and its `#:` output does not display the name, so renaming is cheap). Suggested fix: rename the class (e.g. `SharedInstance` or `Singleton`) in the example and its test.
