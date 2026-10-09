<!-- outside review of Chapters/41_Functional--Toolkits.md, model gemini-3.1-pro-high, 2026-10-08 -->

Please apply the following technical and structural refinements to the `41_Functional--Toolkits.md` chapter:

**1. The `functools` Toolkit: `partial` (Non-existent `functools.Placeholder`)**
* **Target Text:** "[`functools.Placeholder`](40_Functional--Foundations.md#leaving-a-gap-with-placeholder) reserves a position so you can preset a later positional argument and leave an earlier one for the caller."
* **Issue:** Python's standard `functools` module does not contain a `Placeholder` object for partial application. While the previous chapter may have built a custom placeholder for teaching purposes, asserting that it belongs to `functools` will cause readers to write failing imports.
* **Instruction:** Change to: "[`Placeholder`](40_Functional--Foundations.md#leaving-a-gap-with-placeholder) from the previous chapter reserves a position so you can preset a later positional argument and leave an earlier one for the caller, which standard `functools.partial` does not support."

**2. The `functools` Toolkit: `partialmethod` (`partial` is not a descriptor)**
* **Target Text:** "A `partial` object is a descriptor too, so writing `zero_pad = partial(pad, fill="0")` here works. `partial` and `partialmethod` differ as soon as an argument is positional. `partialmethod` passes the instance first and the bound arguments after it, the order a method expects. `partial` passes the bound arguments first and the instance after them, so `partial(pad, 5)` calls `pad(5, instance)` and fails with `AttributeError: 'int' object has no attribute 'value'`."
* **Issue:** A `functools.partial` object is not a descriptor, meaning it does not intercept attribute access to bind the instance. Accessing it on an instance simply returns the unbound partial object, and calling it fails with a `TypeError` for a missing argument (since the instance is never passed), not an `AttributeError` from inverted arguments.
* **Instruction:** Replace with: "A `partial` object is not a descriptor, so it does not bind `self` when accessed through an instance. If you wrote `zero_pad = partial(pad, 5)`, calling `instance.zero_pad()` would fail with a `TypeError` because the instance is never passed and `self` is missing. `partialmethod` acts as a descriptor that correctly inserts the instance as the first argument, making it the right choice inside a class body."

**3. The `itertools` Toolkit: `chain` (List comprehension unpacking loses laziness)**
* **Target Text:** "Where the iterables come from a loop, unpacking in a comprehension says the same thing without the import."
* **Issue:** `chain.from_iterable()` is lazy, maintaining constant memory use. Unpacking in a comprehension (e.g., `[*lst for lst in iterables]`) builds a fully realized list in memory. Since generator expressions do not support unpacking, replacing a lazy pipeline step with a list comprehension destroys its memory efficiency.
* **Instruction:** Change to: "Where the iterables come from a loop, a nested generator expression like `(x for lst in iterables for x in lst)` says the same thing without the import and preserves laziness. Unpacking in a list comprehension (`[*lst for lst in iterables]`) also works if you need the full list in memory."

## Verdicts

No item applied; each was tested against the chapter and run under `uv run`.

1. Rejected. `from functools import Placeholder` succeeds under `uv run python` (3.15.0rc2) and prints `Placeholder`; the object has been in `functools` since 3.14, and chapter 40's linked section teaches the standard one.
2. Rejected. `partial` has a `__get__()` on 3.15, and a probe class reproducing the listing printed `007` for `zero_pad = partial(pad, fill="0")` and `AttributeError 'int' object has no attribute 'value'` for `partial(pad, 5)`, which are the chapter's two claims word for word; no `TypeError` arises.
3. Rejected. PEP 798 allows unpacking in generator expressions too: `(*x for x in [[1, 2], [3, 4]])` is a `generator` yielding `[1, 2, 3, 4]` on 3.15, and the linked section of chapter 16 says the `*` works in "a comprehension or generator expression", so the chapter's sentence loses no laziness.
