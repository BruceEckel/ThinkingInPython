#!/usr/bin/env python
"""Check that the tools this project needs are actually installed.

Two tiers:

- basic (default): what a reader needs for the everyday commands
  (`make verify`, `make test`, `make ty`, `make lint`, ...): `uv`
  itself, plus the uv-managed dev tools (`ty`, `ruff`, `pytest`) that
  `uv run` resolves from `uv.lock`. `make` and `git` are checked too
  but marked "assumed", since you already needed both to get this
  far; they never fail the check.
- --full: everything above, plus what a book maintainer needs for
  the rest of `make help`: `pandoc` (`make site`, `make local`) and
  the standalone `vale` binary (`make prose`).

Each row prints ok/MISSING and, on failure, a one-line install hint.
Exit status is 0 only if every non-assumed tool for the requested
tier is present.

Usage:
    python tools/check_tools.py         # basic tier
    python tools/check_tools.py --full  # basic + site/prose tools
"""
import argparse
import shutil
import subprocess

# (name, command, install hint, tier, assumed)
TOOLS: list[tuple[str, list[str], str, str, bool]] = [
    ("make", ["make", "--version"],
     "winget install ezwinports.make (Windows); preinstalled on "
     "Linux/macOS (macOS: xcode-select --install)", "basic", True),
    ("git", ["git", "--version"],
     "https://git-scm.com/downloads", "basic", True),
    ("uv", ["uv", "--version"],
     "https://docs.astral.sh/uv/", "basic", False),
    ("python (via uv)", ["uv", "run", "python", "--version"],
     "run `uv sync`", "basic", False),
    ("ty (via uv)", ["uv", "run", "ty", "--version"],
     "run `uv sync`", "basic", False),
    ("ruff (via uv)", ["uv", "run", "ruff", "--version"],
     "run `uv sync`", "basic", False),
    ("pytest (via uv)", ["uv", "run", "pytest", "--version"],
     "run `uv sync`", "basic", False),
    ("pandoc", ["pandoc", "--version"],
     "https://pandoc.org/installing.html", "full", False),
    ("vale", ["vale", "--version"],
     "winget install errata-ai.Vale / brew install vale / "
     "https://vale.sh/docs/install", "full", False),
]


def first_line(cmd: list[str]) -> str | None:
    """First line of cmd's output, or None if missing/failed."""
    if shutil.which(cmd[0]) is None:
        return None
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    output = (proc.stdout or proc.stderr).strip()
    return output.splitlines()[0] if output else ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--full", action="store_true",
        help="also check the site/prose tools (pandoc, vale)")
    args = ap.parse_args(argv)

    tiers = {"basic", "full"} if args.full else {"basic"}
    tools = [t for t in TOOLS if t[3] in tiers]
    width = max(len(name) for name, *_ in tools)

    missing: list[str] = []
    for name, cmd, hint, _tier, assumed in tools:
        version = first_line(cmd)
        if version is not None:
            print(f"  {name:<{width}}  ok       {version}")
        else:
            label = "assumed" if assumed else "MISSING"
            print(f"  {name:<{width}}  {label:<7}  {hint}")
            if not assumed:
                missing.append(name)

    print()
    if missing:
        print(f"{len(missing)} required tool(s) missing: "
              f"{', '.join(missing)}")
        return 1
    print("Everything required for this tier is installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
