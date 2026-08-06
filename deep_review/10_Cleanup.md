[[Reviewed]]
# Deep review: 10_Cleanup.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Weak references are not a cleanup mechanism: add `weakref.finalize()`

**Kind:** teaching, code
**Where:** "Two approaches are more reliable:" (line ~105) and the `weak_value.py` listing that follows

**Problem:** The numbered list promises two ways to release a resource more reliably than `__del__()`. The first (an explicit `close()` called from a `with` block) is one. The second is not: a `WeakValueDictionary` releases nothing. It observes liveness. A reader who owns a socket and reads "two approaches are more reliable" will look at `weak_value.py` and be unable to see how it closes anything, because it doesn't. The mechanism the chapter is missing is `weakref.finalize()`, which the CPython documentation names directly as the alternative right below the warning the chapter quotes: "`weakref.finalize` provides a straightforward way to register a cleanup function to be called when an object is garbage collected." It is strictly better than `__del__()` for the same job: the callback holds no reference to the object, it can be invoked early and by hand, it is idempotent, and it runs at interpreter exit by default instead of maybe running.

**Proposal:** Make the list three items, and give the new second item a listing. Reword the framing so the weakref registry is presented as what it is (observing lifetime without extending it) rather than as a cleanup mechanism.

Replacement for the list intro and item 2, keeping item 1's text as it stands (only the count in the intro line changes):

> Three approaches are more reliable:
>
> 1\. An explicit finalizer such as the `close()` that file objects provide, called from a `with` block. This runs even when an error interrupts the code. `[Context Managers](15_Context_Managers.md)` covers `with` in full.
>
> 2\. `weakref.finalize()`, which registers a cleanup callback for an object without giving that callback a reference to the object:

```python
# finalizer.py
from weakref import finalize

class Connection:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")
        self.closer = finalize(self, print, name, "closed")

    def close(self) -> None:
        self.closer()

a = Connection("A")
#: A opened
b = Connection("B")
#: B opened
a.close()
#: A closed
a.close()
print(a.closer.alive, b.closer.alive)
#: False True
del b
#: B closed
print("End of program")
#: End of program
```

Prose to follow the listing (draft):

```
`finalize()` registers `print(name, "closed")` to run when `a` is destroyed.
The callback receives `name`, not the `Connection`,
so registering the cleanup does not keep the object alive.
`close()` runs the callback immediately.
The second `close()` does nothing:
a finalizer runs at most once, and `alive` reports whether it still can.
When `b` goes away without anyone calling `close()`,
the callback still runs,
and it runs before interpreter shutdown rather than during it.
```

Then item 3 introduces the existing `WeakValueDictionary` listing, reworded as "a weak reference, which tracks an object without keeping it alive" (the current item 2 text stands as-is once it is numbered 3).

I verified the listing's output and markers on the pinned interpreter, and it type-checks.

Alternative, if a new listing is too much for the shortest chapter in the book: keep two items and reword item 2 to say what weak references give you, dropping the implication that they release resources, then name `weakref.finalize()` in one sentence with a pointer to the docs.

**Cost:** One new example file, so the usual sync/gate loop. Nothing else in the book uses `weakref.finalize()`, so no cross-references move. The `weak_value.py` listing and its prose are untouched apart from the item number. Chapter 35's Flyweight pool still relies on this chapter having introduced `WeakValueDictionary`, which it still does.

---

## 2. The chapter never mentions reference cycles, the real reason `__del__()` surprises people

**Kind:** teaching
**Where:** the paragraphs on unpredictable timing (lines ~57 to ~78)

**Problem:** The chapter's argument against `__del__()` rests on shutdown ordering and on other implementations. Both are real, but neither is what a reader hits first. In CPython, an object caught in a reference cycle has a nonzero reference count with nothing reachable to it, so it is not freed when the last outside reference goes away. It waits for the cyclic collector, which runs on its own schedule. A file wrapper that closes in `__del__()` and happens to hold a back-reference stays open indefinitely, on CPython, with no shutdown involved. Since the chapter is about when destruction happens, leaving out the one CPython mechanism that delays it is a gap, and it is also what makes the opening sentence about destruction honest (see "Already fixed" below).

