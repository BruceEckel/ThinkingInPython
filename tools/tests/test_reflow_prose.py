"""Tests for tools/reflow_prose.py (Semantic Line Breaks for prose)."""

from reflow_prose import _DEFAULT_WIDTH, reflow, split_sentences

# ── sentence splitting ────────────────────────────────────────────────────────

def test_splits_on_period() -> None:
    assert split_sentences("One. Two.") == ["One.", "Two."]

def test_splits_on_question_and_exclamation() -> None:
    assert split_sentences("Is it? Yes! Fine.") == ["Is it?", "Yes!", "Fine."]

def test_ellipsis_ends_a_sentence() -> None:
    assert split_sentences("Wait... Then go.") == ["Wait...", "Then go."]

def test_period_inside_inline_code_does_not_split() -> None:
    # Inline code is masked before splitting, so its punctuation is invisible.
    assert split_sentences("See `x = 1. y` here. Next.") == [
        "See `x = 1. y` here.", "Next."]

def test_period_after_inline_code_still_splits() -> None:
    assert split_sentences("Call `f()`. Next.") == ["Call `f()`.", "Next."]

# ── guards against false sentence boundaries ──────────────────────────────────

def test_abbreviation_does_not_split() -> None:
    assert split_sentences("The i.e. case. Next.") == ["The i.e. case.", "Next."]

def test_multiword_abbreviation_does_not_split() -> None:
    assert split_sentences("Vol. 3 is out. Next.") == ["Vol. 3 is out.", "Next."]

def test_initial_does_not_split() -> None:
    # "B." is an initial, not the end of a sentence.
    assert split_sentences("Ask B. Franklin about it. He knows.") == [
        "Ask B. Franklin about it.", "He knows."]

def test_decimal_does_not_split() -> None:
    assert split_sentences("The value is 3. 14 is next.") == [
        "The value is 3. 14 is next."]

def test_single_letter_word_does_split() -> None:
    # "C" is a language name in this book, not an initial (SINGLE_LETTER_WORDS).
    assert split_sentences("Written in C. It is fast.") == [
        "Written in C.", "It is fast."]

def test_slashed_compound_does_split() -> None:
    # The token walk stops at the "/" and yields a bare "O", which the
    # initial rule would otherwise mistake for "B."-style initials, so a
    # sentence ending in "I/O." could never end a sentence.
    assert split_sentences("It performs live I/O. Make it an interface.") == [
        "It performs live I/O.", "Make it an interface."]

def test_slashed_compound_ab_does_split() -> None:
    assert split_sentences("Run an A/B. Then compare.") == [
        "Run an A/B.", "Then compare."]

# ── non-prose blocks are preserved verbatim ───────────────────────────────────

def test_fenced_code_is_untouched() -> None:
    text = "```python\nx = 1. y = 2\n```\n\nOne. Two.\n"
    out, count = reflow(text)
    assert out == "```python\nx = 1. y = 2\n```\n\nOne.\nTwo.\n"
    assert count == 1

def test_heading_and_table_are_untouched() -> None:
    text = "# Head. Ing\n\n| a | b |\n|---|---|\n| 1. 2 | 3 |\n\nOne. Two.\n"
    out, _ = reflow(text)
    assert "# Head. Ing\n" in out
    assert "| 1. 2 | 3 |\n" in out

def test_blockquote_and_rule_are_untouched() -> None:
    out, _ = reflow("> Quoted. Text.\n\n---\n\nOne. Two.\n")
    assert out == "> Quoted. Text.\n\n---\n\nOne.\nTwo.\n"

def test_list_item_continuation_keeps_its_indent() -> None:
    out, _ = reflow("1.  A list item. With two sentences.\n2.  Another one.\n")
    assert out == "1.  A list item.\n    With two sentences.\n2.  Another one.\n"

# ── clause wrapping ───────────────────────────────────────────────────────────

def test_short_sentence_is_left_on_one_line() -> None:
    out, count = reflow("Short, with a comma.\n")
    assert out == "Short, with a comma.\n"
    assert count == 0

def test_long_sentence_breaks_at_clause_punctuation() -> None:
    text = ("This is a fairly long sentence about handlers, which needs a "
            "clause break somewhere, and it keeps going past the width limit.\n")
    out, _ = reflow(text)
    lines = out.splitlines()
    assert len(lines) > 1
    assert all(len(line) <= _DEFAULT_WIDTH for line in lines)
    assert all(line.rstrip().endswith((",", ";", ":", ".")) for line in lines)

def test_each_reflowed_paragraph_is_counted() -> None:
    assert reflow("One. Two.\n\nThree. Four.\n")[1] == 2

# ── the safety invariant: newlines move, words never do ───────────────────────

def test_reflow_preserves_every_word() -> None:
    text = (
        "# A Heading\n\n"
        "One sentence here. A second, longer sentence that runs past the "
        "width limit and therefore breaks at a comma, somewhere sensible.\n\n"
        "```python\nkeep = 'me. verbatim'\n```\n\n"
        "- A list item. With two sentences.\n\n"
        "Trailing prose about I/O. And more.\n"
    )
    out, _ = reflow(text)
    assert out.split() == text.split()

def test_reflow_is_idempotent() -> None:
    text = "One sentence. Another sentence, with a clause.\n"
    once, _ = reflow(text)
    twice, count = reflow(once)
    assert twice == once
    assert count == 0
