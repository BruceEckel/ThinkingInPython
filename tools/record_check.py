#!/usr/bin/env python
"""Fail if a listing writes a frozen data class the long way, or a record
the wrong way.

From chapter 18's `utils/record.py` on, the book writes a frozen data
class as `@record`, which is `dataclass(frozen=True, slots=True)` under
`dataclass_transform(frozen_default=True)`. Since 2026-09-26 the
decorator has a called form, `@record(slots=False)`, for the class
that must keep an instance `__dict__`: one under a base that declares
no `__slots__` and is not the book's to change (Stateless's `Ability`,
`Time`), or one whose listing reads the instance dict on purpose
(chapter 36's version-skew demos). A base the book owns gets an empty
`__slots__ = ()` instead, so its records stay slotted. Nothing else
stops a new listing from drifting back to `@dataclass(frozen=True)`,
from dropping slots without a reason, or from putting a bare `@record`
on a class whose base takes the slots back. This check reports all
three:

- **long-form**: a class decorated with exactly `@dataclass(frozen=True)`
  whose bases are all known to be slotted. It could be a record.
- **needless flag**: a class decorated `@record(slots=False)` whose
  bases are all known to be slotted. The flag drops slots for nothing,
  unless `record_exceptions.txt` lists the class with its reason.
- **unslotted-base**: a class decorated with a bare `@record` and a base
  that is known to declare no `__slots__`. Every instance gets its
  `__dict__` back. Give the base `__slots__ = ()` when it is the
  book's, or write `@record(slots=False)` when it is a library's.

Any other decorator form (`order=True`, `weakref_slot=True`, an explicit
`slots=True`, `eq=False`) is left alone: `record()` forwards only
`slots`, so those classes have no other way to be written. A
`record(...)` call with any other argument is reported as such.

A base is *known slotted* when it is `Protocol`, `Generic`, `ABC`, or
`object`, or a class defined in the same Markdown file that carries
`__slots__`, is a record, or passes `slots=True`. A base is *known
unslotted* when it is defined in the same file with none of those (a
long-form frozen base included, until it converts), or is one of the
library classes in `UNSLOTTED_LIBRARY`. A base the check cannot see
(imported from another listing's module, say) is unknown, and a class
with an unknown base draws no finding either way. The check is a floor:
it under-reports by design and has no false positives to suppress
beyond the listed exceptions.

The deliberate long-form and `slots=False` listings live in
`tools/data/record_exceptions.txt`, one per line:

    <Chapter_Name> <listing> <Class>    # why

`Chapter_Name` is the chapter file's stem after its `NN_Part--` prefix
(`Rethinking_Objects`), so a renumbering or a part rename leaves the
file alone, and one entry covers the chapter and its Solutions file.
`listing` is the slug (`immutable.py`), and `Class` is a class name or
an `fnmatch` pattern (`*`, `Frozen*`). Run standalone (`tip records`),
the tool also fails on an entry that matches no class, so the file
cannot go stale; under `check_all` each document is checked alone and
that whole-tree test does not run.

Scope: chapter 18 from the `utils/record.py` listing on, every later
chapter, and the Solutions files for chapters 18 and up. A block that
does not parse as Python (a fragment with elided lines) is skipped.

Usage:
    python -m tools.record_check                 # Chapters/ and Solutions/
    python -m tools.record_check Chapters/20_Patterns--Rethinking_Objects.md
"""

import argparse
import ast
from collections.abc import Iterator
from dataclasses import dataclass
from fnmatch import fnmatchcase
from functools import cache
from pathlib import Path
from tools.config import DATA_DIR, ROOT
from tools.markdown import Block, Document
from tools.solution_steps import SHAPE_PREFIX
from tools.repo import add_paths_arg, chapter_stem, is_solutions_file, md_files
from tools.report import Check, Finding, report

EXCEPTIONS_FILE = DATA_DIR / "record_exceptions.txt"
FIRST_CHAPTER = 18
DEFINING_SLUG = "utils/record.py"
LONG_FORM = "dataclass(frozen=True)"
DICT_FORM = "record(slots=False)"
SLOTTED_BUILTINS = frozenset({"Protocol", "Generic", "ABC", "object"})
# Library bases the book's frozen classes inherit that declare no
# __slots__. Stateless's Ability and Time are the ones in use; check
# .venv/Lib/site-packages/stateless/ when a release changes them.
UNSLOTTED_LIBRARY = frozenset({"Ability", "Time", "Exception"})


