[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Fixes already applied to `Chapters/30_Observer.md` (not listed as findings):

- "This chapter shows the Pythonic version first" -> "The rest of the chapter
  shows the Pythonic version first", since the classic version is literally
  what was shown first, two paragraphs above.
- "...is a type error instead of a list of strings quietly collecting floats"
  -> "...fails the checker instead of quietly collecting floats in a list of
  strings." The original compared a type error to a list; both halves now
  describe the same subscription. Verified with `ty`: subscribing
  `list[str].append` to a `Thermometer` reports `Expected Observer[int |
  float], found bound method list[str].append`.
- "Writing `t.update` twice" -> "Writing `obj.update` twice". `t` is the
  `Thermometer` everywhere else in the chapter and has no `update()`.
- Added, after the bound-method sentence: "`unsubscribe()` delegates to
  `list.remove()`, so detaching an observer that never subscribed raises
  `ValueError`, and subscribing the same callable twice means two
  notifications and two `unsubscribe()` calls to stop them." Both behaviors
  verified by running the extracted `observers.py`.

---

[] Reject

**"The Pythonic Observer": re-entrant notification is never mentioned.**

The chapter covers three ways a naive `notify()` goes wrong -- an observer
detaching mid-loop, an observer raising, and the lapsed-listener leak -- but
not the fourth and most common one: an observer that writes back to the
observable. `t.celsius = c + 1` inside a subscriber re-enters `notify()` from
inside `notify()` and recurses until the stack limit. This matters more here
than in most chapters because the closing line of the visual section invites
exactly the setup that triggers it: "You can also attach a second view to the
same model and keep both in step." A two-way binding (view edits model, model
notifies view, view edits model) is where readers meet this.

Proposed: extend the "Two more things about Observer need saying" paragraph to
three, or add a short paragraph after it:

> An observer that writes back to the observable re-enters `notify()` from
> inside `notify()`. Two-way bindings are the usual source: the view edits the
> model, the model notifies the view, the view edits the model. Either make
> the write conditional on the value actually changing, or guard the setter
> with a re-entry flag.

I did not apply this because it turns a "two more things" paragraph into three
and adds a third caveat to a section that already carries two, which is a
pacing call. The alternative placement is the paragraph after `box_view.py`,
next to the sentence about a second view, where it is more concrete but
arrives long after the reader could have used it.

---

[] Reject

**Opening, `classic_observer.py`: `_changed` is cleared after the loop, not
before it.**

```python
def notify_observers(self, arg: object = None) -> None:
    if not self._changed:
        return
    for observer in list(self._observers):
        observer(self, arg)
    self._changed = False
```

An observer that calls `source.set_changed()` while being notified has that
flag silently wiped when the loop ends. `java.util.Observable`, which this
listing is paraphrasing, clears the flag before it dispatches, precisely so a
change raised during notification survives.

Proposed: move `self._changed = False` above the `for` loop. It is a two-line
move, it makes the listing match the design it is presenting, and nothing in
the chapter depends on the current placement (the `#: display: 25C` marker is
unaffected).

Low priority: the listing is a straw man that the next section dismantles. But
it is presented as "the classic design", so it should be the classic design.

---

[] Reject

**"Observer and I/O": the async `Observable` drops both the `list()` copy and
`unsubscribe()`, one paragraph after the chapter insisted on them.**

The synchronous section spends a full paragraph on why `notify()` copies
(`"The list() copy inside notify() looks redundant. It is not."`) plus a whole
listing, `self_removing_observer.py`, proving it. Then:

```python
async def notify(self, data: float) -> None:
    await asyncio.gather(*(obs(data) for obs in self._observers))
```

No copy, and the class has no `unsubscribe()` at all. Both are defensible --
`*` materializes the generator into a tuple before `gather()` is called, so
the iteration itself is safe, and with no `unsubscribe()` the question never
comes up -- but a reader who just finished that paragraph will read the
omission as an oversight, or worse, copy it into a version that does have
`unsubscribe()`.

Proposed: one sentence after the listing:

> `notify()` needs no `list()` copy here: `*` drains the generator into a
> tuple before `gather()` runs, so a detach during the fan-out cannot skip
> anyone. It does mean an observer that unsubscribes mid-notification is still
> awaited for this change.

Alternative, if you would rather keep the async listing minimal: add
`unsubscribe()` to the async `Observable` for symmetry and let the sentence
above explain the difference. I recommend the sentence alone; adding the
method costs three lines that no listing exercises.

---

[] Reject

**Exercises: nothing exercises the async section.**

Exercise 1 covers the minimal Observer/Observable, 2 covers the box model, 3
covers the exception gap the prose explicitly flags. "Observer and I/O" is one
of the chapter's three sections and has no exercise, even though the prose
hands one over ready-made: "`gather(*coros, return_exceptions=True)` returns
the failures as data instead, which is the async form of the
catch-collect-continue that exercise 3 asks for."

