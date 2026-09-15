"""tools/pattern_names.py: every naming of a pattern is *Capitalized*."""

from pathlib import Path

from tools.markdown import Document
from tools.pattern_names import fixed, rewrite_line, scan

# Deliberately not longest-first: the matcher sorts them itself.
NAMES = ("Chain of Responsibility", "Template Method", "Null Object",
         "Strategy", "Observer", "State", "Command", "Factory",
         "Factory Method", "!State Machines")


def codes(line: str) -> list[str]:
    return [code for code, _ in rewrite_line(line, NAMES)[1]]


def test_italic_name_is_clean() -> None:
    line = "*Strategy* defers *how*, and a *Chain of Responsibility* tries."
    assert rewrite_line(line, NAMES) == (line, [])


def test_plain_capitalized_name_is_wrapped() -> None:
    new, found = rewrite_line("the Observer pattern is a callback", NAMES)
    assert new == "the *Observer* pattern is a callback"
    assert found == [("plain", "Observer")]


def test_link_text_is_wrapped_and_target_is_not() -> None:
    line = "see [Template Method](25_Patterns--Template_Method.md#a-template-method)"
    new, _ = rewrite_line(line, NAMES)
    assert new == ("see [*Template Method*]"
                   "(25_Patterns--Template_Method.md#a-template-method)")


def test_code_span_is_ignored() -> None:
    line = "the `Strategy` class and `case Command.QUIT:`"
    assert rewrite_line(line, NAMES) == (line, [])


def test_bold_becomes_italic() -> None:
    new, found = rewrite_line("a **Strategy** in **bold** text", NAMES)
    assert new == "a *Strategy* in **bold** text"
    assert found == [("bold", "Strategy")]


def test_lowercase_word_is_left_alone() -> None:
    line = "the observer registers interest; mutable state; a factory"
    assert rewrite_line(line, NAMES) == (line, [])


def test_lowercase_before_pattern_is_the_pattern() -> None:
    new, found = rewrite_line("use the null object pattern here", NAMES)
    assert new == "use the *Null Object* pattern here"
    assert found == [("lower-pattern", "null object")]


def test_ambiguous_name_at_line_start_is_reported_not_fixed() -> None:
    line = "State the rule that predicts the sign."
    new, found = rewrite_line(line, NAMES)
    assert new == line
    assert found == [("sentence-start", "State")]
    # Behind a list marker the line's text still starts there.
    assert codes("- Command defers what to do") == ["sentence-start"]


def test_unambiguous_name_at_line_start_is_fixed() -> None:
    new, _ = rewrite_line("Strategy defers how.", NAMES)
    assert new == "*Strategy* defers how."


def test_name_inside_an_italic_span_is_not_double_wrapped() -> None:
    line = "as *the Strategy pattern* shows"
    assert rewrite_line(line, NAMES) == (line, [])


def test_longer_name_wins() -> None:
    new, found = rewrite_line("a Factory Method, then a Factory", NAMES)
    assert new == "a *Factory Method*, then a *Factory*"
    assert [w for _, w in found] == ["Factory Method", "Factory"]


def test_plural_and_possessive_of_plain_form_are_not_matched() -> None:
    line = "two Observers and Strategys"
    assert rewrite_line(line, NAMES) == (line, [])


def test_headings_and_code_blocks_are_skipped(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text(
        "# Strategy: Choosing\n\nStrategy chooses.\n\n"
        "```python\n# a.py\nclass Strategy: ...\n```\n",
        encoding="utf-8")
    doc = Document.parse(md)
    findings = list(scan(doc, NAMES))
    assert [(f.line, f.code) for f in findings] == [(3, "plain")]
    assert fixed(doc) == (
        "# Strategy: Choosing\n\n*Strategy* chooses.\n\n"
        "```python\n# a.py\nclass Strategy: ...\n```\n")


def test_fixed_is_none_when_clean(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text("*Strategy* chooses.\n", encoding="utf-8")
    assert fixed(Document.parse(md)) is None


def test_excluded_phrase_is_skipped() -> None:
    line = "see [State Machines](31_Patterns--State_Machines.md) for *State*"
    assert rewrite_line(line, NAMES) == (line, [])


def test_sentence_start_is_listed_only_on_request(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text("State the rule.\n", encoding="utf-8")
    doc = Document.parse(md)
    assert list(scan(doc, NAMES)) == []
    assert [f.code for f in scan(doc, NAMES, sentence_start=True)] == [
        "sentence-start"]


def test_bold_span_keeps_its_code_and_wraps_its_name() -> None:
    line = "**The `Wrapper` class is an Observer.** It forwards `x`."
    new, found = rewrite_line(line, NAMES)
    assert new == "**The `Wrapper` class is an *Observer*.** It forwards `x`."
    assert found == [("plain", "Observer")]


def test_indented_code_outside_a_list_is_skipped(tmp_path: Path) -> None:
    md = tmp_path / "x.md"
    md.write_text(
        "A base class could do it:\n\n    class State: pass\n\n"
        "1.  Use Strategy here,\n    and Observer there.\n",
        encoding="utf-8")
    findings = list(scan(Document.parse(md), NAMES))
    assert [(f.line, f.message.split('"')[1]) for f in findings] == [
        (5, "Strategy"), (6, "Observer")]
