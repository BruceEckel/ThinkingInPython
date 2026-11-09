#!/usr/bin/env python
"""Report prose that points at a listing line by position.

The book's convention: prose that points at a line of a listing uses a
numbered tag (`# [1]` in the code, `[1]` as a code span in the prose),
not a positional phrase ("the second `print()`", "the last line",
"line 3") and not a construct name that the listing holds more than
once ("the `for` loop" when the listing has two `for`s). This check
lists the prose that still points positionally, so a human can judge
each hit.

A listing's prose region is the lines after its closing fence, up to
the next fenced block or the next heading, whichever comes first (the
same region `tools/listing_tags.py` uses). Prose before a section's
first listing belongs to no region and is never scanned. Inside a
region the check builds paragraphs: blank lines split them; headings,
block quotes, tables, HTML lines and comments, link definitions, and
`#:` lines are skipped; a list item starts a new paragraph and keeps
its item text. Code spans stay raw, because the patterns read their
text. Each paragraph is joined with single spaces and split into
sentences at `.`, `?`, or `!` followed by whitespace or the end. Code
spans are masked first, so a `.` in `self.x` or a `?` inside a span
never splits. A sentence that holds a citation, a code span whose
whole content is `[n]` with n from 1 up, is already tagged and is
skipped.

Six patterns match on the raw sentence, with ORD an ordinal or
position word (first, last, next, inner, top, ...) and NOUN a
statement-like word (line, call, loop, print, return, ...):

1. `ordinal+noun`: "the ORD NOUN" ("the last line").
2. `ordinal+span`: "the ORD `code`" ("the second `print()`").
3. `line-number`: "line 3", "on lines 4", "at line 7".
4. `line-rel`: "the line above", "the statement that", "the lines
   below".
5. `n-lines`: "two lines later", "a few statements above".
6. `construct`: "the `for` loop", "the if branch", for a keyword in
   `KEYWORDS` followed by a construct noun. It is a hit only when the
   owning block's code holds that keyword two or more times, counted
   per line with the part after the first `#` removed (a crude
   comment strip: a `#` inside a string also cuts the line). The kind
   label carries the count, as in `construct x3`.
7. `count+unit` (2026-11-04): a count applied to an execution noun,
   "the first three runs", "both attempts", "every pass", "the second
   round". The unit counts executions rather than lines, so no tag
   names it, and the fault is a listing that offers more than one way
   to count it: chapter 45's `throw_close_basics.py` has three
   generators and four tagged resumptions, and "the first three runs"
   was right under one count and false under the other. The test is
   whether the listing offers a second way to count the unit; if it
   does, name the unit concretely ("all three generators") or cite the
   tags. The number of the noun follows the count word (each/every
   and an ordinal take the singular, a cardinal or both/all the
   plural), so a quantifier before a verb ("both run", "each runs")
   never matches. A match that overlaps another pattern's match ("the
   first call", already `ordinal+noun`) is dropped. The same shape on
   `call` and `time` ("the first call", "each time") is a survey
   rule, `survey count+unit`: too common and too often right for a
   baseline, it prints under `--survey` only, marked `survey`, and is
   never counted as new. The `ambiguity` skill reads it per chapter.
8. `survey alternative` (2026-11-08): a sentence in a walkthrough
   paragraph that describes a construct the listing lacks, in the
   plain present, with no word marking it as the road not taken.
   Bruce read, under chapter 45's `drive_by_hand.py` (whose driver
   is a `try` statement), "A `for` loop treats `StopIteration` as
   the normal end of the loop, so it discards the exception" and
   took it for the next step of the run: "describing an alternative
   in the same place where the description of what's actually
   happening is described". Two shapes match: a sentence opening
   on an indefinite article and a code span ("A `for` loop", "An
   `__init__()` that assigns `_value_`") whose identifier is absent
   from the owning block's code, and a code span holding a Python
   statement keyword (`ALT_KEYWORDS`) absent from that code. The
   paragraph must be a walkthrough: an earlier sentence in it names
   a code span the block does hold. A sentence carrying a marker
   word (`ALT_MARKERS`: if, would, instead, rather, another, a
   comparison or negation word, and so on) is quiet, since the
   marker already tells the reader. The repair frames the
   alternative ("With a `return` at the match in place of the
   `break` at `[1]`", "If `__init__()` assigns `_value_`", "because
   a `for` loop would discard the exception") and the keeps are a
   general fact about a type that holds for the listing too, and an
   alternative an earlier sentence in the paragraph introduced
   ("The real mistake is catching too much. A bare `except:` ...").
   The 2026-11-08 read over the book had 35 hits of this tightened
   shape and 5 rewrites, so it is a survey rule, printed under
   `--survey`, never baselined; the `ambiguity` skill reads it. A
   sentence that cites a tag is still read for this rule, since the
   chapter 04 find cited `[5]`.

9. `survey self-name` (2026-11-09): a lead-in, the prose paragraph
   directly above a fenced listing, that names that listing's own
   file in a code span. Bruce read chapter 45's "In
   `yield_from_nested.py`, a `yield from` in `survey()` receives that
   `Result`:" above the block whose first line is `# yield_from_nested.py`
   and found it confusing: "it sounds like it's referring to some
   other listing, but it's actually the listing the sentence is
   introducing." The repair is "Here, ..." or the thing itself, since
   the listing's first line already carries the filename. The
   paragraph is found by walking back from the opening fence over
   blank lines; a heading, fence, table row, block quote, list item,
   or HTML comment there means no lead-in. The directory in the path
   comment is dropped before the comparison. Quiet cases: a
   `(continued)` part (its lead-in names the file naturally), the
   `GENERIC_NAMES` (`__init__.py`, `conftest.py`), and a block with no
   path comment or a shape block. The keeps are a file the reader
   already has (chapter 11's missing `palindrome.py` before it is
   supplied, Solutions 26's chapter demo before its revised version).
   Commit 7177b735's run over the book had six rewrites and eight
   keeps, so it is a survey rule, printed under `--survey`, never
   baselined.

Deliberately not matched, so a human never reads them as hits: "the
first argument" or "the first parameter" (a position in a call or
signature), "the first version", "the second form", "the first half"
(a variant), "the first line of output", and "the first element" or
"the first item" (data). The noun list leaves those words out. Known
false-positive shapes remain in the report: "the first call" meaning
the first time a function runs, "the second `run()`" at runtime (the
`ordinal+span` pattern cannot tell a runtime order from a position in
the listing), and a clause inside a one-line comprehension.

Report-only: it prints the hits and exits 0, because the heuristic is
literal and no gate runs it. `--fail` exits 1 when a NEW hit is found.
It runs inside `tip prose` and alone as `tip positional`.

Every hit that a human judged a keep lives in
`tools/data/positional_refs_baseline.txt`, so a run prints only what is
new. An entry is `path<TAB>phrase<TAB>sentence`: the matched phrase and
the whole sentence, whitespace normalized, with no line number, so a
reflow leaves the entry alone while an edit to the sentence retires it
and the rewritten sentence reports as NEW. An entry is a judged keep,
not an exemption from the rule. The default run prints each NEW hit,
then each `stale` entry (a baseline entry for a scanned file that
matches no current hit), then a summary (`N new, M accepted[, K
stale]`). `--all` prints every hit, marked NEW or accepted. `--accept`
adds every NEW hit to the baseline and drops the stale entries. A run
given paths compares against those files' entries alone, and `--accept`
with paths adds and drops entries for those files and keeps
every other file's entries.

    uv run python -m tools.positional_refs          # new hits
    uv run python -m tools.positional_refs --all    # every hit
    uv run python -m tools.positional_refs --survey # + call, time, alternative, self-name
    uv run python -m tools.positional_refs --accept # judged keeps
    uv run python -m tools.positional_refs Chapters/30_*.md
    uv run tip positional CH=30
    uv run tip positional-accept
"""

