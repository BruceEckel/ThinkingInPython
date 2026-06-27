#!/usr/bin/env python3
"""Validate and update #: output markers in Python example files.

Lines starting with #: at column 0 mark expected stdout output.
Each #: block is compared to the stdout produced by the
top-level code above it (since the previous #: block):

    print("Hello")
    #: Hello
    print("world")
    #: world

The same markers can be validated and updated directly inside the book's
Markdown. Each ```python fenced block is treated as one program: its code is
run and the #: lines inside the block are rewritten in place. A block is run
from its extracted chapter directory (build/examples/<chapter>/), so imports of
sibling files and relative data paths resolve the way the book assumes. Run
`tools/extract_examples.py --write` first so that tree exists.

Usage:
    python tools/validate_output.py file.py        # check one file
    python tools/validate_output.py Examples/      # check directory
    python tools/validate_output.py chapter.md     # check Markdown listings
    python tools/validate_output.py --update file.py   # rewrite markers
    python tools/validate_output.py --update Markdown/ # rewrite the book
"""

import argparse
import contextlib
import fnmatch
import io
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TREE = ROOT / "build" / "examples"
NORUN_FILE = ROOT / "tools" / "norun.txt"
INLINE_NORUN = "# extract: no-run"

# Matches #: or #: <content> at column 0 only.
MARKER_RE = re.compile(r'^#:(?: (.*))?$')
# A python fenced block, e.g. ```python or ```py.
FENCE_RE = re.compile(r'^```(\w+)?\s*$')
# First content line of a block naming its relative path, e.g. "# trace.py".
PATH_LINE_RE = re.compile(r'^#\s*([\w./\\-]+\.\w+)\s*$')


def is_marker(line: str) -> bool:
    return bool(MARKER_RE.match(line.rstrip('\n\r')))


def parse_chunks(
    lines: list[str],
) -> list[tuple[str, list[int]]]:
    """Split lines into alternating ('code', indices)/('output', indices)."""
    chunks: list[tuple[str, list[int]]] = []
    i = 0
    while i < len(lines):
        kind = 'output' if is_marker(lines[i]) else 'code'
        start = i
        while i < len(lines) and (
            is_marker(lines[i]) == (kind == 'output')
        ):
            i += 1
        chunks.append((kind, list(range(start, i))))
    return chunks


def decode_output(lines: list[str], indices: list[int]) -> str:
    """Convert #: lines to the output string they represent."""
    parts = []
    for idx in indices:
        m = MARKER_RE.match(lines[idx].rstrip('\n\r'))
        # group(1) is None for bare #:, '' would be empty content
        parts.append(
            m.group(1) if (m and m.group(1) is not None) else ''
        )
    return '\n'.join(parts) + '\n' if parts else ''


def strip_trailing(output: str) -> str:
    """Drop trailing whitespace from each line.

    Trailing spaces (from ``print(end=" ")`` loops, ``ljust`` padding, and the
    like) are invisible in the rendered book, and they would leave trailing
    whitespace in the #: marker lines that ruff rejects. So they are ignored
    both when markers are written and when they are compared.
    """
    return '\n'.join(line.rstrip() for line in output.split('\n'))


def encode_output(output: str) -> list[str]:
    """Convert an output string to #: lines (trailing whitespace dropped)."""
    if not output:
        return []
    # removesuffix strips exactly one trailing newline, preserving
    # any intentional trailing blank lines the program produced.
    content = strip_trailing(output).removesuffix('\n').split('\n')
    return [f'#: {ln}\n' if ln else '#:\n' for ln in content]


def exec_capture(
    source: str, filename: str, namespace: dict
) -> tuple[str, BaseException | None]:
    """exec() source, capturing stdout. Returns (output, error_or_None)."""
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        exec(compile(source, filename, 'exec'), namespace)  # noqa: S102
        return buf.getvalue(), None
    except BaseException as exc:
        return buf.getvalue(), exc
    finally:
        sys.stdout = old_stdout


