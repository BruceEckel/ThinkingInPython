# Memento

> An object is about to change, and someone may want it back the way it was.
> A *Memento* saves what the object was so the program can restore it.

Undo is a feature users expect and programmers dread.
*Memento* is an undo mechanism that keeps encapsulation intact.
The *originator* (the object with state) produces a *memento*,
an opaque snapshot of itself.
A *caretaker* (the undo machinery) stores mementos and returns one on request,
without reading their contents.

The pattern exists because of mutation.
An object that changes in place overwrites its earlier state,
so you must copy that state before the change and freeze the copy.
Python has the classic form when you need it.
Immutable state removes the need.

## A Snapshot Is Not a Reference

[Rethinking Objects](20_Patterns--Rethinking_Objects.md#encapsulation-leaks)
shows a getter handing out a reference where the caller expects a copy.
A memento depends on that difference.
A memento works when it is a copy and fails when it is an alias.
The beginner's memento is an assignment, and an assignment aliases:

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

A one-level copy is enough here because the elements are immutable strings.
When state nests mutable objects inside mutable objects,
`copy.deepcopy()` copies every level of nesting:

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
print(todo)
#: [['eggs', 'milk', 'cheese', 'jam'], ['bread']]
print(deep)
#: [['eggs', 'milk', 'cheese'], ['bread']]
```

`list(todo)` copies the outer list,
so `shallow` and `todo` are different objects.
But their elements are the same inner lists,
so `todo[0].append("cheese")` changes the first element of `shallow` too.

`copy.deepcopy()` takes time and memory proportional to the whole nested structure it rebuilds,
however small the change.

## The Classic Memento

In the pattern as *GoF Design Patterns* presents it,
the originator copies its state into a memento before the state changes.
Here the originator is a `Sketch` that accumulates strokes in a list.
Its memento converts that list to a tuple,
so the snapshot is immutable while the originator stays mutable.
`restore()` copies in the other direction,
rebuilding a fresh list so the sketch's list and the memento's tuple are separate objects:

```python
# sketch.py
from record import record

@record
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
```

```python
# sketch_demo.py
from sketch import Sketch

sketch = Sketch()
sketch.draw("circle")
sketch.draw("beak")
checkpoint = sketch.save()
sketch.draw("scribble")
print(sketch)
#: circle beak scribble
sketch.restore(checkpoint)
print(sketch)
#: circle beak
```

`copy.copy(sketch)` looks like a shortcut for `save()`,
but it copies the `Sketch` and leaves its list shared.
The copy's `strokes` is the same list as `sketch.strokes`,
the alias from `aliased_snapshot.py` one level down.

`save()`'s one-level copy is enough because a stroke is a string.
An originator holding containers inside containers needs `copy.deepcopy()` in `save()`.
Each save then [rebuilds the whole nested structure](#a-snapshot-is-not-a-reference).

The caretaker's side of the contract is to store `checkpoint` and return it,
leaving `checkpoint.strokes` alone.
Languages with access control enforce that rule.
In Python the rule is a convention,
though a frozen memento raises a `FrozenInstanceError` on an accidental edit.

### Why `Memento` Is a Class

You could replace the class with `type Memento = tuple[str, ...]`.
Every call to `save()` and `restore()` still type-checks,
once `restore()` copies the tuple it receives in place of `memento.strokes`.
But an alias is a second name for an existing type.
Any `tuple[str, ...]` in the program satisfies it,
including one a caretaker builds or unpacks on its own.
`NewType("Memento", tuple[str, ...])` exists only for the type checker.
At runtime it is a callable that returns its argument,
so the caretaker still holds a plain tuple it can index, unpack,
or build from scratch.

Wrapping the tuple in a one-field record makes `Memento` a class of its own at runtime.
A parameter typed `tuple[str, ...]` still accepts any tuple of strings,
whatever built it.
A parameter typed `Memento` accepts only a `Memento`,
so the type checker reports a caretaker that passes some other tuple by mistake.
Building a `Memento` takes an import of the class and a call to it,
so every `Memento` a caretaker builds is deliberate.
`Memento` is a [record](18_Techniques--Performance.md#record),
so reassigning `checkpoint.strokes` raises `FrozenInstanceError` at runtime.

The checker and the frozen field both let code holding a `Memento` read `.strokes`,
unpack that tuple, or build a `Memento` of its own.
The caretaker's side of the contract remains a convention,
the one on which the classic pattern relies.
The type checker catches the accidental case:
a caretaker that mixes up a `Memento` with some other tuple.

```python
# memento_type_safety.py
from dataclasses import FrozenInstanceError
from exceptions import expect, expected
from sketch import Sketch

def restore_tuple(sketch: Sketch,
                  strokes: tuple[str, ...]) -> None:
    sketch.strokes = list(strokes)

sketch = Sketch()
sketch.draw("circle")
checkpoint = sketch.save()

restore_tuple(sketch, checkpoint.strokes)
print(sketch)
#: circle
restore_tuple(sketch, ("unrelated", "tuple"))
print(sketch)
#: unrelated tuple

sketch.restore(checkpoint)
print(sketch)
#: circle
# ty: tuple[str, str] is not a Memento:
expect(AttributeError, sketch.restore,
       ("unrelated", "tuple"))  # type: ignore
#: [AttributeError] 'tuple' object has no attribute
#: 'strokes'

with expected(FrozenInstanceError):
    # ty: strokes is read-only on Memento:
    checkpoint.strokes = ("forged",)  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'strokes'
```

`restore_tuple()` accepts either tuple, since both are `tuple[str, ...]`,
so it installs the stray tuple as the sketch's state with no complaint.
The type checker reports the plain tuple before the program runs.
At runtime, `restore()` raises an `AttributeError` when it reads `memento.strokes`.
The `strokes` tuple is immutable on its own.
The record adds a second guard by making the attribute that holds it read-only.

### Testing the Sketch

Three tests check the copying:

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

`test_drawing_after_restore_spares_memento()` checks for the sharing bug.
If the memento shares a mutable list with the sketch (see exercise 4),
drawing after a restore appends to the memento's list too.
Both `save()` and `restore()` must copy.

## Immutability

All that copying exists because `Sketch` mutates its list.
Holders can share an immutable state instead of copying it.
When the state is a record, every state is a memento:

```python
# frozen_sketch.py
from dataclasses import replace
from record import record

@record
class Drawing:
    title: str
    strokes: tuple[str, ...] = ()

    def draw(self, stroke: str) -> Drawing:
        return replace(
            self, strokes=(*self.strokes, stroke))

    def __str__(self) -> str:
        drawn = " ".join(self.strokes) or "(blank)"
        return f"{self.title}: {drawn}"
```

`Drawing` is the frozen form of `Sketch`,
under its own name so a reader always knows which one a listing means.
Its extra `title` field lets [a partial restore](#restoring-part-of-a-state)
later in this chapter rewind one field and keep the other.
`draw()` returns a new `Drawing`,
using `dataclasses.replace()` to change one field and copy the rest.

```python
# frozen_demo.py
from frozen_sketch import Drawing

before = Drawing("Duck").draw("circle").draw("beak")
after = before.draw("scribble")
print(after)
#: Duck: circle beak scribble
print(before)
#: Duck: circle beak
```

Saving means keeping a reference,
the assignment that aliased in `aliased_snapshot.py`.
Here that assignment is safe,
because the object bound to `before` keeps its value for as long as it exists.
The frozen version drops the `Memento` class, `save()`, `restore()`,
and the copying.

![](_images/memento_story)

Frames 1 to 3 trace `sketch_demo.py`,
with a copy in each call to `save()` and `restore()`.
Frame 4 traces `frozen_demo.py`,
where saving keeps a reference instead of a copy.
The caretaker keeps `before`.
`draw()` returns `after` as a new object beside it.

`after` shares the two original stroke strings with `before`,
so a history of `Drawing` states stores each stroke once and duplicates only the pointers:

```python
# sharing.py
from frozen_sketch import Drawing

before = Drawing("Duck").draw("circle")
after = before.draw("beak")
print(after.strokes[0] is before.strokes[0])
#: True
print(after.strokes is before.strokes, len(after.strokes))
#: False 2
```

The two objects share the stroke strings, not the tuple holding them.
On a drawing with `n` strokes,
`draw()` builds a new `Drawing` around a fresh tuple of `n + 1` pointers and reuses every existing string.

Each `draw()` builds one such tuple.
A caretaker that keeps every past state keeps every one of those tuples alive,
as the `History` class in `history.py` does.
When a field grows by one element per edit, the way `strokes` does,
the `n`-th edit builds a tuple of `n` pointers,
so `k` edits held in the history cost `O(k^2)` pointers in total, not `O(k)`.
The next listing keeps every state in a list, as a `History` does,
and counts the pointers:

```python
# growth_cost.py
from frozen_sketch import Drawing

states = [Drawing("Duck")]
for i in range(2000):
    states.append(states[-1].draw(str(i)))
print(sum(len(s.strokes) for s in states),
      len(states[-1].strokes))
#: 2001000 2000
```

Two thousand edits held in a `History` cost about two million pointers.
The final `Drawing` alone costs two thousand.

A field keeps the total proportional to `k` when it stays small,
or when each edit replaces it instead of extending it.
For a field that grows with every edit, bound the history's depth
(see exercise 2), coalesce edits before `History` stores them,
use a persistent structure that shares more than a flat tuple,
or switch to *Command*-based undo, which stores an edit instead of a state.

[Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
argues that encapsulation exists mainly because of mutation,
so freezing removes most of the reason for it.
That section's reasoning also makes `strokes` a tuple rather than a list.
Freezing blocks assignment to the field,
not changes to the object the field holds.
A record holding a list therefore lets that list change,
as `frozen_leaky.py` in that chapter shows.

[*Flyweight*](35_Patterns--Flyweight.md)
shares immutable values among objects that exist at once.
*Memento* shares them among successive states.

Two kinds of state still need the classic form.
Because freezing rebuilds the changed field on every edit,
a state too large to copy per keystroke needs a mutable originator and a `save()` the caller invokes.
So does a state whose class belongs to someone else: a widget tree,
a database row, or any object whose class is theirs to design.
Everywhere else, prefer the frozen value.

Two tests check `draw()`:

```python
# test_frozen_sketch.py
from frozen_sketch import Drawing

def test_draw_leaves_old_drawing() -> None:
    before = Drawing("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_draw_keeps_title() -> None:
    assert Drawing("Duck").draw("x").title == "Duck"
```

## The Caretaker: a Generic History

The caretaker reads no field of the states it holds,
since opacity is the pattern's whole point.
That opacity lets a caretaker hold any type of state,
so `History` is [generic](08_Foundations--Static_Types.md#type-parameters)
over the state type.
Undo and redo are two stacks of past and future states:

![](_images/memento_history)

```python
# history.py
from collections.abc import Callable

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

    def apply(self, edit: Callable[[S], S]) -> S:
        self.do(edit(self._present))
        return self._present

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

    def can_undo(self) -> bool:
        return bool(self._past)

    def can_redo(self) -> bool:
        return bool(self._future)
```

```python
# history_frozen.py
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.apply(lambda d: d.draw("circle"))
history.apply(lambda d: d.draw("beak"))
print(history.present)
#: Duck: circle beak
print(history.undo())
#: Duck: circle
print(history.redo())
#: Duck: circle beak
```

`do()` pushes the present onto the past and clears the future,
so an edit after an undo discards the undone states for good,
as it does in editors.

`apply()` exists because `do()` alone leaves work to the caller.
`do()` takes a finished state,
so every call site must build that state from `history.present` and then pass the result to `do()`.
If a call site builds the new state and forgets to pass it to `do()`,
the history stays as it was.
Each state keeps its value, so every other state stays valid.
The program runs on with the history one state short.

`apply()` takes the edit instead of its result.
It reads `present` for the caller and passes the edit's return value to `do()`,
so `apply()` records every state an edit returns.
`do()` stays public for a state built outside an edit of the present,
such as the `Sketch` mementos that `history_classic.py` passes to it below.

`undo()` and `redo()` leave the empty-stack check to the caller.
Undoing an empty past raises `IndexError` from `pop()`.
That `pop()` comes first, so a failed undo leaves the history as it was.
`can_undo()` and `can_redo()` let a caller check first.
An editor calls them to gray out the menu item.

`History` stores whole states and moves them between stacks,
so it accepts any state type, from `int` to a full `Drawing`.
Correct undo requires one thing of a state: immutability.
`History` keeps a reference, not a copy,
so a list mutated in place changes in the past too.
A `History` of lists is a stack of aliases, the bug in `aliased_snapshot.py`.

`History` holds the classic form as well.
Because the classic `Memento` from `sketch.py` is immutable,
the same generic caretaker holds mementos of the mutable `Sketch`.
Where `History` holds each frozen `Drawing` as it is,
a `Sketch` needs `save()` before each `do()` and `restore()` after each `undo()`,
so the code around the `History` calls both:

```python
# history_classic.py
from history import History
from sketch import Memento, Sketch

sketch = Sketch()
sketch.draw("circle")
history: History[Memento] = History(sketch.save())
sketch.draw("beak")
history.do(sketch.save())
print(sketch)
#: circle beak
sketch.restore(history.undo())
print(sketch)
#: circle
```

Four tests check `History`:

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

def test_apply_edits_the_present() -> None:
    history = History("a")
    assert history.apply(lambda s: s + "b") == "ab"
    assert history.present == "ab"
    assert history.undo() == "a"

def test_edit_after_undo_discards_redo() -> None:
    history = History("a")
    history.do("ab")
    history.undo()
    history.do("ax")
    assert not history.can_redo()
    assert history.present == "ax"

def test_can_undo_and_can_redo() -> None:
    history = History(0)
    assert not history.can_undo()
    history.do(1)
    assert history.can_undo() and not history.can_redo()
    history.undo()
    assert history.can_redo() and not history.can_undo()
```

The alternative design stores commands instead of states.
Each undoable action carries its own inverse,
the [*Command* variation](27_Patterns--Function_Objects.md#a-callable-object-as-a-command).
*Command*-based undo saves memory when a snapshot is large,
but needs an inverse written and tested for every action.
Try snapshot-based undo first,
since immutable states share every value an edit carries over,
as `sharing.py` shows.
Switch to *Command* if the `O(k^2)` pointer total that `growth_cost.py` counts grows too large to hold.

## Restoring Part of a State {#restoring-part-of-a-state}

A whole-state snapshot records every field's value at one moment.
An editor's undo is often narrower.
Undo the strokes, but keep the rename.
Because `History` stores and returns whole states and treats each one as opaque,
the state must supply the partial restore.
A state that defines `__replace__()` supplies it through `copy.replace()`:

```python
# partial_restore.py
import copy
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.apply(lambda d: d.draw("circle"))
checkpoint = history.present
history.apply(lambda d: d.draw("beak"))
history.apply(lambda d: copy.replace(d, title="Goose"))
history.apply(lambda d: d.draw("scribble"))
print(history.present)
#: Goose: circle beak scribble
history.apply(lambda d: copy.replace(
    d, strokes=checkpoint.strokes))
print(history.present)
#: Goose: circle
print(history.undo())
#: Goose: circle beak scribble
```

`checkpoint` names a past `Drawing`.
Immutability keeps that name accurate, since the state it names keeps its value.
The restore goes through `apply()` like any other action,
so `history.undo()` takes it back.
The edit that `apply()` receives is a lambda here because a partial restore combines two states,
and each `Drawing` method reads one state, `self`.

`copy.replace()` is the [general version](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
of `dataclasses.replace()`.
Choosing `copy.replace()` over `dataclasses.replace()` keeps the technique available to state types that are not dataclasses.
`NamedTuple`, `datetime`,
and any class defining `__replace__()` all accept `copy.replace()`.

## Mementos That Outlive the Process

A snapshot in memory disappears when the process ends.
The same frozen value, serialized, becomes a saved game, a session file,
or a crash-recovery point.
The standard library's `pickle` turns almost any Python object into bytes and back:

```python
# round_trip.py
import pickle
from frozen_sketch import Drawing

drawing = Drawing("Duck").draw("circle").draw("beak")
restored = pickle.loads(pickle.dumps(drawing))
print(restored == drawing, restored is drawing)
#: True False
```

A record compares by value,
so `restored == drawing` is `True` while `restored is drawing` is `False`.
A different object with the same value is all a memento needs,
so you can write the bytes from `pickle.dumps()` to a file and load them in a different process,
days later.

Only unpickle data you trust, because the format can execute code.
For untrusted storage or other languages,
convert the state with `dataclasses.asdict()` and write JSON (see exercise 3).

### A Class That Changes After the Save

The class can drift between the save and the load.
The bytes encode a class by module and name,
not by the shape that class had at save time.
If the state class gains, loses, or renames a field before the load,
`pickle.loads()` still succeeds.
The error comes later, from the code that reads a field the bytes lack.

`pickle_drift.py` simulates that drift.
`SketchV1` sits in a module of its own because a real class drifts between two runs of a program:

```python
# sketch_v1.py
from record import record

@record(slots=False)
class SketchV1:
    strokes: tuple[str, ...]
```

```python
# sketch_v2.py
from record import record

@record(slots=False)
class SketchV2:
    strokes: tuple[str, ...]
    title: str
```

```python
# pickle_drift.py
import pickle
import sketch_v1
from exceptions import expected
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV1(("circle", "beak")))
sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
with expected(AttributeError):
    print(restored.title)
#: [AttributeError] 'SketchV2' object has no attribute
#: 'title'
```

`sketch_v1.SketchV1 = SketchV2` stands in for an edit and reload of that module,
with a field added between the save and the load.

`ty` and mypy report that reassignment as unsound,
so it carries a `# type: ignore`.
Pyright accepts the reassignment.
No practical annotation declares that `SketchV1` can become a different class.

`pickle.loads()` looks up the class by the name pickle recorded,
`sketch_v1.SketchV1`.
That name is now bound to `SketchV2`.
`pickle.loads()` builds a bare `SketchV2` with `__new__()`,
skipping `__init__()`, and copies in the fields the old bytes had.

Pickle writes the fields into the object's `__dict__`,
bypassing the frozen check.
A record's generated `__setattr__()` raises `FrozenInstanceError`.
Pickle updates `__dict__` without calling `__setattr__()`.
Skipping `__init__()` also skips `__post_init__()`,
so a memento saved before you add validation to a field loads with that field unchecked.

The loaded object carries the one field the old bytes held.
`restored.strokes` works because both versions agree on that field.
`restored.title` raises `AttributeError` when anything reads it,
often far from the line that called `pickle.loads()`.
Pickle's convenience comes from leaving two jobs to you:
matching the class on load to the class on save,
and rerunning the validation that the load skips.

### A Deleted Field Leaves a Ghost

Deleting a field passes silently.
The old bytes load, and every later read succeeds.
`pickle.loads()` writes the dropped name into the object's `__dict__` as a ghost attribute.
The ghost sits outside the class's declared fields,
so `repr()` omits it and `==` ignores it,
while `getattr()` still finds it in `__dict__`.
The loaded object equals one built fresh from `SketchV1` and hashes the same.

The added-field drift in `pickle_drift.py` raises `AttributeError` when something reads the new field.
The deleted-field drift stays silent,
and reading the deleted `title` returns stale data.
Running the same reassignment backwards shows the deleted field:

```python
# ghost_field.py
import pickle
import sketch_v2
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV2(("circle",), "Duck"))
sketch_v2.SketchV2 = SketchV1  # type: ignore
restored = pickle.loads(blob)
print(restored)
#: SketchV1(strokes=('circle',))
print(restored.title)
#: Duck
print(restored.__dict__)
#: {'strokes': ('circle',), 'title': 'Duck'}
print(restored == SketchV1(("circle",)))
#: True
```

Renaming a field is a delete and an add at once, with both effects.
The old name becomes a ghost, and the new one is missing,
so the generated `repr()` raises `AttributeError`.

These listings use `@record(slots=False)` so the loaded object has a `__dict__` to hold the ghost.
A slotted record pickles its field values as a list in field order,
and the load assigns that list to the current class's fields by position.
When the deleted field is the last one, the load drops its value.
A field deleted from the middle shifts every later value into the wrong field.
A `title`, `strokes`,
`color` record that loses `strokes` loads the old strokes tuple as its `color`,
and the load still succeeds.

### Schema Migrations and Safer Formats

Databases have the same drift.
Their remedy, a *schema migration*, makes the drift deliberate:
a versioned step that changes the table shape and its data together,
instead of leaving a query to fail on the mismatch.

When drift or the security risk is too much to accept,
other libraries address both.
`msgspec` and `pydantic` both validate on load.
A shape mismatch raises the library's `ValidationError` inside the load call,
instead of the delayed `AttributeError` from `pickle_drift.py`.
Protocol Buffers goes further.
A schema shared across languages gives every field a number written in the schema.
Old and new versions can then read each other's messages by design.
All three treat the bytes as data rather than as instructions,
which removes pickle's security risk.

## Snapshots in the Wild

Version control applies the *Memento* pattern to files.
A git commit is an immutable snapshot of your whole tree,
and checkout is `restore()`.
Git shares unchanged content between commits just as the immutable `Drawing` states in `History` share their unchanged strokes.
Databases provide savepoints, mementos scoped to a transaction.
Multiplayer games snapshot the world so they can rewind and replay when a late packet arrives.
Whenever you see rewind, rollback, or restore, something produces mementos.

## Exercises

Try each exercise before opening its [solution](../Solutions/36_Patterns--Memento/).

1.  Add `erase()` to both `Sketch` and `Drawing`.
    It removes the last stroke.
    In `sketch.py` it mutates.
    In `frozen_sketch.py` it returns a new `Drawing`.
    Write tests proving existing mementos and histories stay unchanged in each version.
2.  Give `History` a maximum depth.
    When the past grows beyond `n` states, discard the oldest.
    What should `can_undo()` report then?
3.  Serialize a `Drawing` to JSON using `dataclasses.asdict()` and reconstruct it.
    What did the round trip change that `pickle` preserved,
    and where must your reconstruction compensate?
4.  Change `sketch.py` so `Memento` holds the list itself instead of a tuple copy,
    and so `restore()` assigns that list rather than copying it,
    leaving the sketch and the memento sharing one list in both directions.
    Then write the test that exposes the corruption.
    Which of the three tests in `test_sketch.py` catches it first?
5.  Add `goto(steps_back)` to `History`:
    jump the present several states into the past in one call,
    keeping redo consistent.
6.  A `History` of `Drawing` states records a rename and three strokes.
    Write `restore_field(history, name, past)` that pushes a new state taking one named field from `past` and the rest from `history.present`.
    Why must it go through `do()` rather than editing `_past` directly?
7.  Save two `Drawing`s with `pickle`, one of them with an empty title,
    then add a field with a default to `Drawing` and load the old bytes.
    Does the default appear?
    Now add a `__post_init__()` that rejects an empty title,
    and load the blank one again.
    What did pickle skip, and what does `copy.replace()` catch?
