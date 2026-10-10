#!/usr/bin/env python3
"""Get an outside review of a chapter from Gemini (`tip outside-review CH=17`).

Each chapter goes to Google's Antigravity CLI (`agy`), a Gemini front
end, in one headless call: the review instructions from
`tools/data/outside_review_prompt.md`, then the chapter's full Markdown.
The reply is saved as `outside_review/<chapter stem>.md`, under a first
line that records the chapter, the model, and the date. The tool never
edits a chapter. `outside_review/` is tracked, like `deep_review/`.
Applying a review is a separate step, done in a Claude session that
tests each item against the chapter and a run under `uv run` before
editing, applies what passes, and appends a `## Verdicts` section to
the review file: one line per item, applied or rejected, with the
evidence and the commit. The first runs showed why the test matters:
every item of the first reply was wrong for Python 3.15, and the
corrected reply still claimed a `TypeError` that `type.__new__()` never
raises.

The message travels on stdin as one line of NDJSON, and `agy` answers
with NDJSON events on stdout; the last is a `result` event whose
`response` is the review. A run succeeds when `agy` exits 0 and the
result event reports `SUCCESS` with a non-empty response. A failed
attempt prints stderr (where `agy` reports notices such as a tool it
denied) and the tail of stdout. Two failures are transient and are
rerun, up to `--retries` more times (default 2), each attempt logged
with its number: a result whose status is `ERROR` because the reply
exceeded the output token limit, and an empty response after `agy`
denied a tool call (the model tried to act instead of answering, and
usually answers on the next run). A third `ERROR`, "The stream was
interrupted", can arrive after the whole reply has streamed (chapter
06's Flash round, 2026-10-10, carried four complete items under it):
with a non-empty response the reply is saved, with a second header
line saying the stream was interrupted so the reader checks its tail,
and with an empty one the attempt is rerun. A server error, an
`ERROR` whose text carries "code 500" (chapter 13's Flash round,
2026-10-10: "API error (attempt 2): INTERNAL (code 500)", with a reply
cut short), is transient and rerun. Every other failure, a nonzero
exit, a timeout, a missing result event, or an `ERROR` of another
kind, is final for that chapter, and the run continues with the next
chapter.
Chapters run one after another in the order given.

This is not a gate. Each run costs tokens, the reply is
nondeterministic, and it needs an `agy` signed in on this machine, so
it never joins `verify`/`gate`/`ci` and it refuses to run under `CI`.
Install `agy` from https://antigravity.google/docs/getting-started?tab=cli
and sign in once by running `agy`.

Usage:
    python -m tools.outside_review 17                # one chapter
    python -m tools.outside_review 17 18             # two, in order
    python -m tools.outside_review 30-32             # a range, inclusive
    python -m tools.outside_review 17 --dry-run      # print, run nothing
    python -m tools.outside_review 17 --model gemini-3.8-flash-high
    python -m tools.outside_review 17 --timeout 1800 --out-dir /tmp/r
    python -m tools.outside_review 17 --retries 0     # one attempt, no reruns
    python -m tools.outside_review 17 --suffix .r2   # a second round, saved as 17_....r2.md beside the first
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import date
from enum import Enum
from pathlib import Path

from tools.config import ROOT
from tools.repo import write_text_lf
from tools.rewrite import resolve_chapters

DEFAULT_MODEL = "gemini-3.1-pro-high"
DEFAULT_PROMPT = ROOT / "tools" / "data" / "outside_review_prompt.md"
DEFAULT_OUT_DIR = ROOT / "outside_review"
DEFAULT_TIMEOUT = 900
DEFAULT_RETRIES = 2

# The error text of an `ERROR` result that a rerun can clear.
OUTPUT_LIMIT_ERROR = "exceeded the output token limit"
# The error text of an `ERROR` result that may still carry the reply.
STREAM_INTERRUPTED = "The stream was interrupted"
# The error text of a server-side failure, which a rerun usually clears.
SERVER_ERROR = "code 500"

INSTALL_NOTE = (
    "install it from "
    "https://antigravity.google/docs/getting-started?tab=cli "
    "and sign in once by running `agy`"
)

# How many trailing stdout lines a failure shows.
TAIL_LINES = 8


class Outcome(Enum):
    """What one attempt at a chapter produced."""

    OK = "ok"  # The reply is saved
    RETRY = "retry"  # A transient failure: rerun if attempts remain
    FAIL = "fail"  # A failure a rerun would repeat


def find_agy() -> str | None:
    """The `agy` binary on PATH, else the installer's default location."""
    found = shutil.which("agy")
    if found:
        return found
    local = os.environ.get("LOCALAPPDATA")
    if local:
        candidate = Path(local) / "agy" / "bin" / "agy.exe"
        if candidate.is_file():
            return str(candidate)
    return None


