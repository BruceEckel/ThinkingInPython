[[Reviewed]]
# Deep review: 03_Containers.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Show that immutability is shallow

**Kind:** teaching
**Where:** section "Immutability" (line ~475, after the `MappingProxyType` sentences)
**Problem:** This is the first place in the book that claims immutability, and the claim reads as total. A reader takes away "an immutable container cannot change" and then writes `config = ("host", ["a", "b"])`, shares it, and watches the inner list change under them. The chapter also says a `frozendict` "is hashable" and that `tuple`s can be keys; both fail for a container holding a mutable element, and the reader has no way to predict that from what is here. Chapter 20's `frozen_leaky.py` teaches the same lesson but 17 chapters later, and chapters 22, 35, and 36 already assume the reader knows it.

**Proposal:** Add a listing and a short paragraph at the end of the section:

````
Immutability is also shallow.
An immutable container fixes which objects it holds,
not what those objects contain:

```python
# shallow_immutability.py

nested = (1, [2, 3])
nested[1].append(4)  # The tuple's element is still mutable
print(nested)
#: (1, [2, 3, 4])
try:
    hash(nested)  # So the tuple cannot be hashed
except TypeError as e:
    print(type(e).__name__)
#: TypeError
try:
    nested[0] = 9  # type: ignore
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

The `tuple` refuses to let go of the `list`,
but nothing stops that `list` from changing,
and a container holding an unhashable object is itself unhashable.
Immutability pays off when it goes all the way down.
[Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution)
shows the same leak inside a frozen data class.
```
````

I verified the listing: output and `ty` both clean, and the `# type: ignore` on the tuple assignment is required (`ty` flags the unused ones, so the other two lines carry none).

**Cost:** Adds a fourth listing to the Immutability section, which is already the longest in the chapter. It makes the forward link to chapter 20 explicit, so a rename of that chapter's "The Immutability Solution" heading now breaks `heading_links.py` here too, which is the desired failure mode. It also cross-supports proposal 12 (the key-hashability sentence in "Dictionaries").

---

## 2. Say that reading a missing `defaultdict` key inserts it, and that `Counter` does not

**Kind:** teaching
**Where:** sections "`Counter`" (line ~270) and "`defaultdict`" (line ~297)
**Problem:** The chapter puts these two side by side and describes them the same way. `Counter` gets "A missing key counts as zero rather than raising `KeyError`"; `defaultdict` gets "A missing key gets a fresh empty list." One of those two lookups mutates the dictionary and the other does not, and the chapter never says which. This is the standard `defaultdict` footgun: a read-only membership check written as `if by_kind[k]:` silently grows the dictionary, and a later `len()` or iteration reports keys nobody ever added. The reader has just been shown both types with no signal that they differ.

**Proposal:** Add one line to each listing and one clause to each explanation. In `counter.py`, after `print(counts["dog"])`:

```python
print("dog" in counts)  # Reading it added nothing
#: False
```

In `defaultdict.py`, after `print(by_kind["fish"])`:

```python
print("fish" in by_kind)  # Reading it added the key
#: True
```

Then in the `defaultdict` paragraph, after "a callable that builds the default," add:

```
The factory runs on the *read*, and the new value is stored,
so touching a missing key grows the dictionary.
Use `in` or `dict.get()` when you only want to look.
```

Both outputs verified.

**Cost:** none. Both listings already print a missing-key lookup, so this adds a line each rather than a new example.

---

## 3. Say that `{}` is an empty dictionary, not an empty set

**Kind:** teaching
**Where:** section "Sets" (line ~178)
**Problem:** The chapter teaches the `{...}` set literal and never mentions that its empty form is taken. The Tuples section takes care to show `empty = ()`, so a reader reasoning by symmetry writes `seen = {}` and then gets `AttributeError: 'dict' object has no attribute 'add'` with nothing in the chapter to explain it. The chapter also shows `set()` nowhere, so the reader does not know the empty-set spelling exists.

**Proposal:** In `sets.py`, after the `a = {1, 2, 3, 3}` line, add:

```python
print(type({}).__name__, type(set()).__name__)
#: dict set
```

and one sentence under the listing: "The `{}` literal was taken by `dict` first, so an empty set is `set()`."

**Cost:** none.

---

## 4. Contrast `in` on a list against `in` on a set

