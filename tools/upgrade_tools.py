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

`pandoc` and `vale` are standalone binaries uv does not manage, so
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

`make` and `git` are left alone: they are outside this project's
control, and `make check-tools` already treats them as assumed.

For the pinned Python version itself, use `make upgrade-python`
instead; this script only touches package versions, not the
interpreter.

Usage:
    python tools/upgrade_tools.py
"""
import shutil
import subprocess

from tools_repo import run_echoed

# name -> (winget package id, Homebrew formula, fallback install link)
EXTERNAL: dict[str, tuple[str, str, str]] = {
    "pandoc": ("JohnMacFarlane.Pandoc", "pandoc",
               "https://pandoc.org/installing.html"),
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


def winget_upgrade(package_id: str) -> bool:
    cmd = ["winget", "upgrade", "--id", package_id, "--silent"]
    print(f"$ {' '.join(cmd)}")
    try:
        proc = subprocess.run(cmd)
    except OSError:
        return False
    # subprocess.run()'s returncode on Windows may come back signed or
    # unsigned; masking to 32 bits normalizes either representation.
    code = proc.returncode & 0xFFFFFFFF
    return code in (0, WINGET_ALREADY_LATEST)


def update_external(
    name: str, winget_id: str, brew_formula: str, link: str
) -> None:
    if shutil.which("winget") and winget_upgrade(winget_id):
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
