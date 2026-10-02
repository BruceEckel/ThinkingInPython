"""Tests for tools/check_solutions.py (exercise/solution correspondence)."""
from pathlib import Path

import pytest

from tools import check_solutions
from tools.check_solutions import (
    BARE_CHAPTER_LINK,
    answer_numbers,
    exercise_numbers,
    misnamed_listings,
    out_of_order,
    selected,
    solutions_links,
    solutions_sentence,
    with_solutions_link,
    write_links,
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

# ── the Solutions link ────────────────────────────────────────────────────────

STEM = "05_Foundations--Demo"
NAME = f"{STEM}.md"
LINK = f"](../Solutions/{STEM}/)"
SENTENCE = solutions_sentence(STEM)


def findings(text: str) -> list[str]:
    return [f.message for f in solutions_links(Path(NAME), doc(text))]


def test_a_missing_link_is_reported_at_the_heading() -> None:
    [finding] = solutions_links(Path(NAME), doc(CHAPTER))
    assert finding.line == 3
    assert f"no link to Solutions/{STEM}/" in finding.message
    assert "tip fix-solutions-links" in finding.message


def test_a_link_to_another_file_is_reported() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite",
        "See [s](../Solutions/04_Old--Name.md).\n\n1.  Rewrite")
    [finding] = solutions_links(Path(NAME), doc(text))
    assert finding.line == 5
    assert "04_Old--Name.md" in finding.message
    assert STEM in finding.message


def test_the_flat_layout_link_is_stale() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite",
        f"See [s](../Solutions/{NAME}).\n\n1.  Rewrite")
    [finding] = solutions_links(Path(NAME), doc(text))
    assert f"Solutions/{NAME}" in finding.message


def test_the_readme_file_link_passes_with_or_without_an_anchor() -> None:
    for tail in ("", "#2-second"):
        text = CHAPTER.replace(
            "1.  Rewrite",
            f"See [s](../Solutions/{STEM}/README.md{tail}).\n\n"
            "1.  Rewrite")
        assert findings(text) == []


def test_the_right_link_passes() -> None:
    text = CHAPTER.replace("1.  Rewrite", SENTENCE + "\n\n1.  Rewrite")
    assert findings(text) == []


def test_a_reworded_sentence_with_the_right_link_passes() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite", f"Answers are [here]{LINK}.\n\n1.  Rewrite")
    assert findings(text) == []


def test_a_link_in_a_fence_does_not_count() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite", f"```text\n[x]{LINK}\n```\n\n1.  Rewrite")
    assert len(findings(text)) == 1


def test_write_inserts_with_blank_lines() -> None:
    out = with_solutions_link(CHAPTER, NAME)
    assert "## Exercises\n\n" + SENTENCE + "\n\n1.  Rewrite" in out
    assert out.count("\n") == CHAPTER.count("\n") + 2
    assert out.endswith(CHAPTER[-30:])


def test_write_adds_a_blank_line_when_none_precedes_the_items() -> None:
    text = "## Exercises\n1.  First.\n"
    assert with_solutions_link(text, NAME) == (
        "## Exercises\n\n" + SENTENCE + "\n\n1.  First.\n")


def test_write_keeps_crlf() -> None:
    text = CHAPTER.replace("\n", "\r\n")
    out = with_solutions_link(text, NAME)
    assert SENTENCE + "\r\n\r\n1.  Rewrite" in out
    assert out.replace("\r\n", "") .count("\n") == 0


def test_write_corrects_a_stale_target_and_keeps_the_wording() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite",
        "Answers are [here](../Solutions/04_Old--Name.md#a).\n\n1.  Rewrite")
    out = with_solutions_link(text, NAME)
    assert f"Answers are [here](../Solutions/{STEM}/#a)." in out
    assert out.count("\n") == text.count("\n")


def test_write_migrates_the_flat_layout_link_to_the_folder() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite", f"Answers are [here](../Solutions/{NAME}).\n\n"
        "1.  Rewrite")
    out = with_solutions_link(text, NAME)
    assert f"Answers are [here](../Solutions/{STEM}/)." in out
    assert findings(out) == []


def test_write_leaves_the_readme_file_link_alone() -> None:
    text = CHAPTER.replace(
        "1.  Rewrite", f"Answers: [here](../Solutions/{STEM}/README.md).\n\n"
        "1.  Rewrite")
    assert with_solutions_link(text, NAME) == text


def test_write_twice_changes_nothing() -> None:
    once = with_solutions_link(CHAPTER, NAME)
    assert with_solutions_link(once, NAME) == once


def test_a_chapter_without_exercises_is_untouched() -> None:
    text = "## Exercises\n\nMost chapters end with one.\n"
    assert with_solutions_link(text, NAME) == text


def test_write_links_leaves_a_chapter_without_a_solutions_file(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    empty = tmp_path / "Solutions"
    empty.mkdir()
    monkeypatch.setattr(check_solutions, "SOLUTIONS_DIR", empty)
    chapter = tmp_path / NAME
    chapter.write_text(CHAPTER, encoding="utf-8")
    assert write_links([chapter]) == []
    assert chapter.read_text(encoding="utf-8") == CHAPTER


# ── how a solutions file cites its chapter ────────────────────────────────────

def citation_messages(text: str, tmp_path: Path) -> list[str]:
    path = tmp_path / "Solutions" / STEM / "README.md"
    path.parent.mkdir(parents=True)
    path.write_text(text, encoding="utf-8")
    return [f.message for f in check_solutions.chapter_citations(path)]


def test_a_bare_chapter_link_says_to_use_two_levels(
        tmp_path: Path) -> None:
    [message] = citation_messages(
        "See [x](26_Patterns--Surrogate.md#state).\n", tmp_path)
    assert "../../Chapters/26_Patterns--Surrogate.md" in message


def test_a_one_level_chapters_link_is_reported(tmp_path: Path) -> None:
    [message] = citation_messages(
        "See [x](../Chapters/26_Patterns--Surrogate.md#state).\n", tmp_path)
    assert "resolves inside Solutions/" in message
    assert "../../Chapters/26_Patterns--Surrogate.md#state" in message


def test_a_two_level_chapters_link_passes(tmp_path: Path) -> None:
    assert citation_messages(
        "See [x](../../Chapters/26_Patterns--Surrogate.md#state).\n",
        tmp_path) == []


def test_a_one_level_link_in_a_fence_is_ignored(tmp_path: Path) -> None:
    assert citation_messages(
        "```text\n[x](../Chapters/26_Patterns--Surrogate.md)\n```\n",
        tmp_path) == []
