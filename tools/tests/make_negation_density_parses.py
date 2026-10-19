#!/usr/bin/env python
"""Record the real spaCy parse of the fixture paragraphs the negation tests use.

The tests in `test_negation_density.py` must not need spaCy, so they read
`tools/tests/data/negation_density_parses.json`, a map from paragraph text
to the parser's output, through `recorded_parser()`. Regenerate it after
a spaCy or model upgrade, or when `SOURCES` changes, with the parser
available to `uv`:

    uv run python -m tools.tests.make_negation_density_parses

Then run `uv run tip tools-test` and read any test that moved.
"""

import json
from pathlib import Path
from typing import Final
from tools.markdown import Document
from tools.parsed_prose import RawSentence, parse
from tools.stranded_prepositions import joined, paragraphs

DATA: Final = (Path(__file__).with_name("data")
               / "negation_density_parses.json")

SOURCES: Final[tuple[str, ...]] = (
    "The handler is not ready.",
    "No caller can tell.",
    "The argument stays unchanged.",
    "The handler is stateless.",
    "The class lacks a method.",
    "The function returns without checking the key.",
    "The handler accepts only keyword arguments.",
    "The handler is not ready and stays unchanged.",
    "The handler is not ready, has no key, and stays unchanged.",
    "Hint: the handler is not ready, has no key, and stays unchanged.",
    "The function under the unique key joins the union.",
    "The handler runs unless the key changes.",
    "The handler is not ready, not valid, and not open.",
    "Nevertheless, the handler runs regardless of the key.",
    "Stateless handles the effect.",
    "The handler is not ready, has no key, and takes only one "
    "argument, unchanged.",
    "The handler is not ready, has no key, and stays unchanged. "
    "It never runs.",
    "Some prose.",
)
"""Markdown paragraphs; each is cleaned the way the checks clean it."""


def cleaned(source: str) -> list[str]:
    """The texts the checks send the parser for this source."""
    return [joined(p)[0] for p in paragraphs(Document.from_text(source))]


def recorded_parser(texts: list[str]) -> list[list[RawSentence]]:
    """A parser stub that answers from the recorded file, by text."""
    table = json.loads(DATA.read_text(encoding="utf-8"))
    return [table[text] for text in texts]


def main() -> None:
    texts = [text for source in SOURCES for text in cleaned(source)]
    answers = parse(texts)
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(
        json.dumps(dict(zip(texts, answers, strict=True)), indent=1) + "\n",
        encoding="utf-8", newline="\n")
    print(f"Recorded {len(texts)} paragraphs in {DATA}")


if __name__ == "__main__":
    main()
