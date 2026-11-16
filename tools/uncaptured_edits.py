"""Print a short notice of prose edits nobody has learned from yet.

The standing rule (CLAUDE.md, "Learning from editing passes"): every
edit to the book's prose is a lesson, and the session files it under
the `super-prose` skill. A session can only learn from an edit it
notices, and the author often edits in his own editor and commits
himself, so a new session starts with no sign those edits exist.

This module finds them with two tests, for prose files only
(`Chapters/*.md` and `Solutions/*/README.md`):

- Commits reachable from HEAD, made after a marker commit, that change
  a prose file and whose message has no `Co-Authored-By:` line. The
  session's own commits end with that trailer; the author's do not.
  The marker is the commit named in `tools/data/edits_read_through.txt`
  (comment lines starting with `#`, then one full commit hash) when
  that file exists, parses, and names an ancestor of HEAD. Otherwise
  it is the last commit that touched `bruce_edit_db.md`, the store of
  lessons. That fallback has a hole: a hand commit made before a later
  session commit that touches `bruce_edit_db.md` falls behind the
  marker unread, so the file is the explicit record that every
  trailer-less prose commit up to its hash has been read.
- Uncommitted prose files (modified, added, or untracked), from
  `git status`.

Open editing passes (local tags `edit-start-NN`, or `edit-start-A` for
an appendix) are noted beside the
files they hold. The notice is empty when there is nothing to report,
when `bruce_edit_db.md` has no commit, or when git fails: the
SessionStart hook that runs this module must never fail a session.

`--mark` writes HEAD's full hash to the marker file, after the session
has read the listed commits and filed their lessons.

The module uses only the standard library and imports nothing from
`tools.*`, so the hook cannot fail on an import.

Usage:

    uv run python -m tools.uncaptured_edits
    uv run tip uncaptured
    uv run tip uncaptured ARGS=--mark
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = "bruce_edit_db.md"
MARKER_FILE = "tools/data/edits_read_through.txt"
HASH = re.compile(r"[0-9a-f]{40,64}")
LIMIT = 8
TIMEOUT = 5
TRAILER = re.compile(r"^co-authored-by:", re.IGNORECASE | re.MULTILINE)
NUMBERED = re.compile(r"^(\d\d|[A-Z])_")
RECORD = "\x1e"
FIELD = "\x1f"


@dataclass(frozen=True)
class Commit:
    short: str
    date: str
    subject: str
    files: tuple[str, ...]


def is_prose(path: str) -> bool:
    """True for `Chapters/*.md` and `Solutions/*/README.md`."""
    parts = path.replace("\\", "/").split("/")
    if len(parts) == 2:
        return parts[0] == "Chapters" and parts[1].endswith(".md")
    return len(parts) == 3 and parts[0] == "Solutions" and parts[2] == "README.md"


def has_trailer(message: str) -> bool:
    """True when a line of the message starts `Co-Authored-By:`."""
    return TRAILER.search(message) is not None


def open_pass(path: str, passes: set[str]) -> str | None:
    """The open pass number that holds this file, if any."""
    parts = path.replace("\\", "/").split("/")
    name = parts[1] if len(parts) == 3 else parts[-1]
    found = NUMBERED.match(name)
    if found and found.group(1) in passes:
        return found.group(1)
    return None


def parse_log(text: str) -> list[Commit]:
    """Parse `git log` output built with `RECORD`/`FIELD` separators.

    Each record is `hash FIELD date FIELD subject FIELD body FIELD`,
    then the `--name-only` file lines. Commits that carry a trailer or
    change no prose file are dropped.
    """
    commits: list[Commit] = []
    for record in text.split(RECORD):
        if not record.strip():
            continue
        fields = record.split(FIELD)
        if len(fields) < 5:
            continue
        short, date, subject, body, rest = fields[:5]
        if has_trailer(subject + "\n" + body):
            continue
        files = tuple(
            line.strip() for line in rest.splitlines()
            if line.strip() and is_prose(line.strip())
        )
        if files:
            commits.append(Commit(short.strip(), date, subject, files))
    return commits


def parse_status(text: str) -> list[str]:
    """Prose paths from `git status --porcelain -z` output."""
    entries = text.split("\0")
    paths: list[str] = []
    skip = False
    for entry in entries:
        if skip:
            skip = False
            continue
        if len(entry) < 4:
            continue
        code, path = entry[:2], entry[3:]
        if "R" in code or "C" in code:
            skip = True
        if is_prose(path):
            paths.append(path)
    return paths


def parse_marker(text: str) -> str | None:
    """The commit hash in a marker file's text, or None if it is bad."""
    lines = [
        line.strip() for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(lines) != 1 or not HASH.fullmatch(lines[0]):
        return None
    return lines[0]


def marker_text(head: str) -> str:
    return (
        "# Prose edits read through the commit below: every trailer-less\n"
        "# prose commit up to and including it has been read.\n"
        "# `tip uncaptured ARGS=--mark` rewrites it after the session has\n"
        "# read the listed commits. See tools/uncaptured_edits.py.\n"
        f"{head}\n")


def _more(shown: int, total: int) -> str:
    return f" ... and {total - shown} more" if total > shown else ""


def _file_list(files: list[str], passes: set[str]) -> str:
    shown = []
    for path in files[:LIMIT]:
        number = open_pass(path, passes)
        shown.append(path if number is None else f"{path} (open pass {number})")
    return ", ".join(shown) + _more(len(shown), len(files))


def format_notice(
    commits: list[Commit],
    tree: list[str],
    passes: set[str],
    since: str = "",
    via_file: bool = False,
) -> str:
    """The notice text, or an empty string when there is nothing."""
    if not commits and not tree:
        return ""
    lines = ['Edits not yet learned from (CLAUDE.md, "Every edit is a lesson"):']
    if commits:
        count = len(commits)
        noun = "commit" if count == 1 else "commits"
        mark = ""
        if since and via_file:
            mark = f" since {since} ({MARKER_FILE})"
        elif since:
            mark = f" since {since} last touched {DB_FILE}"
        lines.append(f"{count} {noun} with no Co-Authored-By trailer{mark}:")
        for commit in commits[:LIMIT]:
            files = ", ".join(commit.files[:3])
            if len(commit.files) > 3:
                files += f", +{len(commit.files) - 3}"
            lines.append(
                f"  {commit.short} {commit.date} {commit.subject} ({files})")
        if count > LIMIT:
            lines.append(f"  ... and {count - LIMIT} more")
    if tree:
        lines.append("Working tree: " + _file_list(tree, passes))
        held = sorted({n for p in tree if (n := open_pass(p, passes))})
        for number in held:
            lines.append(
                f"  The edit-start-{number} tag holds pass {number} "
                f"until /edit-done {number}.")
    lines.append(
        'Read each diff, file its lesson under the super-prose skill\'s '
        '"Every edit feeds this skill", and leave a sentence he is still '
        "typing alone. After reading the commits and filing their lessons, "
        "run `uv run tip uncaptured ARGS=--mark`.")
    return "\n".join(lines)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True,
        encoding="utf-8", timeout=TIMEOUT, check=True)
    return result.stdout


