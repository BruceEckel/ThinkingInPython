# Template Method: Solutions

## 1. A file-processing framework, customized both ways

> Create a framework that takes a list of file names.
> It opens every file but the last for reading, and the last one for writing.
> It processes each input file by a step the subclass or the function supplies,
> and writes the output to the last file.
> Supply each of these steps twice,
> once by subclassing and once by passing a function:
>
> 1.  Convert all the letters in each file to uppercase.
> 2.  Treat the first file as a list of search words, one per line,
>     and report which of those words appear in each remaining input file.

<details>
<summary>Where to look</summary>

[Passing the Steps as Functions](../../Chapters/24_Patterns--Template_Method.md#passing-the-steps-as-functions)
shows the same algorithm anchored in a function that takes the varying step as an argument.
The subclass form is in [The Anchored Algorithm](../../Chapters/24_Patterns--Template_Method.md#the-anchored-algorithm).
Put the shared loop (read each input, apply the step, write the output)
in one `run()` and one function, and leave `process()` as the one open step.
The search policy needs the word list,
so store it on the subclass and close over it in the function form.

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
<summary>Done when</summary>

given input files holding `hello` and `world`,
both your subclass and your function form write `'HELLO\nWORLD\n'` to the last file.
Given search words `spam`, `eggs`, and `ham`,
and inputs `spam and eggs` and `green eggs and ham`,
both forms write `'spam eggs\neggs ham\n'`, one line per input file.

<details>
<summary>Solution</summary>

The framework appears twice,
as a base class whose `run()` is the template method and as a function that takes the step as an argument.
Every customization must supply `process()`,
so the base class declares it with `@abstractmethod`:

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

**Let a subclass be a record.**
The empty `__slots__` lets a subclass that carries data be a record,
as [Rethinking Objects](../../Chapters/20_Patterns--Rethinking_Objects.md#abstract-base-classes)
explains.
`Search`, which stores its word list in a field, is such a record.

The uppercase policy needs no data.
The function form passes `str.upper`,
which has the signature the framework expects:

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

The search policy needs the word list while it processes each file.
The framework treats every input alike,
so the client reads the word list from the first file and passes the framework the rest:

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

The report has one line for each input file,
naming the search words that file contains.

**Give the step its data.**
The two forms differ in where they store the word list.
`Search` stores it in a field.
The lambda closes over the local variable `words`.
In both, `run()` and `run_file_framework()` stay the same.
A new policy is a new step.
The algorithm that calls the step belongs to the framework.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 2. Two fixes for the premature engine

> Repair `premature_engine.py` both ways:
> first reorder the two lines in `Greeter.__init__()`,
> then redesign `Framework` instead,
> so clients construct the object and then call `run()`.
> Which repair still protects a second subclass author who has not read this chapter?

<details>
<summary>Where to look</summary>

[Don't Start the Engine in the Constructor](../../Chapters/24_Patterns--Template_Method.md#dont-start-the-engine-in-the-constructor)
shows `Framework.__init__()` calling a step before the subclass has set its attributes.
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
<summary>Done when</summary>

both your files print `Hello, Brian!` (with your name)
where `premature_engine.py` raises an `AttributeError`, and in the redesign,
the greeting waits for the client to call `run()`.
You can answer the closing question by stating what a later subclass author must remember under each repair.

<details>
<summary>Solution</summary>

If you drop the `super().__init__()` call from `Greeter.__init__()` to avoid the trap,
`Greeter("Brian")` completes silently,
because the engine starts in `Framework.__init__()`,
which `Greeter` now bypasses.
The type checker accepts the class too.
The reorder keeps the call and moves it after the setup.
The redesign takes the start out of construction and gives it to the client.

The quick repair reorders the two lines so the subclass finishes its own setup before it calls `Framework.__init__()`:

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

The redesign removes the hazard instead of avoiding it.
`Framework` drops its `__init__()`,
so the client builds a finished object and then starts it:

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

The redesign protects the next author.
The reorder protects the one subclass that performs it.
Each later subclass is safe only if its author remembers to do the same.
The reorder asks every future subclass author to invert the convention they have used everywhere else,
which is to call `super().__init__()` first.
The signature of `Framework.__init__()` is silent on the order.
Every type checker accepts the usual one.
Python reports the failure as an `AttributeError` raised in the subclass's own `step()`,
called from a base class someone else wrote.
The next author may not have read this chapter.

Separating construction from starting makes the mistake impossible,
because the engine starts in `run()`,
and the client calls `run()` on a finished object.
Each call site gains a line, `greeter.run()`.
That line moves the decision about when the algorithm starts from the base class to the client.
The same reasoning favors eager creation in [*Singleton*](../../Chapters/23_Patterns--Singleton.md#double-checked-locking-and-eager-creation).
Eager creation builds the object at import time,
before any thread can read a half-built one.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 3. Who objects to a replaced `run()`

> Subclass `ApplicationFramework` and override `run()` with a version that calls `customize2()` before `customize1()`.
> Run it, then run `ty` over it.
> Which of the two, Python or the type checker, objects to the change?
> What does that tell you about the source of the anchored algorithm's guarantee?

<details>
<summary>Where to look</summary>

[The Anchored Algorithm](../../Chapters/24_Patterns--Template_Method.md#the-anchored-algorithm)
explains how `@final` marks `run()` as the part of the *Template Method* that stays the same.
Override `run()` in a subclass, run the file, then run `ty` over it.
Compare what Python and the type checker each report,
and ask which of them reads the `@final` marker.
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
<summary>Done when</summary>

your file runs and prints `two`, `one`, `two`, `one` with no error,
and `uv run ty check` on it, with no `# type: ignore` on the override,
reports `override-of-final-method` at your `run()`.
You can then say which of the two reads `@final`,
and what that means for a build that skips the type checker.

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

Python accepts the override.
The anchored algorithm is no longer anchored.

The type checker objects.
The override carries a `# type: ignore` to keep this listing in the book's build.
With that comment removed, `ty` reports:

```
error[override-of-final-method]: Cannot override `ApplicationFramework.run`
info: `ApplicationFramework.run` is decorated with `@final`, forbidding overrides
```

The guarantee comes from the type checker, not the language.
`@final` sets `__final__ = True` on the function.
The interpreter ignores that attribute.
The *Template Method*'s central guarantee is therefore in the same category as every other annotation in this book.
A tool enforces it before the program executes, and only when you run that tool.

`@final` protects a codebase only when its build runs a type checker.
When the interpreter must refuse the override,
use the `__init_subclass__()` check from the chapter's `near_miss.py`,
which reads `__final__` from each method a subclass replaces.
The check raises a `TypeError` at the subclass's `class` statement,
as soon as the class body has run, long before anyone constructs an instance.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 4. Two faithless substitutes the type checker accepts

> Write two subclasses of `ApplicationFramework` that both type-check but break the anchored algorithm:
> one whose `customize1()` raises an exception the base does not raise,
> and one that leaves `customize2()` at its `...` default when the anchored algorithm depends on it.
> The type checker reports neither.
> What must be true of the base class for the type checker to catch either one?

<details>
<summary>Where to look</summary>

[Substitutability](../../Chapters/24_Patterns--Template_Method.md#substitutability)
shows a subclass that type-checks yet breaks the algorithm the base class anchors.
Write one subclass whose `customize1()` raises an exception,
and one that keeps the `...` default for a step on which the flow depends.
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
<summary>Done when</summary>

`uv run ty check` passes on your file;
`run()` on the first subclass lets your exception propagate out of `run()`,
and `run()` on the second returns normally while printing evidence that `customize2()` never did its share.
You can name a base-class change that makes the type checker report one subclass,
and say why the type checker accepts the other.

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

The type checker accepts both classes.
Both override with the right name, the right parameters,
and the right return type,
so both satisfy `@override` and every signature rule the base class states.

**Raise an unexpected exception.**
`Exploder` breaks the algorithm on the first step of the first pass.
Code written against `ApplicationFramework` expects `run()` to return normally for every subclass.
`Exploder`'s `customize1()` raises an exception,
which propagates out of `run()` into a caller written for the base version.

**Skip a step the flow needs.**
`HalfDone` breaks the algorithm more quietly,
which makes it the worse of the two.
`customize1()` accumulates work for `customize2()` to consume,
so the pair is a two-step flow.
Leaving `customize2()` at its default breaks the second half.
The program still completes normally.
`pending` grows on every pass.
The flaw stays hidden until the program runs out of memory or the code that reads `pending` reports stale data.

`Exploder` and `HalfDone` need different things from a type checker.
Only one of those things exists.

A declaration in the base class can expose `HalfDone`'s omission.
Through the `...` body,
the base class declares that a subclass may skip this step.
With that body, no checker can catch the omission,
because "deliberately empty" and "forgotten" are the same code.
Only the base class can record that difference.
The base class can declare that a subclass must supply the step,
by inheriting from `ABC` and marking `customize2()` with `@abstractmethod`.
Then constructing `HalfDone` raises a `TypeError`.
The type checker reports the construction before the program runs.

Exposing `Exploder`'s exception would take a declaration that Python lacks.
For a type checker to catch `Exploder`,
the base class must state which exceptions a step may raise,
and the checker must compare every override with that list.
Java's `throws` clause provides that mechanism for checked exceptions.
Python has no such declaration,
and no annotation expresses "this raises nothing."
An exception type in a docstring is a note to a human.
Only discipline, review, or a test catches `Exploder`.

`@final` protects the shape of the algorithm,
and `@abstractmethod` protects the presence of a step,
because both are properties of the class structure that a base class can declare.
What a step does once called is behavior,
and [Liskov substitution](../../Chapters/20_Patterns--Rethinking_Objects.md#liskov-substitution)
is a rule about behavior.
No tool checks substitution,
so the chapter leaves that check to your discipline.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>

## 5. Which names the misspelling check compares

> In `near_miss.py`, subclass `MyApp` with a class that adds a method named `reports()`.
> Predict what the `class` statement does, then run it.
> Against which names does `__init_subclass__()` compare a new method?
> Change the check so it compares a new method only against the names `ApplicationFramework` defines.
> What does the narrower check no longer catch?

<details>
<summary>Where to look</summary>

[Hooks and the Misspelled Override](../../Chapters/24_Patterns--Template_Method.md#hooks-and-the-misspelled-override)
builds the set of known names inside `__init_subclass__()` from the classes in `cls.__mro__`.
`MyApp` defines `report()`.
Subclass it, add a method whose name is one letter off a known name,
and watch which names the check sees.
For the narrower version,
take the names from `vars(ApplicationFramework)` alone.
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

class CheckedFramework(ApplicationFramework):
    def __init_subclass__(cls) -> None:
        ...

class MyApp(CheckedFramework):
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

class CheckedFramework(ApplicationFramework):
    def __init_subclass__(cls) -> None:
        ...

class MyApp(CheckedFramework):
    @override
    def customize1(self) -> None:
        ...

    def report(self) -> None: ...

class Audited(MyApp):
    def reports(self) -> None: ...
```

<details>
<summary>Done when</summary>

your subclass of `MyApp` with `reports()` fails at its `class` statement with a `TypeError` ending `did you mean report?`.
Under your narrowed check the same class completes,
while a subclass defining `customise2()` still fails with `did you mean customize2?`.
You can say which misspelling now passes unreported.

<details>
<summary>Solution</summary>

The chapter's `__init_subclass__()` builds its set of names from every base class,
so the set grows as the hierarchy does.
A subclass of `MyApp` inherits `report()` along with the framework's own names:

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

class CheckedFramework(ApplicationFramework):
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

class MyApp(CheckedFramework):
    @override
    def customize1(self) -> None:
        print("one")

    def report(self) -> None: ...

with expected(TypeError):
    class Audited(MyApp):
        def reports(self) -> None: ...
#: [TypeError] Audited.reports: did you mean report?
```

**Compare against every base.**
The check compares a new method against every non-dunder name in every base,
and `report` is one of those names.
Yet `report()` is a helper that `MyApp` added, not a step of the framework,
so the framework enforces a rule about a name that belongs to `MyApp`.

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

class CheckedFramework(ApplicationFramework):
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

class MyApp(CheckedFramework):
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

**Draw names from the framework alone.**
`ApplicationFramework` exists by the time any subclass's `class` statement runs,
so `__init_subclass__()` can name it.

**Pass the helper, catch the step.**
The `class Audited` statement now completes.
A misspelled step still fails at any depth of the hierarchy,
because the check compares the methods of every subclass with the framework's three names.

A misspelling of a name that a subclass introduced now passes the narrower check.
If `Audited` meant to override `report()`, its `reports()` is a new method,
and every call to `report()` still reaches `MyApp`'s version.
The framework accepts it.
`Audited`'s author must catch that misspelling,
using the protection the chapter recommends for steps:
`@override` on the method, and a type checker in the build.

Before you move on, name what separates your attempt from this one:
a different design, a detail, or an equivalent alternative.

</details>
</details>
</details>
</details>
