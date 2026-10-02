#!/usr/bin/env python3
"""Check what the book says about itself against what the book contains.

`heading_links.py` proves a cross-chapter link resolves. `check_claims.py`
narrows which link texts assert something a tool cannot settle. Neither
reads the sentence around the link, and that sentence is where the book
makes claims about its own contents:

    A class declared with `slots=True`
    ([Rethinking Objects](20_Patterns--Rethinking_Objects.md) uses it)
    has no `__dict__` ...

Chapter 20 contains the string "slot" zero times. The link resolved, the
anchor was fine, every gate was green, and the sentence was false. A
2026-09-02 correctness sweep of all 47 chapters found 56 false claims,
and 13 of them were this shape: prose asserting something about another
chapter, about this chapter, or about the book as a whole, which reading
the named place disproves. Nothing greps for prose, so none of the 13 was
detectable by any gate.

This is that grep. Three rules, each taken from a real error's shape and
each decidable by substring search rather than by understanding English.
Two of them gate. The third gates only on a stored model verdict.

`absence`   GATES. A sentence claiming something appears nowhere else,
            where it does. Chapter 08's basic-types table said "(`bytes`
            and `complex` do not appear elsewhere in this book)", and
            `bytes` is in five other chapters. The search is over code
            spans and listings only, never raw prose, because the book's
            type names are also English words: a raw search "disproves"
            the `complex` half with "a more complex design".

`direction` GATES. An ordering phrase that names a chapter or section
            ("an earlier chapter", "the next chapter") within NEAR
            characters of a link that points the other way. Chapter 14
            introduced `@functools.cache` as coming "from earlier
            chapters"; it is chapter 18.

`grounding` REPORTS until a verdict settles it. A sentence links to
            another chapter and the target contains *none* of the code
            terms the sentence names. That is the `slots=True` case
            above, and running it against the pre-fix book finds it. It
            also finds sentences whose terms belong to the *linking*
            chapter, which a target has no reason to mention: all 41 of
            its findings on 2026-09-27. Search cannot tell the two apart,
            so `grounding_triage.py` asks a model which one each sentence
            is and commits the answer to `tools/data/
            grounding_verdicts.json`. A sentence judged to attribute its
            terms to the target becomes SR004, which GATES; one judged to
            credit the target only with an idea drops out; one with no
            verdict yet stays SR002, which reports. The gate reads the
            committed verdicts and never calls the model.

The rules are deliberately literal, so they under-report, and that is the
trade for precision. A claim with no code term in it ("makes illegal
values impossible to construct", pointing at the section that
demonstrates the *problem*) is invisible here and needs a reader. The
2026-09-02 sweep's own numbers: of its 13 self-reference errors, these
rules would have caught two outright and narrowed several more.

Waivers live in `tools/data/self_reference_ok.txt`, one `file:term`,
`file:target.md`, or `file:*` per line, for the places where the literal
rule is wrong and the prose is right. It is empty today.

Usage:
    python -m tools.check_self_reference              # the gating rules
    python -m tools.check_self_reference --advisory   # plus untriaged grounding
    python -m tools.check_self_reference --rule grounding
    python -m tools.check_self_reference Chapters/07_Foundations--Classes.md
    python -m tools.check_self_reference --list       # the rules
"""

import argparse
import re
from collections.abc import Container, Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from tools import judgments
from tools.config import CHAPTERS_DIR, DATA_DIR
from tools.markdown import Document
from tools.repo import add_paths_arg, chapter_stem, md_files
from tools.report import Check, Finding, report

WAIVERS_FILE = DATA_DIR / "self_reference_ok.txt"
VERDICTS_FILE = DATA_DIR / "grounding_verdicts.json"

# A verdict's probability that the sentence attributes its terms to the
# linked chapter. On 2026-09-27 the 41 real findings scored 0.00-0.11
# and five planted misattributions 0.66-0.93, so 0.4 sits in the gap.
MISATTRIBUTED = 0.4

