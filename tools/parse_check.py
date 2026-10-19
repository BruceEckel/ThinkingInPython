#!/usr/bin/env python
"""Shared machinery for the report-only prose checks on the spaCy parse.

Seven checks read the shared cached dependency parse of
`tools/parsed_prose.py`: `tools/subject_gap.py`,
`tools/sentence_shapes.py`, `tools/passive_voice.py`,
`tools/past_tense.py`, and `tools/expletives.py` judge their hits
against a baseline, while `tools/pointer_words.py` and
`tools/negation_density.py` are surveys with none. Each check keeps what
is its own: the rule that turns a paragraph's sentences into hits, the
label set, the printed form of a hit, the built-in calibration
examples, and its docstring, which documents the user-facing command
line. This module holds the rest, so a fix to the baseline file format
or the report layout happens once.

What it holds, by part:

Reading rules. `skipped()` is the test for a Solutions label paragraph
(`Hint:` or `Done when:`). `sentence_text()`, `first_line()`, and
`last_line()` map a sentence back to its normalized text and its
first and last source line. `inside_quotes()` is the odd-quote-count
test for "the token sits inside double quotes", with the start of the
counted span passed in because the checks disagree on it.

Baseline. `key()` builds an entry (`path<TAB>message`, whitespace
normalized, no line number). `load_baseline()` and `write_baseline()`
read and write the file: comments and blank lines dropped on read, the
check's header plus the sorted entries with LF endings on write.
`apply_baseline()` computes the NEW hits and the stale entries, scoping
the stale ones to the files the run read. `print_rows()` prints the
NEW (or, under `--all`, every) hit and the stale entries, and
`print_summary()` the `N new, M accepted[, S stale]` line.

Command line. `build_arg_parser()` makes the parser every check shares
(paths, `--fail`, `--all`, `--accept`, `--survey`, `--calibrate`, each
optional where a check has no use for it, plus a `leading` hook for a
check's own flags such as `--gap`), `parse_args()` parses it and
refuses `--accept` with paths, and `run_calibrate()` wraps a
calibration in the parser-unavailable handler.

Run driver. `run()` is a baselined check's whole default run: read the
files, call the check's finder, catch `ParserUnavailable` (it prints
`name: parser unavailable (...); nothing checked` to stderr and returns
0), sort and deduplicate the findings, split off the survey hits, apply
the baseline, and either `--accept` or print. Survey hits print as
`survey   path:line: message` after the report, never baselined and
counted on a line of their own (`survey_last` picks whether that sits
before or after the summary line, which the two users disagree on).
The check passes its `BASELINE` and `HEADER` constants in on every
call, so a test that monkeypatches the module's `BASELINE` is honored.

Edit pairs. `calibrate_edit_pairs()` is the first half of every
`--calibrate`: it loads `tools/data/edit_pairs.json`, parses each
`before` and `after` text as a one-paragraph document (with the
record's `previous` sentence in front when `previous=True`, and only
the edited text counting), asks the check's rule which labels each text
earns, and prints for each label the pairs in the groups before only,
both, and after only, with ids and texts, then a counts line. The
check supplies `labels_of(paragraphs, skip)`, where `skip` is the
number of leading sentences that belong to `previous`.

Vale. `vale_alerts()` runs `vale --output=JSON Chapters Solutions`, and
`calibrate_vale()` matches one Vale check's alerts to a check's hits by
line and prints CONFIRMED, VALE-ONLY, and PARSE-ONLY. `passive_voice`
and `expletives` use it.

Adding a check. Write a `find(docs, parser=parse)` generator of
`Finding`s whose message starts with `[LABEL]`, a `LABELS` dict, a
`BASELINE` path and a `HEADER` string, and a `main()` of this shape:

    ap = build_arg_parser(__doc__, fail_help="...", survey_help="...",
                          calibrate_help="...")
    args = parse_args(ap, argv)
    if args.calibrate:
        return run_calibrate("name", calibrate, parser)
    return run("name", args, lambda docs: find(docs, parser),
               baseline=BASELINE, header=HEADER)

plus `load_baseline()` and `write_baseline()` wrappers that pass the
module's `BASELINE` and `HEADER`. A rule that fires per sentence can
call `calibrate_edit_pairs()` with a `labels_of` of a few lines. A
survey tool without a baseline uses `build_arg_parser(..., baselined=False)`,
`prose_paths()`, `report_unavailable()`, and `run_calibrate()` and prints
its own report.

The tests in `tools/tests/test_parse_check.py` exercise these pieces
with a stub parser, with no spaCy.
"""

