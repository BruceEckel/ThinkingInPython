#!/usr/bin/env python3
"""Smoke-test every documented `tip` task: run it, confirm it exits 0.

The target list comes straight from tools/tasks.py (via tip_help.entries),
so a target added there is picked up here automatically, with no separate
list to keep in sync. A handful of targets never run, regardless of tier:

  * tools-upgrade, python-upgrade -- mutate the real dev environment and
    hit the network (winget/brew, uv self update, a new Python build).
    This project's own convention is to never auto-run these.
  * serve, local -- start an HTTP server that runs until Ctrl+C; there is
    nothing for a subprocess call to wait on.
  * verify-targets -- the target that runs this script; testing it would
    recurse.
  * check-ch -- takes a CH= chapter selector and exits with a usage error
    without one; there is no chapter this script could pick for it.
  * pyright -- the raw run over both trees, which prints every
    disagreement with ty (all of them in tools/data/pyright_baseline.txt)
    and exits nonzero by design; pyright-review, which runs here, is
    the check that passes when the baseline is current.

Most targets are read-only or safely idempotent (extract, sync, and the
various check-* targets rewrite a tracked file only if it is genuinely out
of sync, which it should not be if the gate already passes) and run
directly against this working tree.

A handful of targets bake --fix/--write/--add/--update into their recipe
(reflow, spell-add, fix-imports, fix-listings, fix-comment-periods,
fix-comment-caps, fix-comment-spacing, output, and verify, which chains
most of the others): reflow alone would reformat most of the book's
prose on every run, since it is not covered by any gate. Those
run inside a disposable `git worktree` checked out at HEAD instead, so
this working tree is never touched. The clean-* targets run there too,
since they remove build/, which holds this script's own logs. That worktree reflects the last
commit, not any uncommitted changes, so it tests each target's own wiring
rather than whether running it right now would leave your draft clean.

An advisory target reports findings by exiting nonzero, and a crash
exits nonzero too, so its exit code cannot tell a finding from a
crash. `links` is one: a site's bad afternoon would otherwise turn
this run red. For such a target, ADVISORY names the line its script
prints once it has run to completion; a nonzero exit with that line in
the output passes, and the findings are shown as a note in the summary
instead of a failure. A crash, a usage error, or a timeout never prints
the line, so those still fail.

Every target's combined stdout/stderr is saved to
build/target_test_logs/<target>.log for inspection after the run. Each
passing target's time is recorded for the help listing
(build/target_times.json), and the run ends by rewriting
tools/data/target_tiers.txt, the committed tier per target that the
listing falls back on for a target this machine has not run; commit
that file when it changes.

Usage:
    python -m tools.verify_targets                  # every target
    python -m tools.verify_targets --only gate ci    # just these targets
    python -m tools.verify_targets --timeout 60      # per-target timeout
"""

import argparse
import contextlib
import os
import re
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from tools.tip import tip_argv
from tools.tip_help import entries
from tools.config import ROOT
from tools import target_times

LOG_DIR = ROOT / "build" / "target_test_logs"
DEFAULT_TIMEOUT = 300.0

# name -> why this target never runs, in any tier.
EXCLUDED: dict[str, str] = {
    "tools-upgrade": "mutates the real dev environment and hits the network",
    "python-upgrade": "mutates the real dev environment and hits the network",
    "serve": "starts a server that runs forever",
    "local": "starts a server that runs forever",
    "release": "tags the repo and publishes a GitHub release",
    "release-prune": "deletes old GitHub releases",
    "kindle": "opens the Send to Kindle desktop app (a GUI)",
    "figures-open": "opens a browser on the figure gallery",
    "by-hand": "opens every GUI example and waits for a human to close it",
    "preview-check": "needs node, and the network to install jsdom",
    "verify-targets": "this is the target that runs this script",
    "rewrite": "runs headless claude passes that cost tokens and edit prose",
    "check-ch": "needs a CH= chapter selector this smoke test cannot supply",
    "verify-ch": "needs a CH= chapter selector this smoke test cannot supply",
    "pyright": "the raw run prints the baseline disagreements with ty and "
               "exits nonzero by design; pyright-review is the check",
    **{name: "needs a Rust toolchain, which no other task requires"
       for name in ("rust-all", "rust-sync", "rust-build", "rust-test",
                    "rust-clean")},
}

