When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Line numbers below refer to `Chapters/03_Containers.md` **after** the fixes
this review already applied (see the list at the end of the file).

---

[] Reject

**Chapter opening, lines 3-4 — "add-on libraries" is not what C++ and Java do.**

"In languages like C++ and Java, containers are add-on libraries." Both ship
their containers in the standard library: `java.util` is part of the JDK and
the STL is part of ISO C++. Neither is an add-on, and a reader who knows
either language stumbles on the first sentence of the book's third chapter.

The contrast Bruce actually wants is one level down: in C++ and Java a
container is a class you name and construct (`new ArrayList<>()`,
`std::vector<int> v;`), while in Python the three main containers have
literal syntax and operator support baked into the grammar.

Proposed change, replacing lines 3-5:

> In C++ and Java a container is a library class you name and construct.
> Python builds its containers into the grammar:
> `[1, 2]`, `{"a": 1}`, and `{1, 2}` are literals,
> and `in`, `len()`, and slicing work on them without importing anything.
> Lists, tuples, dictionaries, and sets are fundamental data types.

That keeps the comparative opening and makes the claim true. Alternative, if
the shorter opener is preferred: change "add-on libraries" to "library
classes" and leave the rest alone. I recommend the first, because it names
the thing the chapter then spends four sections on.

---

[] Reject

**`slicing.py` (line 40) — one listing, two subjects, and four operations the prose never names.**

