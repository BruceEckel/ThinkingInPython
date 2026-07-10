#!/usr/bin/env python3
"""Render the book's Markdown into a static site, styled like OOPology.

Pandoc converts each chapter through `template.html`: a single readable column
on a warm "paper" background, a small fixed "Contents" link to the index, a
chapter label and title rule, and previous/next navigation. There is no
persistent sidebar. The index page is the table of contents.

This adapts the OOPology build to this book: the chapter title comes from the
first `#` heading (not YAML front matter), images referenced as `_images/<name>`
are resolved against `resources/images`, and intra-book `.md` links are
rewritten to `.html` so cross-references resolve in the site.

Usage:
    python tools/build_site.py            # build into build/site/
    python tools/build_site.py -o DIR     # build somewhere else
    python tools/build_site.py --chapter-toc   # add a per-chapter TOC

Set CHAPTER_TOC below (or pass --chapter-toc / --no-chapter-toc) to give each
chapter page its own table of contents listing that chapter's sections. The
floating "Contents" link to the index is unaffected.
"""

import argparse
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tools_config import BUILD_SITE_DIR as DEFAULT_OUT
from tools_config import CHAPTERS_DIR, ROOT

IMAGES_SRC = ROOT / "resources" / "images"
STATIC_SRC = ROOT / "resources" / "static"
TEMPLATE = ROOT / "template.html"

# Experimental: give each chapter page its own table of contents (its own
# sections). Flip this default, or override per-build with --chapter-toc /
# --no-chapter-toc. CHAPTER_TOC_DEPTH controls how deep the list goes
# (2 = top-level "##" sections only; 3 also includes "###" subsections).
CHAPTER_TOC = True
CHAPTER_TOC_DEPTH = 2

FRONT_STEM = "00_Front"
BOOK_TITLE = "Thinking in Python"
BOOK_SUBTITLE = "Insights, Idioms and Patterns"
BOOK_AUTHOR = "Bruce Eckel"
REPO_URL = "https://github.com/BruceEckel/ThinkingInPython"
HEADING_FONT = "Lexend Deca"
HEADING_FONT_GOOGLE = "Lexend+Deca:wght@400;600;700"
LICENSE_URL = "https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en"
COPYRIGHT = (f"© 2026 {BOOK_AUTHOR}. "
             f'<a href="{LICENSE_URL}" target="_blank" '
             f'rel="noopener">Licensed CC BY-NC-ND 4.0</a>.<br>'
             "Freely readable online. No reproduction without permission.")

IMG_REF = re.compile(r"(!\[[^\]]*\]\()_images/([^)\s]+)(\))")
MD_LINK = re.compile(r"(\]\()([\w./-]+)\.md(#[\w-]+)?(\))")
ATX = re.compile(r"^#\s+(.*?)\s*#*\s*$")


@dataclass
class Chapter:
    md: Path
    out_name: str   # e.g. "11_The_Singleton.html"
    number: str     # the 2-digit filename prefix, e.g. "11"
    title: str      # human title from the first heading
    label: str      # "Chapter 11", or "Front Matter"


# --------------------------------------------------------------------------- #
# Discovery and metadata
# --------------------------------------------------------------------------- #
def derive_label(stem: str) -> str:
    return re.sub(r"^\d+_", "", stem).replace("_", " ")


def load_chapter(md: Path) -> tuple[str, str]:
    """Return (title, body). Strips 00_Front YAML and the leading `#` heading."""
    text = md.read_text(encoding="utf-8")
    if md.stem == FRONT_STEM:
        text = re.sub(r"\A---.*?(?:\n\.\.\.|\n---)\s*\n", "", text, count=1,
                      flags=re.DOTALL)
        return "Front Matter", text.lstrip("\n")
    title = derive_label(md.stem)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        m = ATX.match(line)
        if m:
            title = m.group(1)
            del lines[i]
            break
        break  # first real content is not a heading; leave body as-is
    return title, "\n".join(lines).lstrip("\n")


def discover() -> list[Chapter]:
    chapters: list[Chapter] = []
    for md in sorted(CHAPTERS_DIR.glob("*.md")):
        title, _ = load_chapter(md)
        number = md.stem.split("_", 1)[0]
        # A numeric prefix is a chapter; a letter prefix (e.g. A_, B_) is an
        # appendix, which sorts after the numbered chapters.
        if number == "00":
            label = "Front Matter"
        elif number.isdigit():
            label = f"Chapter {int(number)}"
        else:
            label = f"Appendix {number}"
        chapters.append(Chapter(md, f"{md.stem}.html", number, title, label))
    return chapters


