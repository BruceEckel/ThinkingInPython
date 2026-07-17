#!/usr/bin/env python3
"""Smoke-test every documented `make` target: run it, confirm it exits 0.

The target list comes straight from the Makefile (via make_help.entries),
so a target added there is picked up here automatically, with no separate
list to keep in sync. A handful of targets never run, regardless of tier:

  * upgrade-tools, upgrade-python -- mutate the real dev environment and
    hit the network (winget/brew, uv self update, a new Python build).
    This project's own convention is to never auto-run these.
  * serve, local -- start an HTTP server that runs until Ctrl+C; there is
    nothing for a subprocess call to wait on.
  * verify-targets -- the target that runs this script; testing it would
    recurse.

Most targets are read-only or safely idempotent (extract, sync, and the
various check-* targets rewrite a tracked file only if it is genuinely out
of sync, which it should not be if the gate already passes) and run
directly against this working tree.

A handful of targets bake --fix/--write/--add/--update into their recipe
(reflow, spell-add, fix-imports, fix-listings, fix-comment-periods,
fix-comment-caps, fix-comment-spacing, output, solutions-output, and all,
which chains most of the others): reflow alone would reformat most of
the book's prose on every run, since it is not covered by any gate. Those
run inside a disposable `git worktree` checked out at HEAD instead, so
this working tree is never touched. That worktree reflects the last
commit, not any uncommitted changes, so it tests each target's own wiring
rather than whether running it right now would leave your draft clean.

Every target's combined stdout/stderr is saved to
build/target_test_logs/<target>.log for inspection after the run.

Usage:
    python tools/verify_targets.py                  # every target
    python tools/verify_targets.py --only gate ci    # just these targets
    python tools/verify_targets.py --timeout 60      # per-target timeout
"""

import argparse
import contextlib
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from make_help import MAKEFILE, entries
from tools_config import ROOT

LOG_DIR = ROOT / "build" / "target_test_logs"
DEFAULT_TIMEOUT = 300.0

# name -> why this target never runs, in any tier.
EXCLUDED: dict[str, str] = {
    "upgrade-tools": "mutates the real dev environment and hits the network",
    "upgrade-python": "mutates the real dev environment and hits the network",
    "serve": "starts a server that runs forever",
    "local": "starts a server that runs forever",
    "verify-targets": "this is the target that runs this script",
}

# Targets whose recipe rewrites tracked files unconditionally: run these in
# a disposable worktree rather than this working tree.
WORKTREE_TARGETS: frozenset[str] = frozenset({
    "all", "reflow", "spell-add", "fix-imports", "fix-listings",
    "fix-comment-periods", "fix-comment-caps", "fix-comment-spacing",
    "output", "solutions-output",
})


@dataclass
class Result:
    name: str
    ok: bool
    seconds: float
    summary: str  # empty on success; "exit N" or "timed out" on failure


def documented_targets() -> list[str]:
    """Every target with a `## text` doc comment, in Makefile order."""
    text = MAKEFILE.read_text(encoding="utf-8")
    return [name for name, _ in entries(text) if name is not None]


def run_target(name: str, cwd: Path, timeout: float) -> Result:
    """Run `make <name>` in `cwd`, logging its output. Returns a Result."""
    # A parent VIRTUAL_ENV pointing at this repo's .venv makes uv print a
    # harmless but noisy mismatch warning when cwd is a different checkout
    # (the disposable worktree); drop it so uv resolves cwd's own venv.
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    start = time.monotonic()
    try:
        proc = subprocess.run(
            ["make", name], cwd=cwd, capture_output=True, text=True,
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
        return Result(name, False, seconds, f"exit {proc.returncode}")
    return Result(name, True, seconds, "")


def _write_log(name: str, output: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    (LOG_DIR / f"{name}.log").write_text(output, encoding="utf-8")


def log_tail(name: str, lines: int = 25) -> str:
    text = (LOG_DIR / f"{name}.log").read_text(encoding="utf-8")
    return "\n".join(text.splitlines()[-lines:])


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
        print("ok" if result.ok else f"FAILED ({result.summary})",
              f"[{result.seconds:.1f}s]")

    if worktree:
        print(f"\nSetting up a disposable worktree for "
              f"{len(worktree)} mutating target(s)...")
        with disposable_worktree() as wt:
            for name in worktree:
                print(f"-> {name} (worktree) ...", end=" ", flush=True)
                result = run_target(name, wt, args.timeout)
                results.append(result)
                print("ok" if result.ok else f"FAILED ({result.summary})",
                      f"[{result.seconds:.1f}s]")

    if {"clean-examples", "clean-solutions", "clean-site"} & set(direct):
        # Those targets are real, tested rmtree calls; leaving build/ empty
        # afterward would be a surprising side effect of running this sweep,
        # so put back what a normal `make ci` run leaves behind.
        print("\nRestoring build/ artifacts wiped by the clean-* targets...")
        subprocess.run(["make", "extract", "solutions-extract", "site"],
                        cwd=ROOT, check=False)

    if skipped:
        print("\nNever run (see the module docstring for why):")
        for name in skipped:
            print(f"  {name}: {EXCLUDED[name]}")

    failed = [r for r in results if not r.ok]
    print(f"\n{len(results)} target(s) tested, {len(failed)} failed, "
          f"{len(skipped)} skipped.")

    if failed:
        print("\nFailed targets:")
        for r in failed:
            print(f"\n{r.name} ({r.summary}):")
            print(log_tail(r.name))
            print(f"  (full log: build/target_test_logs/{r.name}.log)")
        return 1

    print("Every make target passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
