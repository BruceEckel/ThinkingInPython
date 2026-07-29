#!/usr/bin/env python3
"""One vocabulary for what a check found, and one way to print it.

Most tools/*.py checkers do the same three things: walk the book's
Markdown, notice problems at particular lines, and end with a count plus
an exit code. Each one used to invent its own shape for "a problem" (a
bare list of line numbers, a (lineno, reason) pair, a (lineno, col, code,
message) tuple) and its own summary printing. That made every checker's
`main()` a near-copy of every other checker's, and it left no type a
future multi-check runner could collect results into.

`Finding` is that type. A check produces `Finding`s and prints nothing;
`report()` prints them and decides the exit code. Splitting the two means
a check is a pure function that a test can call directly, and that the
same findings can later be sorted, merged across files, counted by
severity, or emitted as JSON without touching any checker.

The one output format covers what the existing checkers already print:

    path:line: message
    path:line:col: message                (when `col` is set)
    path:line:col: CODE message           (when `code` is set too)

Named tools_report rather than the shorter "report" for the same reason
as tools_config/tools_repo/tools_pycode: it must never collide with a
book listing's own filename through Python's sys.modules cache. See
tools_repo.py's docstring for the failure that caused those renames.
"""

from collections.abc import Iterable
from pathlib import Path
from typing import NamedTuple


class Finding(NamedTuple):
    """One problem a check noticed, at one place in one file.

    `col` is 1-based to match editor and compiler convention, and is None
    when a check only knows the line. `code` is a short identifier like
    "P001" for checks that classify what they find; it stays empty for
    checks that report only one kind of problem.
    """

    path: Path
    line: int
    message: str
    col: int | None = None
    code: str = ""

    def format(self) -> str:
        """The `path:line[:col]: [CODE ]message` form editors can jump to."""
        where = f"{self.path}:{self.line}"
        if self.col is not None:
            where += f":{self.col}"
        what = f"{self.code} {self.message}" if self.code else self.message
        return f"{where}: {what}"


def report(
    findings: Iterable[Finding], *, clean: str, problem: str,
) -> int:
    """Print every finding, then a summary. Exit code 0 if none, else 1.

    `clean` is printed when there are no findings. `problem` is printed
    after a blank line when there are, and may use `{n}` for the count;
    it carries its own advice about what to do, since that differs per
    check. Findings are printed in the order given, so a caller that
    needs deterministic output across a parallel run sorts first.
    """
    total = 0
    for finding in findings:
        print(finding.format())
        total += 1
    if total:
        print(f"\n{problem.format(n=total)}")
        return 1
    print(clean)
    return 0
