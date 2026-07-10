#!/usr/bin/env python3
"""Check (or fix) line endings in tracked text files.

Reads ``git ls-files --eol`` so it respects ``.gitattributes``: files git
treats as binary are skipped, and only text files are inspected. By default it
reports any tracked text file whose working-tree copy contains CRLF (or mixed)
endings and exits non-zero, which makes it a CI gate. The committed blobs are
already LF because of ``.gitattributes``; this catches a working tree that has
drifted (an editor writing CRLF on Windows, say) before it becomes confusing.

Pass --fix to rewrite the offenders to LF in place.

Usage:
    python tools/check_line_endings.py          # check, exit 1 on CRLF
    python tools/check_line_endings.py --fix     # convert offenders to LF
"""

import argparse
import subprocess

from tools_config import ROOT


def offenders() -> list[str]:
    """Tracked text files whose working tree has CRLF or mixed endings."""
    out = subprocess.run(
        ["git", "ls-files", "--eol"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    bad: list[str] = []
    for line in out.splitlines():
        # Format: "i/lf    w/crlf  attr/text=auto eol=lf \t path"
        info, _, path = line.partition("\t")
        path = path.strip()
        if not path:
            continue
        fields = info.split()
        worktree = next((f for f in fields if f.startswith("w/")), "")
        attrs = [f for f in fields if f.startswith("attr/")]
        if any("binary" in a for a in attrs) or worktree == "w/-text":
            continue  # git treats it as binary
        if worktree in ("w/crlf", "w/mixed"):
            bad.append(path)
    return bad


def fix(paths: list[str]) -> None:
    for p in paths:
        fp = ROOT / p
        data = fp.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        fp.write_bytes(data)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite offending files to LF in place")
    args = ap.parse_args(argv)

    bad = offenders()
    if not bad:
        print("Line endings OK: every tracked text file is LF.")
        return 0
    if args.fix:
        fix(bad)
        print(f"Converted {len(bad)} file(s) to LF:")
        for p in bad:
            print(f"  {p}")
        return 0
    print(f"{len(bad)} tracked text file(s) have CRLF or mixed line endings:")
    for p in bad:
        print(f"  {p}")
    print("\nFix with: python tools/check_line_endings.py --fix")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
