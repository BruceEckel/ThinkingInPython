#!/usr/bin/env python
"""Run every static check over both trees, reporting all failures instead of the first.

`tip gate` stops at its first failing step. That is right when you broke
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

    checks          ok
    ty              FAIL
    lint            ok
    ...
    2 of 7 checks failed: ty, run

`tip tools-upgrade` ends with this, so an upgrade's damage arrives
attached to the upgrade that caused it. It is worth running on its own
(`tip sweep`) after any change wide enough that the first failure is
unlikely to be the only one.

Each check runs as its own `tip <target>` subprocess with output
streamed live, the arrangement tools/verify.py already uses. Every one
of those targets covers both build trees and depends on `extract`, so
both trees are rebuilt before anything reads them; `ty` and `lint` run
one invocation over both, so a failure in one tree never hides the
other's.

The `#:` output markers are deliberately not swept. `tip verify`
rewrites a stale marker rather than failing on it, and a genuinely
nondeterministic listing would report a difference here on every run.
A tool upgrade that changes program output is a `tip verify` question,
not a sweep question.

Usage:
    python -m tools.sweep_checks          # run every check
    python -m tools.sweep_checks --help   # list them, without running
"""

import argparse
import subprocess
import time

from tools.tip_help import entries
from tools.config import ROOT
from tools.target_times import record
from tools.tip import format_seconds, nested_env, tip_argv

# Every check a tool upgrade can break, in run order. Cheapest and most
# likely to move first: ty and ruff are what a checker or linter release
# actually changes, and seeing them before the slower run/test steps
# means the interesting output is not scrolled away.
#
# checks leads because it is the cheapest of all (one process, one parse
# per file), so it cannot scroll anything away; it is the gate's own
# Markdown selection (check_all's whole registry), and Vale is `prose`,
# which no gate runs.
SWEEP_TARGETS: list[str] = [
    "checks",
    "coupling-panels",
    "state-machine-figure",
    "solutions-numbering",
    "ty",
    "lint",
    "run",
    "test",
]


def _docs() -> dict[str, str]:
    return {name: doc for name, doc in entries() if name is not None}


def _listing(heading: str, names: list[str]) -> str:
    docs = _docs()
    width = max(len(name) for name in names)
    lines = [f"  {name:<{width}}  {docs.get(name, '')}" for name in names]
    return f"{heading}\n" + "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        epilog=_listing("tip sweep runs, in order:", SWEEP_TARGETS),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)

    failed: list[str] = []
    took: dict[str, float] = {}
    for name in SWEEP_TARGETS:
        print(f"-> {name}")
        start = time.monotonic()
        proc = subprocess.run(tip_argv(name), cwd=ROOT, env=nested_env())
        took[name] = time.monotonic() - start
        if proc.returncode == 0:
            record(name, took[name])
        if proc.returncode != 0:
            failed.append(name)
            print(f"\n{name} FAILED (exit {proc.returncode}); continuing.\n")

    width = max(len(name) for name in SWEEP_TARGETS)
    print("\nSweep results:")
    for name in SWEEP_TARGETS:
        status = "FAIL" if name in failed else "ok"
        print(f"  {name:<{width}}  {status:<4}  "
              f"{format_seconds(took[name]):>8}")
    print(f"  {'total':<{width}}  {'':<4}  "
          f"{format_seconds(sum(took.values())):>8}")

    if not failed:
        print(f"\nAll {len(SWEEP_TARGETS)} checks passed.")
        return 0
    print(f"\n{len(failed)} of {len(SWEEP_TARGETS)} checks failed: "
          f"{', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
