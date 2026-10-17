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
    <summary>Done when</summary>

    `test_exercise_3.py` passes.

    <details>
    <summary>Solution</summary>

    (the approach, the listing, and the discussion, as authored)

    Before you move on, name what separates your attempt from this one:
    a different design, a detail, or an equivalent alternative.

    </details>
    </details>
    </details>
    </details>

Nesting enforces the order: each toggle stays hidden until the step
above it is open. Without JavaScript the site shows the same native
elements; `resources/static/solutions.js` adds progress memory on top.

The authored form is flat. After the generated exercise quote, a
paragraph whose first word is `Hint:` is the "where to look" step, and
everything after it is the solution. A paragraph beginning `Done when:`
directly after the hint is a criterion: what you can check to know your
attempt is finished (a test file to run, the output to match, a `ty`
diagnostic that must disappear). It becomes a "Done when" step between
"The shape" and "Solution". The criterion is authored, never generated.
A `Done when:` paragraph anywhere else is ordinary prose, and a
solution without one gets the three-step ladder. Only an exercise with such a
paragraph gets a ladder; the rest of the file is left as it is. The
tags are generated, and every run rewrites them in full, the way
`exercise_statements.py` rewrites the quote:

    ## 3. Title

    > (the exercise statement)

    Hint: One or two sentences naming the section and the mechanism.

    Done when: `test_exercise_3.py` passes.

    (the approach, the listing, and the discussion)

The last paragraph of every "Solution" step is `DIAGNOSIS`, a fixed
request to name what separates your attempt from the model solution.
Readers handed a model solution match its surface features unless
something forces a judgment, and its three categories (a different
design, a detail, an equivalent alternative) are the ones `AGENTS.md`
gives a reviewing agent.

"The shape" is generated too, from the solution's own listings. Each
listing named `# path.py` on its first line, except a `test_*.py` file,
is reduced to its declarations: imports, `type` aliases, constants
(an assignment whose target is written in capitals), classes, and
functions, with every function body replaced by `...`. An assignment
to a lowercase name stays when a kept line reads the name, as
`monitoring = sys.monitoring` does above constants written in terms of
it. Every other top-level statement, the demonstration and its `#:`
markers, is dropped.
A constant whose value is a string literal spanning more than
`LONG_LITERAL` lines, a maze layout or a data table, keeps its name
and annotation and has the literal replaced by `...`, so a shape
block shows what the module declares and not the data it carries.
A docstring stays. A listing with no body to elide gives no shape
block, and an exercise whose listings give none has no "The shape"
step. The shape block's first line is `# The shape of <path>`, which
no extractor reads as a path, so `extract_solutions.py` never writes
it, and it carries no `#:` marker, so `validate_output.py` never runs
it.

Which lines the tool owns. In a numbered section (one whose heading
matches `check_solutions.ANSWER`), the `<details>` lines, the
`<summary>` lines carrying one of the four labels, the `</details>`
lines, the `DIAGNOSIS` paragraph (matched by its exact text), and
every fenced block whose first line is `# The shape of ...` are
generated. A run removes them and restores the `Hint:` prefix on the
first paragraph the "Where to look" step held. When a "Done when" step
was present, it also restores the `Done when:` prefix on the paragraph
after the hint. Then it nests the section again from the flat form
that remains. Every other line is kept, so
the authored prose and listings round-trip byte for byte. A check run
(the default) reports each section whose ladder differs from what a
run would write.

`steps()` returns one exercise's steps in order, for `hint.py`, which
prints them one at a time at the command line. Its "Solution" step
ends with the `DIAGNOSIS` paragraph, as the rendered ladder does.

Usage:
    python -m tools.solution_steps              # report drift
    python -m tools.solution_steps --write      # rewrite Solutions/
    python -m tools.solution_steps --write 30   # only chapter 30
