"""Tests for tools/exercise_refs.py.

A sentence that names an exercise by number is prose: inserting an
exercise leaves the chapter's list and its Solutions headings in
agreement and every such sentence pointing one exercise too early.
The check pairs each reference with the Solutions title under its
number and gates the pairs against a baseline. These tests pin what
counts as a reference, which chapter it targets, and how an
insertion shows up in the delta.
"""
from pathlib import Path

import pytest

from tools import exercise_refs as er

CHAPTER = "30_Patterns--Observer"
OTHER = "27_Patterns--Factory"

SOLUTIONS = (
    "# Observer: Solutions\n\n"
    "## 1. A minimal pair\n\nText.\n\n"
    "## 2. A failing listener\n\nText.\n\n"
    "## 3. Two views\n\n"
    "Counting worked in the previous exercise, and\n"
    "exercise 1 set it up.\n"
)
OTHER_SOLUTIONS = (
    "# Factory: Solutions\n\n"
    "## 1 & 2. A `Triangle` in both styles\n\nText.\n\n"
    "## 3. Recursing through `__subclasses__()`\n\nText.\n"
)


def book(root: Path, chapter: str, solutions: str = SOLUTIONS) -> Path:
    """A two-chapter tree under `root`; returns the chapter's path."""
    for tree in ("Chapters", "Solutions"):
        (root / tree).mkdir(exist_ok=True)
    md = root / "Chapters" / f"{CHAPTER}.md"
    md.write_text(chapter, encoding="utf-8")
    (root / "Solutions" / f"{CHAPTER}.md").write_text(
        solutions, encoding="utf-8")
    (root / "Chapters" / f"{OTHER}.md").write_text(
        "# Factory\n", encoding="utf-8")
    (root / "Solutions" / f"{OTHER}.md").write_text(
        OTHER_SOLUTIONS, encoding="utf-8")
    return md


def entries(root: Path, path: Path) -> list[str]:
    pairs, errors = er.resolve(list(er.references(path)), root)
    assert not errors
    return [entry for _, entry in pairs]


def test_numeric_forms_pair_with_their_titles(tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nExercise 2 makes this concrete,\n"
                        "and exercises 1 and 3 frame it.\n")
    assert entries(tmp_path, md) == [
        "Chapters/Observer\tObserver\t2\tA failing listener",
        "Chapters/Observer\tObserver\t1\tA minimal pair",
        "Chapters/Observer\tObserver\t3\tTwo views",
    ]


def test_reference_reports_the_line_it_sits_on(tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nA first line,\n"
                        "then (see Exercise 3).\n")
    [ref] = er.references(md)
    assert (ref.line, ref.number, ref.phrase) == (4, 3, "Exercise 3")


def test_fenced_code_headings_and_the_verb_are_skipped(
        tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\n## Exercise 2 in a heading\n\n"
                        "```python\n# Exercise 2: a comment\n```\n\n"
                        "The second exercises `NotInteresting`.\n")
    assert entries(tmp_path, md) == []


