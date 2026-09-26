#!/usr/bin/env python3
"""Do all the work, with no shortcuts: every fixer and gate, then every build.

`tip verify` skips work that cannot find anything new
(`tools/skip_stamps.py`): the markers of unchanged chapters, the tools'
own tests while tools/ is unchanged, and all but the unmarked listings
between daily full runs. `tip everything` sets `TIP_FULL=1`, which turns
every one of those off, and then goes past the gate: the spelling and
house-style checks, which no gate runs, and the three book builds.

Unlike `verify`, it keeps going after a failure and reports every target
at the end, so one run shows everything that is wrong. It exits nonzero
if any target failed. Run it before a release, after a tool upgrade, or
whenever the shortcuts' assumptions are in doubt.

Left out on purpose: `links` (network, and link rot is not the book's
fault), `pyright-review` (advisory), the `rust-*` tasks (they need cargo),
`verify-targets` (it smoke-tests the harness, not the book), and anything
that publishes.

Usage:
    python -m tools.everything          # run every target in EVERYTHING
    python -m tools.everything --help   # list them, without running
"""

import argparse
import os
import subprocess
import time

from tools.config import ROOT
from tools.skip_stamps import FULL_ENV
from tools.tip import nested_env, tip_argv
from tools.verify import _listing

EVERYTHING: list[str] = [
    "verify",
    "spell",
    "prose",
    "site",
    "epub",
    "pdf",
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        epilog=_listing("tip everything runs, in order:", EVERYTHING),
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)

    os.environ[FULL_ENV] = "1"
    took: dict[str, float] = {}
    failed: list[str] = []
    for name in EVERYTHING:
        print(f"-> {name}")
        start = time.monotonic()
        proc = subprocess.run(tip_argv(name), cwd=ROOT, env=nested_env())
        took[name] = time.monotonic() - start
        if proc.returncode != 0:
            failed.append(name)
            print(f"\n{name} failed (exit {proc.returncode}); continuing.\n")
    print()
    print(_listing("Ran:", EVERYTHING, took))
    if failed:
        print(f"\ntip everything: {len(failed)} target(s) failed: "
              f"{', '.join(failed)}")
        return 1
    print("\ntip everything: every target passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