@dataclass(frozen=True)
class Exemption:
    chapter: str
    listing: str
    cls: str
    line: int

    def covers(self, chapter: str, listing: str, cls: str) -> bool:
        return (self.chapter == chapter and self.listing == listing
                and fnmatchcase(cls, self.cls))


@cache
def exemptions(path: Path = EXCEPTIONS_FILE) -> tuple[Exemption, ...]:
    found: list[Exemption] = []
    if not path.is_file():
        return ()
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = raw.split("#", 1)[0].split()
        if not fields:
            continue
        if len(fields) != 3:
            raise SystemExit(
                f"{path}:{n}: expected '<Chapter_Name> <listing> <Class>', "
                f"got {raw!r}")
        found.append(Exemption(*fields, line=n))
    return tuple(found)


def chapter_name(path: Path) -> str:
    """`Rethinking_Objects` from `20_Patterns--Rethinking_Objects.md`.

    A solutions file (`Solutions/<stem>/README.md`) names its chapter
    the same way, through its directory.
    """
    stem = chapter_stem(path).split("_", 1)[-1]
    return stem.split("--", 1)[-1]


def chapter_number(path: Path) -> int | None:
    head = chapter_stem(path).split("_", 1)[0]
    return int(head) if head.isdigit() else None


@dataclass(frozen=True)
class ClassInfo:
    name: str
    listing: str
    line: int  # 1-based line in the Markdown file
    decorators: tuple[str, ...]
    bases: tuple[str, ...]
    has_slots: bool

    @property
    def is_record(self) -> bool:
        """A bare `@record`, the slotted form."""
        return "record" in self.decorators

    @property
    def is_dict_form(self) -> bool:
        return DICT_FORM in self.decorators

    @property
    def is_long_form(self) -> bool:
        return LONG_FORM in self.decorators

    @property
    def keeps_dict(self) -> bool:
        """Frozen by hand or by flag, slots deliberately absent."""
        return self.is_long_form or self.is_dict_form

    @property
    def odd_record_call(self) -> str | None:
        """A `record(...)` call other than `record(slots=False)`."""
        return next((d for d in self.decorators
                     if d.startswith("record(") and d != DICT_FORM), None)

    @property
    def declares_slots(self) -> bool:
        return self.has_slots or self.is_record or any(
            d.startswith("dataclass(") and "slots=True" in d
            for d in self.decorators)


def _base_name(node: ast.expr) -> str:
    if isinstance(node, ast.Subscript):
        node = node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return "?"


def _classes(block: Block) -> Iterator[ClassInfo]:
    source = "\n".join(line.rstrip("\r\n") for line in block.lines)
    try:
        module = ast.parse(source)
    except SyntaxError:
        return
    listing = block.slug or "-"
    for node in ast.walk(module):
        if not isinstance(node, ast.ClassDef):
            continue
        has_slots = any(
            isinstance(stmt, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "__slots__"
                for t in stmt.targets)
            for stmt in node.body)
        first = min([d.lineno for d in node.decorator_list] + [node.lineno])
        yield ClassInfo(
            name=node.name, listing=listing,
            line=block.line_number(first - 1),
            decorators=tuple(ast.unparse(d) for d in node.decorator_list),
            bases=tuple(_base_name(b) for b in node.bases),
            has_slots=has_slots)


def in_scope_blocks(doc: Document) -> Iterator[Block]:
    """Python blocks the rule applies to, given the file's chapter."""
    number = chapter_number(doc.path)
    if number is None or number < FIRST_CHAPTER:
        return
    started = (number > FIRST_CHAPTER
               or is_solutions_file(doc.path))
    for block in doc.python_blocks():
        if is_shape_block(block):
            # A generated "The shape" block (tools/solution_steps.py)
            # repeats a listing's class declarations under no slug, so
            # the exemptions file could not name it; the listing it was
            # cut from is checked instead.
            continue
        if started:
            yield block
        elif block.slug == DEFINING_SLUG:
            started = True


