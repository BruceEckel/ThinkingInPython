<!-- outside review of Chapters/44_Effects--Effect_Management.md, model gemini-3.8-flash-high, 2026-10-09 -->

**Please apply the following technical and structural refinements to the `44_Effects--Effect_Management.md` chapter:**

**1. Section: Catch the Exception You Expect (misdescription of exception origin)**

* **Target Text:** "`slope()` can catch the one exception it names and turn the failure into an ordinary `float`, its existing return type, instead of introducing a new type:"
* **Issue:** In `divide_by_zero_impurity.py`, `slope()` names no exceptions; `ZeroDivisionError` is raised implicitly by Python's `/` operator. Stating that `slope()` catches the exception it "names" before introducing the listing that adds the `try/except` block misdescribes the original function.
* **Instruction:** Change "the one exception it names" to "the one exception division can raise" (or "the one exception it anticipates").

**2. Section: Catch the Exception You Expect (technical accuracy regarding C++ vs Java exception specifications)**

* **Target Text:** "C++ and Java tried to track exceptions with *exception specifications*, a list of exceptions written by hand on each function. The compiler did not infer that list from the functions a body called, so an exception introduced three levels down meant editing every signature above it by hand. Programmers usually avoided that work by widening the specification until it permitted every exception. The specifications exposed implementation details, and most people now count them a failure. C++ reduced its version to a single bit: whether a function can throw."
* **Issue:** For a book targeted at programmers coming from C++ and Java, this conflates Java's compile-time checked exceptions with C++'s dynamic exception specifications. Prior to C++11 deprecation and C++17 removal, C++ dynamic exception specifications (`throw(...)`) were enforced at runtime (calling `std::unexpected()`), not statically checked by the compiler across call chains; it was Java's checked exceptions (`throws`) that forced upstream signatures to be updated at compile time.
* **Instruction:** Distinguish Java's compile-time checked exceptions from C++'s dynamic specifications. Replace the passage with: "Java tried to track exceptions at compile time with checked exceptions (`throws`), where an exception introduced three levels down meant editing every signature above it by hand. C++ tried runtime exception specifications (`throw(...)`) before reducing its version to a single bit (`noexcept`): whether a function can throw."

**3. Section: Combine the First and Third (control flow misdescription)**

* **Target Text:** "Past that one `match`, `slope()` checks nothing."
* **Issue:** In `slope_edge.py`, `slope(10, run)` is called directly inside the `case Ok(run):` arm of the `match` statement, not past or after the `match` construct.
* **Instruction:** Change "Past that one `match`, `slope()` checks nothing." to "Inside that `match`'s `Ok` branch, `slope()` checks nothing." (or "Once unpacked by that `match`, `slope()` checks nothing.").

**4. Section: Effect Management for Python? (technical accuracy regarding concurrency vs asynchrony)**

* **Target Text:** "Python demonstrates that the machinery can work, and hard-codes it to a single Effect, concurrency, rather than letting you declare your own."
* **Issue:** `async` in Python tracks asynchrony (cooperative suspension of a coroutine), not concurrency. Calling an `async def` function sequentially or driving it with `asyncio.run(description)` (as shown in `coroutines_are_descriptions.py`) involves no concurrent execution; concurrency requires scheduling multiple tasks concurrently via primitives such as `TaskGroup` or `create_task()`.
* **Instruction:** Change "concurrency" to "asynchrony" (or "asynchronous suspension").

## Verdicts

Second run, on the Flash model. Applied in commit 4c4b625e, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. The sentence comes before `slope_catch.py`, so "the one exception it names" points at an `except` clause the reader has not seen yet. The proposed "the one exception division can raise" is false: `10**400 / 1` raises an `OverflowError` under `uv run python`. The sentence now names `ZeroDivisionError` directly.
2. Applied, with a different fix. The reviewer is right that C++'s dynamic specifications were checked at runtime and Java's `throws` lists at compile time, so "The compiler did not infer that list" implied a compile-time check C++ never had. The proposed replacement also dropped the widening and the "exposed implementation details" points. Instead, two lines now say that Java's compiler checks the list while C++ checked it at runtime and ended the program, and "Neither language inferred the list" keeps the rest of the paragraph (no `uv run` test applies; this is a claim about C++ and Java).
3. Applied. `slope(10, run)` sits inside the `case Ok(run):` arm of `slope_edge.py`'s `match`, so "Past that one `match`" placed the call after a construct that contains it. The sentence now reads "Once the `match` unpacks an `Ok`, `slope()` checks nothing."
4. Applied. `coroutines_are_descriptions.py` drives one coroutine with `asyncio.run()` and nothing runs concurrently, so the Effect that `async` tracks is suspension, not concurrency. "concurrency" is now "asynchrony", the term chapter 19 and chapter 47 ("Asynchrony is `async def` and `await`") use.
