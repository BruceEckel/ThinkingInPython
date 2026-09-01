# Template Method: Solutions

## 1. A file-processing framework, customized both ways

The framework anchors the shape: read every file but the last, run the
varying `process()` step over each one's text, and write the combined
result to the last file.

```python
# exercise_1.py
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import final, override

class FileFramework:
    def __init__(self, filenames: list[str]) -> None:
        self.filenames = filenames

    @final
    def run(self) -> None:
        *inputs, output = self.filenames
        pieces = [
            self.process(Path(name).read_text())
            for name in inputs]
        Path(output).write_text("".join(pieces))

    def process(self, text: str) -> str:
        raise NotImplementedError

class UppercaseFramework(FileFramework):
    @override
    def process(self, text: str) -> str:
        return text.upper()

def run_file_framework(
    filenames: list[str], process: Callable[[str], str]
) -> None:
    *inputs, output = filenames
    pieces = [process(Path(name).read_text())
              for name in inputs]
    Path(output).write_text("".join(pieces))

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("hello\n")
        (root / "b.txt").write_text("world\n")

        # Subclassing customization:
        UppercaseFramework([
            str(root / "a.txt"), str(root / "b.txt"),
            str(root / "out1.txt"),
        ]).run()
        print(repr((root / "out1.txt").read_text()))

        # Function-passing customization:
        run_file_framework(
            [str(root / "a.txt"), str(root / "b.txt"),
             str(root / "out2.txt")],
            lambda text: text.upper(),
        )
        print(repr((root / "out2.txt").read_text()))

demo()
#: 'HELLO\nWORLD\n'
#: 'HELLO\nWORLD\n'
```

Both produce identical output, `'HELLO\nWORLD\n'`, because both
express the same `process()` step, an uppercase conversion, through
two different mechanisms for supplying that step. The anchored
algorithm, "read every input, transform it, concatenate into the
output," lives in exactly one place either way: the base class's
`run()`, or the free function `run_file_framework()`.

The second customization idea, searching every input file for words
listed in the first, fits the same shape with a different `process()`
step. That version reads the word list once from the first input
file, before the loop starts. Its `process(text)` then checks each
text against that list and returns a report of the words it found,
rather than a transformed text. The word search needs no change to
`FileFramework.run()` or `run_file_framework()`. Only the step
changes, which is the entire point of the pattern.

## 2. Two fixes for the premature engine

The quick repair reorders the two lines so the subclass finishes its
own setup before handing control to the base class:

```python
# exercise_2_reorder.py
from typing import final, override

class Framework:
    def __init__(self) -> None:
        self.run()

    @final
    def run(self) -> None:
        self.step()

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        self.name = name  # Setup first...
        super().__init__()  # ...then start the engine

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

Greeter("Brian")
#: Hello, Brian!
```

The redesign removes the hazard instead of avoiding it. `Framework`
no longer runs anything during construction, so the client builds a
finished object and starts it:

```python
# exercise_2_redesign.py
from typing import final, override

class Framework:
    @final
    def run(self) -> None:  # No longer called from __init__
        self.step()

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        self.name = name

    @override
    def step(self) -> None:
        print(f"Hello, {self.name}!")

greeter = Greeter("Brian")  # Construction starts nothing
greeter.run()  # The client starts the engine
#: Hello, Brian!
```

The redesign is the one that protects the next author. The reorder
works, but it works only for the subclass that performs it, and it
survives only as long as everyone remembers it. It asks every future
subclass author to invert the convention they have used everywhere
else, which is to call `super().__init__()` first. Nothing in the
signature says so, and no type checker objects to the usual order.
The failure arrives as an `AttributeError` inside a base class
someone else wrote. A rule the next author must remember, without
having read this chapter, is not a repair.

