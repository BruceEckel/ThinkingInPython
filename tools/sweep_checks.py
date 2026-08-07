#!/usr/bin/env python
"""Run every static check over both trees, reporting all failures instead of the first.

`make gate` stops at its first failing step. That is right when you broke
one thing and want the shortest path to it. It is wrong right after a
tool upgrade, when the question is not whether something broke but how
much did.

The masking is worse than "you see the first error". `gate` declares
`solutions-gate` as a *prerequisite*, so the whole Solutions half runs
before gate's own recipe starts. A ty release that moves listings in
both trees therefore reports the Solutions ones and hides every
Chapters/ one behind them, which is the opposite of the order you would
guess from reading the recipe top to bottom. That is how a 0.0.58 to
0.0.63 bump presented as two redundant casts in Solutions/ when it had
in fact moved five sites across three chapters as well.

This runs each check to completion and summarizes:

    gate-checks     ok
    ty              FAIL
    lint            ok
    ...
    2 of 8 checks failed: ty, solutions-ty

`make upgrade-tools` ends with this, so an upgrade's damage arrives
attached to the upgrade that caused it. It is worth running on its own
(`make sweep`) after any change wide enough that the first failure is
unlikely to be the only one.

Each check runs as its own `make <target>` subprocess with output
streamed live, the arrangement tools/run_all.py already uses. Every one
of those targets depends on its own extract step, so both build trees
are rebuilt before anything reads them.

The `#:` output markers are deliberately not swept. `make verify`
rewrites a stale marker rather than failing on it, and a genuinely
nondeterministic listing would report a difference here on every run.
A tool upgrade that changes program output is a `make verify` question,
not a sweep question.

Usage:
    python tools/sweep_checks.py          # run every check
    python tools/sweep_checks.py --help   # list them, without running
"""

import argparse
import subprocess

from make_help import MAKEFILE, entries
from tools_config import ROOT

# Every check a tool upgrade can break, in run order. Cheapest and most
# likely to move first: ty and ruff are what a checker or linter release
# actually changes, and seeing them before the slower run/test steps
# means the interesting output is not scrolled away.
#
# gate-checks leads because it is the cheapest of all (one process, one
# parse per file), so it cannot scroll anything away. It is `gate`'s own
# Markdown selection rather than `checks`, which also runs prose-lint:
# prose-lint reports findings the book has not cleaned up, and a row that
# is permanently FAIL teaches you to stop reading the table.
SWEEP_TARGETS: list[str] = [
    "gate-checks",
    "solutions-numbering",
    "ty",
    "lint",
    "solutions-ty",
    "solutions-lint",
    "run",
    "test",
    "solutions-test",
]


def _docs() -> dict[str, str]:
    text = MAKEFILE.read_text(encoding="utf-8")
    return {name: doc for name, doc in entries(text) if name is not None}


def _listing(heading: str, names: list[str]) -> str:
    docs = _docs()
    width = max(len(name) for name in names)
    lines = [f"  {name:<{width}}  {docs.get(name, '')}" for name in names]
    return f"{heading}\n" + "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        epilog=_listing("make sweep runs, in order:", SWEEP_TARGETS),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)

    failed: list[str] = []
    for name in SWEEP_TARGETS:
        print(f"-> {name}")
        proc = subprocess.run(["make", name], cwd=ROOT)
        if proc.returncode != 0:
            failed.append(name)
            print(f"\n{name} FAILED (exit {proc.returncode}); continuing.\n")

    width = max(len(name) for name in SWEEP_TARGETS)
    print("\nSweep results:")
    for name in SWEEP_TARGETS:
        status = "FAIL" if name in failed else "ok"
        print(f"  {name:<{width}}  {status}")

    if not failed:
        print(f"\nAll {len(SWEEP_TARGETS)} checks passed.")
        return 0
    print(f"\n{len(failed)} of {len(SWEEP_TARGETS)} checks failed: "
          f"{', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
