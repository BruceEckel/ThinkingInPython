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
neither is present or the attempt fails.

`make` and `git` are left alone: they are outside this project's
control, and `make check-tools` already treats them as assumed.

For the pinned Python version itself, use `make upgrade-python`
instead; this script only touches package versions, not the
interpreter.

Usage:
    python tools/upgrade_tools.py
"""
import shutil

from tools_repo import run_echoed

# name -> (winget package id, Homebrew formula, fallback install link)
EXTERNAL: dict[str, tuple[str, str, str]] = {
    "pandoc": ("JohnMacFarlane.Pandoc", "pandoc",
               "https://pandoc.org/installing.html"),
    "vale": ("errata-ai.Vale", "vale", "https://vale.sh/docs/install"),
}


def update_external(
    name: str, winget_id: str, brew_formula: str, link: str
) -> None:
    if shutil.which("winget") and run_echoed(
            ["winget", "upgrade", "--id", winget_id, "--silent"]):
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
