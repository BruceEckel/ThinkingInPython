"""Which prose sentences one version of a chapter rewrote from another.

`prose_calibration.py` and `edit_patterns.py` both need the same
answer from a before and an after text: the sentences that were
rewritten, each paired with the new sentence most like it, and the
sentences left alone. Whitespace is collapsed first, so a reflow is not
a rewrite.

A sentence here is what `check_self_reference.sentences()` yields, less
the ones no sentence-level judgment applies to: table rows, list items
(the splitter joins a run of bullets into one "sentence" until it meets
terminal punctuation), figure captions, anything under 40 characters,
and anything holding a `[[...]]` draft note, which is a note to change
the sentence, not a sentence.
"""

import difflib
import re
from dataclasses import dataclass
from pathlib import Path

from tools.check_self_reference import sentences
from tools.markdown import Document

LIST_ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s")
MIN_CHARS = 40


PARAGRAPH_LIMIT = 2_000


@dataclass(frozen=True)
class Sentence:
    line: int
    text: str
    previous: str
    following: str
    heading: str = ""
    """The nearest heading above the sentence, `#` marks removed."""
    paragraph: str = ""
    """The whole paragraph holding the sentence, whitespace collapsed.
    A judgment about the passage ("the context does not already name
    the mechanism") needs more than the neighboring sentences."""


def surroundings(doc: Document) -> tuple[list[str], list[str]]:
    """Per line: the heading above it and the paragraph holding it."""
    fenced = doc.in_fence()
    headings: list[str] = []
    paragraphs: list[str] = [""] * len(doc.lines)
    heading, start = "", None
    for i, line in enumerate([*doc.lines, ""]):
        prose_line = i < len(doc.lines) and not fenced[i] and line.strip()
        if prose_line and line.startswith("#"):
            heading = line.lstrip("#").strip()
            prose_line = ""
        if prose_line and start is None:
            start = i
        if not prose_line and start is not None:
            text = " ".join(" ".join(doc.lines[start:i]).split())
            for j in range(start, i):
                paragraphs[j] = text[:PARAGRAPH_LIMIT]
            start = None
        if i < len(doc.lines):
            headings.append(heading)
    return headings, paragraphs


def prose(text: str, name: str) -> list[Sentence]:
    doc = Document.from_text(text, Path(name))
    headings, paragraphs = surroundings(doc)
    kept: list[tuple[int, str]] = []
    for line, s in sentences(doc):
        s = " ".join(s.split())
        if (len(s) < MIN_CHARS or s.startswith(("|", "![")) or "[[" in s
                or LIST_ITEM.match(s) or s.count(" - ") > 1):
            continue
        kept.append((line, s))
    return [Sentence(line, s,
                     kept[i - 1][1] if i else "",
                     kept[i + 1][1] if i + 1 < len(kept) else "",
                     headings[line - 1], paragraphs[line - 1])
            for i, (line, s) in enumerate(kept)]


@dataclass(frozen=True)
class Rewrite:
    before: Sentence
    after: str
    """The closest new sentence, or "" when none shares much with it."""
    similarity: float


def diff(before_text: str, after_text: str, name: str
         ) -> tuple[list[Rewrite], list[Sentence]]:
    """(rewritten sentences, sentences left alone) from one edit."""
    before = prose(before_text, name)
    new = prose(after_text, name)
    kept = {s.text for s in new}
    # The splitter ends a sentence at a line-final colon, so a reflow
    # that breaks a line after one splits a sentence nobody edited. Its
    # text still reads straight through the new version's words.
    running = " ".join(after_text.split())
    added = [t for t in kept if t not in {s.text for s in before}]
    rewrites: list[Rewrite] = []
    alone: list[Sentence] = []
    for s in before:
        if s.text in kept or s.text in running:
            alone.append(s)
            continue
        best, ratio = "", 0.0
        for a in added:
            r = difflib.SequenceMatcher(None, s.text, a).ratio()
            if r > ratio:
                best, ratio = a, r
        rewrites.append(Rewrite(s, best, round(ratio, 3)))
    return rewrites, alone
