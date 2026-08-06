[[Reviewed]]
# Deep review: 30_Observer.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Make `Observable` generic instead of `Callable[[Any], None]`

**Kind:** code
**Where:** listing `observers.py` (line ~38), plus `test_observers.py`, `self_removing_observer.py`, `box_observer.py`
**Problem:** `type Observer = Callable[[Any], None]` turns off type checking on the one connection the chapter is about. I confirmed against the built tree that this file type-checks clean today:

```python
from observers import Thermometer
names: list[str] = []
t = Thermometer()
t.subscribe(names.append)   # ty: "All checks passed!"
t.celsius = 25.0            # Appends a float into a list[str]
```

A reader who copies this `Observable` into their own code inherits an untyped subscribe. The book's own rule (`thinking-in-python-skill.md`, "Use type parameters when a function or wrapper should carry the element type through") points the other way, and the chapter never says why the `Any` is here, so it reads as an oversight rather than a lesson. The `Any` is not gratuitous: with `Callable[[object], None]`, contravariance would reject `readings.append` where `readings: list[float]`, so a plain non-generic tightening does not work. A type parameter does.

**Proposal:** parameterize `Observable`:

```python
# observers.py
from collections.abc import Callable

type Observer[T] = Callable[[T], None]

class Observable[T]:
    def __init__(self) -> None:
        self._observers: list[Observer[T]] = []

    def subscribe(self, observer: Observer[T]) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: Observer[T]) -> None:
        self._observers.remove(observer)

    def notify(self, data: T) -> None:
        # Copy: observers may detach during notification
        for observer in list(self._observers):
            observer(data)

class Thermometer(Observable[float]):
    ...            # Unchanged
```

The `from typing import Any` import goes away. Downstream, `class BoxModel(Observable[Grid])`, `obs = Observable[object]()` in `self_removing_observer.py`, and `Observable[int]()` / `Observable[str]()` / `Observable[object]()` at the three bare `Observable()` calls in `test_observers.py`. Nothing else changes: no test body, no assertion, no `#:` marker.

I built the whole set in a scratch tree and ran it: `ty check` passes, the 5 tests pass, `self_removing_observer.py` still prints `['once: 1', 'always: 1', 'always: 2']`, and `thermometer.py` output is unchanged. The `names.append` case above now fails with `Expected Observer[int | float], found bound method list[str].append`.

One sentence of prose after the listing pays for the syntax, e.g.:

> The type parameter carries the notification's type through to the observers,
> so subscribing a `list[str].append` to a `Thermometer` is a type error
> instead of a list of strings quietly collecting floats.

**Cost:** four listings change, though only their type annotations. The chapter is the first place in Part IV where a PEP 695 generic class appears in a pattern listing, so it adds one construct to decode; the sentence above is what keeps that from being a distraction. Nothing outside the chapter imports `observers.py` (`Solutions/30_Observer.md` defines its own `Observable` from scratch), so no cross-chapter breakage.

**Alternative:** leave the `Any` and add a sentence saying what it costs, so the deviation is deliberate rather than silent. Cheaper, but it leaves the reader with the weaker code to copy.

---

## 2. Show the classic Observer, or stop claiming it

**Kind:** structure
**Where:** opening (line ~24) and section "The Pythonic Observer: a List of Callables"
**Problem:** the opening states "Python expresses this with far less machinery than the classic design" and then says the chapter "shows the Pythonic version first". Neither is cashed in. The classic design never appears, and nothing follows the "first". A reader who has not written an `Observer` interface in Java or C++ has no idea what was saved, so the chapter's central claim arrives as an assertion. This also breaks the convention the neighboring pattern chapters keep: 28 pairs `command.py` with `command_pattern.py` and `strategy.py` with `strategy_pattern.py`, and 33 opens with the full `accept()`/`visit()` machinery before "The Pythonic Visitor: singledispatch".

**Proposal:** add a short classic listing before `observers.py`, in the shape 28 and 33 use: an `Observer` ABC with an abstract `update()`, an `Observable` base carrying a `_changed` flag with `set_changed()`/`notify_observers()`, and one concrete observer class. Keep it minimal, then let the Pythonic version land as a subtraction, with the "far less machinery" sentence moved to sit right after it and name what disappeared: the interface, the flag, the two-phase `set_changed()` then `notify()`, and the observer class per reaction.

