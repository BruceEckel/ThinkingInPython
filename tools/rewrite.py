#!/usr/bin/env python3
"""Run the AI editing passes over chapters' prose (`make rewrite CH=25`).

Each pass is one headless `claude -p "/<skill> <chapter>"` run: a skill
from this repo (`.claude/skills/`) or an installed plugin, applied to the
chapter file in place with `--permission-mode acceptEdits`, so it needs
no terminal and no confirmation. `--model` picks the model for every
pass (`make rewrite MODEL=claude-sonnet-5`); the default is
`DEFAULT_MODEL` below, Opus, because the passes' failure mode is
over-editing and restraint is what the stronger model buys. Each pass
header prints the model so a diff can be traced to it. After every pass
the chapter is reflowed (`reflow_prose.py --write`) and the cheap prose
gates run (`banned_phrases.py` and `heading_links.py` on that chapter,
then the book-wide `extract_examples.py` drift check), so a pass that
touched a listing, broke a link, or added a banned phrase fails right
there, not at the next `make verify`. A chapter's chain stops at its
first failure.

Several chapters run in parallel by default (`CH="25 28 30"`), one
pass chain per chapter, up to `--jobs` at once. Each chain writes only
its own chapter, and its banned-phrase and link checks read only that
chapter, so chains never fail each other; the drift check is book-wide
because a changed listing anywhere is a problem whichever chain caused
it, and its message says so. In parallel mode each chain's output is
captured and printed per step under a `[NN]` prefix instead of
interleaving. `--serial` runs the chapters one after another with
output streamed as it happens, the mode to use when watching a pass
work.

The passes live in `PASSES` below, in the order they run. Adding a tool
is appending an entry. A pass with `default=True` runs on a bare `make
rewrite`; the rest are opt-in. `--also NAME ...` adds opt-in passes to
the defaults, `--passes NAME ...` runs only the passes named (replacing
the default set), and `--all` runs every pass. A pass whose own rules
say "only when explicitly asked" (`readability`) stays off until one of
those names it, which counts as asking.

This is not a gate. Each run costs tokens and is nondeterministic, so it
never joins `verify`/`gate`/`ci`, it refuses to run under `CI`, and
`verify_targets.py` excludes it. Each pass runs once per invocation, by
design: Strunk's Rule 13 has no floor, and repeated cut-passes sand the
voice off a chapter. Rerun `make rewrite` by hand for a second lap, and
review the diff before committing.

Usage:
    python tools/rewrite.py 25                # default passes on chapter 25
    python tools/rewrite.py 25 28 30          # three chapters, in parallel
    python tools/rewrite.py 30-40             # a range, inclusive
    python tools/rewrite.py 25 28 --serial    # the same, one at a time
    python tools/rewrite.py --list            # show the passes, run nothing
    python tools/rewrite.py 25 --dry-run      # print the commands only
    python tools/rewrite.py 25 --also activate    # defaults + activate
    python tools/rewrite.py 25 --passes activate  # activate only
    python tools/rewrite.py 25 --model claude-sonnet-5
    python tools/rewrite.py Chapters/25_Patterns--Template_Method.md --all
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from reflow_prose import _resolve
from tools_config import ROOT


@dataclass(frozen=True)
class Pass:
    name: str
    skill: str  # the slash command, without the leading "/"
    what: str
    default: bool = False


# Ordered: general rules first, the most specific (Bruce's own captured
# practices) last, so a later pass never has its work undone by an
# earlier, blunter one. The two cutting passes (elements-of-style,
# activate) go before the five that only rephrase or reorder (literal,
# positive, straighten, cohesion, antecedents). The three sentence-level
# passes run in the order say-what, then build-how: literal replaces a
# figure with the mechanism, positive turns a negation around (which
# often shortens the sentence straighten would otherwise restructure),
# and straighten fixes what is left. cohesion and antecedents come last
# because they clean up after a split sentence, and cohesion precedes
# antecedents because moving a sentence can change what a pronoun points
# at.
PASSES: tuple[Pass, ...] = (
    Pass(
        "elements-of-style",
        "elements-of-style:writing-clearly-and-concisely",
        "Strunk: active voice, positive form, omit needless words",
        default=True,
    ),
    Pass(
        "activate",
        "activate",
        "active register: clear passive, there-is, and weak-verb warnings",
    ),
    Pass(
        "literal",
        "literal",
        "say what the machinery does: a literal verb for each figure",
        default=True,
    ),
    Pass(
        "positive",
        "positive",
        "say what happens, not what does not: keep only the negations that claim",
        default=True,
    ),
    Pass(
        "straighten",
        "straighten",
        "one sentence, one load: name the actor, split at the seam",
        default=True,
    ),
    Pass(
        "cohesion",
        "cohesion",
        "old before new: one topic string per paragraph, news at the end",
        default=True,
    ),
    Pass(
        "antecedents",
        "antecedents",
        "name what each this/it/which points at when two things could",
        default=True,
    ),
    Pass(
        "readability",
        "readability",
        "remove AI-writing tells (off by default; naming it here is the ask)",
    ),
    Pass(
        "bruce-edit-apply",
        "bruce-edit-apply",
        "apply the promoted rules in bruce_edit_db.md",
        default=True,
    ),
)

# The model every pass runs on unless --model says otherwise. Opus: the
# passes edit an author's voice, and the cost of a pass that cuts too
# much is higher than the token difference on one chapter.
DEFAULT_MODEL = "claude-opus-5"

# How many chapters run at once in parallel mode. Each is a live
# `claude` session, so this caps tokens in flight, not CPU.
DEFAULT_JOBS = 4

# What the headless run may do. Read/Grep/Glob to read the skill's own
# reference files and the chapter; Edit/Write for the chapter; `uv run`
# so a skill that verifies its work with a repo tool can. No git, so a
# pass can never commit.
ALLOWED_TOOLS = ("Read", "Edit", "Write", "Grep", "Glob", "Bash(uv run *)")

SCOPE_NOTE = (
    "You are running as one pass of tools/rewrite.py. Edit only the "
    "chapter file named in the prompt. Never change a fenced code block "
    "or a line starting with #: (an output marker); prose only. Do not "
    "run git. Do not ask questions; there is no one to answer. When "
    "done, stop."
)

# (label, argv, scoped) triples run after every pass, in order; the
# first nonzero exit stops that chapter's chain. reflow first, so the
# gates see settled lines. A scoped check gets the chapter path
# appended, so parallel chains never read each other's chapter.
CHECKS: tuple[tuple[str, tuple[str, ...], bool], ...] = (
    ("reflow", ("tools/reflow_prose.py", "--write"), True),
    ("banned phrases", ("tools/banned_phrases.py",), True),
    ("heading links", ("tools/heading_links.py",), True),
    ("examples in sync", ("tools/extract_examples.py",), False),
)

DRIFT_NOTE = (
    "a fenced listing somewhere in Chapters/ no longer matches Examples/; "
    "if another rewrite is running, its chapter may be the one that changed"
)


def claude_argv(
    claude: str, skill: str, chapter: Path, model: str
) -> list[str]:
    """The headless invocation for one pass."""
    return [
        claude,
        "-p",
        f"/{skill} {chapter.as_posix()}",
        "--model",
        model,
        "--permission-mode",
        "acceptEdits",
        "--allowedTools",
        *ALLOWED_TOOLS,
        "--append-system-prompt",
        SCOPE_NOTE,
    ]


def chapter_tag(chapter: Path) -> str:
    """`[25]` from `Chapters/25_Patterns--Template_Method.md`, for parallel output."""
    return f"[{chapter.stem.split('_', 1)[0]}]"


class Reporter:
    """Where one chapter's chain sends its output.

    Serial mode streams each subprocess to the terminal as it runs.
    Parallel mode captures each step and prints it whole under the
    chapter's tag, so two chains' lines never interleave.
    """

    def __init__(self, chapter: Path, capture: bool) -> None:
        self.tag = chapter_tag(chapter)
        self.capture = capture

    def say(self, text: str) -> None:
        prefix = f"{self.tag} " if self.capture else ""
        print(prefix + text, flush=True)

    def run(self, argv: list[str], label: str) -> int:
        """Run argv; return its exit code. Output goes to the terminal
        directly, or is captured and printed under the tag."""
        self.say(f"--- {label}")
        if not self.capture:
            return subprocess.run(argv, cwd=ROOT).returncode
        done = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
        for line in (done.stdout + done.stderr).splitlines():
            self.say(line)
        return done.returncode


def changed_lines(chapter: Path) -> str:
    """`git diff --stat` for the chapter, or an empty string if clean."""
    out = subprocess.run(
        ["git", "diff", "--stat", "--", chapter.as_posix()],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return out.splitlines()[-1].strip() if out else ""


def checks_after(chapter: Path, python: list[str], out: Reporter) -> bool:
    """Reflow the chapter and run the prose gates; False on the first failure."""
    for label, argv, scoped in CHECKS:
        full = [*python, *argv]
        if scoped:
            full.append(chapter.as_posix())
        if out.run(full, f"check: {label}") != 0:
            why = (DRIFT_NOTE if label == "examples in sync"
                   else "after the pass; the chapter is left as is")
            out.say(f"FAILED: {label} ({why})")
            return False
    return True


def rewrite_chapter(
    chapter: Path,
    selected: list[Pass],
    claude: str,
    python: list[str],
    model: str,
    dry_run: bool,
    capture: bool,
) -> bool:
    """Run every selected pass over one chapter; False if any step failed."""
    out = Reporter(chapter, capture)
    if not dry_run and changed_lines(chapter):
        out.say(f"note: {chapter.as_posix()} already has uncommitted "
                "changes; the per-pass diff below includes them")
    for p in selected:
        argv = claude_argv(claude, p.skill, chapter, model)
        if dry_run:
            out.say(subprocess.list2cmdline(argv))
            continue
        code = out.run(argv, f"pass: {p.name} on {model} ({p.what})")
        if code != 0:
            out.say(f"FAILED: pass {p.name} exited {code}; stopping")
            return False
        if not checks_after(chapter, python, out):
            return False
        out.say(f"after {p.name}: {changed_lines(chapter) or 'no change'}")
    if not dry_run:
        out.say(f"done: {len(selected)} pass(es) on {model} over "
                f"{chapter.as_posix()}; review `git diff` before committing")
    return True


_RANGE = re.compile(r"^(\d+)-(\d+)$")


def expand_specs(specs: list[str]) -> list[str]:
    """Split comma-separated specs and expand numeric ranges: `30-32`
    becomes `30`, `31`, `32`, zero-padded to two digits so `5-7`
    resolves `05`..`07` by prefix rather than by substring."""
    out: list[str] = []
    for spec in (s for arg in specs for s in arg.split(",") if s):
        m = _RANGE.match(spec)
        if not m:
            out.append(spec)
            continue
        lo, hi = int(m.group(1)), int(m.group(2))
        if lo > hi:
            raise SystemExit(f"rewrite: range {spec!r} runs backwards")
        out.extend(f"{n:02d}" for n in range(lo, hi + 1))
    return out


def resolve_chapters(specs: list[str]) -> list[Path]:
    """Each spec (number, stem prefix, name part, path, a numeric range
    like `30-40`, or a comma-separated run of them) must match exactly
    one chapter; a range must match one chapter per number."""
    chapters: list[Path] = []
    for spec in expand_specs(specs):
        matched = _resolve(spec)
        if len(matched) != 1:
            found = ", ".join(p.name for p in matched) or "nothing"
            raise SystemExit(
                f"rewrite: {spec!r} must match one chapter, matched {found}")
        chapter = matched[0].resolve().relative_to(ROOT)
        if chapter not in chapters:
            chapters.append(chapter)
    return chapters


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("chapters", nargs="*", metavar="CHAPTER",
                        help="chapter number, stem prefix, name part, or "
                             "path; several run in parallel")
    which = parser.add_mutually_exclusive_group()
    which.add_argument("--also", nargs="+", metavar="NAME",
                       help="the default passes plus these opt-in ones")
    which.add_argument("--passes", nargs="+", metavar="NAME",
                       help="only these passes, replacing the default set")
    which.add_argument("--all", action="store_true",
                       help="every pass, including the opt-in ones")
    parser.add_argument("--list", action="store_true",
                        help="list the passes and exit")
    parser.add_argument("--model", default=DEFAULT_MODEL, metavar="ID",
                        help=f"model for every pass (default: {DEFAULT_MODEL})")
    parser.add_argument("--serial", action="store_true",
                        help="run the chapters one at a time, output streamed")
    parser.add_argument("-j", "--jobs", type=int, default=DEFAULT_JOBS,
                        metavar="N",
                        help=f"chapters at once in parallel mode "
                             f"(default: {DEFAULT_JOBS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="print each command instead of running it")
    args = parser.parse_args()

    if args.list:
        print("Passes, in the order they run. A bare run does the defaults;")
        print("--also NAME adds an opt-in pass to them, --passes NAME runs only it.")
        for p in PASSES:
            tag = "default" if p.default else "opt-in "
            print(f"  {tag}  {p.name:<18} /{p.skill}\n{'':12}{p.what}")
        return 0

    if os.environ.get("CI"):
        print("rewrite: refusing to run under CI (costs tokens, not a gate)")
        return 2
    if not args.chapters:
        parser.error('a chapter is required (CH=25, or CH="25 28" for '
                     'several), or --list')
    chapters = resolve_chapters(args.chapters)

    named = args.passes or args.also or []
    unknown = set(named) - {p.name for p in PASSES}
    if unknown:
        parser.error(f"unknown pass(es): {', '.join(sorted(unknown))}")
    if args.passes:
        selected = [p for p in PASSES if p.name in args.passes]
    elif args.also:
        selected = [p for p in PASSES if p.default or p.name in args.also]
    elif args.all:
        selected = list(PASSES)
    else:
        selected = [p for p in PASSES if p.default]

    claude = shutil.which("claude")
    if claude is None and not args.dry_run:
        print("rewrite: no `claude` on PATH (Claude Code CLI); nothing run")
        return 2
    python = [sys.executable]
    parallel = len(chapters) > 1 and not args.serial

    def one(chapter: Path) -> bool:
        return rewrite_chapter(chapter, selected, claude or "claude",
                               python, args.model, args.dry_run, parallel)

    if parallel:
        jobs = max(1, min(args.jobs, len(chapters)))
        print(f"rewrite: {len(chapters)} chapters, {jobs} at a time "
              "(--serial for one after another)")
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            results = list(pool.map(one, chapters))
    else:
        results = [one(c) for c in chapters]

    failed = [c.as_posix() for c, ok in zip(chapters, results) if not ok]
    if failed:
        print(f"rewrite: failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
