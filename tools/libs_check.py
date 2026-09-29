"""Read locked versions from uv.lock and the latest releases from PyPI.

The dev group holds two kinds of package. The tools (`ty`, `ruff`,
`pytest`) check the listings. The libraries are what the listings
import: a release of one can change a listing's behavior, a revealed
type, or an overload list the prose quotes, the same way a `ty` upgrade
can. Stateless is the heavy case: 88 listings import it, and chapters
46 and 47 describe its API in prose.

`tip tools-upgrade` moves the libraries along with the tools
(`uv lock --upgrade` upgrades everything). `tip tools-status`
(`tool_stamp.py`) uses this module to say when a release is waiting,
for the libraries and for the tools. A library that is behind is
upgraded alone with `uv lock --upgrade-package NAME` and `uv sync`, so
a failure afterward has one cause. The `tool-upgrade` skill's
Stateless-upgrade entry lists what to re-check.

Nothing here raises an exception when PyPI is unreachable: a lookup
returns None, and the report says "latest unknown". An offline
machine must not fail `tip verify-targets`, which runs every
documented target, and no gate uses this module, since a gate that
reaches the network fails for reasons the book did not cause.
"""
import json
import tomllib
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor

from tools.config import ROOT

LOCK = ROOT / "uv.lock"
PYPI = "https://pypi.org/pypi/{name}/json"
TIMEOUT_SECONDS = 10

# The dev-group packages that listings import. A tool the gates run
# (ty, ruff, pytest) belongs in tool_stamp.VERSIONED instead.
LIBRARIES: tuple[str, ...] = (
    "stateless", "numpy", "hypothesis", "time-machine")


def locked_versions(lock_text: str,
                    names: Iterable[str] = LIBRARIES) -> dict[str, str]:
    """Each named package's version in a uv.lock, skipping any it lacks."""
    packages = tomllib.loads(lock_text).get("package", [])
    by_name = {p["name"]: p["version"] for p in packages if "version" in p}
    return {name: by_name[name] for name in names if name in by_name}


def current(names: Iterable[str] = LIBRARIES) -> dict[str, str]:
    """The named packages as locked right now; empty with no uv.lock."""
    if not LOCK.is_file():
        return {}
    return locked_versions(LOCK.read_text(encoding="utf-8"), names)


def pypi_latest(name: str) -> str | None:
    """The newest release PyPI lists for `name`, or None if unreachable."""
    try:
        with urllib.request.urlopen(
                PYPI.format(name=name), timeout=TIMEOUT_SECONDS) as reply:
            return json.load(reply)["info"]["version"]
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
        return None


def rows(locked: dict[str, str],
         latest: Callable[[str], str | None] | None = None,
         ) -> list[tuple[str, str, str | None]]:
    """(name, locked version, latest version or None) per package.

    The lookups run concurrently, so an offline machine waits one
    timeout rather than one per package.
    """
    lookup = latest or pypi_latest
    names = list(locked)
    with ThreadPoolExecutor(max_workers=max(1, len(names))) as pool:
        newest = list(pool.map(lookup, names))
    return [(name, locked[name], found)
            for name, found in zip(names, newest)]


def note(version: str, newest: str | None) -> str:
    """How a locked version compares with PyPI's latest, for a report line."""
    if newest is None:
        return "latest unknown (PyPI unreachable)"
    if newest == version:
        return f"latest {newest}"
    return f"latest {newest}   behind"
