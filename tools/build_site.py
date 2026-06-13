#!/usr/bin/env python3
"""Render the book's Markdown into a static, navigable HTML site.

One command turns ``Markdown/*.md`` into ``build/site/``: a title page with an
ordered table of contents, one HTML page per chapter with previous/next links
and a sidebar, and syntax-highlighted code. Images referenced in the book as
``_images/<name>`` (no extension) are resolved against ``resources/images``
and copied alongside the pages.

Pandoc does the Markdown-to-HTML conversion per chapter; this script handles
discovery, ordering, navigation, image wiring, and the page shell.

Usage:
    python tools/build_site.py            # build into build/site/
    python tools/build_site.py -o DIR     # build somewhere else
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_DIR = ROOT / "Markdown"
IMAGES_SRC = ROOT / "resources" / "images"
STATIC_SRC = ROOT / "resources" / "static"
DEFAULT_OUT = ROOT / "build" / "site"

FRONT_STEM = "00_Front"
IMG_REF = re.compile(r"(!\[[^\]]*\]\()_images/([^)\s]+)(\))")
SETEXT = re.compile(r"^(=+|-+)\s*$")
ATX = re.compile(r"^#+\s+(.*?)\s*#*\s*$")


@dataclass
class Chapter:
    md: Path
    out_name: str  # e.g. "13_The_Singleton.html"
    title: str  # human title for nav and headings


# --------------------------------------------------------------------------- #
# Discovery and metadata
# --------------------------------------------------------------------------- #
def derive_label(stem: str) -> str:
    """Turn a file stem like ``13_The_Singleton`` into ``The Singleton``."""
    body = re.sub(r"^\d+_", "", stem)
    return body.replace("_", " ")


def first_heading(text: str) -> str | None:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        m = ATX.match(line)
        if m:
            return m.group(1).strip()
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if SETEXT.match(nxt):
            return line.strip()
        return None  # first real content is not a heading
    return None


def book_metadata(front_text: str) -> dict[str, str]:
    """Pull title/subtitle/author out of 00_Front's pandoc YAML block."""
    meta = {"title": "Thinking in Python", "subtitle": "", "author": ""}
    m = re.search(r"type:\s*main\s*\n\s*text:\s*(.+)", front_text)
    if m:
        meta["title"] = m.group(1).strip()
    m = re.search(r"^subtitle:\s*(.+)$", front_text, re.MULTILINE)
    if m:
        meta["subtitle"] = m.group(1).strip()
    m = re.search(r"role:\s*author\s*\n\s*text:\s*(.+)", front_text)
    if m:
        meta["author"] = m.group(1).strip()
    return meta


def discover() -> list[Chapter]:
    chapters: list[Chapter] = []
    for md in sorted(MARKDOWN_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        if md.stem == FRONT_STEM:
            title = "Front Matter"
        else:
            title = first_heading(text) or derive_label(md.stem)
        chapters.append(Chapter(md, f"{md.stem}.html", title))
    return chapters


# --------------------------------------------------------------------------- #
# Image handling
# --------------------------------------------------------------------------- #
def build_image_map() -> dict[str, str]:
    """Map bare reference names (``decorator``) to real files (``decorator.gif``)."""
    out: dict[str, str] = {}
    if not IMAGES_SRC.is_dir():
        return out
    for f in IMAGES_SRC.iterdir():
        if f.suffix.lower() in {".png", ".gif", ".jpg", ".jpeg", ".svg"}:
            out[f.stem] = f.name
    return out


def rewrite_images(text: str, img_map: dict[str, str], missing: set[str]) -> str:
    def repl(m: re.Match[str]) -> str:
        name = m.group(2)
        filename = img_map.get(name)
        if not filename:
            missing.add(name)
            filename = f"{name}.png"  # best guess; flagged below
        return f"{m.group(1)}images/{filename}{m.group(3)}"

    return IMG_REF.sub(repl, text)


# --------------------------------------------------------------------------- #
# Pandoc
# --------------------------------------------------------------------------- #
def check_pandoc() -> None:
    if shutil.which("pandoc") is None:
        sys.exit("error: pandoc not found on PATH. Install it: https://pandoc.org/installing.html")


def render_body(markdown: str) -> str:
    proc = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--highlight-style", "pygments"],
        input=markdown, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        sys.exit(f"pandoc failed:\n{proc.stderr}")
    return proc.stdout


def highlight_css() -> str:
    """Ask pandoc for its pygments highlighting CSS, once."""
    sample = "```python\ndef f(x: int) -> int:\n    return x\n```\n"
    proc = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--standalone",
         "--highlight-style", "pygments"],
        input=sample, capture_output=True, text=True, encoding="utf-8",
    )
    blocks = re.findall(r"<style>(.*?)</style>", proc.stdout, re.DOTALL)
    wanted = [b for b in blocks if "sourceCode" in b or "code span" in b]
    return "\n".join(wanted).strip()


