#!/usr/bin/env python3
"""Fold each solution into steps a reader reveals one at a time.

A solution in `Solutions/NN_*/README.md` gives everything away at once:
the exercise, the approach, the listing, and the discussion sit in one
scroll. This tool nests a solution into a ladder of HTML `<details>`
elements, which GitHub and the site both render collapsed, so a reader
sees the exercise alone and opens one step at a time:

    ## 3. Title

    > (the exercise statement, from exercise_statements.py)

    <details>
    <summary>Where to look</summary>

    One or two sentences naming the section and the mechanism to use.

    <details>
    <summary>The shape</summary>

    ```python
    # The shape of exercise_3.py
    class Broadcaster[T]:
        def connect(self, responder: Responder[T]) -> None:
            ...
    ```

    <details>
    <summary>Solution</summary>

    (the approach, the listing, and the discussion, as authored)

    </details>
    </details>
    </details>

Nesting enforces the order: the "Solution" toggle is not visible until
"The shape" is open. Without JavaScript the site shows the same native
elements; `resources/static/solutions.js` adds progress memory on top.

The authored form is flat. After the generated exercise quote, a
paragraph whose first word is `Hint:` is the "where to look" step, and
everything after it is the solution. Only an exercise with such a
paragraph gets a ladder; the rest of the file is left as it is. The
tags are generated, and every run rewrites them in full, the way
`exercise_statements.py` rewrites the quote:

    ## 3. Title

    > (the exercise statement)

    Hint: One or two sentences naming the section and the mechanism.

    (the approach, the listing, and the discussion)

"The shape" is generated too, from the solution's own listings. Each
listing named `# path.py` on its first line, except a `test_*.py` file,
is reduced to its declarations: imports, `type` aliases, constants
(an assignment whose target is written in capitals), classes, and
functions, with every function body replaced by `...` and every other
top-level statement, the demonstration and its `#:` markers, dropped.
A docstring stays. A listing with no body to elide gives no shape
block, and an exercise whose listings give none has no "The shape"
step. The shape block's first line is `# The shape of <path>`, which
no extractor reads as a path, so `extract_solutions.py` never writes
it, and it carries no `#:` marker, so `validate_output.py` never runs
it.

Which lines the tool owns. In a numbered section (one whose heading
matches `check_solutions.ANSWER`), the `<details>` lines, the
`<summary>` lines carrying one of the three labels, the `</details>`
lines, and every fenced block whose first line is `# The shape of ...`
are generated. A run removes them, restores the `Hint:` prefix on the
first paragraph the "Where to look" step held, and nests the section
again from the flat form that remains. Every other line is kept, so
the authored prose and listings round-trip byte for byte. A check run
(the default) reports each section whose ladder differs from what a
run would write.

`steps()` returns one exercise's steps in order, for `hint.py`, which
prints them one at a time at the command line.

Usage:
    python -m tools.solution_steps              # report drift
    python -m tools.solution_steps --write      # rewrite Solutions/
    python -m tools.solution_steps --write 30   # only chapter 30
"""

import argparse
import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.check_solutions import SOLUTIONS_DIR, selected
from tools.exercise_statements import Section, sections
from tools.markdown import Document
from tools.repo import solutions_file
from tools.report import Finding, report

WHERE = "Where to look"
SHAPE = "The shape"
SOLUTION = "Solution"
LABELS = (WHERE, SHAPE, SOLUTION)

HINT_PREFIX = "Hint:"
SHAPE_PREFIX = "# The shape of "
MAX_WIDTH = 60

OPEN = "<details>"
CLOSE = "</details>"
SUMMARY = re.compile(r"^<summary>(.*)</summary>\s*$")
FENCE = re.compile(r"^```")
PYTHON_FENCE = re.compile(r"^```(?:python|py)\s*$")
CONSTANT = re.compile(r"^[A-Z][A-Z0-9_]*$")


def summary_line(label: str) -> str:
    return f"<summary>{label}</summary>"


# --------------------------------------------------------------------------- #
# The shape of a listing
# --------------------------------------------------------------------------- #
def _first_line(node: ast.stmt) -> int:
    """1-based line where a statement starts, decorators included."""
    decorators = getattr(node, "decorator_list", [])
    return min([node.lineno, *(d.lineno for d in decorators)])


def _is_docstring(node: ast.stmt) -> bool:
    return (isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str))


def _is_ellipsis(node: ast.stmt) -> bool:
    return (isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and node.value.value is Ellipsis)


def _elide(lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef,
           edits: list[tuple[int, int, list[str]]]) -> bool:
    """Queue the edit that replaces `node`'s body with `...`.

    Returns False when there is nothing to elide: a body that is only
    a docstring, or already `...`.
    """
    body = node.body
    if body and _is_docstring(body[0]):
        body = body[1:]
    if not body or (len(body) == 1 and _is_ellipsis(body[0])):
        return False
    first, last = body[0], body[-1]
    start = first.lineno - 1
    stop = (last.end_lineno or last.lineno)
    head = lines[start][:first.col_offset]
    if head.strip():
        # The body starts on the signature's last line: `) -> None: x`.
        one = head + "..."
        if len(one) <= MAX_WIDTH:
            edits.append((start, stop, [one]))
        else:
            indent = " " * (node.col_offset + 4)
            edits.append((start, stop, [head.rstrip(), indent + "..."]))
    else:
        edits.append((start, stop, [" " * first.col_offset + "..."]))
    return True


