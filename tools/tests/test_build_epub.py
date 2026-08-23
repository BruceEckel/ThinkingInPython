"""Tests for tools/build_epub.py (the single-document EPUB assembly).

The EPUB merges 47 chapters into one document, where the book's anchors
stop being unique: 44 chapters end in `## Exercises`. Nothing in the
built file looks wrong when that goes bad, the link just opens the wrong
chapter, so the namespacing and relinking are covered here rather than
left to a reader to notice.
"""
import datetime
from pathlib import Path

from build_epub import (
    MAX_HANG_INDENT,
    Ids,
    book_markdown,
    chapter_heading,
    hang_css,
    hang_listings,
    heading_ids,
    listing_html,
    metadata_yaml,
    namespace_headings,
    outside_code,
    relink,
    release_line,
    title_anchor,
)
from build_site import Chapter
from tools_markdown import Document

# ── namespacing one chapter's headings ────────────────────────────────────────

def namespaced(text: str, prefix: str = "ch12") -> list[str]:
    doc = Document.from_text(text)
    lines = list(doc.lines)
    namespace_headings(lines, doc, prefix)
    return lines

def test_heading_gets_namespaced_id() -> None:
    assert namespaced("## Immutability\n")[0] == \
        "## Immutability {#ch12-immutability}"

def test_explicit_id_is_kept_and_namespaced() -> None:
    assert namespaced("## Naming Types {#the-type-statement}\n")[0] == \
        "## Naming Types {#ch12-the-type-statement}"

def test_backticks_dropped_from_the_id_but_kept_in_the_text() -> None:
    assert namespaced("### The `Self` Type\n")[0] == \
        "### The `Self` Type {#ch12-the-self-type}"

def test_repeated_heading_keeps_pandocs_suffix_inside_the_namespace() -> None:
    lines = namespaced("## Setup\n\ntext\n\n## Setup\n")
    assert lines[0] == "## Setup {#ch12-setup}"
    assert lines[4] == "## Setup {#ch12-setup-1}"

def test_a_comment_in_a_listing_is_not_a_heading() -> None:
    # Every book listing opens with a `# path/slug.py` comment, which is a
    # level-1 heading to anything that does not track fences.
    text = "## Real\n\n```python\n# trace.py\nx = 1\n```\n"
    lines = namespaced(text)
    assert lines[0] == "## Real {#ch12-real}"
    assert lines[3] == "# trace.py"

def test_returns_the_ids_it_assigned() -> None:
    doc = Document.from_text("## A\n\n### B\n")
    assert namespace_headings(list(doc.lines), doc, "ch07") == \
        {"ch07-a", "ch07-b"}

def test_heading_with_no_letters_gets_no_id() -> None:
    doc = Document.from_text("## 42\n")
    assert heading_ids(doc) == [(0, None)]

# ── rewriting links ───────────────────────────────────────────────────────────

BOOK = Ids(
    prefixes={"12_Data_Classes": "ch12", "24_Singleton": "ch24"},
    known={"ch12", "ch24", "ch12-immutability", "ch24-borg",
           "ch12-dynamic-binding-vs.-pattern-matching"},
    aliases={"ch24-singleton": "ch24"},
)

def rewritten(text: str, here: str = "ch12") -> str:
    unresolved: set[str] = set()
    return relink(text, here, BOOK, unresolved)

def test_same_document_anchor_is_namespaced() -> None:
    assert rewritten("see [x](#immutability)") == "see [x](#ch12-immutability)"

def test_cross_chapter_anchor_points_into_that_chapter() -> None:
    assert rewritten("[x](24_Singleton.md#borg)") == "[x](#ch24-borg)"

def test_whole_chapter_link_points_at_the_chapter() -> None:
    assert rewritten("[x](24_Singleton.md)") == "[x](#ch24)"

def test_anchor_may_contain_a_period() -> None:
    # Pandoc keeps a period in an auto id, and chapter 13 links to one.
    assert rewritten("[x](#dynamic-binding-vs.-pattern-matching)") == \
        "[x](#ch12-dynamic-binding-vs.-pattern-matching)"