# --------------------------------------------------------------------------- #
# Page shell
# --------------------------------------------------------------------------- #
SITE_CSS = """\
:root { --fg:#1b1b1b; --muted:#666; --accent:#1a5fb4; --rule:#e2e2e2; }
* { box-sizing: border-box; }
body { margin:0; color:var(--fg); font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.wrap { display:flex; max-width:1180px; margin:0 auto; }
nav.sidebar { flex:0 0 260px; padding:1.5rem 1rem; border-right:1px solid var(--rule);
  height:100vh; position:sticky; top:0; overflow:auto; font-size:14px; }
nav.sidebar .booktitle { font-weight:700; font-size:15px; display:block; margin-bottom:1rem; }
nav.sidebar ol { list-style:none; margin:0; padding:0; }
nav.sidebar li { margin:.15rem 0; }
nav.sidebar li.current > a { font-weight:700; color:var(--fg); }
main { flex:1 1 auto; padding:2rem 2.5rem; min-width:0; max-width:820px; }
main img { max-width:100%; height:auto; }
pre { background:#f6f8fa; padding:1rem; overflow:auto; border-radius:6px; }
code { font-family:"SF Mono",Consolas,Menlo,monospace; font-size:.9em; }
p code, li code { background:#f0f0f0; padding:.1em .3em; border-radius:3px; }
blockquote { color:var(--muted); border-left:3px solid var(--rule); margin:1rem 0; padding:.2rem 1rem; }
table { border-collapse:collapse; } th,td { border:1px solid var(--rule); padding:.4rem .6rem; }
.chapnav { display:flex; justify-content:space-between; margin-top:3rem;
  padding-top:1rem; border-top:1px solid var(--rule); font-size:14px; }
.chapnav .next { margin-left:auto; text-align:right; }
.titlepage { text-align:center; padding:4rem 1rem 2rem; }
.titlepage h1 { font-size:2.4rem; margin:.2rem 0; }
.titlepage .subtitle { font-size:1.3rem; color:var(--muted); }
.titlepage .author { margin-top:1rem; font-size:1.1rem; }
"""


def sidebar(chapters: list[Chapter], current: str, meta: dict[str, str]) -> str:
    items = []
    for ch in chapters:
        cls = ' class="current"' if ch.out_name == current else ""
        items.append(
            f'    <li{cls}><a href="{ch.out_name}">{html.escape(ch.title)}</a></li>'
        )
    return (
        '<nav class="sidebar">\n'
        f'  <a class="booktitle" href="index.html">{html.escape(meta["title"])}</a>\n'
        "  <ol>\n" + "\n".join(items) + "\n  </ol>\n</nav>"
    )


def chapter_nav(prev: Chapter | None, nxt: Chapter | None) -> str:
    parts = ['<div class="chapnav">']
    if prev:
        parts.append(
            f'  <a class="prev" href="{prev.out_name}">&larr; {html.escape(prev.title)}</a>'
        )
    if nxt:
        parts.append(
            f'  <a class="next" href="{nxt.out_name}">{html.escape(nxt.title)} &rarr;</a>'
        )
    parts.append("</div>")
    return "\n".join(parts)


