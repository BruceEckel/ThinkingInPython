# Visitor: Solutions

## 1. `flower_visitors.py` with `singledispatch`

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

@singledispatch
def pollinate(flower: Flower, agent: str) -> str:
    return f"{flower} pollinated by {agent}"

@singledispatch
def eat(flower: Flower) -> str:
    return f"{flower} eaten by Worm"

@eat.register
def _(flower: Chrysanthemum) -> str:
    return f"{flower} is toxic to Worm"

for flower in (Ranunculus(), Chrysanthemum()):
    print(pollinate(flower, "Bee"))
    print(eat(flower))
#: Ranunculus pollinated by Bee
#: Ranunculus eaten by Worm
#: Chrysanthemum pollinated by Bee
#: Chrysanthemum is toxic to Worm
```

Everything on the visitor side disappears: the `Visitor` base, `Bug`,
`Pollinator`, `Predator`, `Bee`, `Fly`, and `Worm`, and the two
`visit()` methods. So does `accept()` on `Flower`, and with it the
`Any` annotation the chapter had to explain. What remains is two
functions and one registration.

The `Bug` classes were never carrying state; the middle layer existed
to name one operation, and the leaves existed to be types the second
dispatch could resolve. Once the operation is a function, naming it at
the call site does that selection, so `pollinate(flower, "Bee")` says
what `flower.accept(bee)` said with a class and a method.

The one thing lost is the ability to hold a visitor in a variable and
pass it around as an object. When that matters, the function is still
a value: `op = eat` works, and a `dict[str, Callable[[Flower], str]]`
keyed by operation name recovers the "choose an operation at runtime"
half of what the `Visitor` hierarchy provided, without the classes.

## 2. Adding a type against adding an operation

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
def _(flower: Rose) -> str:  # 3 lines
    return f"{flower}: abundant nectar"

@singledispatch
def fragrance(flower: Flower) -> str:
    return "faint"

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

Adding `Rose` cost two lines for the class plus one registration per
operation that needed a non-default answer, and nothing existing was
touched. Adding `thorns()` cost one new function plus one registration
for the flower that differs, and again nothing existing was touched.

`@singledispatch` makes adding an *operation* the cheaper of the two,
because an operation is a whole function and lives in one place. Adding
a type is cheap here only because most flowers accept the default; a
type that needs a distinct answer from every operation costs one
registration per operation, scattered across the file. That is the
expression problem from
[Pattern Matching](../Chapters/13_Pattern_Matching.md#dynamic-binding-vs.-pattern-matching):
methods on a class make adding a type cheap, functions over a hierarchy
make adding an operation cheap, and no arrangement makes both cheap at
once.

## 3. The `Visits` protocol in place of `Any`

```python
# exercise_3.py
from typing import Protocol

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

try:
    Gladiolus().accept(Beetle())  # type: ignore
except AttributeError as e:
    print(type(e).__name__, e)
#: AttributeError 'Beetle' object has no attribute 'visit'
```

`Visits` names the one method `accept()` calls, so the parameter
declares what it needs instead of accepting anything. `Bee` neither
mentions `Visits` nor inherits from it: a `Protocol` matches on
structure, so any class with a compatible `visit()` satisfies it, and
the `Visitor` hierarchy stays as the chapter wrote it.

The two versions report the `Beetle` mistake at different times. Under
`Any`, the type checker has nothing to compare `Beetle` against, so the call
type-checks and the program dies at runtime with the `AttributeError`
above. Under `Visits`, `ty` rejects the argument before the program
runs, because `Beetle` inherits no `visit()` and so does not match the
protocol. The `ty: ignore` comment above is what makes the listing
compile at all; deleting it is how you see the check working.

That is the price the chapter names for keeping `Any`. It moves an
error a type checker could have caught into the run. The classic pattern
pays it because its `Visitor` base is empty, and either fix, declaring
`visit()` abstract on that base or writing the protocol above, buys the
check back.