# --------------------------------------------------------------------------- #
# Markdown rewriting (images and cross-references)
# --------------------------------------------------------------------------- #
def build_image_map() -> dict[str, str]:
    out: dict[str, str] = {}
    if IMAGES_SRC.is_dir():
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
            filename = f"{name}.png"
        return f"{m.group(1)}images/{filename}{m.group(3)}"

    return IMG_REF.sub(repl, text)


def rewrite_md_links(text: str) -> str:
    return MD_LINK.sub(lambda m: f"{m.group(1)}{m.group(2)}.html"
                                 f"{m.group(3) or ''}{m.group(4)}", text)


# --------------------------------------------------------------------------- #
# Pandoc
# --------------------------------------------------------------------------- #
def check_pandoc() -> None:
    if shutil.which("pandoc") is None:
        sys.exit("error: pandoc not found on PATH. "
                 "Install it: https://pandoc.org/installing.html")


def render_chapter(body: str, ch: Chapter,
                   prev: Chapter | None, nxt: Chapter | None,
                   chapter_toc: bool = False) -> str:
    variables = [
        f"--variable=title:{ch.title}",
        f"--variable=chapter-label:{ch.label}",
        f"--variable=book-title:{BOOK_TITLE}",
        f"--variable=heading-font:{HEADING_FONT}",
        f"--variable=heading-font-google:{HEADING_FONT_GOOGLE}",
    ]
    if prev is not None:
        variables += [f"--variable=prev-url:{prev.out_name}",
                      f"--variable=prev-title:{prev.title}"]
    if nxt is not None:
        variables += [f"--variable=next-url:{nxt.out_name}",
                      f"--variable=next-title:{nxt.title}"]
    toc_opts = ["--toc", f"--toc-depth={CHAPTER_TOC_DEPTH}"] if chapter_toc else []
    proc = subprocess.run(
        ["pandoc", "--template", str(TEMPLATE), "--from", "markdown+smart",
         "--highlight-style", "pygments", *toc_opts, *variables],
        input=body, capture_output=True, text=True, encoding="utf-8",
    )
    if proc.returncode != 0:
        sys.exit(f"pandoc failed on {ch.md.name}:\n{proc.stderr}")
    return proc.stdout


# --------------------------------------------------------------------------- #
# Index page and shared CSS (the table of contents)
# --------------------------------------------------------------------------- #
# A Part heading is emitted before the chapter whose number starts it.
# Introduction (01) stands alone above Part I.
PARTS = {
    "02": ("I", "Foundations"),
    "11": ("II", "Techniques"),
    "20": ("III", "Patterns"),
    "40": ("IV", "Effects"),
}


