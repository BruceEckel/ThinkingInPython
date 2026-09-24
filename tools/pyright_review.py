#!/usr/bin/env python3
"""Diff pyright's diagnostics over both trees against a baseline.

`ty` is the book's gated type checker. Pyright is a second opinion,
and its value is the list of places where the two disagree: a listing
that `ty` accepts and pyright rejects is either a checker limitation,
a deliberate runtime-failure demo, or a prose claim about "the type
checker" that holds for `ty` alone (the 2026-09-14 sweep found
fourteen of those). That list only matters when it changes, so this
tool keeps it in `tools/data/pyright_baseline.txt` and prints the
delta:

    NEW   a diagnostic the baseline does not have: a fresh
          disagreement, usually from an edited listing or a stricter
          pyright release.
    GONE  a baseline entry that no longer fires: pyright caught up
          (the PEP 798 parse errors will leave this way), or the
          listing changed, or `ty` now reports it too and the listing
          gained an ignore that silences both.

Entries are `path<TAB>rule<TAB>message`, with the path relative to
the repo root and the line number dropped, so an edit above a
diagnostic does not churn the baseline. Repeated diagnostics (the
same message three times in one file) are kept as repeated lines and
compared as counts. Informational output (`reveal_type()`) is
ignored.

Nothing here is in `verify`, `gate`, `sweep`, or `ci`, and no listing
carries a pyright suppression comment: every accepted disagreement
lives in the baseline instead. Exit status is nonzero only when NEW
is non-empty, so a script can notice a fresh disagreement; GONE is
news, not a failure.

Usage:
    uv run python -m tools.pyright_review            # the delta
    uv run python -m tools.pyright_review --accept   # rewrite it

Both trees must be extracted first (`make pyright-review` does that).
Pyright is a pinned dev dependency, so `make tools-upgrade` moving it
is the usual reason for a delta, and reading that delta is the
review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from tools.config import DATA_DIR, EXAMPLES_TREE, ROOT

SOLUTIONS_TREE = ROOT / "build" / "solutions"
BASELINE = DATA_DIR / "pyright_baseline.txt"
TREES = (EXAMPLES_TREE, SOLUTIONS_TREE)
HEADER = (
    "# Pyright diagnostics the book accepts as disagreements with\n"
    "# ty. path<TAB>rule<TAB>message, one per occurrence, sorted.\n"
    "# Rewritten by `make pyright-accept`; read the delta with\n"
    "# `make pyright-review` before accepting.\n"
    "# See tools/pyright_review.py.\n"
)


def run_pyright() -> list[dict[str, object]]:
    """Run pyright over both trees; return its generalDiagnostics."""
    for tree in TREES:
        if not tree.is_dir():
            sys.exit(
                f"{tree} is missing; "
                "run make extract"
            )
    cmd = [
        sys.executable, "-m", "pyright", "--outputjson",
        *map(str, TREES),
    ]
    proc = subprocess.run(
        cmd, capture_output=True, text=True, cwd=ROOT
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit(
            "pyright produced no JSON:\n"
            f"{proc.stdout}\n{proc.stderr}"
        )
    diagnostics: list[dict[str, object]] = data["generalDiagnostics"]
    return diagnostics


def normalize(diag: dict[str, object]) -> str | None:
    """One baseline line for a diagnostic; None for informational."""
    if diag["severity"] == "information":
        return None
    file = Path(str(diag["file"])).resolve()
    path = file.relative_to(ROOT).as_posix()
    rule = str(diag.get("rule") or "syntax")
    message = " ".join(str(diag["message"]).split())
    return f"{path}\t{rule}\t{message}"


def current() -> Counter[str]:
    lines = (normalize(d) for d in run_pyright())
    return Counter(line for line in lines if line is not None)


def load_baseline() -> Counter[str]:
    if not BASELINE.exists():
        return Counter()
    text = BASELINE.read_text(encoding="utf-8")
    return Counter(
        line for line in text.splitlines()
        if line and not line.startswith("#")
    )


def write_baseline(entries: Counter[str]) -> None:
    body = "".join(f"{line}\n" for line in sorted(entries.elements()))
    BASELINE.write_text(HEADER + body, encoding="utf-8", newline="\n")


def report(label: str, entries: Counter[str]) -> None:
    for line in sorted(entries.elements()):
        path, rule, message = line.split("\t", 2)
        print(f"{label}  {path}  [{rule}]  {message}")


def main() -> int:
    summary = (__doc__ or "").split("\n\n")[0]
    ap = argparse.ArgumentParser(description=summary)
    ap.add_argument(
        "--accept", action="store_true",
        help="rewrite the baseline from the current run",
    )
    args = ap.parse_args()
    now = current()
    if args.accept:
        write_baseline(now)
        print(
            f"Baseline written: {sum(now.values())} entries "
            f"in {BASELINE}"
        )
        return 0
    before = load_baseline()
    new = now - before
    gone = before - now
    report("NEW ", new)
    report("GONE", gone)
    print(
        f"pyright: {sum(now.values())} diagnostics, "
        f"{sum(new.values())} new, {sum(gone.values())} gone, "
        f"baseline {sum(before.values())}"
    )
    if new:
        print("Read each NEW line, then `make pyright-accept`.")
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())