def agy_argv(agy: str, model: str) -> list[str]:
    """The headless invocation; the prompt itself arrives on stdin."""
    return [
        agy,
        "-p",
        "",
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--model",
        model,
    ]


def build_message(prompt: str, chapter: Path) -> str:
    """The review instructions, then the chapter under a marker line."""
    text = (ROOT / chapter).read_text(encoding="utf-8")
    return (f"{prompt}\n\n=== CHAPTER ===\n\n"
            f"Chapter file: `{chapter.name}`\n\n{text}")


def stdin_line(message: str) -> str:
    """The one NDJSON event `agy` reads from stdin."""
    event = {"event": "user", "message": {"content": message}}
    return json.dumps(event, ensure_ascii=False) + "\n"


def result_event(stdout: str) -> dict[str, object] | None:
    """The last `result` event in `agy`'s NDJSON output, if any."""
    found: dict[str, object] | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get("event") == "result":
            found = event
    return found


def as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def diagnose(stdout: str, stderr: str, why: str) -> str:
    """A failure report: the reason, stderr, and the stdout tail."""
    parts = [f"  FAILED: {why}"]
    if stderr.strip():
        parts.append("  stderr:")
        parts.extend(f"    {ln}" for ln in stderr.strip().splitlines())
    tail = stdout.strip().splitlines()[-TAIL_LINES:]
    if tail:
        parts.append(f"  last {len(tail)} stdout line(s):")
        parts.extend(f"    {ln}" for ln in tail)
    return "\n".join(parts)


def review_chapter(
    chapter: Path,
    argv: list[str],
    message: str,
    model: str,
    out_dir: Path,
    timeout: int,
    suffix: str = "",
    attempt: int = 1,
    attempts: int = 1,
) -> Outcome:
    """Send one chapter to `agy` once and save the reply."""
    tag = chapter.stem.split("_", 1)[0]
    print(f"[{tag}] outside review of {chapter.as_posix()} "
          f"with {model}, attempt {attempt}/{attempts} ...", flush=True)
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
        return Outcome.FAIL
    except OSError as exc:
        print(f"  FAILED: could not start agy: {exc}")
        return Outcome.FAIL

    event = result_event(done.stdout)
    result = as_dict(event.get("result")) if event else {}
    response = result.get("response")
    status = result.get("status")
    retry = False
    interrupted = (status == "ERROR"
                   and STREAM_INTERRUPTED in str(result.get("error", "")))
    if done.returncode != 0:
        why = f"agy exited {done.returncode}"
    elif event is None:
        why = "no result event in the output"
    elif status == "ERROR" and OUTPUT_LIMIT_ERROR in json.dumps(result):
        why = f"result status 'ERROR': the reply {OUTPUT_LIMIT_ERROR}"
        retry = True
    elif interrupted and isinstance(response, str) and response.strip():
        why = ""  # The reply streamed before the stream broke: keep it
    elif interrupted:
        why = f"result status 'ERROR': {STREAM_INTERRUPTED}, no reply"
        retry = True
    elif status == "ERROR" and SERVER_ERROR in str(result.get("error", "")):
        why = f"result status 'ERROR': server error, {result.get('error')}"
        retry = True
    elif status != "SUCCESS":
        why = f"result status {status!r}"
    elif not isinstance(response, str) or not response.strip():
        why = "the response is empty"
        denied = result.get("denied_actions")
        if isinstance(denied, list) and denied:
            names = ", ".join(str(as_dict(d).get("action", "?"))
                              for d in denied)
            why += (f"; agy denied a tool call ({names}), so the model "
                    "tried to act instead of answering")
            retry = True
    else:
        why = ""
    if why or not isinstance(response, str):
        print(diagnose(done.stdout, done.stderr, why or "bad response"))
        return Outcome.RETRY if retry else Outcome.FAIL

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{chapter.stem}{suffix}.md"
    header = (f"<!-- outside review of {chapter.as_posix()}, "
              f"model {model}, {date.today().isoformat()} -->")
    note = ""
    if interrupted:
        note = ("<!-- the stream was interrupted after this reply "
                "streamed; check that its last item is whole -->\n")
    write_text_lf(out, f"{header}\n{note}\n{response.strip()}\n")
    usage = as_dict(result.get("usage"))
    seconds = result.get("duration_seconds")
    shown = round(seconds) if isinstance(seconds, (int, float)) else "?"
    flag = " (stream interrupted; check the tail)" if interrupted else ""
    print(f"  wrote {out}{flag}: {shown} s, tokens in "
          f"{usage.get('input_tokens', '?')}, out "
          f"{usage.get('output_tokens', '?')}, thinking "
          f"{usage.get('thinking_tokens', '?')}", flush=True)
    return Outcome.OK


