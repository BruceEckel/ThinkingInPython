[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Deep review of `Chapters/10_Cleanup.md`.
Fixes already applied to the chapter (not repeated below):
`del c` prose now says it drops a reference rather than only unbinding a name;
a lead-in paragraph was added to "Reference Cycles Delay Destruction",
which was the only section in the chapter (and one of two in the book)
whose heading was immediately followed by a fenced block;
"runs periodically" became "triggered by allocation counts",
which is what `gc`'s documented threshold rule actually says;
`gc.disable()` is now explained;
the `finalizer.py` paragraph gained the `finalize(self, self.close)` near-miss,
the reconciliation between `del b` here and `del c` in `cleanup.py`,
and the `atexit` backstop; and three small wording fixes
("a candidate for releasing resources", "three more groups of lines",
"In this run" where two runs had just been described).

---

[] Reject

**Section: "Why `__del__()` Is Not Cleanup", the indented output block after
`cleanup.py` (the `Third deleted` / `2 Counter objects remaining` / ... lines).**

This is the most interesting output in the chapter and it is the only output in
the chapter that no gate checks. It is an indented prose block, not a `#:`
marker, so if CPython ever changes the order in which `list_dealloc` drops its
items (it currently walks the array backwards, which is exactly why the direct
run prints `Third, Second, First`), the block goes stale silently and the
paragraph that follows it — "That was one run on one machine" — will be
describing output the reader never sees.

I verified the current text: 5 of 5 standalone runs on Python 3.15.0b2 print
`Third / 2 remaining / Second / 1 remaining / First / Last Counter object
deleted`, and `validate_output.py` prints the same six lines in the opposite
object order. So the text is correct today.

Proposed change: none to the text; add a one-line comment for yourself, or
accept the exposure knowingly. I raise it because the chapter's own thesis is
that this output is unpredictable, which makes an ungated transcript of it a
standing maintenance cost. The alternative — splitting the shutdown output into
its own runnable listing so the gate covers it — cannot work, since the whole
point is that the output arrives after the last statement.

---

[] Reject

**Section: "Why `__del__()` Is Not Cleanup", after the documentation quote.**

The chapter quotes the docs saying exceptions in `__del__()` "are ignored, and a
warning is printed to `sys.stderr` instead", and then never shows it. Of the
three failure modes the chapter names — unpredictable timing, unpredictable
order, precarious shutdown — the swallowed exception is the one that actually
hurts in production, because a resource release that fails leaves no trace on
stdout and no nonzero exit code. It is also the one a reader is least likely to
believe without seeing it.

Proposed addition, a listing after the quote. I verified it: it type-checks,
lints at width 70, exits 0, and passes `validate_output.py` cleanly, including
the block that follows it (the traceback goes to stderr, so the `#:` marker
sees only `still running`).

```python
# del_swallows.py
class Resource:
    def __init__(self, name: str) -> None:
        self.name = name

    def __del__(self) -> None:
        raise RuntimeError(f"{self.name} not released")

resource = Resource("db")
del resource
print("still running")
#: still running
```

Suggested prose: the release failed, the program printed nothing about it on
stdout, and the exit status is still `0`. A traceback goes to `sys.stderr`
labelled "Exception ignored", but nothing propagates: no caller can catch it,
no `finally` runs, and a test asserting on stdout passes. A `close()` call in a
`with` block fails loudly instead.

Placement is your call. It reads naturally as the last beat of the `__del__()`
section, before "Reference Cycles Delay Destruction".

---

[] Reject

**Section: "Reference Cycles Delay Destruction", the paragraph after `cycle.py`.**

`cycle.py` demonstrates that an object with `__del__()` inside a cycle *is*
eventually collected. Many readers carry the pre-3.4 rule, where CPython refused
to finalize any cycle containing a `__del__()` and parked the objects in
`gc.garbage` forever. Those readers will read `a finalized` as a mistake in the
listing.

Proposed addition, one sentence at the end of that paragraph:

> Before Python 3.4 the collector refused to finalize a cycle containing a
> `__del__()` at all and left the objects in `gc.garbage`; PEP 442 removed that
> restriction, so the only thing a cycle costs now is the delay.

I am reporting rather than applying this because the book generally does not
carry version history, so the silence may be deliberate.

---

[] Reject

**Section: "Reliable Alternatives", item 1.**

Item 1 is the approach the chapter recommends. "The Rule" restates it — "Give a
class that owns a resource a `close()` method and a `with` block that calls it"
— and neither place shows one. Items 2 and 3 each get a full listing; item 1
gets three lines of prose and a pointer to chapter 15. The reader finishes the
chapter able to write `weakref.finalize()` and a `WeakValueDictionary` registry,
and unable to point at the thing they were told to do instead.

Proposed addition, a listing under item 1. Verified: passes `ty`, `ruff` at
width 70, and produces exactly the markers shown.

```python
# closable.py
class Socket:
    def __init__(self, name: str) -> None:
        self.name = name
        print(name, "opened")

    def close(self) -> None:
        print(self.name, "closed")

    def __enter__(self) -> Socket:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

with Socket("A") as sock:
    print("using", sock.name)
#: A opened
#: using A
#: A closed
try:
    with Socket("B"):
        raise RuntimeError("boom")
except RuntimeError as e:
    print("caught", e)
#: B opened
#: B closed
#: caught boom
```

Suggested prose: `close()` runs at the end of the `with` block, at a line you
can point at, and the second half shows it running when the body raises. Compare
`cleanup.py`, where the release happened at an unknowable moment after the
program's last statement.

Cost of adding it: it partly duplicates chapter 15, which teaches
`__enter__`/`__exit__` properly and prefers `@contextlib.contextmanager` for a
simple case. Two ways to keep the overlap honest, and I recommend the first:

1. Keep the listing minimal as above and say plainly that
   [Context Managers](15_Context_Managers.md) covers the protocol, the
   `@contextmanager` shorthand, and what `__exit__`'s arguments are for. This
   chapter shows the shape; that one explains it.
2. Drop the second (raising) half, leaving five lines of demo. Cheaper, but it
   loses the "runs even when an error interrupts the code" claim that item 1
   makes in its own text and does not demonstrate.

---

[] Reject

**Section: "Reliable Alternatives", item 2, the `finalize(self, self.close)`
warning I added.**

The prose warning is now there, but the failure is invisible: the object simply
stays alive, and nothing prints to say so. A reader who makes this mistake sees
no error, just a callback that never seems to fire. A listing would show it.

Proposed listing, if you want one:

```python
# finalize_trap.py
import gc
from weakref import finalize, ref

class Leaky:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, self.close)

    def close(self) -> None:
        print(self.name, "closed")

class Safe:
    def __init__(self, name: str) -> None:
        self.name = name
        finalize(self, print, name, "closed")

leaky, safe = ref(Leaky("L")), ref(Safe("S"))
gc.collect()
print(leaky() is None, safe() is None)
```

I am reporting rather than applying because of one wrinkle you should decide on:
`Leaky`'s finalizer has `atexit` true by default, so `L closed` prints when the
interpreter exits — after the block's stdout capture closes. Under
`validate_output.py` that lands in the tool's own terminal output at the very
end of the run, the same class of leak `collect_now()` exists to contain for
`cleanup.py`. It does not fail any gate, but it is noise. Adding
`finalize(self, self.close).atexit = False` suppresses it at the cost of
obscuring the point. If that trade is not worth it, the prose warning alone is
enough and this block should be rejected.

---

[] Reject

**Section: "Reliable Alternatives", item 3 (`weak_value.py`) — chapter
structure.**

Item 3 does not advance the chapter's claim. Items 1 and 2 are ways to release a
resource. A weak reference is not: it is a way to hold a reference without
extending a lifetime. The list that introduces it says "Three approaches are
more reliable", and "The Rule" — which is the chapter's summary — names only
items 1 and 2. Nothing downstream of item 3 depends on it.

Meanwhile it is the chapter's longest listing, carries the chapter's longest
explanatory passage, and owns four of the five exercises. The weight is inverted
against the argument.

It is good material and I would not cut it. Proposed change: promote it out of
the numbered list into its own `##` section after "Reliable Alternatives" —
"Watching Objects Without Holding Them" or similar — with a one-line transition
saying that the same weak-reference machinery behind `finalize()` also solves a
different problem: observing which objects are alive without being the reason
they are. Then add a matching line to "The Rule", something like: to track
objects without owning them, hold them weakly, so the registry cannot become the
leak it is watching for.

Price of the move: nothing breaks. No other chapter links to a heading in
chapter 10 (only `04_Control_Flow.md` and `15_Context_Managers.md` link here, and
both link to the file, not an anchor). `heading_links.py` stays green. The
exercises keep working. The only follow-on is that "Three approaches are more
reliable" becomes "Two approaches are more reliable", and item 3's numbering
disappears.

---

[] Reject

**Section: "Reliable Alternatives", item 3, the paragraph beginning "The key is
`id(self)`".**

Two sentences later the chapter says "When the values need no key at all,
`weakref.WeakSet` is the simpler container." But `weak_value.py` needs no key at
all: `live_count()` is `len()`, and nothing in the listing ever looks an
instance up. So the paragraph spends three sentences defending `id(self)` as a
key, and then tells the reader that the listing did not need a key. A reader who
follows the argument ends up asking why the listing is not a `WeakSet`.

The dict is still the right choice, for a reason the chapter does not give:
`WeakValueDictionary` is what you want the moment you look instances up rather
than count them, which is what exercise 3 does with `.values()` and what
chapter 35's `weak_pool.py` does with a real key. Recommendation is to say that
instead of leaving the `WeakSet` line as an unanswered aside:

> A `WeakSet` would do for counting alone. The dictionary is what you want as
> soon as you look instances up rather than count them, which is what
> [Flyweight](35_Flyweight.md) does with a pool keyed by name. `id(self)` is the
> key here because the registry needs one entry per object, not per name: two
> counters could share a name, and one would displace the other.

The alternative — rewriting the listing as a `WeakSet` — costs more than it
saves: exercises 1, 3, and 5 and all five files in `SolutionsCode/10_Cleanup/`
are written against the dictionary form.

---

[] Reject

**Section: "Exercises".**

Four of the five exercises target `weak_value.py`, which by the argument above
is the chapter's least load-bearing listing. One targets `cleanup.py`. Nothing
targets `cycle.py` or `finalizer.py`, and `finalizer.py` is the listing behind
half of "The Rule". A reader who does every exercise has never written a
`finalize()` call.

Exercises 1 and 2 also overlap heavily: both replace the container holding the
strong references and both confirm the count still reaches `0`. Exercise 2 earns
its place on the `clear()`-versus-rebind distinction; exercise 1 adds little
beyond it.

Proposed change: drop exercise 1 and add two, keeping the set at five (or six if
you keep exercise 1):

> In `finalizer.py`, change the `finalize()` call to `finalize(self, self.close)`
> and run the file again. Report when `B closed` now prints relative to
> `End of program`, and say what keeps the `Connection` alive.

> In `cycle.py`, change `self_link()` to build a two-object cycle (`a.peer = b`
> and `b.peer = a`) instead of a self-reference. Confirm both finalizers run at
> `gc.collect()`, then remove the `gc.disable()`/`gc.enable()` pair and explain
> why the output is no longer predictable.

Both need entries in `Solutions/10_Cleanup.md` and `SolutionsCode/10_Cleanup/`,
which I did not touch.

---

[] Reject

**`Solutions/10_Cleanup.md`, exercise 4 (`exercise_4.py`) — out of my edit
scope, reported here.**

The chapter's exercise 4 says "confirm the output is unchanged". The solution's
`Counter.__del__` is not the chapter's: it drops the
`if Counter.count == 0: ... else: ...` branch and prints only `self.name,
"deleted"`. The shutdown output of `exercise_4.py` therefore differs from
`cleanup.py`'s in exactly the lines the chapter's prose block spells out, which
is the opposite of what the exercise asked the reader to confirm. The `#:`
markers stop at `End of delete loop`, so no gate notices.

Proposed change: restore the two dropped lines in `exercise_4.py`'s `__del__`
so the class matches `cleanup.py` exactly, since the exercise is about the
comprehension and nothing else.

While there, exercise 1's wording says "pop entries from that `dict` one at a
time" and `exercise_1.py` uses `del counters["Third"]`. Either is fine; make the
exercise say "remove entries" so the two agree.

---

## Cross-chapter

**`Chapters/35_Flyweight.md`, section "A Pool That Does Not Leak".**

`weak_pool.py` introduces `weakref.WeakValueDictionary` as though for the first
time — "`weakref.WeakValueDictionary` fixes this. It holds its values weakly, so
an entry disappears as soon as no one else uses the object" — but chapter 10
already teaches exactly that, with the same container and the same
reference-counting explanation ("The immediate drop in the count is CPython's
reference counting at work"). Chapter 35 does not link back, and chapter 10 does
not point forward.

Exact change I would make in chapter 35, in the sentence introducing the
container:

> `weakref.WeakValueDictionary`, introduced in
> [Cleanup](10_Cleanup.md#reliable-alternatives), fixes this.

If the item-3 promotion above is applied, the anchor becomes the new section's
slug instead. I made no edit in chapter 35.
