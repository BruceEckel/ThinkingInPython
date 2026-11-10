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
    ADD_AFTER,
    ALL_RULES,
    JUDGED_SURVEY_RULES,
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
    monkeypatch.setattr(sentence_shapes, "SURVEY_BASELINE",
                        tmp_path / "survey.txt")


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
     "the pool hands out the same object.", ["AND", "SAME+NEW"]),
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
    ("The type checker reads the annotation and ignores which code runs first. Pyright accepts the read too.", ["ADD"]),
    ("Programmers have been bad at keeping objects inside that set. Constructing an object in an illegal state is too easy.", []),
    ("The copy shares the inner objects. It duplicates the outer list as well.", []),
    ("`drive()`, imported unchanged, answers a request yielded two generators deep the same way it answers one from `interview()`'s own body.", ["TWO"]),
    ("`drive()` is imported unchanged. The requests now come from `ask()`, one generator below `interview()`, and `yield from` passes each one up to the driver, so `drive()` sees the same `Question`s it saw in `interview_generator.py`.", []),
    ("Use a `set` rather than a `list` for membership tests.", []),
    ("At `[2]`, the same `yield` raises `GeneratorExit`.", ["SAME"]),
    ("The same directory reaches pytest through `pythonpath` in `pyproject.toml`.", ["SAME", "SAME+NEW"]),
    ("Alternative constructors need `Self` for the same reason `bump()` does.", []),
    ("`register()` returns the same `cls` it received, so the name `Espresso` refers to the original class.", []),
    ("The code runs the same with or without them.", []),
    ("A finished f-string is a single `str` in which the values have merged into the literal text. `safe()` uses the same separation to check each value.", ["SAME+NEW"]),
    ("A `Template` keeps each value separate from the literal text. `safe()` uses the same separation.", ["SAME"]),
    ("The `# type: ignore` in `report` silences `ty`'s diagnostic for the same hazard.", ["SAME", "SAME+NEW"]),
    ("The `hash()` failure is a second symptom of the same shallowness.", ["SAME+NEW"]),
    ("`async`/`await` is the same machinery with a syntax that marks a function as one the event loop resumes.", ["SAME+NEW"]),
    ("An `if`/`isinstance()` chain gives the same exhaustiveness check as a `match`.", []),
    ("Every responder that filters by size writes the same comparison.", []),
    ("A pure call returns the same answer every time.", []),
    ("`expect()`, in the same file, prints through `report()` too.", ["SAME"]),
    ("That rejection is the same guarantee the `Result` type gives in Error Handling.", []),
    ("A generator yields a request and waits while the driver carries the request out.", ["PRT"]),
    ("A generator yields a request and waits while the driver carries out the request.", []),
    ("The driver carries it out.", []),
    ("`pickle` looks the class up as `shapes.Circle` and does not find it.", ["PRT"]),
    ("`pickle` looks `name` up in the module.", []),
    ("Gradual typing leaves the amount up to you.", []),
    ("The `Result` that `ask()` returns stops one level up.", []),
    ("`check()` rejects negatives but lets zero through.", []),
    ("The `finally` clause runs on every ending and turns the sensor off.", ["PRT"]),
    ("`close()` requires the generator to finish.", ["CAUS"]),
    ("The decorator lets the caller skip the check.", ["CAUS"]),
    ("`slots=True` makes `dataclass()` build a new class.", ["CAUS"]),
    ("The generator must finish.", []),
    ("It makes the check safe.", []),
    ("The pool needs a lock.", []),
    ("The class is required to define it.", []),
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
    assert set(RULES) == {"IMP", "COLON+AND", "PAIR", "AND+REL", "PRT"}
    assert set(SURVEY_RULES) == {
        "AND", "COLON", "ADD", "TWO", "CAN", "SAME", "SAME+NEW", "CAUS"}
    assert JUDGED_SURVEY_RULES == {"ADD", "SAME", "SAME+NEW", "TWO"}
    assert JUDGED_SURVEY_RULES <= set(SURVEY_RULES)


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
    assert "1 survey, 0 judged" in out and "0 new, 0 accepted" in out


SAME_A = ("The `hash()` failure is a second symptom of the same "
          "shallowness.\n")
SAME_B = ("`async`/`await` is the same machinery with a syntax that "
          "marks a function as one the event loop resumes.\n")


@pytest.fixture
def same_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> Path:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text(SAME_A, encoding="utf-8")
    return path