# name -> the completion line an advisory target prints last, whatever
# it found. check_links ends with "88 ok, 1 failing.".
ADVISORY: dict[str, re.Pattern[str]] = {
    "links": re.compile(r"^\d+ ok, \d+ failing\.$", re.MULTILINE),
}

# Targets whose recipe rewrites tracked files unconditionally: run these in
# a disposable worktree rather than this working tree. `cover` is one:
# it regenerates the committed cover JPEGs under resources/static/.
# The clean-* targets belong here too: they rmtree build/, and this
# script's own logs live under build/, so run in this tree they wiped
# every log written before them (make clean was added 2026-08-29, after
# this script) and the final failure report then crashed reading a log
# that no longer existed.
WORKTREE_TARGETS: frozenset[str] = frozenset({
    "verify", "reflow", "spell-add", "fix-imports", "fix-listings",
    "fix-comment-periods", "fix-comment-caps", "fix-comment-spacing",
    "fix-pattern-names", "fix-coupling-panels", "cover",
    "output",
    "clean", "clean-examples", "clean-solutions", "clean-site",
    "clean-epub", "clean-pdf",
})


@dataclass
class Result:
    name: str
    ok: bool
    seconds: float
    summary: str  # empty on success; "exit N" or "timed out" on failure
    note: str = ""  # an advisory target's findings, on a pass


def documented_targets() -> list[str]:
    """Every task in tools/tasks.py, in listing order."""
    return [name for name, _ in entries() if name is not None]


def run_target(name: str, cwd: Path, timeout: float) -> Result:
    """Run `tip <name>` in `cwd`, logging its output. Returns a Result.

    `python -m tools.tip` puts `cwd` first on sys.path, so a run in the
    disposable worktree uses that checkout's tools/ and tasks."""
    # A parent VIRTUAL_ENV pointing at this repo's .venv makes uv print a
    # harmless but noisy mismatch warning when cwd is a different checkout
    # (the disposable worktree); drop it so uv resolves cwd's own venv.
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    start = time.monotonic()
    try:
        proc = subprocess.run(
            tip_argv(name), cwd=cwd, capture_output=True, text=True,
            timeout=timeout, env=env,
        )
    except subprocess.TimeoutExpired as exc:
        seconds = time.monotonic() - start
        # text=True guarantees str output at runtime; the stdlib stub types
        # it as bytes | str | None since it can't see that correlation.
        stdout = cast(str, exc.stdout) if exc.stdout else ""
        stderr = cast(str, exc.stderr) if exc.stderr else ""
        _write_log(name, stdout + stderr)
        return Result(name, False, seconds, f"timed out after {timeout:.0f}s")

    seconds = time.monotonic() - start
    output = proc.stdout + proc.stderr
    _write_log(name, output)
    if proc.returncode != 0:
        done = ADVISORY.get(name)
        if done and (found := done.search(output)):
            return Result(name, True, seconds, "", found.group(0))
        return Result(name, False, seconds, f"exit {proc.returncode}")
    return Result(name, True, seconds, "")


def status(result: Result) -> str:
    if not result.ok:
        return f"FAILED ({result.summary})"
    return f"ok, advisory: {result.note}" if result.note else "ok"


