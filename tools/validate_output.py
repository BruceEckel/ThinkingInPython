#!/usr/bin/env python3
"""Validate and update #: output markers in Python example files.

Lines starting with #: at column 0 mark expected stdout output.
Each #: block is compared to the stdout produced by the
top-level code above it (since the previous #: block):

    print("Hello")
    #: Hello
    print("world")
    #: world

A lone bare "#:" (no text after it) is a not-yet-filled-in placeholder. It
is always filled in with the actual output, even without --update, so you
can write a listing, leave "#:" under it, and run the checker to fill it
in. A bare "#:" that sits alongside other #: lines is instead a literal
blank line within a multi-line output, and is checked normally.

The same markers can be validated and updated directly inside the book's
Markdown. Each ```python fenced block is treated as one program: its code is
run and the #: lines inside the block are rewritten in place. A block is run
from its extracted chapter directory (build/examples/<chapter>/), so imports of
sibling files and relative data paths resolve the way the book assumes. Run
`tools/extract_examples.py --write` first so that tree exists.

Markers in the listings named by tools/data/timing.txt are treated as
claims rather than observations: those listings print booleans derived
from wall-clock thresholds, so a single run that disagrees with the
committed marker is evidence of a transient (a scheduler burst, another
process on the machine), not of the book being wrong. A claim marker is
never auto-rewritten, even under --update. On a mismatch the block is
rerun, up to CLAIM_ATTEMPTS times in all, and passes as soon as one run
matches the committed text; only a marker that misses every run is
reported as a failure, and then the fix is a human decision: repair the
listing, or change the marker by hand.

Files are processed in parallel, one fresh interpreter per file. That is
not only for speed: running every chapter in one shared process is what
let an orphaned asyncio task wedge a later chapter's asyncio.run(), and
what let a reference-cycled class's __del__ fire while an unrelated
chapter's stdout was being captured. A file that gets its own process
cannot do either. Use -j 1 to go back to one process for everything,
which is the right setting when debugging a block that misbehaves.

Each of those processes is watched. A file that reports nothing within
--file-timeout seconds has its process killed and is run again, up to
FILE_ATTEMPTS times in all, because a listing can hang before it runs a
line of its own code: on Windows asyncio.run() builds the event loop's
self-pipe with socket.socketpair(), CPython emulates that with a
loopback TCP connection, and the emulation's accept() blocks forever
when the connect fails silently. On 2026-09-29 that hung two of twelve
whole-book runs on an idle machine, with one worker inside accept() and
the rest of the pool waiting for it. -j 1 runs in this process and has
no watchdog.

A Markdown file whose markers pass has its digest recorded in
build/marker-stamp.json. With --changed-only, a Markdown file whose digest
still matches is skipped: its text, the utils/ helpers, and the tools are
all as they were when its markers last passed, so its listings print what
they printed then. tools/skip_stamps.py says what the digest covers.
`tip output` passes it; TIP_FULL=1 in the environment overrides it.

Usage:
    python -m tools.validate_output file.py        # check one file
    python -m tools.validate_output Examples/      # check directory
    python -m tools.validate_output chapter.md     # check Markdown listings
    python -m tools.validate_output --update file.py   # rewrite markers
    python -m tools.validate_output --update Chapters/ # rewrite the book
    python -m tools.validate_output -j 1 Chapters/     # serial, one process
    python -m tools.validate_output --update --changed-only Chapters/
"""

import argparse
import contextlib
import fnmatch
import functools
import gc
import io
import multiprocessing
import os
import re
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.connection import Connection
from pathlib import Path

from tools.config import EXAMPLES_TREE as DEFAULT_TREE, utils_dir
from tools.skip_stamps import (
    forced_full, marker_context, markers_current, record_markers)
from tools.config import INLINE_NORUN_MARKER, NORUN_FILE, TIMING_FILE
from tools.pycode import walk_fenced
from tools.repo import add_jobs_arg, block_slug, load_glob_list, write_text_lf

# Matches #: or #: <content> at column 0 only.
MARKER_RE = re.compile(r'^#:(?: (.*))?$')

# Total runs a claim-marker listing (tools/data/timing.txt) gets before
# a mismatch counts as real. Three: a transient misses once, a genuine
# change misses every time, and each run already takes a min over
# repeats internally.
CLAIM_ATTEMPTS = 3

