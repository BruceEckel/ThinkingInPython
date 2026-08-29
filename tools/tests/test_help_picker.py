"""Tests for tools/help_picker.py, driven headlessly.

prompt_toolkit's pipe input feeds key sequences to the real Application
and a dummy output swallows the drawing, so the bindings, the view stack,
and type-to-jump are exercised end to end without a terminal.
"""
import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from help_picker import (
    Picker, all_rows, index_rows, make_command, section_rows, wants_chapter)
from make_help import MAKEFILE, PROMOTED, parse

UP, DOWN, LEFT = "\x1b[A", "\x1b[B", "\x1b[D"
ENTER, ESC, BACKSPACE = "\r", "\x1b", "\x7f"
HOME, END = "\x1b[H", "\x1b[F"
PAGEDOWN = "\x1b[6~"


def _sections():
    return parse(MAKEFILE.read_text(encoding="utf-8"))


def drive(rows, keys: str):
    """Run the picker over `rows` with `keys` typed; the chosen target."""
    sections = _sections()
    with create_pipe_input() as pipe:
        pipe.send_text(keys)
        picker = Picker(sections, rows, input=pipe, output=DummyOutput())
        return picker.run()


def test_index_rows_lead_with_help_then_promoted_targets_then_sections():
    rows = index_rows(_sections())
    assert rows[0].kind == "all" and rows[0].label == "help"
    targets = [r.label for r in rows if r.kind == "target"]
    assert targets == list(PROMOTED)
    slugs = [r.label for r in rows if r.kind == "section"]
    assert slugs == [s.slug for s in _sections() if s.slug]


def test_all_rows_fold_secondary_targets_and_skip_the_preamble():
    names = {r.label for r in all_rows(_sections()) if r.kind == "target"}
    assert "help" not in names   # the preamble: nothing to run there
    for section in _sections():
        if not section.slug:
            continue
        for target in section.targets:
            assert (target.name in names) is not target.secondary


def test_enter_runs_the_first_target():
    rows = all_rows(_sections())
    first = next(r for r in rows if r.kind == "target")
    assert drive(rows, ENTER) is first.target


def test_down_then_enter_runs_the_second_target():
    rows = all_rows(_sections())
    second = [r for r in rows if r.kind == "target"][1]
    assert drive(rows, DOWN + ENTER) is second.target


def test_up_at_the_top_stays_and_end_reaches_the_last():
    rows = all_rows(_sections())
    targets = [r for r in rows if r.kind == "target"]
    assert drive(rows, UP + UP + ENTER) is targets[0].target
    assert drive(rows, END + ENTER) is targets[-1].target
    assert drive(rows, END + HOME + ENTER) is targets[0].target


def test_pagedown_skips_ten_targets():
    rows = all_rows(_sections())
    targets = [r for r in rows if r.kind == "target"]
    assert drive(rows, PAGEDOWN + ENTER) is targets[10].target


def test_typing_jumps_to_a_target_by_prefix():
    rows = all_rows(_sections())
    assert drive(rows, "sw" + ENTER).name == "sweep"
    # a letter that matches nothing is ignored, the highlight stays put
    assert drive(rows, "sw" + "zzz" + ENTER).name == "sweep"


def test_backspace_shortens_the_prefix():
    rows = all_rows(_sections())
    chosen = drive(rows, "sp" + BACKSPACE + ENTER)
    assert chosen.name.startswith("s")


def test_escape_leaves_without_a_target():
    assert drive(all_rows(_sections()), DOWN + ESC) is None


def test_index_enter_on_a_section_opens_it_and_left_returns():
    sections = _sections()
    rows = index_rows(sections)
    to_sections = DOWN * (1 + len(PROMOTED))   # past help and everyday
    first_section = next(s for s in sections if s.slug)
    opened = drive(rows, to_sections + ENTER + ENTER)
    assert opened is first_section.listed()[0]
    # Left comes back to the index with the section row still highlighted
    back_then_up = drive(rows, to_sections + ENTER + LEFT + UP + ENTER)
    assert back_then_up.name == PROMOTED[-1]


def test_index_help_row_opens_every_section_and_left_returns():
    sections = _sections()
    rows = index_rows(sections)
    first_target = next(r for r in all_rows(sections) if r.kind == "target")
    assert drive(rows, ENTER + ENTER) == first_target.target
    assert drive(rows, ENTER + LEFT + DOWN + ENTER).name == PROMOTED[0]


def test_left_at_the_top_level_quits():
    assert drive(section_rows(_sections()[1]), LEFT) is None


def test_the_picker_tracks_the_view_stack():
    sections = _sections()
    picker = Picker(sections, index_rows(sections), output=DummyOutput())
    picker.move_to_end(last=True)
    assert picker.rows[picker.cursor].kind == "section"
    assert picker.activate() is None
    assert picker.rows[0].kind == "heading"
    assert picker.back()
    assert picker.rows[picker.cursor].kind == "section"
    assert not picker.back()


def test_make_command_appends_the_chapter_only_when_given():
    section = next(s for s in _sections() if s.slug == "code")
    check_ch = next(t for t in section.targets if t.name == "check-ch")
    assert wants_chapter(check_ch)
    assert make_command(check_ch)[1:] == ["check-ch"]
    assert make_command(check_ch, "12")[1:] == ["check-ch", "CH=12"]
    plain = next(t for t in section.targets if t.name == "test")
    assert not wants_chapter(plain)


@pytest.mark.parametrize("slug", [s.slug for s in _sections() if s.slug])
def test_every_section_view_has_a_selectable_row(slug):
    section = next(s for s in _sections() if s.slug == slug)
    rows = section_rows(section)
    assert rows[0].kind == "heading" and rows[0].label == f"{slug}:"
    assert any(r.selectable for r in rows)