import argparse
import json
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, NamedTuple
from tools.config import DATA_DIR, ROOT
from tools.markdown import Document
from tools.parsed_prose import (
    Paragraph,
    Parser,
    ParserUnavailable,
    Sentence,
    parsed,
)
from tools.repo import add_paths_arg, md_files
from tools.report import Finding
from tools.stranded_prepositions import display

EDIT_PAIRS: Final = DATA_DIR / "edit_pairs.json"
SKIPPED_LABELS: Final = ("Hint:", "Done when:")
"""Openers of the Solutions label paragraphs that the checks skip."""

Entry = tuple[str, int, str]
"""A report row: (display path, line, message)."""
Pairs = dict[str, dict[str, str]]
"""The edit pairs: id to a record with `before`, `after`, `previous`."""
LabelsOf = Callable[[list[Paragraph], int], set[str]]
"""A check's rule for the pairs: (paragraphs, leading sentences to skip)."""


# Reading rules


def skipped(paragraph: Paragraph) -> bool:
    """Is this a Solutions label paragraph (Hint: or Done when:)?"""
    return paragraph.text.startswith(SKIPPED_LABELS)


def sentence_text(paragraph: Paragraph, sentence: Sentence) -> str:
    """The sentence's text from the paragraph, whitespace normalized."""
    return " ".join(paragraph.text[sentence.start:sentence.end].split())


def first_line(paragraph: Paragraph, sentence: Sentence) -> int:
    """The source line holding the sentence's first character."""
    lines = paragraph.lines
    return lines[min(sentence.start, len(lines) - 1)]


def last_line(paragraph: Paragraph, sentence: Sentence) -> int:
    """The source line holding the sentence's last character."""
    lines = paragraph.lines
    return lines[min(max(sentence.end - 1, 0), len(lines) - 1)]


def inside_quotes(text: str, stop: int, start: int = 0) -> bool:
    """Does `text[start:stop]` hold an odd number of `"` characters?

    The checks disagree on `start`: `past_tense` counts from the
    sentence's first character, `expletives` from the paragraph's.
    """
    return text[start:stop].count('"') % 2 == 1


# Baseline


def key(shown: str, text: str) -> str:
    """The baseline line for a hit: path and message, no line number."""
    return f"{shown}\t{' '.join(text.split())}"


def load_baseline(path: Path) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    if not path.exists():
        return set()
    return {
        line for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def write_baseline(entries: set[str], path: Path, header: str) -> None:
    """The header plus the sorted entries, with LF line endings."""
    body = "".join(f"{entry}\n" for entry in sorted(entries))
    path.write_text(header + body, encoding="utf-8", newline="\n")


def apply_baseline(
    found: list[Entry], baseline: set[str], shown_paths: set[str],
) -> tuple[list[Entry], list[str]]:
    """(the NEW rows, the stale entries) for rows from `shown_paths`.

    A stale entry is a baseline entry for one of the files the run read
    that matches no row any more.
    """
    scope = {e for e in baseline if e.split("\t", 1)[0] in shown_paths}
    current = {key(shown, text) for shown, _, text in found}
    new = [(s, n, t) for s, n, t in found if key(s, t) not in baseline]
    return new, sorted(scope - current)


def print_rows(found: list[Entry], baseline: set[str],
               stale: list[str], show_all: bool) -> None:
    """The NEW (or every) row, then the stale entries."""
    for shown, line, text in found:
        accepted = key(shown, text) in baseline
        if accepted and not show_all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {shown}:{line}: {text}")
    for entry in stale:
        shown, text = entry.split("	", 1)
        print(f"stale    {shown}: {text}")


def print_summary(found: list[Entry], new: list[Entry],
                  stale: list[str]) -> None:
    """`N new, M accepted[, S stale]`."""
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))


