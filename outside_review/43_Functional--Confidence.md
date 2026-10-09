<!-- outside review of Chapters/43_Functional--Confidence.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `43_Functional--Confidence.md` chapter:

**1. Section: Automatic Parallelism (Integer exactness)**

* **Target Text:** "        if all(n % d for d in range(2, int(n**0.5) + 1)):"
* **Issue:** Using `n**0.5` converts the integer to a float, which loses precision for numbers larger than 2^53. While the limits here are small, a prime checker should ideally use exact integer arithmetic, and Python's `math.isqrt(n)` is the robust way to do this.
* **Instruction:** Replace the line with `        if all(n % d for d in range(2, math.isqrt(n) + 1)):` and add `import math` to the top of the listing.

**2. Section: Automatic Parallelism (Python 3.14 requirement)**

* **Target Text:** "The `if __name__ == "__main__"` guard exists for the same reason."
* **Issue:** Readers on Linux may recall that older Python versions used the `fork` start method by default, which didn't strictly require the guard. Python 3.14 changes the default multiprocessing start method to `spawn` universally, making this guard mandatory on all operating systems.
* **Instruction:** Expand the sentence to clarify this: "The `if __name__ == "__main__"` guard exists for the same reason, and Python 3.14 makes it strictly required on all operating systems."

**3. Section: Referential Transparency (Hashability caveat)**

* **Target Text:** "`lru_cache` returns the stored result for any repeated arguments, and nothing in the language checks that the function it wraps is referentially transparent."
* **Issue:** The text explains that `lru_cache` doesn't check for referential transparency, but omits a critical mechanical constraint: `lru_cache` requires all arguments to be hashable. A pure function that takes a mutable collection (like a `list` or `dict`) cannot be cached this way.
* **Instruction:** Append this sentence: "It also requires all arguments to be hashable, so a pure function that takes a list or dictionary cannot be cached this way."

**4. Section: Automatic Parallelism (Order preservation)**

* **Target Text:** "The `assert` passes on every run, because a pure call returns the same answer whichever process runs it, and whenever."
* **Issue:** While purity ensures the values are identical, `parallel == serial` also requires the two lists to be in the exact same order. The assertion passes because `pool.map()` inherently preserves the input order of the results, regardless of which process finishes a task first.
* **Instruction:** Replace the sentence with: "The `assert` passes on every run, because a pure call returns the same answer whichever process runs it, and `pool.map` guarantees the results return in the original order."

**5. Section: Automatic Parallelism (Chunksize performance caveat)**

* **Target Text:** "Whether parallel pays at a given size is a separate question, and the timing answers it."
* **Issue:** For a large number of very fast calls, parallel execution can be slower than serial due to the inter-process communication overhead of sending each task individually. To make parallelism pay off in that scenario, the user must explicitly set the `chunksize` argument in `pool.map()` to group the work.
* **Instruction:** Add this sentence immediately after: "For a large number of fast calls, you must also set `chunksize` in `pool.map()` to reduce the communication overhead."

## Verdicts

Applied in commit 7e7ac2d0, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The largest limit is `800_000`, and `int(n**0.5) == math.isqrt(n)` held for every `n` in `range(2, 800_000)` under `uv run`; the first disagreement found was near `(2**27 + 1)**2`, far past any input the listing gives. The item guards a case `parallel_pure.py` never exercises.
2. Rejected. The mechanism is wrong: on 3.15, `multiprocessing/context.py` makes `forkserver` the default on POSIX systems other than macOS and `spawn` on macOS and Windows (where the probe printed `spawn`); 3.14 did not make `spawn` universal. The chapter already states the guard's reason without a platform qualifier ("Each worker imports this module to find `count_primes()`"), and chapter 19 (Concurrency) covers the guard.
3. Rejected. The linked [`lru_cache`](41_Functional--Toolkits.md#lru_cache) section already says "so every argument must be hashable. Passing a `list` raises `TypeError: unhashable type: 'list'`.", and this paragraph's point is that nothing checks referential transparency.
4. Applied. The `assert` compares lists, so it also depends on order; a probe with `pool.map(slow, [0.6, 0.3, 0.0])` returned `[0.6, 0.3, 0.0]` though the last call finished first. The chapter now adds that `pool.map()` returns the answers in the order of `limits`, as `map()` does, so the lists match position by position in whatever order the calls finish.
5. Rejected. The listing makes four long calls, the case where `chunksize` changes nothing, and the paragraph already says the timing settles whether parallel pays; "you must also set `chunksize`" adds tuning advice for a workload the chapter never shows.
