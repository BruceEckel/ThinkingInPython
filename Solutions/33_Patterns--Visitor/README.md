# Visitor: Solutions

## 1. `flower_visitors.py` with `singledispatch`

> Rewrite `flower_visitors.py` with `singledispatch`:
> make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
> with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
> Which classes and which methods disappear?

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
annotation the chapter explains, and it loses `pollinate()` and
`eat()`, which become functions outside the hierarchy.
`Chrysanthemum`'s `eat()` override becomes a registration. Two
functions and one registration remain.

Only `eat()` is a `singledispatch` function, because only `eat()`
answers differently for one flower type. `pollinate()` does the same
thing for every flower, so it stays an ordinary function.

The `Bug` classes hold no state. `Pollinator` and `Predator` each
exist to name one operation, and `Bee`, `Fly`, and `Worm` exist
to be types the second dispatch can resolve. Once the operation is a
function, the call site names it: `pollinate(flower, "Bee")` says what
`flower.accept(bee)` says with a class and a method.

You lose one thing: holding a visitor in a variable and passing it
around as an object. When that matters, the function is still a value.
`op = eat` works, and a `dict[str, Callable[[Flower, str], str]]` keyed by
operation name recovers the "choose an operation at runtime" half of
what the `Visitor` hierarchy provided, without the classes.

## 2. Adding a type against adding an operation

> Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
> then add a third operation, `thorns()`, over all four flowers.
> Count the lines each change costs,
> and say which of the two changes `@singledispatch` makes cheaper.

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

Adding `Rose` costs eight lines: two for the class and three for each
of its two registrations, one per operation whose default is wrong for
a rose. Adding `thorns()` costs six: three for the function and three
for the one flower that differs. Neither change edits an existing line.

`@singledispatch` makes adding an *operation* cheaper than adding a
type, because an operation is a whole function and lives in one place.
Adding `thorns()` is cheap because three of the four flowers accept
its default. `Rose` needs a distinct answer from every operation, so
it costs one registration per operation, scattered across the file.
That is the expression problem from
[Pattern Matching](../../Chapters/13_Techniques--Pattern_Matching.md#the-expression-problem):
methods on a class make adding a type cheap, functions over a hierarchy
make adding an operation cheap, and no arrangement makes both cheap at
once.

## 3. The `Visits` protocol in place of `Any`

> Rewrite `flower_visitors.py` with the `Visits` protocol in place of `Any`,
> so `accept()` declares what it needs.
> Then add a `Beetle(Bug)` with no `visit()` method and pass it to `accept()`.
> Which version reports the mistake, and when?

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

`Visits` names the one method `accept()` calls, so the parameter
declares what `accept()` needs instead of accepting anything. `Bee`
neither mentions `Visits` nor inherits from it, because a `Protocol`
matches on structure: any class with a compatible `visit()` satisfies
`Visits`. The `Visitor` classes keep the chapter's form; the listing
keeps only the pollinating half of them.

The two versions report the `Beetle` mistake at different times. Under
`Any`, the type checker has nothing to compare `Beetle` against, so
the call type-checks and the program dies at runtime with the
`AttributeError` above. Under `Visits`, the type checker rejects the argument
before the program runs, because `Beetle` inherits no `visit()` and so
does not match the protocol. The `# type: ignore` comment keeps the checker
quiet about that call so the listing can show the runtime failure;
without it, `ty` reports an `invalid-argument-type`.

That is the price the chapter names for keeping `Any`. The `Any` moves
an error a type checker can catch into the run. The chapter's version
pays that price because its `Visitor` base is empty. Either fix
restores the check: declaring `visit()` abstract on that base, as the
classic pattern does, or writing the `Visits` protocol above.