import argparse
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT
from tools.markdown import Block, Document
from tools.prose import (
    BLOCKQUOTE,
    HEADING,
    HTML,
    HTML_COMMENT_CLOSE,
    HTML_COMMENT_OPEN,
    LIST_ITEM,
    TABLE,
)
from tools.repo import add_paths_arg, md_files
from tools.stranded_prepositions import (
    display,
    load_baseline,
)

ORD: Final = (
    r"(?:first|second|third|fourth|fifth|sixth|seventh|last|final"
    r"|next|previous|preceding|following|opening|closing|middle"
    r"|earlier|later|inner|outer|outermost|innermost|top|bottom)")
NOUN: Final = (
    r"(?:line|lines|statement|call|assignment|branch|clause|loop"
    r"|block|case|arm|print|return|yield|comparison|condition|check"
    r"|guard|definition|decorator|handler|expression|append|lookup"
    r"|read|write)")
SPAN: Final = r"`[^`]+`"
KEYWORDS: Final[tuple[str, ...]] = tuple((
    "for while if elif else try except finally with match case "
    "return yield await print assert raise lambda del global "
    "nonlocal"
).split())
CONSTRUCT_NOUN: Final = (
    r"(?:loop|block|statement|branch|clause|call|expression|arm"
    r"|body|line)")

