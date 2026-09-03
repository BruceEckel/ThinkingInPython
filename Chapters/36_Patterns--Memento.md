# Memento

Undo is a feature users expect and programmers dread.
It requires a program to capture an object's state at one moment and restore it later.
The *Memento* pattern does this without breaking encapsulation.
The *originator* (the object with state) produces a *memento*,
an opaque snapshot of itself.
A *caretaker* (the undo machinery)
stores mementos and hands one back when asked, without looking inside.

The pattern exists because of mutation.
An object that changes in place destroys its own past,
so you must copy the past and guard it.
Python has the classic form when you need it,
and immutable state removes the need.

## A Snapshot Is Not a Reference

Aliasing and copying return from [Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution),
because Memento lives or dies by them.
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
so the "snapshot" mutates along with the original.
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
print(todo)
#: [['eggs', 'milk', 'cheese', 'jam'], ['bread']]
print(deep)
#: [['eggs', 'milk', 'cheese'], ['bread']]
```

`list(todo)` copies the outer list,
so `shallow` and `todo` are different objects.
But their elements are the same inner lists,
so `todo[0].append("cheese")` shows up in `shallow` too.
`copy.deepcopy()` walks the whole structure and rebuilds every nested container from scratch,
so `deep`'s inner lists share nothing with `todo`'s.
The later `todo[0].append("jam")` reaches `todo` but never `deep`.
That walk costs time and memory proportional to the whole nested structure it rebuilds,
not just the part that changed,
which is the price `sketch.py` pays below for a state that nests containers inside containers.

## The Classic Memento

Every classic memento, as *GoF Design Patterns* presents the pattern,
is some version of copying the state before it changes.
Here the originator is a `Sketch` that accumulates strokes in a list.
Its memento converts that list to a tuple,
so the snapshot is immutable even though the originator is not.
`restore()` copies in the other direction,
rebuilding a fresh list so the sketch and the memento never share one.
One level is enough because a stroke is a string.
An originator holding containers inside containers needs `copy.deepcopy()` in `save()`,
at the cost the previous section showed:

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
Whoever holds `checkpoint` stores it and gives it back,
and never reaches inside to edit the strokes.
Languages with access control enforce that restraint.
In Python it is a convention,
though freezing the memento means an accidental edit
(swapping the snapshot's strokes for different ones) fails loudly.

You could skip the class and write `type Memento = tuple[str, ...]`.
Every call site would still type-check.
But an alias creates no new type.
Any `tuple[str, ...]` in the program satisfies it,
including one a caretaker builds or unpacks by hand.
`NewType("Memento", tuple[str, ...])` exists only for the type checker.
It vanishes at runtime, so the caretaker still holds a plain tuple it can index,
unpack, or build from scratch.
Wrapping the tuple in a one-field data class gives `Memento` an identity that exists while the program runs.
A parameter typed `tuple[str, ...]` still accepts any tuple of strings,
whatever built it.
A parameter typed `Memento` does not:
only code that already imports `Memento` and constructs one correctly can satisfy it,
so the type checker catches a caretaker that passes the wrong tuple by mistake.
`frozen=True` makes reassigning `checkpoint.strokes` fail at runtime instead of silently succeeding.
Neither guarantee stops code holding a `Memento` from reading `.strokes`, unpacking it, or building one by hand;
that boundary is still a convention, the one the classic pattern always relied on.
What changes is the accidental case, a caretaker that mixes up a `Memento` with some other tuple:

```python
# memento_type_safety.py
from dataclasses import FrozenInstanceError
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
try:
    restore_memento(("unrelated", "tuple"))  # type: ignore
except AttributeError as e:
    print(e)
#: 'tuple' object has no attribute 'strokes'

try:
    # ty: strokes is read-only on Memento:
    checkpoint.strokes = ("forged",)  # type: ignore
except FrozenInstanceError as e:
    print(type(e).__name__)
#: FrozenInstanceError
```

`restore_tuple()` accepts either tuple without complaint, since both are `tuple[str, ...]`.
`restore_memento()` accepts the checkpoint,
and the type checker flags the plain tuple before the program runs;
run anyway, it fails at the first line that expects `.strokes`.
Reassigning `checkpoint.strokes` fails too,
for the same reason: the attribute, not just the tuple inside it, is frozen.

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
drawing after a restore corrupts the snapshot.
Both `save()` and `restore()` must copy.

## Immutability

All of that copying defends against mutation.
If you remove the mutation, nothing remains to prevent.
Once the state is a frozen data class, every state is a memento:

```python
# frozen_sketch.py
from dataclasses import dataclass, replace

@dataclass(frozen=True)
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

