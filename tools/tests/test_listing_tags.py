"""Tests for tools/listing_tags.py: tags and citations."""
from tools.listing_tags import find
from tools.markdown import Document

FENCE = "```"


def listing(*code: str) -> str:
    return "\n".join([f"{FENCE}python", *code, FENCE])


def lines(*parts: str) -> list[int]:
    doc = Document.from_text("\n".join(parts) + "\n")
    return [f.line for f in find(doc)]


def messages(*parts: str) -> list[str]:
    doc = Document.from_text("\n".join(parts) + "\n")
    return [f.message for f in find(doc)]


def test_a_listing_with_every_tag_cited_is_clean() -> None:
    assert lines(
        listing("a = 1  # [1]", "b = 2  # [2]"),
        "",
        "`[1]` sets `a`, and `[2]` sets `b`.",
    ) == []


def test_a_gap_in_the_numbering_is_reported() -> None:
    found = messages(
        listing("a = 1  # [1]", "b = 2  # [3]"),
        "`[1]` and `[3]`.",
    )
    assert found == [
        "tag [3] where [2] comes next; a listing numbers "
        "its tags 1, 2, 3, ... in order"]


def test_a_repeated_tag_is_reported() -> None:
    assert lines(
        listing("a = 1  # [1]", "b = 2  # [1]"),
        "`[1]`.",
    ) == [3]


def test_a_tag_never_cited_is_reported() -> None:
    assert lines(
        listing("a = 1  # [1]", "b = 2  # [2]"),
        "",
        "`[1]` sets `a`.",
    ) == [3]


def test_a_citation_past_a_heading_is_not_counted() -> None:
    assert lines(
        listing("a = 1  # [1]"),
        "",
        "## Next",
        "",
        "`[1]` sets `a`.",
    ) == [2, 7]


def test_a_citation_of_a_missing_tag_is_reported() -> None:
    found = messages(
        listing("a = 1  # [1]"),
        "`[1]` sets `a`, and `[2]` is missing.",
    )
    assert found == [
        "`[2]` names no tag in the listing above it "
        "(opening at line 1)"]


def test_a_citation_under_a_heading_with_no_block() -> None:
    assert lines(
        "# Title",
        "",
        "See `[1]` before any listing.",
    ) == [3]


def test_a_citation_names_the_nearest_block_above() -> None:
    assert lines(
        listing("a = 1  # [1]", "b = 2  # [2]"),
        "`[1]` and `[2]`.",
        listing("c = 3"),
        "`[2]` cites the untagged listing.",
    ) == [9]


def test_a_bare_number_in_brackets_is_reported() -> None:
    doc = Document.from_text(
        listing("a = 1  # [1]", "b = 2  # [2]")
        + "\n`[1]` and [2] here, `[2]` there.\n")
    found = list(find(doc))
    assert [(f.line, f.col) for f in found] == [(5, 11)]
    assert found[0].message.startswith(
        "bare [2]: write it as the code span `[2]`")


def test_links_and_definitions_are_not_bare() -> None:
    assert lines(
        "A [1](https://example.com) link.",
        "",
        "[2]: https://example.com",
    ) == []


def test_an_own_line_tag_marks_the_line_below() -> None:
    assert lines(
        listing(
            "a = 1  # [1]",
            "    # [2]",
            "b = some_long_call(argument_one, two)",
        ),
        "`[1]` sets `a` and `[2]` sets `b`.",
    ) == []


def test_a_text_block_can_carry_tags() -> None:
    assert lines(
        f"{FENCE}text",
        "one  # [1]",
        FENCE,
        "",
    ) == [2]


def test_footnotes_and_subscripts_cite_nothing() -> None:
    assert lines(
        "A note[^1] and `x[1]` and `[0]` in prose.",
        "",
        "[^1]: The note.",
    ) == []


def test_untagged_listings_are_clean() -> None:
    assert lines(
        listing("a = [1, 2]", "print(a[0])"),
        "",
        "The list holds two numbers.",
    ) == []