PATTERNS: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("ordinal+noun",
     re.compile(rf"\bthe {ORD} {NOUN}\b", re.IGNORECASE)),
    ("ordinal+span",
     re.compile(rf"\bthe {ORD} {SPAN}", re.IGNORECASE)),
    ("line-number",
     re.compile(r"\b(?:on |at |in )?lines? \d+\b")),
    ("line-rel",
     re.compile(r"\bthe (?:line|lines|statement) (?:above|below"
                r"|before|after|that|where|which|under|over"
                r"|following|preceding)\b", re.IGNORECASE)),
    ("n-lines",
     re.compile(r"\b(?:one|two|three|four|a few|several) "
                r"(?:lines?|statements?) (?:later|earlier|above"
                r"|below|down|up|before|after)\b", re.IGNORECASE)),
)
CONSTRUCT: Final = re.compile(
    rf"\bthe `?({'|'.join(KEYWORDS)})`? {CONSTRUCT_NOUN}\b",
    re.IGNORECASE)

# `count+unit`: a count applied to an execution noun, a unit the
# listing may offer more than one way to count ("the first three
# runs" of a listing with three generators and four tagged calls).
# The noun's number follows the count word, so a quantifier before a
# verb ("both run", "each runs") never matches: each/every and an
# ordinal take the singular, a cardinal or both/all takes the plural.
COUNT_ORD: Final = (
    r"(?:first|second|third|fourth|fifth|sixth|seventh|last|final"
    r"|next|previous|other)")
COUNT_CARD: Final = r"(?:two|three|four|five|six|several|both|all)"
UNIT_SING: Final = (
    r"(?:run|round|attempt|pass|resumption|trace|exchange)")
UNIT_PLUR: Final = (
    r"(?:runs|rounds|attempts|passes|resumptions|traces|exchanges)")
SURVEY_SING: Final = r"(?:call|time)"
SURVEY_PLUR: Final = r"(?:calls|times)"


def count_unit(singular: str, plural: str) -> re.Pattern[str]:
    """The `count+unit` pattern for one pair of unit-noun forms."""
    return re.compile(
        rf"\b(?:(?:each|every|{COUNT_ORD}) {singular}"
        rf"|(?:{COUNT_ORD} )?{COUNT_CARD} {plural})\b",
        re.IGNORECASE)


COUNT_UNIT: Final = count_unit(UNIT_SING, UNIT_PLUR)
# "call" and "time" are too common and too often right ("the first
# call", "each time") for a baseline; they print under --survey only.
SURVEY_UNIT: Final = count_unit(SURVEY_SING, SURVEY_PLUR)
SURVEY_KIND: Final = "survey count+unit"
ALT_KIND: Final = "survey alternative"
SELF_KIND: Final = "survey self-name"
GENERIC_NAMES: Final = frozenset(("__init__.py", "conftest.py"))
ALT_MARKERS: Final = re.compile(
    r"\b(?:if|would|could|might|were|had|unless|instead|otherwise|"
    r"rather|contrast|compared?|comparison|alternative|another|"
    r"other|whereas|unlike|differen\w*|versus|than|but|though|"
    r"although|without|suppose|imagine|elsewhere|ordinary|usual\w*|"
    r"normally|general\w*|typical\w*|most|some|many|not|no|never|"
    r"cannot|version|same|also|too|still)\b", re.I)
