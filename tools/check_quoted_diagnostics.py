#!/usr/bin/env python3
"""Check quoted `ty` diagnostics against the listings they point at.

The book quotes `ty` output in fenced blocks (```text, or a bare fence)
that begin `error[...]` or `warning[...]`. Each quote carries a
location line, ` --> file.py:LINE:COL`, and gutter lines, `LINE | source`,
that reproduce the listing's source. Nothing gates those: a `#:`
marker is validated against a run, but a quoted diagnostic is prose,
so a listing edit that shifts a line, or a `ty` upgrade that changes
the message, leaves the quote stale with every gate green. The
2026-09-14 claims sweep found such quotes in chapters 08, 13, 20, and
46 and in several Solutions files.

This check reads every quoted block, follows each ` --> file:LINE`
line, and compares every gutter line that follows it with that line
of the extracted listing (`build/examples/<chapter>/` for Chapters/,
`build/solutions/<chapter>/` for Solutions/). A gutter line matches
when it equals the file's line, or equals it with a trailing
`# type: ignore` comment removed (the prose usually says the comment
was stripped to produce the diagnostic), or equals the file's line
with its leading `# ` removed (the book's convention is a
commented-out probe line). Anything else is reported, and so is a
location naming a file the tree does not hold, which usually means a
scratch name the prose explains.

Some quotes are deliberately against an edited copy of the listing
(a `match` block removed, a line uncommented), and the shifted line
numbers are right for that copy, so a plain list of hits would be the
same dozen lines on every run. The accepted ones therefore live in
`tools/data/quoted_diagnostics_baseline.txt`, in the style of
`pyright_review.py`, and the default run prints only the delta:

    NEW   a hit the baseline lacks: a listing edit moved a quoted
          line, or a new quote does not match its listing.
    GONE  a baseline entry that no longer fires: the quote or the
          listing changed.

An entry is `markdown path<TAB>message`, with the Markdown line number
dropped so prose edits above a quote do not churn the baseline. Exit
status is nonzero only when NEW is non-empty, which is what lets the
gate run it: a fresh hit is either a stale quote to fix or a new
deliberate edit to accept. `--accept` rewrites the baseline from the
current run; `--all` lists every hit, baseline or not. A run given
paths compares against those files' baseline entries alone, since an
entry for a file the run never read cannot fire.

A second rule, `--pragmas`, reports and never gates. A gutter line
that matches only with the listing's `# type: ignore` removed is a
quote the printed listing cannot produce: `ty` reports nothing until
the reader strips the comment. The 2026-09-16 sweep of the prose around
every Solutions quote found three solutions that said "`ty` rejects the
call" under such a listing and never mentioned the comment. The rule
reads the prose on both sides of the quote, up to `PRAGMA_WINDOW`
non-blank lines each way and stopping at a heading, and reports the
quote when the word "ignore" appears nowhere in it. Both sides count
because the book sometimes explains the comment after the quote
("The `# type: ignore` silences that diagnostic"). It has no baseline;
do not add it to the gate without first getting its count to zero.

Usage:
    python -m tools.check_quoted_diagnostics            # the delta
    python -m tools.check_quoted_diagnostics --all      # every hit
    python -m tools.check_quoted_diagnostics --accept   # rewrite the baseline
    python -m tools.check_quoted_diagnostics --pragmas  # unmentioned ignores
    python -m tools.check_quoted_diagnostics Chapters/46_*.md --all
"""
import argparse
import re
import sys
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

from tools.config import BUILD_DIR, DATA_DIR, ROOT
from tools.markdown import Block, Document
from tools.report import Finding, report

BASELINE = DATA_DIR / "quoted_diagnostics_baseline.txt"
HEADER = (
    "# Quoted ty diagnostics the book deliberately makes against an\n"
    "# edited copy of a listing, so their gutter lines differ from the\n"
    "# extracted file. markdown path<TAB>message, one per hit, sorted.\n"
    "# Rewritten by `make quoted-diagnostics-accept`; read the delta\n"
    "# with `make quoted-diagnostics` before accepting.\n"
    "# See tools/check_quoted_diagnostics.py.\n"
)

DIAGNOSTIC_START = re.compile(r"^(error|warning)\[[\w-]+\]")
LOCATION = re.compile(r"^\s*-->\s*(\S+?):(\d+):(\d+)\s*$")
GUTTER = re.compile(r"^\s*(\d+)\s\|(?: (.*))?$")
TYPE_IGNORE = re.compile(r"\s*#\s*type:\s*ignore(\[[\w,-]+\])?\s*$")
# The bar ty prints at the left of a multi-line span's continuation lines.
SPAN_BAR = re.compile(r"^\s*\|\s")
# How the prose names the comment a quote was made without.
PRAGMA_MENTION = re.compile(r"\bignore\b", re.IGNORECASE)
# Non-blank prose lines read on each side of a quote for that mention.
PRAGMA_WINDOW = 10
HEADING = re.compile(r"^#{1,6}\s")