"""

import argparse
import ast
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from tools.check_solutions import SOLUTIONS_DIR, selected
from tools.exercise_statements import Section, sections
from tools.markdown import Document
from tools.repo import solutions_file
from tools.report import Finding, report

WHERE = "Where to look"
SHAPE = "The shape"
DONE = "Done when"
SOLUTION = "Solution"
LABELS = (WHERE, SHAPE, DONE, SOLUTION)

HINT_PREFIX = "Hint:"
DONE_PREFIX = "Done when:"
DIAGNOSIS = (
    "Before you move on, name what separates your attempt from this one:",
    "a different design, a detail, or an equivalent alternative.",
)
"""The paragraph that closes every "Solution" step, one entry per line."""
SHAPE_PREFIX = "# The shape of "
MAX_WIDTH = 60
LONG_LITERAL = 3
"""A constant's string literal longer than this many lines is elided."""

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


def _elide_literal(lines: list[str], node: ast.Assign | ast.AnnAssign,
                   edits: list[tuple[int, int, list[str]]]) -> None:
    """Queue the edit that replaces a long string literal with `...`.

    A constant's value that is a string spanning more than
    `LONG_LITERAL` lines, bare or with a method call on it such as
    `.strip()`, is data, not shape; the line that opens it keeps
    everything before the literal and ends in `...`.
    """
    value = node.value
    if value is None:
        return
    literal = value
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
        literal = value.func.value  # `"""...""".strip()`
    if not (isinstance(literal, ast.Constant)
            and isinstance(literal.value, str)):
        return
    start = value.lineno - 1
    stop = value.end_lineno or value.lineno
    if stop - start <= LONG_LITERAL:
        return
    head = lines[start][:value.col_offset]
    edits.append((start, stop, [head + "..."]))


def _collect(nodes: list[ast.stmt], lines: list[str],
             edits: list[tuple[int, int, list[str]]]) -> bool:
    """Queue the body edits under `nodes`; True if any body was elided.

    A long string literal in a constant is elided too, but a listing
    with only that to elide still has no body, and gets no shape.
    """
    elided = False
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            elided = _elide(lines, node, edits) or elided
        elif isinstance(node, ast.ClassDef):
            elided = _collect(node.body, lines, edits) or elided
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            _elide_literal(lines, node, edits)
    return elided


def _declared(node: ast.stmt) -> bool:
    """Whether a top-level statement is a declaration in its own right."""
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef,
                         ast.FunctionDef, ast.AsyncFunctionDef,
                         ast.TypeAlias)):
        return True
    name = _assigned_name(node)
    return name is not None and bool(CONSTANT.match(name))


def _assigned_name(node: ast.stmt) -> str | None:
    """The name a simple assignment binds, or None for anything else."""
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    if (isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)):
        return node.targets[0].id
    return None


def _shown_names(node: ast.AST) -> set[str]:
    """The names `node` reads in the lines a shape block shows.

    A function's body becomes `...`, so the names in it are left out;
    its decorators, signature, and return annotation stay in view.
    """
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        shown: list[ast.AST] = [*node.decorator_list, node.args,
                                *node.type_params]
        if node.returns is not None:
            shown.append(node.returns)
        return set().union(*(_shown_names(part) for part in shown))
    names = ({node.id} if isinstance(node, ast.Name)
             and isinstance(node.ctx, ast.Load) else set())
    for child in ast.iter_child_nodes(node):
        names |= _shown_names(child)
    return names


def _kept(body: list[ast.stmt]) -> list[ast.stmt]:
    """The top-level statements that make up the shape, in order.

    Declarations stay, and so does a simple assignment to a lowercase
    name that a kept statement reads, such as
    `monitoring = sys.monitoring` above constants written in terms of
    it. Every other assignment is demonstration and is dropped.
    """
    kept = [node for node in body if _declared(node)]
    while True:
        needed = set().union(*(_shown_names(node) for node in kept))
        grown = [node for node in body
                 if node in kept or _assigned_name(node) in needed]
        if len(grown) == len(kept):
            return kept
        kept = grown


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
    kept = _kept(tree.body)
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
    """Everything after the hint and done paragraphs (or the quote)."""
    done: list[str] = field(default_factory=list)
    """The `Done when:` paragraph after the hint, prefix removed."""


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
    _own_diagnosis(body, fenced, owned)
    had_hint = had_done = False
    for k, line in enumerate(body):
        if fenced[k] or owned[k]:
            continue
        stripped = line.strip()
        m = SUMMARY.match(stripped)
        if stripped in (OPEN, CLOSE) or (m and m.group(1) in LABELS):
            owned[k] = True
            label = m.group(1) if m else None
            had_hint = had_hint or label == WHERE
            had_done = had_done or label == DONE
    kept = [line for k, line in enumerate(body) if not owned[k]]
    kept = _squeeze(kept)
    first = _paragraph_start(kept, 0) if had_hint else None
    if first is not None:
        if not kept[first].startswith(HINT_PREFIX):
            kept[first] = f"{HINT_PREFIX} {kept[first]}"
        second = _paragraph_start(kept, _paragraph_end(kept, first))
        if (had_done and second is not None
                and not kept[second].startswith(DONE_PREFIX)):
            kept[second] = f"{DONE_PREFIX} {kept[second]}"
    return split_hint(kept)


