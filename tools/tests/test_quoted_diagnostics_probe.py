"""Tests for tools/quoted_diagnostics_probe.py.

The probe compares a quoted `ty` diagnostic with what `ty` prints for a
rebuilt listing. A comparison that passes everything is useless, so
these tests pin both directions: the book's wrapping and omissions
match, and a changed message, rule, location, or label does not.
"""
import pytest

from tools import quoted_diagnostics_probe as probe

ACTUAL = """\
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> build/quoted-probe/05_F/probe_area.py:6:12
  |
6 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
  |
info: Function defined here
 --> build/quoted-probe/05_F/probe_area.py:2:5
  |
2 | def area(width: int, height: int) -> int:
  |     ^^^^ ---------- Parameter declared here
  |
info: rule `invalid-argument-type` is enabled by default
"""

QUOTE = """\
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> area.py:6:12
  |
6 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
info: Function defined here
 --> area.py:2:5
  |
2 | def area(width: int, height: int) -> int:
  |     ^^^^ ---------- Parameter declared here
"""


def check(quote: str, actual: str = ACTUAL) -> str:
    return probe.match_events(probe.events(quote.split("\n")),
                              probe.events(actual.split("\n")))


def test_quote_matches_and_may_omit_trailing_info() -> None:
    assert check(QUOTE) == ""


def test_headline_only_quote_matches() -> None:
    headline = QUOTE.split("\n", 1)[0] + "\n"
    assert check(headline) == ""


def test_wrapped_headline_and_label_match() -> None:
    wrapped = QUOTE.replace(
        "Argument to function `area` is incorrect",
        "Argument to function\n`area` is incorrect").replace(
        "Expected `int`, found",
        "Expected `int`,\n  |            found")
    assert check(wrapped) == ""


@pytest.mark.parametrize("old, new", [
    ("is incorrect", "is wrong"),
    ("invalid-argument-type", "invalid-return-type"),
    ("area.py:6:12", "area.py:7:12"),
    ("Expected `int`", "Expected `str`"),
    ("Parameter declared here", "Parameter named here"),
    ('print(area("3", 4))', 'print(area("4", 4))'),
])
def test_changed_text_is_a_mismatch(old: str, new: str) -> None:
    assert check(QUOTE.replace(old, new)) != ""


def test_probe_name_maps_back_to_the_quoted_name() -> None:
    assert probe.short_name("build\\quoted-probe\\x\\probe_area.py") == "area.py"
    assert probe.short_name("a/probe_area__2.py") == "area.py"
    assert probe.short_name(".venv/Lib/site-packages/stateless/a.py") == "a.py"


def test_info_signature_continuation_joins_the_previous_info() -> None:
    actual = "error[x]: m\ninfo: f(a) -> b\n"
    quote = "error[x]: m\ninfo: f(a)\ninfo:      -> b\n"
    assert check(quote, actual) == ""


def test_quote_may_fold_the_label_into_the_headline() -> None:
    actual = ("info[revealed-type]: Revealed type\n --> a.py:9:17\n  |\n"
              "9 |     reveal_type(x)\n  |                 ^ `int`\n")
    quote = "info[revealed-type]: Revealed type\n`int`\n"
    assert check(quote, actual) == ""
    assert check(quote.replace("`int`", "`str`"), actual) != ""


def test_split_actual_stops_at_the_summary() -> None:
    text = ACTUAL + "\nFound 1 diagnostic\n"
    assert len(probe.split_actual(text)) == 1
    assert probe.split_actual("All checks passed!\n") == []


LISTING = ["a = 1  # type: ignore", "# b = 2", "c = 3", "d = 3", ""]


def test_edit_operations() -> None:
    edit = probe.apply_edit
    assert edit(LISTING, "strip-ignore")[0] == "a = 1"
    assert edit(LISTING, "uncomment: # b = 2")[1] == "b = 2"
    assert edit(LISTING, "replace: a = 1 => a = 9")[0].startswith("a = 9")
    assert "c = 3" not in edit(LISTING, "delete: c = 3")
    assert edit(LISTING, "delete-range: a = 1 => c = 3") == ["d = 3", ""]
    assert edit(LISTING, "insert-after: c = 3 => x\\ny")[3:5] == ["x", "y"]
    assert edit(LISTING, "append: z = 0")[-2:] == ["z = 0", ""]


def test_ambiguous_or_missing_anchor_is_an_error() -> None:
    with pytest.raises(probe.SpecError):
        probe.apply_edit(LISTING, "delete: = 3")
    with pytest.raises(probe.SpecError):
        probe.apply_edit(LISTING, "delete: nowhere")


@pytest.mark.book
def test_spec_is_well_formed_and_covers_every_quote() -> None:
    entries = probe.load_spec()
    keys = {e.key for e in entries}
    assert len(keys) == len(entries)
    quotes = [q for path in probe.md_files(
        [probe.ROOT / "Chapters", probe.ROOT / "Solutions"])
        for q in probe.quotes_in(path)]
    assert {q.key for q in quotes} == keys
