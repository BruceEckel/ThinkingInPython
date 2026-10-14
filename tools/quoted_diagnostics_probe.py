#!/usr/bin/env python3
"""Re-derive every quoted `ty` diagnostic and compare it with the quote.

`check_quoted_diagnostics.py` compares a quote's gutter lines with the
extracted listing. That catches a moved line, but a `ty` upgrade can
change a message, a rule name, or a caret label while every gutter line
still matches. Until this tool existed, each upgrade sent a report-only
agent through all 42 quotes by hand (about 130k tokens). This tool does
the same sweep: it builds the listing each quote describes, runs
`uv run ty check` on it, and compares what `ty` prints with what the
book shows.

A *quote* is one diagnostic in a fenced block of `Chapters/` or
`Solutions/` that begins `error[...]`, `warning[...]`, or `info[...]`
(a `reveal_type()` answer). A block holding two diagnostics is two
quotes. A quote is named by its Markdown file and its ordinal there,
counting every quote in that file from 1, so prose edits above it do
not rename it.

Many quotes are against a copy of the listing that differs from the
extracted file: a `# type: ignore` the prose says to remove, a `match`
block deleted, a line uncommented, a scratch call appended. The spec
file `tools/data/quoted_diagnostics_probes.txt` records that edit for
every quote, one tab-separated entry each:

    markdown path <TAB> ordinal <TAB> listing <TAB> edit [<TAB> edit]...

`listing` is the extracted file to start from, found the way
`check_quoted_diagnostics.py` finds it (the file's own build folder,
then the chapter's, then `build/examples/utils`). Each edit is one of:

    none                       check the listing as extracted
    strip-ignore               remove every trailing `# type: ignore`
    replace: OLD => NEW        in the one line holding OLD, OLD becomes NEW
    delete: TEXT               delete the one line holding TEXT
    delete-range: A => B       delete from the one line holding A through
                               the next line holding B
    insert-after: A => TEXT    add TEXT as a new line after the one line
                               holding A
    append: TEXT               add TEXT as the last line
    uncomment: TEXT            drop the leading `# ` of the one line
                               holding TEXT

Edits apply in order. They are anchored on text, not on line numbers,
so a listing edit that moves a line leaves the spec intact; an anchor
that matches no line or more than one is an error that marks the quote
STALE. In `TEXT`, `\\n` starts a new line (for `insert-after` and
`append`). Leading spaces in `TEXT` are kept, which is how an inserted
line gets its indentation.

The probe goes to `build/quoted-probe/<chapter>/probe_<stem>.py`
(`build/quoted-probe/solutions/<chapter>/` for a Solutions file), never
into the extracted tree, so `extract_examples --write` cannot delete it
mid-run. Its siblings are copied beside it so an import of another
listing in the same folder resolves; `utils/` resolves through the
`extra-paths` in `pyproject.toml`. A second probe from the same listing
is `probe_<stem>__2.py`. The probe name maps back to the quoted name
in location lines.

Comparison. Both the quote and `ty`'s output are cut into events:

    head   `error[rule]: message` (the message may wrap in the book)
    info   an `info:` line, with its wrapped continuation
    loc    a ` --> file:LINE:COL` line, as `file:LINE:COL`
    src    a gutter line, `LINE | source`
    label  the text of a caret label, with the carets and bars removed

Every event is whitespace-normalized, so the book's line wrapping does
not matter. The quote matches when its events appear in `ty`'s output
for the probe, in order, in one diagnostic. Events the quote leaves out
are not a mismatch (the book omits trailing `info:` lines, and some
quotes show only the headline), but every event the quote shows must be
there with the same text. One leniency: a quote that drops the snippet
may fold the caret label into the headline (Solutions 46's
`reveal_type()` quote does), and that matches when the folded text is
the label.

Output is one line per quote, `MATCH` or `STALE`, then for every STALE
quote the quoted text and the actual output. The exit status is nonzero
when any quote is STALE, unspecified, or named by a spec entry that
matches no quote. This tool is report-only and belongs to no gate; run
it after `tip tools-upgrade` with `tip quoted-diagnostics-probe`.

Usage:
    python -m tools.quoted_diagnostics_probe            # every quote
    python -m tools.quoted_diagnostics_probe --list     # the spec as parsed
    python -m tools.quoted_diagnostics_probe --keep     # keep the probes
    python -m tools.quoted_diagnostics_probe --only Chapters/46_*.md
"""
import argparse
import re
import shutil
import subprocess
import sys
from collections.abc import Iterator, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from tools import check_quoted_diagnostics as cqd
from tools.config import BUILD_DIR, DATA_DIR, ROOT
from tools.markdown import Document
from tools.repo import md_files

