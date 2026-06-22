#!/usr/bin/env python3
"""Serve the built site locally, optionally opening a browser.

`make serve` serves the existing `build/site/`. `make local` builds
it first, then runs this with `--open` to open a browser.

Usage:
    python tools/serve.py             # serve build/site/ at :8000
    python tools/serve.py --open      # serve and open a browser
    python tools/serve.py --port 9000 # serve on another port
"""

import argparse
import contextlib
import functools
import http.server
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "build" / "site"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000,
                    help="port to serve on (default: 8000)")
    ap.add_argument("--open", action="store_true",
                    help="open a browser at the served site")
    args = ap.parse_args(argv)

    if not SITE.exists():
        raise SystemExit(
            f"error: {SITE} not found. Build the site first "
            "(make site, or python tools/build_site.py).")

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"Serving {SITE} at {url}  (Ctrl+C to stop)")
    if args.open:
        # The server socket is already bound, so the browser will
        # connect even if it loads before serve_forever() runs.
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
