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
  the rest of `make help`: `pandoc` (`make site`, `make local`,
  `make epub`, `make pdf`), `typst` (the PDF engine `make pdf`
  drives pandoc with), the standalone `vale` binary (`make prose`),
  and `gh` (`make release`).

Each row prints ok/MISSING, and a failing run ends with the commands
that install what is missing on this machine: one `winget install`
line on Windows, one `brew install` line on macOS or wherever
Homebrew is on PATH, one `sudo apt install` line on a Debian-family
Linux, and a download command for a tool the package manager lacks
(typst and vale on Ubuntu, which packages neither). Exit status is 0
only if every non-assumed tool for the requested tier is present.

Usage:
    python -m tools.check_tools         # basic tier
    python -m tools.check_tools --full  # basic + site/prose tools
"""
import argparse
import platform
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass, field

from tools.repo import run_capture

# The package managers a machine can have. `winget` is Windows, `brew`
# is macOS or Linuxbrew, `apt` is the Debian family. A tool with no
# entry for the chosen manager falls back to its `other` command,
# which is a download or a URL.
INSTALL = {
    "winget": "winget install",
    "brew": "brew install",
    "apt": "sudo apt install",
}

_ARCH = platform.machine().lower()
_ARM = _ARCH in ("aarch64", "arm64")
_TYPST_TARGET = ("aarch64" if _ARM else "x86_64") + "-unknown-linux-musl"
_VALE_ASSET = "Linux_arm64" if _ARM else "Linux_64-bit"

# Neither typst nor vale is in Ubuntu's apt, so on a Debian-family
# machine they come from their GitHub release archives. typst's latest
# release has a fixed asset name; vale's carries the version number, so
# the command asks the release API for the asset's URL.
_TYPST_TARBALL = (
    "curl -L https://github.com/typst/typst/releases/latest/download/"
    f"typst-{_TYPST_TARGET}.tar.xz | tar -xJ -C /tmp && "
    f"sudo install /tmp/typst-{_TYPST_TARGET}/typst /usr/local/bin/")
_VALE_TARBALL = (
    "curl -sL https://api.github.com/repos/errata-ai/vale/releases/latest"
    f" | grep -o 'https://[^\"]*{_VALE_ASSET}.tar.gz' | xargs curl -L"
    " | tar -xz -C /tmp vale && sudo install /tmp/vale /usr/local/bin/")
_LINUX = sys.platform.startswith("linux")


@dataclass(frozen=True)
class Tool:
    """One tool: how to detect it and how to install it per manager.

    `packages` maps a manager name to the package the manager installs
    it as; `other` is the command or URL for a machine with none of
    those. `assumed` tools never fail the check.
    """
    name: str
    command: list[str]
    tier: str
    other: str
    packages: dict[str, str] = field(default_factory=dict)
    assumed: bool = False

    def hint(self, manager: str | None) -> str:
        """The one-line install hint printed beside a MISSING row."""
        if manager and manager in self.packages:
            return f"{INSTALL[manager]} {self.packages[manager]}"
        return self.other


TOOLS: list[Tool] = [
    Tool("make", ["make", "--version"], "basic",
         "preinstalled on Linux; macOS: xcode-select --install",
         {"winget": "ezwinports.make"}, assumed=True),
    Tool("git", ["git", "--version"], "basic",
         "https://git-scm.com/downloads",
         {"winget": "Git.Git", "brew": "git", "apt": "git"}, assumed=True),
    Tool("uv", ["uv", "--version"], "basic",
         "https://docs.astral.sh/uv/getting-started/installation/",
         {"winget": "astral-sh.uv", "brew": "uv"}),
    Tool("python (via uv)", ["uv", "run", "python", "--version"], "basic",
         "uv sync"),
    Tool("ty (via uv)", ["uv", "run", "ty", "--version"], "basic",
         "uv sync"),
    Tool("ruff (via uv)", ["uv", "run", "ruff", "--version"], "basic",
         "uv sync"),
    Tool("pytest (via uv)", ["uv", "run", "pytest", "--version"], "basic",
         "uv sync"),
    Tool("pandoc", ["pandoc", "--version"], "full",
         "https://pandoc.org/installing.html",
         {"winget": "JohnMacFarlane.Pandoc", "brew": "pandoc",
          "apt": "pandoc"}),
    Tool("typst", ["typst", "--version"], "full",
         _TYPST_TARBALL if _LINUX
         else "https://github.com/typst/typst/releases",
         {"winget": "Typst.Typst", "brew": "typst"}),
    Tool("vale", ["vale", "--version"], "full",
         _VALE_TARBALL if _LINUX else "https://vale.sh/docs/install",
         {"winget": "errata-ai.Vale", "brew": "vale"}),
    Tool("gh", ["gh", "--version"], "full",
         "https://cli.github.com",
         {"winget": "GitHub.cli", "brew": "gh", "apt": "gh"}),
]


def first_line(cmd: list[str]) -> str | None:
    """First line of cmd's output, or None if missing/failed."""
    result = run_capture(cmd, timeout=60, combine_stderr=True)
    if result is None:
        return None
    output, returncode = result
    if returncode != 0:
        return None
    output = output.strip()
    return output.splitlines()[0] if output else ""


def package_manager(which: Callable[[str], object] = shutil.which,
                    platform_name: str = sys.platform) -> str | None:
    """The manager this machine installs with, or None.

    Windows gets winget. Elsewhere Homebrew wins when it is on PATH
    (macOS, or Linuxbrew), then apt on the Debian family.
    """
    if platform_name == "win32":
        return "winget" if which("winget") else None
    if which("brew"):
        return "brew"
    if which("apt-get"):
        return "apt"
    return None


def install_commands(missing: list[Tool],
                     manager: str | None) -> list[str]:
    """The commands that install `missing` on this machine, one per
    line: the manager's packages folded into a single install line,
    then each remaining tool's own command."""
    packaged = [t.packages[manager] for t in missing
                if manager and manager in t.packages]
    lines: list[str] = []
    if packaged and manager:
        lines.append(f"{INSTALL[manager]} {' '.join(packaged)}")
    lines += [t.other for t in missing
              if not (manager and manager in t.packages)]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--full", action="store_true",
        help="also check the site/prose tools (pandoc, typst, vale, gh)")
    args = ap.parse_args(argv)

    tiers = {"basic", "full"} if args.full else {"basic"}
    tools = [t for t in TOOLS if t.tier in tiers]
    width = max(len(t.name) for t in tools)
    manager = package_manager()

    missing: list[Tool] = []
    for tool in tools:
        version = first_line(tool.command)
        if version is not None:
            print(f"  {tool.name:<{width}}  ok       {version}")
        else:
            label = "assumed" if tool.assumed else "MISSING"
            print(f"  {tool.name:<{width}}  {label:<7}  {tool.hint(manager)}")
            if not tool.assumed:
                missing.append(tool)

    print()
    if missing:
        print(f"{len(missing)} required tool(s) missing: "
              f"{', '.join(t.name for t in missing)}")
        print("To install them on this machine:")
        for line in install_commands(missing, manager):
            print(f"  {line}")
        return 1
    print("Everything required for this tier is installed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
