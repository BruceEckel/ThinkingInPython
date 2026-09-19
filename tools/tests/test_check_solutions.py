"""Tests for tools/check_solutions.py (exercise/solution correspondence)."""
from pathlib import Path

from tools.check_solutions import (
    BARE_CHAPTER_LINK,
    answer_numbers,
    exercise_numbers,
    misnamed_listings,
    out_of_order,
    selected,
)
from tools.config import ROOT
from tools.markdown import Document

CHAPTER = (
    "# A Chapter\n"
    "\n"
    "## Exercises\n"
    "\n"
    "1.  Rewrite it.\n"
    "    A continued line that is not an item.\n"
    "2.  Break it on purpose.\n"
)

SOLUTIONS = (
    "# A Chapter: Solutions\n"
    "\n"
    "## 1. Rewritten\n"
    "\n"
    "```python\n"
    "# exercise_1.py\n"
    "print(1)\n"
    "#: 1\n"
    "```\n"
    "\n"
    "## 2. Broken on purpose\n"
)

def doc(text: str) -> Document:
    return Document.from_text(text, Path("a.md"))

# ── reading the two lists ─────────────────────────────────────────────────────

def test_exercises_are_the_top_level_items() -> None:
    assert exercise_numbers(doc(CHAPTER)) == [(1, 5), (2, 7)]

def test_prose_only_exercises_section_has_no_exercises() -> None:
    # Chapter 1 describes the convention instead of setting exercises.
    prose = "## Exercises\n\nMost chapters end with one.\n"
    assert exercise_numbers(doc(prose)) == []

def test_a_later_exercises_heading_wins() -> None:
    # A chapter mentioning the word early must not accumulate both lists.
    text = "## Exercises\n\n1.  Old.\n\n" + CHAPTER
    assert exercise_numbers(doc(text)) == [(1, 9), (2, 11)]

def test_an_ordered_list_inside_a_fence_is_not_an_exercise() -> None:
    text = "## Exercises\n\n```text\n1.  Sample output.\n```\n\n1.  Real.\n"
    assert exercise_numbers(doc(text)) == [(1, 7)]

def test_answers_are_the_numbered_headings() -> None:
    assert answer_numbers(doc(SOLUTIONS)) == [(1, 3), (2, 11)]

def test_an_unnumbered_heading_is_not_an_answer() -> None:
    assert answer_numbers(doc("# Solutions\n\n## Notes\n")) == []

def test_a_combined_heading_answers_several_exercises() -> None:
    combined = "## 1 & 2. A Triangle in both styles\n"
    assert answer_numbers(doc(combined)) == [(1, 1), (2, 1)]

def test_a_range_heading_answers_the_whole_range() -> None:
    assert answer_numbers(doc("## 2-4. Three at once\n")) == [
        (2, 1), (3, 1), (4, 1),
    ]

# ── numbering ─────────────────────────────────────────────────────────────────

def test_sequential_numbering_is_clean() -> None:
    assert list(out_of_order([(1, 3), (2, 9)], Path("a.md"), "solution")) == []

def test_a_gap_in_the_numbering_is_reported() -> None:
    findings = list(out_of_order([(1, 3), (3, 9)], Path("a.md"), "solution"))
    assert len(findings) == 1
    assert "numbered 3 where 2 was expected" in findings[0].message

# ── listing names ─────────────────────────────────────────────────────────────

def listing(name: str) -> str:
    return f"```python\n# {name}\nprint(1)\n```\n"

def test_a_listing_named_for_its_heading_is_clean() -> None:
    assert list(misnamed_listings(doc(SOLUTIONS))) == []

def test_a_listing_named_for_another_exercise_is_reported() -> None:
    # Chapter 30 after its exercises were reordered.
    text = "## 2. Survives a failure\n\n" + listing("exercise_3.py")
    [finding] = misnamed_listings(doc(text))
    assert finding.line == 4
    assert "exercise_3.py" in finding.message

def test_a_suffixed_listing_name_is_read_too() -> None:
    text = "## 2. Two variants\n\n" + listing("exercise_2b.py")
    assert list(misnamed_listings(doc(text))) == []
    text = "## 2. Two variants\n\n" + listing("exercise_5_frozen.py")
    assert len(list(misnamed_listings(doc(text)))) == 1

def test_exercise_12_is_not_exercise_1() -> None:
    text = "## 1. First\n\n" + listing("exercise_12.py")
    assert len(list(misnamed_listings(doc(text)))) == 1

def test_a_combined_heading_accepts_each_of_its_numbers() -> None:
    text = ("## 1 & 2. Both styles\n\n" + listing("exercise_1.py")
            + "\n" + listing("exercise_2.py"))
    assert list(misnamed_listings(doc(text))) == []

def test_a_test_file_or_helper_is_exempt() -> None:
    text = ("## 2. Survives a failure\n\n"
            + listing("test_resilient_announce.py")
            + "\n" + listing("helpers.py"))
    assert list(misnamed_listings(doc(text))) == []

def test_a_listing_above_the_first_heading_is_exempt() -> None:
    text = listing("exercise_9.py") + "\n## 1. First\n"
    assert list(misnamed_listings(doc(text))) == []

# ── chapter citations ─────────────────────────────────────────────────────────

def test_a_bare_chapter_link_is_flagged() -> None:
    m = BARE_CHAPTER_LINK.search("see [State](26_Patterns--Surrogate.md#state) for")
    assert m is not None
    assert m.group(1) == "26_Patterns--Surrogate.md"

def test_a_bare_link_with_no_anchor_is_flagged_too() -> None:
    assert BARE_CHAPTER_LINK.search("[Classes](07_Foundations--Classes.md)") is not None

def test_a_chapters_prefixed_link_is_clean() -> None:
    text = "[State](../Chapters/26_Patterns--Surrogate.md#state)"
    assert BARE_CHAPTER_LINK.search(text) is None

def test_an_explicit_sibling_link_is_the_opt_out() -> None:
    assert BARE_CHAPTER_LINK.search("[that answer](./26_Patterns--Surrogate.md)") is None

def test_a_same_file_anchor_is_not_a_chapter_link() -> None:
    assert BARE_CHAPTER_LINK.search("[above](#the-heading)") is None

# ── chapter selection ─────────────────────────────────────────────────────────

def test_no_arguments_selects_every_chapter() -> None:
    assert selected([]) == sorted((ROOT / "Chapters").glob("*.md"))

def test_a_bare_number_selects_one_chapter() -> None:
    assert [p.stem for p in selected(["7"])] == ["07_Foundations--Classes"]
