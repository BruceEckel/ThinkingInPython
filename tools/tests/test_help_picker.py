"""Tests for tools/help_picker.py, driven headlessly.

prompt_toolkit's pipe input feeds key sequences to the real Application
and a dummy output swallows the drawing, so the bindings and type-to-jump
are exercised end to end without a terminal.
"""
import pytest
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from unittest import mock

from help_picker import (
    RECORD_VAR, Picker, all_rows, ask_return_or_esc, filter_rows,
    history_files, make_command, record_command, record_history,
    INTERRUPTED, next_version, notes_lines, run_target, section_rows,
    session,
    split_match, variables)
from make_help import MAKEFILE, Target, parse

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


def test_history_files_lists_only_the_ones_that_exist(tmp_path):
    home = tmp_path / "home"
    psrl = (tmp_path / "appdata" / "Microsoft" / "Windows" / "PowerShell"
            / "PSReadLine" / "ConsoleHost_history.txt")
    psrl.parent.mkdir(parents=True)
    psrl.write_text("make\n")
    (home / ".zsh_history").parent.mkdir(parents=True)
    (home / ".zsh_history").write_text("")
    env = {"APPDATA": str(tmp_path / "appdata")}
    assert history_files(env, home) == [psrl, home / ".zsh_history"]
    assert history_files({}, tmp_path / "nowhere") == []


def test_record_history_appends_plain_and_zsh_extended_lines(tmp_path):
    plain = tmp_path / "ConsoleHost_history.txt"
    plain.write_text("make\n")
    zsh = tmp_path / ".zsh_history"
    zsh.write_text(": 1700000000:0;ls\n")
    zsh_plain = tmp_path / "plain" / ".zsh_history"
    zsh_plain.parent.mkdir()
    zsh_plain.write_text("ls\n")
    written = record_history("make sweep", [plain, zsh, zsh_plain], now=42)
    assert written == [plain, zsh, zsh_plain]
    assert plain.read_text().splitlines() == ["make", "make sweep"]
    assert zsh.read_text().splitlines()[-1] == ": 42:0;make sweep"
    assert zsh_plain.read_text().splitlines()[-1] == "make sweep"


def test_record_command_prefers_the_wrappers_file(tmp_path):
    record = tmp_path / "make-menu-abc"        # the wrapper's scratch file
    psrl = (tmp_path / "appdata" / "Microsoft" / "Windows" / "PowerShell"
            / "PSReadLine" / "ConsoleHost_history.txt")
    psrl.parent.mkdir(parents=True)
    psrl.write_text("make\n")
    home = tmp_path / "home"
    home.mkdir()
    env = {"APPDATA": str(tmp_path / "appdata"), RECORD_VAR: str(record)}
    assert record_command("make test", env, home) == [record]
    assert record.read_text().splitlines() == ["make test"]
    assert psrl.read_text().splitlines() == ["make"]     # left alone
    # without the variable, the history files get it
    env.pop(RECORD_VAR)
    assert record_command("make test", env, home) == [psrl]
    assert psrl.read_text().splitlines() == ["make", "make test"]


def test_record_history_skips_a_file_it_cannot_write(tmp_path):
    missing = tmp_path / "no" / "such" / "history"
    assert record_history("make sweep", [missing]) == []


def _target(name):
    return next(t for s in _sections() for t in s.targets if t.name == name)


def test_variables_come_from_the_doc_with_their_examples():
    assert variables(_target("check-ch")) == [("CH", "12")]
    assert variables(_target("release")) == [("VERSION", "1.0")]
    assert variables(_target("python-upgrade")) == [("TO", "3.15")]
    assert variables(_target("code-width")) == [
        ("WIDTH", "nn"), ("ARGS", "--tsv")]
    assert variables(_target("test")) == []
    assert "ARGS=" in _target("all").doc          # documented, but
    assert variables(_target("all")) == []        # never prompted for


@pytest.mark.parametrize("tags, expected", [
    (["v0.1.0", "v0.4.0", "v0.4.1", "v0.4.2"], "0.4.3"),   # patch bump
    (["v0.3.0", "v0.4.0"], "0.5.0"),                        # minor bump
    (["v0.4.2", "v0.4.0", "v0.10.0"], "0.11.0"),   # numeric max
    (["v1.0"], "1.1"),                             # two parts kept
    (["1.2.3", "v1.2.4"], "1.2.5"),                         # bare tags count
    (["draft", "v0.4.2-rc1", "cover-v2"], None),           # no release tag
    ([], None),
])
def test_next_version_guesses_from_the_highest_release_tag(tags, expected):
    assert next_version(tags) == expected


def test_ctrl_c_during_the_run_is_a_note_not_a_traceback(capsys):
    target = _target("test")
    with mock.patch("help_picker.subprocess.call",
                    side_effect=KeyboardInterrupt), \
            mock.patch("help_picker.record_command", return_value=[]):
        assert run_target(target) == INTERRUPTED
    out = capsys.readouterr().out
    assert "$ make test" in out
    assert "(interrupted: make test)" in out
    assert "Traceback" not in out


