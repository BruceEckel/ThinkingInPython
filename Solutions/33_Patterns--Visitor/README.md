# Visitor: Solutions

## 1. `flower_visitors.py` with `singledispatch`

> Rewrite `flower_visitors.py` with `singledispatch`.
> Make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
> with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
> Which classes and which methods disappear?

<details>
<summary>Where to look</summary>

[The Pythonic Visitor: singledispatch](../../Chapters/33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch) adds an operation to a fixed hierarchy from outside it.
Decide which of `pollinate()` and `eat()` answers differently by flower type.
Only that one needs `@singledispatch` and `register`.
Then list what the *Visitor* machinery in [The Classic Visitor](../../Chapters/33_Patterns--Visitor.md#the-classic-visitor) exists to do, and what in it has no job left.

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
<summary>Solution</summary>

If you make `pollinate()` a `singledispatch` function too, the program
prints the same four lines, and `pollinate.registry` holds one key,
`object`, for the default. With no registration to choose, every
call runs the default body, so the decorator adds a dispatch step that
decides nothing. The solution keeps `pollinate()` an ordinary function
and saves `@singledispatch` for `eat()`, the one operation whose answer
depends on the flower type.

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

Everything on the visitor side disappears: the `Visitor` base, `Bug`,
`Pollinator`, `Predator`, `Bee`, `Fly`, and `Worm`, and the two
`visit()` methods. `Flower` loses `accept()`, and with it the `Any`
annotation the chapter explains. `Flower` also loses `pollinate()` and
`eat()`, which become functions outside the hierarchy.
`Chrysanthemum`'s `eat()` override becomes a registration. Two
functions and one registration remain.

**Dispatch where the flower type matters.** Only `eat()` is a `singledispatch` function, because `eat()`
answers differently for one flower type. `pollinate()` does the same
thing for every flower, so it stays an ordinary function.

The `Bug` classes hold no state. `Pollinator` and `Predator` each
exist to name one operation, and `Bee`, `Fly`, and `Worm` exist
to be types the second dispatch can resolve. Once the operation is a
function, the call site names it. `pollinate(flower, "Bee")` says what
`flower.accept(bee)` says with a class and a method.

You lose one thing: holding a visitor in a variable and passing it
around as an object. When that matters, the function is still a value.
`op = eat` works, and a `dict[str, Callable[[Flower, str], str]]` keyed by
operation name recovers the "choose an operation at runtime" half of
what the `Visitor` hierarchy provides, without the classes.

</details>
</details>
</details>

## 2. Adding a type against adding an operation

> Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
> then add a third operation, `thorns()`, over all four flowers.
> Count the lines each change costs,
> and say which of the two changes `@singledispatch` makes cheaper.

<details>
<summary>Where to look</summary>

[The Pythonic Visitor: singledispatch](../../Chapters/33_Patterns--Visitor.md#the-pythonic-visitor-singledispatch) builds each operation as one `@singledispatch` function with a default and a `register` per exception.
A new class costs the class plus one registration in every operation where its answer differs from the default.
A new operation costs one function plus a registration for each flower that differs.
Count both in lines, then compare with [The Expression Problem](../../Chapters/13_Techniques--Pattern_Matching.md#the-expression-problem).

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
<summary>Solution</summary>

If you add the `Rose` class without registering it with `nectar()` and `fragrance()`,
both operations fall back to their defaults,
and the demo prints `Rose: no nectar / faint / sharp`.
Neither the interpreter nor the type checker reports the omission, so the wrong answer goes unnoticed.
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

**Add a type.** Adding `Rose` costs eight lines: two for the class and three for each
of its two registrations, one per operation whose default is wrong for
a rose.

**Add an operation.** Adding `thorns()` costs six lines: three for the function and three
for the one flower that differs. Neither change edits an existing line.

`@singledispatch` makes adding an operation cheaper than adding a
type, because an operation is a whole function and lives in one place.
Adding `thorns()` is cheap because three of the four flowers accept
its default. `Rose` needs a distinct answer from every operation, so
it costs one registration per operation, scattered across the file.
That difference in cost is the
[expression problem](../../Chapters/13_Techniques--Pattern_Matching.md#the-expression-problem):
methods on a class make adding a type cheap, functions over a hierarchy
make adding an operation cheap, and no arrangement makes both cheap at
once.

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

[The Price of the Empty Base](../../Chapters/33_Patterns--Visitor.md#the-price-of-the-empty-base) shows a `Protocol` with a single `visit()` method as the type of the `accept()` parameter.
Because a `Protocol` matches by structure, `Bee` needs no change.
Run the `Beetle` call through the type checker and then through the interpreter, and note which one objects and at what point.

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
<summary>Solution</summary>

If you annotate the `accept()` parameter as `Visitor` instead of `Visits`,
`ty` reports an `unresolved-attribute` on `visitor.visit`,
because the empty `Visitor` base declares no `visit()`.
The `Beetle` call then passes the checker, since `Beetle` is a `Visitor`,
and fails at runtime with the same `AttributeError` as under `Any`.
The solution annotates the parameter with `Visits`, which names the method `accept()` calls.

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

**Declare the visitor's interface.** `Visits` names the one method `accept()` calls, so the parameter
declares what `accept()` needs instead of accepting anything. `Bee`
neither mentions `Visits` nor inherits from it, because a `Protocol`
matches on structure. Any class with a compatible `visit()`
satisfies `Visits`.

The `Visitor` classes keep the chapter's form. The listing keeps
`Visitor`, `Bug`, `Pollinator`, and `Bee` from them and drops `Fly`
and the eating half.

The two versions report the `Beetle` mistake at different times. Under
`Any`, the type checker has no interface against which to compare
`Beetle`, so the call type-checks and the program dies at runtime with the
`AttributeError` above. Under `Visits`, the type checker rejects the argument
before the program runs, because `Beetle` inherits no `visit()` and so
does not match the protocol.

**Demonstrate the runtime failure.** The `# type: ignore` comment
keeps the checker quiet about the `Beetle` call so the listing can
show the runtime failure. Without it, `ty` reports an
`invalid-argument-type`.

Losing the check on the visitor side is the price the chapter names
for keeping `Any`. The `Any` moves
an error a type checker can catch into the run. The chapter's version
pays that price because its `Visitor` base is empty. Either fix
restores the check: declaring `visit()` abstract on that base, as the
classic pattern does, or writing the `Visits` protocol above.

</details>
</details>
</details>