# Seconds a file's process gets to report before it is killed and the
# file run again. A chapter takes under ten seconds with the machine to
# itself, so this passes only for a process that is stuck.
FILE_TIMEOUT = 120.0

# Total runs a file gets before a hang counts as a failure.
FILE_ATTEMPTS = 3

type Outcome = tuple[bool | None, str]
type Work = Callable[[Path], Outcome]


def is_claim(rel: str | None, claims: list[str]) -> bool:
    """Whether `rel` (chapter/slug) names a claim-marker listing."""
    return bool(rel) and any(
        fnmatch.fnmatch(rel, pat) for pat in claims
    )


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


def collect_now() -> None:
    """Force cyclic garbage from the just-finished block to finalize now.

    A class defined in a block's globals refers back to that dict through
    ``SomeClass.some_method.__globals__``, so the dict and the class form a
    reference cycle that plain refcounting can never free. Left alone, it
    waits for gc's next pass, which can land arbitrarily later, while some
    unrelated block's stdout is captured. The caller must drop its own
    last reference (``del namespace``) before calling this, so the cycle
    is truly unreachable and collects here, with real stdout in place,
    instead of leaking a stray ``__del__`` print into the next block.
    """
    gc.collect()


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
            # A lone bare "#:" is a not-yet-filled-in placeholder (not a
            # claim that the output is empty), so it is always filled in,
            # even outside --update. A bare "#:" alongside other marker
            # lines is a literal blank output line instead, and is checked
            # normally.
            placeholder = (
                len(chunk_lines) == 1
                and chunk_lines[0].rstrip('\n\r') == '#:'
            )

            if chunk_lines == canonical:
                new_lines.extend(chunk_lines)
            elif (update or placeholder) and not had_error:
                new_lines.extend(canonical)
                changed = True
                if placeholder and not update:
                    print(f"  line {lineno}: filled in placeholder '#:'")
            else:
                new_lines.extend(chunk_lines)
                if not had_error:
                    print(f"  line {lineno}:")
                    print(f"    have: {''.join(chunk_lines)!r}")
                    print(f"    want: {''.join(canonical)!r}")
                    ok = False

            pending = None

    return new_lines, ok, changed


def process_file(
    path: Path, *, update: bool, claims: list[str] | None = None,
) -> bool | None:
    """Check or update one .py file.

    Returns None  - no #: markers found (file skipped)
            True  - all markers match (or file was updated successfully)
            False - mismatch or execution error
    """
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)

    if not any(is_marker(line) for line in lines):
        return None

    rel = '/'.join(path.parts[-2:])
    attempts = CLAIM_ATTEMPTS if is_claim(rel, claims or []) else 1
    for attempt in range(1, attempts + 1):
        namespace: dict = {'__name__': '__main__', '__file__': str(path)}
        new_lines, ok, changed = process_block(
            lines, str(path),
            update=update and attempts == 1,
            namespace=namespace,
        )
        del namespace
        collect_now()
        if ok or attempt == attempts:
            break
        print(f"  claim marker mismatch; rerunning "
              f"({attempt + 1}/{attempts})")
    if attempts > 1 and not ok:
        print(f"  claim marker missed all {attempts} runs; not "
              "rewritten (see tools/data/timing.txt)")

    # changed can be True here with update=False only via the placeholder
    # fill-in above, which should persist regardless of --update. A claim
    # file keeps its committed markers unless a run matched them.
    if changed and (attempts == 1 or ok):
        write_text_lf(path, ''.join(new_lines))

    return ok


