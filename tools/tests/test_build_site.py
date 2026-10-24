"""Tests for tools/build_site.py's Solutions link rewrite and pages.

A chapter links its Solutions folder with a relative path so GitHub shows
a working link. The EPUB and PDF carry no Solutions pages, so
load_chapter() rewrites the link to the folder's GitHub `tree` URL (and
a link to the README.md in it to the `blob` URL). The site renders each
Solutions file as a page beside the chapter's, and links that instead.
"""
from pathlib import Path

import pytest

from tools.build_epub import Ids, relink
from tools.build_site import (
    BOOK_DESCRIPTION,
    DESCRIPTION_LIMIT,
    SOLUTIONS_BLOB_URL,
    SOLUTIONS_TREE_URL,
    link_solutions,
    load_chapter,
    load_solutions,
    page_description,
    rewrite_md_links,
    search_sources,
    solutions_page_name,
)
from tools.search_index import clean, split_sections

STEM = "05_Foundations--Demo"
NAME = f"{STEM}.md"
SENTENCE = ("This chapter's [solutions](../Solutions/{target}) give "
            "a hint, usually the shape of the code, and a full answer "
            "for each exercise.")
URL = f"{SOLUTIONS_TREE_URL}/{STEM}"
FILE_URL = f"{SOLUTIONS_BLOB_URL}/{STEM}/README.md"


def test_folder_link_becomes_the_github_tree_url() -> None:
    body = "## Exercises\n\n" + SENTENCE.format(target=f"{STEM}/") + "\n"
    assert f"[solutions]({URL}) give" in link_solutions(body)
    assert "../Solutions/" not in link_solutions(body)


def test_readme_link_becomes_the_github_blob_url() -> None:
    body = SENTENCE.format(target=f"{STEM}/README.md") + "\n"
    assert f"[solutions]({FILE_URL}) give" in link_solutions(body)


def test_anchor_survives() -> None:
    body = f"See [it](../Solutions/{STEM}/README.md#2-second) now.\n"
    assert link_solutions(body) == f"See [it]({FILE_URL}#2-second) now.\n"
    body = f"See [it](../Solutions/{STEM}/#2-second) now.\n"
    assert link_solutions(body) == f"See [it]({URL}#2-second) now.\n"


def test_link_inside_a_fence_is_left_alone() -> None:
    body = f"```text\n[x](../Solutions/{STEM}/)\n```\n"
    assert link_solutions(body) == body


def test_body_without_the_link_is_unchanged() -> None:
    body = "# Demo\n\nSee [other](06_Foundations--Other.md).\n"
    assert link_solutions(body) == body


def test_load_chapter_rewrites_the_link(tmp_path: Path) -> None:
    md = tmp_path / NAME
    md.write_text("# Demo\n\n## Exercises\n\n"
                  + SENTENCE.format(target=f"{STEM}/") + "\n\n1. First\n",
                  encoding="utf-8")
    _, body = load_chapter(md)
    assert f"[solutions]({URL})" in body
    assert "../Solutions/" not in body


def test_site_form_links_the_solutions_page() -> None:
    page = solutions_page_name(STEM)
    assert page == f"{STEM}.solutions.html"
    body = SENTENCE.format(target=f"{STEM}/") + "\n"
    assert f"[solutions]({page}) give" in link_solutions(body, site=True)
    body = f"See [it](../Solutions/{STEM}/README.md#2-second) now.\n"
    assert link_solutions(body, site=True) == (
        f"See [it]({page}#2-second) now.\n")


def test_load_solutions_takes_the_title_and_relinks_chapters(
        tmp_path: Path) -> None:
    folder = tmp_path / "Solutions" / STEM
    folder.mkdir(parents=True)
    md = folder / "README.md"
    md.write_text("# Demo: Solutions\n\n## 1. First\n\n"
                  f"> See [here](../../Chapters/{NAME}#x).\n\n"
                  "```text\n](../../Chapters/kept.md)\n```\n",
                  encoding="utf-8")
    title, body = load_solutions(md)
    assert title == "Demo: Solutions"
    assert body.startswith("## 1. First")
    assert f"[here]({NAME}#x)" in body
    assert "](../../Chapters/kept.md)" in body
    assert rewrite_md_links(f"[here]({NAME}#x)") == f"[here]({STEM}.html#x)"


