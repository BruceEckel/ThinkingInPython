#!/usr/bin/env python
"""Report every listing line wider than a chosen width, in the browser.

A survey tool, not a gate: `listing_width.py` enforces the book's
60-character limit, while this answers "what would break at N?"
when weighing a narrower (or wider) limit, an e-reader column, or a
code font size. Every line of every ```python block is measured by
its raw rstripped length, no pragma exemption, since the question
here is what a reader's screen has to fit.

The report is a self-contained HTML page, written to
build/reports/code_width.html and served from a local port so a click
can reach the editor (below); the default browser opens on it. It
groups the lines by chapter, and each row names the extracted file
and line (`Examples/` for Chapters/, `SolutionsCode/` for Solutions/,
`(fragment)` for a block extract_examples.py never writes), the
Markdown line, the width, and the line itself with everything past
the limit highlighted. The page carries every line wider than
SLIDER_MIN columns, so its width slider re-filters and re-highlights
live, without another run; `--width` only sets where the slider
starts. Widths past the 60-character gate are marked separately from
those merely over the slider's value. A checkbox, on by default,
hides the lines the gate itself forgives: those whose code fits the
slider's width once a trailing `# type: ignore` pragma is excluded
(`listing_width.py` decides that, so the two agree). A second
checkbox, off by default, keeps only the lines that are wide because
of a comment: the code before the `#` fits the slider's width and the
comment carries it over. A `#:` output marker is program output, not a
comment, so it never qualifies.

Clicking a row opens the chapter in Zed with the cursor on that
line; the row's file cell opens the extracted file at its own line
instead, and a chapter heading opens the chapter. A browser page
cannot run a program, and Zed's `zed://file/<path>:<line>` URL scheme
opens nothing on Windows (tried: it raises the window and stops), so
the script stays up as a small HTTP server on 127.0.0.1 while the
page is in use, and a click asks it (`/open?path=...&line=N`) to run
the Zed CLI, `zed path:line`, the documented way to land on a line.
The server accepts only files under the repo and exits on Ctrl+C.
The CLI is found through `$ZED`, then `zed` on PATH, then Zed's
per-user install location on Windows and macOS.

The page opens (and the server runs) only when stdout is a terminal,
so a smoke test or a pipe just writes the file and prints its path;
`--open` and `--no-open` override that. `--tsv` skips the page and prints one
tab-separated row per line (code location, Markdown location, width,
line) for `cut -f` or a spreadsheet. Exits 0 whatever it finds.

Usage:
    python tools/code_width.py --width 50
    python tools/code_width.py --width 55 Chapters Solutions
    python tools/code_width.py --tsv > wide.tsv
    make code-width WIDTH=50
"""
import argparse
import contextlib
import html
import http.server
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import webbrowser
from collections.abc import Iterator
from itertools import groupby
from pathlib import Path
from typing import Final, NamedTuple

from extract_examples import route
from listing_width import WIDTH_LIMIT, _effective_width, _triple_states
from tools_config import BUILD_DIR, ROOT
from tools_markdown import Document
from tools_pycode import scan_line
from tools_repo import add_paths_arg, md_files, write_text_lf

DEFAULT_WIDTH = 60
# The slider's range. Every line wider than SLIDER_MIN is embedded in
# the page, so the slider can drop to it without another run.
SLIDER_MIN, SLIDER_MAX = 40, 80
REPORT: Final = BUILD_DIR / "reports" / "code_width.html"
# Where each Markdown tree's blocks extract to, by the tree's dir name.
TREES = {"Chapters": "Examples", "Solutions": "SolutionsCode"}
FRAGMENT: Final = "(fragment)"
# Where Zed's per-user installer puts the CLI, when it is not on PATH.
ZED_INSTALLS: Final = (
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/Zed/bin/Zed.exe",
    Path("/usr/local/bin/zed"),
    Path.home() / ".local/bin/zed",
)


