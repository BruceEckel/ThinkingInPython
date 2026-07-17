#!/usr/bin/env python3
"""Run the everyday edit-and-check loop: every fixer, then the full gate.

`make all` is what to run after touching a chapter: every mutating fixer
(reflow, the comment-style fixers, import sorting, blank-line cleanup),
a refresh of the `#:` output markers, a sync of the generated trees, then
the full gate. It exists because `make verify` only runs the fixer its
own gate already forces (`fix-eol`) plus a bare `gate`; the rest, `reflow`
especially, are not gated at all, so a real edit-and-check loop has to run
them by hand every time.

`output`/`solutions-output` (the targets that rewrite `#:` markers to
match a listing's real stdout) run before `sync`/`solutions-sync` on
purpose, not after: `sync`/`solutions-sync` mirror the Markdown as it
currently reads into the committed Examples/SolutionsCode trees, and
`gate`/`solutions-gate` only rewrite markers *inside* that same run, after
their own sync step already ran. Reversing that order (marker rewrite,
then sync) is what makes a stale marker converge in this single run
instead of needing the next one to catch up.

ALL_TARGETS below is the single list to edit: add or remove a make target
name there and both the run order and the --help listing update
themselves, since the doc text is read straight from that target's own
`## text` comment in the Makefile (the same one `make help` reads).
Nothing else needs to change.

Each target runs as its own `make <target>` subprocess, in order, with
output streamed live rather than captured, so whatever a fixer or the
gate finds shows up immediately. The run stops at the first failing
target, matching how a single Makefile recipe's own sequential lines
already behave.

Usage:
    python tools/run_all.py            # run every target in ALL_TARGETS
    python tools/run_all.py --help     # list the targets, without running
"""

import argparse
import subprocess

from make_help import MAKEFILE, entries
from tools_config import ROOT

# The everyday loop, in run order. Add a make target name here to include
# it; its --help text is read from the Makefile automatically.
ALL_TARGETS: list[str] = [
    "fix-eol",
    "reflow",
    "fix-comment-caps",
    "fix-comment-periods",
    "fix-comment-spacing",
    "fix-listings",
    "fix-imports",
    "output",
    "solutions-output",
    "sync",
    "solutions-sync",
    "gate",
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
        epilog=_listing("make all runs, in order:", ALL_TARGETS),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)

    ran: list[str] = []
    for name in ALL_TARGETS:
        print(f"-> {name}")
        proc = subprocess.run(["make", name], cwd=ROOT)
        ran.append(name)
        if proc.returncode != 0:
            print(f"\n{name} failed (exit {proc.returncode}); stopping.\n")
            print(_listing("Ran:", ran))
            return proc.returncode
    print("\nmake all: every target passed.\n")
    print(_listing("Ran:", ran))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
