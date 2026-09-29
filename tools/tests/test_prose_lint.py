"""Tests for tools/prose_lint.py, mostly the quoted-literal exception.

The other four checks are single regexes; QUOTE-PUNCT is the one that has
to tell quoted prose from a quoted literal, so it carries the cases.
"""

import pytest

from tools.prose_lint import lint_text


def codes(text: str) -> list[str]:
    return [code for _, _, code, _ in lint_text(text)]


# ── QUOTE-PUNCT: quoted prose keeps the mark inside ───────────────────────────

def test_comma_after_quoted_prose_is_reported() -> None:
    assert codes('He called it "a shape of solution", and moved on.') == [
        "QUOTE-PUNCT"]

def test_period_after_quoted_prose_is_reported() -> None:
    assert codes('The docs call this "structural pattern matching".') == [
        "QUOTE-PUNCT"]

def test_mark_inside_a_quotation_is_clean() -> None:
    assert codes('The rule is "ask forgiveness, not permission," in short.') \
        == []


# ── QUOTE-PUNCT: a quoted literal keeps the mark outside ──────────────────────

def test_single_token_quote_named_in_a_code_span_is_a_literal() -> None:
    assert codes('`pytest -k overdraft` runs names that contain "overdraft", '
                 'and no others.') == []

def test_single_token_quote_with_no_code_span_is_prose() -> None:
    text = 'When you have "this", and you need "that", it applies.'
    assert codes(text) == ["QUOTE-PUNCT", "QUOTE-PUNCT"]
    text = 'nothing distinguishes "deliberately empty" from "forgotten".'
    assert codes(text) == ["QUOTE-PUNCT"]

def test_single_token_quote_needs_the_span_on_its_own_line() -> None:
    text = 'A `label` is set.\nThe display reads "label", then clears.'
    assert codes(text) == ["QUOTE-PUNCT"]

def test_quote_holding_a_code_span_is_a_literal() -> None:
    assert codes('It needs a name for "callable, plus `undo()`".') == []

def test_multi_word_quote_without_code_is_still_prose() -> None:
    assert codes('A traceback labeled "Exception ignored", but nothing more.') \
        == ["QUOTE-PUNCT"]

def test_literal_exception_does_not_leak_to_the_next_quote() -> None:
    text = 'Given `-k this` and "this", the docs say "a shape of solution".'
    assert codes(text) == ["QUOTE-PUNCT"]

def test_unpaired_quote_falls_back_to_reporting() -> None:
    # An odd number of quotes leaves the last one unpaired and shifts the
    # pairing, so no quote can be shown to be a literal. The check reports
    # instead of skipping: a false positive is visible, a miss is not.
    assert codes('The 12" ruler, and "a shape of solution".') == [
        "QUOTE-PUNCT"]


# ── HTML comments ─────────────────────────────────────────────────────────────

def test_comment_continuation_line_is_not_prose() -> None:
    assert codes("<!-- TODO: this line has  two spaces\n"
                 "and this  one does too. -->\n") == []

def test_prose_after_a_closed_comment_is_still_checked() -> None:
    assert codes("<!-- a note -->\nOne  two.\n") == ["MULTI-SPACE"]


# ── the checks that do not depend on quoting ──────────────────────────────────

def test_double_space_between_words() -> None:
    assert codes("One  two.") == ["MULTI-SPACE"]

def test_space_before_punctuation() -> None:
    assert codes("One , two.") == ["SPACE-BEFORE"]

def test_ellipsis_is_not_a_misplaced_period() -> None:
    assert codes("It works ... or so it seems.") == []

def test_code_span_is_skipped() -> None:
    assert codes('Write `x = "a".` and move on.') == []


# ── SET-FIX: "fix" meaning "set" reads as "repair" ────────────────────────────

SET_SENSE = [
    'Constructing `Box("gift")` fixes `T` to `str` for that instance.',
    "`membership.py` fixes `target` at the worst case.",
    "`Iterator` fixes the `ReturnType` at `None`.",
    "A *Template Method* fixes the sequence.",
    "It fixes the flow and leaves the steps open.",
    "The formula fixes its shape.",
    "Creating the thread fixes its maximum size.",
    "The type code fixes one type for every element.",
    "Its type parameter fixes the type of each notification.",
    "Fixing the third argument meant more work.",
    "Partial application fixes some of a function's arguments.",
    "A factory that fixes one argument returns a function.",
    "`percent` fixes the bounds and leaves the middle open.",
    "The call fixes the moment of collection.",
    "Because `gather()` fixes its argument list then.",
    "It lets you fix a later positional argument.",
]

REPAIR_SENSE = [
    "Fix the algorithm and the data structures.",
    "Step 4, fixing the algorithm, is usually the biggest win.",
    "Then fix the class so the shared counter moves.",
    "Fix the loop three ways.",
    "Fix the caller two ways.",
    "The weak reference fixes the leak.",
    "A `__post_init__()` fixes that.",
    "One change fixes both problems at once.",
    "Then fix `flatten()` so a `str` yields as one item.",
    "Then fix `WhatIUse2.op()` without restoring the `/`.",
    "It reads a fixed-length record.",
    "A machine has a fixed set of states.",
    "## Rows to a Fixed Point",
    "The fix is a lock.",
    "Two fixes for a spent generator.",
    "Three fixes for late binding.",
]

@pytest.mark.parametrize("text", SET_SENSE)
def test_set_sense_is_reported(text: str) -> None:
    assert codes(text).count("SET-FIX") == 1

@pytest.mark.parametrize("text", REPAIR_SENSE)
def test_repair_sense_and_adjective_are_clean(text: str) -> None:
    assert "SET-FIX" not in codes(text)

def test_set_fix_column_points_at_the_verb() -> None:
    [(_, col, _, _)] = lint_text("- It fixes the sequence.")
    assert col == len("- It ") + 1

def test_set_fix_in_a_fenced_block_is_skipped() -> None:
    text = "```python\n# This fixes the type of `x` to `int`.\n```\n"
    assert codes(text) == []