SPEC = DATA_DIR / "quoted_diagnostics_probes.txt"
PROBE_ROOT = BUILD_DIR / "quoted-probe"
WORKERS = 6
TY_TIMEOUT = 300

DIAG_HEAD = re.compile(r"^(error|warning|info)\[([\w-]+)\]:\s*(.*)$")
INFO_LINE = re.compile(r"^(info|help|note):\s*(.*)$")
# A bar line: ty's left margin with no line number, carrying carets or labels.
BAR_LINE = re.compile(r"^\s*\|(?:\s(.*))?$")
GUTTER_LINE = re.compile(r"^\s*(\d+)\s\|(?: (.*))?$")
MARKER = re.compile(r"^[\^\-_|]+$")
PROBE_NAME = re.compile(r"^probe_(.+?)(?:__\d+)?\.py$")
EDIT_OPS = ("replace", "delete", "delete-range", "insert-after",
            "append", "uncomment")

type Event = tuple[str, str]


class SpecError(Exception):
    """A spec line or edit that cannot be read or applied."""


@dataclass(frozen=True)
class Quote:
    """One quoted diagnostic: where it sits and the lines it shows."""

    md: Path
    ordinal: int
    line: int
    lines: tuple[str, ...]

    @property
    def key(self) -> str:
        return f"{cqd.entry_path(self.md)}#{self.ordinal}"


@dataclass(frozen=True)
class Entry:
    """One spec line: how to build the probe for one quote."""

    md: str
    ordinal: int
    listing: str
    edits: tuple[str, ...]
    spec_line: int

    @property
    def key(self) -> str:
        return f"{self.md}#{self.ordinal}"


@dataclass
class Probe:
    """A quote, its entry, and the file the probe was written to."""

    quote: Quote
    entry: Entry
    path: Path | None = None
    error: str = ""
    actual: str = ""
    problem: str = ""


@dataclass
class Outcome:
    probe: Probe
    ok: bool
    reason: str = ""
    quoted_events: list[Event] = field(default_factory=list)


def norm(text: str) -> str:
    return " ".join(text.split())


def quotes_in(path: Path) -> list[Quote]:
    """Every quoted diagnostic in a Markdown file, in order."""
    doc = Document.parse(path)
    found: list[Quote] = []
    for block in doc.blocks:
        if block.is_python:
            continue
        starts = [i for i, raw in enumerate(block.lines)
                  if DIAG_HEAD.match(raw.rstrip("\r"))]
        if not starts or not DIAG_HEAD.match(
                next((r for r in block.lines if r.strip()), "")):
            continue
        for n, begin in enumerate(starts):
            stop = starts[n + 1] if n + 1 < len(starts) else len(block.lines)
            lines = tuple(r.rstrip("\r") for r in block.lines[begin:stop])
            found.append(Quote(path, len(found) + 1,
                               block.line_number(begin), lines))
    return found


def load_spec(path: Path = SPEC) -> list[Entry]:
    """The spec file's entries, or a `SpecError` naming the bad line."""
    entries: list[Entry] = []
    seen: set[str] = set()
    for number, raw in enumerate(
            path.read_text(encoding="utf-8").split("\n"), 1):
        if not raw.strip() or raw.startswith("#"):
            continue
        fields = raw.rstrip("\r").split("\t")
        if len(fields) < 4 or not fields[1].isdigit():
            raise SpecError(
                f"{path.name}:{number}: expected markdown path, ordinal, "
                f"listing, and at least one edit")
        entry = Entry(fields[0], int(fields[1]), fields[2],
                      tuple(fields[3:]), number)
        for edit in entry.edits:
            check_edit_syntax(edit, f"{path.name}:{number}")
        if entry.key in seen:
            raise SpecError(f"{path.name}:{number}: {entry.key} appears twice")
        seen.add(entry.key)
        entries.append(entry)
    return entries