class Wide(NamedTuple):
    source: str
    """`Chapters/NN_Chapter.md`, relative to the repo root."""
    path: Path
    """The Markdown file, absolute."""
    tree: str
    """Where the file's listings extract, e.g. `Examples/05_Functions`."""
    code: str
    """`slug.py:line` within that directory, or `(fragment)`."""
    md_line: int
    width: int
    """The line's raw width."""
    effective: int
    """Its width with a trailing `# type: ignore` excluded, per the gate."""
    code_width: int
    """The width of the code before a `#` comment; the full width if none."""
    line: str


# ── finding ─────────────────────────────────────────────────────────────

def _code_width(line: str, triple: str | None) -> int:
    """Width of `line` before its comment, or of all of it without one.

    A `#:` output marker counts as program output rather than a
    comment: shortening it means changing what the program prints.
    """
    hash_i, _ = scan_line(line, triple)
    if hash_i == -1 or line[hash_i:].startswith("#:"):
        return len(line)
    return len(line[:hash_i].rstrip())


def find(doc: Document, width: int) -> Iterator[Wide]:
    """Every listing line in `doc` wider than `width`."""
    try:
        source = doc.path.relative_to(ROOT).as_posix()
    except ValueError:
        source = doc.path.as_posix()
    tree_root = TREES.get(doc.path.parent.name, doc.path.parent.name)
    tree = f"{tree_root}/{doc.path.stem}"
    for block in doc.python_blocks():
        target = route(doc, block)
        triples = _triple_states(block.lines)
        for i, raw in enumerate(block.lines):
            line = raw.rstrip()
            if len(line) <= width:
                continue
            if target is None:
                code = FRAGMENT
            else:
                # route() prefixes the chapter stem (or utils/); the row
                # shows only the part below the group's directory.
                name = target.removeprefix(f"{doc.path.stem}/")
                code = f"{name}:{i + 1}"
            yield Wide(source, doc.path, tree, code, block.line_number(i),
                       len(line), _effective_width(block.lines, i, triples),
                       _code_width(line, triples[i]), line)


# ── the page ────────────────────────────────────────────────────────────

CSS: Final = """
:root {
  --bg: #fdfdfb; --fg: #222; --dim: #777; --rule: #ddd;
  --head: #f2f2ee; --path: #2a6e3f; --warn: #9a6a00; --over: #b3261e;
  --spill-bg: #ffd9d6; --spill-fg: #7a1410; --guide: #b3261e;
  --chip: #eee; --link: #1d4ed8;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1b1b1f; --fg: #e6e6e6; --dim: #9a9a9a; --rule: #333;
    --head: #24242a; --path: #7fd39a; --warn: #e6b84a; --over: #ff7b72;
    --spill-bg: #5a1f1a; --spill-fg: #ffd7d3; --guide: #ff7b72;
    --chip: #2e2e34; --link: #8ab4f8;
  }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg);
  font: 15px/1.45 system-ui, sans-serif; }
header { position: sticky; top: 0; background: var(--head);
  border-bottom: 1px solid var(--rule); padding: 0.7rem 1.2rem;
  display: flex; flex-wrap: wrap; gap: 1rem 2rem; align-items: center;
  z-index: 1; }
header h1 { font-size: 1.1rem; margin: 0; }
header label { display: flex; align-items: center; gap: 0.5rem; }
header input[type=range] { width: 14rem; }
header input[type=checkbox] { margin: 0; }
header output { font-family: ui-monospace, monospace; font-weight: bold;
  min-width: 2ch; }
#summary { color: var(--dim); }
#summary b { color: var(--fg); }
#summary .over { color: var(--over); }
main { padding: 0.5rem 1.2rem 3rem; }
details { margin: 0.9rem 0; }
summary { cursor: pointer; font-weight: 600; padding: 0.25rem 0;
  display: flex; gap: 0.8rem; align-items: baseline; }
summary a { color: inherit; text-decoration: none; }
summary a:hover { text-decoration: underline; }
summary .tree { color: var(--path); font-weight: normal;
  font-family: ui-monospace, monospace; font-size: 0.9em; }
summary .count { color: var(--dim); font-weight: normal;
  background: var(--chip); border-radius: 1em; padding: 0 0.6em;
  font-size: 0.85em; }
table { border-collapse: collapse; margin: 0.2rem 0 0 1rem;
  font-family: ui-monospace, "Cascadia Mono", Consolas, monospace;
  font-size: 13px; }
td { padding: 0.15rem 0.7rem 0.15rem 0; vertical-align: top;
  white-space: pre; }
tr[data-path] { cursor: pointer; }
tr[data-path]:hover td { background: var(--chip); }
#status { color: var(--over); }
td.code a { color: inherit; text-decoration: none; }
td.code a:hover { text-decoration: underline; }
td.code { color: var(--path); }
td.code.fragment { color: var(--dim); font-style: italic; }
td.md { color: var(--dim); }
td.w { text-align: right; font-weight: bold; }
tr.warn td.w { color: var(--warn); }
tr.over td.w { color: var(--over); }
td.line .head { border-right: 2px solid var(--guide); }
td.line .spill { background: var(--spill-bg); color: var(--spill-fg); }
tr.hidden, details.hidden { display: none; }
footer { color: var(--dim); padding: 0 1.2rem 2rem; font-size: 0.85em; }
"""

