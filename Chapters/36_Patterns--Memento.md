# Memento

Undo is a feature users expect and programmers dread.
It requires a program to capture an object's state at one moment and restore it later.
The *Memento* pattern captures and restores that state without breaking encapsulation.
The *originator* (the object with state) produces a *memento*,
an opaque snapshot of itself.
A *caretaker* (the undo machinery) stores mementos and returns one on request,
without reading its contents.

![`Sketch` names `Memento`, and `History` names only a type parameter, so it holds a `Memento` without reading it](_images/coupling_36)

The pattern exists because of mutation.
An object that changes in place overwrites its earlier state,
so you must copy that state before the change and keep the copy from changing.
Python has the classic form when you need it,
and immutable state removes the need.

## A Snapshot Is Not a Reference

Aliasing and copying return from [Rethinking Objects](20_Patterns--Rethinking_Objects.md#encapsulation-leaks),
because a memento works only when it is a copy and fails when it is an alias.
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

`saved = todo` binds a second name to the same list,
so every later append to `todo` appears in `saved`.
`list(todo)` makes a real copy,
and later appends to `todo` leave `copied` as it was.
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
`copy.deepcopy()` walks the whole structure and creates a new copy of every nested container,
so `deep`'s inner lists are new objects of its own.
The later `todo[0].append("jam")` changes `todo`'s inner list,
and `deep`'s keeps its three elements.
That walk costs time and memory proportional to the whole nested structure it rebuilds,
however small the change.
`sketch.py` below copies one level and pays for one level;
a state that nests containers inside containers copies the whole structure on every save.

## The Classic Memento

As *GoF Design Patterns* presents the pattern,
every classic memento is some version of copying the state before it changes.
Here the originator is a `Sketch` that accumulates strokes in a list.
Its memento converts that list to a tuple,
so the snapshot is immutable while the originator stays mutable.
`restore()` copies in the other direction,
rebuilding a fresh list so the sketch and the memento never share one.
One level is enough because a stroke is a string.
An originator holding containers inside containers needs `copy.deepcopy()` in `save()`,
and pays the cost described in [A Snapshot Is Not a Reference](#a-snapshot-is-not-a-reference):

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

The caretaker's side of the contract is to store `checkpoint` and return it,
and never to read or assign its `strokes`.
Languages with access control enforce that rule.
In Python it is a convention,
though freezing the memento turns an accidental edit into an exception:
assigning different strokes to the snapshot raises a `FrozenInstanceError`.

### Why `Memento` Is a Class

You could replace the class with `type Memento = tuple[str, ...]`.
Every call site still type-checks.
But an alias creates no new type.
Any `tuple[str, ...]` in the program satisfies it,
including one a caretaker builds or unpacks by hand.
`NewType("Memento", tuple[str, ...])` exists only for the type checker.
At runtime it is a function that returns its argument,
so the caretaker still holds a plain tuple it can index, unpack,
or build from scratch.

Wrapping the tuple in a one-field data class makes `Memento` a class of its own at runtime.
A parameter typed `tuple[str, ...]` still accepts any tuple of strings,
whatever built it.
A parameter typed `Memento` accepts the class alone,
so the type checker reports a caretaker that passes some other tuple by mistake.
Building a `Memento` takes an import of the class and a call to it,
so no caretaker makes one by accident.
`Memento` is a [record](18_Techniques--Performance.md#record),
so reassigning `checkpoint.strokes` raises `FrozenInstanceError` at runtime.
Neither the checker's report nor the frozen field stops code holding a `Memento` from reading `.strokes`,
unpacking that tuple, or building a `Memento` by hand;
that boundary remains a convention,
the one the classic pattern always relied on.
What changes is the accidental case,
a caretaker that mixes up a `Memento` with some other tuple:

```python
# memento_type_safety.py
from dataclasses import FrozenInstanceError
from exceptions import expect, expected
from sketch import Memento, Sketch

def restore_tuple(strokes: tuple[str, ...]) -> None:
    print(strokes)

def restore_memento(memento: Memento) -> None:
    print(memento.strokes)

sketch = Sketch()
sketch.draw("circle")
checkpoint = sketch.save()

restore_tuple(checkpoint.strokes)
#: ('circle',)
restore_tuple(("unrelated", "tuple"))
#: ('unrelated', 'tuple')

restore_memento(checkpoint)
#: ('circle',)
# ty: tuple[str, str] is not a Memento:
expect(AttributeError, restore_memento,
       ("unrelated", "tuple"))  # type: ignore
#: [AttributeError] 'tuple' object has no attribute
#: 'strokes'

with expected(FrozenInstanceError):
    # ty: strokes is read-only on Memento:
    checkpoint.strokes = ("forged",)  # type: ignore
#: [FrozenInstanceError] cannot assign to field 'strokes'
```

`restore_tuple()` accepts either tuple, since both are `tuple[str, ...]`.
`restore_memento()` accepts the checkpoint,
and the type checker reports the plain tuple before the program runs.
If you run the program anyway,
it raises `AttributeError` at the first line that reads `.strokes`.
The checker rejects the assignment to `checkpoint.strokes` too,
and the runtime raises `FrozenInstanceError`.
A record freezes the attribute, not just the tuple inside it.

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

The third test checks for the sharing bug.
If the memento shares a mutable list with the sketch,
as in the variant that exercise 4 explores,
drawing after a restore appends to the snapshot's list too.
Both `save()` and `restore()` must copy.

## Immutability

All of that copying exists because `Sketch` mutates its list.
A state that never mutates needs no copy.
Once the state is a record, every state is a memento:

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

if __name__ == "__main__":
    before = Drawing("Duck").draw("circle").draw("beak")
    after = before.draw("scribble")
    print(after)
    print(before)
#: Duck: circle beak scribble
#: Duck: circle beak
```

`Drawing` is the frozen form of `Sketch`,
under its own name so a reader always knows which one a listing means.
Its extra `title` field lets [a partial restore](#restoring-part-of-a-state)
later in this chapter rewind one field and keep the other.
`draw()` returns a new `Drawing`,
using `dataclasses.replace()` to change one field and copy the rest.
Since each call returns a `Drawing`, the calls chain.
Saving means keeping a reference,
the assignment that aliased in `aliased_snapshot.py`.
Here that assignment is safe because the object bound to `before` keeps its value for as long as it exists,
so the `Memento` class, `save()`, `restore()`, and the copying are all gone.
`after` shares the two original stroke strings with `before`,
so a history of `Drawing` states stores each stroke once and duplicates only the pointers:

```python
# sharing.py
from frozen_sketch import Drawing

stroke = "".join(["cir", "cle"])
before = Drawing("Duck", (stroke,))
after = before.draw("beak")
print(after.strokes[0] is stroke)
#: True
print(after.strokes is before.strokes, len(after.strokes))
#: False 2
```

The two objects share the stroke strings, not the tuple holding them.
Each `draw()` builds a fresh tuple of `n + 1` pointers,
and that tuple is its whole cost,
proportional to the current length of `strokes`.
The stroke comes from `"".join([...])` because the compiler interns a literal like `"circle"`,
and interning makes the identity check print `True` for a copied string too.

A single `draw()` allocates one tuple.
A caretaker that keeps every past state, the `History` class in `history.py`,
keeps every one of those tuples alive.
Once a field grows by one element per edit, the way `strokes` does,
the `n`-th edit builds a tuple of `n` pointers,
so `k` edits held in the history cost `O(k^2)` pointers in total, not `O(k)`.

```python
# growth_cost.py
from frozen_sketch import Drawing

drawing = Drawing("Duck")
pointers = 0
for i in range(2000):
    drawing = drawing.draw(str(i))
    pointers += len(drawing.strokes)
print(pointers, len(drawing.strokes))
#: 2001000 2000
```

Two thousand edits held in a `History` cost about two million pointers;
the final `Drawing` alone costs two thousand.
A field that stays small, or that each edit replaces instead of extends,
keeps the total proportional to `k`.
For one that grows with every edit, bound the history's depth
(exercise 2 asks for exactly this), coalesce edits before `History` stores them,
use a persistent structure that shares more than a flat tuple can,
or switch to *Command*-based undo, which stores an edit instead of a state.

[Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
argues that freezing removes what encapsulation protected.
That section also explains why `strokes` is a tuple rather than a list:
freezing blocks assignment to the field,
not changes to the object the field holds,
so a record holding a list lets that list change,
as `frozen_leaky.py` shows there.
[*Flyweight*](35_Patterns--Flyweight.md)
shares immutable values among objects that exist at once,
and *Memento* shares them among successive states.

Two kinds of state keep the classic form.
Freezing rebuilds the changed field on every edit,
so a state too large to copy per keystroke needs a mutable originator and an explicit `save()`.
So does a state whose class belongs to someone else: a widget tree,
a database row, or any object whose class is theirs to design.
Everywhere else, prefer the frozen value.

```python
# test_frozen_sketch.py
from frozen_sketch import Drawing

def test_draw_returns_new_drawing() -> None:
    before = Drawing("Duck").draw("circle")
    after = before.draw("beak")
    assert before.strokes == ("circle",)
    assert after.strokes == ("circle", "beak")

def test_replace_carries_other_fields() -> None:
    assert Drawing("Duck").draw("x").title == "Duck"
```

## The Caretaker: a Generic History

The caretaker reads no field of the states it holds, frozen or mutable,
since opacity is the pattern's whole point.
`History[S]` below works as written on the classic `Memento` from `sketch.py`,
because the classic form already has opacity.
What immutability removes is the explicit `save()` and `restore()` at every edit,
since a state that keeps its value is already a memento.
Undo and redo are two stacks of past and future states,
generic over the state type
(the `class History[S]` syntax is from [Static Types](08_Foundations--Static_Types.md#type-parameters)):

![History moves the present between two stacks, _past and _future](_images/memento_history)

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

if __name__ == "__main__":
    from frozen_sketch import Drawing
    history = History(Drawing("Duck"))
    history.apply(lambda d: d.draw("circle"))
    history.apply(lambda d: d.draw("beak"))
    print(history.present)
    print(history.undo())
    print(history.redo())
#: Duck: circle beak
#: Duck: circle
#: Duck: circle beak
```

`do()` pushes the present onto the past and clears the future,
so an edit after an undo discards the undone states.
Redo can no longer restore them, and editors behave the same way.
`undo()` and `redo()` each pop one stack, push the present onto the other,
and make the popped state the present.

`apply()` exists because `do()` alone leaves work to the caller.
`do()` takes a finished state,
so every call site must build that state from `history.present` and then pass the result to `do()`.
If you build a new state and keep it in a variable of your own,
the history stays as it was.
Nothing mutates, so every other state stays valid,
and the program runs on with the history one state short.
`apply()` takes the edit instead of its result.
It reads `present` itself and passes whatever the edit returns straight to `do()`,
so both steps happen at every call site.
`do()` stays public for a state that other code builds,
as `history_classic.py` shows below.

`undo()` and `redo()` trust the caller:
undoing an empty past raises `IndexError` from `pop()`.
That `pop()` comes first, so an undo that raises leaves the history as it was.
`can_undo()` and `can_redo()` exist so a caller checks first;
an editor calls them to gray out the menu item.

`History` stores whole states and moves them between stacks,
so it works for any state type, from `int` to a full `Drawing`,
with one condition: states must be immutable.
`History` keeps a reference, not a copy,
so a list mutated in place changes in the past too.
A `History` of lists is a stack of aliases, the bug that opens this chapter.

`History` holds the classic form as well.
The classic `Memento` from `sketch.py` is already immutable,
so the same generic caretaker holds snapshots of the mutable `Sketch`.
The surrounding code calls `save()` and `restore()`,
the two calls a frozen state makes redundant:

```python
# history_classic.py
from history import History
from sketch import Memento, Sketch

sketch = Sketch()
sketch.draw("circle")
history: History[Memento] = History(
    sketch.save())
sketch.draw("beak")
history.do(sketch.save())
sketch.restore(history.undo())
print(sketch)
#: circle
```

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
the *Command* variation that [Function Objects](28_Patterns--Function_Objects.md#a-callable-object-as-a-command)
mentions.
*Command*-based undo saves memory when a snapshot is large,
but needs an inverse written and tested for every action.
Try snapshot-based undo first,
since immutable states share every value an edit carries over,
as `sharing.py` shows.
Switch to *Command* once the `O(k^2)` pointers `growth_cost.py` counts grow too large to hold.

## Restoring Part of a State {#restoring-part-of-a-state}

A whole-state snapshot answers one question: what was every field's value then?
An editor's undo is often narrower.
Undo the drawing, but keep the rename.
`History` cannot express that,
because it stores and returns whole states and reads no field of them.
The answer has to come from the state itself,
and for a state that defines `__replace__()`, `copy.replace()` supplies it:

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

`checkpoint` names a past `Drawing`, and immutability keeps that name accurate,
since the state it names keeps its value.
The restore takes the strokes from that past state and the title from the present one,
producing a state new to the history.
The restore goes through `apply()` like any other action, and so is undoable,
as the last line shows.
The edit that `apply()` receives is a lambda here because a partial restore combines two states,
and every method on `Drawing` works from one.

`copy.replace()` is the general version of `dataclasses.replace()`,
as [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
describes.
`copy.replace()` rather than the `dataclasses` one keeps the technique available to whatever state type a `History` holds:
`NamedTuple`, `datetime`, and any class defining `__replace__()` all accept it.

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

You can write the bytes from `pickle.dumps()` to a file and load them in a different process,
days later.
The round trip produces a different object with the same value,
which is all a memento needs, since a data class compares by value.

Only unpickle data you trust, because the format can execute code.
For untrusted storage or other languages,
convert the state with `dataclasses.asdict()` and write JSON,
which exercise 3 explores.

### A Class That Changes After the Save

The class can drift between the save and the load.
The bytes encode a class by module and name,
not by the shape that class had at save time.
If the state class gains, loses, or renames a field before the load,
`pickle.loads()` still succeeds.
The error comes later, from whatever reads a field the bytes never carried.
`pickle_drift.py` simulates that drift.
`SketchV1` sits in a module of its own because in reality a class drifts between two runs of a program:

```python
# sketch_v1.py
from dataclasses import dataclass

@dataclass(frozen=True)
class SketchV1:
    strokes: tuple[str, ...]
```

```python
# sketch_v2.py
from dataclasses import dataclass

@dataclass(frozen=True)
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

The dump that builds `blob` runs while `sketch_v1.SketchV1` means the one-field class.
`sketch_v1.SketchV1 = SketchV2` stands in for an edit and reload of that module,
with a field added between the save and the load.
`ty` and mypy report that reassignment as unsound,
so it carries a `# type: ignore`.
Pyright lets the reassignment pass.
No practical annotation declares that `SketchV1` can become a different class.

`pickle.loads()` looks up the class by the name pickle recorded,
`sketch_v1.SketchV1`.
That name is now bound to `SketchV2`.
`pickle.loads()` builds a bare `SketchV2` with `__new__()`,
skipping `__init__()`, and copies in the fields the old bytes had.
The fields go straight into the object's `__dict__`, past the frozen check:
`frozen=True` installs a `__setattr__()` that raises `FrozenInstanceError`,
and pickle writes `__dict__` directly.
The same shortcut skips `__post_init__()`,
so a memento saved before a field gained its validation loads a value that the validation never saw.
`title` is absent, since the old bytes never had one.
`restored.strokes` works because both versions agree on that field.
`restored.title` raises `AttributeError` when anything reads it,
often far from the line that called `pickle.loads()`.
Pickle's convenience comes from leaving this contract unstated:
matching the class on load to the class on save is your job.

### A Deleted Field Leaves a Ghost

Deleting a field raises no exception at all: the old bytes load,
and every later read succeeds.
`pickle.loads()` writes the dropped name into the object's `__dict__` as a ghost attribute.
The class declares no such field,
so `getattr()` finds it while `repr()` omits it and `==` ignores it.
The loaded object equals one built fresh from `SketchV1` and hashes the same.
The added-field drift in `pickle_drift.py` raises `AttributeError` when something reads the new field.
This one raises nothing, and the data is wrong.
Renaming a field is a delete and an add at once, with both effects.
The old name becomes a ghost, and the new one is missing,
so `repr()` itself raises `AttributeError`.
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
print(restored.__dict__)
#: {'strokes': ('circle',), 'title': 'Duck'}
print(restored == SketchV1(("circle",)))
#: True
```

Each print contradicts the one before it.
The `repr()` shows a one-field object while the `__dict__` shows two entries.
The loaded object is `==` to a `SketchV1` built with strokes alone,
so every later comparison treats them as the same.

### Schema Migrations and Safer Formats

Databases have the same drift, and its remedy there has a name.
A *schema migration* is the disciplined version of this drift, a versioned,
deliberate step that changes the table shape and its data together,
instead of letting a query discover the mismatch.

When drift or the security risk is too much to accept,
other libraries handle the two separately.
`msgspec` and `pydantic` both validate on load.
A shape mismatch raises a clear error at the boundary,
instead of the delayed `AttributeError` from `pickle_drift.py`.
Protocol Buffers goes further.
A schema shared across languages gives every field an explicit number.
Old and new versions can then read each other's messages by design.
All three read the bytes as data and never run code from them,
so pickle's security risk does not apply.

## Snapshots in the Wild

Version control is the *Memento* pattern applied to a whole file tree.
A git commit is an immutable snapshot of your whole tree,
and checkout is `restore()`.
Git shares unchanged content between commits just as the immutable `Drawing` states in `History` share their unchanged strokes.
Databases provide savepoints, mementos scoped to a transaction.
Multiplayer games snapshot the world so they can rewind and replay when a late packet arrives.
Whenever you see rewind, rollback, or restore, something is producing mementos.

## Exercises

1.  Add `erase()` to both sketches.
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