def check_edit_syntax(edit: str, where: str) -> None:
    if edit in ("none", "strip-ignore"):
        return
    op, sep, rest = edit.partition(": ")
    if not sep or op not in EDIT_OPS:
        raise SpecError(f"{where}: unknown edit {edit!r}")
    if op in ("replace", "delete-range", "insert-after") and " => " not in rest:
        raise SpecError(f"{where}: {op} needs ' => ' in {edit!r}")


def one_line(lines: list[str], text: str, what: str) -> int:
    """The index of the single line holding `text`, else a `SpecError`."""
    hits = [i for i, line in enumerate(lines) if text in line]
    if len(hits) != 1:
        raise SpecError(
            f"{what}: {text!r} matches {len(hits)} lines, expected 1")
    return hits[0]


def expand(text: str) -> list[str]:
    return text.replace("\\n", "\n").split("\n")


def apply_edit(lines: list[str], edit: str) -> list[str]:
    """One edit applied to a listing's lines, as a new list."""
    if edit == "none":
        return lines
    if edit == "strip-ignore":
        return [cqd.TYPE_IGNORE.sub("", line) for line in lines]
    op, _, rest = edit.partition(": ")
    out = list(lines)
    if op == "replace":
        old, _, new = rest.partition(" => ")
        i = one_line(out, old, edit)
        out[i:i + 1] = expand(out[i].replace(old, new, 1))
    elif op == "delete":
        del out[one_line(out, rest, edit)]
    elif op == "delete-range":
        first, _, last = rest.partition(" => ")
        i = one_line(out, first, edit)
        j = next((k for k in range(i, len(out)) if last in out[k]), None)
        if j is None:
            raise SpecError(f"{edit}: {last!r} not found after {first!r}")
        del out[i:j + 1]
    elif op == "insert-after":
        anchor, _, text = rest.partition(" => ")
        i = one_line(out, anchor, edit)
        out[i + 1:i + 1] = expand(text)
    elif op == "append":
        while out and not out[-1].strip():
            out.pop()
        out.extend(expand(rest))
        out.append("")
    elif op == "uncomment":
        i = one_line(out, rest, edit)
        out[i] = re.sub(r"^(\s*)# ?", r"\1", out[i], count=1)
    return out


def ensure_trees() -> None:
    """Extract the build trees when either is missing."""
    if not (BUILD_DIR / "examples").is_dir():
        subprocess.run([sys.executable, "-m", "tools.extract_examples",
                        "--write"], cwd=ROOT, check=True)
    if not (BUILD_DIR / "solutions").is_dir():
        subprocess.run([sys.executable, "-m", "tools.extract_solutions",
                        "--write"], cwd=ROOT, check=True)


def probe_dir(source_dir: Path) -> Path:
    """Where the probes for a listing folder live, outside the build trees."""
    rel = source_dir.relative_to(BUILD_DIR)
    parts = rel.parts
    return PROBE_ROOT.joinpath(*(parts[1:] if parts[0] == "examples"
                                 else parts))


def write_probe(probe: Probe, taken: dict[Path, int]) -> None:
    """Build the probe file for one quote, or record why it cannot be."""
    entry, quote = probe.entry, probe.quote
    try:
        found = cqd.locate(entry.listing, cqd.listing_dirs(quote.md))
        if found is None:
            raise SpecError(f"listing {entry.listing} not found")
        lines = found.read_text(encoding="utf-8").split("\n")
        for edit in entry.edits:
            lines = apply_edit(lines, edit)
        dest = probe_dir(found.parent)
        if not dest.exists():
            shutil.copytree(found.parent, dest,
                            ignore=shutil.ignore_patterns("__pycache__"))
        stem = Path(entry.listing).stem
        key = dest / f"probe_{stem}.py"
        taken[key] = taken.get(key, 0) + 1
        name = (f"probe_{stem}.py" if taken[key] == 1
                else f"probe_{stem}__{taken[key]}.py")
        probe.path = dest / name
        probe.path.write_text("\n".join(lines), encoding="utf-8",
                              newline="\n")
    except SpecError as err:
        probe.error = str(err)