def print_survey(survey: list[Entry]) -> None:
    """Each survey row, then the `N survey` count."""
    for shown, line, text in survey:
        print(f"survey   {shown}:{line}: {text}")
    print(f"{len(survey)} survey")


# Command line


def build_arg_parser(
    description: str | None, *, fail_help: str,
    baselined: bool = True, survey_help: str | None = None,
    calibrate_help: str | None = None,
    leading: Callable[[argparse.ArgumentParser], None] | None = None,
) -> argparse.ArgumentParser:
    """The parser every check shares.

    Arguments in order: paths, whatever `leading` adds (a check's own
    flags), `--fail`, then for a baselined check `--all` and `--accept`,
    then `--survey` when `survey_help` is given and `--calibrate` when
    `calibrate_help` is.
    """
    ap = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    if leading is not None:
        leading(ap)
    ap.add_argument("--fail", action="store_true", help=fail_help)
    if baselined:
        ap.add_argument("--all", action="store_true",
                        help="print every hit, marked NEW or accepted")
        ap.add_argument("--accept", action="store_true",
                        help="add the NEW hits to the baseline and drop "
                             "stale entries")
    if survey_help is not None:
        ap.add_argument("--survey", action="store_true",
                        help=survey_help)
    if calibrate_help is not None:
        ap.add_argument("--calibrate", action="store_true",
                        help=calibrate_help)
    return ap


def parse_args(ap: argparse.ArgumentParser,
               argv: list[str] | None) -> argparse.Namespace:
    """Parse, refusing `--accept` together with paths."""
    args = ap.parse_args(argv)
    if args.paths and getattr(args, "accept", False):
        ap.error("--accept rewrites the whole baseline; give no paths")
    return args


def report_unavailable(name: str, exc: ParserUnavailable) -> None:
    """Say on stderr that the parser could not start."""
    print(f"{name}: parser unavailable ({exc}); nothing checked",
          file=sys.stderr)


def prose_paths(args: argparse.Namespace) -> list[Path]:
    """The Markdown files named on the command line, else the book."""
    return md_files(args.paths or [ROOT / "Chapters", ROOT / "Solutions"])


def run_calibrate(name: str, calibrate: Callable[[Parser], None],
                  parser: Parser) -> int:
    """Run a calibration; an unavailable parser is reported, exit 0."""
    try:
        calibrate(parser)
    except ParserUnavailable as exc:
        report_unavailable(name, exc)
    return 0


# Run driver


def run(name: str, args: argparse.Namespace,
        find_docs: Callable[[list[Document]], Iterable[Finding]], *,
        baseline: Path, header: str,
        is_survey: Callable[[str], bool] | None = None,
        survey_last: bool = False) -> int:
    """A baselined check's default run; the exit code.

    `find_docs` is the check's finder with its parser (and any extra
    arguments) already bound. `is_survey` says which messages are survey
    hits; those print under `--survey` only, apart from the baseline.
    """
    paths = prose_paths(args)
    shown_paths = {display(p) for p in paths}
    try:
        findings = list(find_docs([Document.parse(p) for p in paths]))
    except ParserUnavailable as exc:
        report_unavailable(name, exc)
        return 0
    everything = sorted(
        {(display(f.path), f.line, f.message) for f in findings})
    survey = [h for h in everything if is_survey and is_survey(h[2])]
    found = [h for h in everything if not (is_survey and is_survey(h[2]))]
    accepted = load_baseline(baseline)
    new, stale = apply_baseline(found, accepted, shown_paths)
    if args.accept:
        added = {key(s, t) for s, _, t in new}
        write_baseline((accepted - set(stale)) | added, baseline, header)
        print(f"Baseline: added {len(added)}, dropped {len(stale)} "
              f"stale, in {display(baseline)}")
        return 0
    survey_on = getattr(args, "survey", False)
    print_rows(found, accepted, stale, args.all)
    if survey_on and not survey_last:
        print_survey(survey)
    print_summary(found, new, stale)
    if survey_on and survey_last:
        print_survey(survey)
    return 1 if args.fail and new else 0


# Edit pairs


def load_edit_pairs(path: Path = EDIT_PAIRS) -> Pairs:
    """The recorded rewrites: id to a record of before, after, previous."""
    return json.loads(path.read_text(encoding="utf-8"))