# A link into another chapter file, with an optional anchor. The filename
# class must allow "-", which is what the `--` part-name separator needs;
# a regex that forgot it silently matched nothing for a while (CLAUDE.md
# records that failure under "A regex that matches chapter filenames").
# A chapter file is `NN_...md`; an appendix is `A_...md`.
LINK = re.compile(
    r"\[([^\]]+)\]\(((?:\d{2}|[A-Z])_[\w.-]+\.md)(?:#([\w.-]+))?\)")
CODE_SPAN = re.compile(r"`([^`]+)`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*(?:\{#([^}]+)\})?\s*$")

# "appears nowhere else", "does not appear elsewhere in this book",
# "appears only in this catalog". The claim is always about absence from
# the rest of the book, which is exactly what a corpus search settles.
ABSENCE = re.compile(
    r"\b(?:"
    r"appears?\s+nowhere\s+else"
    r"|(?:does|do)\s+not\s+appear\s+(?:again|elsewhere)"
    r"|appears?\s+only\s+in\s+this"
    r"|nowhere\s+else\s+in\s+(?:this\s+book|the\s+book)"
    r"|(?:is|are)\s+not\s+used\s+(?:again|elsewhere)"
    r")\b",
    re.IGNORECASE,
)

# Phrases that place a *chapter* in reading order. A bare "later" or
# "earlier" is useless here: it almost always modifies something else
# ("every later construction", "a later `import`"), which is what the
# first draft of this rule discovered by reporting seven of those and no
# real ones. The phrase must name a chapter or section, and must sit
# within NEAR characters of the link, so the ordering word is describing
# the link rather than a noun that happens to share the sentence.
BACKWARD = re.compile(
    r"\b(?:an?\s+earlier\s+(?:chapter|section)s?"
    r"|earlier\s+(?:chapter|section)s"
    r"|the\s+(?:previous|preceding)\s+(?:chapter|section)"
    r"|earlier\s+in\s+this\s+book)\b", re.IGNORECASE)
FORWARD = re.compile(
    r"\b(?:an?\s+later\s+(?:chapter|section)s?"
    r"|later\s+(?:chapter|section)s"
    r"|the\s+next\s+chapter"
    r"|later\s+in\s+this\s+book)\b", re.IGNORECASE)
NEAR = 80

# Terms too common to be evidence. A search for "type" or "list" hits
# every chapter, so their absence from a target would never be news and
# their presence proves nothing.
COMMON = frozenset({
    "int", "str", "float", "bool", "list", "dict", "set", "tuple", "type",
    "None", "True", "False", "self", "cls", "object", "print", "len",
    "return", "class", "def", "if", "else", "for", "while", "in", "is",
    "not", "and", "or", "x", "y", "n", "a", "b", "c", "f", "g", "h",
})


def load_waivers(path: Path) -> set[str]:
    """`file:term` lines that suppress one finding each."""
    if not path.exists():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if stripped:
            out.add(stripped)
    return out


def waived(waivers: Container[str], stem: str, term: str) -> bool:
    return f"{stem}:{term}" in waivers or f"{stem}:*" in waivers


def searchable(term: str) -> str | None:
    """The part of a code span worth searching for, or None.

    A span is written for the reader, not for grep: `slots=True` names
    the keyword `slots`, `dict[str, int]` names `dict`, and `f()` names
    `f`. Reduce each to its leading identifier, then drop the ones a
    corpus search cannot learn anything from.
    """
    text = term.strip()
    # `a_package/module4.py` and `path/to/thing.py` search better whole.
    if "/" in text or text.endswith(".py"):
        return text
    m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if m is None:
        return None
    name = m.group(0)
    if name in COMMON or len(name) < 4:
        return None
    return name