@contextlib.contextmanager
def run_location(rundir: Path | None, root: Path | None = None):
    """Run a block from ``rundir`` (cwd + sys.path), leaving no trace.

    Imports of sibling extracted files and relative data paths resolve as they
    do under run_examples. The tree's utils/ directory is also placed on
    sys.path so a block can import shared helpers (such as display.py) kept
    there. sys.path and any modules imported by the block are restored
    afterward so one block cannot leak into the next.
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
    claims: list[str] | None = None,
) -> bool | None:
    """Check or update the #: markers in a Markdown file's python listings.

    Returns None  - no python block carries #: markers (file skipped)
            True  - every marked block matches (or was updated)
            False - a mismatch or execution error in some block
    """
    skips = skips or []
    claims = claims or []
    chapter = path.stem
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)

    out: list[str] = []
    ok = True
    changed = False
    any_markers = False
    n = len(lines)

    for ev in walk_fenced(
        lines, wanted=lambda m: (m.group(1) or '') in ('python', 'py'),
    ):
        if ev.match is None:
            out.append(lines[ev.open_at])
            continue

        block_start = ev.open_at + 1
        block = lines[block_start:ev.end]
        fence_close = lines[ev.end] if ev.end < n else None

        out.append(lines[ev.open_at])  # opening fence
        if any(is_marker(line) for line in block):
            result = process_md_block(
                block, path, chapter, block_start,
                tree=tree, skips=skips, claims=claims, update=update,
            )
            any_markers = True
            ok = ok and result.ok
            changed = changed or result.changed
            out.extend(result.lines)
        else:
            out.extend(block)
        if fence_close is not None:
            out.append(fence_close)

    if not any_markers:
        return None
    # changed can be True here with update=False only via a placeholder
    # fill-in, which should persist regardless of --update.
    if changed:
        write_text_lf(path, ''.join(out))
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
    claims: list[str] | None = None,
) -> BlockResult:
    """Run one ```python block and check or rewrite its #: markers."""
    slug = block_slug(block)
    if slug is None:
        rel: str | None = None
        filepath: Path | None = None
    elif slug.startswith('utils/'):
        rel = slug
        filepath = tree / rel
    else:
        rel = f'{chapter}/{slug}'
        filepath = tree / chapter / slug
    text = ''.join(block)

    if INLINE_NORUN_MARKER in text or (
        rel and any(fnmatch.fnmatch(rel, pat) for pat in skips)
    ):
        # GUI/interactive/infinite-loop listing: cannot run unattended.
        return BlockResult(block, ok=True, changed=False)

    rundir = filepath.parent if filepath else None
    label = f'{path}:{rel}' if rel else str(path)
    attempts = CLAIM_ATTEMPTS if is_claim(rel, claims or []) else 1

    for attempt in range(1, attempts + 1):
        namespace: dict = {
            '__name__': '__main__',
            '__file__': str(filepath) if filepath else str(path),
        }
        with run_location(rundir, utils_dir(tree)):
            new_lines, ok, changed = process_block(
                block, label,
                update=update and attempts == 1,
                namespace=namespace, line_offset=block_start,
            )
        del namespace
        collect_now()
        if ok or attempt == attempts:
            break
        print(f"  {label}: claim marker mismatch; rerunning "
              f"({attempt + 1}/{attempts})")

    if attempts > 1 and not ok:
        print(f"  {label}: claim marker missed all {attempts} runs; "
              "not rewritten (see tools/data/timing.txt)")
        # Keep the committed markers: a claim is never auto-rewritten.
        return BlockResult(block, ok=False, changed=False)
    return BlockResult(new_lines, ok, changed)


def process_one(
    path: Path, *, update: bool, tree: Path, skips: list[str],
    claims: list[str] | None = None,
) -> tuple[bool | None, str]:
    """Process one file, returning its result and everything it printed.

    This is the unit of work a worker process runs, and the reason the
    parallel path is a *process* pool rather than a thread pool: running a
    block mutates interpreter-global state (cwd via ``run_location``,
    ``sys.path``, ``sys.modules``), which threads would share and corrupt.

    stdout is captured instead of printed so the parent can emit each
    file's diagnostics as one contiguous group in a fixed order, whatever
    order the workers happen to finish in.
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if path.suffix == '.md':
            result = process_markdown(
                path, update=update, tree=tree, skips=skips,
                claims=claims,
            )
        else:
            result = process_file(path, update=update, claims=claims)
    return result, buf.getvalue()


def report_to(send: Connection, work: Work, path: Path) -> None:
    """What a file's process runs: do the work, send back the outcome."""
    try:
        send.send(work(path))
    finally:
        send.close()


def run_watched(
    path: Path, *, work: Work, timeout: float = FILE_TIMEOUT,
    attempts: int = FILE_ATTEMPTS,
) -> Outcome:
    """Run `work(path)` in a process of its own, rerunning one that hangs.

    The process is spawned, so it starts with a fresh interpreter, and it
    is killed when it reports nothing within `timeout` seconds. A hung
    run wrote nothing: a Markdown file's markers are rewritten only
    after every block in it has run.
    """
    ctx = multiprocessing.get_context('spawn')
    notes = ''
    for attempt in range(1, attempts + 1):
        recv, send = ctx.Pipe(duplex=False)
        proc = ctx.Process(target=report_to, args=(send, work, path))
        proc.start()
        send.close()  # The child holds the only writing end now
        try:
            if recv.poll(timeout):
                result, output = recv.recv()
                proc.join()
                return result, notes + output
        except EOFError:
            # The pipe closed with nothing in it: the process died.
            proc.join()
            return False, notes + (
                f"  {path}: its process exited with code "
                f"{proc.exitcode} before reporting\n")
        finally:
            recv.close()
        proc.kill()
        proc.join()
        notes += f"  {path}: no result after {timeout:g}s"
        if attempt < attempts:
            notes += f"; rerunning ({attempt + 1}/{attempts})\n"
    return False, notes + f"; hung in all {attempts} runs\n"


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
    ap.add_argument(
        '--changed-only', action='store_true',
        help='skip a Markdown file unchanged since its markers last '
             'passed (see tools/skip_stamps.py)',
    )
    ap.add_argument(
        '--file-timeout', type=float, default=FILE_TIMEOUT, metavar='SEC',
        help='seconds a file gets before its process is killed and the '
             f'file rerun (default: {FILE_TIMEOUT:g}); unused with -j 1',
    )
    add_jobs_arg(ap, 'files')
    args = ap.parse_args(argv)

    # run_location() puts the tree on sys.path and then chdir()s into the
    # chapter directory, so a relative --tree stops resolving the moment
    # the chdir happens and every sibling import fails. run_examples.py has
    # the same trap; here it is fixed once for every caller.
    args.tree = args.tree.resolve()

    files = collect_files(args.targets)
    if not files:
        print("No .py or .md files found.")
        return 1
    context = marker_context(args.tree, utils_dir(args.tree))
    unchanged: list[Path] = []
    if args.changed_only and not forced_full():
        unchanged = [f for f in files
                     if f.suffix == '.md' and markers_current(f, context)]
        files = [f for f in files if f not in unchanged]
        if not files:
            print(f"All {len(unchanged)} file(s) unchanged since their "
                  "markers last passed.")
            return 0

    skips = load_glob_list(NORUN_FILE)
    claims = load_glob_list(TIMING_FILE)
    work = functools.partial(
        process_one, update=args.update, tree=args.tree, skips=skips,
        claims=claims,
    )

    # One fresh process per file, not a pool of reused workers. Files are
    # independent, but a worker that ran several would share what a block
    # left behind: an orphaned asyncio task can wedge a later
    # asyncio.run(), and a class caught in a reference cycle can have its
    # __del__ fire while an unrelated file's stdout is captured. Both are
    # documented traps of the old single-process run, and both stop
    # existing when a file gets an interpreter to itself. The threads
    # here only wait: each starts a file's process and watches it.
    jobs = min(max(1, args.jobs), len(files))
    if jobs == 1:
        outcomes = map(work, files)
    else:
        watched = functools.partial(
            run_watched, work=work, timeout=args.file_timeout)
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            # map() yields in submission order, so output stays in file
            # order and the run is reproducible.
            outcomes = list(pool.map(watched, files))

    n_ok = n_fail = n_skip = 0
    passed: list[Path] = []
    for path, (result, output) in zip(files, outcomes, strict=True):
        if args.verbose:
            print(path)
        if output:
            print(output, end='')
        match result:
            case None:
                n_skip += 1
                passed.append(path)
            case True:
                n_ok += 1
                passed.append(path)
            case False:
                print(f"FAIL: {path}")
                n_fail += 1

    record_markers([p for p in passed if p.suffix == '.md'], context)
    action = 'updated' if args.update else 'ok'
    unchanged_note = (f", {len(unchanged)} unchanged since their last pass"
                      if unchanged else "")
    print(
        f"\n{n_ok} {action}, {n_fail} failed, "
        f"{n_skip} skipped (no markers){unchanged_note}."
    )
    return 0 if n_fail == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