TREES = {"Chapters": BUILD_DIR / "examples", "Solutions": BUILD_DIR / "solutions"}


def quoted_blocks(doc: Document) -> Iterator[Block]:
    """Fenced blocks whose first content line is a `ty` diagnostic."""
    for block in doc.blocks:
        first = next((line for line in block.lines if line.strip()), "")
        if DIAGNOSTIC_START.match(first):
            yield block


def listing_dirs(md: Path) -> list[Path]:
    """Where a quoted file may live, for a chapter or solutions file.

    A solutions file often quotes a diagnostic against the chapter's own
    listing, so its chapter directory under build/examples is searched
    after its own, and the shared helpers in build/examples/utils last.
    """
    tree = TREES.get(md.parent.name)
    if tree is None:
        return []
    dirs = [tree / md.stem]
    if tree is not TREES["Chapters"]:
        dirs.append(TREES["Chapters"] / md.stem)
    dirs.append(TREES["Chapters"] / "utils")
    return dirs


def locate(name: str, dirs: list[Path]) -> Path | None:
    for d in dirs:
        candidate = d / name
        if candidate.exists():
            return candidate
    return None


def gutter_matches(quoted: str, actual: str) -> bool:
    """Whether a quoted gutter line reproduces the listing's line.

    Both sides are compared stripped, since ty indents the source of a
    multi-line span and prefixes its continuation lines with a `|` bar.
    """
    quoted = SPAN_BAR.sub("", quoted).strip()
    actual = actual.strip()
    if quoted == actual:
        return True
    if TYPE_IGNORE.sub("", actual) == quoted:
        return True
    if actual.startswith("# ") and actual[2:] == quoted:
        return True
    return False


def find(doc: Document) -> Iterator[Finding]:
    """Every gutter line in a quoted diagnostic that disagrees with its file."""
    dirs = listing_dirs(doc.path)
    if not dirs:
        return
    for block in quoted_blocks(doc):
        name = ""
        lines: list[str] | None = None
        for index, raw in enumerate(block.lines):
            line = raw.rstrip("\n\r")
            loc = LOCATION.match(line)
            if loc:
                name = loc.group(1).replace("\\", "/")
                found = locate(name, dirs)
                if found is None:
                    lines = None
                    where = dirs[0]
                    if where.is_relative_to(ROOT):
                        where = where.relative_to(ROOT)
                    yield Finding(
                        doc.path, block.line_number(index),
                        f"quoted location names {name}, which "
                        f"{where} does not hold",
                    )
                else:
                    lines = found.read_text(encoding="utf-8").split("\n")
                continue
            gut = GUTTER.match(line)
            if not gut or lines is None:
                continue
            n = int(gut.group(1))
            quoted = gut.group(2) or ""
            if not (0 < n <= len(lines)):
                yield Finding(
                    doc.path, block.line_number(index),
                    f"{name} has no line {n} (quoted: {quoted!r})",
                )
                continue
            actual = lines[n - 1].rstrip("\r")
            if not gutter_matches(quoted, actual):
                yield Finding(
                    doc.path, block.line_number(index),
                    f"{name}:{n} reads {actual.strip()!r}, "
                    f"quote shows {quoted.strip()!r}",
                )


def stripped_pragma(quoted: str, actual: str) -> bool:
    """Whether the quote matches only with the listing's pragma removed."""
    quoted = SPAN_BAR.sub("", quoted).strip()
    actual = actual.strip()
    return quoted != actual and TYPE_IGNORE.sub("", actual) == quoted


def nearby_prose(doc: Document, block: Block) -> list[str]:
    """The prose around a block: `PRAGMA_WINDOW` non-blank lines each way.

    Fenced lines are skipped, not counted, so the listing a quote sits
    under does not use up the window. A heading ends the walk, since it
    starts another exercise or section.
    """
    fenced = doc.in_fence()
    found: list[str] = []
    for indexes in (range(block.open_at - 1, -1, -1),
                    range(doc.end_of(block), len(doc.lines))):
        taken = 0
        for k in indexes:
            if fenced[k] or not doc.lines[k].strip():
                continue
            if HEADING.match(doc.lines[k]) or taken == PRAGMA_WINDOW:
                break
            found.append(doc.lines[k])
            taken += 1
    return found


