#!/usr/bin/env python
"""Normalize inline-comment spacing to two spaces in ```python listings.

An inline comment (code precedes it on the same line) must start exactly two
spaces after the code ends, this book's standard style. A full-line comment
(nothing but the comment on its line) has no code to measure the gap from and
is left alone, and so is a `#:` output marker (always at column 0, never
inline).

It is string-aware (a `#` inside a string is not a comment) and only touches
```python blocks. Any run of whitespace before the `#`, from one space to
many (including a comment deliberately column-aligned with others), collapses
to exactly two spaces; the comment's own text is untouched.

Default mode reports `path:line` and exits non-zero, so it is a gate. Pass
--fix to rewrite the spacing.
"""
import argparse
from pathlib import Path

from tools_pycode import iter_python_blocks, scan_line
from tools_repo import add_paths_arg, md_files, write_text_lf


def _spacing_targets(block: list[str]) -> dict[int, str]:
    """Map block-line index -> rewritten line, for inline comments to fix."""
    fixes: dict[int, str] = {}
    triple = None
    for i, line in enumerate(block):
        hash_i, triple = scan_line(line, triple)
        if hash_i == -1:
            continue
        if line[hash_i:hash_i + 2] == "#:":
            continue  # `#: ...` is a captured-output marker, not a comment
        code = line[:hash_i]
        if code.strip() == "":
            continue  # full-line comment, no code to measure the gap from
        wanted = code.rstrip() + "  " + line[hash_i:]
        if wanted != line:
            fixes[i] = wanted
    return fixes


def check_file(path: Path, fix: bool) -> list[int]:
    """Return the 1-based line numbers with wrong spacing; rewrite if `fix`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    findings: list[int] = []
    out = list(lines)
    for start, block in iter_python_blocks(lines):
        for idx, new_line in _spacing_targets(block).items():
            findings.append(start + idx + 1)
            out[start + idx] = new_line

    if fix and findings:
        write_text_lf(path, "\n".join(out))
    return findings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--fix", action="store_true",
                    help="rewrite the spacing in place")
    args = ap.parse_args(argv)

    total = 0
    for path in md_files(args.paths):
        for lineno in check_file(path, args.fix):
            if not args.fix:
                print(f"{path}:{lineno}: inline comment is not two "
                      "spaces after the code")
            total += 1

    if total and args.fix:
        print(f"Fixed {total} comment(s).")
        return 0
    if total:
        print(f"\n{total} inline comment(s) misaligned. "
              "Fix with: python tools/comment_spacing.py --fix")
        return 1
    print("Comment spacing OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
