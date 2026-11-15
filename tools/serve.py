#!/usr/bin/env python3
"""Serve the built site locally, optionally opening a browser.

`tip serve` runs this with `--watch --copy-on-select` on the existing
`build/site/`. `tip local` builds the site first and adds `--open`.

With `--watch`, a background thread polls `Chapters/*.md` and
`Solutions/*/README.md` (and the few files the whole site is rendered
from: `template.html`, the static assets, and the figures in
`resources/images/`). A changed chapter takes
`build_site.rebuild_chapter()`'s incremental path, two pandoc runs
(the chapter page and its solutions page) rather than the ~95 of a full
build, and a changed solutions file takes the same path through its
chapter, since that path also rewrites the chapter's solutions page (before 2026-10-10 the watcher listed
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
A fresh child that dies, because the save caught a module mid-edit,
leaves the supervisor waiting for the next change to the build code.

With `--copy-on-select`, each served page also carries a script that
copies a mouse selection to the clipboard as soon as the button is
released, for pulling passages out of the rendered book. The copied
text is wrapped in guillemets and followed by its source, so a pasted
passage reads `«...» (31 State Machines › Table-Driven State Machine
#table-driven-state-machine)`: the chapter number and title, the
section title, and the section's anchor. Neither « nor » occurs in the
book, so the marks cannot be mistaken for quoted text. The script then
asks the server (`/__locate`) where the passage sits in the Markdown
and copies it again with the answer appended:
`«...» (31 State Machines › ... #anchor, Chapters/31_....md:412)`, the
source file and the line the passage starts on, so whoever receives
the paste opens that line and does not search for the words (Bruce,
2026-11-12, after each pasted passage cost a search). `locate()`
drops what the page does not show (backticks, asterisks, brackets, a
link's target) and all whitespace from both sides, so a passage with a
code span or one that crosses a source line break still matches, and a
passage the chapter holds twice resolves to the first copy at or after
its section heading. A passage it cannot find keeps the first form.
`tip local` passes it. Both scripts are added to the response as it is served, so
the files in `build/site/`, the ones the published site is built from,
never contain either.

With `--bookmark`, each served page carries two buttons at the bottom
left, `Save place (b)` and `Go to bookmark (g)`, and the keys of the
same names. Saving POSTs the passage at the top of the viewport to
`/__bookmark`, which writes `bookmark.json` at the repo root: the page
file, its title, the nearest `h2`/`h3` and that heading's id, the first
120 characters of the block at the top of the viewport and how far the
viewport top is into it (0 to 1), the Markdown `file:line` that
`locate()` finds for it, and a timestamp. The server then commits that
file with `git commit --only -- bookmark.json`, so other staged or
modified files stay out of the commit, and it reports "already saved"
when the file is unchanged. It runs no `git push` and no amend. The
author pushes, pulls on the other machine, and presses `g`: the page
opens at the saved block (a section that is folded is opened first),
or at the saved heading when the passage has changed. The script is
added to the response as it is served, so `build/site/` and the
published site never carry it. `GET /__bookmark` returns the file.

Usage:
    python -m tools.serve             # serve build/site/ at :8000
    python -m tools.serve --open      # serve and open a browser
    python -m tools.serve --watch     # rebuild and reload on edits
    python -m tools.serve --copy-on-select  # selection copies itself
    python -m tools.serve --bookmark  # b saves, g restores a place
    python -m tools.serve --port 9000 # serve on another port
"""

import argparse
import contextlib
import functools
import http.server
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from typing import Any

from tools import build_site
from tools.config import BUILD_SITE_DIR as SITE
from tools.config import CHAPTERS_DIR, ROOT, SOLUTIONS_DIR
from tools.repo import (
    chapter_stem, is_solutions_file, md_files, solutions_file,
)