JS: Final = """
const rows = [...document.querySelectorAll('tr[data-w]')];
const groups = [...document.querySelectorAll('details')];
const slider = document.getElementById('width');
const hidePragma = document.getElementById('pragma');
const onlyComment = document.getElementById('comment');
const shown = document.getElementById('shown');
const summary = document.getElementById('summary');
const gate = GATE;
function render() {
  const w = +slider.value;
  shown.value = w;
  let total = 0, over = 0;
  for (const tr of rows) {
    const width = +tr.dataset.w;
    // With the box checked, a line is judged by the gate's width:
    // its code with a trailing `# type: ignore` left out.
    const judged = hidePragma.checked ? +tr.dataset.ew : width;
    let visible = judged > w;
    if (visible && onlyComment.checked) {
      // Wide because of a comment: there is one (the code is shorter
      // than the line) and the code alone would fit.
      const code = +tr.dataset.cw;
      visible = code < width && code <= w;
    }
    tr.classList.toggle('hidden', !visible);
    if (!visible) continue;
    total++;
    if (judged > gate) over++;
    tr.classList.toggle('over', judged > gate);
    tr.classList.toggle('warn', judged <= gate);
    const line = tr.dataset.text;
    tr.querySelector('.head').textContent = line.slice(0, w);
    tr.querySelector('.spill').textContent = line.slice(w);
  }
  let files = 0;
  for (const d of groups) {
    const n = d.querySelectorAll('tr[data-w]:not(.hidden)').length;
    d.classList.toggle('hidden', n === 0);
    d.querySelector('.count').textContent = n + (n === 1 ? ' line' : ' lines');
    if (n) files++;
  }
  let text = `<b>${total}</b> line${total === 1 ? '' : 's'} wider than `
    + `<b>${w}</b> in <b>${files}</b> file${files === 1 ? '' : 's'}`;
  if (w < gate) text += `; <span class="over">${over}</span> past the ${gate} gate`;
  summary.innerHTML = text + '.';
}
const status = document.getElementById('status');
let statusTimer = 0;
function flash(text) {
  status.textContent = text;
  clearTimeout(statusTimer);
  statusTimer = setTimeout(() => status.textContent = '', 6000);
}
function openInZed(path, line) {
  const q = new URLSearchParams({path, line});
  fetch('/open?' + q).then(r => {
    if (!r.ok) r.text().then(t => flash(t || `open failed (${r.status})`));
  }).catch(() => flash('no report server: run make code-width again'));
}
document.querySelector('main').addEventListener('click', e => {
  const a = e.target.closest('a[data-path]');
  const tr = e.target.closest('tr[data-path]');
  const el = a || tr;
  if (!el) return;
  e.preventDefault();
  openInZed(el.dataset.path, el.dataset.line);
});
slider.addEventListener('input', render);
hidePragma.addEventListener('change', render);
onlyComment.addEventListener('change', render);
document.getElementById('all').onclick =
  () => groups.forEach(d => d.open = true);
document.getElementById('none').onclick =
  () => groups.forEach(d => d.open = false);
render();
"""


