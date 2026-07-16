#!/usr/bin/env python3
"""Small behaviors shared by the tools/*.py scripts.

Complements tools_config.py's constants: where that module holds *what* the
repo's layout and conventions are, this module holds the small pieces of
behavior that read them the same way in more than one script (walking
Chapters/, reading a norun.txt-style glob list, naming a block's extracted
path, running a subprocess and reporting whether it succeeded).

Named tools_* rather than the shorter config/repo so it can never collide
with a book listing of the same name: a chapter's own example file can be
"config.py" or "repo.py" (chapter 24's Singleton demo has one), and Python's
sys.modules cache would silently resolve that chapter's ``import config`` to
this module instead once this module had already been imported once in the
process, which is exactly what validate_output.py does while running every
block in a single process.
"""

import argparse
import shutil
import subprocess
from pathlib import Path

from tools_config import CHAPTERS_DIR, PATH_LINE_RE


def md_files(paths: list[str | Path] | None = None) -> list[Path]:
    """Markdown files named directly, or every *.md in a named directory.

    Defaults to CHAPTERS_DIR when `paths` is empty or None.
    """
    files: list[Path] = []
    for p in (paths or [CHAPTERS_DIR]):
        path = Path(p)
        files.extend(sorted(path.glob("*.md")) if path.is_dir() else [path])
    return files


def add_paths_arg(ap: argparse.ArgumentParser) -> None:
    ap.add_argument(
        "paths", nargs="*",
        help="Markdown files or directories (default: Chapters/)",
    )


def block_slug(block: list[str]) -> str | None:
    """The relative path a block names on its first content line, if any.

    A slug starting with "utils/" is the caller's cue that the file lands
    at the tree root's utils/ directory rather than a chapter directory.
    """
    for line in block:
        if line.strip():
            m = PATH_LINE_RE.match(line.rstrip('\n\r'))
            if not m:
                return None
            return m.group(1).replace('\\', '/')
    return None


def load_glob_list(path: Path) -> list[str]:
    """Forward-slash glob patterns from a norun.txt-style file.

    Blank lines and `#`-prefixed comments (including a trailing `# comment`
    on a pattern line) are ignored.
    """
    if not path.exists():
        return []
    out: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            out.append(line.replace("\\", "/"))
    return out


def write_text_lf(path: Path, text: str) -> None:
    """Write `text` to `path` as UTF-8 with LF line endings.

    newline="\\n" keeps endings LF even on Windows; the line-endings gate
    rejects CRLF.
    """
    path.write_text(text, encoding="utf-8", newline="\n")


def run_capture(
    cmd: list[str], *, timeout: float = 30, combine_stderr: bool = False,
) -> tuple[str, int] | None:
    """Run `cmd`, capturing output. None if the binary is missing or won't start.

    Otherwise (output, returncode): stdout alone, or stdout-or-stderr when
    `combine_stderr` is set (some tools print their version to stderr).
    """
    if shutil.which(cmd[0]) is None:
        return None
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except OSError:
        return None
    output = (proc.stdout or proc.stderr) if combine_stderr else (proc.stdout or "")
    return output, proc.returncode


def run_echoed(cmd: list[str], *, check: bool = False) -> bool:
    """Print `$ cmd...`, run it, and return whether it succeeded.

    With check=True a nonzero exit raises (subprocess.run's own default),
    for a caller that wants to abort rather than continue past a failure.
    """
    print(f"$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd, check=check)
    except OSError:
        return False
    return proc.returncode == 0
