#!/usr/bin/env python3
"""Run every Markdown check in one process, parsing each file once.

Each check still has its own script and its own make target, which is
what you want when one thing is broken and you are iterating on it. But
running them one at a time means N interpreter startups and N parses of
the same 45 chapters, and it means N summaries to read instead of one
answer to "is the book clean?".

This runs them together. Every file is parsed once into a `Document`
(tools_markdown.py) and handed to each selected check, and all findings
land in one list, sorted by file and line, so the report reads top to
bottom through the book rather than grouped by which tool noticed.

The registry is the CHECKS list below: an explicit list of the `Check`
objects the checker modules define, in the spirit of run_all.py's
ALL_TARGETS. Adding a check means importing it and putting it in the
list, and it then appears in --list, in the default run, and as a
selectable name. Deliberately not a discovery mechanism that scans the
directory: an explicit list is greppable, is obvious to a human adding
one by hand, and cannot surprise the interpreter that also exec()s book
listings (see tools_repo.py on the sys.modules collision hazard).

There is no --jobs here on purpose. The whole sweep is well under a
second, nearly all of it interpreter startup, so a process pool would
cost more than it saves. validate_output.py is the tool that needed
parallelism, because it *runs* the book rather than reading it.

Usage:
    python tools/check_all.py                    # every check, Chapters/
    python tools/check_all.py --list             # names and descriptions
    python tools/check_all.py listings banned    # only these
    python tools/check_all.py --fix              # apply what can be fixed
    python tools/check_all.py Solutions/         # a different tree
"""

import argparse
from collections.abc import Iterable

import banned_phrases
import capitalize_comments
import check_anchors
import comment_periods
import comment_spacing
import listing_format
import prose_lint
from tools_markdown import Document
from tools_repo import md_files, write_text_lf
from tools_report import Check, Finding

# The registry. Add a Check here and it joins every mode below.
CHECKS: list[Check] = [
    listing_format.CHECK,
    comment_periods.CHECK,
    comment_spacing.CHECK,
    capitalize_comments.CHECK,
    banned_phrases.CHECK,
    check_anchors.CHECK,
    prose_lint.CHECK,
]


def by_name() -> dict[str, Check]:
    return {check.name: check for check in CHECKS}


def select(names: list[str]) -> list[Check]:
    """The named checks, or all of them when nothing is named."""
    if not names:
        return CHECKS
    known = by_name()
    unknown = [n for n in names if n not in known]
    if unknown:
        raise SystemExit(
            f"unknown check(s): {', '.join(unknown)}\n"
            f"available: {', '.join(known)}"
        )
    return [known[n] for n in names]


def run(checks: Iterable[Check], docs: Iterable[Document]) -> list[Finding]:
    """Every finding from every check, sorted into reading order."""
    findings = [f for doc in docs for check in checks for f in check.run(doc)]
    return sorted(findings, key=lambda f: (str(f.path), f.line, f.col or 0))


def apply_fixes(checks: list[Check], docs: list[Document]) -> int:
    """Rewrite what the fixable checks can fix. Returns files changed.

    Each check is applied to a freshly parsed document, since one check's
    rewrite shifts the line numbers the next one would compute.
    """
    changed = 0
    for doc in docs:
        current = doc
        touched = False
        for check in checks:
            if check.fixer is None:
                continue
            new_text = check.fixer(current)
            if new_text is not None and new_text != current.text:
                current = Document.from_text(new_text, current.path)
                touched = True
        if touched:
            write_text_lf(current.path, current.text)
            changed += 1
    return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", metavar="CHECK",
                    help="checks to run (default: all; see --list)")
    # --paths is an option here, not the bare positional the single-check
    # scripts use: CHECK names already occupy the positional slot, and
    # two nargs="*" positionals cannot be told apart.
    ap.add_argument("--paths", nargs="*", default=None,
                    help="Markdown files or directories (default: Chapters/)")
    ap.add_argument("--list", action="store_true",
                    help="list the checks and exit")
    ap.add_argument("--fix", action="store_true",
                    help="apply every fix the selected checks can make")
    args = ap.parse_args(argv)

    if args.list:
        width = max(len(check.name) for check in CHECKS)
        for check in CHECKS:
            fix = " (fixable)" if check.fixer else ""
            print(f"  {check.name:<{width}}  {check.doc}{fix}")
        return 0

    checks = select(args.names)
    paths = md_files(args.paths)
    docs = [Document.parse(p) for p in paths]

    if args.fix:
        changed = apply_fixes(checks, docs)
        print(f"{changed} file(s) rewritten.")
        return 0

    findings = run(checks, docs)
    for finding in findings:
        print(finding.format())
    if findings:
        print(f"\n{len(findings)} issue(s) in {len(paths)} file(s) "
              f"from {len(checks)} check(s).")
        return 1
    print(f"All {len(checks)} check(s) clean across {len(paths)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