def _collect(nodes: list[ast.stmt], lines: list[str],
             edits: list[tuple[int, int, list[str]]]) -> bool:
    """Queue the body edits under `nodes`; True if any body was elided."""
    elided = False
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            elided = _elide(lines, node, edits) or elided
        elif isinstance(node, ast.ClassDef):
            elided = _collect(node.body, lines, edits) or elided
    return elided


def _kept(node: ast.stmt) -> bool:
    """Whether a top-level statement is part of the shape."""
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef,
                         ast.FunctionDef, ast.AsyncFunctionDef,
                         ast.TypeAlias)):
        return True
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return bool(CONSTANT.match(node.target.id))
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target = node.targets[0]
        return isinstance(target, ast.Name) and bool(CONSTANT.match(target.id))
    return False


def shape(listing: Sequence[str]) -> list[str] | None:
    """The declarations of a listing with every function body elided.

    `listing` is the block's content lines. The `# path.py` line, a
    comment, is not a declaration and is left out; `shapes()` puts the
    shape line in its place. None when the listing does not parse or
    has no body to elide.
    """
    source = "\n".join(listing)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    lines = source.split("\n")
    kept = [node for node in tree.body if _kept(node)]
    edits: list[tuple[int, int, list[str]]] = []
    if not _collect(kept, lines, edits):
        return None
    for start, stop, replacement in sorted(edits, reverse=True):
        lines[start:stop] = replacement
    # Line numbers moved with the edits; map each kept statement's span
    # through them. Edits never cross a statement's bounds, so a span's
    # new end is its old end less the lines the edits inside it removed.
    out: list[str] = []
    previous_end: int | None = None
    offset = 0
    for node in kept:
        first = _first_line(node) - 1
        last = node.end_lineno or node.lineno
        inside = [(s, e, r) for s, e, r in edits if first <= s < last]
        removed = sum(e - s - len(r) for s, e, r in inside)
        if previous_end is not None:
            gap = source.split("\n")[previous_end:first]
            if any(not line.strip() for line in gap):
                out.append("")
        out.extend(lines[first - offset:last - offset - removed])
        offset += removed
        previous_end = last
    return out


# --------------------------------------------------------------------------- #
# The flat form and the nested form of one section
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Flat:
    """A section's authored lines, with the hint (if any) set apart."""

    hint: list[str]
    """The hint paragraph, `Hint:` prefix removed; empty when none."""
    rest: list[str]
    """Everything after the hint paragraph (or after the quote)."""


def _blocks(lines: Sequence[str]) -> list[tuple[int, int]]:
    """(open, close) line indexes of each fenced block in `lines`."""
    found: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        if FENCE.match(lines[i]):
            j = i + 1
            while j < len(lines) and not FENCE.match(lines[j]):
                j += 1
            found.append((i, j))
            i = j + 1
        else:
            i += 1
    return found


def _in_blocks(lines: Sequence[str]) -> list[bool]:
    flags = [False] * len(lines)
    for i, j in _blocks(lines):
        for k in range(i, min(j + 1, len(lines))):
            flags[k] = True
    return flags


def is_shape_block(lines: Sequence[str], open_at: int) -> bool:
    """Whether the fenced block opening at `open_at` is a shape block."""
    k = open_at + 1
    while k < len(lines) and not lines[k].strip():
        k += 1
    return k < len(lines) and lines[k].startswith(SHAPE_PREFIX)


def unwrap(body: Sequence[str]) -> Flat:
    """The flat form of a section's lines after its quote."""
    owned = [False] * len(body)
    fenced = _in_blocks(body)
    for i, j in _blocks(body):
        if is_shape_block(body, i):
            for k in range(i, min(j + 1, len(body))):
                owned[k] = True
    had_hint = False
    for k, line in enumerate(body):
        if fenced[k] or owned[k]:
            continue
        stripped = line.strip()
        m = SUMMARY.match(stripped)
        if stripped in (OPEN, CLOSE) or (m and m.group(1) in LABELS):
            owned[k] = True
            had_hint = had_hint or (m is not None and m.group(1) == WHERE)
    kept = [line for k, line in enumerate(body) if not owned[k]]
    kept = _squeeze(kept)
    if had_hint:
        first = next((k for k, line in enumerate(kept) if line.strip()),
                     None)
        if first is not None and not kept[first].startswith(HINT_PREFIX):
            kept[first] = f"{HINT_PREFIX} {kept[first]}"
    return split_hint(kept)


