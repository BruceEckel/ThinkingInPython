#!/usr/bin/env python3
"""Serve the built site locally, optionally opening a browser.

`make serve` serves the existing `build/site/`. `make local` builds
it first, then runs this with `--open --watch`.

With `--watch`, a background thread polls `Chapters/*.md` (and the few
files the whole site is rendered from: `template.html`, the static
assets, `build_site.py`, `search_index.py`). A changed chapter takes
`build_site.rebuild_chapter()`'s incremental path, one pandoc run rather
than the ~46 of a full build; a changed template or tool rebuilds
everything. Each served page carries a small script that polls
`/__reload` and reloads once the rebuild lands, so an edit in the editor
becomes a refreshed browser page with nothing to press.

Usage:
    python tools/serve.py             # serve build/site/ at :8000
    python tools/serve.py --open      # serve and open a browser
    python tools/serve.py --watch     # rebuild and reload on edits
    python tools/serve.py --port 9000 # serve on another port
"""

import argparse
import contextlib
import functools
import http.server
import os
import threading
import time
import webbrowser
from pathlib import Path

import build_site
from tools_config import BUILD_SITE_DIR as SITE
from tools_config import ROOT
from tools_repo import md_files

POLL_SECONDS = 1.0
RELOAD_PATH = "/__reload"

# Changing one of these rebuilds every page, not one: they are inputs to
# the whole site rather than to a single chapter.
GLOBAL_INPUTS = (
    ROOT / "template.html",
    ROOT / "resources" / "static" / "search.css",
    ROOT / "resources" / "static" / "search.js",
    ROOT / "tools" / "build_site.py",
    ROOT / "tools" / "search_index.py",
)

RELOAD_SCRIPT = """
<script>
(() => {
  let current = null;
  const poll = async () => {
    try {
      const response = await fetch("%s", {cache: "no-store"});
      const token = await response.text();
      if (current === null) current = token;
      else if (token !== current) location.reload();
    } catch (error) { /* server restarting; try again next tick */ }
  };
  setInterval(poll, %d);
})();
</script>
""" % (RELOAD_PATH, int(POLL_SECONDS * 1000))


def snapshot() -> dict[Path, float]:
    """Modification times of every file a built page depends on."""
    watched = [*md_files(), *GLOBAL_INPUTS]
    out: dict[Path, float] = {}
    for path in watched:
        with contextlib.suppress(OSError):
            out[path] = path.stat().st_mtime
    return out


class Watcher:
    """Polls the sources and rebuilds, holding a token pages compare against.

    `lock` is held across a rebuild so the handler cannot serve a page from
    a directory a full build is in the middle of deleting and rewriting.
    """

    def __init__(self, out_dir: Path, chapter_toc: bool) -> None:
        self.out_dir = out_dir
        self.chapter_toc = chapter_toc
        self.lock = threading.RLock()
        self.token = "0"
        self._counter = 0
        self._seen = snapshot()

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self) -> None:
        while True:
            time.sleep(POLL_SECONDS)
            with contextlib.suppress(Exception):
                self._check()

    def _check(self) -> None:
        now = snapshot()
        changed = [p for p, m in now.items() if self._seen.get(p) != m]
        removed = [p for p in self._seen if p not in now]
        self._seen = now
        if not changed and not removed:
            return
        chapters = [p for p in changed if p.suffix == ".md"]
        full = bool(removed) or len(chapters) != len(changed)
        with self.lock:
            if full or not chapters:
                print("Rebuilding the whole site...")
                build_site.build(self.out_dir, self.chapter_toc)
            else:
                for md in chapters:
                    if not build_site.rebuild_chapter(md, self.out_dir,
                                                      self.chapter_toc):
                        build_site.build(self.out_dir, self.chapter_toc)
                        break
                    print(f"Rebuilt {md.name}")
            self._counter += 1
            self.token = str(self._counter)
        # A rebuild's own writes must not look like a new edit.
        self._seen = snapshot()


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the site, answering /__reload and injecting the poll script."""

    watcher: Watcher | None = None

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler's name)
        if self.path.split("?")[0] == RELOAD_PATH:
            self.reply_token()
            return
        watcher = type(self).watcher
        if watcher is None:
            super().do_GET()
            return
        with watcher.lock:
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                path = os.path.join(path, "index.html")
            if path.endswith(".html") and os.path.isfile(path):
                self.reply_page(path)
            else:
                super().do_GET()

    def reply_token(self) -> None:
        watcher = type(self).watcher
        body = (watcher.token if watcher else "0").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def reply_page(self, path: str) -> None:
        html = Path(path).read_text(encoding="utf-8")
        marker = "</body>"
        if marker in html:
            head, _, tail = html.rpartition(marker)
            html = f"{head}{RELOAD_SCRIPT}{marker}{tail}"
        else:
            html += RELOAD_SCRIPT
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        # The reload poll would otherwise print a line every second.
        if RELOAD_PATH not in str(args[0] if args else ""):
            super().log_message(format, *args)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000,
                    help="port to serve on (default: 8000)")
    ap.add_argument("--open", action="store_true",
                    help="open a browser at the served site")
    ap.add_argument("--watch", action="store_true",
                    help="rebuild on edits to Chapters/ and reload the page")
    ap.add_argument("--chapter-toc", action=argparse.BooleanOptionalAction,
                    default=build_site.CHAPTER_TOC,
                    help="per-chapter table of contents on a --watch rebuild "
                         f"(default: {build_site.CHAPTER_TOC})")
    args = ap.parse_args(argv)

    if not SITE.exists():
        raise SystemExit(
            f"error: {SITE} not found. Build the site first "
            "(make site, or python tools/build_site.py).")

    if args.watch:
        build_site.check_pandoc()
        Handler.watcher = Watcher(SITE, args.chapter_toc)
        Handler.watcher.start()

    handler = functools.partial(Handler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"Serving {SITE} at {url}  (Ctrl+C to stop)")
    if args.watch:
        print("Watching Chapters/ for edits; pages reload after a rebuild.")
    if args.open:
        # The server socket is already bound, so the browser will
        # connect even if it loads before serve_forever() runs.
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
