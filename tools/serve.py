#!/usr/bin/env python3
"""Serve the built site locally, optionally opening a browser.

`tip serve` runs this with `--watch --copy-on-select` on the existing
`build/site/`. `tip local` builds the site first and adds `--open`.

With `--watch`, a background thread polls `Chapters/*.md` and
`Solutions/*/README.md` (and the few files the whole site is rendered
from: `template.html`, the static assets, and the figures in
`resources/images/`). A changed chapter takes
`build_site.rebuild_chapter()`'s incremental path, one pandoc run
rather than the ~46 of a full build, and a changed solutions file takes
the same path through its chapter, since that one run also rewrites
the chapter's solutions page (before 2026-10-10 the watcher listed
`Chapters/` alone, so a solutions edit never reached the browser). A
changed template or asset rebuilds everything. A rebuild that raises
an exception prints its traceback in the server's terminal and leaves
the page as it was; the next save tries again. Each served page carries
a small script that polls `/__reload` and reloads once the rebuild
lands, so an edit in the editor becomes a refreshed browser page with
nothing to press. The book's index page is the one page a save leaves
alone: matching every term against the whole book is the slowest step
of a build (ten seconds when the index arrived on 2026-10-16, about two
since the seeded search of the same day), and it made each save wait
that long. The chapter rebuild matches the edited chapter alone, which
keeps the page's `#ix-` anchors right, and marks the index page stale;
the server rebuilds it when the page is next requested.

A change to the build code needs more than a rebuild. The server
imports `build_site` once, so a rebuild after an edit to it, or to any
module it imports, would render with the code as it was at startup:
on 2026-09-26 a server started before the epigraph commit went on
rebuilding edited chapters in the old layout for hours. So `--watch`
runs the server as a child process under a supervisor, which polls the
source of every `tools/` module it has itself imported (the same set
the child uses, `serve.py` included). On a change it stops the child
and starts a fresh one, which rebuilds the whole site with the new code
before serving; the open page reloads when the new server answers.

With `--copy-on-select`, each served page also carries a script that
copies a mouse selection to the clipboard as soon as the button is
released, for pulling passages out of the rendered book. The copied
text is wrapped in guillemets and followed by its source, so a pasted
passage reads `«...» (31 State Machines › Table-Driven State Machine
#table-driven-state-machine)`: the chapter number and title, the
section title, and the section's anchor. Neither « nor » occurs in the
book, so the marks cannot be mistaken for quoted text. `tip local` passes it. Both scripts are added to the response as it is served, so
the files in `build/site/`, the ones the published site is built from,
never contain either.

Usage:
    python -m tools.serve             # serve build/site/ at :8000
    python -m tools.serve --open      # serve and open a browser
    python -m tools.serve --watch     # rebuild and reload on edits
    python -m tools.serve --copy-on-select  # selection copies itself
    python -m tools.serve --port 9000 # serve on another port
"""

import argparse
import contextlib
import functools
import http.server
import os
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path

from tools import build_site
from tools.config import BUILD_SITE_DIR as SITE
from tools.config import CHAPTERS_DIR, ROOT, SOLUTIONS_DIR
from tools.repo import chapter_stem, is_solutions_file, md_files

POLL_SECONDS = 1.0
RELOAD_PATH = "/__reload"

# Changing one of these rebuilds every page, not one: they are inputs to
# the whole site rather than to a single chapter. The build code is not
# here; a change to it restarts the server (see Supervisor).
GLOBAL_INPUTS = (
    ROOT / "template.html",
    ROOT / "resources" / "static" / "search.css",
    ROOT / "resources" / "static" / "search.js",
)
# `rebuild_chapter()` copies a figure only when the site lacks it, so a
# changed one (a regenerated coupling panel, say) rebuilds every page.
IMAGES = ROOT / "resources" / "images"
# Set in the child the supervisor starts, so the child serves instead of
# supervising.
CHILD_ENV = "TIP_SERVE_CHILD"

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

