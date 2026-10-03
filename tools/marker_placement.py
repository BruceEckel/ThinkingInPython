#!/usr/bin/env python3
"""Report or fix #: output markers that sit below the wrong statement.

A #: run belongs directly after the top-level statement that printed it,
so the reader sees each result beside the code responsible for it.
validate_output.py cannot see a misplaced run: it compares each run with
everything printed since the previous run, so markers gathered at the end
of a listing pass as long as their text is right.

This tool runs each marked ```python block the way validate_output.py
does (same directory, same sys.path, same namespace), but one top-level
statement at a time, recording which statement printed each output line.
It then lays the markers out again:

- Output from an ordinary statement goes directly after its last line.
- Output from an import goes after the blank lines that close the import
  block, directly above the next statement. A marker hugging an import
  sits inside the import block, and ruff's I001 fails it.
- Output that does not end in a newline joins the next statement's output,
  since one #: line cannot be split across two runs.
- Statements on one line share a run.

A block whose current layout differs is reported. With --write the block
is rewritten with the same marker text in the new layout. A block whose
total output differs from its markers (a stale marker, a timing listing,
output printed only at interpreter exit) is reported and left alone; run
`tip output` first so only placement remains.

Usage:
    python -m tools.marker_placement Chapters Solutions
    python -m tools.marker_placement --write Chapters/30_Patterns--Observer.md
"""

import __future__

import argparse
import ast
import contextlib
import fnmatch
import functools
import io
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from tools.config import (
    BUILD_DIR, EXAMPLES_TREE, INLINE_NORUN_MARKER, NORUN_FILE,
    SOLUTIONS_DIR, utils_dir)
from tools.pycode import walk_fenced
from tools.repo import (
    add_jobs_arg, block_slug, chapter_stem, load_glob_list, write_text_lf)
from tools.validate_output import (
    collect_files, collect_now, encode_output, is_marker, run_location,
    run_watched)

SOLUTIONS_TREE = BUILD_DIR / "solutions"


@dataclass
class Run:
    """A #: run: how many code lines sit above it, and its lines."""
    anchor: int
    lines: list[str] = field(default_factory=list)


def split_block(block: list[str]) -> tuple[list[str], list[int], list[Run]]:
    """Separate a block into code lines, their block indices, and runs."""
    code: list[str] = []
    where: list[int] = []
    runs: list[Run] = []
    for i, line in enumerate(block):
        if is_marker(line):
            if not runs or runs[-1].anchor != len(code):
                runs.append(Run(len(code)))
            runs[-1].lines.append(line)
        else:
            code.append(line)
            where.append(i)
    return code, where, runs


def first_line(stmt: ast.stmt) -> int:
    """A statement's first line, counting its decorators."""
    decorators = getattr(stmt, "decorator_list", [])
    return min([stmt.lineno, *(d.lineno for d in decorators)])


def is_import(stmt: ast.stmt) -> bool:
    return isinstance(stmt, (ast.Import, ast.ImportFrom))


def run_statements(
    code: list[str], filename: str, namespace: dict,
) -> tuple[list[tuple[ast.stmt, str]], str | None]:
    """Execute each top-level statement, capturing what it prints."""
    tree = ast.parse("".join(code), filename)
    flags = 0
    results: list[tuple[ast.stmt, str]] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__":
            for alias in stmt.names:
                flags |= getattr(__future__, alias.name).compiler_flag
        compiled = compile(
            ast.Module(body=[stmt], type_ignores=[]), filename, "exec",
            flags=flags, dont_inherit=True)
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            exec(compiled, namespace)  # noqa: S102
        except BaseException as exc:  # noqa: BLE001
            results.append((stmt, buf.getvalue()))
            return results, f"line {stmt.lineno}: {type(exc).__name__}: {exc}"
        finally:
            sys.stdout = old
        results.append((stmt, buf.getvalue()))
    return results, None


def wanted_runs(
    code: list[str], results: list[tuple[ast.stmt, str]],
) -> list[Run]:
    """Where each statement's output belongs, as runs."""
    runs: list[Run] = []
    pending = ""
    last: ast.stmt | None = None
    groups: list[tuple[ast.stmt, str]] = []
    for stmt, out in results:
        if not out:
            continue
        pending += out
        last = stmt
        if pending.endswith("\n"):
            groups.append((stmt, pending))
            pending = ""
    if pending and last is not None:
        groups.append((last, pending))
    stmts = [stmt for stmt, _ in results]
    for stmt, text in groups:
        anchor = stmt.end_lineno or stmt.lineno
        if is_import(stmt):
            # Past the rest of the import block and the blank lines after it
            i = stmts.index(stmt)
            while i + 1 < len(stmts) and is_import(stmts[i + 1]):
                i += 1
            anchor = stmts[i].end_lineno or stmts[i].lineno
            while anchor < len(code) and not code[anchor].strip():
                anchor += 1
        else:
            # Indented comments closing a block belong to its statement
            while anchor < len(code) and code[anchor][:1].isspace() and (
                    code[anchor].lstrip().startswith("#")):
                anchor += 1
        if runs and runs[-1].anchor == anchor:
            runs[-1].lines.extend(encode_output(text))
        else:
            runs.append(Run(anchor, encode_output(text)))
    return runs