def test_ctrl_c_at_a_variable_prompt_cancels_the_run(capsys):
    target = _target("check-ch")
    with mock.patch("help_picker.ask_variables",
                    side_effect=KeyboardInterrupt), \
            mock.patch("help_picker.subprocess.call") as call:
        assert run_target(target) == INTERRUPTED
    call.assert_not_called()
    assert "(cancelled)" in capsys.readouterr().out


def test_a_failing_target_reports_its_status(capsys):
    target = _target("test")
    with mock.patch("help_picker.subprocess.call", return_value=2), \
            mock.patch("help_picker.record_command", return_value=[]), \
            mock.patch("help_picker.ask_variables", return_value={}):
        assert run_target(target) == 2
    assert "(make test exited with status 2)" in capsys.readouterr().out


def test_make_command_appends_only_the_variables_given_a_value():
    check_ch = _target("check-ch")
    assert make_command(check_ch)[1:] == ["check-ch"]
    assert make_command(check_ch, {"CH": ""})[1:] == ["check-ch"]
    assert make_command(check_ch, {"CH": "12"})[1:] == ["check-ch", "CH=12"]
    assert make_command(_target("release"), {"VERSION": "1.0"})[1:] == [
        "release", "VERSION=1.0"]
    assert make_command(_target("code-width"),
                        {"WIDTH": "", "ARGS": "--tsv"})[1:] == [
        "code-width", "ARGS=--tsv"]


@pytest.mark.parametrize("slug", [s.slug for s in _sections() if s.slug])
def test_every_section_view_has_a_selectable_row(slug):
    section = next(s for s in _sections() if s.slug == slug)
    rows = section_rows(section)
    assert rows[0].kind == "heading" and rows[0].label == f"{slug}:"
    assert any(r.selectable for r in rows)


# ---- `?`: the notes view


def test_question_mark_opens_the_notes_and_enter_runs_from_there():
    rows = all_rows(_sections())
    first = next(r for r in rows if r.kind == "target")
    assert drive(rows, "?" + ENTER) is first.target


def test_escape_closes_the_notes_and_the_list_resumes_where_it_was():
    rows = all_rows(_sections())
    second = [r for r in rows if r.kind == "target"][1]
    assert drive(rows, DOWN + "?" + ESC + ENTER) is second.target
    assert drive(rows, DOWN + "?" + "?" + ENTER) is second.target
    assert drive(rows, DOWN + "?" + BACKSPACE + ENTER) is second.target


def test_typing_while_the_notes_are_open_does_not_search():
    rows = all_rows(_sections())
    first = next(r for r in rows if r.kind == "target")
    assert drive(rows, "?" + "sweep" + ESC + ENTER) is first.target


def test_notes_scroll_clamps_at_both_ends():
    rows = all_rows(_sections())
    picker = Picker(rows, output=DummyOutput())
    sweep = next(r for r in rows if r.label == "sweep")
    picker.cursor = rows.index(sweep)
    picker.open_notes()
    assert picker.notes is sweep.target
    picker.scroll_notes(-5)
    assert picker.notes_scroll == 0
    picker.scroll_notes_to_end(last=True)
    picker._notes_body()
    assert sweep.target is not None
    assert picker.notes_scroll == len(
        notes_lines(sweep.target, picker._width())) - 1
    picker.scroll_notes_to_end(last=False)
    assert picker.notes_scroll == 0


def test_footer_names_the_notes_key_and_the_open_target():
    rows = all_rows(_sections())
    picker = Picker(rows, output=DummyOutput())
    assert "? help" in picker._footer()[0][1]
    picker.open_notes()
    assert picker.notes is not None
    assert picker._footer()[0][1].startswith(f" {picker.notes.name}:")
    assert "Esc back" in picker._footer()[0][1]


def test_notes_lines_show_the_doc_the_comment_block_and_the_recipe():
    sweep = next(t for s in _sections() for t in s.targets
                 if t.name == "sweep")
    lines = notes_lines(sweep, 72)
    texts = [text for _, text in lines]
    assert lines[0] == ("class:slug", "sweep")
    assert texts[1].startswith("  Run every check")
    assert any("first failure" in t for t in texts)      # the comment
    assert "Runs:" in texts
    assert texts[-1] == "    $(PY) tools/sweep_checks.py"
    assert all(len(t) <= 72 for t in texts)


def test_a_prerequisites_only_target_lists_them():
    verify = next(t for s in _sections() for t in s.targets
                  if t.name == "verify")
    texts = [t for _, t in notes_lines(verify, 72)]
    at = texts.index("Prerequisites:")
    assert texts[at + 1].startswith("    fix-eol ")
    assert "gate" in texts[at + 1]
    assert "Runs:" not in texts


def test_notes_lines_without_notes_or_recipe_say_so():
    texts = [t for _, t in notes_lines(Target("x", "Do x"), 60)]
    assert texts == ["x", "  Do x", "",
                     "  (no notes, prerequisites, or recipe in the Makefile)"]


def test_notes_lines_keep_an_indented_paragraph_as_written():
    target = Target("x", "Do x", notes="Install it with:\n  winget install x")
    texts = [t for _, t in notes_lines(target, 60)]
    assert texts[3:] == ["  Install it with:", "    winget install x"]
