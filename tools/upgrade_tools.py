#!/usr/bin/env python
"""Update this project's tools to their latest versions.

Three things are fully automated:

- `uv self update` -- updates the uv binary itself. This only works
  when uv was installed via its standalone installer; if it was
  installed through pipx, Homebrew, winget, etc., uv prints its own
  message telling you to upgrade it that way instead, and this script
  moves on regardless.
- `uv tool upgrade ty` -- upgrades the globally installed `ty`, the
  copy bare `ty` on PATH resolves to (see this project's CLAUDE.md on
  bare `ty` lagging `uv run ty`). This is separate from, and does not
  replace, the project-local copy `uv run ty` uses below; best-effort,
  since not every machine has installed `ty` this way.
- `uv lock --upgrade` then `uv sync` -- upgrades every uv-managed dev
  tool (`ty`, `ruff`, `pytest`, `codespell`, ...) to the latest version
  `pyproject.toml`'s constraints allow, and installs the result into
  `.venv`. This rewrites `uv.lock`; review `git diff uv.lock` before
  committing.

`pandoc`, `typst`, and `vale` are standalone binaries uv does not manage, so
there is no single command that works on every machine. This tries the
package manager actually on PATH (winget on Windows, Homebrew
elsewhere) and falls back to printing the install/upgrade link if
neither is present or the attempt fails. On Windows, `winget upgrade`
exits with a large nonzero code, not 0, when the package is already
the latest version; that code is treated as success too, or an
up-to-date tool would be wrongly reported as "could not auto-update".
Confirmed by direct testing against winget-cli v1.29.280: Microsoft's
own return-code documentation names a different meaning for this exact
code, disagreeing with the behavior actually observed, so this trusts
the test over the docs.

A package installed per machine (pandoc's MSI) fails differently: the
silent upgrade cannot remove the old version without elevation. At a
terminal this script retries once with `--interactive`, so the
installer can raise its own UAC prompt; in a headless run it prints
the command to run from an elevated shell. See
`WINGET_UNINSTALL_FAILED`.

`git` is left alone: it is outside this project's control, and
`tip tools-check` already treats it as assumed.

For the pinned Python version itself, use `tip python-upgrade`
instead; this script only touches package versions, not the
interpreter.

Usage:
    python -m tools.upgrade_tools
"""
import shutil
import subprocess
import sys

from tools.repo import run_echoed

# name -> (winget package id, Homebrew formula, fallback install link)
EXTERNAL: dict[str, tuple[str, str, str]] = {
    "pandoc": ("JohnMacFarlane.Pandoc", "pandoc",
               "https://pandoc.org/installing.html"),
    "typst": ("Typst.Typst", "typst",
              "https://github.com/typst/typst/releases"),
    "vale": ("errata-ai.Vale", "vale", "https://vale.sh/docs/install"),
}

# winget's exit code when the package is already the latest version,
# paired with its own "No available upgrade found" message. Confirmed
# by direct testing (winget-cli v1.29.280), and distinct from the code
# winget returns for a package it cannot find at all (0x8A150014,
# "No installed package found matching input criteria"), which must
# still be reported as a failure. Do not trust this to Microsoft's own
# return-code table: it names 0x8A15002B as a manifest-validation
# error, which contradicts what was actually observed here.
WINGET_ALREADY_LATEST = 0x8A15002B
WINGET_OK = (0, WINGET_ALREADY_LATEST)

# winget's exit code when the old version's uninstaller fails, printed
# with "Uninstall failed with exit code: 1603" (1603 is the MSI's own
# code; winget's is this one). Observed 2026-11-20 on pandoc, winget's
# only package here that installs per machine: its MSI lives in
# `C:\Program Files` and removing it needs an elevated process. A
# `--silent` run from an unelevated shell cannot raise the UAC prompt,
# so the uninstall fails on every upgrade. typst and vale are portable
# packages under the user profile and never return it.
WINGET_UNINSTALL_FAILED = 0x8A150030


def winget_command(package_id: str, *, interactive: bool = False) -> list[str]:
    mode = "--interactive" if interactive else "--silent"
    return ["winget", "upgrade", "--id", package_id, mode]


def winget_upgrade(package_id: str, *, interactive: bool = False) -> int | None:
    """Run the upgrade and return winget's exit code, None if it cannot start."""
    cmd = winget_command(package_id, interactive=interactive)
    print(f"$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd)
    except OSError:
        return None
    # subprocess.run()'s returncode on Windows may come back signed or
    # unsigned; masking to 32 bits normalizes either representation.
    return proc.returncode & 0xFFFFFFFF


def needs_elevation(name: str, winget_id: str) -> bool:
    """Handle a failed uninstall: retry with a UAC prompt, or say how.

    The interactive retry lets the installer ask for elevation, so it
    runs only when a person is at a terminal to answer; a headless run
    (CI, an agent, output redirected to a log) prints the command to
    run from an elevated shell and never opens a dialog.
    """
    if sys.stdout.isatty():
        print(f"{name}: the silent upgrade could not remove the old "
              "version; retrying with the installer's own prompts.")
        if winget_upgrade(winget_id, interactive=True) in WINGET_OK:
            return True
    cmd = " ".join(winget_command(winget_id))
    print(f"Could not auto-update {name}: removing the installed version "
          "needs administrator rights.\n"
          f"Run this from an elevated shell: {cmd}")
    return False


def update_external(
    name: str, winget_id: str, brew_formula: str, link: str
) -> None:
    if shutil.which("winget"):
        code = winget_upgrade(winget_id)
        if code in WINGET_OK:
            return
        if code == WINGET_UNINSTALL_FAILED:
            needs_elevation(name, winget_id)
            return
    if shutil.which("brew") and run_echoed(["brew", "upgrade", brew_formula]):
        return
    print(f"Could not auto-update {name}. "
          f"Install or upgrade it yourself: {link}")


def main() -> int:
    run_echoed(["uv", "self", "update"])

    if not run_echoed(["uv", "tool", "upgrade", "ty"]):
        print("Could not upgrade the global `ty` tool "
              "(not installed via `uv tool install ty`?). "
              "`uv run ty`, used by this project, is unaffected.")

    if not run_echoed(["uv", "lock", "--upgrade"]):
        print("`uv lock --upgrade` failed; see the error above.")
        return 1
    if not run_echoed(["uv", "sync"]):
        print("`uv sync` failed; see the error above.")
        return 1

    for name, (winget_id, brew_formula, link) in EXTERNAL.items():
        update_external(name, winget_id, brew_formula, link)

    print("\nuv.lock was rewritten. "
          "Review `git diff uv.lock` before committing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
