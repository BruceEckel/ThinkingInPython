#!/usr/bin/env python3
"""Run the AI editing passes over one chapter's prose (`make rewrite CH=25`).

Each pass is one headless `claude -p "/<skill> <chapter>"` run: a skill
from this repo (`.claude/skills/`) or an installed plugin, applied to the
chapter file in place with `--permission-mode acceptEdits`, so it needs
no terminal and no confirmation. `--model` picks the model for every
pass (`make rewrite MODEL=claude-sonnet-5`); the default is
`DEFAULT_MODEL` below, Opus, because the passes' failure mode is
over-editing and restraint is what the stronger model buys. Each pass
header prints the model so a diff can be traced to it. After every pass the chapter is reflowed
(`reflow_prose.py --write`) and the cheap prose gates run
(`banned_phrases.py`, `heading_links.py`, the `extract_examples.py`
drift check), so a pass that touched a listing, broke a link, or added a
banned phrase fails right there, not at the next `make verify`. The
chain stops at the first failure.

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
    python tools/rewrite.py 25 --list         # show the passes, run nothing
    python tools/rewrite.py 25 --dry-run      # print the commands only
    python tools/rewrite.py 25 --also activate    # defaults + activate
    python tools/rewrite.py 25 --model claude-sonnet-5
    python tools/rewrite.py 25 --passes activate  # activate only
    python tools/rewrite.py Chapters/25_Template_Method.md --all
"""

import argparse
import os
import shutil
import subprocess
import sys
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
# activate) go before the three that only rephrase or reorder (literal,
# cohesion, antecedents); cohesion precedes antecedents because moving a
# sentence can change what a pronoun points at.
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

# (label, argv) pairs run after every pass, in order; the first nonzero
# exit stops the chain. reflow first, so the gates see settled lines.
CHECKS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("reflow", ("tools/reflow_prose.py", "--write")),  # + chapter
    ("banned phrases", ("tools/banned_phrases.py",)),
    ("heading links", ("tools/heading_links.py",)),
    ("examples in sync", ("tools/extract_examples.py",)),
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


def run(argv: list[str], label: str) -> int:
    """Run argv with output streaming to the terminal; return its exit code."""
    print(f"--- {label}", flush=True)
    return subprocess.run(argv, cwd=ROOT).returncode


def changed_lines(chapter: Path) -> str:
    """`git diff --stat` for the chapter, or an empty string if clean."""
    out = subprocess.run(
        ["git", "diff", "--stat", "--", chapter.as_posix()],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return out.splitlines()[-1].strip() if out else ""


def checks_after(chapter: Path, python: list[str]) -> bool:
    """Reflow the chapter and run the prose gates; False on the first failure."""
    for label, argv in CHECKS:
        full = [*python, *argv]
        if label == "reflow":
            full.append(chapter.as_posix())
        if run(full, f"check: {label}") != 0:
            print(f"FAILED: {label} (after the pass; the chapter is left as is)")
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("chapter", nargs="?",
                        help="chapter number, stem prefix, name part, or path")
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
    if not args.chapter:
        parser.error("a chapter is required (CH=25), or --list")

    matched = _resolve(args.chapter)
    if len(matched) != 1:
        found = ", ".join(p.name for p in matched) or "nothing"
        print(f"rewrite: {args.chapter!r} must match one chapter, matched {found}")
        return 2
    chapter = matched[0].resolve().relative_to(ROOT)

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

    if changed_lines(chapter):
        print(f"note: {chapter} already has uncommitted changes; "
              "the per-pass diff below includes them")

    for p in selected:
        argv = claude_argv(claude or "claude", p.skill, chapter, args.model)
        if args.dry_run:
            print(subprocess.list2cmdline(argv))
            continue
        code = run(argv, f"pass: {p.name} on {args.model} ({p.what})")
        if code != 0:
            print(f"FAILED: pass {p.name} exited {code}; stopping")
            return 1
        if not checks_after(chapter, python):
            return 1
        print(f"after {p.name}: {changed_lines(chapter) or 'no change'}")

    if not args.dry_run:
        print(f"done: {len(selected)} pass(es) on {args.model} over "
              f"{chapter.as_posix()}; review `git diff` before committing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
