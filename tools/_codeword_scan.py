"""One-off scan: bare identifiers in prose that may need backticks.

Skips fenced code, indented code blocks, inline-code spans, link URLs, and
footnotes. Reports each bare occurrence of a candidate identifier with its line,
grouped so high-confidence words can be fixed and ambiguous ones reviewed.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# Candidates worth checking. Ordinary-English keywords (and, or, not, in, is,
# for, if) are deliberately excluded: backticking those needs case-by-case prose
# judgment, not a sweep.
WORDS = [
    "None", "True", "False", "lambda", "dict", "tuple", "str", "int", "bool",
    "float", "bytes", "frozenset", "set", "list", "type", "object", "map",
    "filter", "range", "super", "property", "staticmethod", "classmethod",
    "isinstance", "issubclass", "enumerate", "zip", "sorted", "repr", "iter",
    "self", "cls", "len", "print", "open", "vars", "callable", "bytearray",
]

FENCE = re.compile(r"^\s*(```+|~~~+)")
INDENTED = re.compile(r"^( {4,}|\t)")


def prose_lines(text: str) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    in_fence = False
    marker = ""
    for i, line in enumerate(text.splitlines(), 1):
        f = FENCE.match(line)
        if in_fence:
            if f and line.strip().startswith(marker):
                in_fence = False
            continue
        if f:
            in_fence = True
            marker = f.group(1)[0] * 3
            continue
        if INDENTED.match(line):       # indented code block
            continue
        out.append((i, line))
    return out


def mask(line: str) -> str:
    line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)
    line = re.sub(r"\]\([^)]*\)", lambda m: " " * len(m.group(0)), line)
    line = re.sub(r"\^\[[^\]]*\]", lambda m: " " * len(m.group(0)), line)
    return line


def main(words: list[str]) -> None:
    patterns = {w: re.compile(rf"\b{re.escape(w)}\b") for w in words}
    counts: Counter[str] = Counter()
    for p in sorted(Path("Markdown").glob("*.md")):
        for ln, line in prose_lines(p.read_text(encoding="utf-8")):
            m = mask(line)
            for w, pat in patterns.items():
                if pat.search(m):
                    counts[w] += len(pat.findall(m))
                    print(f"{w:10} {p.name}:{ln}: {line.strip()[:96]}")
    print("\n--- counts ---")
    for w in words:
        if counts[w]:
            print(f"{w}: {counts[w]}")


if __name__ == "__main__":
    chosen = sys.argv[1:] or WORDS
    main(chosen)
