<!-- outside review of Chapters/44_Effects--Effect_Management.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `44_Effects--Effect_Management.md` chapter:

**1. A Program Can Never Be Pure: ZeroDivisionError risk (Technical Refinement)**

* **Target Text:** "report(busy=busy, idle=idle, ratio=busy / idle)"
* **Issue:** `timeit.timeit(do_nothing, number=5)` executes five empty function calls, which takes only nanoseconds. Depending on the OS and clock resolution, `idle` can measure as exactly `0.0`, causing `busy / idle` to raise a `ZeroDivisionError` and crash the script.
* **Instruction:** Prevent the division by zero by clamping the divisor, for example: `report(busy=busy, idle=idle, ratio=busy / max(idle, 1e-9))`, or remove the ratio calculation entirely.

**2. What Is an Effect?: PRNG state mutation (Technical Refinement)**

* **Target Text:** "Suppose your function reads the time of day, or a random number. The read changes nothing in the environment, yet the result differs from one call to the next."
* **Issue:** Reading a pseudo-random number from a standard library (like Python's `random.random()`) actually *does* change the environment, because it mutates the hidden global PRNG state to advance the seed. This makes it both a side cause and a side effect.
* **Instruction:** Replace the random number example with a pure side cause, such as reading a configuration setting, or omit it to keep the focus on the clock: "Suppose your function reads the time of day. The read changes nothing in the environment..."

**3. Catch the Exception You Expect: Compiler computation vs. inference (Technical Refinement)**

* **Target Text:** "The compiler did not compute that list from the functions a body called, so an exception introduced three levels down meant editing every signature above it by hand."
* **Issue:** The Java compiler *does* compute the list of checked exceptions a body can throw—that is exactly how it knows to reject the code and force you to edit the signatures above it. The actual limitation is that it does not *infer* the signature automatically for you.
* **Instruction:** Change "The compiler did not compute that list" to "The compiler did not infer that list for the signature".

**4. Effects by Hand: ContextVar default values (Technical Refinement)**

* **Target Text:** "Setting the wrong one, or forgetting to set one, fails at the read, in whatever frame reads it."
* **Issue:** Forgetting to set a `ContextVar` only fails at the read (raising `LookupError`) if the variable was created without a `default` value. If a default was provided, the read silently succeeds with that fallback value instead of failing.
* **Instruction:** Add a brief caveat about defaults: "Setting the wrong one, or forgetting to set one (when no default is provided), fails at the read..."

## Verdicts

Applied in commit a10340d2, after each item was tested against the chapter and run under `uv run`.

1. Rejected. Timing `do_nothing()` with `timeit.timeit(..., number=5)` 200,000 times under `uv run python` gave a minimum of one `perf_counter` tick (1e-07 s, the clock's reported resolution) and zero readings of `0.0`, so the timed loop always spans at least one tick and `busy / idle` never divides by zero; the clamp guards a case the listing never meets.
2. Applied. `random.getstate()` differs before and after one `random.random()` call, so reading the global generator does change the environment and contradicts "The read changes nothing in the environment." The example sentence now names the time of day alone; the list of usual sources keeps the random number, which is still a side cause.
3. Applied. Java's compiler computes the checked exceptions a body can throw from its callees' `throws` clauses, which is how it rejects an uncovered one; what it lacks is inference into the signature. "did not compute" is now "did not infer" (no `uv run` test applies; this is a claim about Java's compiler).
4. Applied, with a different fix. A `ContextVar` with no default raised `LookupError` on `get()`, and one created with `default="fallback"` returned `fallback`. Rather than a parenthetical, the sentence now names the `LookupError`, and a new sentence says a defaulted `ContextVar` returns its default, so the mistake surfaces later, which strengthens the paragraph's point about lost checking.
