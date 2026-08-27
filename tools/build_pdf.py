#!/usr/bin/env python3
"""Render the book's Markdown into a single PDF with pandoc and typst.

The assembly is build_epub.py's: every chapter concatenated into one
Markdown stream, every heading id namespaced by chapter (ch12-...), and
every `.md` link rewritten to an in-document anchor, so a link the
`anchors` gate accepts is a link this build resolves. See that module's
docstring for why the namespacing exists. The one difference is
`hang_code=False`: the EPUB rewrites listings into raw-HTML `<pre>`
blocks for its hanging indent, and pandoc's typst writer drops raw
HTML, so here the listings stay fenced code blocks. Nothing is lost by
that: ruff caps listing lines at 70 characters, which fits the text
column, and typst highlights fenced Python natively.

Typst is the PDF engine rather than a LaTeX: it is a single ~40 MB
binary (`winget install Typst.Typst`), compiles the whole book in
seconds, ships its own fonts, and renders the book's SVG diagrams
directly, so no rasterization step is needed. Pandoc resolves each
diagram through --resource-path and hands it to typst itself.

The title block, table of contents (with page numbers), and per-part /
per-chapter page breaks come from pandoc's stock typst template plus
the preamble from `header_typst()`; chapter numbers live in the
heading text ("3. Containers"), so section numbering stays off. That
preamble also sets a running footer (chapter name, page number, and on
a release build the release stamp); see FOOTER_TYPST.

Usage:
    python tools/build_pdf.py               # build/pdf/ThinkingInPython.pdf
    python tools/build_pdf.py -o DIR        # build somewhere else
    python tools/build_pdf.py --keep-source # leave build/pdf/src/ in place

Requires `pandoc` and `typst` on PATH (`make tools-check-full`
verifies both).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import build_epub
import build_site
from tools_config import BUILD_PDF_DIR as DEFAULT_OUT
from tools_config import ROOT

PDF_NAME = "ThinkingInPython.pdf"
PDF_ENGINE = "typst"
TYPST_HINT = ("winget install Typst.Typst (Windows) / "
              "brew install typst (macOS) / "
              "https://github.com/typst/typst/releases")
PAPER = "us-letter"
# Parts and chapters are level 1, their sections level 2. Deep enough
# to navigate by, shallow enough that the contents stays a contents.
TOC_DEPTH = 2

# Every Part divider and chapter title is a level-1 heading, and each
# starts its own page. `weak: true` collapses a page break that lands
# on an already-fresh page, so a Part divider and the chapter right
# behind it cost one break, not an extra blank page.
PAGEBREAK_TYPST = """\
#show heading.where(level: 1): it => {
  pagebreak(weak: true)
  it
}
"""

# The running footer: chapter name left, release stamp centered, page
# number right, nothing on the title page. Setting `footer` explicitly
# replaces the bare centered number the template's page numbering
# would render, while the numbering setting itself stays on (see
# run_pandoc), since the outline reads the TOC's page numbers from it.
# The chapter name is the nearest level-1 heading at or before this
# page, which also labels the TOC pages "Contents" and the pages of a
# Part divider with that Part's name. `<<stamp>>` is replaced by
# `header_typst()`; for an unstamped build the center cell is empty.
FOOTER_TYPST = """\
#set page(footer: context {
  if here().page() > <<first>> {
    let past = query(heading.where(level: 1)).filter(
      h => h.location().page() <= here().page())
    let chapter = if past.len() > 0 { past.last().body } else { [] }
    set text(size: 8pt, fill: luma(30%))
    grid(
      columns: (1fr, auto, 1fr),
      align: (left, center, right),
      chapter,
      [<<stamp>>],
      counter(page).display("1"),
    )
  }
})
"""


# The cover, emitted from the preamble so it lands before the
# template's title page. Margins collapse to zero for a full-bleed
# page; the footer rule below skips page 1 anyway, and page
# numbering restarts so the title page stays page 1 for the TOC.
# `<<cover>>` is replaced by `header_typst()` with the SVG's
# absolute path, which typst accepts because run_pandoc widens the
# project root to the filesystem root.
COVER_TYPST = """\
#page(margin: 0pt, footer: none,
      image("<<cover>>", width: 100%, height: 100%))
