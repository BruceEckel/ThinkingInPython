#!/usr/bin/env python3
"""Run the everyday edit-and-check loop: every fixer, then the full gate.

`tip verify` is what to run after touching a chapter: every mutating
fixer (the comment-style fixers, import sorting, blank-line cleanup), a
refresh of the `#:` output markers, a sync of the committed Examples/ and
Solutions/ code, the figure gallery, then the full gate. Each fixer
repairs something the gate would otherwise fail on, and the gate already
self-heals line endings, reflow, and markers, so a loop without the
fixers would only trade a fix for a failure.

`output` (the target that rewrites `#:` markers to match a listing's real
stdout, in both trees) runs before `sync` on purpose, not after: `sync`
mirrors the Markdown as it currently reads into the committed trees, and
`gate`/`solutions-gate` only rewrite markers *inside* that same run, after
their own sync step already ran. Reversing that order (marker rewrite,
then sync) is what makes a stale marker converge in this single run
instead of needing the next one to catch up.

VERIFY_TARGETS below is the single list to edit: add or remove a task
name there and both the run order and the --help listing update
themselves, since the doc text is read straight from that task's own
one-line doc in tools/tasks.py (the same one `tip help` reads).
Nothing else needs to change.

`gate` runs with MARKERS=fresh, which skips its own marker refresh (and
solutions-gate's): the `output` step above already refreshed every marker
in both trees, and no step between them edits a listing. The refresh
executes every marked block, so running it twice cost ~15 s a run.

Each target runs as its own `tip <target>` subprocess, in order, with
output streamed live rather than captured, so whatever a fixer or the
gate finds shows up immediately. The run stops at the first failing
target, matching how a single task's own sequential steps already
behave.

Usage:
    python -m tools.verify            # run every target in VERIFY_TARGETS
    python -m tools.verify --help     # list the targets, without running
"""

import argparse
import subprocess
import time

from tools.tip_help import entries
from tools.config import ROOT
from tools.target_times import record
from tools.tip import format_seconds, nested_env, tip_argv

# The everyday loop, in run order. Add a task name here to include it;
# its --help text is read from tools/tasks.py automatically. The gate
# reflows prose itself (`reflow_prose --write`), so reflow is not a step.
VERIFY_TARGETS: list[str] = [
    "fix-eol",
    "fix-comment-caps",
    "fix-comment-periods",
    "fix-comment-spacing",
    "fix-listings",
    "fix-imports",
    "output",
    "sync",
    "figures",
    "gate",
]
# Extra words for a target's command line.
TARGET_ARGS: dict[str, list[str]] = {"gate": ["MARKERS=fresh"]}
# How a target runs here, where that differs from its own one-line doc:
# the gate's doc names the marker refresh, which MARKERS=fresh skips.
DOC_OVERRIDES: dict[str, str] = {
    "output": "Update the #: output markers of every chapter changed "
              "since its markers last passed, in both trees",
    "gate": "The gate, minus the marker refresh `output` just did "
            "(check, reflow, slugs, placement, ty, ruff, run, pytest, solutions-gate)",
}


def _docs() -> dict[str, str]:
    docs = {name: doc for name, doc in entries() if name is not None}
    return docs | DOC_OVERRIDES


def _listing(heading: str, names: list[str],
             took: dict[str, float] | None = None) -> str:
    """One line per target: its doc, and its seconds when `took` has them."""
    docs = _docs()
    width = max(len(name) for name in names)
    lines = [f"  {name:<{width}}  "
             + (f"{format_seconds(took[name]):>8}  " if took else "")
             + docs.get(name, '')
             for name in names]
    if took:
        lines.append(f"  {'total':<{width}}  "
                     f"{format_seconds(sum(took.values())):>8}")
    return f"{heading}\n" + "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        epilog=_listing("tip verify runs, in order:", VERIFY_TARGETS),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)

    ran: list[str] = []
    took: dict[str, float] = {}
    for name in VERIFY_TARGETS:
        print(f"-> {name}")
        start = time.monotonic()
        proc = subprocess.run(tip_argv(name, *TARGET_ARGS.get(name, [])),
                              cwd=ROOT, env=nested_env())
        took[name] = time.monotonic() - start
        ran.append(name)
        if proc.returncode == 0:
            record(name, took[name])
        if proc.returncode != 0:
            print(f"\n{name} failed (exit {proc.returncode}); stopping.\n")
            print(_listing("Ran:", ran, took))
            return proc.returncode
    print("\ntip verify: every target passed.\n")
    print(_listing("Ran:", ran, took))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