`Drawing` is the same idea as `Sketch` with the mutation removed,
under a different name so a reader never has to ask which one a listing means.
Its extra `title` field lets a later section restore one field and keep the other.
`draw()` returns a new `Drawing` instead of editing this one,
using `dataclasses.replace()` to change one field and carry the rest along.
Since each call returns a `Drawing`, the calls chain.
Saving means keeping a reference, the move that failed in `aliased_snapshot.py`.
Now it is safe because no operation anywhere can change the object bound to `before`.
No `Memento` class exists, no `save()`, no `restore()`,
and no copying to protect the past.
`after` shares the two original stroke strings with `before`,
which is why a whole history of them stays cheap:

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
Each `draw()` builds a fresh tuple of `n + 1` pointers and copies nothing else,
so one `draw()` costs pointers proportional to the current length of `strokes`, not the whole `Drawing`.
The stroke comes from `"".join([...])` rather than the literal `"circle"` because the compiler interns a literal,
and interning would make the identity check print `True` even for a copied string.

A single `draw()` is cheap.
A `History` that keeps every past state is not, once a field grows by accretion the way `strokes` does:
edit `n` costs `n` pointers, so `k` edits held in `_past` cost `O(k^2)` pointers in total, not `O(k)`.

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
A field that stays small, or that replaces instead of growing, never reaches this cost.
For one that grows without bound,
bound the history's depth (exercise 2 asks for exactly this),
coalesce edits before they reach `History`,
use a persistent structure that shares more than a flat tuple can,
or fall back to Command-based undo, which stores an edit instead of a state.

