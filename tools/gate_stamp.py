#!/usr/bin/env python
"""Record when the gate last passed, and whether the book changed since.

`make gate` takes tens of seconds, so it is run occasionally rather than
constantly, and after an editing session it is easy to lose track of whether
the current text has ever been through it. This writes a stamp when the gate
passes and reports on it afterwards:

    make gate-status

The stamp is more than a timestamp. It records a hash of every
``Chapters/*.md`` and ``Solutions/*.md`` file, so the report can answer the
question that actually matters, which is not "when did the gate run" but
"has anything changed since it did":

    gate passed 12 minutes ago (2026-07-25 14:03), at commit d6b9ad6
    3 files changed since: 23_Patterns--Iterators.md, 24_Patterns--Singleton.md, ...

It lives in ``build/``, which is gitignored, so it never enters a commit or
a diff. ``make clean-examples`` and friends remove only their own
subdirectories and leave it alone; a full ``rm -rf build`` drops it, which
is correct, since a rebuilt-from-nothing tree deserves a fresh gate.

Usage:
    python tools/gate_stamp.py --write gate   # record a pass
    python tools/gate_stamp.py                # report
"""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime
from typing import Any

from tools_config import BUILD_DIR, ROOT

STAMP = BUILD_DIR / "gate-stamp.json"
SOURCES = ("Chapters", "Solutions")
MAX_LISTED = 6


def digests() -> dict[str, str]:
    """A hash per Markdown file the gate checks."""
    out: dict[str, str] = {}
    for folder in SOURCES:
        for md in sorted((ROOT / folder).glob("*.md")):
            data = md.read_bytes()
            out[f"{folder}/{md.name}"] = hashlib.sha256(data).hexdigest()
    return out


def head() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write(target: str) -> None:
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(json.dumps({
        "target": target,
        "when": datetime.now().isoformat(timespec="seconds"),
        "head": head(),
        "files": digests(),
    }), encoding="utf-8")


def ago(then: datetime) -> str:
    seconds = (datetime.now() - then).total_seconds()
    if seconds < 90:
        return "just now"
    minutes = seconds / 60
    if minutes < 90:
        return f"{minutes:.0f} minutes ago"
    hours = minutes / 60
    if hours < 36:
        return f"{hours:.0f} hours ago"
    return f"{hours / 24:.0f} days ago"


def changes(recorded: dict[str, str]) -> list[str]:
    """Files added, removed, or edited since the stamp."""
    current = digests()
    names = set(recorded) | set(current)
    return sorted(
        name for name in names
        if recorded.get(name) != current.get(name))


def report() -> int:
    """Always succeeds: this answers a question, it does not gate anything."""
    if not STAMP.is_file():
        print("No gate run recorded. Run `make gate`.")
        return 0
    stamp: dict[str, Any] = json.loads(STAMP.read_text(encoding="utf-8"))
    when = datetime.fromisoformat(stamp["when"])
    print(f"{stamp['target']} passed {ago(when)} "
          f"({when:%Y-%m-%d %H:%M}), at commit {stamp['head']}")

    edited = changes(stamp.get("files", {}))
    if not edited:
        print("Nothing in Chapters/ or Solutions/ has changed since.")
        return 0
    # Keep the folder: Chapters/ and Solutions/ share file names by design,
    # so a bare basename reports the same thing twice.
    shown = ", ".join(edited[:MAX_LISTED])
    extra = len(edited) - MAX_LISTED
    more = f", +{extra} more" if extra > 0 else ""
    print(f"{len(edited)} file(s) changed since: {shown}{more}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", metavar="TARGET",
                    help="record that TARGET passed, instead of reporting")
    args = ap.parse_args(argv)
    if args.write:
        write(args.write)
        return 0
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