**Proposal:** Add a short section after the docs warning, before "Two approaches are more reliable", with this listing:

```python
# cycle.py
import gc

class Node:
    peer: Node

    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        print(self.name, "finalized")

def self_link() -> None:
    node = Node("a")
    node.peer = node

gc.disable()
self_link()
print("unreachable, but still alive")
#: unreachable, but still alive
gc.collect()
#: a finalized
gc.enable()
print("after collect")
#: after collect
```

Prose (draft):

```
CPython frees most objects by counting references:
when the last reference to an object goes away, the object goes with it.
A reference cycle defeats that count.
`self_link()` returns and its local `node` disappears,
but the object still refers to itself, so its count never reaches zero.
Freeing it takes the cyclic garbage collector, a separate mechanism that
runs periodically rather than at the moment the object becomes unreachable.
`gc.collect()` above forces a run so the timing is visible;
in a real program nothing tells you when it happens.
This is a second reason not to put cleanup in `__del__()`:
one back-reference between two objects is enough to postpone it,
and the code that creates the cycle is often not the code that owns the resource.
```

**Cost:** One new example file. The `gc.disable()`/`gc.enable()` pair is deliberate and needs to stay: `validate_output.py` runs every chapter's blocks in one process, where an automatic gen-0 collection could fire between `self_link()` and the print and finalize the node early, flipping the marker. Disabling around the demo and re-enabling immediately keeps that contained. This is the same family as the `__del__()`-leaking-across-chapters trap already in `CLAUDE.md`. If the pair is unwanted, the demo still works standalone but becomes a flaky-marker risk in the whole-tree run.

---

## 3. Show the shutdown output instead of telling the reader to go find it

**Kind:** teaching
**Where:** "Run `python cleanup.py` directly to see those lines appear." (line ~64)

**Problem:** The whole point of `cleanup.py` is that the `deleted` lines print after the last statement of the program. The listing's markers stop before them, and the prose explains why, but the reader is then sent away to run the file to see the thing the section is about. A reader on a train sees the explanation of an output they never see.

**Proposal:** Follow that sentence with an unfenced-from-extraction output block (no `# path.py` first line, so nothing is extracted) showing the trailing lines, plus one sentence that the order is not fixed:

```
Run `cleanup.py` directly and three more groups of lines follow the last one above:

    Third deleted
    2 Counter objects remaining
    Second deleted
    1 Counter objects remaining
    First deleted
    Last Counter object deleted

That was one run on one machine.
Running the same file under this book's output checker,
which executes every chapter in a single process,
finalizes the three objects in the opposite order.
```

The two orders are real: standalone the objects finalized Third, Second, First on this machine, and under `validate_output.py` they finalized First, Second, Third. That contrast is better evidence for the unstable-order claim than the assertion alone, and it costs three lines.

Alternative: show the six lines with no commentary and leave the ordering claim where it is, if pointing at the book's own tooling inside a chapter is unwanted.

**Cost:** none. An indented block is not an extractable listing and carries no markers.

---

## 4. Exercise 2 asks the reader to justify something that is only true here

**Kind:** exercise
**Where:** "## Exercises", item 2 (line ~174)

**Problem:** The exercise says "Explain, in terms of the object to which `counters` refers, why rebinding has the same effect as clearing." Rebinding and clearing do not have the same effect in general. `clear()` empties the one list every reference can see; `counters = []` drops this name's reference and leaves the old list intact for anyone else holding it. They coincide in `weak_value.py` only because that list has exactly one reference. As worded, a reader who answers correctly has learned a false rule, and the chapter has just spent a page teaching that reference counts are the thing to think about.

