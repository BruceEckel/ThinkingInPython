# Memento

Undo is a feature users expect and programmers dread.
It requires a program to capture an object's state at one moment and restore it later.
The *Memento* pattern does this without breaking encapsulation.
The *originator* (the object with state) produces a *memento*,
an opaque snapshot of itself.
A *caretaker* (the undo machinery) stores mementos and hands one back when asked,
without ever looking inside.

The pattern exists because of mutation.
An object that changes in place destroys its own past,
so you must copy the past and guard it.
Python offers the classic form when you need it,
and obviates the pattern when state is immutable.

## A Snapshot Is Not a Reference

The beginner's memento is an assignment, and it does not work:

```python
# aliased_snapshot.py

todo = ["eggs", "milk"]
saved = todo
todo.append("bread")
print(saved, saved is todo)
#: ['eggs', 'milk', 'bread'] True
copied = list(todo)
todo.append("jam")
print(copied)
#: ['eggs', 'milk', 'bread']
```

`saved = todo` binds a second name to the same list,
so the "snapshot" mutates right along with the original.
`list(todo)` makes a real copy, and later changes leave it alone.
A one-level copy is enough here because the elements are immutable strings.
When state nests mutable objects inside mutable objects,
`copy.deepcopy()` copies all the way down:

```python
# nested_mutation.py
import copy

todo = [["eggs", "milk"], ["bread"]]
shallow = list(todo)
todo[0].append("cheese")
print(shallow)
#: [['eggs', 'milk', 'cheese'], ['bread']]

deep = copy.deepcopy(todo)
todo[0].append("jam")
print(deep)
#: [['eggs', 'milk', 'cheese'], ['bread']]
```

`list(todo)` copies the outer list,
so `shallow` and `todo` are different objects.
But their elements are the same inner lists,
so `todo[0].append("cheese")` shows up in `shallow` too.
`copy.deepcopy()` walks the whole structure and rebuilds every nested container from scratch,
so `deep`'s inner lists share nothing with `todo`'s.
The later `todo[0].append("jam")` never reaches `deep`.

## The Classic Memento

Every classic memento is some version of copying the state before it changes.
Here the originator is a `Sketch` that accumulates strokes in a list.
Its memento converts that list to a tuple,
so the snapshot is immutable even though the originator is not.
`restore()` copies in the other direction,
rebuilding a fresh list so the sketch and the memento never share one:

```python
# sketch.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Memento:
    strokes: tuple[str, ...]

class Sketch:
    def __init__(self) -> None:
        self.strokes: list[str] = []

    def draw(self, stroke: str) -> None:
        self.strokes.append(stroke)

    def save(self) -> Memento:
        return Memento(tuple(self.strokes))

    def restore(self, memento: Memento) -> None:
        self.strokes = list(memento.strokes)

    def __str__(self) -> str:
        return " ".join(self.strokes) or "(blank)"

if __name__ == "__main__":
    sketch = Sketch()
    sketch.draw("circle")
    sketch.draw("beak")
    checkpoint = sketch.save()
    sketch.draw("scribble")
    print(sketch)
    sketch.restore(checkpoint)
    print(sketch)
#: circle beak scribble
#: circle beak
```

The caretaker's side of the contract is restraint.
Whoever holds `checkpoint` stores it and gives it back.
It does not reach inside and edit the strokes.
Languages with access control enforce this opacity.
In Python it is a convention,
though freezing the memento means the honest mistakes (mutating the snapshot) fail loudly.

A plain `type Memento = tuple[str, ...]` alias would type-check
at every call site instead of the class.
But an alias is *structural*, not *nominal*.
Any `tuple[str, ...]` in the program satisfies it,
including one a caretaker builds or unpacks by hand.
Wrapping the tuple in a one-field dataclass gives `Memento` an identity of its own.
The only way to see the strokes is through `.strokes`,
so reaching inside becomes visible in the code, not just a convention to honor.
`frozen=True` is what makes reassigning `checkpoint.strokes` fail instead of silently succeeding.
The tuple inside was already immutable, but the attribute itself was not.

```python
# test_sketch.py
from sketch import Sketch

def test_restore_rewinds_state() -> None:
    sketch = Sketch()
    sketch.draw("a")
    checkpoint = sketch.save()
    sketch.draw("b")
    sketch.restore(checkpoint)
    assert sketch.strokes == ["a"]

def test_memento_ignores_later_drawing() -> None:
    sketch = Sketch()
    sketch.draw("a")
    checkpoint = sketch.save()
    sketch.draw("b")
    assert checkpoint.strokes == ("a",)

def test_drawing_after_restore_spares_memento() -> None:
    sketch = Sketch()
    checkpoint = sketch.save()
    sketch.restore(checkpoint)
    sketch.draw("x")
    assert checkpoint.strokes == ()
```

