#!/usr/bin/env python
"""List, and optionally bump, the tool versions the prose pins.

Some sentences in the book and in the project's instructions make a
claim about the type checker and name the version on which it was last
checked: "under `ty` 0.0.87 both orders infer the same result type."
`tip tools-upgrade` moves `ty` through uv, but nothing rewrites those
numbers, so after an upgrade each pin keeps asserting a version nobody
has run. This tool finds every pin, compares it with the installed
version, and reports the stale ones. With `--write` it rewrites them.

A pin is a code span naming the tool, one space, and a three-part
version, as in `` `ty` 0.0.87 ``. The tool matches only the version, and
only in these files: every chapter, every chapter's `README.md` under
`Solutions/`, `CLAUDE.md`, `tools/CLAUDE.md`, `AGENTS.md`, and the two
copies of the coding-style skill (which `tip skill-copies` requires to
stay identical, so one run bumps both). Review files, `archive/`, and
the tool-upgrade skill record history and keep their old versions.

A historical sentence in a scanned file ("they matched on 2026-09-13,
both `ty` 0.0.78") must keep its version. List it in
`tools/data/version_pins_keep.txt`, one `path:substring` per line, where
the path is relative to the repo root with forward slashes and the
substring is text on the line. A matching line is reported as KEEP and
the tool never rewrites it. An entry that matches no line is an error,
so the list cannot rot after the sentence changes.

The installed version comes from `uv run <tool> --version`. The `TOOLS`
table maps each tool name to that command and to the regex for its
pins, so a second tool is one more row.

The report is a to-do list, not a gate: the exit status is 0 whether or
not pins are stale, and 2 on an error (the tool is missing, or a keep
entry matches nothing). Run `--write` after the probes in the
tool-upgrade skill pass, because a bumped pin asserts that someone
re-checked the claim on that version.

Usage:
    python -m tools.version_pins             # stale pins only
    python -m tools.version_pins --all       # current and kept pins too
    python -m tools.version_pins --write     # bump the stale pins
"""

import argparse
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT
from tools.repo import (
    run_capture,
    solutions_files,
    write_text_lf,
)

KEEP_FILE: Final = DATA_DIR / "version_pins_keep.txt"

EXTRA_FILES: Final = [
    "CLAUDE.md",
    "tools/CLAUDE.md",
    "AGENTS.md",
    "thinking-in-python-skill.md",
    ".claude/skills/thinking-in-python/SKILL.md",
]


@dataclass(frozen=True)
class Tool:
    """How to read a tool's installed version and recognize its pins."""
    command: list[str]
    version: re.Pattern[str]  # group 1 of the command's output
    pin: re.Pattern[str]  # group 1 of a pin in prose


TOOLS: Final = {
    "ty": Tool(
        command=["uv", "run", "ty", "--version"],
        version=re.compile(r"\bty (\d+\.\d+\.\d+)"),
        pin=re.compile(r"`ty` (\d+\.\d+\.\d+)"),
    ),
}


@dataclass(frozen=True)
class Pin:
    path: Path
    line: int
    tool: str
    found: str
    installed: str
    text: str
    kept: bool

    @property
    def stale(self) -> bool:
        return self.found != self.installed and not self.kept


@dataclass(frozen=True)
class KeepEntry:
    path: str
    substring: str


def scanned_files(root: Path = ROOT) -> list[Path]:
    """Every existing file whose pins this tool manages."""
    files = [
        *sorted((root / "Chapters").glob("*.md")),
        *solutions_files(root / "Solutions"),
        *(root / name for name in EXTRA_FILES),
    ]
    return [p for p in files if p.is_file()]


