"""Tests for tools/reading_level.py, on in-memory documents and tmp files."""

import math
from pathlib import Path
import pytest
from tools import reading_level
from tools.markdown import Document
from tools.reading_level import (
    Counts,
    DictionaryUnavailable,
    code_units,
    coleman_liau,
    flesch_kincaid,
    heuristic,
    load_table,
    main,
    read,
    report,
    smog,
    syllables,
    total,
)


@pytest.fixture(autouse=True)
def isolated_table(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the generated table at a tmp file so the book's is unused."""
    path = tmp_path / "overrides.txt"
    monkeypatch.setattr(reading_level, "OVERRIDES", path)
    return path


def doc(text: str) -> Document:
    return Document.from_text(text, Path("fixture.md"))


def counted(text: str, mode: str = "words") -> Counts:
    return total(s.counts for s in read(doc(text), mode))


def word_count(text: str, mode: str = "words") -> int:
    return counted(text, mode).words


def test_flesch_kincaid_by_hand() -> None:
    c = Counts(words=100, sentences=5, syllables=150)
    # 0.39 * 20 + 11.8 * 1.5 - 15.59
    assert flesch_kincaid(c) == pytest.approx(9.91)


def test_smog_by_hand() -> None:
    c = Counts(words=300, sentences=30, polysyllables=16)
    # 1.0430 * sqrt(16 * 30 / 30) + 3.1291
    assert smog(c) == pytest.approx(1.0430 * 4 + 3.1291)


def test_coleman_liau_by_hand() -> None:
    c = Counts(words=100, sentences=5, letters=450)
    # 0.0588 * 450 - 0.296 * 5 - 15.8
    assert coleman_liau(c) == pytest.approx(9.18)


def test_scores_of_nothing_are_zero() -> None:
    empty = Counts()
    assert flesch_kincaid(empty) == 0.0
    assert smog(empty) == 0.0
    assert coleman_liau(empty) == 0.0


@pytest.mark.parametrize("word, count", [
    ("cat", 1), ("table", 2), ("while", 1), ("file", 1), ("module", 2),
    ("example", 3), ("wanted", 2), ("makes", 1), ("boxes", 2), ("the", 1),
    # The rules added after calibration against CMUdict.
    ("value", 2), ("handled", 2), ("carries", 2), ("handles", 2),
    ("actual", 3), ("evaluate", 4), ("algorithm", 4), ("supplied", 2),
])
def test_heuristic(word: str, count: int) -> None:
    assert heuristic(word) == count


def test_syllables_of_compounds_and_possessives() -> None:
    assert syllables("keyword-only") == 4
    assert syllables("computer's") == 3
    assert syllables("Don’t") == 1


def test_lookup_order(isolated_table: Path) -> None:
    isolated_table.write_text("# note\nmakes 2\ncat 3\n", encoding="utf-8")
    assert syllables("makes") == 2
    assert syllables("Cat") == 3
    assert syllables("namespace") == 2


def test_missing_table_is_empty(tmp_path: Path) -> None:
    assert load_table(tmp_path / "absent.txt") == {}


def test_hyphenated_compound_is_one_word() -> None:
    assert word_count("A keyword-only argument.") == 3


def test_number_is_no_word() -> None:
    assert word_count("Python 3.15 arrived in 2026.") == 3


def test_apostrophe_form_is_one_word() -> None:
    assert word_count("I don't know.") == 3


def test_link_text_is_read_and_the_url_is_not() -> None:
    assert word_count("See [the guide](http://x.y/zzz) now.") == 4


def test_image_and_footnote_reference_count_nothing() -> None:
    assert word_count("![a picture](pic.png) Hello there[^note].") == 2


def test_skipped_blocks_contribute_nothing() -> None:
    text = "\n".join([
        "# A heading with words",
        "",
        "```python",
        "# a comment inside the fence",
        "```",
        "",
        "> A quoted statement here.",
        "",
        "| a | b |",
        "|---|---|",
        "| cell | text |",
        "",
        "Real prose.",
        "#: output marker words",
    ])
    assert word_count(text) == 2


def test_list_items_are_read() -> None:
    c = counted("- Apples are red\n- Pears are green\n")
    assert (c.words, c.sentences) == (6, 2)


def test_em_dash_separates_words() -> None:
    assert word_count("One--two---three and four—five.") == 6


def test_code_span_words_mode() -> None:
    units = [u for s in read(doc("Call `StopIteration` now."), "words")
             for u in s.units]
    assert [u.syllables for u in units] == [1, 5, 1]
    assert units[1].letters == 13


def test_snake_case_identifier() -> None:
    (unit,) = code_units("`validate_output`", "words")
    assert unit.parts == ("validate", "output")
    assert unit.syllables == 5
    (dunder,) = code_units("`__post_init__`", "words")
    assert dunder.parts == ("post", "init")
    assert dunder.syllables == 3


def test_acronym_run_splits_before_a_capitalized_word() -> None:
    (unit,) = code_units("`HTTPServer`", "words")
    assert unit.parts == ("http", "server")


def test_span_with_two_identifiers_is_two_words() -> None:
    assert word_count("Try `foo(bar)` first.") == 4


def test_span_without_identifier_is_no_word() -> None:
    assert word_count("See `[1]` and `42` and `#:` now.") == 4
    assert code_units("`42`", "words") == []


def test_digits_split_an_identifier() -> None:
    (unit,) = code_units("`py3k`", "words")
    assert unit.parts == ("py", "k")


def test_code_it_mode_counts_every_span_as_it() -> None:
    text = "Call `StopIteration` now."
    assert word_count(text, "it") == 3
    assert counted(text, "words").syllables == 7
    assert counted(text, "it").syllables == 3
    assert counted(text, "it").letters == 4 + 2 + 3


def sentences_of(text: str) -> list[tuple[int, str]]:
    return [(s.line, s.text) for s in read(doc(text), "words")]


def test_two_sentences_on_one_line() -> None:
    assert [t for _, t in sentences_of("One thing. Two things.")] == [
        "One thing.", "Two things."]


def test_one_sentence_over_three_lines() -> None:
    found = sentences_of("A sentence that\nwraps over\nthree lines.")
    assert found == [(1, "A sentence that wraps over three lines.")]


def test_abbreviation_inside_a_sentence() -> None:
    found = sentences_of("Use a tool, e.g. a linter, to check.")
    assert len(found) == 1


def test_decimal_inside_a_sentence() -> None:
    found = sentences_of("Python 3.15 is new. Done now.")
    assert [t for _, t in found] == ["Python 3.15 is new.", "Done now."]


def test_paragraph_ending_on_a_colon_is_one_sentence() -> None:
    assert len(sentences_of("Here is the list:")) == 1


def test_fragment_list_item_is_a_sentence() -> None:
    assert len(sentences_of("- Functions, classes, objects")) == 1


def test_line_of_a_sentence_that_starts_mid_paragraph() -> None:
    text = "# Title\n\nAlpha one.\nBeta two. Gamma\nthree four."
    assert sentences_of(text) == [
        (3, "Alpha one."), (4, "Beta two."), (4, "Gamma three four.")]


SECTIONS = """\
Opening words here.

## First `Thing` {#first}

Body one.

### Sub

Body two.

```text
## not a heading
```

## Second

Body three.
"""


def test_sections() -> None:
    r = report(doc(SECTIONS), "words")
    assert list(r.sections) == ["(opening)", "First Thing", "Second"]
    assert [c.sentences for c in r.sections.values()] == [1, 2, 1]


def test_section_without_sentences_has_no_row() -> None:
    r = report(doc("## Empty\n\n## Full\n\nSome prose.\n"), "words")
    assert list(r.sections) == ["Full"]


def test_file_total_is_the_sum_of_sections() -> None:
    r = report(doc(SECTIONS), "words")
    assert r.whole == total(r.sections.values())
    assert r.whole.sentences == 4


def write(tmp_path: Path, name: str, text: str) -> str:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def output(capsys: pytest.CaptureFixture[str]) -> list[str]:
    return capsys.readouterr().out.splitlines()


def test_main_prints_header_and_whole_file_row(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", SECTIONS)
    assert main([path]) == 0
    lines = output(capsys)
    assert lines[1].split() == [
        "section", "words", "sent", "w/sent", "syl/w", "FK", "SMOG", "C-L"]
    assert lines[2].lstrip().startswith("(whole file)")
    assert [ln.split()[0] for ln in lines[3:6]] == [
        "(opening)", "First", "Second"]
    assert "  longest sentences" in lines


def test_longest_zero_prints_no_list(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", SECTIONS)
    main([path, "--longest", "0"])
    assert "longest sentences" not in "\n".join(output(capsys))


def test_longest_sentences_are_ranked_by_words(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", "Short one.\n\nA much longer sentence "
                 "than the other one.\n")
    main([path, "--longest", "1"])
    lines = output(capsys)
    at = lines.index("  longest sentences")
    assert "a.md:3: A much longer sentence" in lines[at + 1]
    assert lines[at + 1].split()[0] == "8"


def test_summary_prints_only_the_table(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", SECTIONS)
    main([path, "--summary"])
    lines = output(capsys)
    assert lines[0].split()[0] == "file"
    assert "(whole file)" not in "\n".join(lines)
    assert lines[-1].startswith("1 files, ")
    assert "Flesch-Kincaid" in lines[-1]


HARD = ("Instrumentation notwithstanding characteristically "
        "extraordinarily.\n")


def test_target_marks_rows_and_counts_sections(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    text = "## Easy\n\nI am at it.\n\n## Hard\n\n" + HARD
    path = write(tmp_path, "a.md", text)
    assert main([path, "--target", "8", "--longest", "0"]) == 0
    lines = output(capsys)
    easy = next(ln for ln in lines if ln.startswith("  Easy"))
    hard = next(ln for ln in lines if ln.startswith("  Hard"))
    assert hard.endswith(" >")
    assert not easy.endswith(" >")
    assert lines[-1] == "1 of 2 sections above grade 8"


def test_fail_exits_one_above_the_target(tmp_path: Path) -> None:
    path = write(tmp_path, "a.md", HARD)
    assert main([path, "--target", "8", "--fail"]) == 1
    assert main([path, "--target", "100", "--fail"]) == 0
    assert main([path, "--fail"]) == 0


def test_two_files_give_a_summary_hardest_first(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    easy = write(tmp_path, "easy.md", "I am at it.\n")
    hard = write(tmp_path, "a_file_name_longer_than_the_section_column"
                 "_is_wide.md", HARD)
    main([easy, hard, "--longest", "0"])
    lines = output(capsys)
    at = next(i for i, ln in enumerate(lines) if ln.startswith("  file"))
    # The summary's path column fits the longest path, uncut.
    assert "_is_wide.md " in lines[at + 1]
    assert "easy.md " in lines[at + 2]
    assert len(lines[at]) == len(lines[at + 1]) == len(lines[at + 2])
    assert lines[-1].startswith("2 files, ")


def test_file_without_prose(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty = write(tmp_path, "empty.md", "# Only a heading\n")
    full = write(tmp_path, "full.md", "Some words.\n")
    main([empty, full])
    text = "\n".join(output(capsys))
    assert "  no prose" in text
    assert text.splitlines()[-1].startswith("1 files, ")


def test_code_mode_changes_the_counts(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", "Call `StopIteration` now.\n")
    main([path, "--longest", "0"])
    assert "2.33" in "\n".join(output(capsys))
    main([path, "--longest", "0", "--code", "it"])
    assert "1.00" in "\n".join(output(capsys))


DICTIONARY = {"she": 1, "makes": 2, "tables": 2}


def fake_lookup(words: list[str]) -> dict[str, int]:
    return {w: DICTIONARY[w] for w in words if w in DICTIONARY}


def test_calibrate_prints_the_report(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = write(tmp_path, "a.md", "She makes tables. Xyzzy makes tables.\n")
    assert main(["--calibrate", path], lookup=fake_lookup) == 0
    lines = output(capsys)
    assert lines[0] == "4 distinct words, 6 tokens in 1 files"
    assert lines[1].startswith("the dictionary has 3 of them (")
    assert lines[2].startswith("heuristic alone: ")
    assert lines[3].startswith("with HAND and the table: ")
    assert "missing from the table: 1" in lines
    assert "       2  makes  heuristic 1, dictionary 2" in lines
    assert "stale in the table: 0" in lines
    assert "not in the dictionary, most frequent first:" in lines
    assert "       1  xyzzy  2" in lines


def test_calibrate_write_then_calibrate_again(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        isolated_table: Path) -> None:
    path = write(tmp_path, "a.md", "She makes tables.\n")
    assert main(["--calibrate", "--write", path], lookup=fake_lookup) == 0
    assert output(capsys)[0].startswith("wrote 1 entries to ")
    body = isolated_table.read_text(encoding="utf-8")
    assert "\nmakes 2\n" in body
    assert "tables" not in body.replace("tables.", "")
    assert body.startswith("# ")
    assert "\r" not in body
    main(["--calibrate", path], lookup=fake_lookup)
    lines = output(capsys)
    assert "missing from the table: 0" in lines
    assert "stale in the table: 0" in lines


def test_write_keeps_words_of_other_paths_and_drops_stale_ones(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        isolated_table: Path) -> None:
    first = write(tmp_path, "a.md", "She makes tables.\n")
    main(["--calibrate", "--write", first], lookup=fake_lookup)
    # "tables 3" is stale: the heuristic and the dictionary both say 2.
    isolated_table.write_text(
        isolated_table.read_text(encoding="utf-8") + "tables 3\n",
        encoding="utf-8")
    load_table.cache_clear()
    second = write(tmp_path, "b.md", "She sat.\n")
    main(["--calibrate", "--write", second], lookup=fake_lookup)
    assert output(capsys)[-1].startswith("wrote 1 entries to ")
    body = isolated_table.read_text(encoding="utf-8")
    assert "\nmakes 2\n" in body
    assert "\ntables " not in body


def test_unreadable_dictionary_answer_is_unavailable(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class Done:
        returncode = 0
        stdout = "not json"
        stderr = ""

    monkeypatch.setattr(reading_level.subprocess, "run",
                        lambda *args, **kwargs: Done())
    with pytest.raises(DictionaryUnavailable, match="unreadable answer"):
        reading_level.dictionary(["table"])


def test_stale_table_entry(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        isolated_table: Path) -> None:
    isolated_table.write_text("makes 1\n", encoding="utf-8")
    path = write(tmp_path, "a.md", "She makes tables.\n")
    main(["--calibrate", path], lookup=fake_lookup)
    lines = output(capsys)
    assert "stale in the table: 1" in lines
    assert "missing from the table: 1" in lines


def test_dictionary_unavailable_exits_zero(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def broken(words: list[str]) -> dict[str, int]:
        raise DictionaryUnavailable("uv: command not found")

    path = write(tmp_path, "a.md", "Some words here.\n")
    assert main(["--calibrate", path], lookup=broken) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.strip() == (
        "reading_level: dictionary unavailable (uv: command not found); "
        "nothing calibrated")


def test_write_without_calibrate_is_an_error(tmp_path: Path) -> None:
    path = write(tmp_path, "a.md", "Some words here.\n")
    with pytest.raises(SystemExit) as info:
        main(["--write", path])
    assert info.value.code == 2


def test_scores_use_the_documented_formulas() -> None:
    c = counted("The cat sat. A dog ran.")
    assert (c.words, c.sentences, c.syllables) == (6, 2, 6)
    assert flesch_kincaid(c) == pytest.approx(
        0.39 * 3 + 11.8 * 1 - 15.59)
    assert smog(c) == pytest.approx(3.1291)
    assert math.isfinite(coleman_liau(c))