Proposed exercise 4:

> 4.  Redo exercise 3 for `async_observers.py`. Make `notify()` use
>     `gather(*coros, return_exceptions=True)`, separate the returned
>     exceptions from the successes, and raise them together as an
>     `ExceptionGroup`. Write a test in which the first observer raises and
>     the second still records its notification.

This makes the sync and async halves answer the same question, which is the
chapter's thesis ("One `Observable` served three jobs"), and it needs a
solution written for `Solutions/30_Observer.md`, which is the cost.

---

[] Reject

**Opening, `classic_observer.py`: the `changed` flag is dismissed without ever
saying what it buys.**

The listing shows `set_changed()` / `notify_observers()` as "a two-phase
notification", and later the Pythonic section counts "the `changed` flag" and
"the two-phase `set_changed()` then `notify_observers()`" among the four things
that are gone. But in the demo `set_celsius()` calls both back to back, so the
flag does nothing observable and the reader cannot tell what was discarded.
The flag exists to coalesce several mutations into one notification (change
three fields, then broadcast once) and to let a subclass decide that a change
is not worth announcing.

Proposed: one sentence after the classic listing, before "Python expresses
this with far less machinery":

> The flag lets several mutations coalesce into one broadcast, and lets a
> subclass decide a change is not worth announcing; `set_celsius()` calls both
> halves at once, so nothing here needs it.

Without this the "four things gone" list reads as pure subtraction, and a
reader who later needs batched notification will not know the classic design
had an answer for it.

---

[] Reject

**"The Pythonic Observer": the `source` argument disappears and is not
counted.**

The classic `update(self, source: Observable, arg: object)` hands the observer
both the payload and the object that changed. The Pythonic `Observer[T]` takes
only the payload. The prose lists "four things from the classic version are
gone" -- interface, flag, two-phase notify, class per reaction -- and all four
are pure wins. The fifth removal is not: an observer subscribed to two
thermometers can no longer tell which one fired.

Proposed: add after the four-things sentence:

> The `source` argument went too. An observer that needs to know who changed
> takes it as part of the payload (`notify((self, value))`) or subscribes a
> bound method whose instance already holds the reference.

This closes the most likely reader question at the exact point it arises,
instead of leaving the impression that the classic signature carried nothing
the Pythonic one lacks.

---

[] Reject

**"Observer and I/O": `AsyncObserver` is not generic while `Observer[T]` is.**

```python
type Observer[T] = Callable[[T], None]           # sync
type AsyncObserver = Callable[[float], Awaitable[None]]   # async
```

The sync section makes a point of the type parameter ("carries the
notification's type through to the observers"), then the async section
hard-codes `float` with no comment. `type AsyncObserver[T] = Callable[[T],
Awaitable[None]]` plus `class Observable[T]` costs nothing and keeps the two
halves parallel; the chapter's own argument for the parameter applies
identically.

If the narrowing is deliberate -- keeping the async listing as short as
possible so `gather()` is the only new idea -- say so in half a sentence,
because as written it looks like the generic version was forgotten.

---

[] Reject

**"Observer and I/O": `gather()` completion order vs. result order is the
near-miss here.**

"The `alarm` is slower than the log, yet the log prints first. [...] Concurrent
fan-out lets each finish on its own schedule, so the faster observer reports
first." That is right about side-effect order, and a reader will generalize it
to the return value. `gather()` returns its results in argument order, not
completion order. Nothing here reads the results, so no listing is wrong, but
the reader who moves this shape to observers that return something will get it
backwards.

Proposed: append to that paragraph:

> The results `gather()` hands back stay in argument order regardless; only
> the side effects interleave.

Low priority, one clause.

---

[] Reject

**"A Visual Example of Observers": the `cell_px` naming sentence.**

> `cell_px` is named for what it holds: the model's `cell` is a `Coord`,
> and this one is a pixel count.

This defends a naming choice the reader did not question, and the sentence
itself needs a second reading ("named for what it holds" followed by a
contrast with a different name). Proposed: cut it. The paragraph then ends on
the canvas-clearing point, which is the one that teaches something.

If you want to keep the model/view vocabulary separation explicit, the place
for it is the sentence introducing the two files, not a postscript after the
listing.

## Cross-chapter

None. Every outbound link was checked against its target and is consistent:
19's `gather()`-vs-`TaskGroup` guidance (30 cites it and states why it
deviates), 28's event bus (30 cites it twice as the same fan-out keyed by
type), 44's Thermometer exercise, 41's lapsed-listener reference, and 39's
catalog rows. `heading_links.py` passes and `tools/data/norun.txt` still lists
`30_Observer/box_view.py`.