def open_attrs(path: Path, line: int) -> str:
    """The data attributes a click hands to `/open`: repo-relative path."""
    rel = path.resolve().relative_to(ROOT).as_posix()
    return f'data-path="{html.escape(rel)}" data-line="{line}"'


def row(w: Wide) -> str:
    if w.code == FRAGMENT:
        code = f'<td class="code fragment">{FRAGMENT}</td>'
    else:
        name, _, line = w.code.rpartition(":")
        code = (f'<td class="code"><a href="#" '
                f'{open_attrs(ROOT / w.tree / name, int(line))} '
                f'title="open {html.escape(w.tree)}/{html.escape(name)} '
                f'in Zed">{html.escape(w.code)}</a></td>')
    return (f'<tr data-w="{w.width}" data-ew="{w.effective}" '
            f'data-cw="{w.code_width}" {open_attrs(w.path, w.md_line)} '
            f'data-text="{html.escape(w.line)}" '
            f'title="open {html.escape(w.source)}:{w.md_line} in Zed">'
            f'{code}'
            f'<td class="md">md {w.md_line}</td>'
            f'<td class="w">{w.width}</td>'
            '<td class="line"><span class="head"></span>'
            '<span class="spill"></span></td></tr>')


def group_html(source: str, group: list[Wide]) -> str:
    tree = html.escape(group[0].tree)
    rows = "\n".join(row(w) for w in group)
    return (f'<details open><summary><a href="#" '
            f'{open_attrs(group[0].path, 1)} '
            f'title="open in Zed">{html.escape(source)}</a> '
            f'<span class="tree">&rarr; {tree}/</span> '
            '<span class="count"></span></summary>'
            f"<table>{rows}</table></details>")


def page(found: list[Wide], width: int) -> str:
    groups = "\n".join(group_html(src, list(g))
                       for src, g in groupby(found, key=lambda w: w.source))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Listing widths</title>
<style>{CSS}</style></head>
<body>
<header>
  <h1>Listing widths</h1>
  <label>wider than
    <input id="width" type="range" min="{SLIDER_MIN}" max="{SLIDER_MAX}"
           value="{width}">
    <output id="shown">{width}</output>
  </label>
  <label><input id="pragma" type="checkbox" checked>
    hide lines that fit once a trailing <code># type: ignore</code>
    is excluded</label>
  <label><input id="comment" type="checkbox">
    only lines wide because of a comment</label>
  <span id="summary"></span>
  <span id="status"></span>
  <span><button id="all">expand all</button>
        <button id="none">collapse all</button></span>
