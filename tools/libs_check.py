#!/usr/bin/env python
"""Compare the book's libraries, as locked, with the latest on PyPI.

The dev group holds two kinds of package. The tools (`ty`, `ruff`,
`pytest`) check the listings. The libraries are what the listings
import: a release of one can change a listing's behavior, a revealed
type, or an overload list the prose quotes, the same way a `ty` upgrade
can. Stateless is the heavy case: 88 listings import it, and chapters
46 and 47 describe its API in prose.

`make tools-upgrade` moves the libraries along with the tools
(`uv lock --upgrade` upgrades everything), but nothing says when a
library has a release waiting. This does, and changes nothing:

    stateless      0.6.1     latest 0.7.0   behind
    numpy          2.5.3     latest 2.5.3

A library that is behind is upgraded alone with
`uv lock --upgrade-package NAME` and `uv sync`, so a failure afterward
has one cause. The `tool-upgrade` skill's Stateless-upgrade entry
lists what to re-check.

It always exits 0. It answers a question, and an offline machine or a
PyPI outage must not fail `make verify-targets`, which runs every
documented target. It belongs to no gate: a gate that reaches the
network fails for reasons the book did not cause.

Usage:
    python -m tools.libs_check
"""
import json
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable

from tools.config import ROOT

LOCK = ROOT / "uv.lock"
PYPI = "https://pypi.org/pypi/{name}/json"
TIMEOUT_SECONDS = 10

# The dev-group packages that listings import. A tool the gates run
# (ty, ruff, pytest) belongs in tool_stamp.VERSIONED instead.
LIBRARIES: tuple[str, ...] = (
    "stateless", "numpy", "hypothesis", "time-machine")


def locked_versions(lock_text: str) -> dict[str, str]:
    """Each library's version in a uv.lock, skipping any it does not hold."""
    packages = tomllib.loads(lock_text).get("package", [])
    by_name = {p["name"]: p["version"] for p in packages if "version" in p}
    return {name: by_name[name] for name in LIBRARIES if name in by_name}


def current() -> dict[str, str]:
    """The libraries as locked right now; empty with no uv.lock."""
    if not LOCK.is_file():
        return {}
    return locked_versions(LOCK.read_text(encoding="utf-8"))


def pypi_latest(name: str) -> str | None:
    """The newest release PyPI lists for `name`, or None if unreachable."""
    try:
        with urllib.request.urlopen(
                PYPI.format(name=name), timeout=TIMEOUT_SECONDS) as reply:
            return json.load(reply)["info"]["version"]
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
        return None


def rows(locked: dict[str, str],
         latest: Callable[[str], str | None] = pypi_latest,
         ) -> list[tuple[str, str, str | None]]:
    """(name, locked version, latest version or None) per library."""
    return [(name, version, latest(name))
            for name, version in locked.items()]


def main() -> int:
    locked = current()
    if not locked:
        print(f"No libraries found in {LOCK.name}.")
        return 0
    found = rows(locked)
    for name, version, newest in found:
        if newest is None:
            note = "latest unknown (PyPI unreachable)"
        elif newest == version:
            note = f"latest {newest}"
        else:
            note = f"latest {newest}   behind"
        print(f"{name:<14} {version:<9} {note}")
    behind = [name for name, version, newest in found
              if newest is not None and newest != version]
    if behind:
        print("Upgrade one alone: `uv lock --upgrade-package NAME` then "
              "`uv sync`, then `make sweep`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