def test_external_link_is_untouched() -> None:
    url = "[x](https://example.com/a.md#b)"
    assert rewritten(url) == url

def test_link_inside_inline_code_is_untouched() -> None:
    assert rewritten("write `[x](#immutability)` here") == \
        "write `[x](#immutability)` here"

def test_unknown_chapter_is_reported_and_left_alone() -> None:
    unresolved: set[str] = set()
    text = "[x](99_Nope.md#thing)"
    assert relink(text, "ch12", BOOK, unresolved) == text
    assert unresolved == {"99_Nope.md#thing"}

def test_unknown_anchor_is_reported_and_left_alone() -> None:
    unresolved: set[str] = set()
    text = "[x](#no-such-section)"
    assert relink(text, "ch12", BOOK, unresolved) == text
    assert unresolved == {"#no-such-section"}

def test_alias_sends_a_title_anchor_to_the_chapter_root() -> None:
    assert rewritten("[x](24_Singleton.md#singleton)") == "[x](#ch24)"

def test_outside_code_leaves_code_spans_alone() -> None:
    assert outside_code("a `b` c", str.upper) == "A `b` C"

# ── titles ────────────────────────────────────────────────────────────────────

def test_title_anchor_matches_pandocs_id_for_the_heading() -> None:
    assert title_anchor("Data Classes as Types") == "data-classes-as-types"

def test_title_anchor_prefers_an_explicit_id() -> None:
    assert title_anchor("Generators {#gen}") == "gen"

def test_chapter_heading_is_numbered() -> None:
    ch = Chapter(Path("12_Data.md"), "12_Data.html", "12", "Data Classes",
                 "Chapter 12")
    assert chapter_heading(ch) == "12. Data Classes"

def test_appendix_heading_is_lettered() -> None:
    ch = Chapter(Path("A_Extras.md"), "A_Extras.html", "A", "Extras",
                 "Appendix A")
    assert chapter_heading(ch) == "Appendix A. Extras"

# ── the whole assembly ────────────────────────────────────────────────────────

def chapters_in(tmp_path: Path, files: dict[str, str]) -> list[Chapter]:
    """Write `files` as chapters and describe them the way discover() does."""
    out: list[Chapter] = []
    for stem, text in files.items():
        md = tmp_path / f"{stem}.md"
        md.write_text(text, encoding="utf-8")
        number = stem.split("_", 1)[0]
        title = text.split("\n", 1)[0].lstrip("# ").strip()
        out.append(Chapter(md, f"{stem}.html", number, title,
                           f"Chapter {number}"))
    return out

def test_colliding_headings_land_in_separate_namespaces(
        tmp_path: Path) -> None:
    chapters = chapters_in(tmp_path, {
        "03_Containers": "# Containers\n\n## Immutability\n\ntext\n",
        "12_Data": "# Data\n\n## Immutability\n\n"
                   "[back](03_Containers.md#immutability)\n",
    })
    missing: set[str] = set()
    unresolved: set[str] = set()
    text = book_markdown(chapters, missing, unresolved)
    assert "## Immutability {#ch03-immutability}" in text
    assert "## Immutability {#ch12-immutability}" in text
    # The link resolves to chapter 3, not to whichever came first.
    assert "[back](#ch03-immutability)" in text
    assert not unresolved

def test_chapter_title_becomes_a_numbered_level_one_heading(
        tmp_path: Path) -> None:
    chapters = chapters_in(tmp_path, {"07_Classes": "# Classes\n\nbody\n"})
    text = book_markdown(chapters, set(), set())
    assert text.startswith("# 7. Classes {#ch07}")
    assert "# Classes\n" not in text  # the original heading is not repeated

def test_part_divider_is_emitted_before_its_chapter(tmp_path: Path) -> None:
    # build_site.PARTS starts Part I at chapter 02.
    chapters = chapters_in(tmp_path, {
        "01_Introduction": "# Introduction\n\nbody\n",
        "02_Tour": "# Tour\n\nbody\n",
    })
    text = book_markdown(chapters, set(), set())
    assert text.index("# Part I") < text.index("# 2. Tour")
    assert text.index("# 1. Introduction") < text.index("# Part I")

