#!/usr/bin/env python
"""Diagnose common environment problems before they surprise you.

Read-only: this never installs, upgrades, or kills anything. Each
check prints ok/WARN and, on WARN, the exact command (or manual
step) that fixes it.

Checks:

- Python build freshness. `.python-version` pins a floating minor
  (e.g. "3.15"), so `uv sync` always resolves to *some* build of
  it, but a stale `uv` binary can keep resolving the same old
  prerelease (alpha/beta) indefinitely: it only learns a newer
  build exists when it is updated itself. This compares the active
  interpreter against every build `uv python list --all-versions`
  currently knows about for the pinned minor, and flags it if a
  newer one exists that isn't active.
- (Windows only) Whether a process is currently running from this
  project's `.venv`. An editor's `ruff`/`ty` language server is the
  usual culprit; it holds a Windows file lock that makes `uv sync`
  (and so `make upgrade-python`) fail with "Access is denied"
  trying to remove `.venv\\Scripts`. Not a real problem on POSIX,
  where a process can hold a file open after it's been unlinked.

Usage:
    python tools/doctor.py
"""

import argparse
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYVER = ROOT / ".python-version"
VENV = ROOT / ".venv"

STAGE_ORDER = {"a": 0, "b": 1, "rc": 2, "": 3}
VERSION_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)(a|b|rc)?(\d+)?")


def version_key(v: str) -> tuple[int, int, int, int, int]:
    """Order 'a' < 'b' < 'rc' < final, then by prerelease number."""
    m = VERSION_RE.search(v)
    if not m:
        return (0, 0, 0, -1, 0)
    major, minor, micro, stage, stage_n = m.groups()
    return (
        int(major), int(minor), int(micro),
        STAGE_ORDER.get(stage or "", 3),
        int(stage_n) if stage_n else 0,
    )


def pinned_minor_and_suffix() -> tuple[str, str]:
    """Return (minor, suffix): ('3.15', '') or ('3.15', '+gil')."""
    m = re.match(
        r"(\d+\.\d+)(.*)", PYVER.read_text(encoding="utf-8").strip()
    )
    return (m.group(1), m.group(2).strip()) if m else ("", "")


def run(cmd: list[str]) -> str:
    """Run cmd, return combined stdout ('' on any failure)."""
    if shutil.which(cmd[0]) is None:
        return ""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
    except OSError:
        return ""
    return proc.stdout or ""


def check_uv_present() -> tuple[bool, str]:
    out = run(["uv", "--version"])
    if not out:
        return False, "uv not found: https://docs.astral.sh/uv/"
    return True, out.strip().splitlines()[0]


def check_python_freshness() -> tuple[bool, str]:
    minor, suffix = pinned_minor_and_suffix()
    if not minor:
        return False, f"Cannot parse a minor version from {PYVER}"

    active = run(["uv", "run", "python", "--version"])
    active = active.strip().removeprefix("Python ").strip()
    if not active:
        return False, (
            "`uv run python --version` failed; run `uv sync`"
        )

    prefix = f"cpython-{minor}."
    listing = run(["uv", "python", "list", "--all-versions"])
    candidates = []
    for line in listing.splitlines():
        token = line.split()[0] if line.split() else ""
        if not token.startswith(prefix):
            continue
        ver_part = token.removeprefix("cpython-").partition("-")[0]
        if bool(suffix) != ("+" in ver_part):
            continue
        candidates.append(ver_part)

    if not candidates:
        return True, f"{active} (no other {minor} build known)"

    newest = max(candidates, key=version_key)
    if version_key(newest) > version_key(active):
        return False, (
            f"active build is {active}, but uv knows about "
            f"{newest}. A stale uv can keep resolving an old "
            "prerelease forever. Run: make upgrade-tools "
            "&& make upgrade-python"
        )
    return True, f"{active} (newest uv knows of for {minor})"


def check_venv_locks() -> tuple[bool, str]:
    if platform.system() != "Windows":
        return True, "not checked (Windows-only failure mode)"
    if not VENV.exists():
        return True, "no .venv yet"

    # `uv run python` launches .venv\Scripts\python.exe as a
    # trampoline that spawns the real interpreter as a child, so
    # this script's own invocation always has a
    # .venv\Scripts\python.exe *ancestor* alive for its whole run.
    # Walk up from our own pid and exclude that chain, or every run
    # would flag itself as the lock.
    ps_cmd = f"""
$ancestors = @()
$cur = {os.getpid()}
for ($i = 0; $i -lt 10 -and $cur -ne 0; $i++) {{
    $ancestors += $cur
    $p = Get-CimInstance Win32_Process `
        -Filter "ProcessId=$cur" -ErrorAction SilentlyContinue
    if (-not $p) {{ break }}
    $cur = $p.ParentProcessId
}}
Get-CimInstance Win32_Process | Where-Object {{
    $_.ExecutablePath -like '*{VENV}\\*' -and
    ($ancestors -notcontains $_.ProcessId)
}} | ForEach-Object {{
    "$($_.ProcessId) $($_.Name) $($_.ExecutablePath)"
}}
"""
    out = run(["powershell", "-NoProfile", "-Command", ps_cmd])
    hits = [line.strip() for line in out.splitlines() if line.strip()]
    if not hits:
        return True, "nothing is running from .venv"
    return False, (
        "running from .venv, will lock it on the next upgrade: "
        + "; ".join(hits)
        + ". Close your editor (its ruff/ty language server is the "
        "usual culprit) or stop the process, then retry."
    )


CHECKS = [
    ("uv on PATH", check_uv_present),
    ("Python build freshness", check_python_freshness),
    ("Nothing locking .venv", check_venv_locks),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.parse_args(argv)

    width = max(len(name) for name, _ in CHECKS)
    failed = []
    for name, check in CHECKS:
        ok, detail = check()
        label = "ok  " if ok else "WARN"
        print(f"  {name:<{width}}  {label}  {detail}")
        if not ok:
            failed.append(name)

    print()
    if failed:
        names = ", ".join(failed)
        print(f"{len(failed)} check(s) need attention: {names}")
        return 1
    print("Environment looks healthy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
