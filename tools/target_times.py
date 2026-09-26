#!/usr/bin/env python
"""How long each tip task takes, for the help listing to show.

Two sources, the first preferred:

* `build/target_times.json`, this machine's last successful run of each
  target, written by everything that already times a run: tip.py
  (every goal named on a command line), verify.py and sweep_checks.py
  (each of their steps), and verify_targets.py (every target it runs).
  It is under build/, so gitignored: a fresh clone starts empty.
* `tools/data/target_tiers.txt`, committed, one tier per target
  (`quick`, `normal`, `long`, `very long`), written by verify_targets.py
  from its own measurements and merged over what the file already
  had, so a target that run never touches keeps its line. A tier
  changes rarely, which keeps the file's diffs small and meaningful.

`timings()` merges the two: a target with a local measurement shows
its seconds, colored by tier; one with a baseline line alone shows the
tier's name; one with neither shows nothing. The thresholds are TIERS.

Usage:
    python -m tools.target_times            # print what the listing knows
"""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from tools.config import ROOT
from tools.tip import format_seconds

CACHE = ROOT / "build" / "target_times.json"
BASELINE = ROOT / "tools" / "data" / "target_tiers.txt"

# (tier, upper bound in seconds), in order; the last catches everything.
TIERS: tuple[tuple[str, float], ...] = (
    ("quick", 5.0),
    ("normal", 30.0),
    ("long", 120.0),
    ("very long", math.inf),
)

_HEADER = """\
# How long each tip task takes, as a tier: quick (under 5 s),
# normal (under 30 s), long (under 2 min), very long. Written by
# `tip verify-targets` from its own measurements; a line for a target
# that run never executes is kept as it was. The help listing shows
# this tier for a target this machine has not run yet, and the
# measured seconds (build/target_times.json) once it has.
"""


@dataclass(frozen=True)
class Timing:
    """What the listing prints for one target and which tier colors it."""
    label: str
    tier: str


def tier(seconds: float) -> str:
    """The tier `seconds` falls in."""
    for name, limit in TIERS:
        if seconds < limit:
            return name
    return TIERS[-1][0]


def cached(path: Path = CACHE) -> dict[str, float]:
    """This machine's last measured seconds per target, or {}."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {name: float(entry["seconds"]) for name, entry in data.items()
            if isinstance(entry, dict) and "seconds" in entry}


def record(name: str, seconds: float, path: Path = CACHE) -> None:
    """Remember `name`'s successful run of `seconds`, replacing the last."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data[name] = {"seconds": round(seconds, 1),
                  "when": datetime.now(timezone.utc).isoformat(
                      timespec="seconds")}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def baseline(path: Path = BASELINE) -> dict[str, str]:
    """The committed tier per target, or {} when the file is missing."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    found: dict[str, str] = {}
    for line in lines:
        if not line or line.startswith("#"):
            continue
        name, _, tier_name = line.partition("\t")
        if tier_name in {t for t, _ in TIERS}:
            found[name] = tier_name
    return found


def write_baseline(times: Mapping[str, float],
                   path: Path = BASELINE) -> dict[str, str]:
    """Merge `times` (seconds per target) over the file's tiers and
    rewrite it, sorted by name. Returns what was written."""
    tiers = baseline(path)
    tiers.update({name: tier(s) for name, s in times.items()})
    body = "".join(f"{name}\t{tiers[name]}\n" for name in sorted(tiers))
    path.write_text(_HEADER + body, encoding="utf-8", newline="\n")
    return tiers


def timings(cache: Path = CACHE,
            base: Path = BASELINE) -> dict[str, Timing]:
    """What the listing shows: measured seconds where this machine has
    them, the committed tier where it does not."""
    shown: dict[str, Timing] = {
        name: Timing(tier_name, tier_name)
        for name, tier_name in baseline(base).items()}
    for name, seconds in cached(cache).items():
        shown[name] = Timing(short(seconds), tier(seconds))
    return shown


def short(seconds: float) -> str:
    """`0.8s`, `56s`, `1m 32s`: whole seconds once past ten."""
    if seconds < 10:
        return f"{seconds:.1f}s"
    if seconds < 60:
        return f"{seconds:.0f}s"
    return format_seconds(seconds)


def main() -> int:
    known = timings()
    if not known:
        print("No timings yet: run a target, or `tip verify-targets`.")
        return 0
    width = max(len(n) for n in known)
    for name in sorted(known):
        t = known[name]
        print(f"  {name:<{width}}  {t.label:>8}  {t.tier}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
