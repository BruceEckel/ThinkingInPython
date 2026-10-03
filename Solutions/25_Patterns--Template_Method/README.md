# Template Method: Solutions

## 1. A file-processing framework, customized both ways

> Create a framework that takes a list of file names.
> It opens every file but the last for reading, and the last one for writing.
> It processes each input file by a policy the customization supplies,
> and writes the output to the last file.
> Supply each of these policies twice,
> once by subclassing and once by passing a function:
>
> 1.  Convert all the letters in each file to uppercase.
> 2.  Treat the first file as a list of search words, one per line,
>     and report which of those words appear in each remaining input file.

<details>
<summary>Where to look</summary>

[Passing the Steps as Functions](../../Chapters/25_Patterns--Template_Method.md#passing-the-steps-as-functions) shows the same algorithm anchored in a function that takes the varying step as an argument.
The subclass form is in [The Anchored Algorithm](../../Chapters/25_Patterns--Template_Method.md#the-anchored-algorithm).
Put the fixed loop (read each input, apply the step, write the output) in one `run()` and one function, and leave only `process()` open.
The search policy needs the word list, so store it on the subclass and close over it in the function form.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_1.py
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import final

class FileFramework(ABC):
    __slots__ = ()

    @final
    def run(self, filenames: list[str]) -> None:
        ...

    @abstractmethod
    def process(self, text: str) -> str: ...

def run_file_framework(
    filenames: list[str], process: Callable[[str], str]
) -> None:
    ...
```

```python
# The shape of exercise_1_upper.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework

class Uppercase(FileFramework):
    @override
    def process(self, text: str) -> str:
        ...

def demo() -> None:
    ...
```

```python
# The shape of exercise_1_search.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework
from record import record

def found(words: list[str], text: str) -> str:
    ...

@record
class Search(FileFramework):
    words: list[str]

    @override
    def process(self, text: str) -> str:
        ...

def demo() -> None:
    ...
```

<details>
<summary>Solution</summary>

The framework anchors the shape: read every file but the last, run the
varying `process()` step over each one's text, and write the combined
result to the last file. It appears twice, as a base class whose
`run()` is the template method and as a function that takes the step
as an argument. Every customization must supply `process()`, so the
base class declares it with `@abstractmethod`:

```python
# exercise_1.py
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import final

class FileFramework(ABC):
    __slots__ = ()

    @final
    def run(self, filenames: list[str]) -> None:
        *inputs, output = filenames
        pieces = [
            self.process(Path(name).read_text())
            for name in inputs]
        Path(output).write_text("".join(pieces))

    @abstractmethod
    def process(self, text: str) -> str: ...

def run_file_framework(
    filenames: list[str], process: Callable[[str], str]
) -> None:
    *inputs, output = filenames
    pieces = [process(Path(name).read_text())
              for name in inputs]
    Path(output).write_text("".join(pieces))
```

The empty `__slots__` lets a subclass that carries data be a record,
as
[Rethinking Objects](../../Chapters/20_Patterns--Rethinking_Objects.md#abstract-base-classes)
explains.

The uppercase policy needs no data. The subclass overrides
`process()`, and the function form passes `str.upper`, which has the
signature the framework calls:

```python
# exercise_1_upper.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework

class Uppercase(FileFramework):
    @override
    def process(self, text: str) -> str:
        return text.upper()

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.txt").write_text("hello\n")
        (root / "b.txt").write_text("world\n")
        inputs = [str(root / "a.txt"), str(root / "b.txt")]

        # Subclassing customization:
        out1 = root / "out1.txt"
        Uppercase().run([*inputs, str(out1)])
        print(repr(out1.read_text()))

        # Function-passing customization:
        out2 = root / "out2.txt"
        run_file_framework([*inputs, str(out2)], str.upper)
        print(repr(out2.read_text()))

demo()
#: 'HELLO\nWORLD\n'
#: 'HELLO\nWORLD\n'
```

Both produce `'HELLO\nWORLD\n'`, because both supply the same step
through two different mechanisms. The anchored algorithm, "read every
input, transform it, concatenate into the output," lives in one place
either way: the base class's `run()`, or the function
`run_file_framework()`.

The search policy needs the word list while it processes each file.
The framework treats every input alike, so the client reads the word
list from the first file and hands the framework the rest:

```python
# exercise_1_search.py
import tempfile
from pathlib import Path
from typing import override
from exercise_1 import FileFramework, run_file_framework
from record import record

def found(words: list[str], text: str) -> str:
    present = [w for w in words if w in text.split()]
    return f"{' '.join(present)}\n"

@record
class Search(FileFramework):
    words: list[str]

    @override
    def process(self, text: str) -> str:
        return found(self.words, text)

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        wordfile = root / "words.txt"
        wordfile.write_text("spam\neggs\nham\n")
        (root / "a.txt").write_text("spam and eggs\n")
        (root / "b.txt").write_text("green eggs and ham\n")
        inputs = [str(root / "a.txt"), str(root / "b.txt")]
        words = wordfile.read_text().split()

        # Subclassing customization:
        out1 = root / "out1.txt"
        Search(words).run([*inputs, str(out1)])
        print(repr(out1.read_text()))

        # Function-passing customization:
        out2 = root / "out2.txt"
        run_file_framework(
            [*inputs, str(out2)],
            lambda text: found(words, text))
        print(repr(out2.read_text()))

demo()
#: 'spam eggs\neggs ham\n'
#: 'spam eggs\neggs ham\n'
```

The report has one line for each input file, naming the search words
that file contains. The two forms differ in where the word list
lives. `Search` stores it in a field, and the lambda closes over the
local variable `words`. In both, `run()` and `run_file_framework()`
stay unchanged: a new policy is a new step, and the algorithm that
calls the step belongs to the framework.

</details>
</details>
</details>

## 2. Two fixes for the premature engine

> Repair `premature_engine.py` both ways:
> first reorder the two lines in `Greeter.__init__()`,
> then redesign `Framework` instead,
> so clients construct the object and call `run()` explicitly.
> Which repair still protects a second subclass author who has never read this chapter?

<details>
<summary>Where to look</summary>

[Don't Start the Engine in the Constructor](../../Chapters/25_Patterns--Template_Method.md#dont-start-the-engine-in-the-constructor) shows `Framework.__init__()` calling a step before the subclass has set its attributes.
One repair changes the order of two lines in `Greeter.__init__()`.
The other removes the call from `Framework.__init__()` so that the client calls `run()`.
To choose between them, consider who must remember what.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_2_reorder.py
from typing import final, override

class Framework:
    def __init__(self) -> None:
        ...

    @final
    def run(self) -> None:
        ...

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        ...

    @override
    def step(self) -> None:
        ...
```

```python
# The shape of exercise_2_redesign.py
from typing import final, override

class Framework:
    @final
    def run(self) -> None:  # No longer called from __init__
        ...

    def step(self) -> None: ...

class Greeter(Framework):
    def __init__(self, name: str) -> None:
        ...

    @override
    def step(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

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
site, `greeter.run()`, moves the decision about when the algorithm
starts from the base class to the code that knows the object is
ready. The same reasoning drives eager versus lazy construction in
[*Singleton*](../../Chapters/24_Patterns--Singleton.md#double-checked-locking-and-eager-creation),
where the timing of a hidden step makes the difference.

</details>
</details>
</details>

## 3. Who objects to a replaced `run()`

> Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
> Run it, then run `ty` over it.
> Which of the two, Python or the type checker, objects to the change?
> What does that tell you about where the anchored algorithm's guarantee comes from?

<details>
<summary>Where to look</summary>

[Hooks and the Misspelled Override](../../Chapters/25_Patterns--Template_Method.md#hooks-and-the-misspelled-override) explains how `@final` marks `run()` as the fixed part of the *Template Method*.
Override `run()` anyway, run the file, then run `ty` over it.
Compare what each one reports, and ask which of them reads the `@final` marker.
A `# type: ignore` on the override keeps the listing in the build.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_3.py
from typing import final, override

class ApplicationFramework:
    @final
    def run(self) -> None:
        ...

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Reversed(ApplicationFramework):
    @override
    def run(self) -> None:  # type: ignore
        ...

    @override
    def customize1(self) -> None:
        ...

    @override
    def customize2(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

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

`ty` objects. The override carries a `# type: ignore` so this listing
stays in the book's build:

```
error[override-of-final-method]: Cannot override `ApplicationFramework.run`
info: `ApplicationFramework.run` is decorated with `@final`, forbidding overrides
```

The guarantee comes from the type checker, not the language. `@final`
sets `__final__ = True` on the function, and nothing in the
interpreter consults that attribute. The *Template Method*'s central
guarantee is therefore in the same category as every other annotation
in this book: a tool enforces it before the program executes, and
only when you run that tool.

`@final` protects a codebase whose build runs a type checker, and
protects nothing in a codebase that does not. When the interpreter
must refuse the override, use the `__init_subclass__()` check from
the chapter's `near_miss.py`, which reads `__final__` from each
method a subclass replaces. The check raises a `TypeError` at the
subclass's `class` statement, as soon as the class body has run, long
before anyone constructs an instance.

</details>
</details>
</details>

## 4. Two faithless substitutes the type checker accepts

> Write two subclasses of `ApplicationFramework` that both type-check but break the anchored algorithm:
> one whose `customize1()` raises an exception the base never raises,
> and one that leaves `customize2()` at its `...` default when the flow depends on it.
> The type checker reports neither.
> What must be true of the base class for the type checker to catch either one?

<details>
<summary>Where to look</summary>

[Substitutability](../../Chapters/25_Patterns--Template_Method.md#substitutability) shows a subclass that type-checks yet breaks the algorithm the base class anchors.
Write one subclass whose `customize1()` raises an exception, and one that keeps the `...` default for a step the flow depends on.
The base class can declare a step mandatory with `ABC` and `@abstractmethod`.
Consider which of the two failures any declaration available in Python could expose.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_4.py
from typing import final, override
from exceptions import expect

class ApplicationFramework:
    @final
    def run(self) -> None:
        ...

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

class Exploder(ApplicationFramework):
    @override
    def customize1(self) -> None:
        ...

class HalfDone(ApplicationFramework):
    def __init__(self) -> None:
        ...

    @override
    def customize1(self) -> None:
        ...
```

<details>
<summary>Solution</summary>

```python
# exercise_4.py
from typing import final, override
from exceptions import expect

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

expect(RuntimeError, Exploder().run)
#: [RuntimeError] step 1 refuses

app = HalfDone()
app.run()
print(app.pending)
#: ['work', 'work']
```

The type checker reports nothing about either class. Both override with
the right name, the right parameters, and the right return type, so both satisfy
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
exception nor prints anything wrong. `pending` grows on every pass.
Nothing shows from outside until whatever `pending` feeds runs out of
memory or reports stale data.

`Exploder` and `HalfDone` need different things from a type checker,
and only one of those things exists.

`HalfDone`'s omission is repairable. The `...` body makes the step
optional, and that is the base class's decision: it declares that a
subclass may skip this step. Declare instead that a subclass may not,
by inheriting from `ABC` and marking `customize2()` with
`@abstractmethod`, and Python refuses to construct `HalfDone`. The
type checker reports the construction too, before the program runs.
No checker could catch the omission before, because
"deliberately empty" and "forgotten" were the same code, and only
the base class could have recorded that difference.

`Exploder`'s exception is not repairable this way. For a type
checker to catch `Exploder`, the base class must state which
exceptions a step may raise, and the checker must hold every
override to that list, the mechanism Java's `throws` clause provides. Python has no such declaration, and no
annotation expresses "this raises nothing." An exception type in a
docstring is a note to a human. Only discipline, review, or a test
catches `Exploder`.

That split is the chapter's point stated from the other side. `@final`
protects the shape of the algorithm, and `@abstractmethod` protects the
presence of a step, because both are properties of the class structure
that a base class can declare. What a step does once called is
behavior, and Liskov substitution is a rule about behavior, so
enforcing it stays where the chapter leaves it: with you.

</details>
</details>
</details>

## 5. Which names the misspelling check compares

> In `near_miss.py`, subclass `MyApp` with a class that adds a method named `reports()`.
> Predict what the `class` statement does, then run it.
> Which names does `__init_subclass__()` compare a new method against?
> Change the check so it compares a new method only against the names `ApplicationFramework` defines.
> What does the narrower check no longer catch?

<details>
<summary>Where to look</summary>

[Hooks and the Misspelled Override](../../Chapters/25_Patterns--Template_Method.md#hooks-and-the-misspelled-override) builds the set of known names inside `__init_subclass__()` from the classes in `cls.__mro__`.
Add a method to `MyApp`, subclass it with a near-miss name, and watch which names the check sees.
For the narrower version, take the names from `vars(ApplicationFramework)` alone.
Then test a misspelling of a name that a subclass added.

<details>
<summary>The shape</summary>

```python
# The shape of exercise_5.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

class ApplicationFramework:
    @final
    def run(self) -> None:
        ...

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

    def __init_subclass__(cls) -> None:
        ...

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        ...

    def report(self) -> None: ...
```

```python
# The shape of exercise_5_narrow.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

class ApplicationFramework:
    @final
    def run(self) -> None:
        ...

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

    def __init_subclass__(cls) -> None:
        ...

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        ...

    def report(self) -> None: ...

class Audited(MyApp):
    def reports(self) -> None: ...
```

<details>
<summary>Solution</summary>

The chapter's `__init_subclass__()` builds its set of names from every
base class, so the set grows as the hierarchy does. `MyApp` adds
`report()`, and a subclass of `MyApp` inherits that name along with
the framework's own:

```python
# exercise_5.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        inherited = {
            name
            for base in cls.__mro__[1:]
            for name in vars(base)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            replaced = getattr(super(cls, cls), name, None)
            if getattr(replaced, "__final__", False):
                raise TypeError(
                    f"{cls.__name__}.{name} "
                    "overrides a @final method"
                )
            if name in inherited:
                continue
            if near := get_close_matches(name, inherited):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Audited(MyApp):
        def reports(self) -> None: ...
#: [TypeError] Audited.reports: did you mean report?
```

The `class Audited` statement raises a `TypeError`. The check
compares a new method against every non-dunder name in every base,
and `report` is one of them, although `report()` is a helper that
`MyApp` added and no step of the framework. The framework enforces a
rule about a name it did not define.

The narrower check reads its names from `ApplicationFramework` alone:

```python
# exercise_5_narrow.py
from difflib import get_close_matches
from typing import final, override
from exceptions import expected

class ApplicationFramework:
    @final
    def run(self) -> None:
        for _ in range(2):
            self.customize1()
            self.customize2()

    def customize1(self) -> None: ...
    def customize2(self) -> None: ...

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        declared = {
            name
            for name in vars(ApplicationFramework)
            if not name.startswith("__")
        }
        for name in vars(cls):
            if name.startswith("__"):
                continue
            replaced = getattr(super(cls, cls), name, None)
            if getattr(replaced, "__final__", False):
                raise TypeError(
                    f"{cls.__name__}.{name} "
                    "overrides a @final method"
                )
            if name in declared:
                continue
            if near := get_close_matches(name, declared):
                raise TypeError(
                    f"{cls.__name__}.{name}: "
                    f"did you mean {near[0]}?"
                )

class MyApp(ApplicationFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

class Audited(MyApp):
    def reports(self) -> None: ...

print(Audited.reports.__qualname__)
#: Audited.reports

with expected(TypeError):
    class Typo(MyApp):
        def customise2(self) -> None: ...
#: [TypeError] Typo.customise2: did you mean customize2?
```

`ApplicationFramework` exists by the time any subclass's `class`
statement runs, so `__init_subclass__()` can name it. `Audited` now
finishes, and a misspelled step still fails at any depth of the
hierarchy, because the check compares every subclass against the
framework's three names.

The narrower check no longer catches a misspelling of a name that a
subclass introduced. If `Audited` meant to override `report()`, its
`reports()` is a new method that nothing calls, and the framework
reports nothing. Catching that misspelling falls to `Audited`'s
author, who can use the protection the chapter recommends for steps:
`@override` on the method, and a type checker in the build.

</details>
</details>
</details>
