#!/usr/bin/env python
"""Record the real spaCy parse of the fixture text the past-tense tests use.

The tests in `test_past_tense.py` must not need spaCy, so they read
`tools/tests/data/past_tense_parses.json`, a map from text to the
parser's output, through `recorded_parser()`. The map holds every
paragraph in `SOURCES` as the checks clean it, and every heading in
`HEADINGS` as `heading_lines()` cleans it. Regenerate the file after a
spaCy or model upgrade, or when either list changes, with the parser
available to `uv`:

    uv run python -m tools.tests.make_past_tense_parses

Then run `uv run tip tools-test` and read any test that moved.
"""

import json
from pathlib import Path
from typing import Final
from tools.markdown import Document
from tools.parsed_prose import RawSentence, parse
from tools.past_tense import heading_lines
from tools.stranded_prepositions import joined, paragraphs

DATA: Final = Path(__file__).with_name("data") / "past_tense_parses.json"

SOURCES: Final[tuple[str, ...]] = (
    "One design served three jobs in this chapter.",
    "One design serves three jobs in this chapter.",
    "In every case the observer was a callable.",
    "Python 3.12 added the type statement.",
    "The 1994 book carried it into the mainstream.",
    "PEP 695 added the type statement.",
    "If the list were empty, the loop would stop.",
    "The marker was rewritten by the gate.",
    "The gate has rewritten the marker.",
    'The message says "the key was marked read-only".',
    "The loop ran first and the gate rewrote the marker.",
    "Hint: the loop ran first.",
    "The loop runs first. The gate rewrote the marker.",
    "The loop runs first,\nand the gate\nrewrote the marker.",
    "The function the caller passed runs.",
    "I began adding material.",
    "If the list were empty, it stops.",
    "One design served three jobs.",
    "Some prose.",
)
"""Markdown paragraphs; each is cleaned the way the checks clean it."""

HEADINGS: Final[tuple[str, ...]] = (
    "What Stayed Constant",
    "What Stays Constant",
    "What Stayed Constant {#stayed}",
)
"""Heading lines (without the `#`s); each is read by `heading_lines()`."""


def cleaned(source: str) -> str:
    """The text the checks send the parser for this one-paragraph source."""
    found = list(paragraphs(Document.from_text(source)))
    assert len(found) == 1, source
    return joined(found[0])[0]


def cleaned_heading(source: str) -> str:
    """The text the checks send the parser for this heading."""
    [(_, text)] = heading_lines(Document.from_text(f"## {source}"))
    return text


def recorded_parser(texts: list[str]) -> list[list[RawSentence]]:
    """A parser stub that answers from the recorded file, by text."""
    table = json.loads(DATA.read_text(encoding="utf-8"))
    return [table[text] for text in texts]


def main() -> None:
    texts = [cleaned(source) for source in SOURCES]
    texts += [cleaned_heading(source) for source in HEADINGS]
    texts = list(dict.fromkeys(texts))
    answers = parse(texts)
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(
        json.dumps(dict(zip(texts, answers, strict=True)), indent=1) + "\n",
        encoding="utf-8", newline="\n")
    print(f"Recorded {len(texts)} texts in {DATA}")


if __name__ == "__main__":
    main()
