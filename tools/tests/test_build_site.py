"""Tests for tools/build_site.py's Solutions link rewrite.

A chapter links its Solutions file with a relative path so GitHub shows
a working link. The built site, EPUB, and PDF carry no Solutions pages,
so load_chapter() rewrites the link to the file's GitHub URL.
"""
from pathlib import Path

from tools.build_epub import Ids, relink
from tools.build_site import (
    SOLUTIONS_URL,
    link_solutions,
    load_chapter,
    rewrite_md_links,
)

NAME = "05_Foundations--Demo.md"
SENTENCE = ("Each exercise is answered in this chapter's "
            "[solutions](../Solutions/{target}).")
URL = f"{SOLUTIONS_URL}/{NAME}"


def test_relative_link_becomes_the_github_url() -> None:
    body = "## Exercises\n\n" + SENTENCE.format(target=NAME) + "\n"
    assert f"[solutions]({URL})." in link_solutions(body)
    assert "../Solutions/" not in link_solutions(body)


def test_anchor_survives() -> None:
    body = f"See [it](../Solutions/{NAME}#2-second) now.\n"
    assert link_solutions(body) == f"See [it]({URL}#2-second) now.\n"


def test_link_inside_a_fence_is_left_alone() -> None:
    body = f"```text\n[x](../Solutions/{NAME})\n```\n"
    assert link_solutions(body) == body


def test_body_without_the_link_is_unchanged() -> None:
    body = "# Demo\n\nSee [other](06_Foundations--Other.md).\n"
    assert link_solutions(body) == body


def test_load_chapter_rewrites_the_link(tmp_path: Path) -> None:
    md = tmp_path / NAME
    md.write_text("# Demo\n\n## Exercises\n\n"
                  + SENTENCE.format(target=NAME) + "\n\n1. First\n",
                  encoding="utf-8")
    _, body = load_chapter(md)
    assert f"[solutions]({URL})" in body
    assert "../Solutions/" not in body


def test_url_survives_rewrite_md_links() -> None:
    text = f"[solutions]({URL}#x)"
    assert rewrite_md_links(text) == text


def test_url_survives_the_epub_relink() -> None:
    text = f"[solutions]({URL})"
    unresolved: set[str] = set()
    ids = Ids(prefixes={}, known=set(), aliases={})
    assert relink(text, "ch05", ids, unresolved) == text
    assert unresolved == set()
