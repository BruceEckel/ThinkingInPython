# Design Patterns: Solutions

The first three exercises ask about your own experience, so no answer
here can be the answer. Each solution works a single example through
instead. The method is the transferable part: name the axis, subtract
Python's share, then take away one more thing and see whether anything
breaks. The last exercise has an answer you can check against the chapter's
figure.

## 1. Naming a vector of change

> Pick a program you have written that changed more than once.
> Name its vector of change: the thing that shifted every time.
> Say which part of the design absorbed the change,
> and which parts you edited by hand.

<details>
<summary>Where to look</summary>

[The Vector of Change](../../Chapters/21_Patterns--Design_Patterns.md#the-vector-of-change) names the one axis along which a design keeps shifting.
Look at your history for the same function edited again and again, since that function marks the axis.
Then ask which part absorbed each change and which parts you edited by hand.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1a.py
from record import record

@record
class Row:
    name: str
    amount: int

def render(rows: list[Row], style: str) -> str:
    ...
```

```python
# The shape of exercise_1b.py
from collections.abc import Callable
from record import record

@record
class Row:
    name: str
    amount: int

STYLES: dict[str, Callable[[Row], str]] = {
    "text": lambda r: f"{r.name}: {r.amount}",
    "csv": lambda r: f"{r.name},{r.amount}",
}

def render(rows: list[Row], style: str) -> str:
    ...
```

<details>
<summary>Solution</summary>

The example is a small report writer. It prints plain text, then must
emit CSV for a spreadsheet, then JSON for a web front end. Three
changes along one axis, the output format. Everything else stays put
through all three: the rows, their source, what the numbers mean.

Here is the version that survived the first two changes:

```python
# exercise_1a.py
from record import record

@record
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

**Branch on the format.** Nothing absorbs the change. Each new format means opening `render()`
and adding a `case`, so the third request edits the same function the
first two did. The `match` reads well and hides the cost, which is why
this shape survives as long as it does. It is not wrong, but every new
format is an edit you make by hand.

Naming the axis says what to do about it. If the format varies, the
format must become a value the program can hold, rather than a
branch in a function:

```python
# exercise_1b.py
from collections.abc import Callable
from record import record

@record
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

**Hold each format as data.** The third format arrives without touching `render()`. The
assignment that adds the format can sit in any module that imports
`STYLES`. `STYLES` absorbs the change because a format is now data.

Everything the axis does not cover still needs hand edits. Adding a
field to `Row` touches every entry in `STYLES`, because a field is a
different vector of change, one about which this design does nothing.

Two things generalize from the example. First, the axis is visible in
the history rather than in the code. The same function appearing in
three consecutive commits names the axis for you. Second, absorbing one
vector says nothing about the others. A design that makes formats
pluggable and fields painful is the right answer only if formats are
what keep changing.

</details>
</details>
</details>

## 2. Subtracting a pattern

> Take a pattern you know from another language and list its parts:
> the classes, the interfaces, and the methods its usual form requires.
> Cross out every part Python supplies without your writing it.
> Describe what remains in one sentence.

<details>
<summary>Where to look</summary>

[When a Pattern Dissolves](../../Chapters/21_Patterns--Design_Patterns.md#when-a-pattern-dissolves) shows a pattern whose parts Python supplies.
List the interface, the concrete classes, the context, and the wiring the usual form needs.
Cross out each part that a function or a type annotation covers, and state what remains in one sentence.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Callable

def flat(weight: float) -> float:
    ...

def by_weight(weight: float) -> float:
    ...

def checkout(
    weight: float, shipping: Callable[[float], float]
) -> float:
    ...
```

<details>
<summary>Solution</summary>

The pattern is *Strategy*, in the shape it takes in Java. Its usual
form requires:

- an interface, `ShippingStrategy`, declaring one method, `cost()`
- a concrete class per algorithm, `FlatRate` and `ByWeight`, each
  implementing that interface
- a context class, `Checkout`, holding a `ShippingStrategy` field
- a constructor argument or setter on the context to install a `ShippingStrategy`
- at the call site, a `new FlatRate()` to pass in

Now cross out what Python supplies:

- The interface goes. A function is a value with a call
  signature, and `Callable[[float], float]` states that signature
  without declaring a type.
- The concrete classes go. Each holds one method and no state, so each
  becomes one function.
- The context class goes, along with its field and its setter. Nothing
  remains to hold, only an argument to pass.
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

Five constructs become one parameter, and the type checker still knows
what the parameter accepts. `Callable[[float], float]` rejects a
function taking the wrong arguments as surely as an interface rejects
a class that does not implement it.

The sentence that remains is the pattern. Everything crossed out is
the cost of expressing the pattern in a language where a method cannot
travel without an object around it. Python supplies the missing piece,
a function that travels on its own, and
[When a Pattern Dissolves](../../Chapters/21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
describes that case as the language having the piece all along. The
intent survives the subtraction. Only the scaffolding disappears.

</details>
</details>
</details>

## 3. Applying *Subtraction*

> Apply *Subtraction* to a design of your own.
> Remove one class, one interface, or one level of inheritance,
> and say what stopped working.
> If nothing did, leave it out.

<details>
<summary>Where to look</summary>

[Design Principles](../../Chapters/21_Patterns--Design_Patterns.md#design-principles) states *Subtraction* as a test: take one thing away and run the program.
Choose a class or a level of inheritance that holds a single method and no state.
If nothing breaks, the piece was scaffolding.
If something breaks, you have found the part that carries the design's intent.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from abc import ABC, abstractmethod
from typing import override

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: float) -> float: ...

class Flat(Shipping):
    @override
    def cost(self, weight: float) -> float:
        ...

class ByWeight(Shipping):
    @override
    def cost(self, weight: float) -> float:
        ...

def checkout(weight: float, shipping: Shipping) -> float:
    ...
```

<details>
<summary>Solution</summary>

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

If you remove the abstract base and turn both subclasses into
functions, you have exercise 2's version. What stops working? Nothing.
The numbers are identical, the type checker still rejects a wrongly-shaped argument,
and adding a third rule is still one new definition. `Flat` and
`ByWeight` each carry a single method and no state, so the hierarchy is a container
for functions that do not need containing. By the rule that a design
is complete when you cannot take anything else away, the class version
is not complete.

Taking away one more thing changes the answer. If you remove
`checkout()`'s `shipping` parameter, inlining `5.0` where the call through `shipping` was,
the program still runs and still prints a number. What stops working is
the requirement. You can no longer charge by weight without
editing `checkout()`. Removing the parameter reaches the floor, the
point where subtraction stops. The parameter is the last piece that carries the design's
intent, so removing it removes the design rather than its scaffolding.

Both outcomes are the exercise working correctly. Subtraction is a test
you run rather than a direction in which you push: take something away, run
the program, and read the result. Nothing broke means the piece was
scaffolding. Something broke means you found the floor, and the thing
you removed is worth keeping and worth naming.

</details>
</details>
</details>

## 4. Measuring the reach of a change

> Write the `Report` design from [The Reach of a Change](../../Chapters/21_Patterns--Design_Patterns.md#the-reach-of-a-change)
> twice, with a PDF writer and an HTML writer:
> once where `Report` names each writer class,
> and once where `Report` names a `Writer` protocol.
> Add a Markdown writer to both versions.
> For each version, list the existing classes and functions you edited.

<details>
<summary>Where to look</summary>

[The Reach of a Change](../../Chapters/21_Patterns--Design_Patterns.md#the-reach-of-a-change) compares a design in which `Report` names each writer with one in which it names a protocol.
In the first version give each writer its own method name.
In the second give every writer the same method and declare it in a `Protocol`.
Add the Markdown writer to each, then count the existing definitions you opened.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4a.py
from record import record

class PdfWriter:
    def pdf(self, text: str) -> str:
        ...

class HtmlWriter:
    def html(self, text: str) -> str:
        ...

class MdWriter:
    def markdown(self, text: str) -> str:
        ...

type AnyWriter = PdfWriter | HtmlWriter | MdWriter

@record
class Report:
    text: str

    def render(self, writer: AnyWriter) -> str:
        ...

def main(kind: str) -> None:
    ...
```

```python
# The shape of exercise_4b.py
from typing import Protocol
from record import record

class Writer(Protocol):
    def write(self, text: str) -> str: ...

class PdfWriter:
    def write(self, text: str) -> str:
        ...

class HtmlWriter:
    def write(self, text: str) -> str:
        ...

class MdWriter:
    def write(self, text: str) -> str:
        ...

@record
class Report:
    text: str

    def render(self, writer: Writer) -> str:
        ...

def main(kind: str) -> None:
    ...
```

<details>
<summary>Solution</summary>

If you add `MdWriter` to the `AnyWriter` alias and to `main()` but miss the `case` in `Report.render()`,
`main("md")` prints `None`, because no `case` matches and `render()` returns nothing.
The type checker catches the gap.
`ty` reports `invalid-return-type`, since `render()` can implicitly return `None`.
The first version below makes all three edits,
and the second takes the other path, leaving `Report` no `case` to miss.

The first version gives each writer its own method name, which is the
usual reason a class like `Report` ends up naming every writer. The
class must know which method to call on which writer.

```python
# exercise_4a.py
from record import record

class PdfWriter:
    def pdf(self, text: str) -> str:
        return f"%PDF {text}"

class HtmlWriter:
    def html(self, text: str) -> str:
        return f"<p>{text}</p>"

class MdWriter:
    def markdown(self, text: str) -> str:
        return f"**{text}**"

type AnyWriter = PdfWriter | HtmlWriter | MdWriter

@record
class Report:
    text: str

    def render(self, writer: AnyWriter) -> str:
        match writer:
            case PdfWriter():
                return writer.pdf(self.text)
            case HtmlWriter():
                return writer.html(self.text)
            case MdWriter():
                return writer.markdown(self.text)

def main(kind: str) -> None:
    writer: AnyWriter
    match kind:
        case "pdf":
            writer = PdfWriter()
        case "html":
            writer = HtmlWriter()
        case "md":
            writer = MdWriter()
        case _:
            raise ValueError(f"unknown kind {kind!r}")
    print(Report("Q3 sales").render(writer))

main("pdf")
#: %PDF Q3 sales
main("md")
#: **Q3 sales**
```

`MdWriter` is new code, so it does not count. Adding it edits three
existing things: the `AnyWriter` alias gains a member, `Report.render()`
gains a `case`, and `main()` gains a `case`. The alias and `render()`
both belong to `Report`, so the change reaches two parts, `Report` and
`main`, as the left half of the chapter's figure shows.

The second version gives every writer the same method and lets
`Report` name that method through a protocol:

```python
# exercise_4b.py
from typing import Protocol
from record import record

class Writer(Protocol):
    def write(self, text: str) -> str: ...

class PdfWriter:
    def write(self, text: str) -> str:
        return f"%PDF {text}"

class HtmlWriter:
    def write(self, text: str) -> str:
        return f"<p>{text}</p>"

class MdWriter:
    def write(self, text: str) -> str:
        return f"**{text}**"

@record
class Report:
    text: str

    def render(self, writer: Writer) -> str:
        return writer.write(self.text)

def main(kind: str) -> None:
    writer: Writer
    match kind:
        case "pdf":
            writer = PdfWriter()
        case "html":
            writer = HtmlWriter()
        case "md":
            writer = MdWriter()
        case _:
            raise ValueError(f"unknown kind {kind!r}")
    print(Report("Q3 sales").render(writer))

main("pdf")
#: %PDF Q3 sales
main("md")
#: **Q3 sales**
```

Here `MdWriter` edits one existing thing, the `case` that `main()`
gains. `Report` and `Writer` keep their source, and no writer names
`Writer`. The type checker matches each class to the protocol when
`main()` assigns an instance to `writer`.

The count is the answer, three edits in two parts against one edit in
one part, but the places matter more than the number. In the first
version a new format sends you into `Report`, a class whose subject is
the report's content. In the second, the one edit sits in `main()`,
the part whose job is to assemble the pieces. The `match` in `main()`
is the heavy edge that remains, and a
[registry](../../Chapters/27_Patterns--Factory.md#self-registration)
moves it out of `main()` as well.

</details>
</details>
</details>