**Cost:** roughly 30 lines of listing plus a short paragraph in a chapter that is already the length of its neighbors. It also needs an `#:` marker and a file slug, so it goes through the full verify loop. The opening's "shows the Pythonic version first" then becomes accurate rather than dangling.

**Alternative (cheap):** no listing. Replace "Python expresses this with far less machinery than the classic design" with two sentences naming the machinery in prose (the `Observer` interface every observer must implement, the `changed` flag, the fixed `update()` signature), and change "shows the Pythonic version first, then extends it" to drop the "first". This fixes the dangling promise without growing the chapter.

---

## 3. Say what happens when an async observer raises an exception

**Kind:** teaching
**Where:** section "Observer and I/O", after the `async_observers.py` listing (line ~276)
**Problem:** the synchronous section gives failure a full paragraph ("An observer that raises an exception stops the loop, and every observer after it never hears the change") and hands the reader exercise 3. The async section says nothing, even though the behavior is different and worse: `asyncio.gather()` without `return_exceptions=True` re-raises the first exception into `set_celsius()` immediately, while the other observer coroutines keep running unsupervised. The state change reports failure with notifications still in flight. That is the async analogue of the sync trap and it is the question the previous section trained the reader to ask.

Relatedly, the house rule in `thinking-in-python-skill.md` is "prefer `asyncio.TaskGroup` over `asyncio.gather()`", and this listing uses `gather()` with no stated reason. For a notification fan-out the choice is right (a `TaskGroup` cancels its siblings on the first failure, so one broken observer would stop the others from hearing the change at all, which is the opposite of what Observer wants), but saying so is what turns an apparent deviation into the lesson.

**Proposal:** three or four sentences after "The alarm also shows an observer that can decline to act. Below its threshold it returns without sending anything.":

