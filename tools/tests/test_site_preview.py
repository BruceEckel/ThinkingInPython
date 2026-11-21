"""Run the link-preview checker over one chapter and the index page.

On 2026-10-31 commit be65fba91 put one link per listing into the
section menu at the top left of each page. The preview checker
(`tools/site_preview_check.js`) filed each as a heading link, expected
a panel for it, and found none, so all 96 pages failed
`tip preview-check` and stopped `tip release`. Commit b1bb0a4f taught `kindOf()` the region, but nothing
ran the checker between releases. This test renders chapter 11 and its
Solutions page with the real site builder into a temp directory and runs
the checker over them, so a template or build change that adds links the
checker misclassifies fails in the tools tests.

On 2026-11-21 `tip release` failed again. The checker took the book
index's `ix-` locator spans (`<span id="ix-11-3"></span>`) for
authored listing anchors and reported 1,379 problems on
`book-index.html`, each "an authored anchor's panel holds no
listing". Commit 6819dc70 fixed `targetsAuthoredAnchor()`. The test
now renders the index page too. It matches the index against chapter
11 alone, as `rebuild_chapter()` does, so the test adds one page and
the index links point into chapter 11.

The test runs when `tools/` changed, like the rest of the suite,
and carries no `book` mark. The links it guards come from
`template.html` and `tools/build_site.py`, so a chapter edit alone
leaves it unaffected.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path
import pytest
from tools import book_index
from tools.build_site import (
    CHAPTER_TOC,
    INDEX_PAGE,
    build_image_map,
    discover,
    listing_targets,
    solutions_page_name,
    write_page,
    write_shared,
    write_solutions_page,
)
from tools.config import ROOT

JSDOM = ROOT / "build" / "node" / "node_modules" / "jsdom"
HREF = re.compile(r'href="([^"#]+\.html)(?:#[^"]*)?"')


def linked_pages(page: Path) -> set[str]:
    """The page names that `page` links to."""
    html = page.read_text(encoding="utf-8")
    return set(HREF.findall(html))


@pytest.mark.skipif(
    shutil.which("pandoc") is None
    or shutil.which("node") is None
    or not JSDOM.is_dir(),
    reason="needs pandoc, node, and jsdom under build/node/; the "
    "checker installs jsdom from the network on its first run "
    "(`tip preview-check`), and this test never does")
def test_chapter_pages_pass_the_preview_check(tmp_path: Path) -> None:
    chapters = discover()
    chapter = next(c for c in chapters if c.md.stem.startswith("11_"))
    img_map = build_image_map()
    targets = listing_targets(chapters)
    missing: set[str] = set()
    located = book_index.book_index([chapter])

    def render(name: str) -> None:
        if (tmp_path / name).exists():
            return
        for ch in chapters:
            if name == ch.out_name:
                write_page(ch, chapters, tmp_path, img_map, missing,
                           CHAPTER_TOC, targets,
                           located if ch is chapter else None)
                return
            if name == solutions_page_name(ch.md.stem):
                write_solutions_page(ch, chapters, tmp_path, img_map,
                                     missing, CHAPTER_TOC, targets)
                return

    tested = [chapter.out_name, solutions_page_name(chapter.md.stem)]
    for name in tested:
        render(name)
    for name in sorted(set().union(
            *(linked_pages(tmp_path / n) for n in tested))):
        render(name)
    write_shared(chapters, tmp_path, located)
    tested.append(INDEX_PAGE)

    # The checker keeps every page whose name starts with an argument.
    names = {p.name for p in tmp_path.glob("*.html")}
    assert {n for n in names if n.startswith(chapter.out_name)} <= {
        *tested}, "another page starts with the chapter's name"
    assert {n for n in names if n.startswith(INDEX_PAGE)} == {
        INDEX_PAGE}, "another page starts with the index page's name"

    index_html = (tmp_path / INDEX_PAGE).read_text(encoding="utf-8")
    assert re.search(r'href="[^"]*#ix-', index_html), (
        "the index page links no #ix- locator")
    chapter_html = (tmp_path / chapter.out_name).read_text(
        encoding="utf-8")
    assert '<span id="ix-' in chapter_html, (
        "chapter 11 carries no ix- locator span")

    result = subprocess.run(
        [str(shutil.which("node")),
         str(ROOT / "tools" / "site_preview_check.js"), *tested],
        cwd=ROOT, env={**os.environ, "PREVIEW_SITE": str(tmp_path)},
        capture_output=True, text=True, encoding="utf-8")
    report = f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert result.returncode == 0, report
    assert "Link previews OK" in result.stdout, report
