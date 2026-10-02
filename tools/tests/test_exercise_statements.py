"""Tests for tools/exercise_statements.py (statements copied to Solutions)."""
from pathlib import Path

from tools import exercise_refs as er
from tools.exercise_statements import (
    apply,
    generated_lines,
    rewrite_links,
    statements,
)
from tools.markdown import Document

NAME = "05_Foundations--Demo.md"


def doc(text: str, name: str = "a.md") -> Document:
    return Document.from_text(text, Path(name))


def chapter(*items: str, after: str = "") -> Document:
    body = "".join(items)
    return doc(f"# Demo\n\n## Exercises\n\n{body}{after}", NAME)


def rendered(solutions: str, source: Document) -> str:
    lines, _ = apply(doc(solutions), source, NAME)
    return "\n".join(lines)


def test_one_digit_item_is_dedented_and_loses_its_marker() -> None:
    source = chapter("1.  Write it.\n    Then test it.\n")
    text = rendered("## 1. Write\n\nAnswer.\n", source)
    assert text == (
        "## 1. Write\n\n> Write it.\n> Then test it.\n\nAnswer.\n")


def test_two_digit_item_text_starts_at_column_four() -> None:
    items = "".join(
        f"{n}.{' ' if n > 9 else '  '}Item {n}.\n" for n in range(1, 11))
    found = statements(chapter(items))
    assert found[10].column == 4
    assert found[10].lines == ("10. Item 10.",)
    assert found[9].lines == ("9.  Item 9.",)
    assert found[9].column == 4


def test_blank_line_and_nested_list_keep_their_structure() -> None:
    source = chapter(
        "1.  Do this:\n\n"
        "    1. First.\n"
        "    2. Second.\n\n"
        "2.  Next.\n")
    text = rendered("## 1. A\n\nBody.\n", source)
    assert text == (
        "## 1. A\n\n"
        "> Do this:\n>\n"
        "> 1. First.\n"
        "> 2. Second.\n\n"
        "Body.\n")


def test_a_footnote_definition_is_not_part_of_the_last_exercise() -> None:
    source = chapter(
        "1.  Last one.[^note]\n",
        after="\n[^note]: A note.\n    More of it.\n\n"
              "    ```python\n    x = 1\n    ```\n")
    [only] = statements(source).values()
    assert only.lines == ("1.  Last one.[^note]",)
    assert rendered("## 1. A\n\nBody.\n", source).startswith(
        "## 1. A\n\n> Last one.\n\nBody.")


def test_a_combined_heading_keeps_each_item_as_written() -> None:
    source = chapter("1.  First.\n    More.\n2.  Second.\n3.  Third.\n")
    text = rendered("## 1 & 2. Both\n\nBody.\n", source)
    assert text == (
        "## 1 & 2. Both\n\n"
        "> 1.  First.\n>     More.\n>\n> 2.  Second.\n\nBody.\n")
    assert "3.  Third" not in text


def test_anchor_and_book_links_gain_the_chapters_prefix() -> None:
    text = rewrite_links(
        "See [x](#a-heading) and [y](17_Techniques--Metaprogramming.md#z)"
        " and [z](A_Effect_Tracking.md).", NAME)
    assert text == (
        f"See [x](../Chapters/{NAME}#a-heading) and "
        "[y](../Chapters/17_Techniques--Metaprogramming.md#z) and "
        "[z](../Chapters/A_Effect_Tracking.md).")


def test_code_spans_and_other_links_are_left_alone() -> None:
    same = ("`last[T](items: list[T])` and [w](https://x.org/a.md)"
            " and [v](dir/a.md) and [u](../Chapters/a.md)")
    assert rewrite_links(same, NAME) == same


def test_footnote_references_are_removed() -> None:
    assert rewrite_links("Done.[^one] Again[^two].", NAME) == (
        "Done. Again.")


def test_an_existing_block_is_replaced_in_full() -> None:
    source = chapter("1.  New text.\n")
    old = "## 1. A\n\n> Old text.\n> More old.\n\nBody.\n"
    assert rendered(old, source) == (
        "## 1. A\n\n> New text.\n\nBody.\n")


def test_a_second_run_changes_nothing() -> None:
    source = chapter("1.  Text.\n", "2.  Other.\n")
    first = rendered("## 1. A\n\nBody.\n\n## 2. B\nBody.\n", source)
    lines, changed = apply(doc(first), source, NAME)
    assert changed == []
    assert "\n".join(lines) == first


def test_unnumbered_and_unmatched_headings_get_nothing() -> None:
    source = chapter("1.  Text.\n")
    text = "## Shared code: the bakery\n\nBody.\n\n## 9. Gone\n\nBody.\n"
    assert rendered(text, source) == text


def test_fenced_headings_and_quotes_are_ignored() -> None:
    source = chapter("1.  Text.\n")
    text = "```text\n## 1. Not a heading\n```\n"
    assert rendered(text, source) == text


def test_crlf_endings_and_final_newline_survive() -> None:
    source = chapter("1.  Text.\n")
    text = "## 1. A\r\n\r\nBody.\r\n"
    lines, changed = apply(doc(text), source, NAME)
    assert changed == [(1, True)]
    assert "\n".join(lines) == (
        "## 1. A\r\n\r\n> Text.\r\n\r\nBody.\r\n")


def test_generated_lines_are_the_quote_lines_only() -> None:
    text = "## 1. A\n\n> One.\n>\n> Two.\n\nBody.\n\n> Elsewhere.\n"
    assert generated_lines(doc(text)) == {3, 4, 5}


def test_exercise_refs_skips_the_generated_statement(
        tmp_path: Path) -> None:
    path = tmp_path / "Solutions" / "05_Foundations--Demo.md"
    path.parent.mkdir()
    path.write_text(
        "## 1. A\n\n> See exercise 2 for the rest.\n\n"
        "Body mentions exercise 2 again.\n\n## 2. B\n\nText.\n",
        encoding="utf-8")
    found = list(er.references(path))
    assert [(r.line, r.number) for r in found] == [(5, 2)]
