#!/usr/bin/env python
"""Fail the build if any banned phrase appears in the book.

Reads phrases from `tools/banned_phrases.txt` (one per line) and searches every
`Markdown/*.md` file, prose and code alike, for each as a literal,
case-sensitive substring. Every occurrence is reported as `path:line:col`, and
a non-zero exit makes it a gate. Use it to retire constructs the book has moved
past, such as `from __future__ import annotations` (unnecessary on Python 3.14).

In the phrases file, blank lines and lines starting with `#` are ignored, so you
can group and explain the entries.

Usage:
    python tools/banned_phrases.py                 # scan Markdown/
    python tools/banned_phrases.py path ...        # scan specific files/dirs
    python tools/banned_phrases.py --phrases FILE  # use another phrases file
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHRASES_FILE = ROOT / "tools" / "banned_phrases.txt"


def load_phrases(path: Path) -> list[str]:
    if not path.exists():
        return []
    phrases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            phrases.append(stripped)
    return phrases


def iter_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        files.extend(sorted(path.glob("*.md")) if path.is_dir() else [path])
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*",
                    help="Markdown files or directories (default: Markdown/)")
    ap.add_argument("--phrases", type=Path, default=PHRASES_FILE,
                    help=f"phrases file (default: {PHRASES_FILE.name})")
    args = ap.parse_args(argv)

    phrases = load_phrases(args.phrases)
    if not phrases:
        print(f"No banned phrases configured in {args.phrases}.")
        return 0

    total = 0
    for path in iter_files(args.paths or ["Markdown"]):
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            for phrase in phrases:
                col = line.find(phrase)
                while col != -1:
                    print(f'{path}:{lineno}:{col + 1}: '
                          f'banned phrase: "{phrase}"')
                    total += 1
                    col = line.find(phrase, col + 1)

    if total:
        print(f"\n{total} banned phrase occurrence(s). "
              "Remove them or edit tools/banned_phrases.txt.")
        return 1
    print("No banned phrases found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
