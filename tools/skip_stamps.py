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
- **Refreshing the markers of a chapter nothing touched** (``tip output``,
  15-25 s for the book). ``validate_output --changed-only`` skips a
  Markdown file whose digest matches the one recorded when its markers
  last passed. The digest covers the file, the tree's ``utils/`` helpers
  (every listing can import them), and ``tools_digest()`` (the checker,
  ``timing.txt``, ``norun.txt``, the locked dependencies), plus
  ``.python-version``. Nothing else can change a listing's output: the
  build trees come from the Markdown alone, and no listing reads another
  chapter's directory. An edit to one chapter then refreshes that
  chapter. A marker the refresh rewrites changes the file, so the next
  run refreshes it once more and then settles.

Setting ``TIP_FULL=1`` in the environment disables every shortcut. ``tip
ci``, ``tip release``, and ``tip everything`` set it; ``tip gate
RUN=full`` sets it for one gate; ``tip run`` and ``tip tools-test``
always do the full work, and a passing full run refreshes its stamp.
Every pass records its stamp, shortcut or not.
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
MARKER_STAMP = BUILD_DIR / "marker-stamp.json"
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


def marker_context(tree: Path, utils: Path) -> str:
    """What every listing in `tree` depends on beyond its own Markdown."""
    h = hashlib.sha256(tools_digest().encode())
    version = ROOT / ".python-version"
    if version.is_file():
        h.update(version.read_bytes())
    h.update(_tree_key(tree).encode())
    if utils.is_dir():
        for path in sorted(utils.rglob("*.py")):
            h.update(path.name.encode() + b"\0" + path.read_bytes())
    return h.hexdigest()


def marker_digest(md: Path, context: str) -> str:
    return hashlib.sha256(context.encode() + md.read_bytes()).hexdigest()


def _marker_key(md: Path) -> str | None:
    """The book-relative key, or None for a file outside the repo (a
    test's temporary Markdown), which is never stamped."""
    resolved = md.resolve()
    if not resolved.is_relative_to(ROOT):
        return None
    return resolved.relative_to(ROOT).as_posix()


def markers_current(md: Path, context: str) -> bool:
    key = _marker_key(md)
    return (key is not None
            and _read(MARKER_STAMP).get(key) == marker_digest(md, context))


def record_markers(passed: list[Path], context: str) -> None:
    keyed = [(key, md) for md in passed
             if (key := _marker_key(md)) is not None]
    if not keyed:
        return
    stamps = _read(MARKER_STAMP)
    for key, md in keyed:
        stamps[key] = marker_digest(md, context)
    _write(MARKER_STAMP, stamps)
