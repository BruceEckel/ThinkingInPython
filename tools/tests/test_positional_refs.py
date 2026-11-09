"""Tests for tools/positional_refs.py, on in-memory documents."""

from pathlib import Path
import pytest
from tools.markdown import Document
from tools.positional_refs import (
    display,
    find,
    key,
    load_baseline,
    main,
)

LOOP = "```python\nfor a in x:\n    pass\nfor b in y:\n    pass\n```\n"
ONE = "```python\nprint(1)\nprint(2)\n```\n"


def hits(text: str) -> list[tuple[int, str, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(h.line, h.kind, h.phrase) for h in find(doc)]


def test_ordinal_span_hit() -> None:
    text = ONE + "\nThe second `print()` shows two.\n"
    assert hits(text) == [(6, "ordinal+span", "The second `print()`")]


def test_ordinal_noun_hit() -> None:
    text = ONE + "\nThe last line prints two.\n"
    assert hits(text) == [(6, "ordinal+noun", "The last line")]


def test_line_number_hit() -> None:
    text = ONE + "\nSee line 3 for the call.\n"
    assert [k for _, k, _ in hits(text)] == ["line-number"]


def test_line_rel_and_n_lines() -> None:
    text = ONE + "\nThe line above sets it, two lines later it ends.\n"
    assert [k for _, k, _ in hits(text)] == ["line-rel", "n-lines"]


def test_construct_hit_needs_two() -> None:
    text = LOOP + "\nThe `for` loop runs.\n"
    assert [k for _, k, _ in hits(text)] == ["construct x2"]
    single = "```python\nfor a in x:\n    pass\n```\n"
    assert hits(single + "\nThe `for` loop runs.\n") == []


def test_construct_ignores_comments() -> None:
    text = ("```python\nfor a in x:  # for each\n    pass\n```\n"
            "\nThe `for` loop runs.\n")
    assert hits(text) == []


def test_first_argument_is_not_a_hit() -> None:
    assert hits(ONE + "\nThe first argument is a name.\n") == []


def test_citation_sentence_is_skipped() -> None:
    text = ONE + "\nThe second `print()` at `[1]` shows two.\n"
    assert hits(text) == []


def test_prose_above_first_listing_is_skipped() -> None:
    text = "The last line matters.\n\n" + ONE
    assert hits(text) == []


def test_heading_ends_the_region() -> None:
    text = ONE + "\n# Next\n\nThe last line matters.\n"
    assert hits(text) == []


def test_no_split_inside_code_span() -> None:
    text = ONE + "\nThe `self.x` call. The last line (see `a? b`) ends.\n"
    found = hits(text)
    assert [k for _, k, _ in found] == ["ordinal+noun"]


def test_sentence_is_whole_sentence() -> None:
    doc = Document.from_text(
        ONE + "\nThe `self.x` is set.\nThe last line\nprints two.\n",
        Path("fixture.md"))
    (hit,) = find(doc)
    assert hit.sentence == "The last line prints two."
    assert hit.line == 7


def test_key_has_no_line_number() -> None:
    k = key("a.md", "the last line", "The  last line\tends.")
    assert k == "a.md\tthe last line\tThe last line ends."


@pytest.fixture
def book(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path.resolve()
    monkeypatch.setattr("tools.positional_refs.ROOT", root)
    monkeypatch.setattr("tools.stranded_prepositions.ROOT", root)
    monkeypatch.setattr(
        "tools.positional_refs.BASELINE", root / "baseline.txt")
    (root / "Chapters").mkdir()
    (root / "Solutions").mkdir()
    path = root / "Chapters" / "a.md"
    path.write_text(ONE + "\nThe last line prints two.\n",
                    encoding="utf-8")
    return path


def test_accept_then_zero_new(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--fail"]) == 1
    assert "1 new, 0 accepted" in capsys.readouterr().out
    assert main(["--accept"]) == 0
    capsys.readouterr()
    entries = load_baseline(book.parent.parent / "baseline.txt")
    assert len(entries) == 1
    assert next(iter(entries)).startswith(display(book) + "\t")
    assert main(["--fail"]) == 0
    assert "0 new, 1 accepted" in capsys.readouterr().out


def test_edit_retires_entry(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    main(["--accept"])
    capsys.readouterr()
    book.write_text(ONE + "\nThe last line prints one.\n",
                    encoding="utf-8")
    assert main([]) == 0
    assert "1 new, 0 accepted, 1 stale" in capsys.readouterr().out


def test_accept_with_paths_touches_only_their_entries(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    other = book.parent / "b.md"
    other.write_text(book.read_text(encoding="utf-8"), encoding="utf-8")
    assert main([str(book), "--accept"]) == 0
    entries = load_baseline(book.parent.parent / "baseline.txt")
    assert [e.split("\t", 1)[0] for e in entries] == [display(book)]
    capsys.readouterr()
    assert main(["--fail"]) == 1
    assert "1 new, 1 accepted" in capsys.readouterr().out


THREE = ("```python\ng = f()\nnext(g)  # [1]\ng = f()\nnext(g)  # [2]\n"
         "g = f()\nnext(g)  # [3]\n```\n")


def test_count_unit_hits() -> None:
    text = THREE + ("\nIn the first three runs the value arrives.\n"
                    "Every run ends closed. Both attempts fail.\n")
    assert [(k, p) for _, k, p in hits(text)] == [
        ("count+unit", "first three runs"),
        ("count+unit", "Every run"),
        ("count+unit", "Both attempts"),
    ]


def test_quantifier_before_a_verb_is_not_a_hit() -> None:
    text = THREE + "\nThey both run the body, and each runs it once.\n"
    assert hits(text) == []


def test_count_unit_defers_to_ordinal_noun() -> None:
    text = THREE + "\nThe first call primes it.\n"
    assert [(k, p) for _, k, p in hits(text)] == [
        ("ordinal+noun", "The first call")]


def test_survey_units_are_marked() -> None:
    text = THREE + "\nEach time the body runs, two calls arrive.\n"
    assert [(k, p) for _, k, p in hits(text)] == [
        ("survey count+unit", "Each time"),
        ("survey count+unit", "two calls"),
    ]


def test_survey_hits_print_only_under_survey(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    book.write_text(THREE + "\nEach time it prints.\n", encoding="utf-8")
    assert main(["--fail"]) == 0
    out = capsys.readouterr().out
    assert "survey" not in out and "0 new, 0 accepted" in out
    assert main(["--survey"]) == 0
    out = capsys.readouterr().out
    assert "survey   " in out and "'Each time'" in out
    assert out.strip().endswith("0 new, 0 accepted, 1 survey")


TRY = ("```python\ntry:\n    conversation.send(x)\n"
       "except StopIteration as stop:\n    result = stop.value\n```\n")
WALK = TRY + "\nThat `send()` raises `StopIteration`.\n"


def test_alternative_fires_on_an_unframed_construct() -> None:
    text = WALK + ("A `for` loop treats `StopIteration` as the normal end "
                   "of the loop, so it discards the exception.\n")
    assert [(k, p) for _, k, p in hits(text)] == [
        ("survey alternative", "A `for`")]


def test_alternative_keyword_span_anywhere_in_the_sentence() -> None:
    text = WALK + "The value is lost in a `for` loop at `[1]`.\n"
    assert [(k, p) for _, k, p in hits(text)] == [
        ("survey alternative", "`for`")]


@pytest.mark.parametrize("tail", [
    # A marker word frames the alternative.
    "If a `for` loop drove it, the value is lost.\n",
    "A `for` loop would discard the exception.\n",
    "A `for` loop, by contrast, discards the exception.\n",
    # The construct is in the listing.
    "An `except` clause catches it.\n",
    # A second mention after a framed introduction.
    "A `for` loop would discard it. A `for` loop treats it as the end.\n",
])
def test_alternative_quiet(tail: str) -> None:
    assert hits(WALK + tail) == []


def test_alternative_needs_a_walkthrough_paragraph() -> None:
    text = TRY + "\nA `for` loop treats `StopIteration` as the end.\n"
    assert hits(text) == []


def test_alternative_is_a_survey_rule(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    book.write_text(WALK + "A `for` loop discards it.\n", encoding="utf-8")
    assert main(["--fail"]) == 0
    assert "alternative" not in capsys.readouterr().out
    assert main(["--survey"]) == 0
    out = capsys.readouterr().out
    assert "[survey alternative] 'A `for`'" in out
    assert out.strip().endswith("0 new, 0 accepted, 1 survey")


def self_hits(text: str) -> list[tuple[int, str, str]]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [(h.line, h.kind, h.phrase) for h in find(doc)
            if h.kind == "survey self-name"]


def test_self_name_lead_in() -> None:
    text = ("In `items.py`, the loop runs:\n\n"
            "```python\n# items.py\nprint(1)\n```\n")
    assert self_hits(text) == [(1, "survey self-name", "`items.py`")]


def test_self_name_ignores_directory_prefix() -> None:
    text = ("See `items.py`:\n\n"
            "```python\n# utils/items.py\nprint(1)\n```\n")
    assert [p for _, _, p in self_hits(text)] == ["`items.py`"]


def test_self_name_quiet_cases() -> None:
    here = "Here, the loop runs:\n\n```python\n# items.py\nprint(1)\n```\n"
    assert self_hits(here) == []
    part = ("```python\n# items.py\nprint(1)\n```\n\n"
            "Complete `items.py`:\n\n"
            "```python\n# items.py (continued)\nprint(2)\n```\n")
    assert self_hits(part) == []
    init = ("In `__init__.py`, the package loads:\n\n"
            "```python\n# a_package/__init__.py\nprint(1)\n```\n")
    assert self_hits(init) == []
    other = ("Compare `other.py`:\n\n"
             "```python\n# items.py\nprint(1)\n```\n")
    assert self_hits(other) == []
    heading = "## `items.py`\n\n```python\n# items.py\nprint(1)\n```\n"
    assert self_hits(heading) == []


def test_self_name_is_a_survey_rule(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    book.write_text("In `items.py`, it runs:\n\n"
                    "```python\n# items.py\nprint(1)\n```\n",
                    encoding="utf-8")
    assert main(["--fail"]) == 0
    assert "self-name" not in capsys.readouterr().out
    assert main(["--survey"]) == 0
    out = capsys.readouterr().out
    assert "[survey self-name] '`items.py`'" in out
    assert out.strip().endswith("0 new, 0 accepted, 1 survey")


def absent_hits(text: str) -> list[str]:
    doc = Document.from_text(text, Path("fixture.md"))
    return [h.phrase for h in find(doc) if h.kind == "survey absent-name"]


def test_absent_name_function() -> None:
    text = ("`proxy()` works, and `survey()` can delegate:\n\n"
            "```python\n# a.py\ndef proxy(): ...\n```\n")
    assert absent_hits(text) == ["`survey()`"]


def test_absent_name_once_per_sentence() -> None:
    text = ("Both `survey()` and `survey()` run:\n\n"
            "```python\n# a.py\nprint(1)\n```\n")
    assert absent_hits(text) == ["`survey()`"]


def test_absent_name_quiet_cases() -> None:
    imported = ("`survey()` runs:\n\n"
                "```python\n# a.py\nfrom b import survey\n```\n")
    assert absent_hits(imported) == []
    defined = ("`Shape` is a base:\n\n"
               "```python\n# a.py\nclass Shape: ...\n```\n")
    assert absent_hits(defined) == []
    builtin = ("`print()` shows it:\n\n"
               "```python\n# a.py\nx = 1\n```\n")
    assert absent_hits(builtin) == []
    variable = ("The `inner` name is bound:\n\n"
                "```python\n# a.py\nx = 1\n```\n")
    assert absent_hits(variable) == []
    earlier = ("`survey()` is defined elsewhere. Here it runs:\n\n"
               "```python\n# a.py\nx = 1\n```\n")
    assert absent_hits(earlier) == []


def test_absent_name_checks_the_whole_file() -> None:
    text = ("```python\n# a.py\ndef survey(): ...\n```\n\n"
            "`survey()` continues:\n\n"
            "```python\n# a.py (continued)\nx = 1\n```\n")
    assert absent_hits(text) == []


def test_absent_name_is_a_survey_rule(
    book: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    book.write_text("`survey()` runs:\n\n"
                    "```python\n# a.py\nx = 1\n```\n",
                    encoding="utf-8")
    assert main(["--fail"]) == 0
    assert "absent-name" not in capsys.readouterr().out
    assert main(["--survey"]) == 0
    out = capsys.readouterr().out
    assert "[survey absent-name] '`survey()`'" in out
