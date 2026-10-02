"""Tests for tools/build_site.py's Solutions link rewrite.

A chapter links its Solutions folder with a relative path so GitHub shows
a working link. The built site, EPUB, and PDF carry no Solutions pages,
so load_chapter() rewrites the link to the folder's GitHub `tree` URL
(and a link to the README.md in it to the `blob` URL).
"""
from pathlib import Path

from tools.build_epub import Ids, relink
from tools.build_site import (
    SOLUTIONS_BLOB_URL,
    SOLUTIONS_TREE_URL,
    link_solutions,
    load_chapter,
    rewrite_md_links,
)

STEM = "05_Foundations--Demo"
NAME = f"{STEM}.md"
SENTENCE = ("Each exercise is answered in this chapter's "
            "[solutions](../Solutions/{target}).")
URL = f"{SOLUTIONS_TREE_URL}/{STEM}"
FILE_URL = f"{SOLUTIONS_BLOB_URL}/{STEM}/README.md"


def test_folder_link_becomes_the_github_tree_url() -> None:
    body = "## Exercises\n\n" + SENTENCE.format(target=f"{STEM}/") + "\n"
    assert f"[solutions]({URL})." in link_solutions(body)
    assert "../Solutions/" not in link_solutions(body)


def test_readme_link_becomes_the_github_blob_url() -> None:
    body = SENTENCE.format(target=f"{STEM}/README.md") + "\n"
    assert f"[solutions]({FILE_URL})." in link_solutions(body)


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