**Proposal:** Reword to make the difference the point:

```
2.  In `weak_value.py`, replace the final `counters.clear()` with `counters = []`
    (rebinding the name) and confirm `live_count()` still reaches `0`.
    The two do different things to the list object.
    Say what each one does, then say what a second name bound to the same list
    would see after each.
```

**Cost:** none.

---

## 5. Four sentences make the same "no guarantee" point

**Kind:** prose
**Where:** lines ~66 to ~78

**Problem:** In thirteen lines the chapter says the timing is not guaranteed four times: "an unstable implementation detail", "not a guarantee", "The language does not specify when, or in what order", and "fragile because Python does not guarantee the timing". The repetition reads as insistence rather than explanation, and the one genuinely new fact in the passage (globals may be gone) arrives last, behind three restatements.

**Proposal:** Condense to two paragraphs:

```
The order in which the three finalizers run is an implementation detail.
It depends on how the interpreter tears down the `counters` list at shutdown,
and it can differ from one CPython build to the next.
Another implementation, such as PyPy with a tracing garbage collector,
could destroy the objects in a different order,
or not run the finalizers before exiting.

So `__del__()` is fragile: the language specifies neither when it runs nor whether it runs at all.
At interpreter shutdown,
the globals a `__del__()` method refers to may already be gone.
The Python documentation warns:
```

**Cost:** none. The docs quote follows unchanged.

---

## 6. `id(self)` as the registry key is unexplained

**Kind:** teaching
**Where:** `weak_value.py`, `self._instances[id(self)] = self` (line ~127)

**Problem:** A reader meeting `WeakValueDictionary` for the first time also meets `id()` used as a key, with no word about why. The obvious question ("why not key by name?") has a real answer, and the other obvious worry ("`id()` values get reused") has one too. Chapter 35 later keys a `WeakValueDictionary` by a meaningful string, so a reader who saw only `id(self)` here has the wrong mental model of what the key is for.

**Proposal:** Add two sentences after "Storing each instance in a `WeakValueDictionary` tracks it without keeping it alive.":

```
The key is `id(self)` because the registry needs a key per object, not per name:
two counters could share a name, and one would then displace the other.
Reused `id()` values are not a hazard here,
since the dictionary only ever holds live objects and no two live objects share an id.
When the values need no key at all, `weakref.WeakSet` is the simpler container.
```

**Cost:** none, unless exercise 3 (`live_names()` reading `_instances.values()`) is later rewritten around a `WeakSet`, in which case the last sentence should go.

---

## 7. The chapter closes on a warning, never on what to do

**Kind:** structure
**Where:** end of the chapter, before "## Exercises" (line ~168)

**Problem:** Reading front to back, the reader is told at length what not to do, then shown a registry that counts objects, and then hits the exercises. The capability they gained is hard to name. The one thing they came for, what to write when a class owns a file or a socket, is a forward pointer to chapter 15 and never a rule stated in this chapter.

