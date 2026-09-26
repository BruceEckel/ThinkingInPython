"""Tests for tools/listing_links.py (prose mentions linked to listings).

A mention like `shape_table.py` in the prose becomes a link to that
listing in the site and the EPUB, with no change to the Markdown. The
rewrite runs at build time and nothing in the built page looks wrong
when it goes bad: a mention that should link stays plain code, or a
link points at a block that carries no id. So the pieces are pinned
here, and one end-to-end assembly through build_epub.book_markdown().
"""
from pathlib import Path

from tools.build_epub import book_markdown, hang_listings, listing_html
from tools.build_site import (
    STATIC_FILES,
    STATIC_SRC,
    TEMPLATE,
    Chapter,
    render_css,
    render_index,
)
from tools.listing_links import (
    epub_href,
    fence_ids,
    link_line,
    link_mentions,
    listing_id,
    listing_index,
    site_href,
    site_rewrite,
)
from tools.markdown import Document

# ── ids ──────────────────────────────────────────────────────────────────────

def test_listing_id_keeps_the_period_and_replaces_the_slash() -> None:
    assert listing_id("registry.py") == "listing-registry.py"
    assert listing_id("mouse/MouseAction.py") == "listing-mouse-MouseAction.py"


# ── the index of names ───────────────────────────────────────────────────────

def docs(**texts: str) -> list[tuple[str, Document]]:
    return [(stem, Document.from_text(text)) for stem, text in texts.items()]


def test_index_keys_both_the_slug_and_its_basename() -> None:
    index = listing_index(docs(
        ch31="```python\n# mouse/MouseAction.py\nx = 1\n```\n"))
    target = ("ch31", "listing-mouse-MouseAction.py")
    assert index["mouse/MouseAction.py"] == target
    assert index["MouseAction.py"] == target


def test_index_drops_a_name_two_chapters_both_define() -> None:
    index = listing_index(docs(
        ch03="```python\n# import_once.py\nx = 1\n```\n",
        ch06="```python\n# import_once.py\nx = 2\n```\n"
             "```python\n# only_here.py\nx = 3\n```\n"))
    assert "import_once.py" not in index
    assert index["only_here.py"] == ("ch06", "listing-only_here.py")


def test_index_skips_a_block_naming_no_file() -> None:
    index = listing_index(docs(ch05="```python\nx = 1\n```\n"))
    assert index == {}


# ── one line ─────────────────────────────────────────────────────────────────

INDEX = {"registry.py": ("27_Patterns--Factory", "listing-registry.py"),
         "sketch.py": ("30_Patterns--Observer", "listing-sketch.py")}


def test_mention_becomes_a_classed_link_on_the_same_page() -> None:
    line = "The registry in `registry.py` does the same job."
    out = link_line(line, INDEX, site_href("27_Patterns--Factory"))
    assert out == ("The registry in [`registry.py`](#listing-registry.py)"
                   "{.listing-link} does the same job.")


def test_cross_chapter_mention_names_the_other_page() -> None:
    out = link_line("see `sketch.py`", INDEX, site_href("27_Patterns--Factory"))
    assert ("[`sketch.py`](30_Patterns--Observer.html#listing-sketch.py)"
            in out)


def test_epub_href_is_always_in_document() -> None:
    out = link_line("see `sketch.py`", INDEX, epub_href)
    assert "[`sketch.py`](#listing-sketch.py){.listing-link}" in out


def test_unknown_name_and_longer_code_span_stay_code() -> None:
    line = "`__init__.py` and `from registry import make` and `registry.pyc`"
    assert link_line(line, INDEX, epub_href) == line


def test_mention_inside_an_existing_link_is_left_alone() -> None:
    line = "[the `registry.py` listing](27_Patterns--Factory.md#self-registration)"
    assert link_line(line, INDEX, epub_href) == line


def test_possessive_after_the_span_survives() -> None:
    out = link_line("`registry.py`'s table", INDEX, epub_href)
    assert out == "[`registry.py`](#listing-registry.py){.listing-link}'s table"


# ── whole text ───────────────────────────────────────────────────────────────

def test_mentions_inside_a_fence_are_not_touched() -> None:
    text = ("prose `registry.py`\n\n```python\n# registry.py\n"
            "# see `registry.py`\n```\n")
    out = link_mentions(text, INDEX, epub_href)
    assert out.count("listing-link") == 1
    assert "# see `registry.py`\n" in out


# ── fences on the site ───────────────────────────────────────────────────────

def test_fence_gains_the_id_and_keeps_its_language() -> None:
    out = fence_ids("```python\n# registry.py\nx = 1\n```\n")
    assert out.startswith("``` {#listing-registry.py .python}\n")
    assert out.endswith("```\n")


def test_fence_naming_no_file_is_unchanged() -> None:
    text = "```text\noutput\n```\n"
    assert fence_ids(text) == text