def process_block(
    lines: list[str],
    filename: str,
    *,
    update: bool,
    namespace: dict | None = None,
    line_offset: int = 0,
) -> tuple[list[str], bool, bool]:
    """Run one code/output sequence and check or rewrite its #: markers.

    ``lines`` is the code (with #: markers); ``filename`` labels it for
    compile() and diagnostics; ``line_offset`` shifts reported line numbers so
    they point at the right line of an enclosing file. Returns
    ``(new_lines, ok, changed)``.
    """
    if namespace is None:
        namespace = {'__name__': '__main__', '__file__': filename}

    chunks = parse_chunks(lines)
    new_lines: list[str] = []
    pending: str | None = None
    had_error = False
    ok = True
    changed = False

    for kind, indices in chunks:
        chunk_lines = [lines[i] for i in indices]
        lineno = indices[0] + 1 + line_offset if indices else '?'

        if kind == 'code':
            if not had_error:
                captured, exc = exec_capture(
                    ''.join(chunk_lines), filename, namespace
                )
                if exc:
                    print(
                        f"  line {lineno}: "
                        f"{type(exc).__name__}: {exc}"
                    )
                    ok = False
                    had_error = True
                    pending = None
                else:
                    pending = captured
            new_lines.extend(chunk_lines)

        else:  # output marker block
            actual = pending if pending is not None else ''
            # Canonical form has trailing whitespace stripped, so a marker is
            # correct only when it already matches it. That keeps the markers
            # clean for ruff and lets update rewrite stale trailing spaces.
            canonical = encode_output(actual)

            if chunk_lines == canonical:
                new_lines.extend(chunk_lines)
            elif update and not had_error:
                new_lines.extend(canonical)
                changed = True
            else:
                new_lines.extend(chunk_lines)
                if not had_error:
                    print(f"  line {lineno}:")
                    print(f"    have: {''.join(chunk_lines)!r}")
                    print(f"    want: {''.join(canonical)!r}")
                    ok = False

            pending = None

    return new_lines, ok, changed


def process_file(path: Path, *, update: bool) -> bool | None:
    """Check or update one .py file.

    Returns None  - no #: markers found (file skipped)
            True  - all markers match (or file was updated successfully)
            False - mismatch or execution error
    """
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)

    if not any(is_marker(line) for line in lines):
        return None

    namespace: dict = {'__name__': '__main__', '__file__': str(path)}
    new_lines, ok, changed = process_block(
        lines, str(path), update=update, namespace=namespace
    )

    if update and changed:
        # newline="\n" keeps LF on Windows; the gate rejects CRLF.
        path.write_text(
            ''.join(new_lines), encoding='utf-8', newline='\n'
        )

    return ok


def load_skips() -> list[str]:
    """Glob patterns (forward-slash relative paths) that must not be run."""
    if not NORUN_FILE.exists():
        return []
    out: list[str] = []
    for raw in NORUN_FILE.read_text(encoding='utf-8').splitlines():
        line = raw.split('#', 1)[0].strip()
        if line:
            out.append(line.replace('\\', '/'))
    return out


def block_slug(block: list[str]) -> str | None:
    """The relative path a block names on its first content line, if any."""
    for line in block:
        if line.strip():
            m = PATH_LINE_RE.match(line.rstrip('\n\r'))
            return m.group(1).replace('\\', '/') if m else None
    return None


@contextlib.contextmanager
def run_location(rundir: Path | None, root: Path | None = None):
    """Run a block from ``rundir`` (cwd + sys.path), leaving no trace.

    Imports of sibling extracted files and relative data paths resolve as they
    do under run_examples. The tree root is also placed on sys.path so a block
    can import shared helpers (such as display.py) kept there. sys.path and any
    modules imported by the block are restored afterward so one block cannot
    leak into the next.
    """
    if rundir is None or not rundir.exists():
        yield
        return
    old_cwd = Path.cwd()
    saved_path = list(sys.path)
    saved_modules = set(sys.modules)
    if root is not None:
        sys.path.insert(0, str(root))
    sys.path.insert(0, str(rundir))
    os.chdir(rundir)
    try:
        yield
    finally:
        os.chdir(old_cwd)
        sys.path[:] = saved_path
        for name in set(sys.modules) - saved_modules:
            del sys.modules[name]