The prose above the listing introduces indexing and slicing only. The last
four statements of the listing (`xs.append(60)`, `xs.insert(3, 5)`,
`len(xs)`, `5 in xs`) are a different subject, and three of them are new:
`insert`, `len`, and `in` appear here with no explanation, and the prose
after the block goes straight back to slicing ("Slicing works on any
sequence"). `insert` then gets explained properly 400 lines later in
`list_as_deque.py`, where it is introduced as though for the first time.

There is also a small trap in the current form: `xs.insert(3, 5)` inserts the
*value* 5 at *index* 3, and the very next line prints `5 in xs`. A reader
still learning that `[3]` and `3` mean different things in different
positions has to work out which `5` is which.

Proposed change: end `slicing.py` at the `xs[::-1]` line and move the four
mutating/query statements into their own listing under the "Slicing works on
any sequence" sentence, with one line of prose naming them:

```python
# list_ops.py

xs = [10, 20, 30]
xs.append(40)  # Add one item at the end
xs.extend([50, 60])  # Add every item of an iterable
xs.insert(1, 15)  # Insert before index 1
print(xs, len(xs))
#: [10, 15, 20, 30, 40, 50, 60] 7
xs.remove(15)  # Remove the first item equal to 15
del xs[0]  # Remove by index
print(xs, 30 in xs)
#: [20, 30, 40, 50, 60] True
```

That also closes the `append`/`extend` gap (below) at no extra cost.

---

[] Reject

**Lists section — `append` vs. `extend` is never taught, here or in the book.**

`grep -rn "\.extend(" Chapters/` returns exactly two hits, both in chapter 20
and both incidental (`counted.extend([2, 3])` demonstrating that `extend()`
does not route through `append()`). Chapter 3 is where a reader learns to
grow a list, and `xs.append([1, 2])` versus `xs.extend([1, 2])` is one of the
most-hit beginner potholes in the language: the two look interchangeable and
differ by one nesting level.

Proposed change: adopt the `list_ops.py` listing above, which shows both
adjacent, and add one sentence after it:

> `append()` adds its argument as a single element, so `xs.append([1, 2])`
> puts a `list` inside the `list`.
> `extend()` adds each item of its argument instead.

---

[] Reject

**Lists section — `[[0]] * 3` and mutating-while-iterating go unwarned.**

Two near-misses a reader will write in their first week, neither mentioned:

1. `grid = [[0]] * 3` (or `[[0] * 3] * 3`) makes three names for one inner
   list, so `grid[0][0] = 1` changes all three rows. Chapter 2 taught that
   assignment does not copy, which is exactly the machinery here, so this is
   an application of taught material rather than new content.
2. Removing items from a list while iterating over it skips elements,
   silently and with no exception.

Proposed change: one short listing at the end of the Lists section covering
both, or, if that is too much for a survey chapter, two sentences of prose
pointing at the `*` case only. I recommend the listing for `*` (it produces
visible wrong output, which prose cannot) and prose for the iteration case.
This is a judgement call about chapter length, which is why it is reported
rather than applied.

---

[] Reject

**Dictionaries section (lines 203-246) — the most-used container gets the shortest section.**

One listing and, after the fixes applied, three short paragraphs. Compare:
sets get two listings plus a timing listing, and `deque` alone gets three
listings. Missing from the section entirely:

- removing entries: `del ages["Bob"]` and `ages.pop("Bob", None)`
- merging: `a | b` and `a |= b` (3.9+), and `update()`
- constructing: `dict(zip(names, ages))`, `dict(pairs)`

`|` on dicts is particularly worth having, because the same operator means
union on sets one section later and a reader will assume the same semantics
(it is not symmetric for dicts: the right operand wins on a collision).

Proposed change: a second listing in the Dictionaries section:

```python
# dict_ops.py

a = {"x": 1, "y": 2}
b = {"y": 20, "z": 3}
print(a | b)  # Merge; the right side wins a collision
#: {'x': 1, 'y': 20, 'z': 3}
print(a.pop("x"), a)  # Remove and return
#: 1 {'y': 2}
del b["z"]
print(b)
#: {'y': 20}
print(dict(zip("abc", [1, 2, 3])))  # Build from pairs
#: {'a': 1, 'b': 2, 'c': 3}
```

Price: about 20 lines, and it makes the Dictionaries section the length its
subject deserves. Cheaper alternative: the `|` line and the `del`/`pop` lines
appended to `dictionaries.py`, with no new listing.

---

[] Reject

**Chapter-wide — nothing points at comprehensions.**

Comprehensions are how lists, dicts, and sets are built in practice, and the
very next chapter introduces them
([Control Flow](04_Control_Flow.md#comprehensions)), with a full chapter at
[Comprehensions](16_Comprehensions.md). Chapter 3 never mentions the word.
A reader finishes the container chapter knowing only `append()` in a loop.

Proposed change: one sentence at the end of the Lists section, after the
mixed-types paragraph:

> A loop with `append()` is not the usual way to build a list from another
> one. [Control Flow](04_Control_Flow.md#comprehensions) introduces the
> comprehension, which does it in a single expression, and
> [Comprehensions](16_Comprehensions.md) covers the dict and set forms.

---

[] Reject

**Lines 244-246 — the ordering paragraph is half about a container introduced in the next section.**

> A `dict` iterates in insertion order, which the language guarantees.
> A `set` makes no such guarantee: the order it prints is an artifact of
> hashing, so never write code, or a test, that depends on it.

The second sentence sits in the Dictionaries section and warns about a
container the reader has not met. Thirty-five lines later, in the Sets
section, line 281 says essentially the same thing again: "The order these
sets print comes from CPython's hashing and is not a guarantee." The point is
made
twice, once early and once in the right place.

Proposed change: keep the `dict` sentence where it is and delete the `set`
sentence from lines 245-246. Then strengthen the surviving Sets version at
line 281, which currently states the fact without the consequence:

> The order these sets print comes from CPython's hashing, not from any
> guarantee, so never write code, or a test, that depends on it.

---

[] Reject

**Line 283 — "Every operator above has a named method" is not quite true of the listing above it.**

`sets.py` ends with `print(2 in a)`. `in` is an operator and it has no public
named-method form (`__contains__` is the dunder, not an API). Everything else
in the sentence is right.

Proposed change: "Every set-algebra operator above has a named method."
Two words, and the paragraph's real point (methods take any iterable and any
number of arguments) is untouched.

---

[] Reject

**`deque_timing.py` (line 466) — the boolean carries no magnitude, unlike its sibling three sections earlier.**

`membership_cost.py` prints `set_time * 100 < list_time` with the comment
`# Not close`, so the single `True` tells the reader the gap is at least a
hundredfold. `deque_timing.py` prints a bare `deque_time < list_time`, which
is compatible with the `deque` being one percent faster. The prose above it
promises "Timing the two at the left end shows it," and the output shows only
that one is smaller than the other. A reader cannot narrate the mechanism
from that.

Measured here (Linux, 2 CPUs, shared, `n = 20_000`, three runs): ratios of
414, 364, and 401. At `n = 2_000` the ratios were 8, 25, and 31; at
`n = 200_000`, 3574, 3374, and 3373.

Proposed change: `print(deque_time * 50 < list_time)  # Not close`, matching
the neighboring listing. 50 leaves a 7x margin against the worst observed
ratio at the listing's own `n = 20_000`.

This is deliberately reported and not applied: it edits a
timing-comparison boolean, and the numbers above come from a noisy shared
Linux box, not Bruce's machine. Please confirm the margin holds there before
taking it.

---

[] Reject

**Line 492 — "Use a `deque` whenever you need a queue" overreaches, and `maxlen` is missing.**

Two problems in one line.

First, the advice is wrong at both edges of the word "queue." A queue shared
between threads should be `queue.Queue`, which blocks and is thread-safe
(chapter 19 says so at its line 1322); a priority queue should be `heapq`,
which this chapter itself recommends three paragraphs later. `deque` is the
right answer for a single-threaded FIFO, which is narrower than "whenever you
need a queue."

Second, `deque(maxlen=N)` — a bounded ring buffer that discards from the far
end on overflow — is the `deque` feature with no `list` equivalent at all,
and `grep -rn maxlen Chapters/` returns nothing book-wide. Everything the
chapter shows about `deque` is "a `list` but faster at the left end";
`maxlen` is the part that is a different data structure.

Proposed change, replacing line 492:

> Use a `deque` for a single-threaded queue.
> A `deque(maxlen=n)` additionally caps its length,
> discarding from the far end when a new item overflows it,
> which is the sliding window a `list` has no equivalent for.
> For a queue shared between threads, use `queue.Queue`
> (see [Concurrency](19_Concurrency.md)),
> and for a priority queue, `heapq`.

Optionally add two lines to `deque.py` showing `maxlen` in action; I would,
since the prose claim ("discarding from the far end") is exactly the kind
that reads clearer as output.

---

[] Reject

**`frozendict_demo.py` (line 586) — the listing does not show the property the next paragraph asserts.**

Right after the listing: "Because a `frozendict` cannot change, it is
hashable when its values are, so like a `tuple` or a `frozenset` it can serve
as a dictionary key or a set member." The listing shows subscripting,
equality, and the `TypeError` on write. It never hashes anything.

`immutability.py` does not have this problem: it puts `frozenset`s into a
`set` and proves membership. The `frozendict` listing should carry its own
weight the same way, especially since being usable as a key is the entire
reason PEP 814 exists.

Proposed change: two lines before the `try` block in `frozendict_demo.py`:

```python
cache = {prefs: "rendered"}  # Usable as a dict key
print(cache[frozendict(zoom=125, theme="dark")])
#: rendered
```

Verified to run and to type-check clean on the pinned 3.15.0b2 build.

---

[] Reject

**`immutability.py` (line 543) — the `MappingProxyType` caveat is stated in prose but never shown.**

Lines 613-614: "It blocks writes through the view, but it is a window onto
the original `dict`, so changes to that underlying `dict` still show
through." That is the one thing about `MappingProxyType` a reader can get
wrong, it is the reason line 612 calls it "the one exception to watch," and
it is 70 lines from the listing that would demonstrate it. The listing still
holds `settings`, so the demonstration costs two lines.

Proposed change: after the existing `print(config["level"])` line in
`immutability.py`:

```python
settings["level"] = 9  # The view is live, not a copy
print(config["level"])
#: 9
```

Then the paragraph at lines 612-614 can say "as `immutability.py` showed"
instead of introducing the fact cold. Price: the later `try` block's
`config["level"] = 9` now reads as "assigning 9 again," which is fine, but if
that bothers you, change the write-through to `settings["level"] = 4` and the
marker to `4`.

---

[] Reject

**Exercise 1 (line 648) — `n = 200_000` costs about a minute of the reader's time.**

Measured here: the `list` side of `deque_timing.py` takes 57 seconds at
`n = 200_000` (three runs: 58.7 s, 57.0 s, 57.6 s) against 0.017 s for the
`deque`. It is O(n²), so a machine half as fast takes two minutes, and a
reader who does not know that will assume they hung the interpreter.

The exercise's point — the margin grows with `n` — is already fully visible
at `n = 100_000`: measured here at 13.5 s for the `list` and 0.008 s for the
`deque`, a ratio of 1679 against the 400 seen at `n = 20_000`. The solution's
explanation holds unchanged at that size.

Proposed change: use `100_000` instead of `200_000`, or keep `200_000` and
add "the list version takes roughly a minute at this size; that is the point"
to the exercise. Either way the Solutions file's line 10 comment
(`n = 2_000  # then 200_000`) needs the same number, which is outside this
review's scope — flagging it so the two stay in step.

---

[] Reject

**Exercises — nothing exercises the Dictionaries section or unpacking.**

Mapping the seven exercises onto the chapter: 1 `deque`, 2 `defaultdict`,
3 sets, 4 sets + hashability, 5 slicing, 6 `Counter`/`defaultdict`,
7 `namedtuple`. Plain `dict` is touched only through `defaultdict`, and
unpacking — half of a section title, and now a listing of its own — is not
touched at all.

Proposed change: add two exercises.

> 8.  Given `pairs = [("a", 1), ("b", 2), ("c", 3)]`, build a `dict` from it,
>     then print its keys, its values, and the result of merging it with
>     `{"c": 30, "d": 4}`. Which value ends up under `"c"`, and why?
> 9.  Using one unpacking assignment each, and no indexing, pull the first
>     element, the last element, and everything in between out of
>     `row = [1, 2, 3, 4, 5]`. Then explain why `a, b = row` raises
>     `ValueError` while `a, *b = row` does not.

Price: `Solutions/03_Containers.md` needs two matching entries, which is out
of scope for this review. Exercise 8 assumes the `dict_ops.py` listing
proposed above; drop it if that listing is rejected.

---

[] Reject

**End of chapter (line 644) — the reader leaves with facts but no decision procedure.**

The chapter's real claim is "Python gives you a container for every job,
built in." By the end the reader has met eight of them and has no compact
answer to "which one do I use?" The chapter never puts the choice in one
place, and the closest thing to a summary, the last line before Exercises, is
about shallow immutability.

Chapters 2 and 4-7 also have no conclusion section, so adding a
`## Conclusion` heading would be out of character for Part I. A closing
paragraph under the existing Immutability section would not be.

Proposed change: three or four lines before `## Exercises`:

> Choosing a container is mostly one question: what do you do with it most?
> Ordered items you walk through are a `list`;
> a fixed record whose positions mean different things is a `tuple`
> or a `namedtuple`;
> lookup by key is a `dict`;
> uniqueness and membership are a `set`.
> Reach past those four only when a measurement or a specific job says to,
> and freeze whichever you pick as soon as it stops changing.

Note: "Reach past" contains "Reach ", which `banned_phrases.py` does **not**
match (the banned entry is "Reach for"), but it is the same tic — I would
write "Go past those four only when...". Flagging so the gate result is not
mistaken for approval of the phrasing.

---

## Cross-chapter

Two threads that end in other chapters. **Neither needs an edit there** —
both are now consistent — but they should stay that way if either end moves.

- **`Chapters/02_Tour.md` line 132.** It says
  "`*rest` collects whatever is left over.
  [Containers](03_Containers.md#tuples-and-unpacking) covers the general
  form." Before this review that forward reference was unsatisfied: chapter
  3's "Tuples and Unpacking" section showed only `x, y = point` and never
  mentioned a starred target. The new `unpacking.py` listing satisfies it. If
  that listing is ever cut, chapter 2's sentence goes stale silently, since
  the link resolves to a real anchor and `heading_links.py` cannot see the
  broken promise.

- **`Chapters/22_Data_Transfer_Objects.md` line 101.** It links to
  `03_Containers.md#namedtuple` and says `typing.NamedTuple` is the class
  form of `collections.namedtuple`. Chapter 3 now links forward to
  `22_Data_Transfer_Objects.md#the-standard-library-versions`, so the pair is
  mutually linked. Chapter 3's old advice ("For records with defaults,
  methods, or type annotations, prefer a data class") contradicted chapter
  22, which recommends `NamedTuple` for a typed immutable record and a data
  class for a mutable one; chapter 3 now matches chapter 22.

---

## Fixes already applied to `Chapters/03_Containers.md`

For reference when reading the diff; no action needed on these.

1. Line 5: added `tuple` to the opening list of fundamental data types.
2. Lines 146-147: noted that the empty tuple `()` is the exception to
   "the comma makes the tuple."
3. Lines 149-180: new `unpacking.py` listing plus prose — starred targets,
   unpacking any iterable, nested targets, and the `ValueError` when the
   counts do not match. Satisfies chapter 2's forward reference.
4. Lines 224-227 and 237-242: `dictionaries.py` now shows that iterating a
   `dict` yields its keys and shows `values()`; new prose names the three
   views and warns that `for name, age in ages` unpacks each *key*.
5. Line 325: `timeit()` "runs a callable `number` times and returns the
   total elapsed seconds" (it was "runs a callable and returns the elapsed
   seconds", which reads as one call).
6. Lines 412-417: `setdefault()` contrasted with `defaultdict` — the
   `defaultdict` section hand-rolls the `if kind not in plain` form that
   `setdefault` replaces, and never named it.
7. Lines 517-523: `namedtuple` now points at `typing.NamedTuple` and at
   chapter 22, and recommends a data class for a *mutable* record rather
   than for "defaults, methods, or type annotations" (all three of which
   `NamedTuple` supports).
8. Line 533: "Each of the three built-in mutable containers has an immutable
   counterpart" — the previous "Each mutable container" was false directly
   after a section introducing `deque`, `Counter`, and `defaultdict`, none
   of which have one.
9. Line 578: "Modifying an immutable container is a type error" — the
   previous "Assigning into" does not describe `primes.add(11)`, the first
   of the two lines the sentence explains.
10. Lines 603-604: "The requirement on a dictionary key is hashability, not
    immutability. Immutability is how a container earns a stable hash."
    The previous "A dictionary key must be hashable rather than immutable"
    reads as though the two were alternatives.

## Things checked and found correct

- All four `# type: ignore` comments are still required under `ty` 0.0.65.
  Removing them produces four diagnostics (`unresolved-attribute` on
  `frozenset.add`, `invalid-assignment` on the `MappingProxyType`,
  `frozendict`, and `tuple` subscripts). CLAUDE.md's note about two of
  chapter 3's ignores going unused at `ty` 0.0.63 no longer applies.
- Both timing booleans are stable here. `membership_cost.py` printed `True`
  6 of 6 standalone runs, with measured ratios of 7768, 8354, and 5124
  against its threshold of 100. `deque_timing.py` printed `True` 6 of 6.
  Neither was edited.
- `frozendict` and PEP 814 verified: PEP 814 is Final, accepted 2026-02-11,
  landed in 3.15 as a builtin. `frozendict(theme="dark", zoom=125)` runs,
  hashes, and type-checks on the pinned 3.15.0b2.
- No `def __init__(self` anywhere in the chapter, and no annotations in any
  listing, which matches chapters 2 and 4-7 (static typing starts at
  chapter 8).