def run_ty(probe: Probe) -> None:
    """Run `uv run ty check` on one probe and keep what it printed."""
    assert probe.path is not None
    uv = shutil.which("uv") or "uv"
    rel = probe.path.relative_to(ROOT).as_posix()
    done = subprocess.run(
        [uv, "run", "ty", "check", "--color", "never", rel],
        cwd=ROOT, capture_output=True, timeout=TY_TIMEOUT,
        encoding="utf-8", errors="replace",
    )
    probe.actual = done.stdout.replace("\r", "")
    if done.returncode not in (0, 1):
        probe.problem = (f"ty exited {done.returncode}: "
                         f"{done.stderr.strip()[:400]}")


def short_name(path: str) -> str:
    """A location's file as the quote names it: no folder, no probe_ prefix."""
    base = path.replace("\\", "/").rsplit("/", 1)[-1]
    m = PROBE_NAME.match(base)
    return f"{m.group(1)}.py" if m else base


def events(lines: Sequence[str]) -> list[Event]:
    """Cut one diagnostic's lines into normalized events."""
    out: list[Event] = []
    current: int | None = None  # index of the head/info being continued
    for raw in lines:
        line = raw.rstrip()
        head = DIAG_HEAD.match(line)
        if head:
            out.append(("head", norm(
                f"{head.group(1)}[{head.group(2)}]: {head.group(3)}")))
            current = len(out) - 1
            continue
        info = INFO_LINE.match(line)
        if info:
            text = norm(f"{info.group(1)}: {info.group(2)}")
            if (text.startswith(f"{info.group(1)}: ->") and out
                    and out[-1][0] == "info"):
                out[-1] = ("info", f"{out[-1][1]} {text.split(': ', 1)[1]}")
            else:
                out.append(("info", text))
            current = len(out) - 1
            continue
        loc = cqd.LOCATION.match(line)
        if loc:
            out.append(("loc",
                        f"{short_name(loc.group(1))}:{loc.group(2)}:"
                        f"{loc.group(3)}"))
            current = None
            continue
        gut = GUTTER_LINE.match(line)
        if gut:
            source = re.sub(r"^\|\s?", "", gut.group(2) or "")
            out.append(("src", f"{gut.group(1)} | {norm(source)}"))
            current = None
            continue
        bar = BAR_LINE.match(line)
        if bar:
            words = (bar.group(1) or "").split()
            while words and MARKER.match(words[0]):
                words.pop(0)
            if words:
                text = " ".join(words)
                if out and out[-1][0] == "label":
                    out[-1] = ("label", f"{out[-1][1]} {text}")
                else:
                    out.append(("label", text))
            current = None
            continue
        if not line.strip():
            current = None
        elif current is not None:
            kind, text = out[current]
            out[current] = (kind, norm(f"{text} {line}"))
    return out


def split_actual(text: str) -> list[list[str]]:
    """`ty`'s output as one list of lines per diagnostic."""
    diagnostics: list[list[str]] = []
    for line in text.split("\n"):
        if DIAG_HEAD.match(line):
            diagnostics.append([line])
        elif line.startswith("Found ") or line.startswith("All checks"):
            break
        elif diagnostics:
            diagnostics[-1].append(line)
    return diagnostics


def folded(actual: list[Event], at: int, quoted: str) -> bool:
    """Whether a quoted headline is `actual[at]` plus the next label."""
    text = actual[at][1]
    if not quoted.startswith(text + " "):
        return False
    rest = quoted[len(text) + 1:]
    for kind, label in actual[at + 1:]:
        if kind == "label":
            return label == rest
        if kind not in ("loc", "src"):
            return False
    return False


def match_events(quoted: list[Event], actual: list[Event]) -> str:
    """Empty when the quote's events appear in order in `actual`."""
    pos = 0
    for kind, text in quoted:
        while pos < len(actual):
            a_kind, a_text = actual[pos]
            pos += 1
            if a_kind != kind:
                continue
            if a_text == text or (
                    kind in ("head", "info")
                    and folded(actual, pos - 1, text)):
                break
        else:
            return f"{kind} not found in order: {text}"
    return ""