def parse_keeps(text: str) -> list[KeepEntry]:
    """Entries from the keep file's text; `#` lines and blanks are skipped."""
    entries: list[KeepEntry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        path, _, substring = line.partition(":")
        entries.append(KeepEntry(path.strip(), substring.strip()))
    return entries


def load_keeps(path: Path = KEEP_FILE) -> list[KeepEntry]:
    if not path.is_file():
        return []
    return parse_keeps(path.read_text(encoding="utf-8"))


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def keep_substrings(path: Path, root: Path,
                    keeps: Sequence[KeepEntry]) -> list[str]:
    """The keep substrings that apply to `path`."""
    rel = _rel(path, root)
    return [k.substring for k in keeps if k.path == rel]


def unmatched_keeps(root: Path, keeps: Sequence[KeepEntry]) -> list[KeepEntry]:
    """Entries whose file is missing or has no line with the substring."""
    bad: list[KeepEntry] = []
    for k in keeps:
        path = root / k.path
        if not path.is_file() or not any(
            k.substring in line
            for line in path.read_text(encoding="utf-8").splitlines()
        ):
            bad.append(k)
    return bad


def find_pins(
    paths: Sequence[Path], version: str, *, root: Path = ROOT,
    keeps: Sequence[KeepEntry] = (), tool: str = "ty",
) -> list[Pin]:
    """Every pin of `tool` in `paths`, marked kept or stale against `version`."""
    pattern = TOOLS[tool].pin
    pins: list[Pin] = []
    for path in paths:
        kept_text = keep_substrings(path, root, keeps)
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, 1):
            kept = any(s in line for s in kept_text)
            for m in pattern.finditer(line):
                pins.append(Pin(path, lineno, tool, m.group(1), version,
                                line, kept))
    return pins


def rewrite(path: Path, version: str, *, keep: Sequence[str] = (),
            tool: str = "ty") -> int:
    """Set each stale pin of `tool` in `path` to `version`; return the count.

    A line containing any `keep` substring stays as it is. Line endings
    stay as they are, and the file is written (as UTF-8, LF for new
    text) only when a pin changed.
    """
    pattern = TOOLS[tool].pin
    count = 0

    def bump(m: re.Match[str]) -> str:
        nonlocal count
        if m.group(1) == version:
            return m.group(0)
        count += 1
        return m.group(0)[: m.start(1) - m.start(0)] + version

    with path.open(encoding="utf-8", newline="") as f:
        lines = f.read().splitlines(keepends=True)
    out = [
        line if any(s in line for s in keep) else pattern.sub(bump, line)
        for line in lines
    ]
    if count:
        write_text_lf(path, "".join(out))
    return count


def installed_version(tool: str) -> str | None:
    spec = TOOLS[tool]
    result = run_capture(spec.command, timeout=120)
    if result is None:
        return None
    m = spec.version.search(result[0])
    return m.group(1) if m else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--write", action="store_true",
                    help="rewrite each stale pin to the installed version")
    ap.add_argument("--all", action="store_true",
                    help="also list current and kept pins")
    args = ap.parse_args(argv)

    keeps = load_keeps()
    bad = unmatched_keeps(ROOT, keeps)
    for k in bad:
        print(f"error: keep entry matches no line: {k.path}:{k.substring}",
              file=sys.stderr)
    paths = scanned_files()
    stale = current = kept = 0
    failed = bool(bad)
    for tool in TOOLS:
        version = installed_version(tool)
        if version is None:
            print(f"error: cannot read the installed {tool} version",
                  file=sys.stderr)
            failed = True
            continue
        for pin in find_pins(paths, version, root=ROOT, keeps=keeps,
                             tool=tool):
            where = f"{_rel(pin.path, ROOT)}:{pin.line}"
            if pin.kept:
                kept += 1
                label = "KEEP"
            elif pin.stale:
                stale += 1
                label = f"{tool} {pin.found} -> {version}"
            else:
                current += 1
                label = f"{tool} {pin.found} (current)"
            if pin.stale or args.all:
                print(f"{where}: {label}\n    {pin.text.strip()}")
        if args.write and not failed:
            for path in paths:
                n = rewrite(path, version, tool=tool,
                            keep=keep_substrings(path, ROOT, keeps))
                if n:
                    print(f"wrote {_rel(path, ROOT)}: {n} pin(s) -> "
                          f"{tool} {version}")
    print(f"{stale} stale, {current} current, {kept} kept")
    return 2 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
