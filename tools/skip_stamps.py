"""Stamps that let the gate skip work it has already done, and say when not to.

The gate repeats two kinds of work on every run that rarely find anything
new, so each gets a stamp in ``build/`` (gitignored, like the gate stamp)
that records the last time the work passed:

- **The tools' own tests** (``tools/tests``, ~7 s). They test the tools,
  so while nothing under ``tools/`` changes, a rerun cannot fail
  differently. ``tools_digest()`` hashes every file under ``tools/``
  (code, tests, data) plus ``pyproject.toml`` and ``uv.lock``, since a
  dependency bump can break a tool too. ``tools/tools_tests.py`` skips the
  suite when the digest matches the last pass. A test that reads the book
  itself (a chapter, not a fixture) is marked ``book`` and runs every
  time, since a chapter edit can break it with ``tools/`` untouched.
- **Running every listing as its own process** (``run_examples``, ~13 s).
  Nine in ten listings carry ``#:`` markers, and the marker refresh has
  already executed each of those in the same gate. ``run_examples
  --quick`` runs only the unmarked ones, unless the tree's last full run
  is older than ``FULL_RUN_EVERY`` or never happened. The full run is
  not redundant: it runs each listing in a fresh process, as a reader
  would, where the marker refresh execs every block of a chapter in one
  interpreter, so it catches a listing that leans on a module an earlier
  block imported, or that fails only as ``__main__`` in its own cwd.
  Those breaks are rare and slow to appear, which is why once a day
  suffices.

Setting ``TIP_FULL=1`` in the environment disables both shortcuts. ``tip
ci`` and ``tip release`` set it; ``tip gate RUN=full`` sets it for one
gate; ``tip run`` and ``tip tools-test`` always do the full work, and a
passing full run refreshes its stamp.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from tools.config import BUILD_DIR, ROOT

FULL_ENV = "TIP_FULL"
FULL_RUN_EVERY = timedelta(hours=24)
TOOLS_STAMP = BUILD_DIR / "tools-tests-stamp.json"
FULL_RUN_STAMP = BUILD_DIR / "full-run-stamp.json"
# Beyond tools/: what a tool's behavior also depends on.
TOOLS_EXTRA = ("pyproject.toml", "uv.lock")


def forced_full() -> bool:
    """True when the caller asked for every shortcut to be off."""
    return os.environ.get(FULL_ENV) == "1"


def tools_digest() -> str:
    """One hash over every file under tools/ and TOOLS_EXTRA."""
    h = hashlib.sha256()
    files = sorted(
        p for p in (ROOT / "tools").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts)
    files += [ROOT / name for name in TOOLS_EXTRA]
    for path in files:
        h.update(path.relative_to(ROOT).as_posix().encode())
        h.update(b"\0")
        if path.is_file():
            h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def _read(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _write(path: Path, data: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")


def tools_tests_current(digest: str) -> bool:
    return _read(TOOLS_STAMP).get("digest") == digest


def record_tools_tests(digest: str) -> None:
    _write(TOOLS_STAMP, {
        "digest": digest,
        "when": datetime.now().isoformat(timespec="seconds")})


def _tree_key(tree: Path) -> str:
    return tree.resolve().name


def full_run_due(tree: Path) -> str | None:
    """Why `tree` needs a full run now, or None if a quick run will do."""
    if forced_full():
        return f"{FULL_ENV}=1"
    when = _read(FULL_RUN_STAMP).get(_tree_key(tree))
    if when is None:
        return "no full run recorded"
    age = datetime.now() - datetime.fromisoformat(when)
    if age > FULL_RUN_EVERY:
        return f"last full run {age.total_seconds() / 3600:.0f} h ago"
    return None


def record_full_run(tree: Path) -> None:
    stamps = _read(FULL_RUN_STAMP)
    stamps[_tree_key(tree)] = datetime.now().isoformat(timespec="seconds")
    _write(FULL_RUN_STAMP, stamps)