def _write_log(name: str, output: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{name}.log").write_text(output, encoding="utf-8")


# A line that names a failure: Vale's and ty's "error", pytest's
# "FAILED", a Python exception ("KeyError: ..."), or a traceback.
ERROR_LINE = re.compile(r"\berror\b|\bFAILED\b|\w+Error:|^Traceback")
# A line that is only a file path, as Vale prints above its findings.
PATH_HEADER = re.compile(r"^\s*[\w./-]+\.\w+\s*$")


def excerpt(text: str, lines: int = 25, max_errors: int = 15) -> str:
    """The last `lines` lines, preceded by any error lines above them.

    Vale prints its one error among dozens of warnings and ends with a
    summary, so a failure's cause can sit far above the tail. Each error
    line comes with the file path Vale printed over it, since the line
    alone gives only a line and column.
    """
    all_lines = text.splitlines()
    head, tail = all_lines[:-lines], all_lines[-lines:]
    found: list[str] = []
    header = shown = ""
    for line in head:
        if PATH_HEADER.match(line):
            header = line
        elif ERROR_LINE.search(line):
            if header and header != shown:
                found.append(header)
                shown = header
            found.append(line)
    if not found:
        return "\n".join(tail)
    if len(found) > max_errors:
        extra = len(found) - max_errors
        found = found[:max_errors] + [f"  ... {extra} more error line(s)"]
    return "\n".join(["Error lines:", *found, "", "Last lines:", *tail])


def log_tail(name: str, lines: int = 25) -> str:
    text = (LOG_DIR / f"{name}.log").read_text(encoding="utf-8")
    return excerpt(text, lines)


@contextlib.contextmanager
def disposable_worktree():
    """A throwaway `git worktree` checked out at HEAD, removed on exit."""
    base = Path(tempfile.mkdtemp(prefix="tip-worktree-"))
    path = base / "wt"  # git worktree add requires a not-yet-existing path
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(path), "HEAD"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    try:
        yield path
    finally:
        subprocess.run(
            ["git", "worktree", "remove", "--force", str(path)],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )
        shutil.rmtree(base, ignore_errors=True)
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=ROOT, check=False, capture_output=True, text=True,
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        "--only", nargs="+", metavar="TARGET",
        help="test only these targets (still honors exclusions/tiers)",
    )
    ap.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help=f"seconds before a target is killed (default: {DEFAULT_TIMEOUT:.0f})",
    )
    args = ap.parse_args(argv)

    if LOG_DIR.exists():
        shutil.rmtree(LOG_DIR)

    targets = documented_targets()
    if args.only:
        wanted = set(args.only)
        targets = [t for t in targets if t in wanted]

    skipped = [t for t in targets if t in EXCLUDED]
    worktree = [t for t in targets if t in WORKTREE_TARGETS]
    direct = [
        t for t in targets if t not in EXCLUDED and t not in WORKTREE_TARGETS
    ]

    results: list[Result] = []

    for name in direct:
        print(f"-> {name} ...", end=" ", flush=True)
        result = run_target(name, ROOT, args.timeout)
        results.append(result)
        print(status(result), f"[{result.seconds:.1f}s]")

    if worktree:
        print(f"\nSetting up a disposable worktree for "
              f"{len(worktree)} mutating target(s)...")
        with disposable_worktree() as wt:
            for name in worktree:
                print(f"-> {name} (worktree) ...", end=" ", flush=True)
                result = run_target(name, wt, args.timeout)
                results.append(result)
                print(status(result), f"[{result.seconds:.1f}s]")

    if skipped:
        print("\nNever run (see the module docstring for why):")
        for name in skipped:
            print(f"  {name}: {EXCLUDED[name]}")

    failed = [r for r in results if not r.ok]
    print(f"\n{len(results)} target(s) tested, {len(failed)} failed, "
          f"{len(skipped)} skipped.")

    passed = {r.name: r.seconds for r in results if r.ok}
    for name, seconds in passed.items():
        target_times.record(name, seconds)
    if passed:
        target_times.write_baseline(passed)
        print(f"Recorded {len(passed)} timing(s); tiers written to "
              f"{target_times.BASELINE.relative_to(ROOT)}.")

    noted = [r for r in results if r.note]
    if noted:
        print("\nAdvisory findings (not failures):")
        for r in noted:
            print(f"\n{r.name} ({r.note}):")
            print(log_tail(r.name))
            print(f"  (full log: build/target_test_logs/{r.name}.log)")

    if failed:
        print("\nFailed targets:")
        for r in failed:
            print(f"\n{r.name} ({r.summary}):")
            print(log_tail(r.name))
            print(f"  (full log: build/target_test_logs/{r.name}.log)")
        return 1

    print("Every task passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