def find_unmentioned_pragmas(doc: Document) -> Iterator[Finding]:
    """Quotes the printed listing cannot produce, with no word of why."""
    dirs = listing_dirs(doc.path)
    for block in quoted_blocks(doc):
        name = ""
        lines: list[str] | None = None
        for index, raw in enumerate(block.lines):
            line = raw.rstrip("\n\r")
            loc = LOCATION.match(line)
            if loc:
                name = loc.group(1).replace("\\", "/")
                found = locate(name, dirs)
                lines = (found.read_text(encoding="utf-8").split("\n")
                         if found else None)
                continue
            gut = GUTTER.match(line)
            if not gut or lines is None:
                continue
            n = int(gut.group(1))
            if not (0 < n <= len(lines)):
                continue
            if not stripped_pragma(gut.group(2) or "", lines[n - 1]):
                continue
            if any(PRAGMA_MENTION.search(p) for p in nearby_prose(doc, block)):
                continue
            yield Finding(
                doc.path, block.line_number(index),
                f"{name}:{n} carries a `# type: ignore` the quote drops, "
                f"and the prose around the quote does not mention it",
            )


def entry_path(path: Path) -> str:
    """A Markdown file as the baseline names it: repo-relative, posix."""
    path = path.resolve()
    if path.is_relative_to(ROOT):
        path = path.relative_to(ROOT)
    return path.as_posix()


def entry(finding: Finding) -> str:
    """The baseline line for a finding: path and message, no line number."""
    return f"{entry_path(finding.path)}\t{finding.message}"


def scoped(baseline: Counter[str], paths: list[Path]) -> Counter[str]:
    """The baseline entries that belong to `paths`.

    A run over one chapter (`verify-ch`) reads none of the other files,
    so their entries cannot fire, and comparing against them would
    report every one as GONE.
    """
    names = {entry_path(p) for p in paths}
    return Counter({line: count for line, count in baseline.items()
                    if line.split("\t", 1)[0] in names})


def load_baseline(path: Path = BASELINE) -> Counter[str]:
    if not path.exists():
        return Counter()
    text = path.read_text(encoding="utf-8")
    return Counter(
        line for line in text.splitlines()
        if line and not line.startswith("#")
    )


def write_baseline(entries: Counter[str], path: Path = BASELINE) -> None:
    body = "".join(f"{line}\n" for line in sorted(entries.elements()))
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")


def delta(findings: list[Finding], before: Counter[str],
          ) -> tuple[Counter[str], Counter[str], Counter[str]]:
    """(now, new, gone) for the current findings against a baseline."""
    now = Counter(entry(f) for f in findings)
    return now, now - before, before - now


def show(label: str, entries: Counter[str]) -> None:
    for line in sorted(entries.elements()):
        path, message = line.split("\t", 1)
        print(f"{label}  {path}  {message}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files to check (default: Chapters/ and "
                         "Solutions/)")
    ap.add_argument("--all", action="store_true",
                    help="list every hit, ignoring the baseline")
    ap.add_argument("--accept", action="store_true",
                    help="rewrite the baseline from the current run")
    ap.add_argument("--pragmas", action="store_true",
                    help="list quotes made without the listing's "
                         "`# type: ignore` that the prose never mentions "
                         "(report-only, no baseline)")
    args = ap.parse_args(argv)
    paths = [Path(p) for p in args.paths] or sorted(
        list((ROOT / "Chapters").glob("*.md"))
        + list((ROOT / "Solutions").glob("*.md")))
    if args.pragmas:
        return report(
            [f for p in paths
             for f in find_unmentioned_pragmas(Document.parse(p))],
            clean="Every quote made without a `# type: ignore` says so.",
            problem="{n} quoted diagnostic(s) need the listing's "
                    "`# type: ignore` removed, and the prose does not "
                    "say so. On the listing as printed, ty reports "
                    "nothing.",
        )
    findings = [f for p in paths for f in find(Document.parse(p))]
    if args.all:
        return report(
            findings,
            clean="Quoted diagnostics match their listings.",
            problem="{n} quoted diagnostic line(s) disagree with the "
                    "extracted listing. Read each against its prose: a "
                    "quote against an edited copy is expected, a stale "
                    "line number is not.",
        )
    if args.paths and args.accept:
        ap.error("--accept rewrites the whole baseline; give no paths")
    baseline = scoped(load_baseline(), paths)
    now, new, gone = delta(findings, baseline)
    if args.accept:
        write_baseline(now)
        print(f"Baseline written: {sum(now.values())} entries in {BASELINE}")
        return 0
    show("NEW ", new)
    show("GONE", gone)
    print(
        f"quoted diagnostics: {sum(now.values())} hit(s), "
        f"{sum(new.values())} new, {sum(gone.values())} gone, "
        f"baseline {sum(baseline.values())}"
    )
    if new:
        print("Read each NEW line against its prose: fix a stale quote, "
              "or `make quoted-diagnostics-accept` a deliberate edit.")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