ALT_SUBJECT: Final = re.compile(
    r"^An?\s+(?:[\w-]+\s+){0,2}(`[^`]+`)")
ALT_KEYWORDS: Final = frozenset((
    "for", "while", "if", "else", "elif", "try", "except", "finally",
    "with", "return", "yield", "await", "async", "lambda", "class",
    "def", "match", "case", "raise", "del", "global", "nonlocal",
    "pass", "break", "continue", "import", "from", "assert",
))
BASELINE: Final = DATA_DIR / "positional_refs_baseline.txt"
HEADER: Final = (
    "# Prose that points at a listing line by position or by a\n"
    "# repeated construct, which a human read and judged a keep: a\n"
    "# runtime order, a variant, a position in data. An entry is not\n"
    "# an exemption from the rule.\n"
    "# path<TAB>phrase<TAB>sentence, with the sentence's whitespace\n"
    "# normalized and no line number, so a reflow leaves an entry\n"
    "# alone and an edit to the sentence retires it. Rewritten by\n"
    "# `tip positional-accept`; read the delta with `tip positional`\n"
    "# before accepting.\n"
    "# See tools/positional_refs.py.\n"
)

CODE_SPAN = re.compile(r"``[^`]*``|`[^`]*`")
CITATION = re.compile(r"\[([1-9]\d*)\]")
LINK_DEF = re.compile(r"^\s*\[[^\]]+\]:\s")
OUTPUT_MARKER = re.compile(r"^\s*#:")
SENTENCE_END = re.compile(r"[.?!]+(?=\s|$)")


@dataclass(frozen=True)
class Hit:
    """One positional reference: where, what kind, and its sentence."""

    line: int
    kind: str
    phrase: str
    sentence: str


def region_paragraphs(
    doc: Document,
) -> Iterator[tuple[Block, list[tuple[int, str]]]]:
    """(owning block, [(1-based line, text)]) per paragraph.

    Only lines in a listing's prose region are read: after the
    closing fence, up to the next fenced block or heading.
    """
    by_end = {block.end: block for block in doc.blocks}
    fenced = doc.in_fence()
    owner: Block | None = None
    current: list[tuple[int, str]] = []
    in_comment = False
    for index, line in enumerate(doc.lines):
        if index in by_end:
            if owner is not None and current:
                yield owner, current
            current = []
            owner = by_end[index]
            continue
        if fenced[index] or HEADING.match(line):
            if owner is not None and current:
                yield owner, current
            current = []
            owner = None
            in_comment = False
            continue
        if owner is None:
            continue
        text: str | None = line
        if in_comment:
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif HTML_COMMENT_OPEN.match(line):
            in_comment = HTML_COMMENT_CLOSE.search(line) is None
            text = None
        elif not line.strip():
            text = None
        elif (BLOCKQUOTE.match(line) or TABLE.match(line)
              or HTML.match(line) or LINK_DEF.match(line)
              or OUTPUT_MARKER.match(line)):
            text = None
        elif m := LIST_ITEM.match(line):
            if current:
                yield owner, current
                current = []
            text = m.group(4)
        if text is None:
            if current:
                yield owner, current
                current = []
            continue
        current.append((index + 1, text.strip()))
    if owner is not None and current:
        yield owner, current


def joined(paragraph: list[tuple[int, str]]) -> tuple[str, list[int]]:
    """The paragraph as one string, plus the line of every character."""
    chars: list[str] = []
    lines: list[int] = []
    for number, text in paragraph:
        if chars:
            chars.append(" ")
            lines.append(number)
        chars.extend(text)
        lines.extend([number] * len(text))
    return "".join(chars), lines


def sentences(text: str) -> Iterator[tuple[int, str]]:
    """(start offset, sentence) pairs; code spans never split."""
    masked = CODE_SPAN.sub(lambda m: "x" * len(m.group()), text)
    start = 0
    for m in SENTENCE_END.finditer(masked):
        yield start, text[start:m.end()]
        start = m.end()
    if text[start:].strip():
        yield start, text[start:]