@dataclass(frozen=True)
class Chapter:
    """One chapter's text, plus the span of each of its sections."""

    path: Path
    number: int
    text: str
    code: str
    sections: dict[str, str]

    def contains(self, term: str, anchor: str = "") -> bool:
        """Does `term` appear, in the anchored section or anywhere?"""
        scope = self.sections.get(anchor) if anchor else None
        return term in (scope if scope is not None else self.text)

    def uses(self, term: str) -> bool:
        """Does `term` appear *as code*: in a listing or a code span?

        The absence rule needs this rather than a raw text search,
        because the book's type names are also English words. Chapter 08
        said `complex` appears nowhere else, and a raw search "disproved"
        it with "a more complex design" in three other chapters. Only
        code occurrences bear on a claim about a type.
        """
        return term in self.code


def load(path: Path) -> Chapter:
    doc = Document.parse(path)
    fenced = doc.in_fence()
    # (anchor, first content line) for each heading, then slice between.
    marks: list[tuple[str, int, int]] = []
    for index, line in enumerate(doc.lines):
        if fenced[index]:
            continue
        m = HEADING.match(line)
        if m is None:
            continue
        marks.append((m.group(3) or slugify(m.group(2)), len(m.group(1)),
                      index))
    sections: dict[str, str] = {}
    for i, (anchor, level, start) in enumerate(marks):
        stop = len(doc.lines)
        for _, level2, start2 in marks[i + 1:]:
            if level2 <= level:
                stop = start2
                break
        sections[anchor] = "\n".join(doc.lines[start:stop])
    # Code spans must be read from prose lines one at a time, never from
    # the whole document: a ``` fence is three backticks, so scanning the
    # joined text pairs an opening fence with the next stray backtick and
    # hands back whole paragraphs of prose as "code". That is what made
    # the absence rule believe `complex` was code in three chapters that
    # only ever say "a more complex design".
    spans = [
        s
        for index, line in enumerate(doc.lines) if not fenced[index]
        for s in CODE_SPAN.findall(line)
    ]
    code = "\n".join(["\n".join(b.lines) for b in doc.blocks] + spans)
    return Chapter(path, reading_order(path), doc.text, code, sections)


APPENDIX_BASE = 1000


def reading_order(path: Path) -> int:
    """A chapter's number, or for an appendix (`A_...`) a number past
    every chapter's, since the appendices follow the last chapter."""
    head = path.stem.split("_", 1)[0]
    if head.isdigit():
        return int(head)
    return APPENDIX_BASE + ord(head[0]) - ord("A")


def place(chapter: Chapter) -> str:
    """How a finding names a target: "chapter 7" or "appendix A"."""
    head = chapter.path.stem.split("_", 1)[0]
    return f"chapter {int(head)}" if head.isdigit() else f"appendix {head}"


def slugify(text: str) -> str:
    """Pandoc's heading slug, matching check_claims.py's version."""
    out = re.sub(r"`([^`]*)`", r"\1", text.lower())
    out = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", out)
    out = re.sub(r"[^a-z0-9 .\-_]", "", out)
    out = re.sub(r"^[^a-z]+", "", out.strip())
    return out.replace(" ", "-")


def sentences(doc: Document) -> Iterator[tuple[int, str]]:
    """(line of the first line, joined text) for each prose sentence.

    Prose here follows Semantic Line Breaks, so one sentence occupies one
    or more consecutive lines and ends where a line ends in terminal
    punctuation. Joining them is what lets a rule see a link on one line
    and the code term it is about on another, which is how the
    `slots=True` case reads.
    """
    fenced = doc.in_fence()
    start = -1
    buffer: list[str] = []
    for index, line in enumerate(doc.lines):
        stripped = line.strip()
        if fenced[index] or not stripped or stripped.startswith("#"):
            if buffer:
                yield start + 1, " ".join(buffer)
                start, buffer = -1, []
            continue
        # A table row is a sentence of its own, never joined to its
        # neighbors. Joining a whole table put every row's vocabulary in
        # scope at once (chapter 39's catalog produced five bogus
        # findings from one line that way); skipping tables outright lost
        # the one real absence claim in the book, which lives in chapter
        # 08's basic-types row.
        if stripped.startswith("|"):
            if buffer:
                yield start + 1, " ".join(buffer)
                start, buffer = -1, []
            yield index + 1, stripped
            continue
        if not buffer:
            start = index
        buffer.append(line.strip())
        if line.rstrip().endswith((".", ":", "?", "!")):
            yield start + 1, " ".join(buffer)
            start, buffer = -1, []
    if buffer:
        yield start + 1, " ".join(buffer)


