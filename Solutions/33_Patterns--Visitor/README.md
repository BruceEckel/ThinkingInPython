# Visitor: Solutions

## 1. `flower_visitors.py` with `singledispatch`

> Rewrite `flower_visitors.py` with `singledispatch`.
> Make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
> with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
> Which classes and which methods disappear?

<details>
<summary>Where to look</summary>

[The Pythonic *Visitor*: singledispatch](../../Chapters/33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
adds an operation to an existing hierarchy from outside it.
Decide which of `pollinate()` and `eat()` answers differently by flower type.
Only that one needs `@singledispatch` and `register`.
Then list what the *Visitor* machinery in [The Classic *Visitor*](../../Chapters/33_Patterns--Visitor.md#the-classic-visitor)
exists to do, and what takes over each job when the operations become functions.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        ...

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

def pollinate(flower: Flower, pollinator: str) -> str:
    ...

@singledispatch
def eat(flower: Flower, eater: str) -> str:
    ...

@eat.register
def _(flower: Chrysanthemum, eater: str) -> str:
    ...
```

<details>
<summary>Done when</summary>

your file prints the `flower_visitors.py` lines for each flower you run,
with `Chrysanthemum is toxic to Worm` coming from a registered implementation of `eat()`,
and `uv run ty check` passes on it.
You can also list every class and method of `flower_visitors.py` that your file no longer has,
and say what takes over each one's job.

<details>
<summary>Solution</summary>

If you make `pollinate()` a `singledispatch` function too,
the program prints the same four lines.
`pollinate.registry` then holds one key, `object`, for the default,
so every call runs the default body.
In this program the decorator's one effect is a registry lookup on each call.
The solution keeps `pollinate()` an ordinary function and saves `@singledispatch` for `eat()`,
the one operation whose answer depends on the flower type.

```python
# exercise_1.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass

def pollinate(flower: Flower, pollinator: str) -> str:
    return f"{flower} pollinated by {pollinator}"

@singledispatch
def eat(flower: Flower, eater: str) -> str:
    return f"{flower} eaten by {eater}"

@eat.register
def _(flower: Chrysanthemum, eater: str) -> str:
    return f"{flower} is toxic to {eater}"

for flower in (Ranunculus(), Chrysanthemum()):
    print(pollinate(flower, "Bee"))
    print(eat(flower, "Worm"))
#: Ranunculus pollinated by Bee
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum is toxic to Worm
```

Everything on the visitor side disappears: seven classes
(`Visitor`, `Bug`, `Pollinator`, `Predator`, `Bee`, `Fly`, `Worm`)
and their two `visit()` methods.
`Flower` loses `accept()`,
and with it the `Any` annotation the chapter explains.
`Flower` also loses `pollinate()` and `eat()`,
which become functions outside the hierarchy.
`Chrysanthemum`'s `eat()` override becomes a registration.
Beside the four flower classes, two functions and one registration remain.

The `Bug` classes hold no state.
`Pollinator` and `Predator` each exist to name one operation.
`Bee`, `Fly`, and `Worm` exist as the types on which the `visit()` call dispatches.
Once the operation is a function, the call site names it.
`pollinate(flower, "Bee")` says what `flower.accept(bee)` says with a class and a method.

You lose one thing: holding a visitor in a variable and passing it around as an object.
When that matters, pass the function instead, since a function is a value too.
`op = eat` works.
A `dict[str, Callable[[Flower, str], str]]` keyed by operation name lets a program choose an operation at runtime,
as a `Visitor` hierarchy does, without the classes.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Adding a type against adding an operation

> Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
> then add a third operation, `thorns()`, over all four flowers.
> Count the lines each change adds,
> and say which of the two changes `@singledispatch` makes shorter.

<details>
<summary>Where to look</summary>

[The Pythonic *Visitor*: singledispatch](../../Chapters/33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch)
builds each operation as one `@singledispatch` function with a default and a `register` for each flower whose answer differs from the default.
A new class requires the class plus one registration in every operation where its answer differs from the default.
A new operation requires one function plus a registration for each flower that differs.
Count both in lines,
then compare with [The Expression Problem](../../Chapters/13_Techniques--Pattern_Matching.md#the-expression-problem).

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        ...

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass
class Rose(Flower):  # The new type: 2 lines
    pass

@singledispatch
def nectar(flower: Flower) -> str:
    ...

@nectar.register
def _(flower: Gladiolus) -> str:
    ...

@nectar.register
def _(flower: Chrysanthemum) -> str:
    ...

@nectar.register
def _(flower: Rose) -> str:  # 3 lines
    ...

@singledispatch
def fragrance(flower: Flower) -> str:
    ...

@fragrance.register
def _(flower: Ranunculus) -> str:
    ...

@fragrance.register
def _(flower: Rose) -> str:  # 3 lines
    ...

@singledispatch  # The new operation: 3 lines
def thorns(flower: Flower) -> str:
    ...

@thorns.register
def _(flower: Rose) -> str:  # 3 lines
    ...
```

<details>
<summary>Done when</summary>

your file prints `Rose: abundant nectar` from `nectar()`,
`strong` from `fragrance()`,
and a `thorns()` answer for the rose that differs from the answer the other three flowers share.
You can also state, for each change,
how many lines and how many `register` calls it adds.

<details>
<summary>Solution</summary>

If you add the `Rose` class without registering it with `nectar()` and `fragrance()`,
both fall back to their defaults,
so the demo prints `Rose: no nectar / faint / sharp`.
The interpreter and the type checker both accept that version,
so the wrong answer arrives as ordinary output.
The solution registers `Rose` with every operation whose default is wrong for a rose.

```python
# exercise_2.py
from functools import singledispatch

class Flower:
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass
class Ranunculus(Flower):
    pass
class Chrysanthemum(Flower):
    pass
class Rose(Flower):  # The new type: 2 lines
    pass

@singledispatch
def nectar(flower: Flower) -> str:
    return f"{flower}: no nectar"

@nectar.register
def _(flower: Gladiolus) -> str:
    return f"{flower}: abundant nectar"

@nectar.register
def _(flower: Chrysanthemum) -> str:
    return f"{flower}: a little nectar"

@nectar.register
def _(flower: Rose) -> str:  # 3 lines
    return f"{flower}: abundant nectar"

@singledispatch
def fragrance(flower: Flower) -> str:
    return "faint"

@fragrance.register
def _(flower: Ranunculus) -> str:
    return "strong"

@fragrance.register
def _(flower: Rose) -> str:  # 3 lines
    return "strong"

@singledispatch  # The new operation: 3 lines
def thorns(flower: Flower) -> str:
    return "none"

@thorns.register
def _(flower: Rose) -> str:  # 3 lines
    return "sharp"

rose = Rose()
print(nectar(rose), "/", fragrance(rose), "/", thorns(rose))
#: Rose: abundant nectar / strong / sharp
print(thorns(Gladiolus()))
#: none
```

**Add a type.**
`Rose` needs eight lines:
two for the class and three for each of its two registrations,
one per operation whose default is wrong for a rose.

**Add an operation.**
`thorns()` needs six lines:
three for the function and three for the one flower that differs.

Both changes add lines and leave every existing line as it was.
Here the operation takes fewer lines to add than the type.
`thorns()` needs one registration,
because three of the four flowers get its default answer.
`Rose` differs from the default in both existing operations,
so it needs a registration in each.

The new operation also sits in one place,
while the new type's two registrations sit in two places,
each beside the operation it extends.
That difference is the [expression problem](../../Chapters/13_Techniques--Pattern_Matching.md#the-expression-problem).
Methods on a class keep a new type in one place.
Functions over a hierarchy keep a new operation in one place.
No arrangement does both at once.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. The `Visits` protocol in place of `Any`

> Rewrite `flower_visitors.py` with the `Visits` protocol in place of `Any`,
> so `accept()` declares what it needs.
> Then add a `Beetle(Bug)` with no `visit()` method and pass it to `accept()`.
> Which version reports the mistake, and when?

<details>
<summary>Where to look</summary>

[Two Departures from the Classic Shape](../../Chapters/33_Patterns--Visitor.md#two-departures-from-the-classic-shape)
shows a `Protocol` with a single `visit()` method as the type of the `accept()` parameter.
Because a `Protocol` matches by structure, `Bee` stays as it is.
Run the `Beetle` call through the type checker and then through the interpreter,
and note which one reports the mistake, and when.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import Protocol
from exceptions import expect

class Visits(Protocol):
    def visit(self, flower: Flower) -> None: ...

class Flower:
    def accept(self, visitor: Visits) -> None:
        ...
    def pollinate(self, pollinator: Visitor) -> None:
        ...
    def __str__(self) -> str:
        ...

class Gladiolus(Flower):
    pass

class Visitor:
    def __str__(self) -> str:
        ...

class Bug(Visitor):
    pass

class Pollinator(Bug):
    def visit(self, flower: Flower) -> None:
        ...

class Bee(Pollinator):
    pass

class Beetle(Bug):  # Inherits no visit()
    pass
```

<details>
<summary>Done when</summary>

your `Bee` call prints `Gladiolus pollinated by Bee`,
and `uv run ty check` reports `invalid-argument-type` on your `Beetle` call to `accept()`.
Under the chapter's `Any` version, the checker accepts the same call.
Running it raises an `AttributeError`:
`'Beetle' object has no attribute 'visit'`.

<details>
<summary>Solution</summary>

If you annotate the `accept()` parameter as `Visitor` instead of `Visits`,
`ty` reports an `unresolved-attribute` on `visitor.visit`,
because the empty `Visitor` base declares no `visit()`.
The `Beetle` call then passes the checker, since `Beetle` is a `Visitor`.
At runtime the call raises the same `AttributeError` as it does under `Any`.
The solution annotates the parameter with `Visits`,
which specifies the method `accept()` calls.

```python
# exercise_3.py
from typing import Protocol
from exceptions import expect

class Visits(Protocol):
    def visit(self, flower: Flower) -> None: ...

class Flower:
    def accept(self, visitor: Visits) -> None:
        visitor.visit(self)
    def pollinate(self, pollinator: Visitor) -> None:
        print(self, "pollinated by", pollinator)
    def __str__(self) -> str:
        return type(self).__name__

class Gladiolus(Flower):
    pass

class Visitor:
    def __str__(self) -> str:
        return type(self).__name__

class Bug(Visitor):
    pass

class Pollinator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

class Bee(Pollinator):
    pass

class Beetle(Bug):  # Inherits no visit()
    pass

Gladiolus().accept(Bee())
#: Gladiolus pollinated by Bee

expect(AttributeError, Gladiolus().accept, Beetle())  # type: ignore
#: [AttributeError] 'Beetle' object has no attribute 'visit'
```

**Declare the visitor's interface.**
`Visits` specifies the one method `accept()` calls,
so the parameter declares what `accept()` needs instead of accepting anything.
A `Protocol` matches on structure,
so `Bee` matches `Visits` through the `visit()` it inherits from `Pollinator`.
Any class with a compatible `visit()` satisfies `Visits`,
whatever its base classes.

The listing keeps the chapter's `Visitor`, `Bug`, `Pollinator`,
and `Bee` as they are.
It drops `Fly`, `Ranunculus`, and the eating half: `eat()`, `Chrysanthemum`,
`Predator`, and `Worm`.

The `Any` and `Visits` versions report the `Beetle` mistake at different times.
Under `Any`, the type checker accepts every argument, so the call type-checks.
At runtime `accept()` raises `AttributeError` under either annotation,
as the `#:` line shows.
Under `Visits`, the type checker rejects the argument before the program runs,
because `Visits` requires a `visit()` method and `Beetle` inherits none.

**Demonstrate the runtime failure.**
The `# type: ignore` comment suppresses the checker's report on the `Beetle` call so the listing can show the runtime failure.
If you remove the comment, `ty` reports an `invalid-argument-type`.

The chapter's version needs the `Any` because its `Visitor` base is empty.
Two fixes restore the checks that `Any` turns off on the visitor side:
declaring `visit()` abstract on that base, as the classic pattern does,
or annotating the parameter with the `Visits` protocol, as this solution does.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