[Rethinking Objects](20_Patterns--Rethinking_Objects.md#the-immutability-solution)
makes this argument about sharing.
That section also explains why `strokes` is a tuple rather than a list:
`frozen=True` guards the binding, not the object,
so a frozen data class holding a list still lets that list change underneath it,
as `frozen_leaky.py` shows there.
[Flyweight](35_Patterns--Flyweight.md) shares immutable values across space,
and Memento shares them across time.

The classic form has not disappeared.
It has narrowed.
Freezing rebuilds the changed field on every edit,
so a state too large to copy per keystroke still needs a mutable originator and an explicit `save()`.
So does a state you do not own: a widget tree, a database row,
or any object whose class you cannot redesign.
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

The caretaker needs to know nothing about the states it holds,
frozen or not: opacity is the pattern's whole point,
and `History[S]` below works unchanged on the classic `Memento` from `sketch.py`.
What immutability buys is not opacity, which the classic form always had,
but freedom from an explicit `save()` and `restore()` at every edit,
since a state that already cannot change is already a memento.
Undo and redo are two stacks of past and future states,
generic over the state type
(the `class History[S]` syntax is from [Static Types](08_Foundations--Static_Types.md#generic-functions-and-classes)):

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
    from frozen_sketch import Drawing
    history = History(Drawing("Duck"))
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
Redo can no longer reach the states you undid, which is how editors behave.
`undo()` and `redo()` just shuttle the present between the two stacks.
Every change must go through `do()`.
Build a new state from `history.present` and keep it without handing it back,
and the history omits it; because nothing mutates,
every other state stays valid and the gap goes unnoticed.
`undo()` and `redo()` check no precondition of their own:
undoing with no past raises `IndexError` from `pop()`.
`can_undo()` and `can_redo()` exist so callers ask first,
which is how an editor knows to gray out the menu item.
`History` stores whole states, not descriptions of changes,
so it never interprets anything.
That works for any state type, from `int` to a full `Drawing`,
with one condition: states must be immutable.
`History` cannot protect a list that someone mutates in place.
A `History` of lists is a stack of aliases, the bug that opened this chapter.

`History` does not require a frozen state class either.
The classic `Memento` from `sketch.py` is already immutable,
so the same generic caretaker drives the mutable `Sketch` it snapshots,
calling `save()` and `restore()` where `frozen_sketch.py`'s version needed neither:

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
the Command variation that [Function Objects](28_Patterns--Function_Objects.md)
mentions.
Command-based undo saves memory when a snapshot is large,
at the cost of writing and testing an inverse for every action.
Try snapshot-based undo first:
immutable states make one edit inexpensive, as `sharing.py` showed,
and switch to Command once `growth_cost.py`'s `O(k^2)` starts to matter.

## Restoring Part of a State {#restoring-part-of-a-state}

A whole-state snapshot answers one question: what did everything look like then?
Editors face a narrower one.
Undo the drawing, but keep the rename.
`History` cannot express that,
because it moves whole states and never looks inside them.
The answer has to come from the state itself,
and for a state that defines `__replace__()`, `copy.replace()` supplies it:

```python
# partial_restore.py
import copy
from frozen_sketch import Drawing
from history import History

history = History(Drawing("Duck"))
history.do(history.present.draw("circle"))
checkpoint = history.present
history.do(history.present.draw("beak"))
history.do(copy.replace(history.present, title="Goose"))
history.do(history.present.draw("scribble"))
print(history.present)
#: Goose: circle beak scribble
history.do(copy.replace(history.present,
                        strokes=checkpoint.strokes))
print(history.present)
#: Goose: circle
print(history.undo())
#: Goose: circle beak scribble
```

`checkpoint` names a past `Drawing`,
and naming a past state is the whole trick immutability makes possible.
The restore takes the strokes from that past state and the title from the present one,
producing a state that never existed before.
It goes through `do()` like any other action,
so the partial restore is undoable, as the last line shows.

`copy.replace()` is the general version of `dataclasses.replace()`,
which [Data Classes as Types](12_Techniques--Data_Classes_as_Types.md#the-general-form-of-replace)
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

The bytes from `pickle.dumps()` can go to a file and come back in a different process,
days later.
The round trip produces a different object with the same value,
which is all a memento needs, since a data class compares by value.

Only unpickle data you trust, because the format can execute code.
For untrusted storage or other languages,
convert the state with `dataclasses.asdict()` and write JSON,
which exercise 3 explores.

Pickle's other limitation is time.
The bytes encode a class by module and name,
not by the shape that class had at save time.
If the state class gains, loses, or renames a field before the load,
`pickle.loads()` still succeeds.
What breaks is whatever later touches a field the bytes never carried.
The listing simulates that drift,
and puts the class in its own module because in reality a class drifts between two runs of a program,
not inside one script:

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
from sketch_v1 import SketchV1
from sketch_v2 import SketchV2

blob = pickle.dumps(SketchV1(("circle", "beak")))
sketch_v1.SketchV1 = SketchV2  # type: ignore
restored = pickle.loads(blob)
print(restored.strokes)
#: ('circle', 'beak')
try:
    print(restored.title)
except AttributeError as e:
    print(e)
#: 'SketchV2' object has no attribute 'title'
```

The dump that builds `blob` runs while `sketch_v1.SketchV1` still means the one-field class.
`sketch_v1.SketchV1 = SketchV2` stands in for an edit and reload of that module,
with a field added between the save and the load.
The type checker flags that reassignment as unsound,
so it carries a `# type: ignore`.
No practical annotation declares that `SketchV1` can become a different class.
`pickle.loads()` looks up the class by the name pickle recorded,
`sketch_v1.SketchV1`.
That name now points at `SketchV2`.
`pickle.loads()` builds a bare `SketchV2`, skipping `__init__()`,
and copies in only the fields the old bytes had.
The fields go straight into the object's `__dict__`,
so `frozen=True` stays out of the way: freezing guards attribute assignment,
and pickle writes the dictionary directly.
`title` is absent, since the old bytes never had one.
The same shortcut skips `__post_init__()`,
so a memento saved before a validated field existed can load a value nothing ever validated.
`restored.strokes` works because both versions agree on that field.
`restored.title` fails if anything asks for it,
which is often nowhere near the line that called `pickle.loads()`.
Pickle is convenient because it hides this contract.
Nothing enforces that the class on load matches the class on save.

Drift in the other direction is quieter still.
If you delete a field, the old bytes load with no error anywhere.
The dropped name arrives in the object's `__dict__` as a ghost attribute,
readable but invisible to the class definition,
so `repr()` omits it and `==` ignores it.
The loaded object is equal to, and hashes the same as,
one built fresh without that field.
The added-field drift above at least fails when something touches the gap.
This one never raises an exception.
The data is quietly wrong.
Renaming a field is a delete and an add at once, and does both:
the old name becomes a ghost and the new one is missing,
so even `repr()` raises `AttributeError`.
Running the same substitution backwards shows the quiet case:

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
The `repr()` shows a one-field object while the `__dict__` shows two entries,
and the loaded object is `==` to a `SketchV1` that never had a title,
so nothing downstream can tell them apart.

Databases hit the same problem and gave it a name.
A *schema migration* is the disciplined version of this drift, a versioned,
deliberate step that moves the table shape and its data forward together,
instead of discovering the mismatch when a query runs.

When either limitation rules out `pickle`,
other libraries answer drift and security separately.
`msgspec` and `pydantic` both validate on load.
A shape mismatch raises a clear error at the boundary,
instead of the delayed `AttributeError` from `pickle_drift.py`.
Protocol Buffers goes further.
A schema shared across languages gives every field an explicit, numbered slot.
Old and new versions can then read each other's messages on purpose,
not by accident.
None of the three execute the bytes they read,
so none carry pickle's security risk either.

## Snapshots in the Wild

Version control is the Memento pattern at industrial scale.
A git commit is an immutable snapshot of your whole tree,
checkout is `restore()`,
and git shares unchanged content between commits just as the immutable `Drawing` states in `History` share their unchanged strokes.
Databases hand out savepoints, mementos scoped to a transaction.
Multiplayer games snapshot the world so they can rewind and replay when a late packet arrives.
Whenever you see rewind, rollback, or restore, something is producing mementos.

## Exercises

1.  Add `erase()` to both sketches.
    It removes the last stroke.
    In `sketch.py` it mutates.
    In `frozen_sketch.py` it returns a new `Drawing`.
    Write tests proving existing mementos and histories survive untouched in each version.
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
    What did pickle skip, and what would `copy.replace()` have caught?