The third test checks for the subtle bug.
If `restore()` handed the memento's data back by reference,
drawing afterward would corrupt the snapshot.
Both `save()` and `restore()` must copy.

## Immutability

All of that copying defends against mutation.
Remove the mutation and there is nothing left to prevent.
Make the state a frozen data class and every state *is* a memento:

```python
# frozen_sketch.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Sketch:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Sketch:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def __str__(self) -> str:
        drawn = " ".join(self.strokes) or "(blank)"
        return f"{self.title}: {drawn}"

if __name__ == "__main__":
    before = Sketch("Duck").draw("circle").draw("beak")
    after = before.draw("scribble")
    print(after)
    print(before)
#: Duck: circle beak scribble
#: Duck: circle beak
```

`draw()` returns a new `Sketch` instead of editing this one,
using `dataclasses.replace()` to change one field and carry the rest along.
Since each call returns a `Sketch`, the calls can be chained.
Saving means keeping a reference,
exactly the move that failed in `aliased_snapshot.py`.
Now it is safe because no operation anywhere can change the object bound to `before`.
No `Memento` class exists, no `save()`, no `restore()`,
and no copying to protect the past.
`after` shares the two original stroke strings with `before`.
This is the argument made by [Rethinking Objects](20_Rethinking_Objects.md#the-immutability-solution),
as [Flyweight](35_Flyweight.md) shares immutable values across space,
and Memento shares them across time.

```python
# test_frozen_sketch.py
from frozen_sketch import Sketch

def test_draw_returns_new_sketch() -> None:
    before = Sketch("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_replace_carries_other_fields() -> None:
    assert Sketch("Duck").draw("x").title == "Duck"

def test_equal_states_compare_equal() -> None:
    first = Sketch("Duck").draw("circle")
    second = Sketch("Duck").draw("circle")
    assert first == second and first is not second
```

## The Caretaker: a Generic History

With states as plain immutable values,
the caretaker no longer needs to know anything about them.
Undo and redo are two stacks of past and future states,
generic over the state type (the `class History[S]` syntax is from [Static Typing](08_Static_Typing.md#generic-functions-and-classes)):

![Three lanes holding state: do() pushes present into _past and clears _future; undo() shuttles present into _future and pops _past; redo() shuttles present into _past and pops _future](_images/memento_history)

```python
# history.py

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

    def can_undo(self) -> bool:
        return bool(self._past)

    def can_redo(self) -> bool:
        return bool(self._future)

if __name__ == "__main__":
    from frozen_sketch import Sketch
    history = History(Sketch("Duck"))
    history.do(history.present.draw("circle"))
    history.do(history.present.draw("beak"))
    print(history.present)
    print(history.undo())
    print(history.redo())
#: Duck: circle beak
#: Duck: circle
#: Duck: circle beak
```

`do()` pushes the present into the past and clears the future,
because acting after an undo starts a new timeline.
The states you undid are no longer reachable by redo,
which is how every editor behaves.
`undo()` and `redo()` just shuttle the present between the two stacks.
`History` stores whole states, not descriptions of changes,
so it never interprets anything.
That works for any state type, `int` to full `Sketch`, with one condition:
states must be immutable.
`History` cannot protect a list that someone mutates in place.
It would be a stack of aliases, the bug with which this chapter opened.

```python
# test_history.py
from history import History

def test_undo_and_redo() -> None:
    history = History(0)
    history.do(1)
    history.do(2)
    assert history.undo() == 1
    assert history.undo() == 0
    assert history.redo() == 1

def test_new_action_clears_redo() -> None:
    history = History("a")
    history.do("ab")
    history.undo()
    history.do("ax")
    assert not history.can_redo()
    assert history.present == "ax"

def test_bounds_are_reported() -> None:
    history = History(0)
    assert not history.can_undo()
    history.do(1)
    assert history.can_undo() and not history.can_redo()
    history.undo()
    assert history.can_redo() and not history.can_undo()
```

The alternative design stores commands instead of states.
Each undoable action carries its own inverse,
the Command variation mentioned in [Function Objects](28_Function_Objects.md).
Command-based undo saves memory when states are huge,
at the cost of writing and testing an inverse for every action.
Snapshot-based undo is the one to try first,
because immutable states make snapshots inexpensive.
Each `Sketch` above shares almost all of its strokes with its neighbors in the history.

## Mementos That Outlive the Process

A snapshot in memory disappears when the process ends.
The same frozen value, serialized, becomes a saved game,
a session file, or a crash-recovery point.
The standard library's `pickle` turns almost any Python object into bytes and back:

```python
# round_trip.py
import pickle
from frozen_sketch import Sketch

drawing = Sketch("Duck").draw("circle").draw("beak")
restored = pickle.loads(pickle.dumps(drawing))
print(restored == drawing, restored is drawing)
#: True False
```

The bytes from `pickle.dumps()` can go to a file and come back in a different process,
days later.
The round trip produces a different object with the same value,
which is all a memento needs, since frozen data classes compare by value.

Only unpickle data you trust, because the format can execute code.
For untrusted storage or other languages,
convert the state with `dataclasses.asdict()` and write JSON,
which one of the exercises explores.

Pickle's other limitation is time.
The bytes encode a class by module and name,
not by the shape that class had at save time.
If `Sketch` gains, loses, or renames a field before the load happens,
`pickle.loads()` still succeeds.
What breaks is everything that touches the missing piece.
Splitting the class into its own module keeps the simulation honest,
since real drift happens between two separate runs of a program,
not inside one script:

```python
# sketch_v1.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SketchV1:
    strokes: tuple[str, ...]
```

```python
# pickle_drift.py
import pickle
from dataclasses import dataclass
import sketch_v1
from sketch_v1 import SketchV1

blob = pickle.dumps(SketchV1(("circle", "beak")))

@dataclass(frozen=True)
class SketchV2:
    strokes: tuple[str, ...]
    title: str

sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
try:
    print(restored.title)
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError 'SketchV2' object has no attribute 'title'
```

`blob` is written while `sketch_v1.SketchV1` still means the one-field class.
`sketch_v1.SketchV1 = SketchV2` stands in for that module being edited and reloaded,
with a field added between the save and the load.
The type checker flags that reassignment as unsound so it carries a `# type: ignore`.
There isn't a practical way to declare that `SketchV1` can become a different class.
`pickle.loads()` never calls `__init__`.
It looks up the class by the name pickle recorded, `sketch_v1.SketchV1`.
That name now points at `SketchV2`.
`pickle.loads()` builds a bare `SketchV2`
and copies in only the fields the old bytes had.
`title` is simply absent, since the old bytes never had one.
The same shortcut skips `__post_init__`,
so a memento saved before a validated field existed
can load a value nothing ever validated.
`restored.strokes` works because both versions agree on that field.
`restored.title` fails the moment anything asks for it,
which is often nowhere near the line that called `pickle.loads()`.
Pickle is convenient because it hides this contract.
Nothing enforces that the class on load matches the class on save.

Databases hit the same problem and gave it a name.
A *schema migration* is the disciplined version of this drift,
a versioned, deliberate step that moves the table shape
and its data forward together,
instead of discovering the mismatch when a query runs.

When either limitation rules out `pickle`, there are open-source libraries.
`msgspec` and `pydantic` both validate on load.
A shape mismatch raises a clear error at the boundary,
instead of the delayed `AttributeError` from `pickle_drift.py`.
Protocol Buffers goes further.
Every field gets an explicit, numbered slot in a schema
shared across languages.
Old and new versions can then read each other's messages
on purpose, not by accident.
None of the three execute the bytes they read,
so none carry pickle's security risk either.

## Snapshots in the Wild

Version control is the memento pattern at industrial scale.
A git commit is an immutable snapshot of your whole tree,
checkout is `restore()`,
and git shares unchanged content between commits just as `History` shares unchanged strokes between states.
Databases hand out savepoints, mementos scoped to a transaction.
Multiplayer games snapshot the world so they can rewind and replay when a late packet arrives.
Whenever you see rewind, rollback, or restore, something is producing mementos.

## Exercises

1.  Add `erase()` to both sketches.
    It removes the last stroke.
    In `sketch.py` it mutates. In `frozen_sketch.py` it returns a new `Sketch`.
    Write tests proving existing mementos and histories are unaffected in each version.
2.  Give `History` a maximum depth.
    When the past grows beyond `n` states, discard the oldest.
    What should happen to `can_undo()`?
3.  Serialize a `Sketch` to JSON using `dataclasses.asdict()` and reconstruct it.
    What did the round trip change that `pickle` preserved,
    and where must your reconstruction compensate?
4.  Change `sketch.py` so `Memento` holds the list itself instead of a tuple copy,
    then write the test that exposes the corruption.
    Which of the three tests in `test_sketch.py` catches it first?
5.  Add `goto(steps_back)` to `History`:
    jump the present several states into the past in one call,
    keeping redo consistent.
