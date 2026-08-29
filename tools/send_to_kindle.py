#!/usr/bin/env python3
"""Hand a built EPUB to Amazon's Send to Kindle desktop app.

`make kindle` lands here. The app (https://www.amazon.com/sendtokindle)
takes a file path on its command line, the same call its Explorer
"Send to Kindle" context-menu entry makes, and opens its dialog with
the file queued; the device choice and the final Send click are its
own, so this script returns as soon as the app is up rather than
waiting for the upload. A file-manager window (Explorer, or Finder
on macOS) also opens with the EPUB selected, so if the app ever
starts empty, or a second file is wanted, drag and drop from that
window is one motion away. Email delivery was the earlier route,
but it needs a mail client or an authenticated API; the app needs
neither.

The e-ink variant is the default (a Paperwhite is the target), and
`VARIANT=color` picks the other. The EPUB is rebuilt first when it
is missing or older than any of its inputs (Chapters/, resources/,
the builder modules), the same in-process `build_epub.build()` call
`make epub` makes, so the file sent is never behind the Markdown;
a current file is sent as-is, and its age is printed either way.
`make epub` itself always rebuilds; this is the only place the
inputs are compared, since here a stale file would go to a device
and pass for the current book.

Usage:
    uv run python tools/send_to_kindle.py            # eink
    uv run python tools/send_to_kindle.py color
"""

import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import build_epub
from tools_config import BUILD_EPUB_DIR, CHAPTERS_DIR, ROOT, TOOLS_DIR

EPUB_DIR = BUILD_EPUB_DIR
VARIANTS = ("eink", "color")
# Everything an EPUB is built from; a change to any of these makes
# the built file stale.
INPUTS = (CHAPTERS_DIR, ROOT / "resources",
          TOOLS_DIR / "build_epub.py", TOOLS_DIR / "build_site.py",
          TOOLS_DIR / "tools_config.py")

WINDOWS_APP = Path(
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
) / "Amazon" / "SendToKindle" / "SendToKindle.exe"


def newest_input() -> float:
    """Modification time of the most recently changed input file."""
    latest = 0.0
    for root in INPUTS:
        files = root.rglob("*") if root.is_dir() else (root,)
        for f in files:
            if f.is_file():
                latest = max(latest, f.stat().st_mtime)
    return latest


def epub_path(variant: str) -> Path:
    """The variant's EPUB, rebuilt first if missing or stale."""
    if variant not in VARIANTS:
        raise SystemExit(
            f"unknown variant {variant!r}; use one of {VARIANTS}")
    path = EPUB_DIR / build_epub.epub_name(variant)
    if not path.exists():
        print(f"{path.relative_to(ROOT)} not built yet; building.")
    elif path.stat().st_mtime < newest_input():
        print(f"{path.relative_to(ROOT)} is older than its inputs; "
              "rebuilding.")
    else:
        return path
    if build_epub.build(EPUB_DIR) != 0:
        raise SystemExit("EPUB build failed; nothing sent")
    return path


def age(path: Path) -> str:
    minutes = (time.time() - path.stat().st_mtime) / 60
    if minutes < 90:
        return f"{minutes:.0f} min"
    if minutes < 60 * 36:
        return f"{minutes / 60:.1f} h"
    return f"{minutes / 60 / 24:.1f} days"


def reveal(path: Path, system: str) -> None:
    """Open a file-manager window with `path` selected."""
    if system == "Windows":
        # explorer's own syntax: no space after the comma.
        subprocess.Popen(["explorer", f"/select,{path}"])
    elif system == "Darwin":
        subprocess.Popen(["open", "-R", str(path)])


def launch(path: Path) -> None:
    system = platform.system()
    if system == "Windows":
        if not WINDOWS_APP.exists():
            raise SystemExit(
                f"{WINDOWS_APP} not found; install Send to Kindle "
                "from https://www.amazon.com/sendtokindle/pc")
        reveal(path, system)
        subprocess.Popen([str(WINDOWS_APP), str(path)])
    elif system == "Darwin":
        reveal(path, system)
        subprocess.Popen(["open", "-a", "Send to Kindle", str(path)])
    else:
        raise SystemExit(
            "Send to Kindle has no Linux app; email the file to the "
            "Kindle address or use https://www.amazon.com/sendtokindle")


def main() -> None:
    variant = sys.argv[1] if len(sys.argv) > 1 else "eink"
    path = epub_path(variant)
    launch(path)
    print(f"Queued {path.relative_to(ROOT)} (built {age(path)} ago) "
          "in Send to Kindle and selected it in a file window; "
          "pick the device and click Send.")


if __name__ == "__main__":
    main()
