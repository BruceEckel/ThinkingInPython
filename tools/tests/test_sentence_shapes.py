"""Tests for tools/sentence_shapes.py, on recorded spaCy parses.

The parser is a throwaway-environment subprocess, so these tests use
`tools/tests/data/sentence_shapes_parses.json`, the parser's real
answers for the fixture paragraphs, through a stub keyed by text.
`tools/tests/make_sentence_shapes_parses.py` regenerates the file.
"""

from pathlib import Path
import pytest
from tools import parsed_prose, sentence_shapes
from tools.markdown import Document
from tools.parsed_prose import Paragraph, RawSentence, parsed
from tools.sentence_shapes import (
    CALIBRATION_EXAMPLES,
    ALL_RULES,
    RULES,
    SURVEY_RULES,
    colon_clause,
    colon_units,
    find,
    main,
    merge,
    shapes,
)
from tools.tests.make_sentence_shapes_parses import recorded_parser


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", tmp_path / "parses")


def paragraph(source: str) -> Paragraph:
    doc = Document.from_text(source, Path("fixture.md"))
    [[found]] = parsed([doc], recorded_parser, use_cache=False)
    return found


def rules(source: str) -> list[str]:
    return [rule for rule, _ in shapes(paragraph(source))]


@pytest.mark.parametrize("source, expected", [
    ("Remove `frozen=True` and the pattern fails.", ["IMP"]),
    ("Forget the new argument at a call and `ty` reports "
     "a `missing-argument`.", ["IMP"]),
    ("If you remove `frozen=True`, the pattern fails.", []),
    ("Try the operation and handle the exception.", []),
    ("Run `ty` and read the error it reports.", []),
    ("The handler reads the key, and it stores the entry.", []),
    ("A `@dataclass` `Thermometer` has no list of listeners, and "
     "`subscribe()` raises an `AttributeError`.", ["AND"]),
    ("The design has three parts: an `Observer` interface, a `Subject` "
     "base class, and a `notify()` method.", []),
    ("The call prints this: `hello`.", []),
    ("The check has one limit: it reads literal text.", []),
    ("The prediction: the lease returns the item.", ["COLON"]),
    ("Remove `frozen=True` and confirm the program runs the same "
     "way while the type checker reports nothing.", []),
    ("Write a test in which the first responder fails and the second "
     "still records its notification.", []),
    ("Then ask what holds the callback, and what that means for the "
     "reference count.", []),
    ("Explain both failures, and why an intermediate kick avoids "
     "them.", []),
    ("Confirm that reading `x` several times builds nothing, and that "
     "the first `y` reports the count.", []),
    ("Then say what you gave up, and whether `Foo` should be a "
     "subclass of `Bar`.", []),
    ("Three tests check what the lease guarantees: the item leaves "
     "the pool, it comes back when the block raises an exception, and "
     "the pool hands out the same object.", ["AND"]),
    ("This technique is *dependency injection*: the caller hands the "
     "function its dependencies, and the function fetches nothing on "
     "its own.", ["AND", "COLON+AND"]),
    ("The handler nearest the Effect answers first, and the outer one "
     "handles the requests that remain.", ["AND"]),
    ("Python supplies `self` only when the lookup finds the function "
     "on the class: a function stored there is a descriptor, and "
     "reading it through an instance binds that instance.",
     ["COLON+AND"]),
    ("Hint: Remove `frozen=True` and the pattern fails.", []),
    ("The problem appears whenever the producer keeps state between "
     "values and the consumer has a loop of its own.", ["PAIR"]),
    ("The problem appears whenever the producer keeps state from one "
     "value to the next while the consumer has a loop of its own.", []),
    ("`interview()` runs the same under both drivers and each returns "
     "the result.", ["AND", "PAIR"]),
    ("Both forms keep the result and the name.", []),
    ("A `break` at the match leaves both loops in one step and skips "
     "`else` along with them.", []),
    ("A call between the check and the use can reset that attribute.",
     ["CAN"]),
    ("`Temperature` has no `__dict__` to assign them, so neither the "
     "class nor the instance holds an `celsius`.", []),
    ("The third-party `more-itertools` package supplies one as "
     "`iterate(func, start)`, which produces `start`, `func(start)`, "
     "`func(func(start))`, and so on without end, and `toolz` has an "
     "`iterate()` of the same shape.", ["AND+REL"]),
    ("The third-party `more-itertools` package supplies one as "
     "`iterate(func, start)`, which produces `start`, `func(start)`, "
     "`func(func(start))`, and so on without end. `toolz` has an "
     "`iterate()` of the same shape.", []),
    ("Intro paragraph.", []),
    ("A closure keeps its captured variables between calls, but each call runs its body from the top. The generator keeps its place as well, so a loop in progress survives.", ["ADD"]),
    ("A closure keeps its captured variables between calls, but each call runs its body from the top. The generator keeps its locals and its place in the body, so a loop in progress survives.", []),
    ("It checks the declaration's type and ignores which code runs first. Pyright accepts the read too.", ["ADD"]),
    ("Programmers have been bad at keeping objects inside that set. Constructing an object in an illegal state is too easy.", []),
    ("The copy shares the inner objects. It duplicates the outer list as well.", []),
    ("`drive()`, imported unchanged, answers a request yielded two generators deep the same way it answers one from `interview()`'s own body.", ["TWO"]),
    ("`drive()` is imported unchanged. The requests now come from `ask()`, one generator below `interview()`, and `yield from` passes each one up to the driver, so `drive()` sees the same `Question`s it saw in `interview_generator.py`.", []),
    ("Use a `set` rather than a `list` for membership tests.", []),
])
def test_rules(source: str, expected: list[str]) -> None:
    assert rules(source) == expected