def test_hang_code_false_keeps_listings_fenced(tmp_path: Path) -> None:
    # build_pdf.py passes hang_code=False: pandoc's typst writer drops
    # raw HTML, so the EPUB's <pre> rewrite would erase every listing
    # from the PDF.
    chapters = chapters_in(tmp_path, {
        "05_F": "# F\n\n```python\n# t.py\nx = 1\n```\n"})
    text = book_markdown(chapters, set(), set(), hang_code=False)
    assert "```python" in text
    assert "<pre>" not in text

def test_missing_image_is_reported(tmp_path: Path) -> None:
    chapters = chapters_in(
        tmp_path, {"05_F": "# F\n\n![d](_images/no_such_image)\n"})
    missing: set[str] = set()
    book_markdown(chapters, missing, set())
    assert missing == {"no_such_image"}

# ── the release stamp on the title page ───────────────────────────────────────

def test_release_line_spells_out_the_date() -> None:
    # No zero-padded day: "August 3", not "August 03".
    assert release_line("1.0", datetime.date(2026, 8, 3)) == \
        "Release 1.0 · August 3, 2026"

def test_release_stamp_becomes_the_metadata_date() -> None:
    # The middle dot is JSON-escaped in the YAML (a backslash-u
    # code, as the copyright sign in rights already is), so assert
    # around it, not through it.
    assert "Release 1.0" in metadata_yaml("1.0")

def test_without_a_release_the_date_stays_the_copyright_year() -> None:
    # An ad-hoc `make epub`/`make pdf` must not masquerade as a
    # numbered release.
    assert 'date: "2026"' in metadata_yaml()
    assert "Release" not in metadata_yaml()

# ── hanging indent for wrapped code lines ─────────────────────────────────────

def test_each_line_becomes_its_own_block() -> None:
    # The hanging indent needs a block box per line; a `<pre>` full of
    # newlines is one block, and text-indent would only reach line one.
    html = listing_html(["a = 1", "b = 2"])
    assert html == ('<pre><span class="h0">a = 1</span>'
                    '<span class="h0">b = 2</span></pre>')

def test_line_carries_its_own_indent_as_its_class() -> None:
    # h8 hangs past column 8, so the continuation of a line indented
    # eight columns does not begin to the left of the code it continues.
    html = listing_html(["def f():", "    if x:", "        pass"])
    assert 'class="h0">def f():' in html
    assert 'class="h4">    if x:' in html
    assert 'class="h8">        pass' in html

def test_indent_deeper_than_the_last_rule_is_clamped() -> None:
    deep = " " * (MAX_HANG_INDENT + 6) + "x"
    assert f'class="h{MAX_HANG_INDENT}"' in listing_html([deep])

def test_every_class_a_listing_can_emit_has_a_rule() -> None:
    css = hang_css()
    for column in range(MAX_HANG_INDENT + 1):
        assert f"pre .h{column} {{" in css

def test_blank_line_keeps_its_height() -> None:
    # An empty block box collapses to nothing, closing the gap the
    # author put in the listing.
    assert "&#160;" in listing_html(["a = 1", "", "b = 2"])

def test_markup_characters_are_escaped() -> None:
    html = listing_html(["if a < b & c:"])
    assert "a &lt; b &amp; c" in html

def test_no_newline_between_spans() -> None:
    # Under pre-wrap a newline between two block spans is a second
    # line break, double-spacing the listing.
    assert "\n" not in listing_html(["a = 1", "b = 2"])

def test_prose_around_a_fence_is_untouched() -> None:
    out = hang_listings("Before.\n\n```python\nx = 1\n```\n\nAfter.\n")
    assert out.startswith("Before.\n\n<pre>")
    assert out.endswith("</pre>\n\nAfter.\n")
    assert "```" not in out

def test_a_text_fence_is_converted_too() -> None:
    # Program output wraps the same way code does.
    assert "<pre>" in hang_listings("```text\nsome output\n```\n")

def test_text_with_no_fence_is_returned_unchanged() -> None:
    assert hang_listings("Just prose.\n") == "Just prose.\n"