# Copies the selection when the mouse button comes up. mouseup is the
# user gesture the clipboard API requires; selectionchange alone is not
# one. The text goes out as «text» (NN Chapter › Section #anchor): the
# chapter is the page's <h1>, prefixed with the number that opens the
# page's file name (31 for 31_Patterns--State_Machines.html; no prefix
# when the name has no underscore). The section is the last <h2>/<h3>
# before the selection starts, and the anchor is that heading's id. The
# execCommand fallback covers a page served over plain http
# on a LAN address, where navigator.clipboard is absent; it copies the
# bare selection, since it cannot see the wrapped text. The toast makes
# the copy visible, since every drag-select overwrites the clipboard.
COPY_SCRIPT = """
<script>
(() => {
  const toast = document.createElement("div");
  toast.textContent = "copied";
  toast.style.cssText = "position:fixed;bottom:1rem;right:1rem;padding:0.3rem 0.7rem;"
    + "background:#333;color:#fff;font:0.8rem sans-serif;border-radius:4px;"
    + "opacity:0;transition:opacity 0.2s;pointer-events:none;z-index:9999";
  document.body.appendChild(toast);
  let hide = null;
  const show = () => {
    toast.style.opacity = "1";
    clearTimeout(hide);
    hide = setTimeout(() => { toast.style.opacity = "0"; }, 700);
  };
  const source = (range) => {
    const h1 = document.querySelector("h1");
    const title = h1 ? h1.textContent.trim() : document.title;
    const file = location.pathname.split("/").pop();
    const number = file.includes("_") ? file.split("_")[0] : "";
    const parts = [number ? number + " " + title : title];
    let section = null;
    for (const h of document.querySelectorAll("h2, h3")) {
      if (range.comparePoint(h, 0) > 0) break;
      section = h.textContent.trim();
      if (h.id) section += " #" + h.id;
    }
    if (section) parts.push(section);
    return parts.join(" › ");
  };
  document.addEventListener("mouseup", (event) => {
    const tag = event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    const selection = document.getSelection();
    const text = selection.toString();
    if (text.trim() === "" || selection.rangeCount === 0) return;
    const wrapped = "«" + text + "» ("
      + source(selection.getRangeAt(0)) + ")";
    const fallback = () => { if (document.execCommand("copy")) show(); };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(wrapped).then(show, fallback);
    } else {
      fallback();
    }
  });
})();
</script>
"""


def watched_sources() -> list[Path]:
    """Every file a built page depends on: both Markdown trees, the
    whole-site inputs, and the figures."""
    return [*md_files([CHAPTERS_DIR, SOLUTIONS_DIR]), *GLOBAL_INPUTS,
            *IMAGES.iterdir()]


def source_chapter(md: Path) -> Path:
    """The chapter whose pages a Markdown edit changes.

    A chapter is its own; a solutions file maps to the chapter it
    belongs to, since `rebuild_chapter()` renders the chapter page and
    its solutions page in one run.
    """
    if is_solutions_file(md):
        return CHAPTERS_DIR / f"{chapter_stem(md)}.md"
    return md