def is_shape_block(block: Block) -> bool:
    first = next((line for line in block.lines if line.strip()), "")
    return first.startswith(SHAPE_PREFIX)


def _slotted(name: str, here: str, index: dict[str, list[ClassInfo]],
             seen: tuple[str, ...] = ()) -> bool | None:
    """True/False when every definition of `name` agrees; None if unknown."""
    if name in SLOTTED_BUILTINS:
        return True
    if name in UNSLOTTED_LIBRARY:
        return False
    if name in seen or name not in index:
        return None
    candidates = ([c for c in index[name] if c.listing == here]
                  or index[name])
    verdicts: set[bool | None] = set()
    for c in candidates:
        own = c.declares_slots
        above = [_slotted(b, c.listing, index, (*seen, name))
                 for b in c.bases]
        if not own or False in above:
            verdicts.add(False)
        elif None in above:
            verdicts.add(None)
        else:
            verdicts.add(True)
    return verdicts.pop() if len(verdicts) == 1 else None


def survey(doc: Document) -> list[tuple[ClassInfo, list[bool | None]]]:
    """Every in-scope class with the slotted-verdict of each base."""
    classes = [c for b in in_scope_blocks(doc) for c in _classes(b)]
    index: dict[str, list[ClassInfo]] = {}
    for c in classes:
        index.setdefault(c.name, []).append(c)
    return [(c, [_slotted(b, c.listing, index) for b in c.bases])
            for c in classes]


def find(doc: Document) -> Iterator[Finding]:
    chapter = chapter_name(doc.path)
    for c, bases in survey(doc):
        if (odd := c.odd_record_call) is not None:
            yield Finding(
                doc.path, c.line,
                f"{c.listing}: {c.name} is @{odd}; record() takes only "
                "slots=False, so write @record, @record(slots=False), "
                "or @dataclass(...) in full")
        elif c.keeps_dict and all(v is True for v in bases):
            if any(e.covers(chapter, c.listing, c.name)
                   for e in exemptions()):
                continue
            form = ("@dataclass(frozen=True)" if c.is_long_form
                    else "@record(slots=False)")
            yield Finding(
                doc.path, c.line,
                f"{c.listing}: {c.name} is {form} and could be @record "
                "(or list it in tools/data/record_exceptions.txt with "
                "the reason)")
        elif c.is_record and False in bases:
            bad = [b for b, v in zip(c.bases, bases) if v is False]
            yield Finding(
                doc.path, c.line,
                f"{c.listing}: {c.name} is @record but its base "
                f"{', '.join(bad)} declares no __slots__, so instances "
                "keep a __dict__; give the base __slots__ = () if it is "
                "the book's, or write @record(slots=False)")


def unused_exemptions(docs: list[Document]) -> Iterator[Finding]:
    """An exception that matches no dict-keeping class in `docs`."""
    seen = {(chapter_name(d.path), c.listing, c.name)
            for d in docs for c, _ in survey(d) if c.keeps_dict}
    for e in exemptions():
        if not any(e.covers(*key) for key in seen):
            yield Finding(
                EXCEPTIONS_FILE, e.line,
                f"{e.chapter} {e.listing} {e.cls} matches no "
                "@dataclass(frozen=True) or @record(slots=False) class; "
                "remove the entry")


CHECK = Check(
    name="records",
    doc="a frozen data class after chapter 18 is written @record, "
        "slots=False only with a reason, and a bare @record only "
        "under slotted bases",
    run=find,
    clean="Frozen data classes use @record where they can.",
    problem="{n} class(es) on the wrong decorator. CLAUDE.md's @record "
            "section has the rules.",
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_paths_arg(ap)
    args = ap.parse_args(argv)
    whole_book = not args.paths
    paths: list[str | Path] = args.paths or [
        ROOT / "Chapters", ROOT / "Solutions"]
    docs = [Document.parse(p) for p in md_files(paths)]
    findings = [f for d in docs for f in find(d)]
    if whole_book:
        findings += unused_exemptions(docs)
    return report(findings, clean=CHECK.clean, problem=CHECK.problem)


if __name__ == "__main__":
    raise SystemExit(main())