def process_markdown(
    path: Path,
    *,
    update: bool,
    tree: Path = DEFAULT_TREE,
    skips: list[str] | None = None,
) -> bool | None:
    """Check or update the #: markers in a Markdown file's python listings.

    Returns None  - no python block carries #: markers (file skipped)
            True  - every marked block matches (or was updated)
            False - a mismatch or execution error in some block
    """
    skips = skips or []
    chapter = path.stem
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)

    out: list[str] = []
    ok = True
    changed = False
    any_markers = False
    i = 0
    n = len(lines)

    while i < n:
        m = FENCE_RE.match(lines[i].rstrip('\n\r'))
        if not (m and (m.group(1) or '') in ('python', 'py')):
            out.append(lines[i])
            i += 1
            continue

        fence_open = lines[i]
        block_start = i + 1
        i = block_start
        while i < n and not lines[i].startswith('```'):
            i += 1
        block = lines[block_start:i]
        fence_close = lines[i] if i < n else None
        if i < n:
            i += 1

        out.append(fence_open)
        if any(is_marker(line) for line in block):
            block = process_md_block(
                block, path, chapter, block_start,
                tree=tree, skips=skips, update=update,
            )
            any_markers = True
            ok = ok and block.ok
            changed = changed or block.changed
            out.extend(block.lines)
        else:
            out.extend(block)
        if fence_close is not None:
            out.append(fence_close)

    if not any_markers:
        return None
    if update and changed:
        # newline="\n" keeps LF on Windows; the gate rejects CRLF.
        path.write_text(''.join(out), encoding='utf-8', newline='\n')
    return ok


class BlockResult:
    """Outcome of processing one fenced block."""

    def __init__(self, lines: list[str], ok: bool, changed: bool):
        self.lines = lines
        self.ok = ok
        self.changed = changed


def process_md_block(
    block: list[str],
    path: Path,
    chapter: str,
    block_start: int,
    *,
    tree: Path,
    skips: list[str],
    update: bool,
) -> BlockResult:
    """Run one ```python block and check or rewrite its #: markers."""
    slug = block_slug(block)
    rel = f'{chapter}/{slug}' if slug else None
    text = ''.join(block)

    if INLINE_NORUN in text or (
        rel and any(fnmatch.fnmatch(rel, pat) for pat in skips)
    ):
        # GUI/interactive/infinite-loop listing: cannot run unattended.
        return BlockResult(block, ok=True, changed=False)

    filepath = tree / chapter / slug if slug else None
    rundir = filepath.parent if filepath else None
    namespace: dict = {
        '__name__': '__main__',
        '__file__': str(filepath) if filepath else str(path),
    }
    label = f'{path}:{rel}' if rel else str(path)

    with run_location(rundir, tree):
        new_lines, ok, changed = process_block(
            block, label, update=update,
            namespace=namespace, line_offset=block_start,
        )
    return BlockResult(new_lines, ok, changed)


def collect_files(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        if t.is_dir():
            files.extend(
                sorted(
                    p for p in t.rglob('*')
                    if p.suffix in ('.py', '.md')
                )
            )
        elif t.suffix in ('.py', '.md'):
            files.append(t)
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument(
        'targets', nargs='+', type=Path,
        help='Python files or directories to process',
    )
    ap.add_argument(
        '--update', action='store_true',
        help='rewrite #: lines with actual output (default: check)',
    )
    ap.add_argument(
        '--tree', type=Path, default=DEFAULT_TREE,
        help='extracted-examples tree Markdown blocks run from '
             f'(default: {DEFAULT_TREE})',
    )
    ap.add_argument(
        '-v', '--verbose', action='store_true',
        help='print each file as it is processed',
    )
    args = ap.parse_args(argv)

    files = collect_files(args.targets)
    if not files:
        print("No .py or .md files found.")
        return 1

    skips = load_skips()
    n_ok = n_fail = n_skip = 0
    for path in files:
        if args.verbose:
            print(path)
        if path.suffix == '.md':
            result = process_markdown(
                path, update=args.update, tree=args.tree, skips=skips
            )
        else:
            result = process_file(path, update=args.update)
        match result:
            case None:
                n_skip += 1
            case True:
                n_ok += 1
            case False:
                print(f"FAIL: {path}")
                n_fail += 1

    action = 'updated' if args.update else 'ok'
    print(
        f"\n{n_ok} {action}, {n_fail} failed, "
        f"{n_skip} skipped (no markers)."
    )
    return 0 if n_fail == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
