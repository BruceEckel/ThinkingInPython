"""Write, check, or rasterize the book's story figures.

    uv run python -m tools.story_figures                  # write every SVG
    uv run python -m tools.story_figures --check          # drift + lint
    uv run python -m tools.story_figures --only 27 --png build/story

See `tools/story_figures/__init__.py` for what a figure module defines.
"""

from __future__ import annotations

import argparse
import importlib
import pkgutil
import re
import sys
from pathlib import Path
from types import ModuleType

from tools import story_figures
from tools.config import ROOT
from tools.story_figures import IMAGES, lint, png

MODULE_RE = re.compile(r"ch(\d\d)_\w+$")


def modules(only: str | None = None) -> list[tuple[str, ModuleType]]:
    """(chapter number, module) for every figure module, in chapter order."""
    out = []
    for info in pkgutil.iter_modules(story_figures.__path__):
        m = MODULE_RE.match(info.name)
        if m and (only is None or m.group(1) == only.zfill(2)):
            out.append((m.group(1), importlib.import_module(
                f"tools.story_figures.{info.name}")))
    return sorted(out, key=lambda pair: pair[0])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="fail on drift or a lint finding; write nothing")
    ap.add_argument("--only", metavar="NN", help="one chapter's figure")
    ap.add_argument("--png", metavar="DIR", type=Path,
                    help="also rasterize each figure into DIR")
    args = ap.parse_args(argv)
    found = modules(args.only)
    if not found:
        print(f"story figures: no module for chapter {args.only}")
        return 1
    problems = 0
    for ch, mod in found:
        out = IMAGES / f"{mod.STEM}.svg"
        name = out.relative_to(ROOT).as_posix()
        body = mod.render()
        for flag in lint(body, mod.STEM):
            print(f"{name}: {flag}")
            problems += 1
        current = out.read_text(encoding="utf-8") if out.exists() else None
        if args.check:
            if current != body:
                print(f"{name}: differs from tools/story_figures "
                      f"(chapter {ch}); rerun without --check")
                problems += 1
        elif current != body:
            out.write_text(body, encoding="utf-8", newline="\n")
            print(f"wrote  {name}")
        if args.png:
            print(f"png    {png(out, args.png / f'{mod.STEM}.png')}")
    if problems:
        print(f"story figures: {problems} problem(s)")
        return 1
    print(f"story figures: {len(found)} in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
