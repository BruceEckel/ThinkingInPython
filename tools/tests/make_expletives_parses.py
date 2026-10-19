#!/usr/bin/env python
"""Record the real spaCy parse of the fixture paragraphs the expletive tests use.

The tests in `test_expletives.py` must not need spaCy, so they read
`tools/tests/data/expletives_parses.json`, a map from paragraph text
to the parser's output, through `recorded_parser()`. Regenerate it after
a spaCy or model upgrade, or when `SOURCES` changes, with the parser
available to `uv`:

    uv run python -m tools.tests.make_expletives_parses

Then run `uv run tip tools-test` and read any test that moved.
"""

import json
from pathlib import Path
from typing import Final
from tools.markdown import Document
from tools.parsed_prose import RawSentence, parse
from tools.stranded_prepositions import joined, paragraphs

DATA: Final = Path(__file__).with_name("data") / "expletives_parses.json"

SOURCES: Final[tuple[str, ...]] = (
    "There is a simpler design.",
    "A simpler design exists.",
    "There are three parts.",
    "The loop calls the method.",
    "It is easy to add a state.",
    "Adding a state is easy.",
    "It is a record.",
    "It is true that the loop stops.",
    "Put the file there.",
    "Caching there is one way to build a Singleton.",
    "In hindsight, it might have been better to name the file.",
    'The message says "there is no such file".',
    "Without a guard, there is a race.",
    "Hint: there is a race.",
    "There is a race, and it is easy to add a lock.",
    "Some prose.",
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