def _paragraph_start(lines: Sequence[str], start: int) -> int | None:
    """Index of the first nonblank line at or after `start`, or None."""
    return next((k for k in range(start, len(lines)) if lines[k].strip()),
                None)


def _paragraph_end(lines: Sequence[str], start: int) -> int:
    """One past the last line of the paragraph opening at `start`."""
    end = start
    while end < len(lines) and lines[end].strip():
        end += 1
    return end


def _own_diagnosis(body: Sequence[str], fenced: list[bool],
                   owned: list[bool]) -> None:
    """Mark each unfenced run of lines that is the `DIAGNOSIS` text."""
    size = len(DIAGNOSIS)
    for k in range(len(body) - size + 1):
        if any(fenced[k:k + size]):
            continue
        if tuple(line.strip() for line in body[k:k + size]) == DIAGNOSIS:
            for j in range(k, k + size):
                owned[j] = True


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


def _paragraph(lines: Sequence[str], start: int | None,
               prefix: str) -> tuple[list[str], int] | None:
    """(the paragraph opening at `start` less `prefix`, one past its end).

    None when there is no paragraph at `start` or its first line does
    not begin with `prefix`.
    """
    if start is None or not lines[start].startswith(prefix):
        return None
    end = _paragraph_end(lines, start)
    found = list(lines[start:end])
    found[0] = found[0].removeprefix(prefix).lstrip()
    return found, end


def split_hint(lines: list[str]) -> Flat:
    """Separate the `Hint:` paragraph that opens `lines`, if one does.

    A `Done when:` paragraph directly after the hint is set apart too.
    """
    hint = _paragraph(lines, _paragraph_start(lines, 0), HINT_PREFIX)
    if hint is None:
        return Flat([], lines)
    hint_lines, end = hint
    done = _paragraph(lines, _paragraph_start(lines, end), DONE_PREFIX)
    if done is None:
        return Flat(hint_lines, _squeeze(lines[end:]))
    done_lines, end = done
    return Flat(hint_lines, _squeeze(lines[end:]), done_lines)


def shapes(rest: list[str]) -> list[list[str]]:
    """A shape block's lines for each listing in `rest` that has one."""
    found: list[list[str]] = []
    for i, j in _blocks(rest):
        if not PYTHON_FENCE.match(rest[i]) or j >= len(rest):
            continue
        content = rest[i + 1:j]
        first = next((line for line in content if line.strip()), "")
        # A "(continued)" part has no shape of its own: the regex stops
        # at the name, so such a block is passed over here.
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
    if flat.done:
        out += [OPEN, summary_line(DONE), "", *flat.done, ""]
        depth += 1
    out += [OPEN, summary_line(SOLUTION), "", *_solution(flat), ""]
    depth += 1
    out += [CLOSE] * depth
    return out


def _solution(flat: Flat) -> list[str]:
    """The "Solution" step's lines: the authored rest, then `DIAGNOSIS`."""
    return [*flat.rest, "", *DIAGNOSIS] if flat.rest else list(DIAGNOSIS)


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
    if flat.done:
        found.append(Step(DONE, list(flat.done)))
    found.append(Step(SOLUTION, _solution(flat)))
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
