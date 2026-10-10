#!/usr/bin/env python3
"""Probe which outside-review prompt facts the model still disputes.

`tools/data/outside_review_prompt.md` has a section that opens with
the line `Treat these as valid and do not flag them:`. Each bullet
under it states a Python 3.12-3.15 fact that the reviewer model tends
to get wrong. A bullet costs tokens in every review, so each one
should earn its place.

This tool asks the model about the bullets without the prompt and
without the "treat these as valid" framing. One `agy` call carries
all the statements, numbered. The model answers `N. TRUE`,
`N. FALSE`, or `N. UNSURE` with a one-sentence reason. The tool
prints one row per statement:

    number, verdict, match (yes when TRUE), statement, reason

A `no` row is a bullet the model still disputes, so the bullet still
earns its place. A `yes` row is a candidate to drop, once a later run
agrees. The last line counts the disputed statements (FALSE, UNSURE,
or missing).

The call reuses the helpers of `tools/outside_review.py`: the `agy`
lookup, the command line, the NDJSON message, and the result event.
There is no retry. The tool is a report, not a gate: it returns 0
after printing the table, never joins `verify`/`gate`/`ci`, costs
tokens, gives different answers from run to run, and refuses to run
under `CI`. It needs an `agy` signed in on this machine; see
`tools/outside_review.py`.

Usage:
    python -m tools.prompt_facts_probe                # the table
    python -m tools.prompt_facts_probe --dry-run      # print, run nothing
    python -m tools.prompt_facts_probe --raw          # reply, then table
    python -m tools.prompt_facts_probe --model gemini-3.1-pro-high
    python -m tools.prompt_facts_probe --prompt other.md --timeout 1200
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from tools.config import ROOT
from tools.outside_review import (
    DEFAULT_PROMPT,
    INSTALL_NOTE,
    TAIL_LINES,
    agy_argv,
    as_dict,
    find_agy,
    result_event,
    stdin_line,
)

DEFAULT_MODEL = "gemini-3.8-flash-high"
DEFAULT_TIMEOUT = 600
HEADING = "Treat these as valid and do not flag them:"
FACT_WIDTH = 50

VERDICT_LINE = re.compile(
    r"^\W*(\d+)\s*[.)]?\W*\s*(TRUE|FALSE|UNSURE)\b\W*(.*)$",
    re.IGNORECASE,
)


def parse_facts(prompt_text: str) -> list[str]:
    """The bullet texts under the heading, without the `- `."""
    lines = prompt_text.splitlines()
    try:
        start = lines.index(HEADING) + 1
    except ValueError:
        raise ValueError(
            f"the prompt has no line {HEADING!r}") from None
    facts: list[str] = []
    for line in lines[start:]:
        if line.startswith("- "):
            facts.append(line[2:].strip())
        elif facts and not line.strip():
            break
    return facts


def build_message(facts: list[str]) -> str:
    """The question: numbered statements and the answer format."""
    numbered = "\n".join(f"{n}. {fact}"
                         for n, fact in enumerate(facts, 1))
    return (
        "You have no tools; a tool call ends the run with no answer. "
        "Answer from what you know. The statements below concern "
        "Python 3.15 and the `ty` type checker. For each numbered "
        "statement, answer on its own line in the exact form "
        "`N. TRUE`, `N. FALSE`, or `N. UNSURE`, followed by a colon "
        "and one sentence of reason. Name the Python version you "
        "assume where it matters.\n\n"
        f"{numbered}\n\n"
        "No preamble, no summary."
    )


def parse_verdicts(
    reply: str, count: int
) -> dict[int, tuple[str, str]]:
    """Map statement number to (verdict, reason) from the reply."""
    found: dict[int, tuple[str, str]] = {}
    for line in reply.splitlines():
        match = VERDICT_LINE.match(line.strip())
        if not match:
            continue
        number = int(match.group(1))
        if not 1 <= number <= count:
            continue
        reason = match.group(3).strip()
        found[number] = (match.group(2).upper(), reason)
    return found


def shorten(text: str, width: int = FACT_WIDTH) -> str:
    return text if len(text) <= width else text[:width - 3] + "..."


def report_lines(
    facts: list[str], verdicts: dict[int, tuple[str, str]]
) -> list[str]:
    """The table rows and the summary line."""
    lines = [f"{'#':>3}  {'verdict':<7}  {'match':<5}  statement"]
    disputed = 0
    for number, fact in enumerate(facts, 1):
        verdict, reason = verdicts.get(number, ("NONE", ""))
        match = "yes" if verdict == "TRUE" else "no"
        if match == "no":
            disputed += 1
        lines.append(f"{number:>3}  {verdict:<7}  {match:<5}  "
                     f"{shorten(fact)}")
        if reason:
            lines.append(f"       {reason}")
    lines.append(
        f"prompt_facts_probe: {disputed} of {len(facts)} statements "
        "still disputed (FALSE, UNSURE, or missing)")
    return lines


def ask(argv: list[str], message: str, timeout: int) -> str | None:
    """One `agy` call; the reply text, or None after a report."""
    try:
        done = subprocess.run(
            argv,
            input=stdin_line(message),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"  FAILED: no reply within {timeout} s (--timeout)")
        return None
    except OSError as exc:
        print(f"  FAILED: could not start agy: {exc}")
        return None

    event = result_event(done.stdout)
    result = as_dict(event.get("result")) if event else {}
    response = result.get("response")
    status = result.get("status")
    if done.returncode != 0:
        why = f"agy exited {done.returncode}"
    elif event is None:
        why = "no result event in the output"
    elif status != "SUCCESS":
        why = f"result status {status!r}"
    elif not isinstance(response, str) or not response.strip():
        why = "the response is empty"
    else:
        return response
    print(f"  FAILED: {why}")
    if done.stderr.strip():
        print("  stderr:")
        for line in done.stderr.strip().splitlines():
            print(f"    {line}")
    tail = done.stdout.strip().splitlines()[-TAIL_LINES:]
    for line in tail:
        print(f"    {line}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, metavar="ID",
                        help=f"agy model (default: {DEFAULT_MODEL})")
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT,
                        metavar="FILE",
                        help="the prompt whose bullets are probed "
                             "(default: "
                             "tools/data/outside_review_prompt.md)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        metavar="SECONDS",
                        help=f"for the call (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the command, the statement count, "
                             "and the message; call nothing")
    parser.add_argument("--raw", action="store_true",
                        help="print the model's reply before the table")
    args = parser.parse_args()

    if os.environ.get("CI"):
        print("prompt_facts_probe: refusing to run under CI "
              "(costs tokens, not a gate)")
        return 1
    if not args.prompt.is_file():
        print(f"prompt_facts_probe: no prompt file at {args.prompt}")
        return 1
    try:
        facts = parse_facts(args.prompt.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"prompt_facts_probe: {exc}")
        return 1

    agy = find_agy()
    if agy is None and not args.dry_run:
        print(f"prompt_facts_probe: agy not found; {INSTALL_NOTE}")
        return 1
    argv = agy_argv(agy or "agy", args.model)
    message = build_message(facts)

    if args.dry_run:
        print(subprocess.list2cmdline(argv))
        print(f"  model: {args.model}")
        print(f"  statements: {len(facts)}")
        print("  message:")
        print(message)
        return 0

    print(f"prompt_facts_probe: asking {args.model} about "
          f"{len(facts)} statements ...", flush=True)
    reply = ask(argv, message, args.timeout)
    if reply is None:
        return 1
    if args.raw:
        print(reply.strip())
        print()
    for line in report_lines(facts, parse_verdicts(reply, len(facts))):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