def pair_documents(pairs: Pairs, previous: bool) -> list[Document]:
    """One-paragraph documents named `calibrate/<id>.<side>.md`.

    With `previous`, each record also gets a `<id>.prev.md` document
    (its `previous` sentence, or "x" when it has none), and the
    `before` and `after` texts start with that sentence.
    """
    docs: list[Document] = []
    for ident, record in pairs.items():
        lead = record.get("previous", "").strip() if previous else ""
        if previous:
            docs.append(Document.from_text(
                lead or "x", Path(f"calibrate/{ident}.prev.md")))
        for side in ("before", "after"):
            text = f"{lead} {record[side]}" if lead else record[side]
            docs.append(Document.from_text(
                text, Path(f"calibrate/{ident}.{side}.md")))
    return docs


def edit_pair_sides(
    pairs: Pairs, parser: Parser, labels_of: LabelsOf, *,
    previous: bool, extra_docs: Sequence[Document] = (),
) -> dict[str, set[str]]:
    """Per document name, the labels its text earns.

    `extra_docs` (calibration examples) are parsed in the same call and
    judged with no sentences skipped. The cache is not used.
    """
    docs = pair_documents(pairs, previous) + list(extra_docs)
    results = parsed(docs, parser, use_cache=False)
    skip: dict[str, int] = {}
    for doc, paras in zip(docs, results, strict=True):
        name = doc.path.name
        if name.endswith(".prev.md"):
            ident = name.removesuffix(".prev.md")
            has_previous = bool(pairs[ident].get("previous", "").strip())
            skip[ident] = (sum(len(p.sentences) for p in paras)
                           if has_previous else 0)
    sides: dict[str, set[str]] = {}
    for doc, paras in zip(docs, results, strict=True):
        name = doc.path.name
        if name.endswith(".prev.md"):
            continue
        ident = name.rsplit(".", 2)[0]
        sides[name] = labels_of(paras, skip.get(ident, 0))
    return sides


def print_edit_pairs(
    pairs: Pairs, sides: Mapping[str, set[str]],
    labels: Mapping[str, str], *, previous: bool, meanings: bool,
    summary: bool,
) -> None:
    """Per label, the pairs in before only, both, and after only.

    `meanings` puts the label's description in the heading, `previous`
    prints each record's `previous` sentence and aligns the three texts,
    and `summary` ends with one line of counts for all labels.
    """
    totals: dict[str, tuple[int, int, int]] = {}
    for label, meaning in labels.items():
        before_only: list[str] = []
        after_only: list[str] = []
        both: list[str] = []
        for ident in pairs:
            b = label in sides[f"{ident}.before.md"]
            a = label in sides[f"{ident}.after.md"]
            if b and a:
                both.append(ident)
            elif b:
                before_only.append(ident)
            elif a:
                after_only.append(ident)
        print(f"== {label}: {meaning} ==" if meanings
              else f"== {label} ==")
        for title, ids in (("before only", before_only),
                           ("both", both), ("after only", after_only)):
            for ident in ids:
                print(f"{title}: {ident}")
                if previous:
                    print(f"  previous: {pairs[ident].get('previous', '')}")
                    print(f"  before:   {pairs[ident]['before']}")
                    print(f"  after:    {pairs[ident]['after']}")
                else:
                    print(f"  before: {pairs[ident]['before']}")
                    print(f"  after:  {pairs[ident]['after']}")
        totals[label] = (len(before_only), len(both), len(after_only))
        print(f"{label}: before-only {len(before_only)}, "
              f"both {len(both)}, after-only {len(after_only)}, "
              f"of {len(pairs)} pairs\n")
    if summary:
        text = "; ".join(f"{label} {b}/{n}/{a}"
                         for label, (b, n, a) in totals.items())
        print(f"Summary (before-only/both/after-only, of {len(pairs)} "
              f"pairs): {text}\n")