def layout(code: list[str], runs: list[Run]) -> list[str]:
    """Interleave code lines and runs, dropping trailing blank lines."""
    at = {run.anchor: run.lines for run in runs}
    out: list[str] = []
    for i, line in enumerate(code):
        out.extend(at.get(i, []))
        out.append(line)
    out.extend(at.get(len(code), []))
    while out and not out[-1].strip():
        out.pop()
    return out


@dataclass
class BlockOutcome:
    lines: list[str]
    notes: list[str]
    moved: bool
    stuck: bool


def check_block(
    block: list[str], path: Path, chapter: str, start: int, *,
    tree: Path, skips: list[str],
) -> BlockOutcome:
    """Check one marked block; return its lines in the wanted layout."""
    keep = BlockOutcome(block, [], moved=False, stuck=False)
    slug = block_slug(block)
    if slug is None:
        rel, filepath = None, None
    elif slug.startswith("utils/"):
        rel, filepath = slug, tree / slug
    else:
        rel, filepath = f"{chapter}/{slug}", tree / chapter / slug
    if INLINE_NORUN_MARKER in "".join(block) or (
        rel and any(fnmatch.fnmatch(rel, pat) for pat in skips)
    ):
        return keep
    label = f"{path.as_posix()}:{start + 1} {rel or '(no slug)'}"
    code, where, have = split_block(block)
    namespace: dict = {
        "__name__": "__main__",
        "__file__": str(filepath) if filepath else str(path),
    }
    try:
        with run_location(filepath.parent if filepath else None,
                          utils_dir(tree)):
            results, error = run_statements(code, str(filepath), namespace)
    except SyntaxError as exc:
        results, error = [], f"SyntaxError: {exc}"
    del namespace
    collect_now()
    if error:
        keep.notes.append(f"{label}: skipped, {error}")
        keep.stuck = True
        return keep
    # Output below the last run is deliberately unmarked (it varies by
    # machine, say), as validate_output.py also treats it.
    if have:
        results = [(stmt, out) for stmt, out in results
                   if first_line(stmt) - 1 < have[-1].anchor]
    want = wanted_runs(code, results)
    have_text = [line for run in have for line in run.lines]
    if len(have_text) != sum(len(run.lines) for run in want):
        keep.notes.append(f"{label}: skipped, output differs from markers")
        keep.stuck = True
        return keep
    # Keep the committed text, so a measured value that varies from run
    # to run (a timing, a memory peak) moves without changing.
    taken = iter(have_text)
    for run in want:
        run.lines = [next(taken) for _ in run.lines]
    if [(r.anchor, len(r.lines)) for r in have] == [
            (r.anchor, len(r.lines)) for r in want]:
        return keep
    for run in want:
        if any(r.anchor == run.anchor for r in have):
            continue
        below = where[run.anchor - 1] if run.anchor else -1
        keep.notes.append(
            f"{label}: {len(run.lines)} line(s) belong after line "
            f"{start + below + 1}: {run.lines[0].rstrip()}")
    return BlockOutcome(layout(code, want), keep.notes, moved=True,
                        stuck=False)


def process(
    path: Path, *, write: bool, skips: list[str],
) -> tuple[bool | None, str]:
    """Check one Markdown file. True: clean; False: something to report."""
    tree = (SOLUTIONS_TREE if path.resolve().is_relative_to(SOLUTIONS_DIR)
            else EXAMPLES_TREE)
    chapter = chapter_stem(path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    notes: list[str] = []
    moved = stuck = marked = False
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        for ev in walk_fenced(
            lines, wanted=lambda m: (m.group(1) or "") in ("python", "py"),
        ):
            out.append(lines[ev.open_at])
            if ev.match is None:
                continue
            block = lines[ev.open_at + 1:ev.end]
            if any(is_marker(line) for line in block):
                marked = True
                result = check_block(
                    block, path, chapter, ev.open_at + 1,
                    tree=tree.resolve(), skips=skips)
                notes.extend(result.notes)
                moved = moved or result.moved
                stuck = stuck or result.stuck
                block = result.lines
            out.extend(block)
            if ev.end < len(lines):
                out.append(lines[ev.end])
    if moved and write:
        write_text_lf(path, "".join(out))
    report = "".join(f"  {note}\n" for note in notes)
    if not marked:
        return None, report
    return not (moved or stuck), report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", type=Path,
                    help="Markdown files or directories")
    ap.add_argument("--write", action="store_true",
                    help="move misplaced runs (default: report)")
    add_jobs_arg(ap, "files")
    args = ap.parse_args(argv)
    files = [f for f in collect_files(args.targets) if f.suffix == ".md"]
    work = functools.partial(
        process, write=args.write, skips=load_glob_list(NORUN_FILE))
    jobs = min(max(1, args.jobs), len(files))
    if jobs == 1:
        outcomes = list(map(work, files))
    else:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            outcomes = list(pool.map(
                functools.partial(run_watched, work=work), files))
    bad = 0
    for path, (result, report) in zip(files, outcomes, strict=True):
        if report:
            print(f"{path.as_posix()}\n{report}", end="")
        if result is False:
            bad += 1
    verb = "rewritten" if args.write else "to fix"
    print(f"\n{bad} file(s) {verb} of {len(files)}.")
    return 1 if bad and not args.write else 0


if __name__ == "__main__":
    raise SystemExit(main())