Separating construction from starting makes the mistake unavailable.
No window exists in which the engine runs against half-built state,
because construction runs no engine. The extra line at every call
site, `greeter.run()`, moves the decision about *when* the algorithm
starts out of the base class and into the hands of the code that
knows the object is ready. The same reasoning drives eager versus
lazy construction in
[Singleton](../Chapters/24_Patterns--Singleton.md#when-you-want-a-class-cache-the-instance),
where the timing of a hidden step makes the difference.

## 3. Who objects to a replaced `run()`

```python
# exercise_3.py
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Reversed(ApplicationFramework):
    @override
    def run(self) -> None:  # type: ignore
        for _ in range(2):
            self.customize2()
            self.customize1()

    @override
    def customize1(self) -> None:
        print("one")

    @override
    def customize2(self) -> None:
        print("two")

Reversed().run()
#: two
#: one
#: two
#: one
```

Python objects to nothing. The program runs, and the steps come out
in the reversed order the subclass chose. The anchored algorithm is
no longer anchored.

`ty` is the one that complains. The override carries a `# type: ignore`
so this listing stays in the book's build:

```
error[override-of-final-method]: Cannot override `ApplicationFramework.run`
info: `ApplicationFramework.run` is decorated with `@final`, forbidding overrides
```

The guarantee comes from the type checker, not the language. `@final`
sets `__final__ = True` on the function and does nothing else. No
runtime check consults it. That missing check places the Template
Method's central promise in the same category as every other
annotation in this book: enforced before the program executes, by a
tool you have to actually invoke.

`@final` therefore protects a codebase whose build runs a type
checker, and protects nothing in a codebase that does not. When the
interpreter itself must refuse the override, use the
`__init_subclass__()` technique the chapter points at, which raises a
`TypeError` while the subclass's own class body is executing, long
before anyone constructs an instance.

## 4. Two faithless substitutes the type checker accepts

```python
# exercise_4.py
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Exploder(ApplicationFramework):
    @override
    def customize1(self) -> None:
        raise RuntimeError("step 1 refuses")

class HalfDone(ApplicationFramework):
    def __init__(self) -> None:
        self.pending: list[str] = []

    @override
    def customize1(self) -> None:
        self.pending.append("work")
    # The `...` default on customize2() drains nothing

try:
    Exploder().run()
except RuntimeError as e:
    print(e)
#: step 1 refuses

app = HalfDone()
app.run()
print(app.pending)
#: ['work', 'work']
```

`ty` reports nothing about either class. Both override with the right
name, the right parameters, and the right return type, so both satisfy
`@override` and every signature rule the base class states.

`Exploder` breaks the algorithm on the first step of the first pass.
Code written against `ApplicationFramework` expects `run()` to return
normally for every subclass the base contemplates. `Exploder` raises
an exception instead, so a caller with no `try` around `run()` gets an
exception out of a method that never advertised one.

`HalfDone` breaks the algorithm more quietly, which makes it the
worse of the two. `customize1()` accumulates work for `customize2()`
to consume, so the pair is a two-step flow. Leaving `customize2()` at
its default breaks the second half, and the program neither raises an
exception nor prints anything wrong. `pending` simply grows forever.
Nothing shows from outside until whatever `pending` feeds runs out of
memory or reports stale data.

`Exploder` and `HalfDone` need different things from a type checker,
and only one of those things exists.

`HalfDone`'s omission is repairable. The `...` body makes the step
optional, and that is the base class's decision: it declares that a
subclass may skip this step. Declare instead that a subclass may not,
by inheriting from `ABC` and marking `customize2()` with
`@abstractmethod`, and both tools object. `ty` reports the
instantiation of an abstract class, and Python refuses to construct
`HalfDone` at all. The type checker could not catch the omission
before, because "deliberately empty" and "forgotten" were the same
code, and only the base class could have recorded that difference.

`Exploder`'s exception is not repairable this way. Catching it would
require the base class to state which exceptions a step may raise, and
the type checker to hold every override to that list, which is Java's
`throws` clause. Python has no such declaration, and no annotation
expresses "this raises nothing." An exception type in a docstring is
a note to a human. Only discipline, review, or a test catches
`Exploder`.

That split is the chapter's point stated from the other side. `@final`
protects the shape of the algorithm, and `@abstractmethod` protects the
presence of a step, because both are properties of the class structure
that a base class can declare. What a step *does* once called is
behavior, and Liskov substitution is a rule about behavior, so
enforcing it stays where the chapter left it: with you.