def judge(probe: Probe) -> Outcome:
    """Compare a probe's quote with what `ty` printed for it."""
    quoted = events(probe.quote.lines)
    if probe.error:
        return Outcome(probe, False, f"probe not built: {probe.error}", quoted)
    if probe.problem:
        return Outcome(probe, False, probe.problem, quoted)
    diagnostics = split_actual(probe.actual)
    if not diagnostics:
        return Outcome(probe, False, "ty printed no diagnostics", quoted)
    reasons = []
    for lines in diagnostics:
        why = match_events(quoted, events(lines))
        if not why:
            return Outcome(probe, True, "", quoted)
        reasons.append(why)
    first = next((r for r in reasons if not r.startswith("head")), reasons[0])
    return Outcome(probe, False, first, quoted)


def select_quotes(paths: list[Path]) -> Iterator[Quote]:
    for path in paths:
        yield from quotes_in(path)


def show_stale(outcome: Outcome) -> None:
    probe = outcome.probe
    print(f"  reason: {outcome.reason}")
    print("  quoted:")
    for line in probe.quote.lines:
        print(f"    {line}")
    print("  actual:")
    text = probe.actual.rstrip() or probe.error or "(nothing)"
    for line in text.split("\n"):
        print(f"    {line}")
    print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true",
                    help="print the spec as parsed and exit")
    ap.add_argument("--keep", action="store_true",
                    help="leave the probe files under build/quoted-probe/")
    ap.add_argument("--only", metavar="PATH",
                    help="check the quotes of one Markdown file")
    args = ap.parse_args(argv)

    try:
        spec = load_spec()
    except SpecError as err:
        print(f"spec error: {err}")
        return 2
    if args.list:
        for e in spec:
            print(f"{e.key}\t{e.listing}\t" + "\t".join(e.edits))
        print(f"{len(spec)} entries in {SPEC.relative_to(ROOT)}")
        return 0

    paths = md_files([ROOT / "Chapters", ROOT / "Solutions"])
    if args.only:
        want = Path(args.only).resolve()
        paths = [p for p in paths if p.resolve() == want]
        if not paths:
            print(f"--only: no Markdown file {args.only}")
            return 2
    ensure_trees()
    quotes = list(select_quotes(paths))
    by_key = {e.key: e for e in spec}
    in_scope = {cqd.entry_path(p) for p in paths}
    failed = 0

    probes: list[Probe] = []
    for quote in quotes:
        entry = by_key.get(quote.key)
        if entry is None:
            print(f"UNSPECIFIED  {quote.key}  (line {quote.line}): "
                  f"add an entry to {SPEC.relative_to(ROOT)}")
            failed += 1
            continue
        probes.append(Probe(quote, entry))
    known = {q.key for q in quotes}
    for entry in spec:
        if entry.key not in known and entry.md in in_scope:
            print(f"NO QUOTE     {entry.key}  (spec line {entry.spec_line}): "
                  f"the file has no quote with that ordinal")
            failed += 1

    if PROBE_ROOT.exists():
        for child in PROBE_ROOT.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
    taken: dict[Path, int] = {}
    for probe in probes:
        write_probe(probe, taken)
    runnable = [p for p in probes if p.path is not None]
    try:
        with ThreadPoolExecutor(WORKERS) as pool:
            list(pool.map(run_ty, runnable))
        stale: list[Outcome] = []
        for probe in probes:
            outcome = judge(probe)
            label = "MATCH" if outcome.ok else "STALE"
            print(f"{label:<6} {probe.quote.key}  line {probe.quote.line}")
            if not outcome.ok:
                stale.append(outcome)
        print()
        for outcome in stale:
            print(f"STALE {outcome.probe.quote.key} "
                  f"(line {outcome.probe.quote.line}, "
                  f"probe of {outcome.probe.entry.listing})")
            show_stale(outcome)
        failed += len(stale)
        total = len(probes)
        print(f"quoted diagnostics probe: {total - len(stale)} of {total} "
              f"MATCH, {len(stale)} STALE")
    finally:
        if not args.keep and PROBE_ROOT.exists():
            for child in PROBE_ROOT.iterdir():
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