def calibrate_edit_pairs(
    parser: Parser, labels: Mapping[str, str], labels_of: LabelsOf, *,
    previous: bool, meanings: bool = True, summary: bool = False,
    extra_docs: Sequence[Document] = (),
) -> dict[str, set[str]]:
    """Load, judge, and print the edit pairs; the sides, for the caller.

    The returned map also holds the labels of `extra_docs`, keyed by
    document name.
    """
    pairs = load_edit_pairs()
    sides = edit_pair_sides(pairs, parser, labels_of, previous=previous,
                            extra_docs=extra_docs)
    print_edit_pairs(pairs, sides, labels, previous=previous,
                     meanings=meanings, summary=summary)
    return sides


# Vale


class Unit(NamedTuple):
    """A sentence or a hit with the source lines it spans."""
    first: int
    last: int
    text: str


def vale_alerts() -> dict[str, list[dict[str, Any]]] | None:
    """Vale's JSON for the book, or None (after saying why)."""
    if shutil.which("vale") is None:
        print("vale: not on PATH; skipping the Vale comparison")
        return None
    done = subprocess.run(
        ["vale", "--output=JSON", "Chapters", "Solutions"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        check=False)
    try:
        data = json.loads(done.stdout)
    except ValueError:
        print(f"vale: no JSON (exit {done.returncode}); skipping the "
              f"Vale comparison")
        return None
    return {str(k).replace("\\", "/"): v for k, v in data.items()}


def calibrate_vale(
    parser: Parser, vale_check: str,
    hits_of: Callable[[Paragraph], Iterator[tuple[Sentence, str]]],
    hits_name: str = "hits",
) -> None:
    """CONFIRMED, VALE-ONLY, and PARSE-ONLY against one Vale check.

    `hits_of` yields (sentence, message) for each hit of the check in a
    paragraph. `hits_name` words the summary line ("[THERE] hits").
    """
    alerts = vale_alerts()
    if alerts is None:
        return
    names = {a["Check"] for found in alerts.values() for a in found}
    kept = {path: [a for a in found if a["Check"] == vale_check]
            for path, found in alerts.items()}
    if not any(kept.values()):
        print(f"vale: no {vale_check} alerts; checks seen: "
              f"{sorted(names)}")
        return
    paths = md_files([ROOT / "Chapters", ROOT / "Solutions"])
    docs = [Document.parse(p) for p in paths]
    mine: dict[str, list[Unit]] = {}
    sentences: dict[str, list[Unit]] = {}
    for doc, paras in zip(docs, parsed(docs, parser), strict=True):
        shown = display(doc.path).replace("\\", "/")
        for paragraph in paras:
            for sentence in paragraph.sentences:
                sentences.setdefault(shown, []).append(Unit(
                    first_line(paragraph, sentence),
                    last_line(paragraph, sentence),
                    sentence_text(paragraph, sentence)))
            for sentence, text in hits_of(paragraph):
                mine.setdefault(shown, []).append(Unit(
                    first_line(paragraph, sentence),
                    last_line(paragraph, sentence), text))
    confirmed: list[str] = []
    vale_only: list[str] = []
    parse_only: list[str] = []
    matched: set[tuple[str, int, int, str]] = set()
    for path, found in kept.items():
        units = mine.get(path, [])
        for alert in found:
            line = alert["Line"]
            hit_units = [u for u in units if u.first <= line <= u.last]
            if hit_units:
                matched.update((path, u.first, u.last, u.text)
                               for u in hit_units)
                confirmed.append(f"{path}:{line}: {alert['Match']!r}: "
                                 f"{hit_units[0].text}")
                continue
            near = [u for u in sentences.get(path, [])
                    if u.first <= line <= u.last]
            text = near[0].text if near else "(sentence not found)"
            vale_only.append(f"{path}:{line}: {alert['Match']!r}: {text}")
    for path, units in mine.items():
        for u in units:
            if (path, u.first, u.last, u.text) not in matched:
                parse_only.append(f"{path}:{u.first}: {u.text}")
    for title, items in (("CONFIRMED", confirmed), ("VALE-ONLY", vale_only),
                         ("PARSE-ONLY", parse_only)):
        print(f"== {title} ({len(items)}) ==")
        for item in items:
            print(item)
        print()
    total = sum(len(u) for u in mine.values())
    print(f"Vale {sum(len(v) for v in kept.values())} alerts, parse "
          f"{total} {hits_name}: {len(confirmed)} confirmed alerts, "
          f"{len(vale_only)} vale-only, {len(parse_only)} parse-only")
