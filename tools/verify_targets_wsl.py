"""Run `tip verify-targets` in the WSL clone, brought up to this checkout first.

`tip verify-targets` runs every task, and on Windows that takes most
of an hour; the same run in the WSL clone (`~/ThinkingInPython`, a
Linux-filesystem clone, see README.md's Install section) took seven
minutes on 2026-10-10, since Linux starts a process ten times faster.
The clone normally pulls from GitHub, which means pushing before every
smoke test. This script skips the push: it fetches this checkout's
branch into the clone over `/mnt/<drive>/...`, fast-forwards the
clone to it, and runs verify-targets there, streaming its output,
with the summary and each failed target's excerpt at the end.

The clone is a place to run things, never a place to edit. The
script resets the clone's tracked files before the fast-forward
(`git checkout -- .`), since a verify-targets run leaves
`tools/data/target_tiers.txt` and a self-healed marker or two behind,
and a fast-forward refuses to run over them. A commit made in the
clone fails the `--ff-only` merge, loudly, rather than being
discarded. The script refuses to start where `wsl` is not on PATH,
and kills the run after `--limit` minutes (40 by default, six times
the measured run).

Usage:
    python -m tools.verify_targets_wsl                  # the whole run
    python -m tools.verify_targets_wsl --only gate ci   # these targets
    python -m tools.verify_targets_wsl --limit 60       # minutes
    python -m tools.verify_targets_wsl --dry-run        # print the script

Options the script does not take itself (`--only`, `--timeout`) are
forwarded to verify_targets.
"""

import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import PurePath

from tools.config import ROOT

CLONE = "~/ThinkingInPython"
BRANCH = "master"
DEFAULT_LIMIT = 40.0  # minutes; the 2026-10-10 run took seven


def mount_path(path: PurePath) -> str:
    """The path WSL gives a Windows path: `C:\\git\\x` is `/mnt/c/git/x`.
    A path with no drive is returned as it is."""
    posix = path.as_posix()
    drive = path.drive
    if len(drive) == 2 and drive[1] == ":":
        return f"/mnt/{drive[0].lower()}{posix[2:]}"
    return posix


def script(source: str, clone: str, branch: str, args: list[str]) -> str:
    """The bash script the clone runs: reset its tracked files,
    fast-forward to `branch` of `source`, then run verify_targets with
    `args`. `clone` is left unquoted so a leading `~` expands."""
    extra = "".join(" " + shlex.quote(a) for a in args)
    return "\n".join([
        "set -e",
        f"cd {clone}",
        "git checkout -- .",
        f"git fetch --quiet {shlex.quote(source)} {shlex.quote(branch)}",
        "git merge --ff-only FETCH_HEAD",
        f"uv run python -m tools.verify_targets{extra}",
    ])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--clone", default=CLONE,
                    help=f"the clone's path inside WSL (default: {CLONE})")
    ap.add_argument("--branch", default=BRANCH,
                    help=f"the branch to fetch and run (default: {BRANCH})")
    ap.add_argument("--limit", type=float, default=DEFAULT_LIMIT,
                    metavar="MINUTES",
                    help="kill the run after this many minutes "
                         f"(default: {DEFAULT_LIMIT:.0f})")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the script the clone would run and exit")
    args, forwarded = ap.parse_known_args(argv)

    source = mount_path(ROOT)
    text = script(source, args.clone, args.branch, forwarded)
    if args.dry_run:
        print(text)
        return 0
    wsl = shutil.which("wsl")
    if wsl is None:
        print("verify_targets_wsl: wsl is not on PATH; this runs from a "
              "Windows checkout with WSL installed", file=sys.stderr)
        return 2
    print(f"verify_targets_wsl: {args.clone} <- {source} {args.branch}, "
          f"then verify-targets, {args.limit:.0f} minute limit",
          flush=True)
    try:
        done = subprocess.run([wsl, "-e", "bash", "-lc", text],
                              timeout=args.limit * 60)
    except subprocess.TimeoutExpired:
        print(f"verify_targets_wsl: no result after {args.limit:.0f} "
              "minutes; the run was killed", file=sys.stderr)
        return 1
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