def near(pattern: re.Pattern[str], text: str, at: int) -> str | None:
    """The pattern's match within NEAR characters of position `at`.

    Proximity is what makes an ordering phrase evidence about the link
    rather than about whatever else shares the sentence.
    """
    for m in pattern.finditer(text):
        if abs(m.start() - at) <= NEAR:
            return m.group(0)
    return None


@cache
def corpus() -> dict[str, Chapter]:
    return {p.name: load(p) for p in md_files([CHAPTERS_DIR])}


def scan(doc: Document, waivers: frozenset[str]) -> Iterator[Finding]:
    """Every self-reference a literal search disproves."""
    book = corpus()
    own = f"{chapter_stem(doc.path)}.md"
    here = book.get(own)
    stem = chapter_stem(doc.path)
    for line, text in sentences(doc):
        # dict.fromkeys, not set: the report reads better in the order
        # the sentence names things, and a term repeated in one sentence
        # (a table row naming `bytes` in two columns) is one claim.
        terms = list(dict.fromkeys(
            t for t in (searchable(c) for c in CODE_SPAN.findall(text)) if t))

        if ABSENCE.search(text):
            for term in terms:
                if waived(waivers, stem, term):
                    continue
                others = sorted(
                    name for name, chapter in book.items()
                    if name != own and chapter.uses(term))
                if others:
                    shown = ", ".join(c.split("_", 1)[0] for c in others[:4])
                    more = "" if len(others) <= 4 else f" +{len(others) - 4}"
                    yield Finding(
                        doc.path, line, code="SR001",
                        message=(f"claims `{term}` appears nowhere else; "
                                 f"it is in {shown}{more}"))

        for match in LINK.finditer(text):
            label, target_file = match.group(1), match.group(2)
            target = book.get(target_file)
            if target is None or here is None:
                continue
            if waived(waivers, stem, target_file):
                continue

            if target.number != here.number:
                for pattern, forward in ((BACKWARD, False), (FORWARD, True)):
                    hit = near(pattern, text, match.start())
                    if hit is None:
                        continue
                    wrong = ((target.number > here.number) if not forward
                             else (target.number < here.number))
                    if wrong:
                        way = "forward" if not forward else "back"
                        yield Finding(
                            doc.path, line, code="SR003",
                            message=(f'"{hit}" points {way}: [{label}] is '
                                     f"{place(target)}"))

    for site in grounding_sites(doc, waivers):
        listed = ", ".join(f"`{t}`" for t in site.terms[:3])
        extra = len(site.terms) - 3
        more = "" if extra <= 0 else f" (+{extra} more)"
        verdict = grounding_verdicts().get(site.key)
        if verdict is None:
            yield Finding(
                doc.path, site.line, code="SR002",
                message=(f"{site.target} contains none of {listed}{more}; "
                         "no verdict yet, run `tip grounding-triage`"))
        elif verdict["p_terms"] >= MISATTRIBUTED:
            yield Finding(
                doc.path, site.line, code="SR004",
                message=(f"{site.target} contains none of {listed}{more}, "
                         "and this sentence attributes them to it "
                         f"(p={verdict['p_terms']:.2f})"))


@dataclass(frozen=True)
class Site:
    """One sentence and one link where the grounding rule fires."""

    line: int
    sentence: str
    previous: str
    target: str
    anchor: str
    label: str
    terms: list[str]

    @property
    def key(self) -> str:
        return grounding_key(self.target, self.sentence)


