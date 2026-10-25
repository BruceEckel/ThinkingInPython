# Data Transfer Objects: Solutions

## 1. Two `Messenger`s do not share attributes

> In `messenger_idiom.py`,
> create a second `Messenger` with different keyword arguments and confirm each instance keeps its own attributes
> (unlike a [class attribute](../../Chapters/09_Foundations--Class_Attributes.md)).

<details>
<summary>Where to look</summary>

[A Hand-Rolled *Messenger*](../../Chapters/28_Patterns--Data_Transfer_Objects.md#a-hand-rolled-messenger)
shows `__init__()` assigning the keyword arguments to `self.__dict__`.
Build two instances with different keywords,
then compare what `hasattr()` reports for each name on each instance.
Ask where each instance keeps its dictionary.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        ...
```

<details>
<summary>Done when</summary>

each `Messenger` prints the values of its own keyword arguments,
and `hasattr()` reports `False` on each instance for a name passed to the other instance alone.
You can say where each instance keeps its attributes and why a class attribute behaves differently.

<details>
<summary>Solution</summary>

```python
# exercise_1.py
from typing import Any

class Messenger:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__ = kwargs

m1: Any = Messenger(info="hi", count=3)
m2: Any = Messenger(name="Bob", age=30)
print(m1.info, m1.count)
#: hi 3
print(m2.name, m2.age)
#: Bob 30
print(hasattr(m1, "name"), hasattr(m2, "info"))
#: False False
```

Each `Messenger()` call builds a fresh `dict` in `**kwargs` from that call's arguments and assigns it to that instance's `__dict__`.
So every instance holds its own dictionary.
A [class attribute](../../Chapters/09_Foundations--Class_Attributes.md)
works the other way.
Every instance shares the one object the class holds,
until an instance attribute of the same name shadows it.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. A third field on `Point`

> In `point_dataclass.py`, add a third field, `z: float`,
> to the `Point` data class,
> and update the `Point(...)` call to pass three arguments.

<details>
<summary>Where to look</summary>

[`@dataclass`](../../Chapters/28_Patterns--Data_Transfer_Objects.md#dataclass)
shows that the decorator builds the methods from the annotated fields in the class body.
Declare the new field with an annotation like the other two.
Then check how `repr()` and `==` change on their own.

<details>
<summary>Done when</summary>

your `point_dataclass.py` prints `Point(x=1.0, y=2.0, z=...)` with your third value,
and `uv run ty check` passes on it.
Leaving any `Point(...)` call at two arguments makes the type checker report `missing-argument` for `z`.

<details>
<summary>Solution</summary>

If you add `z: float` and leave the call as `Point(1.0, 2.0)`,
Python raises a `TypeError` at that call for the missing positional argument `'z'`.
Before the script runs, `ty` reports the same call as a `missing-argument`.
A field declared without a default becomes a required parameter of the generated `__init__()`,
so the solution passes three arguments to every `Point(...)` call.

```python
# exercise_2.py
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    z: float

p = Point(1.0, 2.0, 3.0)
print(p)
#: Point(x=1.0, y=2.0, z=3.0)
p.x = 3.5
print(p == Point(3.5, 2.0, 3.0))
#: True
```

`@dataclass` reads the fields the class body declares and generates `__init__()`,
`__repr__()`, and `__eq__()` to match.
Adding `z: float` extends the constructor to three positional arguments,
the `repr()` to three fields, and the equality comparison to three values,
all from that one line.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 3. A `NamedTuple` holding a list

> Add a `NamedTuple` called `Recipe` with fields `name: str` and `steps: list[str]` to `color_namedtuple.py`.
> Mutate the `steps` list of an instance and print the `Recipe`.
> Then try to use the `Recipe` as a `dict` key and explain the result.

<details>
<summary>Where to look</summary>

[`NamedTuple`](../../Chapters/28_Patterns--Data_Transfer_Objects.md#namedtuple)
says how far a `NamedTuple`'s immutability reaches, and why it hashes.
Call a mutating method on the `list` field.
That call changes the list and leaves the `Recipe`'s fields as they were.
For the `dict` key, ask what hashing a tuple does with each of its elements.

<details>
<summary>Done when</summary>

printing your `Recipe` after the mutation shows the new step inside `steps`,
and using it as a `dict` key raises a `TypeError` ending `(unhashable type: 'list')`.
You can name the one cause behind both results.

<details>
<summary>Solution</summary>

If you assign a longer list to the field,
as in `toast.steps = toast.steps + ["butter"]`,
Python raises an `AttributeError` with the message `can't set attribute`.
The type checker reports the assignment too,
as `color_namedtuple.py` shows for `red.r = 9`.
That attempt tests the `Recipe`'s immutability, which holds.
The solution calls `append()`, which edits the field's list in place.

```python
# exercise_3.py
from typing import NamedTuple
from exceptions import expected

class Recipe(NamedTuple):
    name: str
    steps: list[str]

toast = Recipe("Toast", ["slice", "heat"])
toast.steps.append("butter")
print(toast)
#: Recipe(name='Toast', steps=['slice', 'heat', 'butter'])
with expected(TypeError):
    key = {toast: "breakfast"}
#: [TypeError] cannot use 'Recipe' as a dict key (unhashable
#: type: 'list')
```

**Mutate through the field.**
The `Recipe` changed, and both Python and the type checker accepted the change.
`NamedTuple` raises an `AttributeError` when code rebinds `toast.steps`,
but `append()` leaves `toast.steps` bound to the same list.

**Hash the `Recipe`.**
Hashing a tuple hashes each element,
so a `Recipe` is hashable only when every field is.
The `list` has no hash, so the `Recipe` has none either.

The silent `append()` and the `TypeError` have one cause.
A `NamedTuple` freezes which object each field references,
and that object stays as mutable as it was.
[`frozen=True`](../../Chapters/20_Patterns--Rethinking_Objects.md#the-immutability-solution)
is shallow the same way.
Declaring `steps: tuple[str, ...]` fixes the silent `append()` and the `TypeError` at once.
The contents freeze, and the `Recipe` becomes hashable.
One declaration fixing both is the clue that they are one problem.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 4. A fourth attribute, by keyword and by assignment

> In `display_namespace.py`,
> add a fourth attribute to `m` by passing it to the constructor,
> then add it by assignment after the existing `m.more = 11` instead.
> Confirm `vars(m)` reports the same four attributes either way,
> and note whether they come out in the same order.

<details>
<summary>Where to look</summary>

[`SimpleNamespace`](../../Chapters/28_Patterns--Data_Transfer_Objects.md#simplenamespace)
shows `vars()` reading the instance's `__dict__`.
Build one namespace with the extra keyword and another by assigning it afterward,
then compare `list(vars(m))` for both.
A `dict` keeps its keys in insertion order,
so consider when each namespace inserts the new name.

<details>
<summary>Done when</summary>

`list(vars(m))` puts your new attribute third, before `more`,
in the constructor version and last in the assignment version,
while `==` on the two `vars()` dicts prints `True`.
You can say which `dict` property produces each result.

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from types import SimpleNamespace
from typing import Final

TAGS: Final[list[str]] = ["urgent", "todo"]

built = SimpleNamespace(info="Spam", tags=TAGS, note=12)
built.more = 11
print(list(vars(built)))
#: ['info', 'tags', 'note', 'more']

assigned = SimpleNamespace(info="Spam", tags=TAGS)
assigned.more = 11
assigned.note = 12
print(list(vars(assigned)))
#: ['info', 'tags', 'more', 'note']

print(vars(built) == vars(assigned), built == assigned)
#: True True
```

**Add the attribute two ways.**
A keyword argument and a later assignment both add one entry to the instance's `__dict__`.
`vars()` reads that dict, which keeps insertion order.
The two namespaces insert `note` at different moments.

**Compare the contents.**
Dict equality ignores order, so the two dicts compare equal,
and so do the namespaces.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 5. Returning a bare `tuple[float, int]`

> In `summarize_stats.py`,
> change `summarize()` to return a bare `tuple[float, int]`,
> and repair the one line that breaks.
> What do the call sites lose,
> and which mistakes does the type checker still catch?

<details>
<summary>Where to look</summary>

[Returning Multiple Values](../../Chapters/28_Patterns--Data_Transfer_Objects.md#returning-multiple-values)
compares a bare tuple with a `NamedTuple` as a return type.
The broken line reads the fields by name.
A tuple has no `mean`, and its `count` is a method, so index the tuple instead.
To see what the type checker still catches,
try unpacking into the wrong number of names,
then swap two names that have different types or the same type.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    ...
```

<details>
<summary>Done when</summary>

`uv run ty check` passes on your repaired file,
and restoring the broken line makes it report `unresolved-attribute` for `mean`.
The swapped `count, mean = summarize(...)` still type-checks and prints `mean=2 count=3.0`,
and you can name two mistakes the checker still reports.

<details>
<summary>Solution</summary>

```python
# exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    return (sum(data) / len(data), len(data))

result = summarize([2.0, 4.0, 6.0])
print(result)
#: (4.0, 3)
print(result[0], result[1])
#: 4.0 3
mean, count = summarize([1.0, 5.0])
print(f"{mean=} {count=}")
#: mean=3.0 count=2
count, mean = summarize([1.0, 5.0])
print(f"{mean=} {count=}")
#: mean=2 count=3.0
```

**Read the fields by position.**
Printing and unpacking still run, because they treat the result as a tuple,
and a `Stats` is a tuple too.
The line that reads `result.mean` and `result.count` breaks.
A bare tuple has no `mean` attribute,
so the type checker reports the `mean` read.
At runtime that read raises an `AttributeError` before the `count` read runs.
The `count` read passes the type checker,
because a tuple has a `count()` method.
`result.count` evaluates to that bound method instead of the number.

The call sites lose the names.
`print(result)` now writes `(4.0, 3)` where it wrote `Stats(mean=4.0, count=3)`,
so a reader of the call site must open `summarize()` to learn which number is which.
The call sites also lose attribute access.
`result.mean` becomes `result[0]`,
the same value labeled by its position instead of its meaning.
And they lose the type as a name.
A function accepting a summary now declares `tuple[float, int]` where it declared `Stats`,
and any pair of a `float` and an `int` satisfies that annotation.

The type checker still catches several mistakes.
It reports unpacking into the wrong number of names,
since the tuple's length is part of its type.
It reports passing `mean` to a parameter declared `int`,
since the element types are still known positionally.
It also reports indexing past the end and calling a `str` method on `count`.

The checker cannot catch the mistake this exercise examines:
swapping `mean` and `count`.
The swapped unpacking type-checks cleanly and misnames both values,
as the listing's `mean=2 count=3.0` output shows.
With `Stats` you write `result.count`, which reads the field by name,
whatever its position.
A parameter annotated `Stats` also rejects a hand-built tuple in either order,
because a `tuple[float, int]` is not a `Stats`.
A position tells the type checker an element's type and tells a reader an index.
A name tells both of them what the element is.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 6. Structural equality across three-field types

> In `still_a_tuple.py`, add `class Point3(NamedTuple)` with fields `x`, `y`,
> `z`.
> Predict `Color(1, 2, 3) == Point3(1, 2, 3)` before running it,
> then predict `FrozenColor(1, 2, 3) == (1, 2, 3)` and check that too.

<details>
<summary>Where to look</summary>

[A `NamedTuple` Is Still a Tuple](../../Chapters/28_Patterns--Data_Transfer_Objects.md#a-namedtuple-is-still-a-tuple)
explains that `NamedTuple` equality is `tuple` equality.
Compare two `NamedTuple` classes with the same values,
then a frozen data class with a tuple.
For the second case,
consider which class's `__eq__()` runs first and what it returns for an operand of another type.

<details>
<summary>Done when</summary>

your file prints `True` for `Color(1, 2, 3) == Point3(1, 2, 3)` and `False` for `FrozenColor(1, 2, 3) == (1, 2, 3)`,
you wrote both predictions down before running it,
and you can explain each answer from the `__eq__()` each side carries.

<details>
<summary>Solution</summary>

```python
# exercise_6.py
from dataclasses import dataclass
from typing import NamedTuple

class Color(NamedTuple):
    r: int
    g: int
    b: int

class Point3(NamedTuple):
    x: int
    y: int
    z: int

print(Color(1, 2, 3) == Point3(1, 2, 3))
#: True

@dataclass(frozen=True)
class FrozenColor:
    r: int
    g: int
    b: int

print(FrozenColor(1, 2, 3) == (1, 2, 3))
#: False
```

**Compare by position and length.**
`Color(1, 2, 3) == Point3(1, 2, 3)` is `True`,
the same answer `Dimensions` gives, and for the same reason.
A `NamedTuple` inherits `tuple.__eq__()`,
which compares length and elements and ignores both classes.
Adding a third `NamedTuple` adds a third type that compares equal to `Color` and `Dimensions`,
so the set of types whose instances equal `(1, 2, 3)` grows with every three-integer `NamedTuple` in the program.
The field names serve the reader.
The `==` operator ignores them.

**Check the class before the fields.**
A frozen data class's generated `__eq__()` checks `other.__class__ is self.__class__` before comparing fields,
and returns `NotImplemented` for a tuple.
Python then tries the tuple's own comparison,
which also returns `NotImplemented`.
When both sides return `NotImplemented`, `==` falls back to identity,
which is `False` for two distinct objects.

A `NamedTuple` is a tuple with labels,
so it works with any code that expects a tuple and compares equal to any tuple holding the same values.
A frozen data class's `__eq__()` checks the class first,
so `==` matches it against instances of its own class and answers `False` for everything else.
Which one is right depends on whether your three numbers should be interchangeable with any tuple of the same values.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 7. Choosing a type for three scenarios

> For each scenario, name the type from "Which Should You Use?" that fits,
> and say why the others do not:
> a configuration bag whose keys first appear at runtime;
> a 2D grid coordinate that must work as a `dict` key;
> an object decoded from a JSON API response whose fields you also validate.

<details>
<summary>Where to look</summary>

[Which Should You Use?](../../Chapters/28_Patterns--Data_Transfer_Objects.md#which-should-you-use)
lists what each type offers and when to choose it.
For each scenario, find the one requirement that rules out the others:
keys that first appear at runtime, a hashable value,
or code that checks fields on construction.
Consider also what `json.dumps()` does with each type.

<details>
<summary>Done when</summary>

each scenario has one type and a reason that rules out each of the others.
Using an instance of your grid type as a `dict` key succeeds,
and passing an instance of your JSON type to `json.dumps()` gives the result your answer predicts for the field names.

<details>
<summary>Solution</summary>

**The configuration bag is a `SimpleNamespace`.**
Its keys arrive at runtime, so you write the code before you know the fields.
A `@dataclass` or `NamedTuple` needs every field named in the class body before any instance exists.
Here the names arrive with the instance.
A `TypedDict` exists to specify the keys for the type checker,
but here every key arrives at runtime, after the type checker has run.
`SimpleNamespace` accepts any name at construction or later,
which is the looseness the scenario needs.
The type checker cannot report a typo in a key name,
because no declaration lists the keys.

**The grid coordinate is a `NamedTuple`.**
It must work as a `dict` key, so it must hash.
A `NamedTuple` hashes as long as its fields do.
A frozen `@dataclass` also hashes by value (with the default `eq=True`).
A mutable `@dataclass` sets `__hash__` to `None`,
so using one as a key raises a `TypeError`.
`SimpleNamespace` and a `TypedDict` raise the same `TypeError`.
`SimpleNamespace` compares by contents and defines no hash.
A `TypedDict` is a `dict` at runtime.

Between a frozen data class and a `NamedTuple` here,
the `NamedTuple` supports two more uses.
A `NamedTuple` coordinate unpacks as `x, y = point` and passes to code that takes a tuple.
Unpacking a frozen data class raises a `TypeError`.
The type checker rejects a frozen data class passed to a parameter that declares a tuple.

**The JSON record is a frozen data class.**
`json.dumps()` writes a `NamedTuple` as a bare array that holds the values and drops the field names.
Given a `@dataclass`,
`json.dumps()` raises a `TypeError` instead of dropping the names silently.

A `@dataclass` also has a place for the validation this scenario requires.
[Data Classes as Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes `__post_init__()` the place to check each value the JSON decoder produces.
Freezing the data class makes that check final,
since every field keeps the value `__post_init__()` checked.
Python raises an `AttributeError` at class creation if a `NamedTuple` class defines `__new__()` or `__init__()`,
so a `NamedTuple` [runs its check in a factory function](../../Chapters/12_Techniques--Data_Classes_as_Types.md#namedtuple-cannot-validate)
that a caller can bypass.
A `TypedDict` describes the `dict` that `json.loads()` returns and declares the keys for the type checker,
but at runtime it is a `dict`, which stores the values `json.loads()` gives it.
A `SimpleNamespace` accepts any name with any value,
at runtime and under the type checker, so the record holds what the JSON held.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>

## 8. A `Point` that survives addition

> Give `point_tuple.py`'s `Point` an `__add__()` that returns a `Point`,
> and a `__repr__()` that prints `Point(1.0, 2.0)`.
> Check that slicing still returns a plain tuple.

<details>
<summary>Where to look</summary>

[Subclassing `tuple` Directly](../../Chapters/28_Patterns--Data_Transfer_Objects.md#subclassing-tuple-directly)
shows that tuple operations return plain tuples.
Override `__add__()` to build the sum through `type(self)(...)`,
so the result is a `Point`, and write `__repr__()` from the two properties.
Slicing goes through `__getitem__()`, which the exercise leaves alone,
so predict what `p[:1]` returns before you run it.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_8.py
from typing import Self

class Point(tuple[float, float]):
    __slots__ = ()

    def __new__(cls, x: float, y: float) -> Self:
        ...

    @property
    def x(self) -> float:
        ...

    @property
    def y(self) -> float:
        ...

    def __add__(self, other: tuple[float, ...]) -> Self:
        ...

    def __repr__(self) -> str:
        ...
```

<details>
<summary>Done when</summary>

`Point(1.0, 2.0) + Point(3.0, 4.0)` prints `Point(4.0, 6.0)` and its `type()` is `Point`,
slicing it with `[:1]` prints the tuple `(4.0,)`,
and `uv run ty check` passes on your file with no `invalid-method-override` on `__add__()`.

<details>
<summary>Solution</summary>

```python
# exercise_8.py
from typing import Self

class Point(tuple[float, float]):
    __slots__ = ()

    def __new__(cls, x: float, y: float) -> Self:
        return super().__new__(cls, (x, y))

    @property
    def x(self) -> float:
        return self[0]

    @property
    def y(self) -> float:
        return self[1]

    def __add__(self, other: tuple[float, ...]) -> Self:
        x, y = other
        return type(self)(self.x + x, self.y + y)

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

p = Point(1.0, 2.0) + Point(3.0, 4.0)
print(p, type(p).__name__)
#: Point(4.0, 6.0) Point
print(p + (1.0, 1.0), p == (4.0, 6.0))
#: Point(5.0, 7.0) True
print(p[:1], (1.0, 1.0) + p)
#: (4.0,) (1.0, 1.0, 4.0, 6.0)
```

**Build the result through the class.**
`tuple.__add__()` concatenates and returns a `tuple`,
so the override replaces it with a sum of the coordinates and constructs the result with `type(self)(...)`.
Using `type(self)` rather than `Point` means a subclass of `Point` gets an instance of its own class back.
The parameter carries `tuple[float, ...]` rather than `tuple[float, float]` because an override must accept everything the base method accepts.
`tuple.__add__()` takes a tuple of any length,
so `ty` reports `invalid-method-override` for the two-element annotation,
citing the Liskov Substitution Principle.
The wider annotation lets `p + (1.0, 1.0)` type-check as well as `Point + Point`.
At runtime, the unpacking `x, y = other` raises a `ValueError` for a tuple of any other length.

**Reuse the properties in `__repr__()`.**
`tuple.__repr__()` prints `(4.0, 6.0)`.
The override makes a `Point` name its type the way a `NamedTuple` does.

**What stays a tuple.**
Slicing goes through `tuple.__getitem__()`, which the exercise leaves alone,
so `p[:1]` is the plain `(4.0,)`.
A tuple on the left of `+` is the other gap:
`(1.0, 1.0) + p` runs `tuple.__add__()`,
which concatenates to a four-element tuple.
Python calls `__radd__()` on the right operand first when that operand's class is a subclass of the left operand's class,
but `Point` defines no `__radd__()`.
Each tuple operation a `Point` must survive is one more override.
So a `NamedTuple` is a better choice when positional tuple behavior is a feature,
and a record is a better choice when that behavior is a liability.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
