#!/usr/bin/env python3
"""Hand a built EPUB to Amazon's Send to Kindle desktop app.

`make kindle` lands here. The app (https://www.amazon.com/sendtokindle)
takes a file path on its command line, the same call its Explorer
"Send to Kindle" context-menu entry makes, and opens its dialog with
the file queued; the device choice and the final Send click are its
own, so this script returns as soon as the app is up rather than
waiting for the upload. Email delivery was the earlier route, but it
needs a mail client or an authenticated API; the app needs neither.

The e-ink variant is the default (a Paperwhite is the target), and
`VARIANT=color` picks the other. Only a file that `make epub` already
built is sent, never a rebuild: the point is to send the book that
was just checked, and a stale file is reported with its age so it
cannot pass for fresh by accident.

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

ROOT = Path(__file__).resolve().parent.parent
EPUB_DIR = ROOT / "build" / "epub"
VARIANTS = ("eink", "color")

WINDOWS_APP = Path(
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
) / "Amazon" / "SendToKindle" / "SendToKindle.exe"


def epub_path(variant: str) -> Path:
    if variant not in VARIANTS:
        raise SystemExit(
            f"unknown variant {variant!r}; use one of {VARIANTS}")
    path = EPUB_DIR / f"ThinkingInPython-{variant}.epub"
    if not path.exists():
        raise SystemExit(f"{path} not found; run `make epub` first")
    return path


def age(path: Path) -> str:
    minutes = (time.time() - path.stat().st_mtime) / 60
    if minutes < 90:
        return f"{minutes:.0f} min"
    if minutes < 60 * 36:
        return f"{minutes / 60:.1f} h"
    return f"{minutes / 60 / 24:.1f} days"


def launch(path: Path) -> None:
    system = platform.system()
    if system == "Windows":
        if not WINDOWS_APP.exists():
            raise SystemExit(
                f"{WINDOWS_APP} not found; install Send to Kindle "
                "from https://www.amazon.com/sendtokindle/pc")
        subprocess.Popen([str(WINDOWS_APP), str(path)])
    elif system == "Darwin":
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
          "in Send to Kindle; pick the device and click Send.")


if __name__ == "__main__":
    main()
