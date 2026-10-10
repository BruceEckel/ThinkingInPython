<!-- outside review of Chapters/04_Foundations--Control_Flow.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `04_Foundations--Control_Flow.md` chapter:

**1. Section: Errors and Exceptions (Correction of non-existent compiler warning)**

* **Target Text:** "Python also flags the `return` in `finally` at compile time. Running the listing prints `SyntaxWarning: 'return' in a 'finally' block` to standard error before `swallowed`."
* **Issue:** CPython (assuming Python 3.8 through 3.15) does not emit a `SyntaxWarning` or any compile-time diagnostic for a `return` statement inside a `finally` block; executing `finally_swallows.py` prints only `swallowed` to stdout and emits nothing to stderr. Linters such as Ruff flag this construct (rule `B012`), but the Python compiler itself does not.
* **Instruction:** Replace the claim with a note attributing the warning to linters: "Python executes the statement without complaint, but linters such as Ruff flag a `return` inside a `finally` block (rule `B012`) because discarding an in-flight exception is almost always a bug."

**2. Section: Mutating a Container While Looping (Alignment of advice with listing)**

* **Target Text:** "The fix is the same for both. Build a new container with a comprehension, or collect what to remove first and remove it after the loop."
* **Issue:** In `mutating_while_looping.py`, the dictionary mutation adds new keys (`ages[name + "!"] = 0`), so advising the reader to "collect what to remove first" contradicts the code directly above it. In addition, iterating over a snapshot of the container via `list(ages)` or `ages.copy()` is the standard Python technique when mutating during iteration.
* **Instruction:** Update the text to address additions as well as removals, and introduce iterating over a snapshot: "The fix is to build a new container with a comprehension, iterate over a snapshot of keys (`for name in list(ages):`), or collect modifications first and apply them after the loop."

**3. Section: The Loop `else` Clause (Disambiguation of control-flow ladder)**

* **Target Text:** "Put `continue` in the inner loop's `else` and a `break` right after it."
* **Issue:** "Right after it" easily reads as placing `break` directly after `continue` inside the `else` block, where it would be unreachable dead code. In `nested_break.py`, the `break` belongs outside the `else` block at the outer loop's indentation level, immediately following the inner `for`/`else` construct.
* **Instruction:** Clarify the structural placement of the outer `break`: "Put `continue` in the inner loop's `else`, and place a `break` immediately after the inner loop's `else` block, at the outer loop's indentation level."

**4. Section: `range()`, `enumerate()`, and `zip()` (Mechanism of lazy validation)**

* **Target Text:** "`strict=True` raises a `ValueError` on the mismatch instead."
* **Issue:** C++ and Java programmers accustomed to eager collection utilities may assume `strict=True` validates collection lengths upfront when `zip()` is invoked. Because `zip` returns an iterator, length checking occurs lazily during iteration once the shortest sequence is exhausted while another still has items, which is why `zipping.py` must consume the iterator with `list()` to trigger the exception.
* **Instruction:** Clarify that validation happens during iteration: "`strict=True` raises a `ValueError` lazily during iteration once the shortest sequence runs out while another still has items, which is why the example consumes the iterator with `list()` to trigger the check."

## Verdicts

Second run, on the Flash model. Applied in commit 04446504, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Rejected. Running `Examples/04_Foundations--Control_Flow/finally_swallows.py` under `uv run python` printed `finally_swallows.py:7: SyntaxWarning: 'return' in a 'finally' block` to standard error before `swallowed`, and `-W error` turned it into a `SyntaxError`; the compiler-time warning is PEP 765's, in CPython since 3.14, so the chapter's claim is what this Python does and the reviewer's "3.8 through 3.15" is out of date.
2. Applied, with a different fix. The listing's dictionary loop adds keys (`ages[name + "!"] = 0`), so "collect what to remove" named a fix for the list half alone. The sentence now offers a comprehension, a loop over a snapshot such as `list(ages)` while changing the original, or collecting the changes and applying them after the loop, in place of "modifications"; the snapshot idiom the reviewer names is the usual one and the chapter had not shown it.
3. Applied, with a different fix. In `nested_break.py` the outer `break` (`[3]`) sits after the inner `for`/`else` at the outer loop's indentation, and "right after it" could put it inside the `else` behind the `continue`, where it would never run. The sentence, which comes before the listing and so cannot cite a tag, now says "a `break` after the inner loop, at the outer loop's level", shorter than the proposed wording.
4. Applied, with a different fix. `zip()` returns an iterator and the listing wraps the strict call in `list()` for that reason, which the prose left unexplained. The sentence now says the `ValueError` comes at the point where iteration finds one argument exhausted and another not, and that this is why the listing consumes the `zip()` with `list()`, without the "lazily" and "C++ and Java" framing.