**Proposal:** Two or three sentences of close, titled for their content rather than "Summary" (per the book's convention):

```
## The Rule

Never put resource release in `__del__()`.
Give a class that owns a resource a `close()` method and a `with` block that calls it,
so the release happens at a point in the program you can see.
Where a callback must still run if the caller forgets,
add `weakref.finalize()` as the backstop, not as the plan.
```

The last sentence assumes proposal 1. Drop it if that one is rejected.

**Cost:** none. Chapter 15 opens by referring back to this chapter's `__del__()` argument, and this close sets that up rather than duplicating it.

---

## 8. The chapter has no headings

**Kind:** structure
**Where:** whole chapter

**Problem:** At 182 lines this is the shortest chapter in the book, and the only `##` in it is "Exercises". Its neighbors (9 and 11) both break into named sections. The site build gives the chapter no navigation, and a reader scanning for "how do I do this properly" has nowhere to land.

**Proposal:** Three headings over the existing text, changing no prose:

- `## Why __del__() Is Not Cleanup` before the `cleanup.py` listing (with an explicit `{#why-del-is-not-cleanup}` id, since the auto-slug of `__del__()` is ugly)
- `## Reliable Alternatives` at "Two approaches are more reliable:"
- plus whatever proposals 1, 2 and 7 add

**Cost:** `heading_links.py` gates the anchors, so the explicit id matters. No other chapter links into this one by anchor (chapters 4 and 15 link to the file), so adding headings breaks nothing.

---

## 9. Add an exercise that makes the reader watch the leak

**Kind:** exercise
**Where:** "## Exercises"

**Problem:** The chapter asserts that a `dict` or `list` registry "keeps every instance alive forever, so the count can never fall", which is the claim that justifies the whole `WeakValueDictionary` listing, and no exercise has the reader confirm it. Exercise 4 in its place asks for a list comprehension and a confirmation that nothing changed, which tests the least of the chapter's claims.

**Proposal:** Add:

```
5.  In `weak_value.py`, change `_instances` from a `WeakValueDictionary` to a
    `dict[int, Counter]` and run the file again.
    Report what `live_count()` prints after each `pop()`, and explain the difference
    in terms of what each container holds.
```

Recommended as an addition rather than a replacement for exercise 4, which is cheap and does confirm that the comprehension's result is still referenced.

**Cost:** none.

---

## 10. Small prose nits

**Kind:** prose
**Where:** scattered

**Problem/Proposal:** each is one word or one sentence, take or leave individually.

- line ~4: "when an object owns an outside resource" reads oddly; "an external resource" is the usual term and is what chapter 4 and chapter 15 both effectively describe.
- line ~52: "The `counters` list still references each `Counter`, so its reference count never reaches zero" has a pronoun with two candidates (the list, or each `Counter`). Suggest "so no `Counter`'s reference count reaches zero during the loop".
- lines ~53 and ~61: "That is why no `deleted` lines appear while the loop runs" and "That is why the `deleted` lines are missing from the output above" land two sentences apart and say nearly the same thing. Cut the second; the paragraph it opens already explains the shutdown timing.
- line ~66: "an unstable implementation detail" says the order changes; "an unspecified implementation detail" says the language never promised one, which is the argument being made.
- line ~99: "In this run the deletions happen during shutdown" uses "happen" from the watch list; "the objects are destroyed during shutdown" says it directly.
- line ~160: "A plain `dict` or `list` as the registry" uses "plain" as filler. Here it does draw a contrast with the weak container, so it is a judgment call; "An ordinary `dict` or `list`" or just "A `dict` or `list`" both read the same.
- line ~172, exercise 1: "to a plain `dict` keyed by name" is the same word with no contrast behind it. Drop it.

**Cost:** none.

---

## Already fixed directly (no decision needed)

- line ~6: "The Python garbage collector calls an object's `__del__()` method when it collects that object" became "Python calls an object's `__del__()` method when it destroys that object." In CPython an object with a zero reference count is destroyed by the reference count reaching zero, not by the garbage collector, which in Python names the separate cyclic collector in the `gc` module. The original sentence also contradicted the chapter's own later prose, which calls the timing "a reference-counting detail" and describes a tracing collector as what other implementations have.

## Verified clean (no action)

- `cleanup.py` and `weak_value.py` both run, and every `#:` marker matches real stdout. `ty`, `ruff`, and the anchor-link gate all pass over the chapter, and `banned_phrases.py` reports nothing.
- The quoted `__del__()` warning matches the current CPython documentation word for word.
- The one cross-reference, `[Context Managers](15_Context_Managers.md)`, points at the right chapter, and the chapter uses no relative "previous chapter" phrasing that a future split could break.
- Both listings follow the house style: no `__init__` that a dataclass would generate (`Counter` prints on construction), constants annotated `ClassVar`, top-level demo code, one blank line maximum, and no line over 70 characters.
