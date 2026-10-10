<!-- outside review of Chapters/03_Foundations--Containers.md, model gemini-3.8-flash-high, 2026-10-10 -->

Please apply the following technical and structural refinements to the `03_Foundations--Containers.md` chapter:**

**1. Section: Tuples and Unpacking (clarification of listing behavior)**

* **Target Text:** "`*rest` collects on the left of the assignment and spreads inside the display, so the pair rotates `evens` by one place."
* **Issue:** `evens` is not mutated or rotated in place; it remains `[0, 2, 4]`. The unpacking assignment and subsequent list display construct a new list `[2, 4, 0]` with the elements rotated. For programmers coming from C++ (`std::rotate`) or Java, describing this as rotating `evens` misstates what the listing does.
* **Instruction:** Clarify that the operation produces a new rotated list rather than mutating `evens`: "`*rest` collects on the left of the assignment and spreads inside the display, producing a new list with `evens`'s elements rotated by one place."

**2. Section: Dictionaries (precision regarding iteration failure)**

* **Target Text:** "A two-character key such as `"Bo"` unpacks into its letters and the loop finishes with no error."
* **Issue:** In `for name, age in ages:`, the loop unpacks every key yielded by the dictionary. If `ages` contains a two-character key alongside keys with other lengths (such as `"Alice"` or `"Carol"` in `dictionaries.py`), the loop still raises `ValueError` on those keys. The silent failure where the loop runs to completion without an exception occurs only when every key in the dictionary happens to have length two.
* **Instruction:** Specify that the loop finishes without error only when all keys have two characters: "If every key has two characters (such as `{"Bo": 1, "Jo": 2}`), each key unpacks into its letters and the loop finishes with no error."

**3. Section: Specialized Containers (concurrency accuracy for `deque`)**

* **Target Text:** "Use a `deque` for a single-threaded queue."
* **Issue:** In CPython, `collections.deque` provides thread-safe, atomic `append()`, `appendleft()`, `pop()`, and `popleft()` operations. The reason to prefer `queue.Queue` across threads is that `Queue` provides blocking synchronization (`get(block=True)`, `task_done()`), not that `deque` cannot be used safely across threads.
* **Instruction:** Clarify that `deque` is suited for queues that do not require blocking coordination: "Use a `deque` when you need a fast FIFO queue without blocking synchronization."

**4. Section: Shallow Immutability (technical accuracy regarding container hashability)**

* **Target Text:** "A container holding an unhashable object is unhashable too."
* **Issue:** Built-in mutable containers (`list`, `dict`, `set`) are always unhashable, regardless of whether their elements are hashable. The rule illustrated by `nested = (1, [2, 3])` applies specifically to immutable containers that would otherwise be hashable, such as tuples and `frozendict`s. Stating that any container holding an unhashable object is unhashable suggests the false converse—that containers are hashable unless an element breaks them.
* **Instruction:** Restrict the statement to immutable containers: "An immutable container holding an unhashable object is unhashable too."

## Verdicts

Second run, on the Flash model. Applied in commit 56a05830, after each item was tested against the chapter and run under `uv run` on 3.15.0rc2.

1. Applied, with a different fix. The listing's `print([*rest, first])` builds a display, so `evens` keeps `[0, 2, 4]` and the rotated list is new; "rotates `evens`" misdescribed its listing. The sentence now says the pair builds a new list holding `evens` rotated by one place and that `evens` stays as it was, shorter than the proposed wording.
2. Applied, with a different fix. A probe of `for name, age in {"Bo": 1, "Jo": 2}:` ran to the end printing letters, and the same loop over `{"Bo": 1, "Alice": 2}` raised `ValueError: too many values to unpack (expected 2)` at the second key, so "the loop finishes with no error" held for a dictionary of two-character keys alone. The sentence now says the key unpacks with no error and a dictionary whose keys are all that length hides the slip, in place of the reviewer's example dictionary.
3. Applied, with a different fix. `collections.deque`'s documentation calls its appends and pops from either side thread-safe, so "single-threaded" named the wrong distinction; the paragraph's own next sentences already send a reader to `queue.Queue`, and chapter 19 says what it adds: it blocks the calling thread while it waits. The first sentence is now "Use a `deque` for a queue", and the `queue.Queue` sentence now gives the blocking `get()` as the reason to switch, in place of "shared between threads".
4. Applied. The surrounding paragraph is about a `tuple`, and a `list` or `dict` is unhashable whatever it holds, so the general "A container" invited the false converse the reviewer names. The sentence now reads "An immutable container holding an unhashable object is unhashable too", the reviewer's wording.
