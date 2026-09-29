#!/usr/bin/env python
"""Record when the dev tools were last upgraded, and say so when that was a while ago.

`tip tools-upgrade` is deliberately manual. It rewrites the tracked
uv.lock and can invoke winget or Homebrew, so nothing runs it on a
schedule and nothing should. The cost of that choice is drifting quietly
behind for months, then meeting every breaking change at once: one ty
bump moved five listings across three chapters and both Solutions
exercises.

This is the cheap half of the fix. `tools-upgrade` records a stamp when
it finishes, and the gate prints one line when that stamp is old:

    tools last upgraded 23 days ago (2026-07-04)
    That is over 14 days. Consider `tip tools-upgrade`, then `tip
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

The full report also says whether an upgrade is waiting. It compares
uv, the tools uv.lock pins (`LOCKED_TOOLS`: ty, ruff, pytest,
pyright), and the libraries the listings import
(`libs_check.LIBRARIES`: Stateless, numpy, and so on) with the latest
release on PyPI:

    uv             0.9.30    latest 0.9.31   behind
    ty             0.0.84    latest 0.0.84
    stateless      0.6.1     latest 0.6.1

It also notes a library that has moved since the stamp. A library can
move without a stamp, through `uv lock --upgrade-package`, and a
Stateless release is as much a book-wide event as a `ty` one.
Only the full report reaches the network. Its lookups run
concurrently, so an offline machine waits one timeout and reads
"latest unknown". `--nag`, which `gate` runs, reads the stamp alone,
since a gate must not reach the network.

With `--offer`, which `tip tools-status` passes, a report that finds
anything behind asks whether to run `tip tools-upgrade`. It asks only
a person at a terminal (stdin and stdout both a TTY, and no `CI`), so
a captured run, `tip verify-targets`, or an agent's shell never sees
the question, and the upgrade, which rewrites uv.lock, never starts
unattended. Anything but "y" or "yes" declines.

Usage:
    python -m tools.tool_stamp --write   # record an upgrade
    python -m tools.tool_stamp           # report, with PyPI's latest
    python -m tools.tool_stamp --offer   # the same, offering an upgrade
    python -m tools.tool_stamp --nag     # report only when stale
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any

from tools import libs_check
from tools.gate_stamp import ago
from tools.config import BUILD_DIR, ROOT
from tools.repo import run_capture

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

# The dev tools whose versions uv.lock pins, compared with PyPI in the
# full report. uv itself is not in the lock; `uv_version()` asks it.
LOCKED_TOOLS: tuple[str, ...] = ("ty", "ruff", "pytest", "pyright")

# The exit status of `--offer` when the person accepts the upgrade.
# The tools-status task catches it and runs tools-upgrade in the same
# `tip` run, so the upgrade's steps are timed and echoed like any other.
UPGRADE_REQUESTED = 10


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
        "libraries": libs_check.current(),
    }), encoding="utf-8")


def read_stamp() -> dict[str, Any]:
    if not STAMP.is_file():
        return {}
    return json.loads(STAMP.read_text(encoding="utf-8"))


def last_upgrade() -> tuple[datetime, dict[str, str], str] | None:
    """When the toolchain last moved, from the stamp or else uv.lock."""
    stamp = read_stamp()
    if stamp:
        return (datetime.fromisoformat(stamp["when"]),
                stamp.get("versions", {}), "tools-upgrade")
    if LOCK.is_file():
        when = datetime.fromtimestamp(LOCK.stat().st_mtime)
        return when, {}, "uv.lock"
    return None


def uv_version() -> str | None:
    """The running uv's version number, or None if uv will not answer."""
    result = run_capture(["uv", "--version"])
    if result is None or result[1] != 0:
        return None
    words = result[0].split()
    return words[1] if len(words) > 1 else None