def cites_a_tag(sentence: str) -> bool:
    """Does a code span in the sentence hold exactly `[n]`?"""
    return any(
        CITATION.fullmatch(span.group().strip("`"))
        for span in CODE_SPAN.finditer(sentence))


def keyword_counts(block: Block) -> dict[str, int]:
    """How often each keyword occurs in the block's code.

    The part of a line after its first `#` is dropped first.
    """
    counts = dict.fromkeys(KEYWORDS, 0)
    for line in block.lines:
        code = line.split("#", 1)[0]
        for word in KEYWORDS:
            counts[word] += len(
                re.findall(rf"(?<![\w.]){word}\b", code))
    return counts


def sentence_hits(
    sentence: str, counts: dict[str, int],
) -> Iterator[tuple[int, str, str]]:
    """(offset, kind, phrase) for each pattern match in a sentence.

    A `count+unit` match that overlaps another pattern's match ("the
    first call" is already an `ordinal+noun` hit) is dropped, so a
    phrase is reported once.
    """
    spans: list[tuple[int, int]] = []
    for kind, pattern in PATTERNS:
        for m in pattern.finditer(sentence):
            spans.append(m.span())
            yield m.start(), kind, m.group()
    for m in CONSTRUCT.finditer(sentence):
        n = counts.get(m.group(1).lower(), 0)
        if n >= 2:
            spans.append(m.span())
            yield m.start(), f"construct x{n}", m.group()
    for kind, pattern in (("count+unit", COUNT_UNIT),
                          (SURVEY_KIND, SURVEY_UNIT)):
        for m in pattern.finditer(sentence):
            start, end = m.span()
            if any(s < end and start < e for s, e in spans):
                continue
            yield start, kind, m.group()


def identifier(span: str) -> str:
    """The bare name a code span refers to: `a.b()` and `b[0]` give `b`."""
    body = span.strip("`").strip()
    body = body.split("(")[0].split("[")[0].split(".")[-1]
    return body.strip("*@")


def block_code(block: Block) -> str:
    """The block's code with the part after each line's first `#` dropped."""
    return "\n".join(line.split("#", 1)[0] for line in block.lines)


def in_code(name: str, code: str) -> bool:
    """Does `name` occur in `code` as a whole word, not after a dot?"""
    if not re.fullmatch(r"[A-Za-z_]\w*", name):
        return True
    return re.search(rf"(?<![\w.]){re.escape(name)}\b", code) is not None


def names_a_listing_span(sentence: str, code: str) -> bool:
    """Does a code span in the sentence name something the code holds?"""
    return any(
        re.fullmatch(r"[A-Za-z_]\w*", identifier(m.group()))
        and in_code(identifier(m.group()), code)
        for m in CODE_SPAN.finditer(sentence))


def alternative_hit(
    sentence: str, code: str, seen: set[str],
) -> tuple[int, str] | None:
    """(offset, phrase) when the sentence describes an unmarked alternative.

    The caller has already checked that the paragraph is a walkthrough.
    `seen` holds the identifiers earlier sentences of the paragraph
    named in code spans: a construct an earlier sentence introduced,
    marked or not, is not reported again.
    """
    s = sentence.strip()
    lead = len(sentence) - len(sentence.lstrip())
    if ALT_MARKERS.search(CODE_SPAN.sub(" x ", s)):
        return None
    if m := ALT_SUBJECT.match(s):
        name = identifier(m.group(1))
        if name not in seen and not in_code(name, code):
            return lead, m.group(0)
    for m in CODE_SPAN.finditer(s):
        name = identifier(m.group())
        if (name in ALT_KEYWORDS and name not in seen
                and not in_code(name, code)):
            return lead + m.start(), m.group()
    return None


def lead_in(doc: Document, block: Block) -> list[tuple[int, str]]:
    """The paragraph directly above a block's opening fence, if any.

    Walks back over blank lines to the previous non-blank line. A
    heading, fence, table row, block quote, list item, or HTML comment
    there means no lead-in; otherwise the contiguous non-blank lines
    upward form the paragraph, as (1-based line, text) pairs.
    """
    fenced = doc.in_fence()
    index = block.open_at - 1
    while index >= 0 and not doc.lines[index].strip():
        index -= 1
    paragraph: list[tuple[int, str]] = []
    first = True
    while index >= 0:
        line = doc.lines[index]
        if (not line.strip() or fenced[index] or HEADING.match(line)):
            break
        if (BLOCKQUOTE.match(line) or TABLE.match(line)
                or HTML.match(line) or HTML_COMMENT_OPEN.match(line)
                or HTML_COMMENT_CLOSE.search(line)
                or (first and LIST_ITEM.match(line))):
            return [] if first else paragraph
        first = False
        paragraph.insert(0, (index + 1, line.strip()))
        index -= 1
    return paragraph


