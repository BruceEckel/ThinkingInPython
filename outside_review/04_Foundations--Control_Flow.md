<!-- outside review of Chapters/04_Foundations--Control_Flow.md, model gemini-3.1-pro-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `04_Foundations--Control_Flow.md` chapter:

**1. Errors and Exceptions (Refining terminology)**
* **Target Text:** "`checked_divide()` raises a `ValueError` rather than letting Python's own `ZeroDivisionError` through. Raise your own exception that way when the caller should hear about the bad argument rather than the failed arithmetic."
* **Issue:** `ValueError` is a standard, built-in exception, not a custom one. Calling it "your own exception" might confuse a reader into thinking they must define a new class here, which the text doesn't introduce until the `BadNumber` example later.
* **Instruction:** Change it to: "`checked_divide()` raises a `ValueError` rather than letting Python's own `ZeroDivisionError` through. Raise an exception explicitly that way when the caller should hear about the bad argument rather than the failed arithmetic."

**2. Context Managers (Binding guarantee caveat)**
* **Target Text:** "A `with` statement creates a guarantee about the exit, not a scope, so `f` is still in scope afterward and the listing can print `f.closed`."
* **Issue:** The variable `f` is only bound if the context manager's setup (the `__enter__` method) completes successfully. If opening the file failed and raised an exception, `f` would never be bound, and accessing it afterward would raise a `NameError`.
* **Instruction:** Change it to: "A `with` statement creates a guarantee about the exit, not a scope, so as long as the resource successfully opens, `f` is still in scope afterward and the listing can print `f.closed`."

**3. Mutating a Container While Looping (Dictionary mutation clarification)**
* **Target Text:** "The dictionary raises a `RuntimeError` instead of skipping silently."
* **Issue:** The surrounding text implies that any mutation of a dictionary during iteration is forbidden. While adding or removing keys changes the size and raises a `RuntimeError`, updating the values of existing keys is perfectly safe and a very common pattern.
* **Instruction:** Change it to: "The dictionary raises a `RuntimeError` instead of skipping silently, though updating the values of existing keys is perfectly safe."

**4. The Walrus Operator (Explaining the short-circuit guard)**
* **Target Text:** "The header pops a value, names it, and tests it, so the body starts with that value in hand."
* **Issue:** The listing's loop condition is `while stack and (item := stack.pop()) != "a":`. The explanation describes the pop, assignment, and test, but skips the crucial `stack and` part, which short-circuits to safely prevent an `IndexError` if the list empties before finding `"a"`.
* **Instruction:** Change it to: "The header uses `stack and` to short-circuit if the list empties, then pops a value, names it, and tests it, so the body starts with that value in hand."

## Verdicts

Applied in commit 0df793af, after each item was tested against the chapter and run under `uv run`.

1. Applied, with a different fix. `ValueError` is built in, and "your own exception" set against "Python's own `ZeroDivisionError`" could read as a class to define, which the chapter does not do until `BadNumber`. The sentence now reads "Choose the exception that way", since choosing which exception the caller sees is what `checked_divide()` does; the reviewer's "raise an exception explicitly" drops that contrast.
2. Rejected. The listing's `path.open("w")` succeeds, so a failed `__enter__()` is a case the listing never runs, and in this listing `f` is bound by the earlier `with path.open() as f` anyway, so `f.closed` would print even if the second open failed. (A probe confirmed the general point: after a failed `open()` inside `with ... as g`, `g` is unbound.)
3. Applied, with a different fix. A probe of `for k in d: d[k] = 0` ran clean, so the chapter's bare "the dictionary raises" was broader than the mechanism. The sentence now names the cause, "Adding the key changes the dictionary's size", which is the condition chapter 03's linked section states ("Changing a `dict`'s size while iterating over it raises a `RuntimeError`"), so the explicit values-are-safe caveat stays out.
4. Applied. The header is `while stack and (item := stack.pop()) != "a":` and the sentence described the pop, the name, and the test but not the `stack and` guard that keeps `pop()` off an empty list. It now reads "checks that the stack has an item, pops it, names it, and tests it".
