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

Most examples fail today because of unmodernized Python 2 code (Phase 2 of the
publishing plan). A run that is red on every one of those is useless as a gate,
so this script also supports a *baseline* of currently-known failures:

  * ``--write-baseline`` records the set of failing/timing-out examples to
    ``tools/examples_baseline.txt``.
  * ``--baseline`` runs, then fails only on *new* breakage (an example that
    fails but is not in the baseline). Examples that used to fail and now pass
    are reported as good news; trim them from the baseline as Phase 2 lands.

That makes CI green today and red the moment a change breaks something that
currently works.

Usage:
    python tools/run_examples.py                 # run everything (all cores)
    python tools/run_examples.py StateMachine    # only that subtree
    python tools/run_examples.py --timeout 20
    python tools/run_examples.py -j 1            # run serially
    python tools/run_examples.py -j 8            # run 8 examples at once
    python tools/run_examples.py --baseline      # fail only on regressions
    python tools/run_examples.py --write-baseline
"""

import argparse
import fnmatch
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TREE = ROOT / "ExtractedExamples"
NORUN_FILE = ROOT / "tools" / "norun.txt"
BASELINE_FILE = ROOT / "tools" / "examples_baseline.txt"
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


def is_pytest_file(name: str) -> bool:
    """pytest owns these (run via `pytest`, not as standalone scripts)."""
    return name == "conftest.py" or (name.startswith("test_")
                                     and name.endswith(".py"))


def is_skipped(rel: str, text: str, skips: list[str]) -> bool:
    if INLINE_MARKER in text:
        return True
    return any(fnmatch.fnmatch(rel, pat) for pat in skips)


def load_baseline() -> set[str]:
    if not BASELINE_FILE.exists():
        return set()
    out: set[str] = set()
    for line in BASELINE_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line.replace("\\", "/"))
    return out


def write_baseline(failing: list[str]) -> None:
    header = (
        "# Examples known to fail or time out right now (Phase 2 backlog).\n"
        "# Regenerate with: python tools/run_examples.py --write-baseline\n"
        "# CI uses this with --baseline to fail only on NEW breakage.\n"
        "# One forward-slash relative path per line.\n\n"
    )
    body = "".join(f"{rel}\n" for rel in sorted(failing))
    BASELINE_FILE.write_text(header + body, encoding="utf-8")


def jobs_arg(value: str) -> int:
    """Parse --jobs: a positive int, or "auto" for all available cores."""
    if value == "auto":
        return os.process_cpu_count() or 1
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("jobs must be a positive int or 'auto'")
    if n < 1:
        raise argparse.ArgumentTypeError("jobs must be at least 1")
    return n


def run_one(path: Path, rel: str, timeout: float) -> tuple[str, str, str]:
    """Execute one example as a subprocess. Returns (status, rel, last_stderr).

    status is "passed", "failed", or "timeout". Examples are independent
    subprocesses with their own cwd, so this is safe to call concurrently.
    """
    try:
        proc = subprocess.run(
            [sys.executable, path.name],
            cwd=path.parent,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ("timeout", rel, "")
    if proc.returncode == 0:
        return ("passed", rel, "")
    tail = (proc.stderr.strip().splitlines() or ["(no stderr)"])[-1]
    return ("failed", rel, tail)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("subtree", nargs="?", default="",
                    help="only run examples whose path contains this substring")
    ap.add_argument("--tree", type=Path, default=DEFAULT_TREE,
                    help=f"root of extracted examples (default: {DEFAULT_TREE.name})")
    ap.add_argument("--timeout", type=float, default=15.0,
                    help="seconds before an example is killed (default: 15)")
    ap.add_argument("-j", "--jobs", type=jobs_arg, default="auto", metavar="N",
                    help="examples to run concurrently: an int or 'auto' "
                         "for all cores (default: auto). Use -j 1 for serial.")
    ap.add_argument("--baseline", action="store_true",
                    help="fail only on examples not already in the baseline")
    ap.add_argument("--write-baseline", action="store_true",
                    help="record current failures as the baseline and exit 0")
    args = ap.parse_args(argv)

    if not args.tree.exists():
        print(f"No example tree at {args.tree}. "
              "Run: python tools/extract_examples.py --write")
        return 2

    skips = load_skips()
    py_files = sorted(args.tree.rglob("*.py"))
    passed: list[str] = []
    failed: list[tuple[str, str]] = []
    pytest_files: list[str] = []
    unattended: list[str] = []
    timed_out: list[str] = []

    to_run: list[tuple[Path, str]] = []
    for f in py_files:
        rel = f.relative_to(args.tree).as_posix()
        if args.subtree and args.subtree not in rel:
            continue
        if is_pytest_file(f.name):
            pytest_files.append(rel)  # run by `pytest`, not as a script
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        if is_skipped(rel, text, skips):
            unattended.append(rel)  # GUI/interactive/infinite-loop: norun.txt
            continue
        to_run.append((f, rel))

    # Each example is its own subprocess, so threads parallelize cleanly: the
    # work happens in child processes, not under the GIL.
    jobs = max(1, args.jobs)
    if jobs == 1:
        results = [run_one(f, rel, args.timeout) for f, rel in to_run]
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(
                lambda fr: run_one(fr[0], fr[1], args.timeout), to_run))

    for status, rel, tail in results:
        if status == "passed":
            passed.append(rel)
        elif status == "timeout":
            timed_out.append(rel)
        else:
            failed.append((rel, tail))
    passed.sort()
    timed_out.sort()
    failed.sort()

    print()
    for label, count in (
        ("Passed:", len(passed)),
        ("Tested via pytest:", len(pytest_files)),
        ("Can't run unattended:", len(unattended)),
        ("Timeout:", len(timed_out)),
        ("Failed:", len(failed)),
    ):
        print(f"{label:<22}{count}")
    if timed_out:
        print("\nTimed out (consider adding to tools/norun.txt):")
        for rel in timed_out:
            print(f"  T {rel}")
    if failed:
        print("\nFailures (last stderr line):")
        for rel, tail in failed:
            print(f"  F {rel}\n      {tail}")

    failing = [rel for rel, _ in failed] + timed_out

    if args.write_baseline:
        write_baseline(failing)
        print(f"\nWrote {len(failing)} entries to {BASELINE_FILE.name}.")
        return 0

    if args.baseline:
        baseline = load_baseline()
        current = set(failing)
        regressions = sorted(current - baseline)
        fixed = sorted(baseline - current)
        if fixed:
            print(f"\n{len(fixed)} example(s) in the baseline now pass. "
                  "Trim them from tools/examples_baseline.txt:")
            for rel in fixed:
                print(f"  + {rel}")
        if regressions:
            print(f"\n{len(regressions)} NEW failure(s) not in the baseline:")
            for rel in regressions:
                print(f"  ! {rel}")
            return 1
        print("\nNo new failures against the baseline.")
        return 0

    return 1 if failed or timed_out else 0


if __name__ == "__main__":
    raise SystemExit(main())
