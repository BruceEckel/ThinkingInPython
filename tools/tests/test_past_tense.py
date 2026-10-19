"""Tests for tools/past_tense.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/past_tense_parses.json`, the parser's real answers
for the fixture texts, through a stub keyed by text.
`tools/tests/make_past_tense_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import parsed_prose, past_tense
from tools.markdown import Document
from tools.parsed_prose import Paragraph, RawSentence, parsed
from tools.past_tense import find, heading_lines, hits, main
from tools.tests.make_past_tense_parses import recorded_parser


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def paragraph(source: str) -> Paragraph:
    doc = Document.from_text(source, Path("fixture.md"))
    [[found]] = parsed([doc], recorded_parser, use_cache=False)
    return found


def shown(source: str) -> list[str]:
    return [hit.shown for hit in hits(paragraph(source))]


@pytest.mark.parametrize("source, expected", [
    ("One design served three jobs in this chapter.", ["served"]),
    ("One design serves three jobs in this chapter.", []),
    ("In every case the observer was a callable.", ["was"]),
    ("Python 3.12 added the type statement.", []),
    ("The 1994 book carried it into the mainstream.", []),
    ("PEP 695 added the type statement.", []),
    ("If the list were empty, the loop would stop.", []),
    ("The marker was rewritten by the gate.", ["was rewritten"]),
    ("The gate has rewritten the marker.", []),
    ('The message says "the key was marked read-only".', []),
    ("The loop ran first and the gate rewrote the marker.",
     ["ran", "rewrote"]),
    ("Hint: the loop ran first.", []),
    ("The loop runs first. The gate rewrote the marker.", ["rewrote"]),
])
def test_hits(source: str, expected: list[str]) -> None:
    assert shown(source) == expected


def test_a_paragraph_hit_is_labeled_past() -> None:
    [hit] = hits(paragraph("In every case the observer was a callable."))
    assert hit.label == "PAST"


def test_the_reported_line_is_the_sentences_first_character() -> None:
    doc = Document.from_text(
        "Some prose.\n\nThe loop runs first,\nand the gate\n"
        "rewrote the marker.\n", Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 3
    assert found.message == (
        "[PAST] rewrote: The loop runs first, and the gate rewrote the "
        "marker.")


def test_the_second_sentence_maps_to_its_own_line() -> None:
    doc = Document.from_text(
        "Some prose.\n\nThe loop runs first.\nThe gate rewrote the marker.\n",
        Path("fixture.md"))
    # The one-paragraph fixture text is "The loop runs first. The gate ..."
    [found] = list(find([doc], recorded_parser))
    assert found.line == 4
    assert found.message == "[PAST] rewrote: The gate rewrote the marker."


def test_a_heading_with_an_id_attribute_is_scanned() -> None:
    doc = Document.from_text(
        "Some prose.\n\n## What Stayed Constant {#stayed}\n",
        Path("fixture.md"))
    assert heading_lines(doc) == [(3, "What Stayed Constant")]
    [found] = list(find([doc], recorded_parser))
    assert found.line == 3
    assert found.message == "[PAST-HEADING] Stayed: What Stayed Constant"


def test_a_present_tense_heading_is_quiet() -> None:
    doc = Document.from_text("# What Stays Constant\n", Path("fixture.md"))
    assert list(find([doc], recorded_parser)) == []


def test_a_heading_inside_a_fence_is_ignored() -> None:
    doc = Document.from_text(
        "```python\n# What Stayed Constant\n```\n", Path("fixture.md"))
    assert heading_lines(doc) == []
    assert list(find([doc], recorded_parser)) == []


def test_main_reports_without_failing_and_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(past_tense, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("In every case the observer was a callable.\n",
                    encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "NEW" in out and "[PAST] was: In every case" in out
    assert "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    name = past_tense.display(path)
    past_tense.write_baseline({past_tense.key(
        name, "[PAST] was: In every case the observer was a callable.")})
    assert main([str(path), "--fail"], recorded_parser) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out
    assert main([str(path), "--all"], recorded_parser) == 0
    assert "accepted" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        main([str(path), "--accept"], recorded_parser)


def test_the_baseline_is_written_with_lf_endings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    base = tmp_path / "base.txt"
    monkeypatch.setattr(past_tense, "BASELINE", base)
    past_tense.write_baseline({"x\ty"})
    assert b"\r\n" not in base.read_bytes()
    assert past_tense.load_baseline() == {"x\ty"}


def test_a_stale_entry_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(past_tense, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")
    name = past_tense.display(path)
    past_tense.write_baseline({past_tense.key(
        name, "[PAST] was: Gone.")})
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "stale" in out and "0 new, 0 accepted, 1 stale" in out


def test_a_missing_baseline_is_empty(tmp_path: Path) -> None:
    assert past_tense.load_baseline(tmp_path / "none.txt") == set()


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise parsed_prose.ParserUnavailable("uv: command not found")

    assert main([str(path), "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
    assert main([str(path), "--calibrate"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err


def kinds(source: str) -> list[tuple[str, str]]:
    return [(hit.label, hit.shown) for hit in hits(paragraph(source))]


@pytest.mark.parametrize("source, expected", [
    ("One design served three jobs.", [("PAST", "served")]),
    ("The function the caller passed runs.", [("PAST-SUB", "passed")]),
    ("I began adding material.", []),
    ("If the list were empty, it stops.", []),
    ("The loop ran first and the gate rewrote the marker.",
     [("PAST", "ran"), ("PAST", "rewrote")]),
])
def test_the_split(source: str, expected: list[tuple[str, str]]) -> None:
    assert kinds(source) == expected


def test_survey_lines_print_only_under_survey(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(past_tense, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("The function the caller passed runs.\n",
                    encoding="utf-8")
    assert main([str(path), "--fail"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey" not in out and "0 new, 0 accepted" in out
    assert main([str(path), "--survey", "--fail"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[PAST-SUB] passed:" in out
    assert "0 new, 0 accepted" in out and "1 survey" in out
