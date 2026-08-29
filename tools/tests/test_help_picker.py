"""Tests for tools/help_picker.py, driven headlessly.

prompt_toolkit's pipe input feeds key sequences to the real Application
and a dummy output swallows the drawing, so the bindings and type-to-jump
are exercised end to end without a terminal.
"""
import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from help_picker import (
    Picker, all_rows, ask_return_or_esc, filter_rows, make_command,
    section_rows, session, split_match, wants_chapter)
from make_help import MAKEFILE, parse

UP, DOWN = "\x1b[A", "\x1b[B"
ENTER, ESC, BACKSPACE = "\r", "\x1b", "\x7f"
HOME, END = "\x1b[H", "\x1b[F"
PAGEDOWN = "\x1b[6~"


def _sections():
    return parse(MAKEFILE.read_text(encoding="utf-8"))


def drive(rows, keys: str):
    """Run the picker over `rows` with `keys` typed; the chosen target."""
    with create_pipe_input() as pipe:
        pipe.send_text(keys)
        picker = Picker(rows, input=pipe, output=DummyOutput())
        return picker.run()


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


def test_typing_searches_and_enter_runs_the_first_name_match():
    rows = all_rows(_sections())
    assert drive(rows, "sw" + ENTER).name == "sweep"
    assert drive(rows, "/sw" + ENTER).name == "sweep"
    assert drive(rows, "SWEE" + ENTER).name == "sweep"


def test_search_matches_doc_text_too():
    rows = all_rows(_sections())
    assert drive(rows, "CRLF" + ENTER).name == "eol"


def test_search_that_matches_nothing_leaves_enter_inert_until_cleared():
    rows = all_rows(_sections())
    first = next(r for r in rows if r.kind == "target")
    assert drive(rows, "zzzz" + ESC + ENTER) is first.target


def test_backspace_edits_the_query_and_escape_clears_it():
    rows = all_rows(_sections())
    assert drive(rows, "swx" + BACKSPACE + ENTER).name == "sweep"
    # clearing the search keeps the highlight where the search left it
    assert drive(rows, "sw" + ESC + ENTER).name == "sweep"
    assert drive(rows, "sw" + ESC + UP + ENTER).name != "sweep"
    assert drive(rows, "sw" + ESC + ESC) is None


def test_rendering_caps_the_scroll_at_the_highlighted_sections_heading():
    rows = all_rows(_sections())
    picker = Picker(rows, output=DummyOutput())
    picker.window.vertical_scroll = 500      # as if arrowed far down
    picker.search("must be clean")           # doc-only: `ty` first, row 1
    assert picker.rows[picker.cursor].label == "ty"
    picker._body()
    assert picker.window.vertical_scroll == 0    # its heading is line 0
    picker.move_to_end(last=True)            # under "solutions:"
    picker.window.vertical_scroll = 500
    text = "".join(f[1] for f in picker._body())
    heading_line = next(i for i, line in enumerate(text.splitlines())
                        if line.startswith("solutions: "))
    assert heading_line > 0
    assert picker.window.vertical_scroll == heading_line
    picker.window.vertical_scroll = 0        # never scrolls forward
    picker._body()
    assert picker.window.vertical_scroll == 0


def test_filter_rows_keeps_headings_of_matching_sections_only():
    rows = all_rows(_sections())
    kept = filter_rows(rows, "clean")
    kinds = [r.kind for r in kept]
    assert "blank" not in kinds[:1] and "blank" not in kinds[-1:]
    for i, row in enumerate(kept):
        if row.kind == "heading":
            assert kept[i + 1].kind == "target"     # no empty sections
        if row.kind == "target":
            assert "clean" in row.label or "clean" in row.doc.lower()
    assert any(r.label == "clean" for r in kept)
    assert filter_rows(rows, "") is rows


def test_split_match_marks_every_occurrence_case_insensitively():
    assert split_match("solutions-sync", "s") == [
        ("s", True), ("olution", False), ("s", True), ("-", False),
        ("s", True), ("ync", False)]
    assert split_match("gate", "GATE") == [("gate", True)]
    assert split_match("gate", "x") == [("gate", False)]
    assert split_match("gate", "") == [("gate", False)]


def test_escape_leaves_without_a_target():
    assert drive(all_rows(_sections()), DOWN + ESC) is None


def test_picker_reopens_at_the_given_cursor():
    rows = all_rows(_sections())
    targets = [i for i, r in enumerate(rows) if r.kind == "target"]
    with create_pipe_input() as pipe:
        pipe.send_text(ENTER)
        picker = Picker(rows, cursor=targets[3], input=pipe,
                        output=DummyOutput())
        assert picker.run() is rows[targets[3]].target
        assert picker.cursor == targets[3]


@pytest.mark.parametrize("keys, again", [
    (ENTER, True), ("x" + ENTER, True), (ESC, False), ("\x03", False)])
def test_after_a_run_return_reopens_and_esc_quits(keys, again):
    with create_pipe_input() as pipe:
        pipe.send_text(keys)
        assert ask_return_or_esc(input=pipe, output=DummyOutput()) is again


def test_session_loops_until_esc_and_reports_the_last_status():
    rows = all_rows(_sections())
    targets = [r.target for r in rows if r.target is not None]
    picks = iter([(targets[0], 1), (targets[2], 3), (None, 3)])
    answers = iter([True, True])
    ran: list[str] = []
    seen_cursors: list[int | None] = []

    def pick(cursor):
        seen_cursors.append(cursor)
        return next(picks)

    def run(target):
        ran.append(target.name)
        return 7 if target is targets[2] else 0

    status = session(pick, run, lambda: next(answers))
    assert ran == [targets[0].name, targets[2].name]
    assert seen_cursors == [None, 1, 3]     # the highlight is restored
    assert status == 7                       # the last run's status


def test_session_esc_after_a_run_quits_with_that_status():
    rows = all_rows(_sections())
    target = next(r.target for r in rows if r.kind == "target")
    status = session(lambda c: (target, 0), lambda t: 3, lambda: False)
    assert status == 3
    assert session(lambda c: (None, 0), lambda t: 3, lambda: True) == 0


def test_a_section_view_offers_only_that_sections_targets():
    section = next(s for s in _sections() if s.slug == "cleanup")
    rows = section_rows(section)
    assert drive(rows, END + ENTER).name == section.listed()[-1].name
    assert drive(rows, DOWN * 50 + ENTER).name == section.listed()[-1].name


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