POLL_SECONDS = 1.0
RELOAD_PATH = "/__reload"
LOCATE_PATH = "/__locate"
BOOKMARK_PATH = "/__bookmark"
BOOKMARK_FILE = ROOT / "bookmark.json"
BOOKMARK_TEXT = 120    # Characters of the top block a bookmark keeps
BOOKMARK_LOCK = threading.Lock()

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
# The first write happens inside the mouseup handler, where the gesture
# is certain; the second, with the source line from /__locate, follows
# the fetch and replaces it. If the fetch or the second write fails,
# the clipboard keeps the first form.
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
    let heading = "";
    for (const h of document.querySelectorAll("h2, h3")) {
      if (range.comparePoint(h, 0) > 0) break;
      heading = h.textContent.trim();
      section = heading;
      if (h.id) section += " #" + h.id;
    }
    if (section) parts.push(section);
    return {label: parts.join(" › "), file, heading};
  };
  const locate = async (text, where) => {
    const response = await fetch("%s", {
      method: "POST",
      body: JSON.stringify(
        {page: where.file, heading: where.heading, text}),
    });
    return response.ok ? (await response.text()).trim() : "";
  };
  document.addEventListener("mouseup", (event) => {
    const tag = event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    const selection = document.getSelection();
    const text = selection.toString();
    if (text.trim() === "" || selection.rangeCount === 0) return;
    const where = source(selection.getRangeAt(0));
    const wrap = (line) => "«" + text + "» (" + where.label
      + (line ? ", " + line : "") + ")";
    const fallback = () => { if (document.execCommand("copy")) show(); };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(wrap("")).then(show, fallback);
      locate(text, where).then((line) => {
        if (line) return navigator.clipboard.writeText(wrap(line));
      }).catch(() => {});
    } else {
      fallback();
    }
  });
})();
</script>
""" % LOCATE_PATH

# Saves and restores a reading place. The bar sits at the bottom left,
# since the copy toast uses the bottom right, and fades to 0.45 opacity
# until the pointer or the keyboard focus reaches it. The keys b and g
# do the same as the buttons, and give way to a text field, a modifier,
# or a handler that already took the key (the search uses / and Ctrl+K).
# A place is the first block (paragraph, list item, listing, table, and
# so on) whose bottom edge is below the top of the viewport, with the
# fraction of it that has scrolled past. Blocks inside a closed
# <details> have no layout box, so saving skips them. Restoring
# searches every block, matches the saved text as a prefix of the
# block's text, prefers a match at or after the saved heading, and opens
# the <details> around it before it scrolls. A bookmark on another page
# sets a sessionStorage flag and navigates; the new page restores after
# its load event, once images have settled the layout, and does not
# navigate a second time.
BOOKMARK_SCRIPT = r"""
<script>
(() => {
  const PATH = "__PATH__";
  const KEY = "tip-bookmark-go";
  const BLOCKS = "h2, h3, p, pre, li, blockquote, table, figure, summary";
  const root = document.querySelector(".page") || document.body;
  const bar = document.createElement("div");
  bar.style.cssText = "position:fixed;bottom:1rem;left:1rem;display:flex;"
    + "gap:0.4rem;align-items:center;font:0.75rem sans-serif;"
    + "transition:opacity 0.2s;z-index:9999";
  let hot = false;
  let shown = false;
  const paint = () => { bar.style.opacity = hot || shown ? "1" : "0.45"; };
  const warm = (on) => () => { hot = on; paint(); };
  bar.addEventListener("mouseenter", warm(true));
  bar.addEventListener("mouseleave", warm(false));
  bar.addEventListener("focusin", warm(true));
  bar.addEventListener("focusout", warm(false));
  const button = (label, action) => {
    const b = document.createElement("button");
    b.textContent = label;
    b.style.cssText = "font:inherit;padding:0.2rem 0.5rem;cursor:pointer;"
      + "border:1px solid #888;border-radius:4px;background:#fff;color:#333";
    b.addEventListener("click", action);
    return b;
  };
  const status = document.createElement("span");
  status.style.cssText = "display:none;padding:0.2rem 0.6rem;"
    + "background:#333;color:#fff;border-radius:4px";
  let hide = null;
  const say = (text) => {
    status.textContent = text;
    status.style.display = "";
    shown = true;
    paint();
    clearTimeout(hide);
    hide = setTimeout(() => {
      status.style.display = "none";
      shown = false;
      paint();
    }, 2500);
  };
  const squash = (text) => text.replace(/\s+/g, " ").trim();
  const words = (el) => squash(el.textContent).slice(0, __SIZE__).trim();
  const file = () => location.pathname.split("/").pop() || "index.html";
  const blocks = (everything) => [...root.querySelectorAll(BLOCKS)].filter(
    (el) => (everything || el.offsetParent !== null)
      && squash(el.textContent) !== "");
  const save = async () => {
    const block = blocks(false).find(
      (el) => el.getBoundingClientRect().bottom > 8);
    if (!block) { say("nothing to save"); return; }
    const rect = block.getBoundingClientRect();
    const offset = rect.height > 0
      ? Math.min(1, Math.max(0, -rect.top / rect.height)) : 0;
    let heading = null;
    for (const h of root.querySelectorAll("h2, h3")) {
      if (h.offsetParent !== null
          && h.getBoundingClientRect().top <= rect.top + 1) heading = h;
    }
    const h1 = document.querySelector("h1");
    const mark = {
      page: file(),
      title: h1 ? squash(h1.textContent) : document.title,
      heading: heading ? squash(heading.textContent) : "",
      heading_id: heading ? heading.id : "",
      text: words(block),
      offset: Math.round(offset * 1000) / 1000,
    };
    try {
      const response = await fetch(PATH, {
        method: "POST", body: JSON.stringify(mark)});
      if (!response.ok) {
        say("not saved: " + (await response.text()).trim());
        return;
      }
      say((await response.json()).message);
    } catch (error) {
      say("not saved: server unreachable");
    }
  };
  const reveal = (el) => {
    for (let d = el.closest("details"); d;
         d = d.parentElement && d.parentElement.closest("details")) {
      d.open = true;
    }
  };
  const go = (mark) => {
    const anchor = mark.heading_id
      ? document.getElementById(mark.heading_id) : null;
    let matches = [];
    if (mark.text) {
      matches = blocks(true).filter(
        (el) => squash(el.textContent).startsWith(mark.text));
    }
    const block = matches.find((el) => anchor && (el === anchor
      || anchor.compareDocumentPosition(el)
        & Node.DOCUMENT_POSITION_FOLLOWING)) || matches[0];
    if (block) {
      reveal(block);
      const rect = block.getBoundingClientRect();
      window.scrollTo({
        top: window.scrollY + rect.top + mark.offset * rect.height,
        behavior: "instant"});
      const before = block.style.outline;
      block.style.outline = "2px solid #e6a100";
      setTimeout(() => { block.style.outline = before; }, 1500);
      say("at your bookmark");
    } else if (anchor) {
      reveal(anchor);
      anchor.scrollIntoView({block: "start", behavior: "instant"});
      say("passage not found; at its section");
    } else {
      say("bookmark not found on this page");
    }
  };
  const restore = async (resuming) => {
    let mark = {};
    try {
      mark = await (await fetch(PATH, {cache: "no-store"})).json();
    } catch (error) {
      say("server unreachable");
      return;
    }
    if (!mark.page) { say("no bookmark yet"); return; }
    if (mark.page === file()) { go(mark); return; }
    if (resuming) { say("bookmark not found on this page"); return; }
    sessionStorage.setItem(KEY, "1");
    location.href = encodeURIComponent(mark.page);
  };
  bar.append(button("Save place (b)", save),
             button("Go to bookmark (g)", () => restore(false)), status);
  paint();
  document.body.appendChild(bar);
  document.addEventListener("keydown", (event) => {
    if (event.defaultPrevented || event.ctrlKey || event.metaKey
        || event.altKey) return;
    const target = event.target;
    if (target.isContentEditable
        || ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)) return;
    if (event.key === "b") save();
    else if (event.key === "g") restore(false);
  });
  const resume = () => {
    if (!sessionStorage.getItem(KEY)) return;
    sessionStorage.removeItem(KEY);
    restore(true);
  };
  if (document.readyState === "complete") resume();
  else window.addEventListener("load", resume);
})();
</script>
""".replace("__PATH__", BOOKMARK_PATH).replace("__SIZE__", str(BOOKMARK_TEXT))

# What a rendered page does not show of its Markdown: a link's target,
# then (dropped from both sides of the comparison) backticks,
# asterisks, square brackets, and all whitespace. The target must look
# like one (an anchor, a URL, a file), so `table[0](arg)` in a listing
# keeps its call. Typographic quotes and the ellipsis are pandoc's.
LINK_TARGET = re.compile(
    r"\]\((?:#|https?:|[\w./-]*\.(?:md|svg|png|html))[^)\s]*\)")
HEADING_ID = re.compile(r"\s*\{#[^}]*\}\s*$")
DROPPED = re.compile(r"[\s`*\[\]]+")
TYPOGRAPHIC = str.maketrans(
    {"‘": "'", "’": "'", "“": '"', "”": '"'})


def squeeze(text: str) -> str:
    """`text` as the comparison sees it: ASCII quotes, three dots for
    an ellipsis, and no whitespace, backticks, asterisks, or brackets."""
    text = text.translate(TYPOGRAPHIC).replace("…", "...")
    return DROPPED.sub("", text)


def page_source(page: str) -> Path | None:
    """The Markdown file a served page was rendered from, if it has one:
    a chapter for `<stem>.html`, its solutions file for
    `<stem>.solutions.html`."""
    name = Path(page).name
    if name.endswith(".solutions.html"):
        md = solutions_file(name.removesuffix(".solutions.html"))
    elif name.endswith(".html"):
        md = CHAPTERS_DIR / f"{name.removesuffix('.html')}.md"
    else:
        return None
    return md if md.is_file() else None


def locate(md: Path, text: str, heading: str = "") -> int | None:
    """The 1-based line of `md` on which the rendered passage `text`
    starts, or None when the file does not hold it.

    Both sides are compared squeezed, so a passage that crosses a
    source line break or holds a code span matches. With `heading`, the
    section title the passage sits under, the first match at or after
    that heading's line wins; a passage found only above it (a heading
    the page renders differently from its source) still resolves.
    """
    needle = squeeze(text)
    if not needle:
        return None
    want = squeeze(heading)
    starts: list[int] = []   # offset in `flat` where each line begins
    parts: list[str] = []
    offset = section = 0     # `section`: offset of the heading's line
    lines = md.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if want and line.startswith("#") and squeeze(
                HEADING_ID.sub("", line.lstrip("#"))) == want:
            section = offset
        part = squeeze(LINK_TARGET.sub("]", line))
        starts.append(offset)
        parts.append(part)
        offset += len(part)
    flat = "".join(parts)
    found = flat.find(needle, section)
    if found < 0:
        found = flat.find(needle)
    if found < 0:
        return None
    # The last line that starts at or before the match and has text.
    for index in range(len(starts) - 1, -1, -1):
        if starts[index] <= found and parts[index]:
            return index + 1
    return None


def clean_bookmark(request: object, site: Path = SITE) -> dict:
    """The bookmark fields from a POST body, coerced, or a ValueError
    whose message says what is wrong.

    `page` must be the base name of a `.html` file in `site`: no
    separators, no `..`. `text` is collapsed and cut to 120 characters
    the way the script cuts it, and `offset` is clamped to 0..1.
    """
    if not isinstance(request, dict):
        raise ValueError("expected a JSON object")
    fields: dict = {}
    for key in ("page", "title", "heading", "heading_id", "text"):
        value = request.get(key, "")
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
        fields[key] = value
    page = fields["page"]
    if (not page.endswith(".html") or "/" in page or "\\" in page
            or ".." in page or not (site / page).is_file()):
        raise ValueError(f"unknown page: {page!r}")
    try:
        offset = float(request.get("offset", 0))
    except (TypeError, ValueError):
        raise ValueError("offset must be a number") from None
    if offset != offset:    # NaN
        offset = 0.0
    fields["text"] = " ".join(fields["text"].split())[:BOOKMARK_TEXT].strip()
    for key in ("title", "heading", "heading_id"):
        fields[key] = " ".join(fields[key].split())
    fields["offset"] = round(min(1.0, max(0.0, offset)), 3)
    return fields


def bookmark_source(page: str, text: str, heading: str) -> str:
    """`Chapters/NN_....md:LINE` for a bookmark's passage, or "" when
    the Markdown does not hold it. A shorter start of the text is the
    second and third try, since the page can render a passage's end
    differently from its source."""
    md = page_source(page)
    if md is None:
        return ""
    for size in (len(text), 60, 30):
        if size < 1:
            continue
        line = locate(md, text[:size], heading)
        if line is not None:
            return f"{md.relative_to(ROOT).as_posix()}:{line}"
    return ""


def bookmark_message(mark: dict) -> str:
    """The commit message: `Bookmark: <title> › <heading> (<source>)`,
    without the heading or the source when it is empty."""
    message = f"Bookmark: {mark['title']}"
    if mark.get("heading"):
        message += f" › {mark['heading']}"
    if mark.get("source"):
        message += f" ({mark['source']})"
    return message


def load_bookmark(file: Path | None = None) -> dict:
    """The saved bookmark, or an empty dict when there is none."""
    try:
        mark = json.loads((file or BOOKMARK_FILE).read_text(
            encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return mark if isinstance(mark, dict) else {}


def write_bookmark(mark: dict, file: Path | None = None) -> None:
    file = file or BOOKMARK_FILE
    text = json.dumps(mark, indent=2, ensure_ascii=False) + "\n"
    with file.open("w", encoding="utf-8", newline="\n") as out:
        out.write(text)


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True,
                          text=True, timeout=30)


def first_line(result: subprocess.CompletedProcess[str]) -> str:
    lines = (result.stderr.strip() or result.stdout.strip()).splitlines()
    return lines[0] if lines else f"git exited {result.returncode}"


def commit_bookmark(mark: dict, root: Path | None = None,
                    file: Path | None = None) -> tuple[bool, str]:
    """Commit the bookmark file alone and report (committed, message).

    `git commit --only -- <file>` leaves other staged and modified files
    out of the commit. An unchanged file is "already saved". Any git
    failure comes back as a message; nothing is pushed or amended.
    """
    root = root or ROOT
    name = (file or BOOKMARK_FILE).name
    try:
        added = git(root, "add", "--", name)
        if added.returncode != 0:
            return False, f"saved, not committed: {first_line(added)}"
        # Exit 0: the index matches HEAD for this file. Exit 1: it
        # differs, as on the first save, when HEAD lacks the file.
        changed = git(root, "diff", "--cached", "--quiet", "--", name)
        if changed.returncode == 0:
            return False, "already saved"
        if changed.returncode != 1:
            return False, f"saved, not committed: {first_line(changed)}"
        done = git(root, "commit", "--only", "--quiet", "-m",
                   bookmark_message(mark), "--", name)
        if done.returncode != 0:
            return False, f"saved, not committed: {first_line(done)}"
    except (OSError, subprocess.SubprocessError) as error:
        return False, f"saved, not committed: {error}"
    return True, "saved and committed"


def save_bookmark(mark: dict, root: Path | None = None,
                  file: Path | None = None) -> tuple[bool, str]:
    """Write the bookmark file and commit it; saves run one at a time."""
    with BOOKMARK_LOCK:
        write_bookmark(mark, file)
        return commit_bookmark(mark, root, file)


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
    # under --watch, COPY_SCRIPT under --copy-on-select, BOOKMARK_SCRIPT
    # under --bookmark, any combination, or none.
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
        if self.path.split("?")[0] == BOOKMARK_PATH:
            self.reply(200, json.dumps(load_bookmark()).encode(),
                       "application/json; charset=utf-8")
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

    def do_POST(self) -> None:  # noqa: N802
        route = self.path.split("?")[0]
        if route == LOCATE_PATH:
            self.reply_locate()
        elif route == BOOKMARK_PATH:
            self.reply_bookmark()
        else:
            self.send_error(404)

    def read_json(self) -> Any:
        size = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(size))

    def reply_locate(self) -> None:
        """Answer /__locate: `Chapters/NN_....md:LINE` for the passage
        in the request, or an empty body when it cannot be placed."""
        answer = ""
        try:
            request = self.read_json()
            md = page_source(str(request["page"]))
            if md is not None:
                line = locate(md, str(request["text"]),
                              str(request.get("heading", "")))
                if line is not None:
                    answer = f"{md.relative_to(ROOT).as_posix()}:{line}"
        except (ValueError, KeyError, TypeError, OSError):
            answer = ""
        self.reply(200, answer.encode(), "text/plain; charset=utf-8")

    def reply_bookmark(self) -> None:
        """Answer a POST to /__bookmark: validate, write, commit."""
        try:
            mark = clean_bookmark(self.read_json(), Path(self.directory))
        except ValueError as error:
            self.reply(400, str(error).encode(),
                       "text/plain; charset=utf-8")
            return
        mark["source"] = bookmark_source(
            mark["page"], mark["text"], mark["heading"])
        mark["saved"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        try:
            committed, message = save_bookmark(mark)
        except OSError as error:
            self.reply(500, f"could not write the file: {error}".encode(),
                       "text/plain; charset=utf-8")
            return
        print(f"Bookmark: {message}")
        body = json.dumps({"saved": True, "committed": committed,
                           "message": message}).encode()
        self.reply(200, body, "application/json; charset=utf-8")

    def reply(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def reply_token(self) -> None:
        watcher = type(self).watcher
        body = (watcher.token if watcher else "0").encode()
        self.reply(200, body, "text/plain; charset=utf-8")

    def reply_page(self, path: str) -> None:
        html = Path(path).read_text(encoding="utf-8")
        inject = type(self).inject
        marker = "</body>"
        if marker in html:
            head, _, tail = html.rpartition(marker)
            html = f"{head}{inject}{marker}{tail}"
        else:
            html += inject
        self.reply(200, html.encode("utf-8"), "text/html; charset=utf-8")

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
    restarted = waiting = False
    try:
        while True:
            time.sleep(POLL_SECONDS)
            now = code_snapshot(files)
            if now == seen:
                code = child.poll()
                if code is None:
                    continue
                # A save caught mid-edit (a syntax error, a half-renamed
                # name) kills the restarted child. The next save fixes
                # it, so wait for that instead of ending the session.
                if not restarted or code == 0:
                    return code
                if not waiting:
                    print(f"The server exited ({code}); waiting for "
                          "the next change to the build code...")
                    waiting = True
                continue
            seen = now
            print("Build code changed; restarting the server...")
            stop(child)
            child = subprocess.Popen(restart, env=env)
            restarted, waiting = True, False
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
    ap.add_argument("--bookmark", action="store_true",
                    help="b saves the reading place to bookmark.json and "
                         "commits it, g returns to it (served pages only)")
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
    if args.bookmark:
        Handler.inject += BOOKMARK_SCRIPT

    handler = functools.partial(Handler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("", args.port), handler)
    url = f"http://localhost:{args.port}/"
    print(f"Serving {SITE} at {url}  (Ctrl+C to stop)")
    if args.watch:
        print("Watching Chapters/ and the build code; "
              "pages reload after a rebuild.")
    if args.copy_on_select:
        print("Selecting text with the mouse copies it to the clipboard.")
    if args.bookmark:
        print("Press b to save your place in bookmark.json (committed, "
              "never pushed) and g to return to it.")
    if args.open:
        # The server socket is already bound, so the browser will
        # connect even if it loads before serve_forever() runs.
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