def self_name_hits(doc: Document) -> Iterator[Hit]:
    """A hit per lead-in that names the listing it introduces."""
    for block in doc.blocks:
        slug = block.slug
        if slug is None or block.continued:
            continue
        name = slug.rsplit("/", 1)[-1]
        if name in GENERIC_NAMES:
            continue
        paragraph = lead_in(doc, block)
        if not paragraph:
            continue
        text, lines = joined(paragraph)
        for start, sentence in sentences(text):
            for m in CODE_SPAN.finditer(sentence):
                if m.group().strip("`").strip() == name:
                    yield Hit(lines[start + m.start()], SELF_KIND,
                              m.group(), " ".join(sentence.split()))


def find(doc: Document) -> Iterator[Hit]:
    """A hit per positional reference in one document."""
    yield from self_name_hits(doc)
    for block, paragraph in region_paragraphs(doc):
        text, lines = joined(paragraph)
        counts = keyword_counts(block)
        code = block_code(block)
        walkthrough = False
        seen: set[str] = set()
        for start, sentence in sentences(text):
            shown = " ".join(sentence.split())
            if walkthrough and (
                    alt := alternative_hit(sentence, code, seen)):
                offset, phrase = alt
                yield Hit(lines[start + offset], ALT_KIND, phrase, shown)
            walkthrough = walkthrough or names_a_listing_span(sentence, code)
            seen.update(identifier(m.group())
                        for m in CODE_SPAN.finditer(sentence))
            if cites_a_tag(sentence):
                continue
            for offset, kind, phrase in sentence_hits(sentence, counts):
                yield Hit(lines[start + offset], kind, phrase, shown)


def key(shown: str, phrase: str, sentence: str) -> str:
    """The baseline line for a hit: path, phrase, sentence."""
    return (f"{shown}\t{' '.join(phrase.split())}"
            f"\t{' '.join(sentence.split())}")


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    path = path or BASELINE
    body = "".join(f"{entry}\n" for entry in sorted(entries))
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW hit is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    ap.add_argument("--survey", action="store_true",
                    help="also print the survey hits (a count on "
                         "`call` or `time`; an unmarked alternative in "
                         "a walkthrough; a lead-in that names its own "
                         "listing), which are never baselined")
    args = ap.parse_args(argv)
    paths = md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])
    shown_paths = {display(p) for p in paths}
    every = sorted(
        ((display(p), h) for p in paths for h in find(Document.parse(p))),
        key=lambda item: (item[0], item[1].line, item[1].phrase),
    )
    survey = [item for item in every
              if item[1].kind.startswith("survey")]
    found = [item for item in every
             if not item[1].kind.startswith("survey")]
    baseline = load_baseline(BASELINE)
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    keys = [key(s, h.phrase, h.sentence) for s, h in found]
    new = [item for item, k in zip(found, keys) if k not in baseline]
    stale = sorted(scope - set(keys))
    if args.accept:
        added = {key(s, h.phrase, h.sentence) for s, h in new}
        write_baseline((baseline - set(stale)) | added)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    for (shown, hit), k in zip(found, keys):
        accepted = k in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {shown}:{hit.line}: [{hit.kind}] "
              f"'{hit.phrase}' :: {hit.sentence}")
    for entry in stale:
        shown, phrase, sentence = entry.split("\t", 2)
        print(f"stale    {shown}: '{phrase}' :: {sentence}")
    if args.survey:
        for shown, hit in survey:
            print(f"survey   {shown}:{hit.line}: [{hit.kind}] "
                  f"'{hit.phrase}' :: {hit.sentence}")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else "")
          + (f", {len(survey)} survey" if args.survey else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