def test_load_solutions_links_a_sibling_solutions_page(
        tmp_path: Path) -> None:
    folder = tmp_path / "Solutions" / STEM
    folder.mkdir(parents=True)
    md = folder / "README.md"
    other = "04_Foundations--Other"
    md.write_text("# Demo: Solutions\n\n## 1. First\n\n"
                  f"See [the pool](../{other}/README.md#a-pool) and "
                  f"[that file](../{other}/README.md).\n\n"
                  f"```text\n](../{other}/README.md#a-pool)\n```\n",
                  encoding="utf-8")
    _, body = load_solutions(md)
    page = solutions_page_name(other)
    assert f"[the pool]({page}#a-pool)" in body
    assert f"[that file]({page})" in body
    assert f"](../{other}/README.md#a-pool)" in body
    assert rewrite_md_links(f"[x]({page}#a-pool)") == f"[x]({page}#a-pool)"


def test_url_survives_rewrite_md_links() -> None:
    text = f"[solutions]({URL}#x)"
    assert rewrite_md_links(text) == text
    text = f"[solutions]({FILE_URL}#x)"
    assert rewrite_md_links(text) == text


def test_url_survives_the_epub_relink() -> None:
    for url in (URL, FILE_URL):
        text = f"[solutions]({url})"
        unresolved: set[str] = set()
        ids = Ids(prefixes={}, known=set(), aliases={})
        assert relink(text, "ch05", ids, unresolved) == text
        assert unresolved == set()


def test_solutions_pages_join_the_search_index(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from tools import build_site
    from tools.build_site import Chapter
    monkeypatch.setattr(build_site, "solutions_file",
                        lambda md: tmp_path / "Solutions" / STEM / "README.md")
    chapters_dir = tmp_path / "Chapters"
    chapters_dir.mkdir()
    md = chapters_dir / NAME
    md.write_text("# Demo\n\nText.\n", encoding="utf-8")
    folder = tmp_path / "Solutions" / STEM
    folder.mkdir(parents=True)
    sol = folder / "README.md"
    sol.write_text("# Demo: Solutions\n\n## 1. First\n\n> Ask.\n\n"
                   "<details>\n<summary>Where to look</summary>\n\n"
                   "Look at `thing()`.\n\n</details>\n", encoding="utf-8")
    ch = Chapter(md, f"{STEM}.html", "05", "Demo", "Chapter 5")
    sources = search_sources([ch])
    assert [s.url for s in sources] == [f"{STEM}.html",
                                        f"{STEM}.solutions.html"]
    assert sources[1].label == "Solutions 5"
    assert sources[1].title == "Demo: Solutions"
    [record] = [s for s in split_sections(sources[1]) if s.anchor]
    assert record.heading == "First"  # the list mark is stripped
    assert "Where to look" not in record.text
    assert "thing()" in record.text


def test_clean_drops_only_the_step_labels() -> None:
    assert clean(["<summary>Solution</summary>", "A Solution here."]) == (
        "A Solution here.")


def test_description_is_the_epigraph_as_plain_text() -> None:
    body = ("> A *Factory* puts `make()`\n> in [one place](x.md).\n\n"
            "Prose.\n")
    assert page_description(body) == "A Factory puts make() in one place."


def test_description_without_an_epigraph_is_the_first_paragraph() -> None:
    body = ("![fig](_images/a.svg)\n\n- a list\n\n"
            "*Observer* calls `__init__()`.\n\nMore.\n")
    assert page_description(body) == "Observer calls __init__()."


def test_description_stops_at_the_first_section() -> None:
    assert page_description("## Start\n\nProse.\n") == BOOK_DESCRIPTION


def test_long_description_is_cut_at_a_sentence() -> None:
    first = "Short sentence here."
    assert page_description(f"{first} {'word ' * 60}end.\n") == first
    assert len(page_description("word " * 60)) <= DESCRIPTION_LIMIT + 1