def test_ordinal_names_a_number(tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nThe second exercise does it.\n")
    assert entries(tmp_path, md) == [
        "Chapters/Observer\tObserver\t2\tA failing listener"]


def test_previous_and_next_resolve_from_the_exercise_item(
        tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nThe next exercise is not one.\n\n"
                        "## Exercises\n\n"
                        "1.  Write a pair.\n"
                        "    The next exercise breaks it.\n"
                        "2.  Break it.\n"
                        "3.  Modify the previous exercise.\n")
    assert entries(tmp_path, md) == [
        "Chapters/Observer\tObserver\t2\tA failing listener",
        "Chapters/Observer\tObserver\t2\tA failing listener",
    ]


def test_previous_resolves_from_the_solutions_section(
        tmp_path: Path) -> None:
    book(tmp_path, "# Observer\n")
    sol = tmp_path / "Solutions" / f"{CHAPTER}.md"
    assert entries(tmp_path, sol) == [
        "Solutions/Observer\tObserver\t2\tA failing listener",
        "Solutions/Observer\tObserver\t1\tA minimal pair",
    ]


@pytest.mark.parametrize("sentence", [
    f"as exercise 3 of [Factory]({OTHER}.md#exercises) shows.",
    f"The third exercise in [Factory](../Chapters/{OTHER}.md) shows it.",
    f"[Factory]({OTHER}.md)'s exercise 3 shows it.",
    f"(that chapter's [Simple]({OTHER}.md#simple) describes it,\n"
    "and its exercise 3 writes it).",
])
def test_a_tied_link_retargets_the_reference(
        tmp_path: Path, sentence: str) -> None:
    md = book(tmp_path, f"# Observer\n\n{sentence}\n")
    assert entries(tmp_path, md) == [
        "Chapters/Observer\tFactory\t3\t"
        "Recursing through `__subclasses__()`"]


def test_a_link_that_only_shares_the_sentence_does_not_retarget(
        tmp_path: Path) -> None:
    md = book(tmp_path, f"# Observer\n\n[Factory]({OTHER}.md#x) covers "
                        "the rule, as exercise 1 does here.\n")
    assert entries(tmp_path, md) == [
        "Chapters/Observer\tObserver\t1\tA minimal pair"]


def test_combined_heading_answers_both_numbers(tmp_path: Path) -> None:
    book(tmp_path, "# Observer\n")
    assert er.titles(tmp_path, OTHER)[2] == "A `Triangle` in both styles"


def test_missing_exercise_is_an_error_no_baseline_excuses(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    book(tmp_path, "# Observer\n\nExercise 9 covers it.\n")
    base = tmp_path / "base.txt"
    args = ["--root", str(tmp_path), "--baseline", str(base)]
    assert er.main([*args, "--accept"]) == 1
    assert er.main(args) == 1
    assert "has no exercise 9" in capsys.readouterr().out


def test_neighboring_chapter_reference_is_an_error(
        tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\n"
                        "The previous chapter's second exercise did it.\n")
    _, errors = er.resolve(list(er.references(md)), tmp_path)
    assert [e.line for e in errors] == [3]
    assert "name the chapter with a link" in errors[0].message


def test_inserting_an_exercise_flags_every_later_reference(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    chapter = ("# Observer\n\nExercise 1 builds the pair.\n"
               "Exercise 2 makes the failure concrete.\n")
    book(tmp_path, chapter)
    base = tmp_path / "base.txt"
    args = ["--root", str(tmp_path), "--baseline", str(base)]
    assert er.main([*args, "--accept"]) == 0
    assert er.main(args) == 0
    book(tmp_path, chapter, SOLUTIONS.replace(
        "## 2. A failing listener",
        "## 2. The pull model\n\nText.\n\n## 3. A failing listener",
    ).replace("## 3. Two views", "## 4. Two views"))
    capsys.readouterr()
    assert er.main(args) == 1
    out = capsys.readouterr().out
    new = [line for line in out.splitlines() if line.startswith("NEW")]
    # The Solutions file's "previous exercise" moved from section 3 to
    # section 4, so it has a new neighbor and fires too.
    assert len(new) == 2
    assert '"Exercise 2" -> Observer 2. The pull model' in new[0]
    assert '"previous exercise" -> Observer 3. A failing' in new[1]
    assert "GONE  Chapters/Observer: Observer 2. A failing" in out


def test_baseline_ignores_line_numbers_and_chapter_numbers(
        tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nExercise 2 covers it.\n")
    before = entries(tmp_path, md)
    md.write_text("# Observer\n\nA new paragraph.\n\n"
                  "Exercise 2 covers it.\n", encoding="utf-8")
    assert entries(tmp_path, md) == before
    for tree in ("Chapters", "Solutions"):
        old = tmp_path / tree / f"{CHAPTER}.md"
        old.rename(old.with_name("31_Behavior--Observer.md"))
    moved = tmp_path / "Chapters" / "31_Behavior--Observer.md"
    assert entries(tmp_path, moved) == before


def test_paths_scope_the_baseline(tmp_path: Path) -> None:
    md = book(tmp_path, "# Observer\n\nExercise 2 covers it.\n")
    base = tmp_path / "base.txt"
    args = ["--root", str(tmp_path), "--baseline", str(base)]
    assert er.main([*args, "--accept"]) == 0
    other = tmp_path / "Chapters" / f"{OTHER}.md"
    scoped = er.scoped(er.load_baseline(base), [other])
    assert not scoped
    assert sum(er.scoped(er.load_baseline(base), [md]).values()) == 1

