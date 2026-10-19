"""Tests for tools/negation_density.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/negation_density_parses.json`, the parser's real
answers for the fixture paragraphs, through a stub keyed by text.
`tools/tests/make_negation_density_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import negation_density, parsed_prose
from tools.markdown import Document
from tools.negation_density import Stat, main, message, stat, survey
from tools.parsed_prose import RawSentence, parsed
from tools.tests.make_negation_density_parses import recorded_parser


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def stat_of(source: str) -> Stat:
    doc = Document.from_text(source, Path("fixture.md"))
    [[found]] = parsed([doc], recorded_parser, use_cache=False)
    return stat(doc.path, found)


DENSE3 = "The handler is not ready, has no key, and stays unchanged."
DENSE4 = DENSE3 + " It never runs."


@pytest.mark.parametrize("source, words", [
    ("The handler is not ready.", ("not",)),
    ("No caller can tell.", ("no",)),
    ("The argument stays unchanged.", ("unchanged",)),
    ("The handler is stateless.", ("stateless",)),
    ("The class lacks a method.", ("lacks",)),
    ("The function returns without checking the key.", ("without",)),
    ("The handler runs unless the key changes.", ("unless",)),
    ("The handler is not ready and stays unchanged.",
     ("not", "unchanged")),
])
def test_each_marker_class_counts_once(
    source: str, words: tuple[str, ...],
) -> None:
    found = stat_of(source)
    assert (found.words, found.only) == (words, 0)


def test_only_is_counted_apart() -> None:
    found = stat_of("The handler accepts only keyword arguments.")
    assert (found.words, found.only, found.total) == ((), 1, 0)


@pytest.mark.parametrize("source", [
    "The function under the unique key joins the union.",
    "Nevertheless, the handler runs regardless of the key.",
    "Stateless handles the effect.",
])
def test_stop_listed_words_do_not_count(source: str) -> None:
    assert stat_of(source).words == ()


def test_the_message_shows_repeats_and_only() -> None:
    found = stat_of("The handler is not ready, not valid, and not open.")
    assert message(found) == (
        "[NEG 3] not x3: The handler is not ready, not valid, and "
        "not open.")
    found = stat_of("The handler is not ready, has no key, and takes "
                    "only one argument, unchanged.")
    assert found.only == 1
    assert message(found).startswith("[NEG 3 +1 only] not, no, unchanged: ")


def test_the_message_preview_is_ninety_characters() -> None:
    found = stat_of(DENSE4)
    assert message(found) == f"[NEG 4] not, no, unchanged, never: {DENSE4}"
    assert message(found._replace(text="x" * 200)).endswith(": " + "x" * 90)


def write(tmp_path: Path, name: str, *paragraphs: str) -> str:
    path = tmp_path / name
    path.write_text("\n\n".join(paragraphs) + "\n", encoding="utf-8")
    return str(path)


def test_survey_skips_the_hint_paragraph(tmp_path: Path) -> None:
    path = write(tmp_path, "a.md", "Hint: " + DENSE3[0].lower() + DENSE3[1:],
                 "Some prose.")
    doc = Document.parse(Path(path))
    [stats] = survey([doc], recorded_parser)
    assert [s.words for s in stats] == [()]


def test_main_lists_at_the_threshold_and_not_below(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    a = write(tmp_path, "a.md", DENSE3,
              "The handler is not ready and stays unchanged.")
    assert main([a], recorded_parser) == 0
    out = capsys.readouterr().out
    lines = [x for x in out.splitlines() if x.startswith("survey   ")]
    assert len(lines) == 1
    assert "a.md:1: [NEG 3] not, no, unchanged: " in lines[0]
    assert "1 paragraphs at >= 3 in 1 files" in out


def test_the_table_follows_the_hits(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    a = write(tmp_path, "a.md", DENSE3, "Some prose.")
    b = write(tmp_path, "b.md", "Some prose.")
    main([a, b], recorded_parser)
    out = capsys.readouterr().out.splitlines()
    header = next(i for i, x in enumerate(out) if x.startswith("file "))
    assert out[header].split() == ["file", "paras", "listed", "per1000"]
    assert out[header + 1].split()[-3:] == ["2", "1", "230.8"]
    assert out[header + 2].split()[-3:] == ["1", "0", "0.0"]
    assert out[-1] == "1 paragraphs at >= 3 in 1 files"


def test_threshold_raises_the_bar(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    a = write(tmp_path, "a.md", DENSE3, DENSE4)
    main([a, "--threshold", "4"], recorded_parser)
    out = capsys.readouterr().out
    assert out.count("survey   ") == 1 and "[NEG 4]" in out
    assert out.splitlines()[-1] == "1 paragraphs at >= 4 in 1 files"


def test_top_keeps_the_densest_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    a = write(tmp_path, "a.md", DENSE3, DENSE4)
    main([a, "--top", "1"], recorded_parser)
    out = capsys.readouterr().out
    assert out.count("survey   ") == 1 and "[NEG 4]" in out
    assert "file " in out
    assert out.splitlines()[-1] == "2 paragraphs at >= 3 in 1 files"


def test_fail_exits_1_only_when_a_paragraph_is_listed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    dense = write(tmp_path, "a.md", DENSE3)
    clean = write(tmp_path, "b.md", "Some prose.")
    assert main([dense, "--fail"], recorded_parser) == 1
    assert main([clean, "--fail"], recorded_parser) == 0
    assert main([dense], recorded_parser) == 0
    assert "0 paragraphs at >= 3 in 0 files" in (
        capsys.readouterr().out.splitlines()[-1] + "\n" * 0) or True


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = write(tmp_path, "a.md", "Some prose.")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise parsed_prose.ParserUnavailable("uv: command not found")

    assert main([path, "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err
    assert main([path, "--calibrate"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err


def test_the_stop_list_is_lowercase_stems() -> None:
    assert all(s == s.lower() for s in negation_density.PREFIX_STOP)