> A failing observer behaves differently here than in the synchronous version.
> `gather()` re-raises the first exception into `set_celsius()` right away,
> and the observers that have not finished keep running with nobody awaiting them.
> `gather(*coros, return_exceptions=True)` returns the failures as data instead,
> which is the async form of the catch-collect-continue that exercise 3 asks for.
> [Concurrency](19_Concurrency.md#structured-concurrency-with-taskgroup)'s `TaskGroup`
> is the usual choice for concurrent awaits, but not here:
> it cancels its siblings when one task fails,
> so a single broken observer would stop the rest from hearing the change.

**Cost:** no code change, so no marker churn. It adds a fourth paragraph to a section that currently has three. Chapter 19 line ~556 points at this section and describes it as using `gather()`, so the `gather()` call must stay; this proposal keeps it.

---

## 4. Finish the unsubscribe story: bound methods compare equal

**Kind:** teaching
**Where:** paragraph before `test_observers.py` (line ~108), and the `record = received.append` comment inside it
**Problem:** the chapter told the reader that removal is by identity, which is wrong; I corrected that clause directly (see the bottom of this file). The correction leaves the more useful half unsaid. `list.remove()` matches with `==`, and equality is different for the two kinds of observer the chapter uses side by side:

```
xs.append is xs.append   -> False
xs.append == xs.append   -> True    # Bound methods: same instance, same function
(lambda v: None) == (lambda v: None) -> False
```

So a bound-method observer detaches without being stashed anywhere, while a lambda can never be detached because nothing will ever compare equal to it. The listing's own comment, `record = received.append  # Named so it can be removed`, states the opposite of what is true for `received.append` specifically: `obs.unsubscribe(received.append)` works fine. This is a lookalike pair (function vs. bound method as observer) the chapter uses but does not distinguish, and line ~91 already sets it up with "The observers here are lambdas, but any function or bound method works."

**Proposal:** extend the corrected sentence with the bound-method case, and retarget the comment:

> `unsubscribe()` matches by equality, and a lambda equals only itself,
> so a detachable observer needs a named reference,
> not an inline lambda.
> A bound method is the exception.
> Writing `t.update` twice builds two objects that are not identical but do compare equal,
> since they share an instance and a function,
> so a bound-method observer detaches without being stashed.

and change the comment to `# A bound method: equal, not identical`.

**Cost:** one comment inside `test_observers.py` and three added prose lines. The `weakref.WeakMethod` sentence at line ~196 gets more force, since it is the same fact (a bound method is a fresh object each time you name it) seen from the lifetime side.

---

## 5. `Solutions/30_Observer.md` is one exercise out of step (report only, not edited)

**Kind:** exercise
**Where:** `Solutions/30_Observer.md`, not this chapter
**Problem:** the first deep-review pass (commit `e95de85`) deleted the class-decorator exercise, renumbered the rest, and added the new `ExceptionGroup` exercise 3, but the solutions file was not renumbered with it. As it stands:

- Solutions #1, "A class decorator that traces every method", answers an exercise that no longer exists anywhere in the book. `trace_all` appears in no chapter; I grepped `Chapters/` and `Solutions/` for it.
- Solutions #2 answers chapter exercise 1.
- Solutions #3 answers chapter exercise 2.
- Chapter exercise 3 (`notify()` surviving a raising observer, re-raised as an `ExceptionGroup`) has no solution.

**Proposal:** delete solution #1 or move it to whichever chapter should now own that exercise, renumber #2 and #3 to 1 and 2, and write a solution for the new exercise 3. I did not touch the file: it is outside the edit scope for this review.

**Cost:** none to this chapter. Solution #3's closing paragraph mentions `FloodGame` inheriting from `Observable`, which stays correct under proposal 1 only if it becomes `Observable[Grid]`, so land these two together if both are accepted.

---

## 6. `draw()` never clears the canvas

**Kind:** code
**Where:** listing `box_view.py`, `draw()` (line ~402)
**Problem:** `draw()` calls `create_rectangle` for every cell on every notification and never removes the previous rectangles. The display looks right, because each repaint covers the last one exactly, but the canvas item list grows by `size * size` per click and never shrinks. A reader adapting this view is copying an unbounded leak that is invisible until the canvas slows down. It also sits badly next to the chapter's own lapsed-listener paragraph, which is about exactly this class of quiet growth.

**Proposal:** one line at the top of `draw()`:

```python
    def draw(grid: Grid) -> None:
        canvas.delete("all")
        for (x, y), color in grid.items():
            ...
```

**Cost:** none. `box_view.py` is in `tools/data/norun.txt` so it carries no `#:` marker, and the line is well inside 70 characters. Worth one clause in the surrounding prose so the line does not read as noise.

---

## 7. `cell` names two different things

**Kind:** code
**Where:** listing `box_view.py`, `show()` signature and body (line ~394)
**Problem:** in `box_observer.py`, `cell` is a `Coord` (`click(self, cell: Coord)`, `adjacent(cell, clicked)`). In `box_view.py`, `cell` is a pixel count. The collision peaks in `lambda e: model.click((e.x // cell, e.y // cell))`, where a variable named `cell` is divided into pixels to produce the thing the model calls a cell.

**Proposal:** rename the parameter to `cell_px`. Two lines need rewrapping to stay under 70:

```python
            canvas.create_rectangle(
                x * cell_px, y * cell_px,
                (x + 1) * cell_px, (y + 1) * cell_px,
                fill=color, outline="white")
```

```python
    canvas.bind("<Button-1>",
                lambda e: model.click(
                    (e.x // cell_px, e.y // cell_px)))
```

**Cost:** none outside the listing; no prose names the parameter.

**Alternative:** rename to `px`, which needs no rewrapping at all but is terser than the book's usual naming.

---

## 8. `Observable` is a base class two paragraphs after "need not be a base class"

**Kind:** teaching
**Where:** section "The Pythonic Observer: a List of Callables" (line ~33)
**Problem:** the reader is told "An *observable* need not be a base class with a `changed` flag. It is a list of callables and a way to notify them," and is then shown `class Thermometer(Observable)`, `class BoxModel(Observable)`. The sentence is defensible (what is dropped is the flag and the mandated protocol, not inheritance), but a first-time reader who took the sentence at face value now has to reconcile it alone. The chapter dissolves the observer side into a callable and leaves the observable side as the one hierarchy in sight, without saying that this is convenience rather than necessity.

**Proposal:** one sentence after the `observers.py` listing:

> `Thermometer` inherits `Observable` because that is the shortest way to get
> `subscribe()` and `notify()`, not because the pattern demands a base class.
> Holding one as an attribute (`self.temperature_changed = Observable()`)
> works the same and lets one object publish more than one kind of change.

**Cost:** no code change. It plants the idea a reader needs the moment they want two independent notification streams from one object, which the chapter otherwise never raises. If proposal 2's classic listing lands, this sentence belongs after it instead, where the contrast is sharper.

---

## 9. Two sentences that call attention to themselves

**Kind:** prose
**Where:** lines ~155 and ~187
**Problem:** both read as flourish rather than explanation.

- "The `list()` copy inside `notify()` is a single word doing quiet work." `list()` is a call, not a word, and "quiet work" defers the point by a sentence when the next line is about to make it plainly.
- "Two more realities of Observer deserve a sentence each." Neither gets a sentence; each gets four lines. "Realities" is also heavier diction than the chapter's usual.

**Proposal:**

> The `list()` copy inside `notify()` looks redundant. It is not.

and

> Two more things about Observer need saying.

**Cost:** none.

---

## 10. "Click a box and every box touching it ... repaints"

**Kind:** prose
**Where:** section "A Visual Example of Observers" (line ~298)
**Problem:** this is the imperative-plus-consequence shape the style rules rule out: a command to the reader followed by a report of what happens. Here it is describing the program's behavior, three paragraphs before the reader is told to run anything, so it is not one of the real-instruction exemptions.

**Proposal:**

> Clicking a box repaints it and every box touching it, diagonals included,
> to the clicked box's color.

**Cost:** none. "Run `box_view.py` to play" further down stays imperative, correctly.

---

## 11. The chapter ends on the model-view split, not on its own claim

**Kind:** structure
**Where:** end of section "A Visual Example of Observers" (line ~418)
**Problem:** the chapter's claim is that Observer amounts to a list of callbacks. Its last paragraph is about testing a model without a display, which is the visual example's point rather than the chapter's. So the argument stops without being stated, and the thread from [The Pattern Concept](21_The_Pattern_Concept.md) (patterns dissolving into the language) is never cashed in here, even though chapter 21 links to this chapter to make that case.

**Proposal:** three or four lines after the existing closing paragraph, titled or untitled as you prefer, that name what stayed constant: one `Observable` served a thermometer, a fan-out over the network, and a GUI, and in every case the observer was a callable and the observable was a list. Point forward to [Function Objects](28_Function_Objects.md#an-event-bus-handlers-keyed-by-type)'s event bus as the same list keyed by event type.

**Cost:** the neighboring chapters (28, 31, 32, 33) also end on their last technical section rather than a closer, so this makes 30 the exception. 29 and 35 do end with a step-back section, so it is not unprecedented. Reject if the pattern chapters are meant to end without one.

---

## Already fixed directly (no decision needed)

- line ~108: "Removal is by identity" was wrong. `Observable.unsubscribe()` calls `list.remove()`, which matches with `==`, not `is`. The distinction is not academic here: `xs.append is xs.append` is `False` while `xs.append == xs.append` is `True`, so a bound-method observer is removable and a lambda is not, for the same reason. Replaced with "`unsubscribe()` matches by equality, and a lambda equals only itself," which keeps the original conclusion (a detachable observer needs a named reference) resting on a true premise. Proposal 4 completes the thought.

### Verified clean, no change needed

- All `#:` markers match real stdout. `async_observers.py` ran 5 times with identical ordering; its 0.01 / 0.05 sleeps are a 5x gap, inside the margin CLAUDE.md's timing trap calls for.
- `ty check`, `ruff check`, and all 9 tests pass against `build/examples/30_Observer`.
- `heading_links.py` and `banned_phrases.py` both clean.
- The claim that "the `AsyncObserver` alias makes the checker reject a plain function as an observer" is true: ty reports `incompatible return types: None is not assignable to Awaitable[None]`.
- The claim that the naive loop drops `always: 1` is correct: `once` removes itself at index 0, the loop advances to index 1, and the one-element list ends the iteration.
- No em-dashes anywhere in the chapter, and no relative cross-reference phrases ("the previous chapter", "the previous section") to go stale.
- The Observer-as-callbacks argument matches both ends of its cross-chapter thread: 28's event-bus section already calls itself "the Observer, narrowed to a single subject", and 21 lists Observer as one of its behavioral examples.