def review_with_retries(
    chapter: Path,
    argv: list[str],
    message: str,
    model: str,
    out_dir: Path,
    timeout: int,
    suffix: str,
    retries: int,
) -> bool:
    """Review a chapter, rerunning a transient failure up to `retries` times."""
    attempts = retries + 1
    for attempt in range(1, attempts + 1):
        outcome = review_chapter(chapter, argv, message, model, out_dir,
                                 timeout, suffix, attempt, attempts)
        if outcome is Outcome.OK:
            return True
        if outcome is Outcome.FAIL:
            return False
        if attempt == attempts:
            print(f"  giving up after {attempts} attempt(s) (--retries)")
            return False
        print(f"  rerunning ({attempt + 1}/{attempts}) ...", flush=True)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n")[0]
    )
    parser.add_argument("selectors", nargs="+", metavar="CHAPTER",
                        help="chapter number, range (30-40), stem prefix, "
                             "name part, or path")
    parser.add_argument("--model", default=DEFAULT_MODEL, metavar="ID",
                        help=f"agy model (default: {DEFAULT_MODEL})")
    parser.add_argument("--prompt", type=Path, default=DEFAULT_PROMPT,
                        metavar="FILE",
                        help="the review instructions "
                             "(default: tools/data/outside_review_prompt.md)")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR,
                        metavar="DIR",
                        help="where replies go (default: outside_review/)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT,
                        metavar="SECONDS",
                        help=f"per chapter (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES,
                        metavar="N",
                        help="reruns of a chapter after a transient "
                             "failure: an ERROR result that exceeded the "
                             "output token limit, or an empty response "
                             f"after a denied tool call (default: "
                             f"{DEFAULT_RETRIES})")
    parser.add_argument("--suffix", default="", metavar="TEXT",
                        help="appended to the output stem, so a second "
                             "round is kept beside the first (.r2 writes "
                             "<stem>.r2.md)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the argv, output path, and message "
                             "length for each chapter; run nothing")
    args = parser.parse_args()
    if args.retries < 0:
        parser.error("--retries must be 0 or more")

    if os.environ.get("CI"):
        print("outside_review: refusing to run under CI "
              "(costs tokens, not a gate)")
        return 1
    chapters = resolve_chapters(args.selectors)
    if not args.prompt.is_file():
        print(f"outside_review: no prompt file at {args.prompt}")
        return 1
    prompt = args.prompt.read_text(encoding="utf-8").rstrip("\n")

    agy = find_agy()
    if agy is None and not args.dry_run:
        print(f"outside_review: agy not found; {INSTALL_NOTE}")
        return 1
    argv = agy_argv(agy or "agy", args.model)

    failed: list[str] = []
    for chapter in chapters:
        message = build_message(prompt, chapter)
        out = args.out_dir / f"{chapter.stem}{args.suffix}.md"
        if args.dry_run:
            print(subprocess.list2cmdline(argv))
            print(f"  output: {out}")
            print(f"  message: {len(message)} characters")
            continue
        if not review_with_retries(chapter, argv, message, args.model,
                                   args.out_dir, args.timeout,
                                   args.suffix, args.retries):
            failed.append(chapter.as_posix())
    if failed:
        print(f"outside_review: failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
