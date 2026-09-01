# Design Patterns: Solutions

All three exercises ask about code you wrote, so no answer here can be
the answer. Each one works a single example through instead. The method
is the transferable part: name the axis, subtract Python's share,
then take away one more thing and see whether anything breaks.

## 1. Naming a vector of change

The example is a small report writer. It printed plain text, then had
to emit CSV for a spreadsheet, then JSON for a web front end. Three
changes along one axis, the output format. Everything else stayed put
through all three: the rows, where they came from, what the numbers
meant.

Here is the version that survived the first two changes:

```python
# exercise_1a.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Row:
    name: str
    amount: int

def render(rows: list[Row], style: str) -> str:
    match style:
        case "text":
            return "\n".join(f"{r.name}: {r.amount}"
                             for r in rows)
        case "csv":
            return "\n".join(f"{r.name},{r.amount}"
                             for r in rows)
        case _:
            raise ValueError(f"unknown style {style!r}")

rows = [Row("pens", 3), Row("paper", 7)]
print(render(rows, "csv"))
#: pens,3
#: paper,7
```

Nothing absorbed the change. Each new format meant opening `render()`
and adding a `case`, so the third request edited the same function the
first two had. The `match` reads well and hides the cost, which is why
this shape survives as long as it does: it is not wrong, it just makes
you the one who changes.

Naming the axis says what to do about it. If the format is what varies,
the format has to become a value the program can hold, rather than a
branch in a function:

```python
# exercise_1b.py
from collections.abc import Callable
from dataclasses import dataclass

@dataclass(frozen=True)
class Row:
    name: str
    amount: int

STYLES: dict[str, Callable[[Row], str]] = {
    "text": lambda r: f"{r.name}: {r.amount}",
    "csv": lambda r: f"{r.name},{r.amount}",
}

def render(rows: list[Row], style: str) -> str:
    line = STYLES[style]
    return "\n".join(line(r) for r in rows)

STYLES["json"] = (
    lambda r: f'{{"name": "{r.name}", '
              f'"amount": {r.amount}}}'
)
rows = [Row("pens", 3), Row("paper", 7)]
print(render(rows, "json"))
#: {"name": "pens", "amount": 3}
#: {"name": "paper", "amount": 7}
```

The third format arrives without touching `render()`. The part worth
noticing is where the assignment that adds it can sit: in any module
that imports `STYLES`. `STYLES` absorbs the change because a format is
now data. Everything the axis does not cover still needs hand edits.
Adding a field to `Row` touches every entry in `STYLES`, because a
field is a different vector of change, one this design does nothing
about.

Two things generalize from the example. First, the axis is visible in
the history rather than in the code: the same function appearing in
three consecutive commits names it for you. Second, absorbing one
vector says nothing about the others. A design that makes formats
pluggable and fields painful is the right answer only if formats are
what keep changing.

## 2. Subtracting a pattern

The pattern is *Strategy*, in the shape it takes in Java. Its usual
form requires:

- an interface, `ShippingStrategy`, declaring one method, `cost()`
- a concrete class per algorithm, `FlatRate` and `ByWeight`, each
  implementing that interface
- a context class, `Checkout`, holding a `ShippingStrategy` field
- a constructor argument or setter on the context to install one
- at the call site, a `new FlatRate()` to pass in

Now cross out what Python supplies:

- The interface goes. A function is already a value with a call
  signature, and `Callable[[float], float]` states that signature
  without declaring a type.
- The concrete classes go. Each held one method and no state, so each
  becomes one function.
- The context class goes, along with its field and its setter. There
  is no object left to hold, only an argument to pass.
- The `new` goes with the classes. A function needs no instantiation.

One sentence remains: make the varying step a parameter.

```python
# exercise_2.py
from collections.abc import Callable

def flat(weight: float) -> float:
    return 5.0

def by_weight(weight: float) -> float:
    return 0.5 * weight

def checkout(
    weight: float, shipping: Callable[[float], float]
) -> float:
    return 20.0 + shipping(weight)

print(checkout(6.0, flat), checkout(6.0, by_weight))
#: 25.0 23.0
```

Five constructs became one parameter, and the type checker still knows
what the parameter accepts: `Callable[[float], float]` rejects a
function taking the wrong arguments as surely as an interface rejects
a class that does not implement it.

The sentence that remains is the pattern. Everything crossed out was
the cost of expressing the pattern in a language where a method cannot
travel without an object around it. Python supplies the missing piece,
a function that travels on its own, and
[When a Pattern Dissolves](../Chapters/21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
describes that case as the language having the piece all along. The
intent survives the subtraction. Only the scaffolding disappears.

## 3. Applying *Subtraction*

The design is the same shipping calculation, written the way it looks
before anyone questions it: an abstract base and two subclasses.

```python
# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: float) -> float: ...

class Flat(Shipping):
    @override
    def cost(self, weight: float) -> float:
        return 5.0

class ByWeight(Shipping):
    @override
    def cost(self, weight: float) -> float:
        return 0.5 * weight

def checkout(weight: float, shipping: Shipping) -> float:
    return 20.0 + shipping.cost(weight)

print(checkout(6.0, Flat()), checkout(6.0, ByWeight()))
#: 25.0 23.0
```

Remove the abstract base and turn both subclasses into functions, and
you have exercise 2's version. What stopped working? Nothing. The
numbers are identical, `ty` still rejects a wrongly-shaped argument,
and adding a third rule is still one new definition. Both classes
carried a single method and no state, so the hierarchy was a container
for functions that did not need containing. By the rule that a design
is complete when you cannot take anything else away, the class version
was not complete.

Take away one more thing and the answer changes. Remove `checkout()`'s
`shipping` parameter, inlining `5.0` where the call was, and the
program still runs and still prints a number. What stops working is the
requirement: there is now no way to charge by weight without editing
`checkout()`. That is the floor, the point where subtraction stops.
The parameter is the last piece that carries the design's actual
intent, so removing it removes the design rather than its scaffolding.

Both outcomes are the exercise working correctly. Subtraction is a test
you run rather than a direction you push in: take something away, run
the program, and read the result. Nothing broke means the piece was
scaffolding. Something broke means you found the floor, and the thing
you removed is worth keeping and worth naming.
