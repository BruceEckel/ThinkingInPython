"""Tests for tools/sentence_diff.py.

Each case is a false rewrite that reached a real report before the
filter that now stops it.
"""
from tools.sentence_diff import diff, prose

LONG = ("The design has three parts: an `Observer` interface, "
        "a `Subject` base class, and `Subject.notify()` that broadcasts:\n")


def test_a_real_rewrite_pairs_with_its_successor() -> None:
    before = "A listener that raises an exception stops the whole loop.\n"
    after = "If a listener raises an exception, the loop stops early.\n"
    [rewrite], alone = diff(before, after, "30_A--B.md")
    assert rewrite.after.startswith("If a listener")
    assert alone == []


def test_a_reflow_is_not_a_rewrite() -> None:
    wrapped = LONG.replace(" a `Subject`", "\na `Subject`")
    rewrites, _ = diff(LONG, wrapped, "30_A--B.md")
    assert rewrites == []


def test_breaking_a_line_after_a_colon_is_not_a_rewrite() -> None:
    """The splitter ends a sentence at a line-final colon, so this
    reflow split one sentence into a short one and a remainder."""
    split = LONG.replace("three parts: an", "three parts:\nan")
    rewrites, _ = diff(LONG, split, "30_A--B.md")
    assert rewrites == []


def test_figure_captions_and_draft_notes_are_not_sentences() -> None:
    text = ("![Assigning to celsius calls every listener in turn]"
            "(_images/observer_broadcast)\n\n"
            "[[which one?]] Remove it here and `ty` objects to the call.\n")
    assert prose(text, "30_A--B.md") == []