def grounding_sites(doc: Document, waivers: frozenset[str]
                    ) -> Iterator[Site]:
    """Each (sentence, linked chapter) whose target shares none of the
    sentence's code terms, once per target even if linked twice.

    Grounding fires only when the target shares NONE of the sentence's
    code vocabulary. Reporting each absent term separately produced 172
    findings, nearly all of them terms belonging to the *linking*
    chapter, which a target has no reason to mention. "Not one of these
    words is over there" is the signal that the sentence named the wrong
    chapter.
    """
    book = corpus()
    if f"{chapter_stem(doc.path)}.md" not in book:
        return
    stem = chapter_stem(doc.path)
    previous = ""
    for line, text in sentences(doc):
        live = [
            t for t in dict.fromkeys(
                t for t in (searchable(c) for c in CODE_SPAN.findall(text))
                if t)
            if not waived(waivers, stem, t)]
        seen: set[str] = set()
        for match in LINK.finditer(text):
            target_file = match.group(2)
            target = book.get(target_file)
            if (target is None or not live or target_file in seen
                    or waived(waivers, stem, target_file)
                    or any(target.contains(t) for t in live)):
                continue
            seen.add(target_file)
            yield Site(line, text, previous, target_file,
                       match.group(3) or "", match.group(1), live)
        previous = text


def grounding_key(target_file: str, sentence: str) -> str:
    """The verdict store's key for one grounding finding."""
    return judgments.key(target_file, sentence)


@cache
def grounding_verdicts() -> dict[str, dict]:
    return judgments.load(VERDICTS_FILE)


@cache
def default_waivers() -> frozenset[str]:
    return frozenset(load_waivers(WAIVERS_FILE))


# What `gate` runs. SR002 stays outside it: a grounding finding with no
# verdict may be either shape, and one check that cries wolf teaches
# everyone to skip it. SR004 is the same finding after a verdict says the
# sentence does attribute its terms to the target. It still catches the
# real thing, chapter 07's `slots=True` attribution to a chapter that
# never mentions slots, and on 2026-09-27 it had nothing else to catch.
GATE_CODES = frozenset({"SR001", "SR003", "SR004"})


def find(doc: Document) -> Iterator[Finding]:
    """The gating subset, which is what check_all.py and `gate` run."""
    return (f for f in scan(doc, default_waivers()) if f.code in GATE_CODES)


CHECK = Check(
    name="self-reference",
    doc="what the book says about its own chapters is in those chapters",
    run=find,
    clean="Self-references check out.",
    problem="{n} self-reference(s) the book's own text disproves. "
            "Fix the prose, or waive in tools/data/self_reference_ok.txt.",
)

RULES = {
    "absence": "SR001",
    "grounding": "SR002",
    "misattribution": "SR004",
    "direction": "SR003",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--rule", choices=sorted(RULES),
                    help="report only this rule")
    ap.add_argument("--advisory", action="store_true",
                    help="include untriaged grounding, which the gate "
                         "leaves out")
    ap.add_argument("--list", action="store_true",
                    help="describe the rules and exit")
    args = ap.parse_args(argv)

    if args.list:
        for name, code in sorted(RULES.items()):
            print(f"{code}  {name}")
        return 0

    wanted = RULES.get(args.rule or "")
    if wanted is not None:
        keep = {wanted}
    elif args.advisory:
        keep = set(RULES.values())
    else:
        keep = set(GATE_CODES)
    findings = [
        f
        for p in md_files(args.paths)
        for f in scan(Document.parse(p), default_waivers())
        if f.code in keep
    ]
    status = report(findings, clean=CHECK.clean, problem=CHECK.problem)
    # Only the gating rules can fail a build. A run that asked for
    # grounding asked for a worklist, and a worklist that exits nonzero
    # cannot sit in tools/tasks.py beside `claims` and `links`.
    return status if keep <= set(GATE_CODES) else 0


if __name__ == "__main__":
    raise SystemExit(main())
