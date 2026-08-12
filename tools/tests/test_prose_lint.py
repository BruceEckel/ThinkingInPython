"""Tests for tools/prose_lint.py, mostly the quoted-literal exception.

The other four checks are single regexes; QUOTE-PUNCT is the one that has
to tell quoted prose from a quoted literal, so it carries the cases.
"""

from prose_lint import lint_text


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

def test_single_token_quote_is_a_literal() -> None:
    assert codes('Names that contain "overdraft", and no others, run.') == []

def test_quote_holding_a_code_span_is_a_literal() -> None:
    assert codes('It needs a name for "callable, plus `undo()`".') == []

def test_multi_word_quote_without_code_is_still_prose() -> None:
    assert codes('A traceback labeled "Exception ignored", but nothing more.') \
        == ["QUOTE-PUNCT"]

def test_literal_exception_does_not_leak_to_the_next_quote() -> None:
    text = 'Given "this", the docs say "a shape of solution".'
    assert codes(text) == ["QUOTE-PUNCT"]

def test_unpaired_quote_falls_back_to_reporting() -> None:
    # An odd number of quotes leaves the last one unpaired and shifts the
    # pairing, so no quote can be shown to be a literal. The check reports
    # instead of skipping: a false positive is visible, a miss is not.
    assert codes('The 12" ruler, and "a shape of solution".') == [
        "QUOTE-PUNCT"]


# ── the checks that do not depend on quoting ──────────────────────────────────

def test_double_space_between_words() -> None:
    assert codes("One  two.") == ["MULTI-SPACE"]

def test_space_before_punctuation() -> None:
    assert codes("One , two.") == ["SPACE-BEFORE"]

def test_ellipsis_is_not_a_misplaced_period() -> None:
    assert codes("It works ... or so it seems.") == []

def test_code_span_is_skipped() -> None:
    assert codes('Write `x = "a".` and move on.') == []