def snapshot() -> dict[Path, float]:
    """Modification times of every file a built page depends on."""
    watched = watched_sources()
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
        # The process id makes a restarted server's first token differ
        # from the last one a page saw, so the page reloads.
        self.token = f"{os.getpid()}-0"
        self._counter = 0
        self._seen = snapshot()
        # Set by a chapter rebuild, cleared when the index page is
        # rebuilt on request or by a full build.
        self.index_stale = False

    def start(self) -> None:
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self) -> None:
        while True:
            time.sleep(POLL_SECONDS)
            self.tick()

    def tick(self) -> None:
        """One poll. A failed rebuild is reported, never hidden: the
        thread goes on polling, and the next save tries again."""
        try:
            self._check()
        except Exception:
            traceback.print_exc()
            print("Rebuild failed; the page was not updated. "
                  "Save again to retry.")

    def refresh_index(self) -> None:
        """Rebuild the index page if a save has made it stale.

        Called with `lock` held, from the handler, when the page is
        requested; the request waits the seconds the rebuild takes.
        """
        if not self.index_stale:
            return
        print("Rebuilding the index page...")
        build_site.rebuild_index_page(self.out_dir)
        self.index_stale = False

    def _check(self) -> None:
        now = snapshot()
        changed = [p for p, m in now.items() if self._seen.get(p) != m]
        removed = [p for p in self._seen if p not in now]
        self._seen = now
        if not changed and not removed:
            return
        markdown = [p for p in changed if p.suffix == ".md"]
        # A chapter and its solutions file changed together rebuild once.
        chapters = list(dict.fromkeys(source_chapter(p) for p in markdown))
        full = bool(removed) or len(markdown) != len(changed)
        with self.lock:
            if full or not chapters:
                print("Rebuilding the whole site...")
                build_site.build(self.out_dir, self.chapter_toc)
                self.index_stale = False
            else:
                for md in chapters:
                    if not build_site.rebuild_chapter(md, self.out_dir,
                                                      self.chapter_toc):
                        build_site.build(self.out_dir, self.chapter_toc)
                        self.index_stale = False
                        break
                    print(f"Rebuilt {md.name}")
                    self.index_stale = True
            self._counter += 1
            self.token = f"{os.getpid()}-{self._counter}"
        # `_seen` stays the snapshot taken before the rebuild. A rebuild
        # writes only under `out_dir`, which nothing watches, so a later
        # snapshot would hide only a save made while pandoc ran (two
        # edits a second apart left the page showing the first).


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the site, answering /__reload and injecting the scripts."""

    watcher: Watcher | None = None
    # The scripts every served page gets before </body>: RELOAD_SCRIPT
    # under --watch, COPY_SCRIPT under --copy-on-select, both, or none.
    inject: str = ""

    def end_headers(self) -> None:
        """Every response, not only the pages, refuses to be cached.

        `SimpleHTTPRequestHandler` sends `Last-Modified` and nothing
        else for a static file, so a browser caches an image on its
        own heuristics. Editing a diagram in `resources/images/` and
        rebuilding then leaves the old drawing on screen, and
        restarting the server does not clear it, because the stale
        bytes are in the browser. A preview server exists to show the
        current file.
        """
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler's name)
        if self.path.split("?")[0] == RELOAD_PATH:
            self.reply_token()
            return
        if not type(self).inject:
            super().do_GET()
            return
        watcher = type(self).watcher
        # Under --watch, hold the lock so a page is never read mid-rebuild.
        lock = watcher.lock if watcher else contextlib.nullcontext()
        with lock:
            path = self.translate_path(self.path)
            if os.path.isdir(path):
                path = os.path.join(path, "index.html")
            if (watcher and os.path.basename(path) == build_site.INDEX_PAGE
                    and os.path.isfile(path)):
                watcher.refresh_index()
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
        self.end_headers()
        self.wfile.write(body)

    def reply_page(self, path: str) -> None:
        html = Path(path).read_text(encoding="utf-8")
        inject = type(self).inject
        marker = "</body>"
        if marker in html:
            head, _, tail = html.rpartition(marker)
            html = f"{head}{inject}{marker}{tail}"
        else:
            html += inject
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        # The reload poll would otherwise print a line every second.
        if RELOAD_PATH not in str(args[0] if args else ""):
            super().log_message(format, *args)


def code_files() -> list[Path]:
    """The source of every `tools/` module this process has imported."""
    tools_dir = ROOT / "tools"
    files = set()
    for module in list(sys.modules.values()):
        name = getattr(module, "__file__", None)
        if name and Path(name).resolve().parent == tools_dir.resolve():
            files.add(Path(name).resolve())
    return sorted(files)


def code_snapshot(files: list[Path]) -> dict[Path, float]:
    out: dict[Path, float] = {}
    for path in files:
        with contextlib.suppress(OSError):
            out[path] = path.stat().st_mtime
    return out


def stop(child: subprocess.Popen[bytes]) -> None:
    """Stop the child and anything it started.

    On Windows `.venv/Scripts/python.exe` is a launcher that starts the
    real interpreter as its own child, so terminating the launcher
    alone would leave the server running and holding the port.
    """
    if child.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(child.pid)],
                       capture_output=True)
    else:
        child.terminate()
    with contextlib.suppress(subprocess.TimeoutExpired):
        child.wait(timeout=10)


def supervise(argv: list[str]) -> int:
    """Run the server as a child, restarting it when the build code changes."""
    files = code_files()
    seen = code_snapshot(files)
    command = [sys.executable, "-m", "tools.serve", *argv]
    env = {**os.environ, CHILD_ENV: "1"}
    child = subprocess.Popen(command, env=env)
    # A restart must not open a second browser window, and its pages
    # were built by the old code.
    restart = [a for a in command if a != "--open"] + ["--rebuild"]
    try:
        while True:
            time.sleep(POLL_SECONDS)
            now = code_snapshot(files)
            if now == seen:
                if child.poll() is not None:
                    return child.returncode
                continue
            seen = now
            print("Build code changed; restarting the server...")
            stop(child)
            child = subprocess.Popen(restart, env=env)
    except KeyboardInterrupt:
        return 0
    finally:
        stop(child)


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
    ap.add_argument("--copy-on-select", action="store_true",
                    help="copy a mouse selection to the clipboard on release "
                         "(served pages only; build/site/ is untouched)")
    ap.add_argument("--chapter-toc", action=argparse.BooleanOptionalAction,
                    default=build_site.CHAPTER_TOC,
                    help="per-chapter table of contents on a --watch rebuild "
                         f"(default: {build_site.CHAPTER_TOC})")
    ap.add_argument("--rebuild", action="store_true",
                    help=argparse.SUPPRESS)  # The supervisor's restart
    args = ap.parse_args(argv)

    if not SITE.exists():
        raise SystemExit(
            f"error: {SITE} not found. Build the site first "
            "(tip site, or python -m tools.build_site).")

    if args.watch and CHILD_ENV not in os.environ:
        return supervise(sys.argv[1:] if argv is None else argv)

    if args.rebuild:
        print("Rebuilding the whole site with the new build code...")
        build_site.build(SITE, args.chapter_toc)

    if args.watch:
        build_site.check_pandoc()
        Handler.watcher = Watcher(SITE, args.chapter_toc)
        Handler.watcher.start()
        Handler.inject += RELOAD_SCRIPT
    if args.copy_on_select:
        Handler.inject += COPY_SCRIPT

    handler = functools.partial(Handler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"Serving {SITE} at {url}  (Ctrl+C to stop)")
    if args.watch:
        print("Watching Chapters/ and the build code; "
              "pages reload after a rebuild.")
    if args.copy_on_select:
        print("Selecting text with the mouse copies it to the clipboard.")
    if args.open:
        # The server socket is already bound, so the browser will
        # connect even if it loads before serve_forever() runs.
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
