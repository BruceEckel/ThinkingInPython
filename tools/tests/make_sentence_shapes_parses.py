#!/usr/bin/env python
"""Record the real spaCy parse of the fixture paragraphs the shape tests use.

The tests in `test_sentence_shapes.py` and `test_subject_gap.py` must
not need spaCy, so they read `tools/tests/data/sentence_shapes_parses.json`,
a map from paragraph text to the parser's output, through
`recorded_parser()`. Regenerate it after a spaCy or model upgrade, or
when `SOURCES` changes, with the parser available to `uv`:

    uv run python -m tools.tests.make_sentence_shapes_parses

Then run `uv run tip tools-test` and read any test that moved: a rule
that stopped firing on a fixture is the upgrade changing a parse, which
is what the fixture exists to show.
"""

import json
from pathlib import Path
from typing import Final
from tools.markdown import Document
from tools.parsed_prose import RawSentence, parse
from tools.stranded_prepositions import joined, paragraphs

DATA: Final = Path(__file__).with_name("data") / "sentence_shapes_parses.json"

SOURCES: Final[tuple[str, ...]] = (
    "`drive()`, imported unchanged, answers a request yielded two generators deep the same way it answers one from `interview()`'s own body.",
    "`drive()` is imported unchanged. The requests now come from `ask()`, one generator below `interview()`, and `yield from` passes each one up to the driver, so `drive()` sees the same `Question`s it saw in `interview_generator.py`.",
    "Use a `set` rather than a `list` for membership tests.",
    "Remove `frozen=True` and the pattern fails.",
    "If you remove `frozen=True`, the pattern fails.",
    "Forget the new argument at a call and `ty` reports "
    "a `missing-argument`.",
    "If you forget the new argument at a call, `ty` reports "
    "a `missing-argument`.",
    "Try the operation and handle the exception.",
    "Run `ty` and read the error it reports.",
    "The handler reads the key, and it stores the entry.",
    "A `@dataclass` `Thermometer` has no list of listeners, and "
    "`subscribe()` raises an `AttributeError`.",
    "The design has three parts: an `Observer` interface, a `Subject` "
    "base class, and a `notify()` method.",
    "The call prints this: `hello`.",
    "The check has one limit: it reads literal text.",
    "Python supplies `self` only when the lookup finds the function "
    "on the class: a function stored there is a descriptor, and "
    "reading it through an instance binds that instance.",
    "Hint: Remove `frozen=True` and the pattern fails.",
    "The rule has a limit:",
    "A function is a descriptor, and reading it binds that instance.",
    "A state's row holds its action, so an action that must run on "
    "every entry into that state appears once.",
    "Remove `frozen=True` and confirm the program runs the same "
    "way while the type checker reports nothing.",
    "Write a test in which the first responder fails and the second "
    "still records its notification.",
    "Then ask what holds the callback, and what that means for the "
    "reference count.",
    "Explain both failures, and why an intermediate kick avoids them.",
    "Confirm that reading `x` several times builds nothing, and that "
    "the first `y` reports the count.",
    "Then say what you gave up, and whether `Foo` should be a "
    "subclass of `Bar`.",
    "Three tests check what the lease guarantees: the item leaves the "
    "pool, it comes back when the block raises an exception, and the "
    "pool hands out the same object.",
    "This technique is *dependency injection*: the caller hands the "
    "function its dependencies, and the function fetches nothing on "
    "its own.",
    "The handler nearest the Effect answers first, and the outer one "
    "handles the requests that remain.",
    "The prediction: the lease returns the item.",
    "The problem appears whenever the producer keeps state between "
    "values and the consumer has a loop of its own.",
    "The problem appears whenever the producer keeps state from one "
    "value to the next while the consumer has a loop of its own.",
    "`interview()` runs the same under both drivers and each returns "
    "the result.",
    "Both forms keep the result and the name.",
    "A `break` at the match leaves both loops in one step and skips "
    "`else` along with them.",
    "A call between the check and the use can reset that attribute.",
    "`Temperature` has no `__dict__` to assign them, so neither the "
    "class nor the instance holds an `celsius`.",
    "The third-party `more-itertools` package supplies one as "
    "`iterate(func, start)`, which produces `start`, `func(start)`, "
    "`func(func(start))`, and so on without end, and `toolz` has an "
    "`iterate()` of the same shape.",
    "The third-party `more-itertools` package supplies one as "
    "`iterate(func, start)`, which produces `start`, `func(start)`, "
    "`func(func(start))`, and so on without end. `toolz` has an "
    "`iterate()` of the same shape.",
    "Intro paragraph.",
    "A closure keeps its captured variables between calls, but each call runs its body from the top. The generator keeps its place as well, so a loop in progress survives.",
    "A closure keeps its captured variables between calls, but each call runs its body from the top. The generator keeps its locals and its place in the body, so a loop in progress survives.",
    "It checks the declaration's type and ignores which code runs first. Pyright accepts the read too.",
    "Programmers have been bad at keeping objects inside that set. Constructing an object in an illegal state is too easy.",
    "The copy shares the inner objects. It duplicates the outer list as well.",
)
"""Markdown paragraphs; each is cleaned the way the checks clean it."""


def cleaned(source: str) -> str:
    """The text the checks send the parser for this one-paragraph source."""
    found = list(paragraphs(Document.from_text(source)))
    assert len(found) == 1, source
    return joined(found[0])[0]


def recorded_parser(texts: list[str]) -> list[list[RawSentence]]:
    """A parser stub that answers from the recorded file, by text."""
    table = json.loads(DATA.read_text(encoding="utf-8"))
    return [table[text] for text in texts]


def main() -> None:
    texts = [cleaned(source) for source in SOURCES]
    answers = parse(texts)
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(
        json.dumps(dict(zip(texts, answers, strict=True)), indent=1) + "\n",
        encoding="utf-8", newline="\n")
    print(f"Recorded {len(texts)} paragraphs in {DATA}")


if __name__ == "__main__":
    main()