def read_marker(root: Path) -> str | None:
    """The marker file's commit if it names an ancestor of HEAD."""
    try:
        text = (root / MARKER_FILE).read_text(encoding="utf-8")
        commit = parse_marker(text)
        if commit is None:
            return None
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root, capture_output=True, text=True, encoding="utf-8",
            timeout=TIMEOUT)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return commit if result.returncode == 0 else None


def write_marker(root: Path = ROOT) -> str:
    """Write HEAD's hash to the marker file; return the short hash."""
    head = git(root, "rev-parse", "HEAD").strip()
    path = root / MARKER_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(marker_text(head), encoding="utf-8", newline="\n")
    return head[:7]


def build_notice(root: Path = ROOT) -> str:
    """Gather the facts from git in `root` and format the notice."""
    try:
        marker = read_marker(root)
        via_file = marker is not None
        if marker is None:
            marker = git(
                root, "log", "-1", "--format=%H", "--", DB_FILE).strip()
        if not marker:
            return ""
        log = git(
            root, "log", f"{marker}..HEAD", "--name-only",
            "--date=short",
            f"--format={RECORD}%h{FIELD}%ad{FIELD}%s{FIELD}%b{FIELD}")
        status = git(root, "status", "--porcelain", "-z", "-uall")
        tags = git(root, "tag", "-l", "edit-start-*").split()
    except (OSError, subprocess.SubprocessError):
        return ""
    passes = {t.removeprefix("edit-start-") for t in tags}
    return format_notice(
        parse_log(log), parse_status(status), passes, marker[:7], via_file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "--mark", action="store_true",
        help="record HEAD as read through, in " + MARKER_FILE)
    args = parser.parse_args(argv)
    if args.mark:
        try:
            short = write_marker(ROOT)
        except (OSError, subprocess.SubprocessError) as error:
            print(f"Could not write the marker: {error}")
            return 1
        print(f"Marked prose edits read through {short}.")
        return 0
    notice = build_notice(ROOT)
    if notice:
        print(notice)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