#counter(page).update(0)
"""

# The letter-ratio rendering, so the full-bleed page crops
# nothing: vector SVG from drawn mode, or JPEG from art mode.
def cover_file() -> Path | None:
    for name in ("cover-letter.svg", "cover-letter.jpg"):
        path = ROOT / "resources" / "static" / name
        if path.exists():
            return path
    return None


def header_typst(release: str | None) -> str:
    """The typst preamble: cover, page breaks, and the footer."""
    stamp = build_epub.release_line(release) if release else ""
    cover = ""
    cover_path = cover_file()
    if cover_path is not None:
        # Typst reads "/..." as root-relative; run_pandoc sets the
        # root to this drive's top, so strip the anchor.
        rooted = "/" + cover_path.relative_to(
            cover_path.anchor).as_posix()
        cover = COVER_TYPST.replace("<<cover>>", rooted)
    # The footer stays off the title page: physical page 2 when
    # the cover is present, page 1 when it is not.
    footer = (FOOTER_TYPST
              .replace("<<stamp>>", stamp)
              .replace("<<first>>", "2" if cover else "1"))
    return cover + PAGEBREAK_TYPST + footer

# Inserted after the title block and before the outline, so the table
# of contents opens on its own page instead of running on from the
# title.
BEFORE_TYPST = "#pagebreak(weak: true)\n"


def check_typst() -> None:
    if shutil.which(PDF_ENGINE) is None:
        sys.exit(f"error: {PDF_ENGINE} not found on PATH. "
                 f"Install it: {TYPST_HINT}")


def run_pandoc(src: Path, meta: Path, header: Path, before: Path,
               pdf: Path) -> None:
    command = [
        "pandoc",
        "--from", "markdown+smart",
        "--pdf-engine", PDF_ENGINE,
        "--output", str(pdf),
        "--metadata-file", str(meta),
        "--resource-path", str(build_site.IMAGES_SRC),
        "--include-in-header", str(header),
        "--include-before-body", str(before),
        # Widen typst's project root to the drive so the cover's
        # root-relative path (see COVER_TYPST) resolves from
        # pandoc's temp compilation directory.
        "--pdf-engine-opt=--root",
        f"--pdf-engine-opt={Path(ROOT.anchor).as_posix()}",
        "--toc", f"--toc-depth={TOC_DEPTH}",
        # Page numbering stays on even though FOOTER_TYPST replaces
        # the footer it would render: the outline formats the TOC's
        # page numbers through it (the template defaults it to none).
        "--variable", f"papersize:{PAPER}",
        "--variable", "page-numbering:1",
        str(src),
    ]
    proc = subprocess.run(command, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        sys.exit(f"pandoc failed:\n{proc.stderr}")
    if proc.stderr.strip():
        print(proc.stderr.strip())


def build(out_dir: Path, keep_source: bool = False,
          release: str | None = None) -> int:
    build_site.check_pandoc()
    check_typst()
    chapters = build_site.discover()
    if not chapters:
        sys.exit("error: no chapters found in Chapters/")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    src_dir = out_dir / "src"
    src_dir.mkdir(parents=True)

    missing: set[str] = set()
    unresolved: set[str] = set()
    text = build_epub.book_markdown(chapters, missing, unresolved,
                                    hang_code=False)

    src = src_dir / "book.md"
    meta = src_dir / "metadata.yaml"
    header = src_dir / "header.typ"
    before = src_dir / "before.typ"
    src.write_text(text, encoding="utf-8")
    meta.write_text(build_epub.metadata_yaml(release), encoding="utf-8")
    header.write_text(header_typst(release), encoding="utf-8")
    before.write_text(BEFORE_TYPST, encoding="utf-8")

    pdf = out_dir / PDF_NAME
    run_pandoc(src, meta, header, before, pdf)

    size = pdf.stat().st_size / 1024
    print(f"Built {pdf.relative_to(ROOT)} "
          f"({len(chapters)} chapters, {size:.0f} KB).")

    if not keep_source:
        shutil.rmtree(src_dir)
    else:
        print(f"Kept the pandoc input in {src_dir.relative_to(ROOT)}.")

    status = 0
    if missing:
        print(f"\nWARNING: {len(missing)} referenced image(s) not found "
              f"in {build_site.IMAGES_SRC.relative_to(ROOT)}:")
        for name in sorted(missing):
            print(f"  ? _images/{name}")
        status = 1
    if unresolved:
        print(f"\nWARNING: {len(unresolved)} link(s) name no book "
              "chapter and stay unlinked in the PDF:")
        for target in sorted(unresolved):
            print(f"  ? {target}")
        status = 1
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT,
                    help=f"output directory (default: {DEFAULT_OUT})")
    ap.add_argument("--keep-source", action="store_true",
                    help="leave the generated pandoc input under <out>/src/")
    ap.add_argument("--release", metavar="VERSION",
                    help="stamp the title page with this release number "
                         "and today's date (used by `make release`)")
    args = ap.parse_args(argv)
    return build(args.out, args.keep_source, args.release)


if __name__ == "__main__":
    raise SystemExit(main())
