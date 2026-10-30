# Design Patterns: Solutions

The first three exercises ask about your own experience,
so no answer here can be the answer.
Each of those solutions works through a single example.
The method is the transferable part: name the axis, subtract Python's share,
then take away one more thing and see whether anything breaks.
The last exercise has an answer you can check against the chapter's figure.

## 1. Naming a vector of change

> Pick a program you have written that changed more than once.
> Name its vector of change: the thing that shifted every time.
> Say which part of the design absorbed the change,
> and which parts you edited.

<details>
<summary>Where to look</summary>

[The Vector of Change](../../Chapters/21_Patterns--Design_Patterns.md#the-vector-of-change)
describes the main axis along which a design keeps shifting.
Look at your history for the same function edited again and again,
since that function marks the axis.
Then ask which part absorbed each change and which parts you edited.

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
<summary>Done when</summary>

you can state the axis in a few words, name the part that absorbed each change
(or say that none did), and list the hand edits each change required.
You can also name one change off that axis and the parts it would force you to edit.

<details>
<summary>Solution</summary>

The example is a small report writer.
It prints plain text, then must emit CSV for a spreadsheet,
then JSON for a web front end.
All three formats run along one axis, the output format.
Everything else stays the same through all three: the rows, their source,
what the numbers mean.

Here is the version that holds the first two formats:

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

**Branch on the format.**
Nothing absorbs the change.
Each new format means opening `render()` and adding a `case`,
so the third request edits the same function the first two did.
The branching shape survives as long as it does because the `match` reads well,
but every new format is an edit to the `match`.

Naming the axis says what to do about those hand edits.
If the format varies, the format must become a value the program can hold,
rather than a branch in a function:

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

**Hold each format as data.**
Adding the third format takes one assignment.
`render()` stays as it was.
`STYLES` absorbs the change because a format is now data.
The assignment that adds the format can sit in any module that imports `STYLES`,
so adding a format can leave the module that defines `STYLES` and `render()` as it was.

Everything outside the axis still needs hand edits.
Printing a new field of `Row` means editing every entry in `STYLES`.
`STYLES` absorbs new formats.
A field is a different vector of change.

Two things generalize from the example.
First, the axis is visible in the history rather than in the code.
When the same function appears in three consecutive commits,
the history shows the axis for you.
Second, a design absorbs one vector and leaves the others as they were.
In this design a new format is one assignment.
A new field is an edit to every format,
so the design is the right answer only if formats are what keep changing.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Subtracting a pattern

> Take a pattern you know from another language and list its parts:
> the classes, the interfaces, and the methods its usual form requires.
> Cross out every part Python supplies for you.
> Describe what remains in one sentence.

<details>
<summary>Where to look</summary>

[When a Pattern Dissolves](../../Chapters/21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
shows a pattern whose parts Python supplies.
List the interface, the concrete classes, the context,
and the wiring the usual form needs.
Cross out each part that a function or a type annotation covers,
and state what remains in one sentence.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2.py
from collections.abc import Callable

type Weight = float
type Cost = float

def flat(weight: Weight) -> Cost:
    ...

def by_weight(weight: Weight) -> Cost:
    ...

def checkout(
    weight: Weight, shipping: Callable[[Weight], Cost]
) -> Cost:
    ...
```

<details>
<summary>Done when</summary>

your list covers every interface, class, method,
and call-site construct the usual form requires,
each crossed-out part has the Python feature that supplies it written beside it,
and the remainder fits in one sentence that states the pattern's intent and names none of its classes.

<details>
<summary>Solution</summary>

The pattern is [*Strategy*](../../Chapters/27_Patterns--Function_Objects.md#strategy-choosing-the-algorithm-at-runtime),
in the shape it takes in Java.
Its usual form requires:

- An interface, `ShippingStrategy`, declaring one method, `cost()`
- A concrete class per algorithm, `FlatRate` and `ByWeight`,
  each implementing that interface
- A context class, `Checkout`, holding a `ShippingStrategy` field
- A constructor argument or setter on the context to install a `ShippingStrategy`
- At the call site, a `new FlatRate()` to pass in

Now cross out what Python supplies:

- The interface goes.
  A function is a value with a call signature,
  and `Callable[[Weight], Cost]` states that signature without declaring an interface.
- The concrete classes go.
  Each holds one method and no state, so each becomes one function.
- The context class goes, along with its field and its setter.
  The strategy becomes an argument to pass rather than a field to hold.
- The `new` goes with the classes.
  You pass a function by its name.

One sentence remains: make the varying step a parameter.

```python
# exercise_2.py
from collections.abc import Callable

type Weight = float
type Cost = float

def flat(weight: Weight) -> Cost:
    return 5.0

def by_weight(weight: Weight) -> Cost:
    return 0.5 * weight

def checkout(
    weight: Weight, shipping: Callable[[Weight], Cost]
) -> Cost:
    return 20.0 + shipping(weight)

print(checkout(6.0, flat), checkout(6.0, by_weight))
#: 25.0 23.0
```

Five constructs become one parameter and a function per algorithm.
The type checker still knows what the parameter accepts:
`Callable[[Weight], Cost]` rejects a function that takes the wrong arguments.
In Java, the `ShippingStrategy` interface makes the same check on a class.

The sentence that remains is the pattern.
The subtraction keeps the pattern's intent and removes the supporting code.
Everything crossed out serves a language where a method belongs to a class.
In such a language, passing a behavior means passing an object.
The crossed-out parts build that object.
Python has had the [missing piece](../../Chapters/21_Patterns--Design_Patterns.md#when-a-pattern-dissolves)
all along, since a function is a value you can pass.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Applying *Subtraction*

> Apply *Subtraction* to a design of your own.
> Remove one class, one interface, or one level of inheritance,
> and say what stopped working.
> If everything still works, leave it out.

<details>
<summary>Where to look</summary>

[Design Principles](../../Chapters/21_Patterns--Design_Patterns.md#design-principles)
states *Subtraction*:
a design is complete when you cannot take anything else away.
Use *Subtraction* as a test: take one thing away and run the program.
Choose a class or a level of inheritance that holds a single method and no state.
If everything still works, the piece you removed is supporting code.
If something breaks, you have found the part that expresses the design's intent.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from abc import ABC, abstractmethod
from typing import override

type Weight = float
type Cost = float

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: Weight) -> Cost: ...

class Flat(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        ...

class ByWeight(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        ...

def checkout(weight: Weight, shipping: Shipping) -> Cost:
    ...
```

<details>
<summary>Done when</summary>

you have removed one piece, run the program and `uv run ty check`,
and written down what changed in the output and in the requirement the program meets.
If both stayed the same, you can say what the removed piece wrapped;
if something broke, you can name the requirement that piece expresses.

<details>
<summary>Solution</summary>

The design is the same shipping calculation,
written the way it looks before anyone questions it:
an abstract base and two subclasses.

```python
# exercise_3.py
from abc import ABC, abstractmethod
from typing import override

type Weight = float
type Cost = float

class Shipping(ABC):
    @abstractmethod
    def cost(self, weight: Weight) -> Cost: ...

class Flat(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        return 5.0

class ByWeight(Shipping):
    @override
    def cost(self, weight: Weight) -> Cost:
        return 0.5 * weight

def checkout(weight: Weight, shipping: Shipping) -> Cost:
    return 20.0 + shipping.cost(weight)

print(checkout(6.0, Flat()), checkout(6.0, ByWeight()))
#: 25.0 23.0
```

If you remove the abstract base and turn both subclasses into functions,
you have exercise 2's version.
What stops working?
Everything still works.
The numbers are identical,
the type checker still rejects a wrongly shaped argument,
and adding a third rule is still one new definition.
`Flat` and `ByWeight` each carry a single method and no state,
so each class is a wrapper around one function.
By the rule that a design is complete when you cannot take anything else away,
the class version has three classes left to take away.

Taking away one more thing changes the answer.
Removing `checkout()`'s `shipping` parameter means inlining `5.0` where the call through `shipping` was and dropping the second argument from each call.
The program still runs and still prints a number.
What stops working is the requirement.
Charging by weight now means editing `checkout()`.
*Subtraction* stops at the parameter.
The parameter is the last piece that expresses the design's intent,
so removing it removes the design rather than its supporting code.

Both outcomes are the exercise working correctly:
a removal that kept the requirement, and one that broke the requirement.
*Subtraction* is a test you run, not a rule to remove as much as you can.
Take something away, run the program, and read the result.
If everything still works, the piece is supporting code.
If something breaks, the piece you removed expresses the design.
Keep it, and give it a name.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Measuring the reach of a change

> Write the `Report` design from [The Reach of a Change](../../Chapters/21_Patterns--Design_Patterns.md#the-reach-of-a-change)
> twice, with a PDF writer and an HTML writer:
> once where `Report` specifies each writer class,
> and once where `Report` specifies a `Writer` protocol.
> Add a Markdown writer to both versions.
> For each version, list the existing classes and functions you edited.

<details>
<summary>Where to look</summary>

[The Reach of a Change](../../Chapters/21_Patterns--Design_Patterns.md#the-reach-of-a-change)
compares a design in which `Report` specifies each writer with one in which it specifies a protocol.
In the first version give each writer its own method name.
In the second give every writer the same method and declare that method in a `Protocol`.
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
<summary>Done when</summary>

both files pass `uv run ty check`,
asking each `main` for the Markdown writer prints your Markdown text rather than `None`,
and your edit lists match the chapter's figure:
`Report` and `main` in the first version, `main` alone in the second.

<details>
<summary>Solution</summary>

The first version gives each writer its own method name,
which is the usual reason a class like `Report` ends up naming every writer.
The class must know which method to call on which writer.

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

`MdWriter` is new code, so it stays out of the count.
Adding it edits three existing things: the `AnyWriter` alias gains a member,
`Report.render()` gains a `case`, and `main()` gains a `case`.
Two of those edits belong to `Report`.
`render()` is its method, and the alias lists the writers `Report` accepts.
The change therefore reaches two parts, `Report` and `main`,
as the left half of the chapter's figure shows.

If you add `MdWriter` to the `AnyWriter` alias and to `main()` but leave `Report.render()` as it was,
`main("md")` prints `None`.
The writer falls through every `case`, and `render()` reaches its end,
where Python returns `None` implicitly.
`ty` reports that path as `invalid-return-type`,
since `render()` declares that it returns `str`.

The second version gives every writer the same method and lets `Report` specify that method through a protocol:

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

Here adding `MdWriter` edits one existing thing, the `case` that `main()` gains.
`Report` and `Writer` keep their source.
No writer lists `Writer` as a base.
The type checker matches each class to the protocol when `main()` assigns an instance to `writer`.

The count gives the answer:
three edits in two parts against one edit in one part.
The places matter more than the number, though.
In the first version a new format means editing `Report`,
a class whose subject is the report's content.
In the second, the one edit is in `main()`,
the part whose job is to assemble the pieces.

The second version still has heavy edges, and they all sit in `main()`.
The `match` in `main()` names every writer class.
A [registry](../../Chapters/26_Patterns--Factory.md#self-registration)
removes those remaining edges from `main()`.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