def test_same_new_hits_are_judged_in_their_own_baseline(
    same_setup: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = same_setup
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[SAME+NEW] shallowness:" in out
    assert "1 survey, 0 judged" in out
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 1, dropped 0" in capsys.readouterr().out
    text = sentence_shapes.SURVEY_BASELINE.read_text(encoding="utf-8")
    assert text.startswith(sentence_shapes.SURVEY_HEADER)
    assert len(sentence_shapes.load_baseline(
        sentence_shapes.SURVEY_BASELINE)) == 1
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "[SAME+NEW]" not in out and "0 survey, 1 judged" in out
    assert main([str(path), "--survey", "--all"], recorded_parser) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any(line.startswith("judged   ") and "[SAME+NEW]" in line
               for line in lines)


def test_a_rewritten_same_new_sentence_retires_its_entry(
    same_setup: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = same_setup
    main([str(path), "--survey-accept"], recorded_parser)
    capsys.readouterr()
    path.write_text(SAME_B, encoding="utf-8")
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert any(line.startswith("survey   ") and "machinery:" in line
               for line in out.splitlines())
    assert any(line.startswith("stale    ") and "shallowness:" in line
               for line in out.splitlines())
    assert "1 survey, 0 judged, 1 stale" in out
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 1, dropped 1 stale" in capsys.readouterr().out
    entries = sentence_shapes.load_baseline(
        sentence_shapes.SURVEY_BASELINE)
    assert len(entries) == 1
    assert "machinery:" in next(iter(entries))


def test_same_hits_are_judged_in_the_shared_baseline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("At `[2]`, the same `yield` raises `GeneratorExit`.\n",
                    encoding="utf-8")
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert any(line.startswith("survey   ") and "[SAME] At CODE" in line
               for line in out.splitlines())
    assert "1 survey, 0 judged" in out
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 1, dropped 0" in capsys.readouterr().out
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "[SAME]" not in out and "0 survey, 1 judged" in out
    assert main([str(path), "--survey", "--all"], recorded_parser) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any(line.startswith("judged   ") and "[SAME] " in line
               for line in lines)


@pytest.mark.parametrize("source, label", [
    ("It checks the declaration's type and ignores which code runs "
     "first. Pyright accepts the read too.\n", "ADD"),
    ("`drive()`, imported unchanged, answers a request yielded two "
     "generators deep the same way it answers one from "
     "`interview()`'s own body.\n", "TWO"),
])
def test_add_and_two_hits_are_judged_in_the_shared_baseline(
    source: str, label: str, tmp_path: Path,
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text(source, encoding="utf-8")
    tag = f"[{label}] "
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert any(line.startswith("survey   ") and tag in line
               for line in out.splitlines())
    assert "1 survey, 0 judged" in out
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 1, dropped 0" in capsys.readouterr().out
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert f"[{label}]" not in out and "0 survey, 1 judged" in out
    assert main([str(path), "--survey", "--all"], recorded_parser) == 0
    lines = capsys.readouterr().out.splitlines()
    assert any(line.startswith("judged   ") and tag in line
               for line in lines)


def test_a_sentence_with_both_same_rules_has_two_entries(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text("The same directory reaches pytest through "
                    "`pythonpath` in `pyproject.toml`.\n",
                    encoding="utf-8")
    assert main([str(path), "--survey"], recorded_parser) == 0
    assert "2 survey, 0 judged" in capsys.readouterr().out
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 2, dropped 0" in capsys.readouterr().out
    messages = [entry.split("\t", 1)[1] for entry in
                sentence_shapes.load_baseline(
                    sentence_shapes.SURVEY_BASELINE)]
    assert len(messages) == 2
    assert sum(m.startswith("[SAME] ") for m in messages) == 1
    assert sum(m.startswith("[SAME+NEW] directory: ")
               for m in messages) == 1
    assert main([str(path), "--survey"], recorded_parser) == 0
    assert "0 survey, 2 judged" in capsys.readouterr().out


def test_other_survey_rules_stay_unjudged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "a.md"
    path.write_text(HANDLER, encoding="utf-8")
    assert main([str(path), "--survey-accept"], recorded_parser) == 0
    assert "added 0, dropped 0" in capsys.readouterr().out
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "[AND] The handler nearest" in out
    assert "1 survey, 0 judged" in out


def test_default_run_prints_nothing_about_the_survey(
    same_setup: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    main([str(same_setup), "--survey-accept"], recorded_parser)
    capsys.readouterr()
    assert main([str(same_setup)], recorded_parser) == 0
    out = capsys.readouterr().out
    assert "survey" not in out and "judged" not in out
    assert out.endswith("0 new, 0 accepted\n")


ADD_P1 = ("It checks the declaration's type and ignores which code "
          "runs first. Pyright accepts the read too.\n")
ADD_P2 = ("The type checker reads the annotation and ignores which "
          "code runs first. Pyright accepts the read too.\n")


def test_an_add_message_carries_the_sentence_before_it() -> None:
    doc = Document.from_text(ADD_P1, Path("fixture.md"))
    [found] = list(find([doc], recorded_parser))
    assert found.message == (
        "[ADD] Pyright accepts the read too." + ADD_AFTER
        + "It checks the declaration's type and ignores which code "
        "runs first.")
    doc = Document.from_text(
        "`drive()`, imported unchanged, answers a request yielded two "
        "generators deep the same way it answers one from "
        "`interview()`'s own body.\n", Path("fixture.md"))
    [two] = list(find([doc], recorded_parser))
    assert two.message.startswith("[TWO] ")
    assert ADD_AFTER not in two.message


def test_an_edit_to_the_sentence_before_retires_an_add_entry(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sentence_shapes, "BASELINE", tmp_path / "base.txt")
    path = tmp_path / "a.md"
    path.write_text(ADD_P1, encoding="utf-8")
    assert main([str(path), "--survey-accept"],
                recorded_parser) == 0
    assert "added 1" in capsys.readouterr().out
    path.write_text(ADD_P2, encoding="utf-8")
    assert main([str(path), "--survey"], recorded_parser) == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert any(line.startswith("survey   ")
               and "| after: The type checker reads" in line
               for line in lines)
    assert any(line.startswith("stale    ")
               and "| after: It checks" in line for line in lines)
    assert "1 survey, 0 judged, 1 stale" in out
    assert main([str(path), "--survey-accept"],
                recorded_parser) == 0
    assert "added 1, dropped 1 stale" in capsys.readouterr().out