**Kind:** teaching
**Where:** section "Sets" (line ~179)
**Problem:** "Like the `dict`, it has fast membership tests" is the closest the chapter comes to saying why sets exist, and *fast* has no comparison attached. Meanwhile `slicing.py` already showed `5 in xs` on a list without saying that scan is O(n). A reader who has been given both spellings and told one is "fast" cannot tell whether the difference matters at 10 items or 10 million. Since dict and set both exist for this one property, the chapter should measure it once.

**Proposal:** Add a listing after the set-algebra prose, plus a sentence:

````
The speed is the reason to convert a `list` to a `set` before repeated lookups.
A `list` compares against every element in turn;
a `set` computes one hash and looks in one place:

```python
# membership_cost.py
from timeit import timeit

n = 200_000
items = list(range(n))
lookup = set(items)
missing = -1
list_time = timeit(lambda: missing in items, number=20)
set_time = timeit(lambda: missing in lookup, number=20)
print(set_time * 100 < list_time)  # Not close
#: True
```

Searching the `list` is O(n) and searching the `set` is O(1),
so the gap widens without limit as `n` grows.
````

I ran this three times; the real ratio is several thousand to one, so the `* 100` margin has room to spare on a loaded machine.

**Alternative:** state the O(n)-vs-O(1) contrast in prose only, with no listing. Cheaper, but the `deque` section already chose to measure rather than assert, so measuring here is the consistent choice.

**Cost:** introduces `timeit` in the Sets section, before the `deque` section that currently introduces it. If you take proposal 6 (splitting `deque.py`), the `timeit` explanation moves here and the `deque` timing listing refers back to it.

---

## 5. State that a `dict` preserves insertion order

**Kind:** teaching
**Where:** section "Dictionaries" (line ~172, under the listing)
**Problem:** `dictionaries.py` prints `{'Alice': 30, 'Bob': 25}` and then iterates and prints Alice, Bob, Carol in insertion order, and the `#:` markers depend on that. Nothing in the chapter, or anywhere in the book, says the order is guaranteed. Two sections later a set is called "unordered," which invites the reader to conclude that a `dict` is unordered too, so the markers here look like luck. Both facts are load-bearing for the rest of the book: `Counter`'s repr, `most_common()`, and every dict-keyed table in later chapters print in a predictable order.

**Proposal:** After "Use `dict.get()` instead of `[]` ...", add:

```
A `dict` iterates in insertion order, which the language guarantees.
A `set` makes no such promise:
the order it prints is an artifact of hashing,
so never write code, or a test, that depends on it.
```

Delete the last clause if you would rather not aim a rule at the reader this early.

**Cost:** touches the "unordered" wording in the Sets section only by reference, not by edit. It makes the chapter's own set listings slightly awkward, since they print sets and show exact orders in the markers; a sentence in the Sets section noting that the displayed order is CPython's and not a guarantee would close that loop.

---

## 6. Split `deque.py` into three things it is currently teaching at once

**Kind:** structure
**Where:** section "`deque`" (line ~306)
**Problem:** One listing introduces `deque`'s four operations, the `list` operations that mimic them, and `timeit` (never mentioned before or explained after). The reader meets a benchmark harness, two module-level functions, and a threshold boolean while trying to learn what a double-ended queue is. The listing is 50 lines, by far the longest in the chapter, and the last third of it has nothing to do with `deque`'s interface.

**Proposal:** Split into `deque.py` (the `deque` operations alone, ending at `print(dq)`), `list_as_deque.py` (the `list` mimicry, ending at `print(lst)`), and `deque_timing.py` (from `n = 20_000` down), with the existing "A `list` can stand in for a `deque`" paragraph moved up between the second and third, so the timing listing arrives as the answer to a question the prose has just raised. Add one sentence introducing `timeit` where it first appears: "`timeit()` runs a callable and returns the elapsed seconds."

**Cost:** exercise 1 names `deque.py` and would become "in `deque_timing.py`". `tools/data/norun.txt` does not list any of these. `18_Performance.md` links to `03_Containers.md#deque`, which is the heading, not the filename, so it survives.

---

## 7. Teach `sorted()` against `list.sort()`

**Kind:** teaching
**Where:** section "Lists and Slicing" (line ~70, after the slicing listing)
**Problem:** Sorting is the operation readers want from a list second, right after appending, and the chapter never mentions it. Book-wide, `sorted()` first appears in chapter 5 as an example of passing a `key=` function, and `.sort()` first appears in chapter 16; neither is contrasted anywhere. The near-miss is well known: `words = words.sort()` binds `None`, because `.sort()` mutates and returns nothing. Nothing in the book warns about it.

**Proposal:** Add after the slicing listing:

````
`sorted()` builds a new sorted list from any iterable.
`list.sort()` reorders a list in place and returns `None`:

