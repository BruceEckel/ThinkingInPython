# Template Method: Solutions

## 1. A file-processing framework, customized both ways

The framework fixes the shape: read every file but the last, run an
undetermined `process()` step over each one's text, and write the
combined result to the last file.

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
            self.process(Path(name).read_text()) for name in inputs]
        Path(output).write_text("".join(pieces))

    def process(self, text: str) -> str:
        raise NotImplementedError

class UppercaseFramework(FileFramework):
    @override
    def process(self, text: str) -> str:
        return text.upper()

def run_file_framework(filenames: list[str],
                        process: Callable[[str], str]) -> None:
    *inputs, output = filenames
    pieces = [process(Path(name).read_text()) for name in inputs]
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

Both produce identical output, `'HELLO\nWORLD\n'`, since both express
the exact same `process()` step, an uppercase conversion, through two
different mechanisms for supplying it. The fixed algorithm, "read
every input, transform it, concatenate into the output," lives in
exactly one place either way: the base class's `run()`, or the free
function `run_file_framework()`.

The second customization idea, searching every input file for words
listed in the first, fits the same shape with a different `process()`
step: a version whose `process(text)` checks the text against a
word list (read once, before the loop, from the first input file) and
returns a report of which words it found, rather than transforming the
text itself. Nothing about `FileFramework.run()` or
`run_file_framework()` needs to change to support it; only the step
does, which is the entire point of the pattern.

## 2. Two fixes for the premature engine

The quick fix reorders the two lines so the subclass finishes its own
setup before handing control to the base class:

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

Greeter("Bruce")
#: Hello, Bruce!
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

greeter = Greeter("Bruce")  # Construction starts nothing
greeter.run()  # The client starts the engine
#: Hello, Bruce!
```

The redesign is the one that protects the next author. The reorder
works, but it works only for the subclass that performs it, and it
survives only as long as everyone remembers it. It asks every future
subclass author to invert the convention they have used everywhere
else, which is to call `super().__init__()` first. Nothing in the
signature says so, no checker objects to the usual order, and the
failure arrives as an `AttributeError` inside a base class the author
did not write. A rule that must be remembered by people who have not
read this chapter is not a fix.

Separating construction from starting makes the mistake unavailable.
There is no window in which the engine runs against half-built state,
because construction runs no engine. The cost is one extra line at
every call site, `greeter.run()`, and that line is worth it: it moves
the decision about *when* the algorithm starts out of the base class
and into the hands of the code that knows the object is ready. This
is the same reasoning behind eager versus lazy construction in
[Singleton](24_Singleton.md#when-you-want-a-class-cache-the-instance),
where the timing of a hidden step makes the difference.

## 3. Who objects to a replaced `run()`

```python
# exercise_3.py
from typing import final, override

class ApplicationFramework:
    def __init__(self) -> None:
        self.run()

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

Reversed()
#: two
#: one
#: two
#: one
```

Python objects to nothing. The program runs, and the steps come out
in the reversed order the subclass chose, which is the fixed algorithm
no longer being fixed.

`ty` is the one that complains, which is why the override carries a
`# type: ignore` to keep this listing in the book's build:

```
error[invalid-override]: Cannot override final method `run`
```

The guarantee comes from the checker, not the language. `@final` sets
`__final__ = True` on the function and does nothing else; no runtime
check consults it. That places the Template Method's central promise
in the same category as every other annotation in this book: enforced
before the program runs, by a tool you have to actually run.

The practical consequence is that `@final` protects a codebase whose
build runs a checker and protects nothing in a codebase that does not.
When the interpreter itself must refuse the override, use the
`__init_subclass__()` technique the chapter points at, which raises a
`TypeError` while the subclass's own class body is executing, long
before anyone constructs one.