def _squeeze(lines: list[str]) -> list[str]:
    """`lines` with runs of blank lines collapsed to one, ends trimmed."""
    out: list[str] = []
    for line in lines:
        if not line.strip() and out and not out[-1].strip():
            continue
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def split_hint(lines: list[str]) -> Flat:
    """Separate the `Hint:` paragraph that opens `lines`, if one does."""
    first = next((k for k, line in enumerate(lines) if line.strip()), None)
    if first is None or not lines[first].startswith(HINT_PREFIX):
        return Flat([], lines)
    end = first
    while end < len(lines) and lines[end].strip():
        end += 1
    hint = list(lines[first:end])
    hint[0] = hint[0].removeprefix(HINT_PREFIX).lstrip()
    return Flat(hint, _squeeze(lines[end:]))


def shapes(rest: list[str]) -> list[list[str]]:
    """A shape block's lines for each listing in `rest` that has one."""
    found: list[list[str]] = []
    for i, j in _blocks(rest):
        if not PYTHON_FENCE.match(rest[i]) or j >= len(rest):
            continue
        content = rest[i + 1:j]
        first = next((line for line in content if line.strip()), "")
        m = re.match(r"^#\s*([\w./-]+\.py)\s*$", first)
        if m is None or m.group(1).rsplit("/", 1)[-1].startswith("test_"):
            continue
        reduced = shape(content)
        if reduced is None:
            continue
        found.append(["```python", f"{SHAPE_PREFIX}{m.group(1)}",
                      *reduced, "```"])
    return found


def wrap(flat: Flat) -> list[str]:
    """The nested form of a section's lines after its quote."""
    if not flat.hint:
        return list(flat.rest)
    out = [OPEN, summary_line(WHERE), "", *flat.hint, ""]
    depth = 1
    blocks = shapes(flat.rest)
    if blocks:
        out += [OPEN, summary_line(SHAPE), ""]
        for block in blocks:
            out += [*block, ""]
        depth += 1
    out += [OPEN, summary_line(SOLUTION), "", *flat.rest, ""]
    depth += 1
    out += [CLOSE] * depth
    return out


# --------------------------------------------------------------------------- #
# Steps, for hint.py
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Step:
    label: str
    lines: list[str]


def steps(flat: Flat) -> list[Step]:
    """The steps a reader reveals, in order, for one exercise."""
    if not flat.hint:
        return [Step(SOLUTION, list(flat.rest))]
    found = [Step(WHERE, list(flat.hint))]
    blocks = shapes(flat.rest)
    if blocks:
        found.append(Step(SHAPE, [line for block in blocks
                                  for line in [*block, ""]][:-1]))
    found.append(Step(SOLUTION, list(flat.rest)))
    return found


# --------------------------------------------------------------------------- #
# Whole files
# --------------------------------------------------------------------------- #
def section_end(doc: Document, section: Section) -> int:
    """One past the last line of the section (before the next heading)."""
    fenced = doc.in_fence()
    for k in range(section.heading + 1, len(doc.lines)):
        if not fenced[k] and doc.lines[k].startswith("## "):
            return k
    return len(doc.lines)


def apply(doc: Document) -> tuple[list[str], list[int]]:
    """(new lines, heading line numbers of the sections that changed)."""
    lines = list(doc.lines)
    changed: list[int] = []
    for section in reversed(list(sections(doc))):
        end = section_end(doc, section)
        body = lines[section.end:end]
        flat = unwrap(body)
        if not flat.hint and not any(
                line.strip() == OPEN for line in body):
            continue
        # A blank line before the ladder and one after it: the one
        # before the next heading, or the file's final newline.
        new = ["", *wrap(flat), ""]
        if body != new:
            lines[section.end:end] = new
            changed.append(section.heading + 1)
    changed.reverse()
    return lines, changed


def flat_sections(doc: Document) -> dict[tuple[int, ...], Flat]:
    """Each numbered section's flat form, keyed by the numbers it answers."""
    found: dict[tuple[int, ...], Flat] = {}
    for section in sections(doc):
        end = section_end(doc, section)
        found[section.numbers] = unwrap(doc.lines[section.end:end])
    return found


def process(chapter: Path, write: bool) -> list[Finding]:
    solutions = solutions_file(chapter, SOLUTIONS_DIR)
    if not solutions.exists():
        return []
    doc = Document.parse(solutions)
    lines, changed = apply(doc)
    if not changed:
        return []
    if write:
        solutions.write_text("\n".join(lines), encoding="utf-8",
                             newline="\n")
    return [Finding(solutions, line,
                    "solution steps are out of date; run `tip steps`")
            for line in changed]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("chapters", nargs="*",
                    help="chapter numbers to process (default: all)")
    ap.add_argument("--write", action="store_true",
                    help="rewrite Solutions/ instead of reporting drift")
    args = ap.parse_args(argv)

    findings: list[Finding] = []
    for chapter in selected(args.chapters):
        found = process(chapter, args.write)
        findings.extend(found)
        if args.write and found:
            print(f"Solutions/{chapter.stem}/README.md: "
                  f"{len(found)} section(s) rewritten")
    if args.write:
        files = len({f.path for f in findings})
        print(f"{files} file(s) changed: {len(findings)} section(s).")
        return 0
    return report(
        findings,
        clean="Every solution's steps are current.",
        problem="{n} section(s) in Solutions/ have stale steps. "
                "Run `tip steps` to rewrite them.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
