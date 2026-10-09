<!-- outside review of Chapters/41_Functional--Toolkits.md, model gemini-3.8-flash-high, 2026-10-09 -->

Please apply the following technical and structural refinements to the `41_Functional--Toolkits.md` chapter:

**1. Section: `permutations` and `combinations` (Count mismatch with listing and explanation)**

* **Target Text:** "Three tools draw `r` elements from an iterable, and two questions separate them:"
* **Issue:** The section sets up a 2×2 classification based on two binary questions (order matters, elements repeat), which yields four outcomes. The listing immediately below imports and demonstrates four tools (`permutations`, `combinations`, `combinations_with_replacement`, and `product`), and the text below the listing explicitly refers to `product()` with `repeat=` as "the fourth combination of answers."
* **Instruction:** Change "Three tools draw `r` elements" to "Four tools draw `r` elements".

**2. Section: `cached_property` (Conflation of class dictionary and instance dictionary)**

* **Target Text:** "The stored value goes in the instance's `__dict__`, so the class must have one. A record is slotted and has none."
* **Issue:** In Python's data model, all classes have a `__dict__` (a `mappingproxy` storing methods and class attributes). The descriptor mechanism requires that the *instance* possess a writable `__dict__`; slotted classes omit `__dict__` from their instances. Stating that the class must have one and that a `@record` class has none confuses the class namespace with instance storage.
* **Instruction:** Change the text to read: "The stored value goes in the instance's `__dict__`, so instances must have one. An instance of a `@record` is slotted and has none."

**3. Section: `reduce` (Input type contract contradicts exception message)**

* **Target Text:** "Folds a sequence into a single value by repeatedly applying a two-argument function."
* **Issue:** `reduce()` operates on any iterable (including generators, streams, and lazy iterators), not just sequences. The text itself quotes the built-in exception two paragraphs later (`TypeError: reduce() of empty iterable with no initial value`), which highlights that an iterable is the actual requirement.
* **Instruction:** Change "Folds a sequence into a single value" to "Folds an iterable into a single value".

**4. Section: Groups of Any Size (Accidental sentence stutter in section opening)**

* **Target Text:** "The circle method is pairs-only. The circle method is a closed-form answer to one narrow question:"
* **Issue:** The subsection opens with two back-to-back sentences starting with "The circle method is...", immediately after the preceding subsection already concluded that the circle method solves the pairs-only version. The first sentence is an accidental duplicate fragment that repeats the start of the second sentence.
* **Instruction:** Remove the standalone "The circle method is pairs-only." sentence and open the subsection directly with "The circle method is a closed-form answer to one narrow question:".

## Verdicts

Second run, on the Flash model. Applied in commit 97d3d256, after each item was tested against the chapter and run under `uv run`.

1. Rejected. The sentence counts the tools that take an `r` argument: `inspect.signature()` under `uv run python` shows `permutations (iterable, r=None)`, `combinations (iterable, r)`, and `combinations_with_replacement (iterable, r)`, while `product` is `(*iterables, repeat=1)`. The prose after the listing introduces `product()` with `repeat=` as "the fourth combination of answers", so "Four tools draw `r` elements" would be the inaccurate count.
2. Applied. A slotted frozen data class under `uv run python` has a class `__dict__` (a `mappingproxy`) while `hasattr(instance, "__dict__")` is `False`, and the first `cached_property` access raises `TypeError: No '__dict__' attribute on 'R' instance`. The two sentences now say "so each instance needs one" and "A record is slotted, so its instances have none."
3. Applied. `reduce(add, (n for n in range(5)))` returns `10` and `reduce()` over an iterator of a set works too, so the section opening now says "Folds an iterable", and the empty-input sentence below it says "On an empty iterable" to match the quoted message.
4. Applied, with a different fix. The first sentence, "The circle method is pairs-only.", came from commit ad9be611 two days ago as the subsection's topic sentence, so it stays; the second sentence now opens "It is a closed-form answer" instead of repeating "The circle method is".