```python
# sorting.py

words = ["pear", "Fig", "apple"]
print(sorted(words))  # A new list; words is untouched
#: ['Fig', 'apple', 'pear']
print(words)
#: ['pear', 'Fig', 'apple']
print(words.sort())  # Sorts in place and returns None
#: None
print(words)
#: ['Fig', 'apple', 'pear']
print(sorted(words, reverse=True))
#: ['pear', 'apple', 'Fig']
```

`sorted(x)` returns the result, so `x = x.sort()` binds `None`
and loses the list.
Uppercase sorts before lowercase because the comparison is by code point;
[Functions](05_Functions.md#lambdas) shows how `key=` changes that.
````

Output verified, and the `05_Functions.md#lambdas` anchor resolves (that section is where `sorted(words, key=...)` already appears).

**Cost:** adds a fourth listing to "Lists and Slicing". The `key=` sentence is a forward reference to chapter 5, which the chapter already does twice (to 5, 12, and 18).

---

## 8. Merge "Lists and Iteration" into "Lists and Slicing"

**Kind:** structure
**Where:** sections "Lists and Iteration" (line 7) and "Lists and Slicing" (line 38)
**Problem:** Two consecutive sections about lists, split at no natural seam. The first teaches `for` over a list and `append()`; the second teaches `append()` again on line 5 of its listing. `for` is not this chapter's subject and is taught properly in [Control Flow](04_Control_Flow.md#conditionals-and-loops) with `range()`, `enumerate()`, and `zip()`. The section's closing lines ("This example has no type declarations. Each object carries its own type.") restate a point chapter 2 already made under "Variables and References."

**Proposal:** Fold `list.py` into the opening of "Lists and Slicing" as the first, smallest listing, retitle the merged section "Lists," and drop the type-declaration sentences. The `for` demonstration stays; it earns its place as the reason lists come first, not as a lesson about `for`.

**Alternative:** keep both sections and cut only the duplicate `append()` from `slicing.py`. Smaller diff, but the two-section split stays unmotivated.

**Cost:** `list.py` keeps its filename, so `Examples/` and `norun.txt` are unaffected. No other chapter links to `#lists-and-iteration` or `#lists-and-slicing` (checked). A merged heading of "Lists" changes the anchor to `#lists`, which nothing currently references.

---

## 9. Do not define a tuple as a record

**Kind:** prose
**Where:** section "Tuples and Unpacking" (line ~144)
**Problem:** "Tuples are fixed-length immutable records where each position has a distinct meaning" reads as the definition of `tuple`, and the chapter's own `tuple([1, 2, 3])` and `tuple("abc")` on the previous page contradict it. Both uses are real and the distinction is worth naming: a tuple as a record (heterogeneous, positions mean different things, `namedtuple` improves it) and a tuple as an immutable sequence (homogeneous, arbitrary length, a frozen list).

**Proposal:** Replace that sentence with:

```
A tuple used this way is a fixed-length immutable record,
where each position has a distinct meaning.
Used the other way, holding many values of one type,
it is an immutable `list`.
```

**Cost:** the `namedtuple` section's opening ("A `namedtuple` is a fixed-length record like the heterogeneous tuple above") still reads correctly against the new wording.

---

## 10. Explain the `# type: ignore` where it first appears

**Kind:** prose
**Where:** section "Immutability" (lines ~435 and ~469)
**Problem:** `immutability.py` carries two `# type: ignore` comments with no explanation. Two listings later the prose says "The one `# type: ignore` sits on the line that deliberately misbehaves," which reads as if this were the first one the reader had seen. A reader who noticed the earlier two is now unsure whether they were something else.

**Proposal:** Move the explanation up to follow `immutability.py`, generalized to cover all three occurrences: "Each `# type: ignore` sits on a line that deliberately misbehaves. Assigning into an immutable container is a type error as well as a runtime one, so the comment lets the example demonstrate the exception it expects." Then delete the paragraph after `frozendict_demo.py`.

**Cost:** none. All three suppressions are still necessary under the current `ty` (verified: it reports unused ones and reports none here).

---

## 11. Add exercises for the first half of the chapter

**Kind:** exercise
**Where:** section "Exercises" (line ~487)
**Problem:** Four exercises, and three of them are on `deque`, `defaultdict`, and `set_methods` alone. Lists, slicing, tuples, unpacking, dictionaries, `Counter`, and `namedtuple` get none, and those are the parts of the chapter a beginner most needs to practice. The set clusters on the second half.

**Proposal:** Add three, and consider dropping exercise 3 (`a.union(b, c)` restates a line the listing already shows):

```
5.  Given `xs = [10, 20, 30, 40, 50]`, write one slice expression for each of:
    the last two items, everything but the first and last,
    and a reversed copy of the middle three.
6.  Rewrite `counter.py`'s tally using a `defaultdict(int)` and no `Counter`.
    Which parts of `Counter` did you have to write yourself?
7.  Rewrite `heterogeneous.py` with a `namedtuple`.
    Show that the unpacking line still works unchanged.
```

Exercise 6 pairs with exercise 2 and makes the `Counter`/`defaultdict` relationship explicit.

**Cost:** `Solutions/03_Containers.md` would need entries for whichever of these you keep.

---

## 12. Qualify which tuples can be dictionary keys

**Kind:** prose
**Where:** section "Dictionaries" (line ~152)
**Problem:** "Strings, numbers, and tuples can" is stated flatly against "the mutable built-in containers are not hashable," so a reader learns "immutable means usable as a key." `(1, [2])` is a tuple and is not usable as a key. The Immutability section later says "A dictionary key must be hashable rather than immutable," which is the correction, but it arrives 300 lines later and never names the case it is correcting.

**Proposal:** Change to "Strings, numbers, and tuples of hashable values can." One word does the work, and it sets up the later sentence instead of contradicting it.

**Cost:** none. Reads better still if proposal 1 lands, since the shallow-immutability listing then demonstrates the excluded case.

---

## 13. Small prose repairs

**Kind:** prose
**Where:** throughout
**Problem and proposal:** four wordings that made me stop and reread.

- Line 3: "With languages like C++ and Java, containers are add-on libraries." "With" is doing the work of "In." Change to "In languages like C++ and Java."
- Line ~73: "Since each slot just holds a reference to whatever object you put there." Cut "just."
- Line ~303: "The `defaultdict` constructor argument is a *factory*, a callable that builds the default. Here, the `list` argument is a factory that produces a fresh empty list for each new key." The second sentence restates "is a factory." Change to "Here, `list` produces a fresh empty list for each new key."
- Line ~450: "It runs under Python 3.15:" means "this listing requires Python 3.15." Change to "This listing requires Python 3.15:" or drop it, since the paragraph two above already dates `frozendict` to 3.15.

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~398: the pointer to [Performance](18_Performance.md) described `memoryview` as "compact homogeneous storage" and `heapq` as an "algorithm over a sorted `list`". Neither is right: a `memoryview` is a zero-copy view onto another object's memory and copies nothing, and a heap is explicitly not a sorted list (chapter 18's own listing prints a heap to show it is not reordered). Split into four accurate phrases, one per module.
- line ~470: "Because a `frozendict` cannot change, it is hashable" is false when a value is unhashable. Verified: `hash(frozendict(a=[1]))` raises `TypeError`. Now "hashable when its values are," which also sets up the next sentence ("A dictionary key must be hashable rather than immutable") instead of contradicting it.
- line ~476: "Neither you nor code you pass it to can modify an immutable container by accident, so you never need a defensive copy before sharing it." False for a container holding a mutable element: `t = (1, [2, 3]); t[1].append(4)` works. Narrowed to "can add, remove, or replace an element by accident, so a container of immutable elements needs no defensive copy before you share it." Proposal 1 above is the fuller repair.
- line ~213: `set_methods.py` was the only listing in the chapter with no blank line between its `# slug.py` marker and the first line of code (55 of 57 listings in chapters 01-09 follow the convention; the other exception is `globals_demo.py` in chapter 6, not mine to touch). Added the blank line.

## Verified clean, no action

- All 14 extracted listings run, and every `#:` marker matches real stdout.
- `ruff check`, `ty check`, and `pytest` on `build/examples/03_Containers` all pass.
- `deque.py`'s `deque_time < list_time` boolean printed `True` on 5 of 5 consecutive runs, so it is not the flaky kind.
- `banned_phrases.py` and `heading_links.py` pass after my edits.
- Cross-references verified against their targets: `12_Data_Classes_as_Types.md#data-classes`, `05_Functions.md#default-and-keyword-arguments`, and `18_Performance.md` all resolve, and `18_Performance.md` links back to this chapter's `#deque` and `#immutability` anchors, both of which survive the edits above.
- PEP 814 confirmed Final for Python 3.15: `frozendict` is a builtin, takes keyword construction, and is hashable when its values are.
- All three `# type: ignore` comments are still required; `ty` flags unused ones and reports none.