</header>
<main>
{groups}
</main>
<footer>Each row: extracted file and line, Markdown line, width, then
the line with its overflow past the slider's column highlighted.
Widths past the {WIDTH_LIMIT}-character gate are red; those only over
the slider are amber. The checkbox applies the gate's one exemption: a
line whose code fits the width and overflows only by its trailing
<code># type: ignore</code>. The comment box keeps only lines whose code
fits and whose comment carries them over; a <code>#:</code> output marker
counts as output, not a comment. Click a row to open the chapter in
Zed at that line; click the file cell to open the extracted file at its
line instead (both need the report server that
<code>make code-width</code> leaves running). Generated by
tools/code_width.py.</footer>
<script>{JS.replace("GATE", json.dumps(WIDTH_LIMIT))}</script>
</body></html>
"""


# ── opening files in the editor ────────────────────────────────────────

def find_zed() -> Path | None:
    """The Zed CLI: `$ZED`, then PATH, then the per-user install."""
    if env := os.environ.get("ZED"):
        return Path(env)
    if found := shutil.which("zed"):
        return Path(found)
    return next((p for p in ZED_INSTALLS if p.is_file()), None)


class Handler(http.server.BaseHTTPRequestHandler):
    """Serves the page at `/` and opens a repo file on `/open`."""

    page: bytes = b""
    zed: Path | None = None

    def do_GET(self) -> None:  # noqa: N802 (the base class's name)
        url = urllib.parse.urlsplit(self.path)
        if url.path == "/":
            self._send(200, self.page, "text/html; charset=utf-8")
        elif url.path == "/open":
            self._open(urllib.parse.parse_qs(url.query))
        else:
            self._send(404, b"not found")

    def _open(self, query: dict[str, list[str]]) -> None:
        if self.zed is None:
            self._send(503, b"Zed CLI not found: set ZED to its path")
            return
        rel = query.get("path", [""])[0]
        line = query.get("line", ["1"])[0]
        target = (ROOT / rel).resolve()
        # Only files inside the repo, whatever the query says.
        if not (target.is_relative_to(ROOT) and target.is_file()
                and line.isdigit()):
            self._send(400, b"not a file in this repository")
            return
        subprocess.Popen([str(self.zed), f"{target}:{line}"])
        self._send(204, b"")

    def _send(self, status: int, body: bytes,
              content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass  # Every click would otherwise echo a request line.


def serve(page_text: str) -> None:
    """Serve the page on an ephemeral local port until Ctrl+C."""
    Handler.page = page_text.encode("utf-8")
    Handler.zed = find_zed()
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    zed = Handler.zed or "not found (set ZED to the CLI's path)"
    # flush: serve_forever() never returns, so a redirected stdout would
    # otherwise hold the URL in its buffer until the process ends.
    print(f"Serving the report at {url}  (Ctrl+C to stop)", flush=True)
    print(f"Clicks open files with Zed: {zed}", flush=True)
    webbrowser.open(url)
    with contextlib.suppress(KeyboardInterrupt):
        server.serve_forever()


def print_tsv(found: list[Wide], width: int) -> None:
    for w in found:
        if w.width <= width:
            continue
        code = w.code if w.code == FRAGMENT else f"{w.tree}/{w.code}"
        print(f"{code}\t{w.source}:{w.md_line}\t{w.width}\t{w.line}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--width", type=int, default=DEFAULT_WIDTH,
                    help=f"where the slider starts "
                         f"(default: {DEFAULT_WIDTH})")
    ap.add_argument("--tsv", action="store_true",
                    help="print tab-separated rows instead of a page")
    opening = ap.add_mutually_exclusive_group()
    opening.add_argument("--open", dest="open", action="store_true",
                         default=None, help="serve and open the page even "
                         "when stdout is not a terminal")
    opening.add_argument("--no-open", dest="open", action="store_false",
                         help="write the page only; no server, no browser")
    add_paths_arg(ap)
    args = ap.parse_args(argv)
    paths: list[str | Path] = list(args.paths)
    embed = min(args.width, SLIDER_MIN)
    found = [w for p in md_files(paths)
             for w in find(Document.parse(p), embed)]
    if args.tsv:
        print_tsv(found, args.width)
        return 0
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    text = page(found, args.width)
    write_text_lf(REPORT, text)
    shown = sum(w.effective > args.width for w in found)
    forgiven = sum(w.width > args.width for w in found) - shown
    note = (f" (plus {forgiven} only by a trailing # type: ignore)"
            if forgiven else "")
    print(f"{shown} line(s) wider than {args.width}{note}: {REPORT}")
    open_it = sys.stdout.isatty() if args.open is None else args.open
    if open_it:
        serve(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
