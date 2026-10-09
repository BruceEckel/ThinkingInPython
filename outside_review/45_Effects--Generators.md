<!-- outside review of Chapters/45_Effects--Generators.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `45_Effects--Generators.md` chapter:

**1. Section: A Generator Is a Description (Missing handling for immediate return)**

* **Target Text:** 
```python
    request = next(conversation)
    while True:
        answer = answers[request]
```
* **Issue:** `drive()` does not catch `StopIteration` on its initial `next(conversation)` call. If a generator finishes without yielding any requests (for example, if it simply executes `return Result(...)` immediately), this first call raises an unhandled `StopIteration` and crashes the driver instead of returning the result.
* **Instruction:** Wrap the first `next()` call in a `try...except StopIteration` block to safely catch an immediate return:
```python
    try:
        request = next(conversation)
    except StopIteration as stop:
        return stop.value
    while True:
        answer = answers[request]
```

**2. Section: The Send Channel (Type checker behavior on iteration)**

* **Target Text:** "The type checker reports nothing, because `manual()` is a valid `Generator[str, int]`."
* **Issue:** Modern strict type checkers (including Pyright, which `ty` wraps) actively flag iterating over a generator that requires a non-`None` `SendType`. The `for` loop implicitly calls `__next__()` (which sends `None`), so `ty` will report a type violation that `None` cannot be sent where `int` is expected, contradicting the claim that it reports nothing.
* **Instruction:** Change the sentence to acknowledge the error: "The type checker rejects the `for` loop because it implicitly sends `None` where `collect()` expects an `int`, but at runtime the generator silently discards the values."

**3. Section: The Return Channel (Clarifying `StopIteration` value)**

* **Target Text:** "A list's iterator sets none, so `v = yield from [1, 2, 3]` yields the three items and sets `v` to `None`."
* **Issue:** A list's iterator doesn't actively "set" `None`; rather, it ends iteration by raising a bare `StopIteration` exception without providing an explicit value, which defaults its `value` attribute to `None`. 
* **Instruction:** Clarify the mechanism by changing the sentence to: "A list's iterator raises `StopIteration` without a value, so `v = yield from [1, 2, 3]` yields the three items and sets `v` to `None`."

## Verdicts

Applied in commit 31f1bd34, after each item was tested against the chapter and run under `uv run`.

1. Rejected. Every generator the chapter passes to `drive()` (`interview()` in `two_way_generator.py` and `yield_from_delegates.py`, and `survey()`) yields at least one `Question`, so the first `next()` always produces a request; an immediate `return` is a case the listing's own input never exercises, and the guard would add defensive code to a teaching listing.
2. Rejected. `uv run ty check` (ty 0.0.84) on the extracted `manual_forwarding.py` printed "All checks passed!", and `uv run pyright` on the same file reported 0 errors, so the chapter's "The type checker reports nothing" holds. `ty` is Astral's own checker and wraps no Pyright.
3. Applied, with a different fix. A probe showed an exhausted list iterator raises `StopIteration()` with empty `args` and `value` `None`, and `v = yield from [1, 2, 3]` binds `None`. "sets none" read as a homophone of `None` beside it, so the sentence now says the list's iterator ends with a bare `StopIteration`, whose `value` defaults to `None`.