def package_lines(found: list[tuple[str, str, str | None]],
                  stamped: dict[str, str]) -> list[str]:
    """One line per package: its version, PyPI's latest, and any move.

    The versions are read live (uv.lock, and `uv --version`), so a
    library upgraded with `uv lock --upgrade-package`, which writes no
    stamp, shows here as moved since the last tools-upgrade.
    """
    lines: list[str] = []
    for name, version, newest in found:
        was = stamped.get(name)
        moved = f"   (was {was} at the last tools-upgrade)" \
            if was and was != version else ""
        lines.append(f"  {name:<14} {version:<9} "
                     f"{libs_check.note(version, newest)}{moved}")
    return lines


def upgrade_report(stamped: dict[str, str]) -> set[str]:
    """Compare uv, the locked tools, and the libraries with PyPI.

    Returns the names of the packages that are behind.
    """
    installed: dict[str, str] = {}
    if uv := uv_version():
        installed["uv"] = uv
    installed |= libs_check.current(LOCKED_TOOLS)
    libraries = set(libs_check.current())
    installed |= libs_check.current()
    if not installed:
        return set()
    found = libs_check.rows(installed)
    print("installed, against the latest on PyPI:")
    print("\n".join(package_lines(found, stamped)))
    behind = {name for name, version, newest in found
              if newest is not None and newest != version}
    if behind - libraries:
        print("`tip tools-upgrade` upgrades uv and the tools "
              "(and the libraries with them).")
    if behind & libraries:
        print("To upgrade one library alone: "
              "`uv lock --upgrade-package NAME`, `uv sync`, `tip sweep`.")
    return behind


def interactive() -> bool:
    """True when a person is at the terminal: never in CI or a pipe."""
    return (not os.environ.get("CI")
            and sys.stdin.isatty() and sys.stdout.isatty())


def wants_upgrade() -> bool:
    """Ask whether to run tools-upgrade now; anything but yes is no."""
    try:
        answer = input("Run `tip tools-upgrade` now? It rewrites uv.lock "
                       "and ends with `tip sweep`. [y/N] ")
    except EOFError:
        return False
    return answer.strip().lower() in {"y", "yes"}


def report(*, nag_only: bool, days: int, offer: bool = False) -> int:
    """Succeeds unless an offered upgrade is accepted.

    This answers a question and gates nothing, so it exits 0, except
    that with `offer`, a person at the terminal who accepts the upgrade
    gets UPGRADE_REQUESTED, which the tools-status task turns into a
    run of tools-upgrade.
    """
    found = last_upgrade()
    if found is None:
        if not nag_only:
            print("No tool upgrade recorded, and no uv.lock to date.")
        return 0

    when, _, source = found
    stale = (datetime.now() - when).days >= days
    if nag_only and not stale:
        return 0

    dated = "" if source == "tools-upgrade" else f", dated from {source}"
    print(f"tools last upgraded {ago(when)} ({when:%Y-%m-%d}){dated}")
    behind: set[str] = set()
    if not nag_only:
        behind = upgrade_report(read_stamp().get("libraries", {}))
    if stale:
        print(f"That is over {days} days. Consider `tip tools-upgrade`, "
              "then `tip sweep` to see what moved.")
    if offer and behind and interactive() and wants_upgrade():
        return UPGRADE_REQUESTED
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true",
                    help="record an upgrade as happening now")
    ap.add_argument("--nag", action="store_true",
                    help="print only when the stamp is stale")
    ap.add_argument("--offer", action="store_true",
                    help="ask a person at the terminal whether to "
                         f"upgrade; yes exits {UPGRADE_REQUESTED}")
    ap.add_argument("--days", type=int, default=STALE_AFTER_DAYS,
                    help=f"days before stale (default {STALE_AFTER_DAYS})")
    args = ap.parse_args(argv)
    if args.write:
        write()
        return 0
    return report(nag_only=args.nag, days=args.days,
                  offer=args.offer and not args.nag)


if __name__ == "__main__":
    raise SystemExit(main())