def test_a_colon_ended_sentence_merges_with_the_next() -> None:
    lead = paragraph("The rule has a limit:")
    tail = paragraph(
        "A function is a descriptor, and reading it binds that instance.")
    assert colon_clause(lead.sentences[0]) is None
    joined_up = merge(lead.sentences[0], tail.sentences[0])
    assert colon_clause(joined_up) == "COLON+AND"
    assert [t.i for t in joined_up.tokens] == list(
        range(len(lead.sentences[0].tokens) + len(tail.sentences[0].tokens)))
    both = Paragraph(lead.path, lead.text + " " + tail.text,
                     lead.lines + [1] + tail.lines,
                     lead.sentences + tail.sentences)
    assert len(colon_units(both)) == 1


def test_the_reported_line_is_the_sentences_first_character() -> None:
    doc = Document.from_text(
        "Intro paragraph.\n\nThe handler nearest the Effect answers "
        "first,\nand the outer one handles the requests that remain.\n",
        Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.line == 3
    assert found.message == (
        "[AND] The handler nearest the Effect answers first, and the "
        "outer one handles the requests that remain.")


def test_calibration_examples_name_known_rules() -> None:
    assert {rule for rule, _, _ in CALIBRATION_EXAMPLES} <= set(ALL_RULES)
    assert set(RULES) == {"IMP", "COLON+AND", "PAIR", "AND+REL"}
    assert set(SURVEY_RULES) == {"AND", "COLON", "ADD", "TWO", "CAN"}


def test_main_reports_without_failing_and_accepts(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("Remove `frozen=True` and the pattern fails.\n",
                    encoding="utf-8")
    assert main([str(path)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "NEW" in out and "[IMP] Remove CODE and" in out
    assert "1 new, 0 accepted" in out
    assert main([str(path), "--fail"], recorded_parser) == 1
    capsys.readouterr()
    shown = sentence_shapes.display(path)
    sentence_shapes.write_baseline({
        sentence_shapes.key(
            shown, "[IMP] Remove CODE and the pattern fails.")})
    assert main([str(path), "--fail"], recorded_parser) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out
    assert main([str(path), "--accept"], recorded_parser) == 0
    assert "added 0, dropped 0" in capsys.readouterr().out


def test_a_missing_baseline_is_empty(tmp_path: Path) -> None:
    assert sentence_shapes.load_baseline(tmp_path / "none.txt") == set()


def test_main_survives_a_missing_parser(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text("Some prose.\n", encoding="utf-8")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise parsed_prose.ParserUnavailable("uv: command not found")

    assert main([str(path), "--fail"], gone) == 0
    assert "parser unavailable" in capsys.readouterr().err


HANDLER = ("The handler nearest the Effect answers first, and the outer "
           "one handles the requests that remain.\n")


def test_survey_rules_print_only_under_survey(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text(HANDLER, encoding="utf-8")
    assert main([str(path), "--fail"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey" not in out and "0 new, 0 accepted" in out
    assert main([str(path), "--survey", "--fail"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[AND] The handler nearest" in out
    assert "1 survey" in out and "0 new, 0 accepted" in out
