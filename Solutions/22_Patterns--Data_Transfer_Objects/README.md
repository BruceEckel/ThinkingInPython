# Data Transfer Objects: Solutions

## 1. Two `Messenger`s do not share attributes

> In `messenger_idiom.py`,
> create a second `Messenger` with different keyword arguments and confirm the two instances do not share attributes
> (unlike a [class attribute](../../Chapters/09_Foundations--Class_Attributes.md)).

<details>
<summary>Where to look</summary>

[A Hand-Rolled *Messenger*](../../Chapters/22_Patterns--Data_Transfer_Objects.md#a-hand-rolled-messenger) shows `__init__()` assigning the keyword arguments to `self.__dict__`.
Build two instances with different keywords, then compare what `hasattr()` reports for each name on each instance.
The question to answer is where each instance keeps its dictionary.

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

Each `Messenger()` call assigns a fresh `dict` to that instance's
`__dict__`: the one `**kwargs` built from that call's own arguments.
Every instance gets its own independent dictionary. A
[class attribute](../../Chapters/09_Foundations--Class_Attributes.md)
works the other way: one object shared by every instance until
something shadows it. `m1` and `m2` share nothing. `m1` has no
`name`, and `m2` has no `info`.

</details>
</details>
</details>

## 2. A third field on `Point`

> In `point_dataclass.py`, add a third field, `z: float`,
> to the `Point` data class,
> and update the `Point(...)` call to pass three arguments.

<details>
<summary>Where to look</summary>

[`@dataclass`](../../Chapters/22_Patterns--Data_Transfer_Objects.md#dataclass) shows that the decorator builds the methods from the annotated fields in the class body.
Declare the new field with an annotation like the other two.
Then check how `repr()` and `==` change without any further edits.

<details>
<summary>Solution</summary>

If you add `z: float` and leave the call as `Point(1.0, 2.0)`,
Python raises a `TypeError` at that call for the missing positional argument `'z'`,
and `ty` reports a `missing-argument` on the call before the script runs.
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

`@dataclass` reads whatever fields the class body declares and
generates `__init__()`, `__repr__()`, and `__eq__()` to match. Adding
`z: float` extends the constructor to three positional arguments, the
`repr()` to three fields, and the equality comparison to three values,
with no other code to update.

</details>
</details>

## 3. A `NamedTuple` holding a list

> Add a `NamedTuple` called `Recipe` with fields `name: str` and `steps: list[str]` to `color_namedtuple.py`.
> Mutate the `steps` list of an instance and print the record.
> Then try to use the record as a `dict` key and explain the result.

<details>
<summary>Where to look</summary>

[A `NamedTuple` Is Still a Tuple](../../Chapters/22_Patterns--Data_Transfer_Objects.md#a-namedtuple-is-still-a-tuple) shows that a `NamedTuple` inherits its behavior from `tuple`, including how it hashes.
Call a mutating method on the `list` field, which assigns nothing to the record.
For the `dict` key, ask what hashing a tuple does with each of its elements.

<details>
<summary>Solution</summary>

If you assign a longer list to the field, as in `toast.steps = toast.steps + ["butter"]`,
Python raises an `AttributeError` (`can't set attribute`) and the type checker reports the assignment,
the same refusal `color_namedtuple.py` shows for `red.r = 9`.
That attempt tests the record's immutability, which holds.
The solution calls `append()` instead, which assigns nothing to the record and edits the field's list in place.

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

**Mutate through the field.** The record changed, and nothing objected. `NamedTuple` refuses to
rebind `toast.steps`. It says nothing about the list that field
references, so `append()` edits that list through the record.
Both the type checker and Python stay silent, because `append()` mutates the
list instead of assigning to a field.

**Hash the record.** Using the record as a `dict` key raises a `TypeError`, whose message
names the cause: `cannot use 'Recipe' as a dict key (unhashable type:
'list')`. Hashing a tuple hashes each element, so a `Recipe` is
hashable only when every field is. The `list` has no hash, so the
record has none either.

The silent `append()` and the `TypeError` are one fact seen twice. The immutability a
`NamedTuple` gives you stops at the field, and a field pointing at a
mutable object hands that object's mutability back. `frozen=True` in
[Rethinking Objects](../../Chapters/20_Patterns--Rethinking_Objects.md#the-immutability-solution)
is shallow the same way. Declaring `steps: tuple[str, ...]` fixes
both at once. The contents stop being editable, and the record
becomes hashable. One declaration fixing both is the clue that they
are one problem.

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

[`SimpleNamespace`](../../Chapters/22_Patterns--Data_Transfer_Objects.md#simplenamespace) shows `vars()` reading the instance's `__dict__`.
Build one namespace with the extra keyword and another by assigning it afterward, then compare `list(vars(m))` for both.
A `dict` keeps its keys in insertion order, so consider when each version inserts the new name.

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

**Add the attribute two ways.** A keyword argument and a later assignment both add one entry to the
instance's `__dict__`, and `vars()` reads that dict. A dict keeps insertion order, and the two versions
insert `note` at different moments. The constructor adds it to
`built` before `built.more = 11` runs, so `note` comes third there.
In `assigned` the assignment to `note` follows `assigned.more = 11`,
so `note` comes last.

**Compare the contents.** The order differs, but `built` and `assigned`
end with the same four attributes, so the two dicts compare equal and
so do the namespaces, since dict equality ignores order.

</details>
</details>

## 5. Returning a bare `tuple[float, int]`

> In `fetch_stats.py`,
> change `summarize()` to return a bare `tuple[float, int]`,
> and repair the one line that stops working.
> What do the call sites lose,
> and which mistakes does the type checker still catch?

<details>
<summary>Where to look</summary>

[Returning Multiple Values](../../Chapters/22_Patterns--Data_Transfer_Objects.md#returning-multiple-values) compares a bare tuple with a named record as a return type.
The broken line reads the fields by name, and a tuple has no `mean` (its `count` is a method), so index it instead.
To see what the type checker still catches, try unpacking into the wrong number of names, then swap two names that have different types or the same type.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
def summarize(data: list[float]) -> tuple[float, int]:
    ...
```

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
mean, count = summarize([1.0, 3.0])
print(mean, count)
#: 2.0 2
```

**Read the fields by position.** Printing and unpacking still run, because a `NamedTuple` was a tuple
all along. The line that reads `result.mean` and `result.count` stops
working. A bare tuple has no `mean` attribute, so the type checker
reports the `mean` read, and at runtime that read raises an
`AttributeError` first.
The `count` read passes the type checker, because a tuple has a
`count()` method, so `result.count` names that bound method instead of
the number.
The repair is `result[0]` and `result[1]`.

The call sites lose the names. `print(result)` now writes
`(4.0, 3)` instead of `Stats(mean=4.0, count=3)`, so the repr no longer
says which number is which. A reader of the call site must open
`summarize()` to find out. The call sites also lose attribute access.
`result.mean` becomes `result[0]`, which holds the same value and no
longer says what it is. And they lose the type as a name. Nothing can
carry a `Stats` annotation anymore, so a function accepting a summary
now advertises `tuple[float, int]`, which any pair of a `float` and an
`int` satisfies.

The type checker still catches a fair amount. Unpacking into the wrong
number of names fails, since the tuple's length is part of its type.
Passing `mean` to a parameter declared `int` fails, since the element
types are still known positionally. Indexing past the end fails, and
so does calling a `str` method on `count`.

The checker cannot catch the mistake this exercise examines:
swapping `mean` and `count`. `mean, count = summarize(data)` and
`count, mean = summarize(data)` destructure the same
`tuple[float, int]` into two names. The second type-checks cleanly and
misnames both values. With `Stats` you write `result.count`, so the
code does not depend on the order. A parameter annotated `Stats` also
rejects a hand-built tuple in either order, because a
`tuple[float, int]` is not a `Stats`.
Position is something the type checker can verify and a reader cannot.
A name is something both can.

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

[A `NamedTuple` Is Still a Tuple](../../Chapters/22_Patterns--Data_Transfer_Objects.md#a-namedtuple-is-still-a-tuple) explains that `NamedTuple` equality is `tuple` equality.
Compare two `NamedTuple` classes with the same values, then a frozen data class with a tuple.
For the second case, consider which class's `__eq__()` runs first and what it returns for an operand of another type.

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

**Compare by position and length.** `Color(1, 2, 3) == Point3(1, 2, 3)` is `True`, the same answer
`Dimensions` gives, and for the same reason. A `NamedTuple` inherits
`tuple.__eq__()`, which compares length and elements and ignores both
classes. Adding a third `NamedTuple` adds a third type that compares
equal to `Color` and `Dimensions`, so the family of things that equal `(1, 2, 3)`
grows with every three-integer `NamedTuple` in the program. The field names
are for you, not for `==`.

**Check the class before the fields.** `FrozenColor(1, 2, 3) == (1, 2, 3)` is `False`. A frozen data class's
generated `__eq__()` checks `other.__class__ is self.__class__` before
comparing fields, and returns `NotImplemented` for a tuple.
Python then tries the tuple's own comparison, which also returns
`NotImplemented`. With both sides declining, `==` falls back to
identity, which is `False` for two distinct objects. A data class is
not a tuple, and no tuple compares equal to one.

`NamedTuple` and the frozen data class offer a choice. A `NamedTuple`
is a tuple with labels, so it interoperates with everything expecting
a tuple and accepts equality with anything of the same shape. A frozen
data class is a distinct type, so it refuses those comparisons and
catches the mismatch instead. Which one is right depends on whether
you want your three numbers to travel as data or to mean something.

</details>
</details>

## 7. Choosing a type for three scenarios

> For each scenario, name the type from "Which Should You Use?" that fits,
> and say why the others do not:
> a configuration bag whose keys arrive at runtime and are not known in advance;
> a 2D grid coordinate that must work as a `dict` key;
> a record decoded from a JSON API response whose fields you also validate.

<details>
<summary>Where to look</summary>

[Which Should You Use?](../../Chapters/22_Patterns--Data_Transfer_Objects.md#which-should-you-use) lists what each type offers and what it costs.
For each scenario, find the one requirement that rules out the others: keys unknown in advance, a hashable value, or code that checks fields on construction.
Consider also what `json.dumps()` does with each type.

<details>
<summary>Solution</summary>

**The configuration bag is a `SimpleNamespace`.** Its keys arrive at
runtime, so no fixed set of fields exists to declare. A `@dataclass`
or `NamedTuple` needs every field named in the class body before any
instance exists, which this scenario cannot supply. A `TypedDict`
exists to name the keys for the type checker, and here every key
arrives at runtime, after the type checker has run. `SimpleNamespace`
accepts any name at construction or later, which is the looseness the
scenario needs. The cost is a type checker that cannot catch a typo
in a key name.

**The grid coordinate is a `NamedTuple`.** It must work as a `dict`
key, so it must hash, and a `NamedTuple` hashes as long as its fields
do. A `@dataclass` also hashes by value when frozen (with the
default `eq=True`), which rules out the mutable `@dataclass`.
`SimpleNamespace` and a `TypedDict` both fail as keys.
`SimpleNamespace` compares by contents and defines no hash, and a
`TypedDict` is a `dict` at runtime, which is unhashable.
Between a frozen data class and a `NamedTuple` here, the tuple form
wins on convenience. Unpacking a coordinate as `x, y = point` and
passing it to code that takes a tuple are both things the scenario
needs and a frozen data class refuses.

**The JSON record is a `@dataclass`.** `json.dumps()` writes a
`NamedTuple` as a bare array, so the record goes back out without
its field names. Given a `@dataclass`, `json.dumps()` raises a `TypeError`
instead of dropping the names silently. A `@dataclass` also has a place for the
validation this scenario requires. [Data Classes as
Types](../../Chapters/12_Techniques--Data_Classes_as_Types.md#a-type-is-a-set-of-values)
makes `__post_init__()` the method that rejects a value the JSON
decoder otherwise accepts unchecked. A `TypedDict` matches the shape
JSON arrives in and names the keys for the type checker, but it is a
dict at runtime and runs no code, so it cannot validate. A
`SimpleNamespace` declares no fields and has no `__post_init__()`, so
neither the type checker nor the class checks the record.

</details>
</details>
