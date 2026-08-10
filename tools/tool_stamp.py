#!/usr/bin/env python
"""Record when the dev tools were last upgraded, and say so when that was a while ago.

`make tools-upgrade` is deliberately manual. It rewrites the tracked
uv.lock and can invoke winget or Homebrew, so nothing runs it on a
schedule and nothing should. The cost of that choice is drifting quietly
behind for months, then meeting every breaking change at once: one ty
bump moved five listings across three chapters and both Solutions
exercises.

This is the cheap half of the fix. `tools-upgrade` records a stamp when
it finishes, and the gate prints one line when that stamp is old:

    tools last upgraded 23 days ago (2026-07-04)
    That is over 14 days. Consider `make tools-upgrade`, then `make
    sweep` to see what moved.

It never fails and never touches a tracked file, so it cannot turn a
green gate red or dirty a chapter commit. The stamp lives in build/,
which is gitignored, beside gate-stamp.json.

With no stamp yet (a fresh clone, or a tree that has never run
tools-upgrade) the mtime of uv.lock stands in. `uv lock --upgrade`
rewrites that file, as does any dependency change, and on a fresh clone
git sets it to checkout time. That is the honest answer there: the
toolchain is as new as the resolve that produced it, so a fresh clone
gets no nag.

Usage:
    python tools/tool_stamp.py --write   # record an upgrade
    python tools/tool_stamp.py           # report, always
    python tools/tool_stamp.py --nag     # report only when stale
"""

import argparse
import json
from datetime import datetime
from typing import Any

from gate_stamp import ago
from tools_config import BUILD_DIR, ROOT
from tools_repo import run_capture

STAMP = BUILD_DIR / "tool-stamp.json"
LOCK = ROOT / "uv.lock"
STALE_AFTER_DAYS = 14

# Worth recording: the uv-managed tools every gate runs. Their versions
# make the report answer "upgraded to what", not just "upgraded when".
VERSIONED: tuple[tuple[str, list[str]], ...] = (
    ("ty", ["uv", "run", "ty", "--version"]),
    ("ruff", ["uv", "run", "ruff", "--version"]),
    ("pytest", ["uv", "run", "pytest", "--version"]),
)


def versions() -> dict[str, str]:
    """What each uv-managed tool reports right now.

    Only called by --write. The reporting paths run on every gate, so
    they read the stamp and start no subprocess at all.
    """
    found: dict[str, str] = {}
    for name, cmd in VERSIONED:
        result = run_capture(cmd, combine_stderr=True)
        if result is None:
            continue
        text, code = result
        if code == 0 and text.strip():
            found[name] = text.strip().splitlines()[0]
    return found


def write() -> None:
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(json.dumps({
        "when": datetime.now().isoformat(timespec="seconds"),
        "versions": versions(),
    }), encoding="utf-8")


def last_upgrade() -> tuple[datetime, dict[str, str], str] | None:
    """When the toolchain last moved, from the stamp or else uv.lock."""
    if STAMP.is_file():
        stamp: dict[str, Any] = json.loads(
            STAMP.read_text(encoding="utf-8"))
        return (datetime.fromisoformat(stamp["when"]),
                stamp.get("versions", {}), "tools-upgrade")
    if LOCK.is_file():
        when = datetime.fromtimestamp(LOCK.stat().st_mtime)
        return when, {}, "uv.lock"
    return None


def report(*, nag_only: bool, days: int) -> int:
    """Always succeeds: this answers a question, it does not gate anything."""
    found = last_upgrade()
    if found is None:
        if not nag_only:
            print("No tool upgrade recorded, and no uv.lock to date.")
        return 0

    when, recorded, source = found
    stale = (datetime.now() - when).days >= days
    if nag_only and not stale:
        return 0

    dated = "" if source == "tools-upgrade" else f", dated from {source}"
    print(f"tools last upgraded {ago(when)} ({when:%Y-%m-%d}){dated}")
    if recorded and not nag_only:
        for name, version in recorded.items():
            print(f"  {name}: {version}")
    if stale:
        print(f"That is over {days} days. Consider `make tools-upgrade`, "
              "then `make sweep` to see what moved.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="record an upgrade as happening now")
    ap.add_argument("--nag", action="store_true",
                    help="print only when the stamp is stale")
    ap.add_argument("--days", type=int, default=STALE_AFTER_DAYS,
                    help=f"days before stale (default {STALE_AFTER_DAYS})")
    args = ap.parse_args(argv)
    if args.write:
        write()
        return 0
    return report(nag_only=args.nag, days=args.days)


if __name__ == "__main__":
    raise SystemExit(main())
