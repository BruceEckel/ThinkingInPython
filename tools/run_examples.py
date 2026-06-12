#!/usr/bin/env python3
"""Run extracted Python examples and report which ones fail.

Walks a tree of extracted examples (default ``ExtractedExamples/``, written by
``extract_examples.py --write``) and executes every ``.py`` file under it with
the current interpreter. Each file runs with its own directory as the working
directory, so the relative data paths in the examples (``../mouse/Moves.txt``)
resolve the way the book assumes.

Some examples cannot run unattended: they open GUI windows, read interactive
input, or loop forever. Exclude those two ways:

  * inline marker: a line ``# extract: no-run`` anywhere in the file, or
  * skip list: glob patterns (one per line, ``#`` comments allowed) in
    ``tools/norun.txt``.

Exit status is non-zero if any non-skipped example fails or times out.

Usage:
    python tools/run_examples.py                 # run everything
    python tools/run_examples.py StateMachine    # only that subtree
    python tools/run_examples.py --timeout 20
"""
from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TREE = ROOT / "ExtractedExamples"
NORUN_FILE = ROOT / "tools" / "norun.txt"
INLINE_MARKER = "# extract: no-run"


def load_skips() -> list[str]:
    if not NORUN_FILE.exists():
        return []
    out = []
    for line in NORUN_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line.replace("\\", "/"))
    return out


def is_skipped(rel: str, text: str, skips: list[str]) -> bool:
    if INLINE_MARKER in text:
        return True
    return any(fnmatch.fnmatch(rel, pat) for pat in skips)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subtree", nargs="?", default="",
                    help="only run examples whose path contains this substring")
    ap.add_argument("--tree", type=Path, default=DEFAULT_TREE,
                    help=f"root of extracted examples (default: {DEFAULT_TREE.name})")
    ap.add_argument("--timeout", type=float, default=15.0,
                    help="seconds before an example is killed (default: 15)")
    args = ap.parse_args(argv)

    if not args.tree.exists():
        print(f"No example tree at {args.tree}. "
              "Run: python tools/extract_examples.py --write")
        return 2

    skips = load_skips()
    py_files = sorted(args.tree.rglob("*.py"))
    passed: list[str] = []
    failed: list[tuple[str, str]] = []
    skipped: list[str] = []
    timed_out: list[str] = []

    for f in py_files:
        rel = f.relative_to(args.tree).as_posix()
        if args.subtree and args.subtree not in rel:
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if is_skipped(rel, text, skips):
            skipped.append(rel)
            continue
        try:
            proc = subprocess.run(
                [sys.executable, f.name],
                cwd=f.parent,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            timed_out.append(rel)
            continue
        if proc.returncode == 0:
            passed.append(rel)
        else:
            tail = (proc.stderr.strip().splitlines() or ["(no stderr)"])[-1]
            failed.append((rel, tail))

    print(f"\nPassed:   {len(passed)}")
    print(f"Skipped:  {len(skipped)}")
    print(f"Timeout:  {len(timed_out)}")
    print(f"Failed:   {len(failed)}")
    if timed_out:
        print("\nTimed out (consider adding to tools/norun.txt):")
        for rel in timed_out:
            print(f"  T {rel}")
    if failed:
        print("\nFailures (last stderr line):")
        for rel, tail in failed:
            print(f"  F {rel}\n      {tail}")
    return 1 if failed or timed_out else 0


if __name__ == "__main__":
    raise SystemExit(main())