def render_index(chapters: list[Chapter]) -> str:
    items: list[str] = []
    for ch in chapters:
        part = PARTS.get(ch.number)
        if part is not None:
            roman, title = part
            items.append(
                '    <li class="toc-part">'
                f'Part {roman} &middot; {title}</li>')
        items.append(
            f'    <li><span class="toc-num">{ch.number}</span>'
            f'<a href="{ch.out_name}">{ch.title}</a></li>')
    rows = "\n".join(items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{BOOK_TITLE}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family={HEADING_FONT_GOOGLE}&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&family=Cormorant+SC:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="page">
    <p class="book-author">{BOOK_AUTHOR}</p>
    <h1 class="book-title">{BOOK_TITLE}</h1>
    <p class="book-subtitle">{BOOK_SUBTITLE}</p>
    <div class="title-rule"></div>
    <ul class="toc-list">
{rows}
    </ul>
    <p class="copyright">{COPYRIGHT}</p>
    <p class="repo-link"><a href="{REPO_URL}" target="_blank" rel="noopener">Book Examples & Exercise Solutions on GitHub</a></p>
  </div>
</body>
</html>
"""


def render_css() -> str:
    return f""":root {{
  --ink: #1a1612; --paper: #f5f0e8; --muted: #7a6e62;
  --accent: #8b1a1a; --rule: #c8bfb0; --max-width: 680px;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ font-size: 18px; }}
body {{ background: var(--paper); color: var(--ink);
  font-family: Georgia, serif; line-height: 1.75; padding: 0 1.5rem; }}
.page {{ max-width: var(--max-width); margin: 0 auto; padding: 4rem 0 6rem; }}
.book-title {{ font-family: '{HEADING_FONT}', sans-serif; font-size: 3.5rem;
  font-weight: 600; line-height: 1.1; margin-bottom: 0.5rem; }}
.book-author {{ font-family: 'Cormorant SC', serif; font-size: 0.85rem;
  letter-spacing: 0.15em; color: var(--muted); margin-bottom: 0.5rem; }}
.book-subtitle {{ font-family: 'Cormorant Garamond', serif; font-style: italic;
  font-size: 1.1rem; color: var(--muted); margin-bottom: 0.25rem; }}
.title-rule {{ width: 3rem; height: 1px; background: var(--accent);
  margin: 1.5rem 0 2.5rem; }}
.toc-list {{ list-style: none; margin-top: 2rem; }}
.toc-list li {{ display: flex; align-items: baseline;
  padding: 0.6rem 0; border-bottom: 1px solid var(--rule); }}
.toc-list li:first-child {{ border-top: 1px solid var(--rule); }}
.toc-num {{ font-family: 'Cormorant SC', serif; font-size: 0.7rem;
  letter-spacing: 0.1em; color: var(--muted); min-width: 2.5rem; }}
.toc-list a {{ font-family: 'Cormorant Garamond', serif; font-size: 1.15rem;
  color: var(--ink); text-decoration: none; flex: 1; }}
.toc-list a:hover {{ color: var(--accent); }}
.toc-part {{ display: block; border-bottom: none; margin-top: 1.5rem;
  padding: 0.4rem 0; font-family: 'Cormorant SC', serif; font-size: 1.7rem;
  letter-spacing: 0.15em; color: var(--accent); }}
.toc-list li.toc-part:first-child {{ border-top: none; }}
.copyright {{ margin-top: 5rem; font-size: 0.78rem; color: var(--muted);
  font-family: 'Cormorant SC', serif; letter-spacing: 0.05em; }}
.copyright a {{ color: var(--muted); text-decoration: none; }}
.copyright a:hover {{ color: var(--accent); }}
.repo-link {{ margin-top: 1.5rem; }}
.repo-link a {{ font-family: 'Cormorant Garamond', serif; font-size: 1.05rem;
  color: var(--ink); text-decoration: none; }}
.repo-link a:hover {{ color: var(--accent); }}
"""


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def build(out_dir: Path, chapter_toc: bool = CHAPTER_TOC) -> int:
    check_pandoc()
    if not TEMPLATE.exists():
        sys.exit(f"error: template not found at {TEMPLATE}")
    chapters = discover()
    img_map = build_image_map()

    if out_dir.exists():
        shutil.rmtree(out_dir)
    images_out = out_dir / "images"
    images_out.mkdir(parents=True)

    used_images: set[str] = set()
    missing: set[str] = set()

    for i, ch in enumerate(chapters):
        prev = chapters[i - 1] if i > 0 else None
        nxt = chapters[i + 1] if i + 1 < len(chapters) else None
        _, body = load_chapter(ch.md)
        for m in IMG_REF.finditer(body):
            used_images.add(m.group(2))
        body = rewrite_images(body, img_map, missing)
        body = rewrite_md_links(body)
        page = render_chapter(body, ch, prev, nxt, chapter_toc)
        (out_dir / ch.out_name).write_text(page, encoding="utf-8")

    (out_dir / "index.html").write_text(render_index(chapters), encoding="utf-8")
    (out_dir / "style.css").write_text(render_css(), encoding="utf-8")

    copied = 0
    for name in sorted(used_images):
        filename = img_map.get(name)
        if filename:
            shutil.copy2(IMAGES_SRC / filename, images_out / filename)
            copied += 1
    if (STATIC_SRC / "favicon.ico").exists():
        shutil.copy2(STATIC_SRC / "favicon.ico", out_dir / "favicon.ico")

    print(f"Built {len(chapters)} pages + index into {out_dir}")
    print(f"Copied {copied} image(s).")
    if missing:
        print(f"\nWARNING: {len(missing)} referenced image(s) not found in "
              f"{IMAGES_SRC.relative_to(ROOT)}:")
        for name in sorted(missing):
            print(f"  ? _images/{name}")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT})")
    ap.add_argument("--chapter-toc", action=argparse.BooleanOptionalAction,
                    default=CHAPTER_TOC,
                    help="add a per-chapter table of contents to each page "
                         f"(default: {CHAPTER_TOC})")
    args = ap.parse_args(argv)
    return build(args.out, args.chapter_toc)


if __name__ == "__main__":
    raise SystemExit(main())
