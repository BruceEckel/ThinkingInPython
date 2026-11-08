"""Tests for tools/word_stutter.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.word_stutter import EXAMPLES, calibrate, find, main, stem


def hits(text: str, window: int = 3) -> list[tuple[int, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(f.line, f.message) for f in find(doc, window)]


def labels(text: str, window: int = 3) -> list[str]:
    return [m.split("]")[0] + "]" for _, m in hits(text, window)]


@pytest.mark.parametrize("text, label", [
    ("The next `next()` links that frame back.", "[CODE!]"),
    ("a function that finishes without a `return` returns `None`",
     "[CODE!]"),
    ("Neither type checker types `fib_table` as the `list[int]` it holds.",
     "[STEM~]"),
    ("Python cannot copy a generator: `copy.copy()` on a suspended "
     "generator raises `TypeError`.", "[CODE]"),
    ("the body resumes after `yield \"ready\"`, prints `resumed`, and "
     "leaves the inner `try`", "[CODE]"),
    ("times each variant five times", "[STEM="),
    ("a call that resumes it; resuming it resumes the body", "[STEM~]"),
])
def test_hit(text: str, label: str) -> None:
    assert any(lab.startswith(label) for lab in labels(text)), labels(text)


@pytest.mark.parametrize("text", [
    # A deliberate pair joined by a connective.
    "The yield channel and the return channel end in different places.",
    "The rat moves one cell at a time, one step per turn.",
    "It reads the words one by one.",
    # A sentence boundary stops the window.
    "Calling it creates the generator. Generator bodies run later.",
    # Link text is hidden.
    "[Iterators](22.md) covers iterators in full.",
    # Stopwords never pair.
    "the value of the value's type",
    # An expression span is not an identifier.
    "`yield from` yields each value",
    "`alpha got 1 and 2` and `beta` sit on adjacent lines",
    # Different stems.
    "the driver drives the generator",
    # Fenced code, headings, block quotes, markers, and tables are skipped.
    "```python\nnext(next_item)\n```",
    "# The next `next()`",
    "> the next `next()` still returns `2`",
    "#: next next",
    "| next | `next()` |",
])
def test_no_hit(text: str) -> None:
    assert not hits(text), hits(text)


JOB = ("The `for` loop primes each `job` and pairs it with its first "
       "request. When the job finishes, its `send()` raises "
       "`StopIteration`. The job is then dropped.")


def test_mixed_once_per_paragraph_at_first_occurrence() -> None:
    found = hits(JOB)
    assert [m.split("]")[0] for _, m in found] == ["[MIXED"]
    assert found[0][1].startswith("[MIXED] job / `job`: ")
    assert " | " in found[0][1]


@pytest.mark.parametrize("text", [
    # A class name beside its common noun is the book's idiom.
    "Every `Shape` draws itself, so the loop asks each shape to draw.",
    # A call or a dotted path is [CODE]'s business, not [MIXED]'s.
    "The driver calls `send()`. The send carries the answer in.",
    "`machine.state` is read later. The state is a record.",
    # Stopwords, keywords, and short spellings never pair.
    "`in` tests membership. The key is in the dict.",
    "The `class` statement runs. Then the class exists.",
    "A `match` tries each `case`. The first case that fits wins the match.",
    "`id` is a builtin. Its id changes.",
    # Two paragraphs are two scopes.
    "The `job` is primed.\n\nThe job then runs.",
])
def test_mixed_quiet(text: str) -> None:
    assert not [m for _, m in hits(text) if m.startswith("[MIXED]")], hits(text)


def test_mixed_reads_a_shadowed_builtin() -> None:
    text = "`next` and `action` are fields. The input decides the next state."
    assert [m.split("]")[0] for _, m in hits(text)] == ["[MIXED"]


def test_mixed_defers_to_a_code_pair() -> None:
    text = "Each `job` is a job the driver owns. The job runs later."
    found = [m.split("]")[0] for _, m in hits(text)]
    assert found == ["[CODE"]


def test_window_widens() -> None:
    text = ("`close()` returns the value the generator returned while "
            "handling `GeneratorExit`.")
    assert not hits(text)
    assert labels(text, 4) == ["[STEM~]"]


def test_list_items_and_criteria_are_read() -> None:
    assert hits("- runs its body `times` times with that instance")
    assert hits("Done when: the next `next()` still returns `2`.")


def test_line_is_the_first_member() -> None:
    assert hits("Intro.\n\nThe value\nis the next\n`next()` value.\n")[0][0] == 4


@pytest.mark.parametrize("word, expected", [
    ("returned", "return"), ("returns", "return"), ("hashing", "hash"),
    ("hashes", "hash"), ("classes", "class"), ("copies", "copy"),
    ("running", "run"), ("driver's", "driver"), ("closed", "clos"),
    ("process", "process"), ("status", "status"),
])
def test_stem(word: str, expected: str) -> None:
    assert stem(word) == expected


def test_examples_calibrate(capsys: pytest.CaptureFixture[str]) -> None:
    assert calibrate() == 0
    out = capsys.readouterr().out
    assert f"{len(EXAMPLES)} of {len(EXAMPLES)} examples" in out


def test_main_on_fixture(tmp_path: Path,
                         capsys: pytest.CaptureFixture[str]) -> None:
    f = tmp_path / "a.md"
    f.write_text("The next `next()` links the frame.\n", encoding="utf-8")
    assert main([str(f)]) == 0
    assert main([str(f), "--fail"]) == 1
    out = capsys.readouterr().out
    assert "survey" in out
    assert "1 stutter candidates (1 code, 0 stem, 0 mixed)" in out
