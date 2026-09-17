"""tools/comment_report.py: which listing comments are new since a ref."""

from textwrap import dedent

from tools.comment_report import CommentRecord, added, comments_in


def md(body: str) -> str:
    """A Markdown file's text from an indented triple-quoted literal."""
    return dedent(body).lstrip("\n")


def texts(records: list[CommentRecord]) -> list[str]:
    return [r.comment for r in records]


def test_trailing_and_full_line_comments_with_line_numbers() -> None:
    doc = md("""
        Prose above the listing.

        ```python
        # composition.py
        # A full-line comment
        class Contact:  # A trailing comment
            pass
        ```
    """)
    records = comments_in(doc)
    assert [(r.line, r.listing, r.comment, r.source) for r in records] == [
        (5, "composition.py", "# A full-line comment",
         "# A full-line comment"),
        (6, "composition.py", "# A trailing comment",
         "class Contact:  # A trailing comment"),
    ]


def test_slug_markers_and_directives_are_skipped() -> None:
    doc = md("""
        ```python
        # slugged.py
        import sys  # noqa: F401
        x: int = ok()  # type: ignore
        print(1)
        #: 1
        y = 2  # Worth reading
        ```
    """)
    assert texts(comments_in(doc)) == ["# Worth reading"]


def test_hash_inside_a_string_is_not_a_comment() -> None:
    doc = md('''
        ```python
        # maze.py
        MAZE = """
        #####
        #...#
        #####
        """
        print(MAZE)  # The real comment
        ```
    ''')
    assert texts(comments_in(doc)) == ["# The real comment"]


def test_fragment_that_fails_whole_block_tokenizing() -> None:
    doc = md("""
        ```python
            def method(self):  # Indented fragment
                return self.x  # Another one
        ```
    """)
    records = comments_in(doc)
    assert texts(records) == ["# Indented fragment", "# Another one"]
    assert [r.listing for r in records] == ["<fragment 1>"] * 2


def test_fragments_are_numbered_in_file_order() -> None:
    doc = md("""
        ```python
        first = 1  # One
        ```

        ```python
        # named.py
        second = 2  # Two
        ```

        ```python
        third = 3  # Three
        ```
    """)
    assert [r.listing for r in comments_in(doc)] == [
        "<fragment 1>", "named.py", "<fragment 2>"]


def test_added_comment_is_new_and_unchanged_ones_are_not() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Keep
        ```
    """)
    new = md("""
        ```python
        # one.py
        a = 1  # Keep
        b = 2  # Fresh
        ```
    """)
    assert texts(added(comments_in(old), comments_in(new))) == ["# Fresh"]


def test_edited_comment_is_new() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Old wording
        ```
    """)
    new = md("""
        ```python
        # one.py
        a = 1  # New wording
        ```
    """)
    assert texts(added(comments_in(old), comments_in(new))) == \
        ["# New wording"]


def test_moved_comment_is_not_new() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Moves
        b = 2
        ```
    """)
    new = md("""
        ```python
        # one.py
        a = 1
        b = 2  # Moves
        ```
    """)
    assert added(comments_in(old), comments_in(new)) == []


def test_a_listing_moved_within_its_file_is_not_new() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Stays put
        ```

        ```python
        # two.py
        b = 2  # Also stays
        ```
    """)
    new = md("""
        ```python
        # two.py
        b = 2  # Also stays
        ```

        ```python
        # one.py
        a = 1  # Stays put
        ```
    """)
    assert added(comments_in(old), comments_in(new)) == []


def test_duplicate_text_added_once_is_reported_once() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Same words
        ```
    """)
    new = md("""
        ```python
        # one.py
        a = 1  # Same words
        b = 2  # Same words
        ```
    """)
    reported = added(comments_in(old), comments_in(new))
    assert texts(reported) == ["# Same words"]
    # The last occurrence is the one reported, so the line is b's.
    assert [r.source for r in reported] == ["b = 2  # Same words"]


def test_the_same_text_in_two_listings_is_keyed_apart() -> None:
    old = md("""
        ```python
        # one.py
        a = 1  # Shared wording
        ```

        ```python
        # two.py
        b = 2
        ```
    """)
    new = md("""
        ```python
        # one.py
        a = 1  # Shared wording
        ```

        ```python
        # two.py
        b = 2  # Shared wording
        ```
    """)
    reported = added(comments_in(old), comments_in(new))
    assert [(r.listing, r.comment) for r in reported] == [
        ("two.py", "# Shared wording")]


def test_a_file_absent_at_the_ref_is_all_new() -> None:
    new = md("""
        ```python
        # one.py
        a = 1  # Brand new file
        ```
    """)
    assert texts(added([], comments_in(new))) == ["# Brand new file"]


def test_non_python_fences_are_ignored() -> None:
    doc = md("""
        ```text
        # not_a_listing.py
        # Looks like a comment
        ```
    """)
    assert comments_in(doc) == []