def test_site_rewrite_links_and_ids_in_the_order_that_works() -> None:
    text = "```python\n# registry.py\nx = 1\n```\n\nprose `registry.py`\n"
    out = site_rewrite(text, INDEX, "27_Patterns--Factory")
    assert "[`registry.py`](#listing-registry.py){.listing-link}" in out
    assert "``` {#listing-registry.py .python}" in out
    # The other order changes the opener first. The parser's FENCE
    # regex then reads the closing fence as an opener, so every prose
    # line after a listing counts as code and stays unlinked.
    assert "listing-link" not in link_mentions(
        fence_ids(text), INDEX, site_href("27_Patterns--Factory"))


# ── the site's hover previews ────────────────────────────────────────────────

def test_preview_script_is_shipped_and_linked_from_the_template() -> None:
    # build_site copies STATIC_FILES beside the pages and the template
    # loads the script and its stylesheet through the preview-js and
    # preview-css variables; a missing file would fail the copy, a
    # missing variable would load nothing.
    assert "link-preview.js" in STATIC_FILES
    assert "link-preview.css" in STATIC_FILES
    for name in STATIC_FILES:
        assert (STATIC_SRC / name).is_file(), name
    template = TEMPLATE.read_text(encoding="utf-8")
    assert "$preview-js$" in template
    assert "$preview-css$" in template
    assert ".listing-link" in template
    assert ".listing-mode" not in template  # the switch was removed


def test_contents_page_loads_the_preview_too(tmp_path: Path) -> None:
    # The contents page is written by render_index(), not the template,
    # so it names the two files itself. The stylesheet's headings read
    # --heading-font, which both pages must set.
    index = render_index(chapters_in(tmp_path, {"14_Decorators": "# D\n"}))
    assert '<script src="link-preview.js?v=' in index
    assert '<link rel="stylesheet" href="link-preview.css?v=' in index
    assert "--heading-font:" in render_css()
    assert "--heading-font:" in TEMPLATE.read_text(encoding="utf-8")


def test_contents_page_sets_the_appendices_apart(tmp_path: Path) -> None:
    # build_site.PARTS gives the appendices a divider with no "Part N".
    index = render_index(chapters_in(tmp_path, {
        "44_Effects--Management": "# M\n",
        "A_Extras": "# E\n",
    }))
    assert '<li class="toc-part">Part V &middot; Effects</li>' in index
    assert '<li class="toc-part">Appendices</li>' in index
    assert (index.index("Part V &middot;")
            < index.index(">Appendices<")
            < index.index("A_Extras.html"))


def test_preview_script_and_template_agree_on_class_names() -> None:
    # The script finds the page's parts, and styles its own panel, by
    # class name. A class renamed on one side leaves the panel unstyled
    # or previews the navigation links. `tip preview-check` would
    # notice, but it needs node and no gate runs it.
    script = (STATIC_SRC / "link-preview.js").read_text(encoding="utf-8")
    styles = (STATIC_SRC / "link-preview.css").read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    for name in ("link-preview", "link-preview-title", "link-preview-more",
                 "link-preview-go"):
        assert name in script, name
        assert f".{name}" in styles, name
    for name in ("chapter-toc", "chapter-nav", "chapter-label",
                 "chapter-ornament", "page"):
        assert name in script, name
        assert f".{name}" in template or f'class="{name}"' in template, name


# ── the EPUB's <pre> ─────────────────────────────────────────────────────────

def test_listing_html_carries_the_id_only_when_given() -> None:
    assert listing_html(["x = 1"]).startswith("<pre>")
    assert listing_html(["x = 1"], id="listing-a.py").startswith(
        '<pre id="listing-a.py">')


def test_hang_listings_ids_slugged_blocks_unless_told_not_to() -> None:
    text = "```python\n# a.py\nx = 1\n```\n"
    assert '<pre id="listing-a.py">' in hang_listings(text)
    assert "<pre>" in hang_listings(text, ids=False)


# ── end to end through the EPUB assembly ─────────────────────────────────────

def chapters_in(tmp_path: Path, files: dict[str, str]) -> list[Chapter]:
    out: list[Chapter] = []
    for stem, text in files.items():
        md = tmp_path / f"{stem}.md"
        md.write_text(text, encoding="utf-8")
        number = stem.split("_", 1)[0]
        out.append(Chapter(md, f"{stem}.html", number, stem,
                           f"Chapter {number}"))
    return out


def test_book_markdown_links_a_mention_across_chapters(
        tmp_path: Path) -> None:
    chapters = chapters_in(tmp_path, {
        "27_Factory": "# Factory\n\n```python\n# registry.py\nx = 1\n```\n",
        "37_Refactoring": "# Refactoring\n\nAs `registry.py` does.\n",
    })
    text = book_markdown(chapters, set(), set())
    assert '<pre id="listing-registry.py">' in text
    assert "As [`registry.py`](#listing-registry.py){.listing-link} does." in text


def test_book_markdown_can_leave_mentions_alone(tmp_path: Path) -> None:
    chapters = chapters_in(tmp_path, {
        "27_Factory": "# Factory\n\n```python\n# registry.py\nx = 1\n```\n"
                      "\nAs `registry.py` does.\n",
    })
    text = book_markdown(chapters, set(), set(), listing_links_on=False)
    assert "listing-link" not in text
    assert 'id="listing-' not in text
    # The PDF path: no ids are written, so no links may point at them.
    text = book_markdown(chapters, set(), set(), hang_code=False)
    assert "listing-link" not in text
