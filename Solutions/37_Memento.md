# Memento: Solutions

## 1. `erase()` in both sketches

```python
# exercise_1_mutable.py
from dataclasses import dataclass

@dataclass(frozen=True)
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
# test_ch37_erase_mutable.py
from dataclasses import dataclass

@dataclass(frozen=True)
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

def test_erase_does_not_affect_existing_memento() -> None:
    sketch = Sketch()
    sketch.draw("a")
    sketch.draw("b")
    checkpoint = sketch.save()
    sketch.erase()
    assert sketch.strokes == ["a"]
    assert checkpoint.strokes == ("a", "b")  # Untouched
```

`erase()` mutates `self.strokes` in place, exactly like `draw()`
does, so it needs no special handling: `save()` already copies into
an immutable `Memento` at the moment it is called, so nothing later,
erase included, can reach back and change a memento already taken.

```python
# exercise_1_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(self, strokes=(*self.strokes, stroke))

    def erase(self) -> Sketch:
        return replace(self, strokes=self.strokes[:-1])

before = Sketch("Duck").draw("circle").draw("beak")
after = before.erase()
print(before.strokes, after.strokes)
#: ('circle', 'beak') ('circle',)
```

```python
# test_ch37_erase_frozen.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(self, strokes=(*self.strokes, stroke))

    def erase(self) -> Sketch:
        return replace(self, strokes=self.strokes[:-1])

def test_erase_returns_new_sketch_leaving_original() -> None:
    before = Sketch("Duck").draw("circle").draw("beak")
    after = before.erase()
    assert before.strokes == ("circle", "beak")  # Untouched
    assert after.strokes == ("circle",)
```

The frozen version's `erase()` follows `draw()`'s shape too: it
returns a new `Sketch` via `replace()`, this time with the last stroke
sliced off, so `before` is never mutated and any `History` holding
`before` as a past state is automatically safe.

## 2. A bounded `History`

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
        self._future.append(self._present)
        self._present = self._past.pop()
        return self._present

    def can_undo(self) -> bool:
        return bool(self._past)

h = History(0, max_depth=2)
h.do(1)
h.do(2)
h.do(3)   # Past would be [0, 1, 2]; 0 is discarded, keeping only 2
print(h._past)
#: [1, 2]
print(h.undo(), h.undo())
#: 2 1
print(h.can_undo())
#: False
```

`can_undo()` needs no change at all: it already just asks whether
`_past` is non-empty. With a bounded history, `_past` empties sooner
(after `max_depth` undos instead of however many `do()` calls ever
happened), so `can_undo()` correctly reports `False` once the discarded
states are the only ones left to go back to; there is no way to
recover state `0` once it has fallen off the bound, and `can_undo()`
reporting `False` at that point is the honest answer, not a bug.

## 3. Serializing a `Sketch` to JSON

```python
# exercise_3.py
import json
from dataclasses import asdict, dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(self, strokes=(*self.strokes, stroke))

drawing = Sketch("Duck").draw("circle").draw("beak")
as_json = json.dumps(asdict(drawing))
data = json.loads(as_json)
print(type(data["strokes"]))
#: <class 'list'>
reconstructed = Sketch(data["title"], tuple(data["strokes"]))
print(reconstructed == drawing)
#: True
```

JSON has no tuple type, only arrays, so `strokes`, a `tuple[str,
...]` in the dataclass, comes back from `json.loads()` as a plain
`list`. `pickle` preserves the exact Python type, tuple in, tuple out,
because it serializes Python's own object representations rather than
translating into a shared, language-neutral format. The reconstruction
has to compensate for what JSON lost: wrapping `data["strokes"]` back
in `tuple(...)` before passing it to `Sketch`, since `Sketch.strokes`
is declared `tuple[str, ...]` and a `Sketch` built with a `list`
there would fail `ty check`, and would also no longer be hashable the
way the rest of the chapter relies on frozen dataclasses being.

## 4. `Memento` holding the list itself

```python
@dataclass(frozen=True)
class Memento:
    strokes: list[str]  # Bug: a list, not a tuple copy

class Sketch:
    def save(self) -> Memento:
        return Memento(self.strokes)      # No copy: same list object
    def restore(self, memento: Memento) -> None:
        self.strokes = memento.strokes    # Also no copy
```

Running the existing three tests against this version, all three
fail, but pytest reports them in the order they appear in the file,
so `test_restore_rewinds_state` is the one that surfaces first:

```
FAILED test_sketch.py::test_restore_rewinds_state
FAILED test_sketch.py::test_memento_ignores_later_drawing
FAILED test_sketch.py::test_drawing_after_restore_spares_memento
```

The corruption is deeper than any single test expects. Because
`Memento.strokes` is now the very same list `Sketch.strokes` points
to, `sketch.draw("b")` after `checkpoint = sketch.save()` mutates
`checkpoint.strokes` too, since they are one object. By the time
`test_restore_rewinds_state` even calls `sketch.restore(checkpoint)`,
the checkpoint it is restoring from has already silently absorbed the
`"b"` stroke it was supposed to be protected from, so `sketch.strokes
== ["a"]` fails immediately, before the test ever reaches the scenario
`test_drawing_after_restore_spares_memento` is specifically designed
to catch. Freezing the `Memento` class itself (`@dataclass(frozen=True)`)
prevents reassigning `strokes` after construction, but it does nothing
to stop the list *inside* it from being mutated, which is exactly why
`save()` must copy into a `tuple`, an immutable container, not merely
wrap a mutable one in a frozen dataclass.

## 5. `goto(steps_back)`

```python
# exercise_5.py
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
        self._future.append(self._present)
        self._present = self._past.pop()
        return self._present

    def redo(self) -> S:
        self._past.append(self._present)
        self._present = self._future.pop()
        return self._present

    def goto(self, steps_back: int) -> S:
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
```

`goto()` adds no new mechanism. It calls the existing `undo()`
repeatedly, which already pushes each visited state onto `_future` one
at a time as it goes, so redo still works exactly as if you had called
`undo()` three separate times: `h.redo()` after `goto(2)` returns `2`,
then `3`, retracing the same path forward. Jumping several states back
"in one call" is a convenience for the caller; the underlying stacks
stay in the same consistent state either way.
