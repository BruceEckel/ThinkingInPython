#!/usr/bin/env python
"""Run one make goal in a child make and report its wall-clock time.

The Makefile's top level hands every goal named on the command line to
this script (the `TIMED` block there), so `make verify` prints
`make verify: 1m 32s` after verify's own output, or the exit code and
the time when it fails. The child make runs with `TIMED=1`, which
selects the real rules, and GNU Make passes a command-line variable on
to every make the child starts, so a nested `$(MAKE) sweep` or the
per-target subprocesses in run_all.py and sweep_checks.py print no line
of their own (those two time each step themselves).

Usage, from the Makefile only:
    python -m tools.timed_make <make-executable> <goal>
"""

import subprocess
import sys
import time


def format_seconds(seconds: float) -> str:
    """`12.3s` under a minute, `1m 32s` under an hour, else `1h 02m 05s`."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {rest:02.0f}s"
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}h {minutes:02d}m {rest:02.0f}s"


def report(goal: str, code: int, seconds: float) -> str:
    """The one line printed after the goal finishes."""
    elapsed = format_seconds(seconds)
    if code == 0:
        return f"make {goal}: {elapsed}"
    return f"make {goal}: failed (exit {code}) after {elapsed}"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: python -m tools.timed_make <make> <goal>",
              file=sys.stderr)
        return 2
    make, goal = args
    sys.stdout.flush()
    start = time.monotonic()
    try:
        code = subprocess.call(
            [make, "--no-print-directory", "TIMED=1", goal])
    except KeyboardInterrupt:
        code = 130
    print(report(goal, code, time.monotonic() - start), flush=True)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
