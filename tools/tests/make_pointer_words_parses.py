#!/usr/bin/env python
"""Record the real spaCy parse of the fixture paragraphs the pointer tests use.

The tests in `test_pointer_words.py` must not need spaCy, so they read
`tools/tests/data/pointer_words_parses.json`, a map from paragraph text
to the parser's output, through `recorded_parser()`. Regenerate it after
a spaCy or model upgrade, or when `SOURCES` changes, with the parser
available to `uv`:

    uv run python -m tools.tests.make_pointer_words_parses

Then run `uv run tip tools-test` and read any test that moved.
"""

import json
from pathlib import Path
from typing import Final
from tools.markdown import Document
from tools.parsed_prose import RawSentence, parse
from tools.stranded_prepositions import joined, paragraphs

DATA: Final = Path(__file__).with_name("data") / "pointer_words_parses.json"

SOURCES: Final[tuple[str, ...]] = (
    "The proxy stores the level. It never consults the implementation again.",
    "The proxy stores the level. The proxy never consults the "
    "implementation again.",
    "The handler checks the key. This is the fast path.",
    "The handler checks the key. This check is the fast path.",
    "It is the loop that calls the method.",
    "The function runs. It returns quickly.",
    "The function returns a wrapper. It keeps the name.",
    "The proxy stores the level. Then it never consults the "
    "implementation again.",
    "The responders hold the values. They are weak references.",
    "It stores the level.",
    "Hint: this is the fast path. It stores the level.",
    "Some prose.\n\nThe proxy stores the level.\nIt never consults the\n"
    "implementation again.",
    "The proxy stores the level.\nIt never consults the\n"
    "implementation again.",
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