PAGE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="static/site.css">
<link rel="stylesheet" href="static/highlight.css">
</head>
<body>
<div class="wrap">
{sidebar}
<main>
{content}
</main>
</div>
</body>
</html>
"""


def render_index(chapters: list[Chapter], meta: dict[str, str], sb: str) -> str:
    rows = "\n".join(
        f'    <li><a href="{ch.out_name}">{html.escape(ch.title)}</a></li>'
        for ch in chapters
    )
    sub = (f'<div class="subtitle">{html.escape(meta["subtitle"])}</div>'
           if meta["subtitle"] else "")
    auth = (f'<div class="author">{html.escape(meta["author"])}</div>'
            if meta["author"] else "")
    content = (
        '<div class="titlepage">\n'
        f'  <h1>{html.escape(meta["title"])}</h1>\n'
        f"  {sub}\n  {auth}\n</div>\n"
        "<h2>Contents</h2>\n<ol>\n" + rows + "\n</ol>"
    )
    return PAGE.format(title=html.escape(meta["title"]), sidebar=sb, content=content)


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def build(out_dir: Path) -> int:
    check_pandoc()
    chapters = discover()
    front_text = (MARKDOWN_DIR / f"{FRONT_STEM}.md").read_text(encoding="utf-8")
    meta = book_metadata(front_text)
    img_map = build_image_map()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    static_out = out_dir / "static"
    images_out = out_dir / "images"
    static_out.mkdir(parents=True)
    images_out.mkdir(parents=True)

    (static_out / "site.css").write_text(SITE_CSS, encoding="utf-8")
    (static_out / "highlight.css").write_text(highlight_css(), encoding="utf-8")

    used_images: set[str] = set()
    missing: set[str] = set()

    for i, ch in enumerate(chapters):
        prev = chapters[i - 1] if i > 0 else None
        nxt = chapters[i + 1] if i + 1 < len(chapters) else None
        text = ch.md.read_text(encoding="utf-8")
        # Strip 00_Front's YAML metadata block; pandoc would render it oddly.
        if ch.md.stem == FRONT_STEM:
            text = re.sub(r"\A---.*?(?:\n\.\.\.|\n---)\s*\n", "", text, count=1,
                          flags=re.DOTALL)
        for m in IMG_REF.finditer(text):
            used_images.add(m.group(2))
        text = rewrite_images(text, img_map, missing)
        body = render_body(text)
        content = body + "\n" + chapter_nav(prev, nxt)
        sb = sidebar(chapters, ch.out_name, meta)
        page = PAGE.format(title=html.escape(ch.title), sidebar=sb, content=content)
        (out_dir / ch.out_name).write_text(page, encoding="utf-8")

    sb = sidebar(chapters, "index.html", meta)
    (out_dir / "index.html").write_text(
        render_index(chapters, meta, sb), encoding="utf-8")

    # Copy only the images the book actually references.
    copied = 0
    for name in sorted(used_images):
        filename = img_map.get(name)
        if filename:
            shutil.copy2(IMAGES_SRC / filename, images_out / filename)
            copied += 1
    if (STATIC_SRC / "favicon.ico").exists():
        shutil.copy2(STATIC_SRC / "favicon.ico", static_out / "favicon.ico")

    print(f"Built {len(chapters)} pages + index into {out_dir}")
    print(f"Copied {copied} image(s).")
    if missing:
        print(f"\nWARNING: {len(missing)} referenced image(s) had no file in "
              f"{IMAGES_SRC.relative_to(ROOT)} (linked with a .png guess):")
        for name in sorted(missing):
            print(f"  ? _images/{name}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT})")
    args = ap.parse_args(argv)
    return build(args.out)


if __name__ == "__main__":
    raise SystemExit(main())
