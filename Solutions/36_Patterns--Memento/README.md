# Memento: Solutions

## 1. `erase()` in both sketches

> Add `erase()` to both sketches.
> It removes the last stroke.
> In `sketch.py` it mutates.
> In `frozen_sketch.py` it returns a new `Drawing`.
> Write tests proving existing mementos and histories stay unchanged in each version.

<details>
<summary>Where to look</summary>

[The Classic Memento](../../Chapters/36_Patterns--Memento.md#the-classic-memento) shows `save()` copying the strokes into an immutable `Memento`, and [Immutability](../../Chapters/36_Patterns--Memento.md#immutability) shows a `Drawing` that returns a new state.
In the mutable sketch, `erase()` pops from the list like `draw()` appends to it.
In the frozen one, build the new `Drawing` with `replace()` and a sliced tuple.
Test each by saving first, erasing, then checking the earlier state still holds both strokes.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1_mutable.py
from record import record

@record
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        ...

    def draw(self, stroke: str) -> None:
        ...

    def erase(self) -> None:
        ...

    def save(self) -> Memento:
        ...

    def restore(self, memento: Memento) -> None:
        ...
```

```python
# The shape of exercise_1_frozen.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        ...

    def erase(self) -> Drawing:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_1_mutable.py
from record import record

@record
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        self.strokes: list[str] = []

    def draw(self, stroke: str) -> None:
        self.strokes.append(stroke)

    def erase(self) -> None:
        if self.strokes:
            self.strokes.pop()

    def save(self) -> Memento:
        return Memento(tuple(self.strokes))

    def restore(self, memento: Memento) -> None:
        self.strokes = list(memento.strokes)

sketch = Sketch()
sketch.draw("a")
sketch.draw("b")
checkpoint = sketch.save()
sketch.erase()
print(sketch.strokes, checkpoint.strokes)
#: ['a'] ('a', 'b')
```

```python
# test_ch36_erase_mutable.py
from record import record

@record
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        self.strokes: list[str] = []

    def draw(self, stroke: str) -> None:
        self.strokes.append(stroke)

    def erase(self) -> None:
        if self.strokes:
            self.strokes.pop()

    def save(self) -> Memento:
        return Memento(tuple(self.strokes))

    def restore(self, memento: Memento) -> None:
        self.strokes = list(memento.strokes)

class History[S]:
    def __init__(self, initial: S) -> None:
        self.present = initial
        self.past: list[S] = []

    def do(self, new_state: S) -> None:
        self.past.append(self.present)
        self.present = new_state

def test_erase_does_not_affect_existing_memento() -> None:
    sketch = Sketch()
    sketch.draw("a")
    sketch.draw("b")
    checkpoint = sketch.save()
    sketch.erase()
    assert sketch.strokes == ["a"]
    assert checkpoint.strokes == ("a", "b")  # Untouched

def test_erase_leaves_history_states_untouched() -> None:
    sketch = Sketch()
    sketch.draw("a")
    history = History(sketch.save())
    sketch.draw("b")
    history.do(sketch.save())
    sketch.erase()
    assert history.present.strokes == ("a", "b")
    assert history.past[0].strokes == ("a",)
```

**Remove the last stroke.** `erase()` mutates `self.strokes` in place, as `draw()`
does, so it needs no special handling.

**Copy the state when saving.** `save()` copies the strokes
into an immutable `Memento` the moment it runs, so nothing later,
erase included, can reach back and change a memento already taken.

**Prove the history keeps its states.** The history test shows the same safety one level up, using a
`History` trimmed to what the test needs. The states that `History`
stores are mementos, and mementos never change, so erasing after a
`do()` leaves both the present state and the past one intact.

```python
# exercise_1_frozen.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def erase(self) -> Drawing:
        return replace(self, strokes=self.strokes[:-1])

before = Drawing("Duck").draw("circle").draw("beak")
after = before.erase()
print(before.strokes, after.strokes)
#: ('circle', 'beak') ('circle',)
```

```python
# test_ch36_erase_frozen.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def erase(self) -> Drawing:
        return replace(self, strokes=self.strokes[:-1])

class History[S]:
    def __init__(self, initial: S) -> None:
        self.present = initial
        self.past: list[S] = []

    def do(self, new_state: S) -> None:
        self.past.append(self.present)
        self.present = new_state

def test_erase_returns_new_drawing_leaving_original(
) -> None:
    before = Drawing("Duck").draw("circle").draw("beak")
    after = before.erase()
    assert before.strokes == ("circle", "beak")  # Untouched
    assert after.strokes == ("circle",)

def test_erase_leaves_history_states_untouched() -> None:
    before = Drawing("Duck").draw("circle").draw("beak")
    history = History(before)
    history.do(before.erase())
    assert history.present.strokes == ("circle",)
    assert history.past[0] is before
    assert before.strokes == ("circle", "beak")
```

**Derive the shorter state.** The frozen version's `erase()` follows `draw()`'s shape too: it
returns a new `Drawing` via `replace()`, this time with the last stroke
sliced off. `before` keeps its own strokes, so any `History` holding
`before` as a past state stays safe.

**Prove the history keeps its states.** The history test confirms that safety: after `do(before.erase())`,
the stored past state `is` the original object, still carrying both
strokes.

</details>
</details>
</details>

## 2. A bounded `History`

> Give `History` a maximum depth.
> When the past grows beyond `n` states, discard the oldest.
> What should `can_undo()` report then?

<details>
<summary>Where to look</summary>

[The Caretaker: a Generic History](../../Chapters/36_Patterns--Memento.md#the-caretaker-a-generic-history) keeps the past as a list that `do()` appends to.
After the append, check the length against a `max_depth` and drop the oldest entry with `pop(0)`.
For `can_undo()`, ask what the list holds now, not what the program once pushed.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
class History[S]:
    def __init__(self, initial: S, max_depth: int) -> None:
        ...

    def do(self, new_state: S) -> None:
        ...

    def undo(self) -> S:
        ...

    def can_undo(self) -> bool:
        ...
```

<details>
<summary>Solution</summary>

If `can_undo()` counts the `do()` calls that `undo()` has not yet reversed,
rather than looking at `_past`,
it reports `True` once the bound has discarded a state the count still includes.
In the demo it reports `True` after the two undos, with `_past` empty,
and the `undo()` it approves raises an `IndexError` from `pop()`.
The solution keeps the chapter's `bool(self._past)`, which asks what the list holds now.

```python
# exercise_2.py
class History[S]:
    def __init__(self, initial: S, max_depth: int) -> None:
        self._present = initial
        self._past: list[S] = []
        self._future: list[S] = []
        self._max_depth = max_depth

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        if len(self._past) > self._max_depth:
            self._past.pop(0)  # Discard the oldest
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        previous = self._past.pop()
        self._future.append(self._present)
        self._present = previous
        return self._present

    def can_undo(self) -> bool:
        return bool(self._past)

h = History(0, max_depth=2)
h.do(1)
h.do(2)
# Past would be [0, 1, 2]; the bound discards 0
h.do(3)
print(h._past)
#: [1, 2]
print(h.undo(), h.undo())
#: 2 1
print(h.can_undo())
#: False
```

**Report what the past still holds.** `can_undo()` needs no change: it already asks whether `_past` still
holds a state. A bounded history empties `_past` sooner: after at
most `max_depth` undos, rather than one undo per `do()` the program
made. So `can_undo()` reports `False` while earlier states exist that
the bound discarded. Once the bound discards state `0`, nothing can
bring it back, and `can_undo()` reporting `False` there is the
correct answer, not a bug.

</details>
</details>
</details>

## 3. Serializing a `Drawing` to JSON

> Serialize a `Drawing` to JSON using `dataclasses.asdict()` and reconstruct it.
> What did the round trip change that `pickle` preserved,
> and where must your reconstruction compensate?

<details>
<summary>Where to look</summary>

[Mementos That Outlive the Process](../../Chapters/36_Patterns--Memento.md#mementos-that-outlive-the-process) uses `pickle`, which keeps Python types intact.
JSON has a smaller set of types, so print the type of `strokes` after `json.loads()`.
Rebuild the `Drawing` from the loaded dictionary, converting that one field back to the type the record declares.
Compare the result with the original using `==`.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
import json
from dataclasses import asdict, replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        ...
```

<details>
<summary>Solution</summary>

If you pass `data["strokes"]` to `Drawing` without wrapping it in `tuple(...)`,
`ty check` still passes, because `json.loads()` returns `Any`,
and an `Any` satisfies the declared `tuple[str, ...]`.
The mismatch surfaces only when the program runs:
`reconstructed == drawing` becomes `False`, since a `list` never
equals a `tuple`, and the `list` costs the `Drawing` the hashability a
record otherwise supplies (`hash()` raises a `TypeError`,
`unhashable type: 'list'`).
The solution converts the field back, so the rebuilt `Drawing` equals the original.

```python
# exercise_3.py
import json
from dataclasses import asdict, replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

drawing = Drawing("Duck").draw("circle").draw("beak")
as_json = json.dumps(asdict(drawing))
data = json.loads(as_json)
print(type(data["strokes"]))
#: <class 'list'>
reconstructed = Drawing(
    data["title"], tuple(data["strokes"]))
print(reconstructed == drawing)
#: True
```

**Find what the round trip changed.** JSON has no tuple type, only arrays, so `strokes` comes back from
`json.loads()` as a `list`, where the record declares it
`tuple[str, ...]`. `pickle` preserves the exact Python type, tuple
in, tuple out, because it serializes Python's own object
representations rather than translating into a shared,
language-neutral format.

**Restore the declared type.** The reconstruction compensates for what
JSON loses: it wraps `data["strokes"]` back in `tuple(...)` before
passing it to `Drawing`.

</details>
</details>
</details>

## 4. `Memento` holding the list itself

> Change `sketch.py` so `Memento` holds the list itself instead of a tuple copy,
> and so `restore()` assigns that list rather than copying it,
> leaving the sketch and the memento sharing one list in both directions.
> Then write the test that exposes the corruption.
> Which of the three tests in `test_sketch.py` catches it first?

<details>
<summary>Where to look</summary>

[A Snapshot Is Not a Reference](../../Chapters/36_Patterns--Memento.md#a-snapshot-is-not-a-reference) shows what happens when two names share one list.
Change `Memento` and `restore()` so the sketch and the memento hold the same list object.
Run the existing tests with `pytest` and read the order of the failures.
Then write a test that draws after `save()` and compares the memento's contents as a list, so only sharing can fail it.

<details>
<summary>Solution</summary>

```python
@record
class Memento:
    strokes: list[str]  # Bug: a list, not a tuple copy

class Sketch:
    def save(self) -> Memento:
        # No copy: same list object
        return Memento(self.strokes)
    def restore(self, memento: Memento) -> None:
        self.strokes = memento.strokes    # Also no copy
```

All three existing tests fail against this version, and pytest
reports them in the order they appear in the file, so
`test_restore_rewinds_state` surfaces first:

```
FAILED test_sketch.py::test_restore_rewinds_state
FAILED test_sketch.py::test_memento_ignores_later_drawing
FAILED test_sketch.py::test_drawing_after_restore_spares_memento
```

**Share the list on save.** The corruption is deeper than any single test expects. Because
`Memento.strokes` is now the same list `Sketch.strokes` points
to, `sketch.draw("b")` after `checkpoint = sketch.save()` mutates
`checkpoint.strokes` too. By the time `test_restore_rewinds_state`
calls `sketch.restore(checkpoint)`, `checkpoint` has already silently
absorbed the `"b"` stroke that the copy in `save()` exists to keep
out. `sketch.strokes == ["a"]` then fails immediately, before the
test reaches the scenario
`test_drawing_after_restore_spares_memento` catches. Making
`Memento` a record prevents
reassigning `strokes` after construction, but the list inside stays
mutable, and every later `draw()` changes it. So `save()`
must copy into a `tuple`, an immutable container, instead of wrapping
a mutable list in a record.

Two of those failures prove less than they seem. The second and third
tests compare `checkpoint.strokes` with a tuple, and a `list` never
equals a `tuple`, so a `Memento` holding a copied list fails them
too, with no sharing at all. The test that exposes the corruption
compares contents only, so the type change alone cannot fail it:

```python
def test_memento_is_a_snapshot() -> None:
    sketch = Sketch()
    sketch.draw("a")
    checkpoint = sketch.save()
    sketch.draw("b")
    assert list(checkpoint.strokes) == ["a"]
```

**Isolate the sharing bug.** Against the shared-list version, `checkpoint.strokes` is `["a", "b"]`
when the assertion runs, because `draw("b")` appended to the one list
`sketch` and `checkpoint` share.

</details>
</details>

## 5. `goto(steps_back)`

> Add `goto(steps_back)` to `History`:
> jump the present several states into the past in one call,
> keeping redo consistent.

<details>
<summary>Where to look</summary>

In [The Caretaker: a Generic History](../../Chapters/36_Patterns--Memento.md#the-caretaker-a-generic-history), `undo()` already moves the present into the future list, which is what makes redo work.
Build `goto()` on top of `undo()` in a loop.
Check the distance against the length of the past before the first step, so a bad request changes nothing.
Raise an `IndexError` for a distance out of range.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from exceptions import expect

class History[S]:
    def __init__(self, initial: S) -> None:
        ...

    @property
    def present(self) -> S:
        ...

    def do(self, new_state: S) -> None:
        ...

    def undo(self) -> S:
        ...

    def redo(self) -> S:
        ...

    def goto(self, steps_back: int) -> S:
        ...
```

<details>
<summary>Solution</summary>

If you leave out the range check,
a jump too far raises an `IndexError` partway, after moving some states to `_future`:
in the demo, `goto(4)` undoes three states before `pop()` fails,
and the present is `0` rather than `3`.
The solution checks the distance before it moves anything, so
a jump that raises an `IndexError` leaves the history where it was,
as the chapter's `undo()` does.

```python
# exercise_5.py
from exceptions import expect

class History[S]:
    def __init__(self, initial: S) -> None:
        self._present = initial
        self._past: list[S] = []
        self._future: list[S] = []

    @property
    def present(self) -> S:
        return self._present

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        previous = self._past.pop()
        self._future.append(self._present)
        self._present = previous
        return self._present

    def redo(self) -> S:
        following = self._future.pop()
        self._past.append(self._present)
        self._present = following
        return self._present

    def goto(self, steps_back: int) -> S:
        if not 0 <= steps_back <= len(self._past):
            raise IndexError(f"cannot go back {steps_back}")
        for _ in range(steps_back):
            self.undo()
        return self._present

h = History(0)
h.do(1)
h.do(2)
h.do(3)
print(h.goto(2))
#: 1
print(h.redo(), h.redo())
#: 2 3
expect(IndexError, h.goto, 4)
#: [IndexError] cannot go back 4
print(h.present)
#: 3
```

**Step back through `undo()`.** `goto()` adds no new mechanism. It calls the existing `undo()`
repeatedly, and each `undo()` pushes the state it leaves onto
`_future`. Redo therefore works exactly as if you had called `undo()`
twice: `h.redo()` after `goto(2)` returns `2`, then `3`, retracing
the same path forward. Jumping several states back
"in one call" is a convenience for the caller.

</details>
</details>
</details>

## 6. Restoring one named field

> A `History` of `Drawing` states records a rename and three strokes.
> Write `restore_field(history, name, past)` that pushes a new state taking one named field from `past` and the rest from `history.present`.
> Why must it go through `do()` rather than editing `_past` directly?

<details>
<summary>Where to look</summary>

[Restoring Part of a State](../../Chapters/36_Patterns--Memento.md#restoring-part-of-a-state) builds a new state from the present and one field of a past state.
Generalize it with `getattr()` to read the named field from `past`, and pass it to `copy.replace()` as the only change.
Push the result with `do()`, then call `undo()` to see that the restore is one step on the timeline.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_6.py
import copy
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        ...

class History[S]:
    def __init__(self, initial: S) -> None:
        ...

    @property
    def present(self) -> S:
        ...

    def do(self, new_state: S) -> None:
        ...

    def undo(self) -> S:
        ...

def restore_field(
    history: History[Drawing], name: str, past: Drawing
) -> None:
    ...
```

<details>
<summary>Solution</summary>

```python
# exercise_6.py
import copy
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

class History[S]:
    def __init__(self, initial: S) -> None:
        self._present = initial
        self._past: list[S] = []
        self._future: list[S] = []

    @property
    def present(self) -> S:
        return self._present

    def do(self, new_state: S) -> None:
        self._past.append(self._present)
        self._present = new_state
        self._future.clear()

    def undo(self) -> S:
        previous = self._past.pop()
        self._future.append(self._present)
        self._present = previous
        return self._present

def restore_field(
    history: History[Drawing], name: str, past: Drawing
) -> None:
    change = {name: getattr(past, name)}
    history.do(copy.replace(history.present, **change))

history = History(Drawing("Duck"))
history.do(history.present.draw("body"))
checkpoint = history.present
history.do(copy.replace(history.present, title="Goose"))
history.do(history.present.draw("beak"))
history.do(history.present.draw("tail"))
print(history.present)
#: Drawing(title='Goose', strokes=('body', 'beak', 'tail'))
restore_field(history, "strokes", checkpoint)
print(history.present)
#: Drawing(title='Goose', strokes=('body',))
print(history.undo())
#: Drawing(title='Goose', strokes=('body', 'beak', 'tail'))
```

**Take one field from the past.** `restore_field()` is `partial_restore.py` with the field name lifted
into a parameter. It reads one attribute off the past state, hands it
to `copy.replace()` as the single change, and pushes the result
through `do()`. The rename to `"Goose"` survives the restore because
`copy.replace()` carries over every field the call did not name.

**Narrow the history's state type.** `restore_field()` takes a `History[Drawing]` rather than a generic
`History[S]`, and that is a typing constraint rather than a design
choice. `copy.replace()` requires a `__replace__()` method, and a bare
type variable `S` has no such method, so a generic version needs
a `Protocol` declaring `__replace__()` as the type variable's bound.
Worth doing in a library; noise in a solution.

**Record the restore as an action.** `restore_field()` must go through `do()` for the reason
[Restoring Part of a State](../../Chapters/36_Patterns--Memento.md#restoring-part-of-a-state)
gives, and the listing's last line proves it: the partial restore is
itself an action, so it belongs on the timeline. Editing `_past`
directly rewrites history rather than extending it, leaving the user
who wanted the strokes back no way to change their mind. Direct
editing also desynchronizes the caretaker's own bookkeeping: `do()`
clears `_future`, so a `_past` edited behind the caretaker's back
leaves a redo stack pointing at states the history can no longer
reach.

</details>
</details>
</details>

## 7. What pickle skips on load

> Save two `Drawing`s with `pickle`, one of them with an empty title,
> then add a field with a default to `Drawing` and load the old bytes.
> Does the default appear?
> Now add a `__post_init__()` that rejects an empty title,
> and load the blank one again.
> What did pickle skip, and what does `copy.replace()` catch?

<details>
<summary>Where to look</summary>

[A Class That Changes After the Save](../../Chapters/36_Patterns--Memento.md#a-class-that-changes-after-the-save) shows `pickle` loading old bytes into a changed class, and [A Deleted Field Leaves a Ghost](../../Chapters/36_Patterns--Memento.md#a-deleted-field-leaves-a-ghost) shows what `pickle` writes into the instance.
Point the old class name at the new class, load the bytes, and look in the instance's `__dict__` for the new field.
Then ask which methods `pickle.loads()` calls, and compare with `copy.replace()`, which constructs a real instance.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_7.py
import copy
import pickle
import drawing_v1
from drawing_v1 import Drawing
from exceptions import expect
from record import record

@record(slots=False)
class DrawingV2:
    title: str
    strokes: tuple[str, ...] = ()
    layer: int = 1

    def __post_init__(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

If you write `DrawingV2` with a bare `@record`, as the chapter writes `Drawing`,
the default does not appear: reading `restored.layer` raises an `AttributeError`.
A slotted class keeps `layer` in a slot instead of as a class attribute,
so nothing supplies the value the old bytes lack.
The solution writes `@record(slots=False)`,
which keeps the default on the class and gives each instance the `__dict__` the listing inspects.

```python
# drawing_v1.py
from record import record

@record(slots=False)
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()
```

```python
# exercise_7.py
import copy
import pickle
import drawing_v1
from drawing_v1 import Drawing
from exceptions import expect
from record import record

blob = pickle.dumps(Drawing("Duck", ("circle",)))
blank = pickle.dumps(Drawing("", ("circle",)))

@record(slots=False)
class DrawingV2:
    title: str
    strokes: tuple[str, ...] = ()
    layer: int = 1

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("title must not be empty")

drawing_v1.Drawing = DrawingV2  # type: ignore

restored = pickle.loads(blob)
print(type(restored).__name__, restored.layer)
#: DrawingV2 1
print("layer" in restored.__dict__)
#: False

empty = pickle.loads(blank)
print(repr(empty.title))
#: ''
expect(ValueError, copy.replace, empty, strokes=())
#: [ValueError] title must not be empty
```

**Find the default on the class.** The default appears, and not because pickle supplied it. A dataclass
field with a simple default stores that default as a class attribute,
so `restored.layer` finds `DrawingV2.layer` by ordinary attribute
lookup while `restored.__dict__` has no `layer`. With the field
written `layer: list[str] = field(default_factory=list)`, the default
disappears: a `default_factory` leaves no class attribute, so the
loaded object raises an `AttributeError` the first time anything
reads `layer`.

**Skip the constructor on load.** What pickle skips is every line of code the class runs at
construction. `pickle.loads()` builds a bare instance and writes the
saved `__dict__` into it, so `__init__()` never runs and neither does
`__post_init__()`. The empty title loads into a class written to
reject it.

**Run the validation on replace.** `copy.replace()`, which the chapter's partial restore uses, behaves
differently. It goes through `__replace__()`, which constructs a real instance
and therefore runs `__post_init__()`, so `__post_init__()` catches the
invalid state the moment anything derives a new state from it. That is
the general shape: a constructor validates the value that enters your
program through it, while a deserializer hands the value straight in.
`msgspec` and `pydantic` exist to close that gap.

</details>
</details>
</details>
