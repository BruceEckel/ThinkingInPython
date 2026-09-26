"""Tests for tools/tip_help.py: the listing, its invariants, and the
Registry that feeds it.

The real tools/tasks.py is exercised too, so a section or doc that
breaks the conventions fails here rather than at the next `tip help`.
"""
import io
import re

import pytest

from tools.target_times import Timing
from tools.tip import Registry, Vars
from tools.tip_help import (
    ANSI, LEGEND, MAX_WIDTH, MIN_DOC, PLAIN, can_colorize, check, entries,
    load_sections, render_all, render_section, terminal_width, want_picker,
    wrap_doc)

_ESCAPES = re.compile(r"\x1b\[[0-9;]*m")


def _noop(v: Vars) -> None:
    pass


def build(*spec: tuple[str, ...]) -> Registry:
    """A registry from ("section", title), ("task", name, doc),
    ("secondary", name, doc), and ("also", name, ...) entries."""
    reg = Registry()
    for kind, *args in spec:
        match kind:
            case "section":
                reg.section(args[0])
            case "task" | "secondary":
                reg.task(args[1], name=args[0],
                         secondary=kind == "secondary")(_noop)
            case "also":
                reg.also(*args)
    return reg


SAMPLE = build(
    ("section", "Build and site"),
    ("task", "build-thing", "Build the thing"),
    ("secondary", "hidden", "A secondary target"),
    ("section", "Style gates"),
    ("task", "eol", "Check for CRLF; `tip fix-eol` converts them"),
    ("secondary", "fix-eol", "Convert CRLF to LF"),
)


def test_sections_group_tasks_under_headings():
    sections = SAMPLE.sections()
    assert [s.slug for s in sections] == ["build", "style"]
    assert [s.title for s in sections] == ["Build and site", "Style gates"]
    assert [t.name for t in sections[0].targets] == ["build-thing", "hidden"]


def test_slug_is_the_headings_first_word_lowercased():
    reg = build(("section", "Code examples (build/examples/)"),
                ("task", "x", "d"))
    assert reg.sections()[0].slug == "code"


def test_secondary_tasks_stay_in_entries_but_leave_the_listing():
    """verify_targets.py enumerates through entries(), so folding must
    not remove a task from the smoke test."""
    sections = SAMPLE.sections()
    assert "hidden" in {n for n, _ in entries(sections) if n}
    assert [t.name for t in sections[0].listed()] == ["build-thing"]


def test_entries_keeps_the_flat_shape_its_callers_expect():
    found = entries(SAMPLE.sections())
    assert (None, "Build and site") in found
    assert ("build-thing", "Build the thing") in found


def test_render_section_shows_only_listed_tasks():
    rendered = render_section(SAMPLE.sections()[0])
    assert "build-thing" in rendered
    assert "hidden" not in rendered


def test_duplicate_slugs_are_rejected():
    reg = build(("section", "Style gates"), ("task", "a", "d"),
                ("section", "Style rules"), ("task", "b", "d"))
    with pytest.raises(SystemExit, match="share the slug"):
        check(reg.sections())


def test_a_task_defined_twice_is_rejected():
    reg = build(("section", "S"), ("task", "a", "d"))
    with pytest.raises(SystemExit, match="defined twice"):
        reg.task("again", name="a")(_noop)


REPEATED = build(
    ("section", "Everyday"),
    ("task", "verify", "Run the gate"),
    ("also", "sync", "fix-eol"),
    ("task", "gate", "The gate"),
    ("section", "Code examples"),
    ("task", "sync", "Sync the tree"),
    ("also", "gate"),
    ("task", "eol", "Check line endings; `tip fix-eol` converts them"),
    ("secondary", "fix-eol", "Convert them"),
)


def test_also_lists_tasks_defined_elsewhere_in_place():
    everyday, code = REPEATED.sections()
    assert [t.name for t in everyday.targets] == [
        "verify", "sync", "fix-eol", "gate"]
    assert [t.name for t in code.targets] == [
        "sync", "gate", "eol", "fix-eol"]
    sync = everyday.targets[1]
    assert sync.repeat and sync.doc == "Sync the tree"
    assert not code.targets[0].repeat


def test_a_repeat_keeps_the_tasks_secondary_flag():
    """A secondary task stays folded wherever it is repeated; the
    sibling that names it is what the reader sees."""
    everyday = REPEATED.sections()[0]
    assert [t.name for t in everyday.listed()] == ["verify", "sync", "gate"]


def test_entries_lists_a_repeated_task_once():
    """verify_targets.py runs every name entries() reports, so a repeat
    must not run its task twice."""
    names = [n for n, _ in entries(REPEATED.sections()) if n]
    assert names == ["verify", "gate", "sync", "eol", "fix-eol"]


def test_a_repeat_of_an_unknown_task_is_rejected():
    reg = build(("section", "Everyday"), ("also", "nonesuch"),
                ("task", "verify", "d"))
    with pytest.raises(SystemExit, match="names no task"):
        reg.sections()


def test_a_repeat_inside_its_own_section_is_rejected():
    reg = build(("section", "Everyday"), ("task", "verify", "d"),
                ("also", "verify"))
    with pytest.raises(SystemExit, match="inside its own section"):
        reg.sections()


LONG = build(("section", "Style gates"), ("task", "x", "word " * 40))


def test_doc_text_wraps_to_the_given_width():
    lines = render_section(LONG.sections()[0], 60).splitlines()
    assert len(lines) > 2
    assert all(len(line) <= 60 for line in lines)


def test_continuation_lines_align_under_the_doc_column():
    lines = render_section(LONG.sections()[0], 60).splitlines()[1:]
    start = lines[0].index("word")
    assert all(len(line) - len(line.lstrip()) == start for line in lines[1:])


def test_a_backticked_command_is_never_split_across_lines():
    reg = build(("section", "Style gates"),
                ("task", "eol", "pad " * 12 + "`tip fix-eol` ok"))
    rendered = render_section(reg.sections()[0], 60)
    for line in rendered.splitlines():
        assert line.count("`") % 2 == 0, line
    assert "`tip fix-eol`" in rendered


def test_a_hyphenated_task_name_is_never_split():
    reg = build(("section", "Style gates"),
                ("task", "fix-comment-spacing", "pad " * 20))
    body = render_section(reg.sections()[0], 40)
    assert "fix-comment-spacing" in body
    assert "fix-comment-\n" not in body


def test_too_narrow_to_wrap_falls_back_to_one_long_line():
    """Below MIN_DOC the doc column would be shredded, so leave it alone."""
    lines = render_section(LONG.sections()[0], MIN_DOC).splitlines()
    assert len(lines) == 2


def test_width_is_capped_and_overridable():
    assert terminal_width(300) == 300
    assert terminal_width() <= MAX_WIDTH


def test_wrap_doc_keeps_backticked_commands_whole():
    lines = wrap_doc("Check for CRLF; `tip fix-eol` converts them", 30)
    assert "`tip fix-eol`" in " ".join(lines)
    for line in lines:
        assert "`tip" not in line or "fix-eol`" in line


def test_want_picker_respects_explicit_choice_and_ci():
    assert want_picker("always", {"CI": "1"})
    assert not want_picker("never", {})
    assert not want_picker("auto", {"CI": "true"})


def test_can_colorize_honors_the_environment_and_the_stream():
    pipe = io.StringIO()
    assert not can_colorize(pipe, {})
    assert can_colorize(pipe, {"FORCE_COLOR": "1"})
    assert not can_colorize(pipe, {"FORCE_COLOR": "1", "NO_COLOR": "1"})


# ---- notes and recipe, the long-form help behind the picker's `?`

NOTED = Registry()
NOTED.section("Build")


@NOTED.task("Build it")
def build_it(v: Vars) -> None:
    """What build does,
    in two lines.

    A second paragraph.
    """
    print("tools.build")
    print("done")


@NOTED.task("Check it", deps=("build-it",), name="check",
            defaults={"WIDTH": "60"})
def check_it(v: Vars) -> None:
    print("tools.check")


def test_notes_are_the_docstring_and_the_recipe_is_the_body():
    build_t, check_t = NOTED.sections()[0].targets
    assert build_t.notes == ("What build does,\nin two lines.\n\n"
                             "A second paragraph.")
    assert build_t.recipe == ('print("tools.build")', 'print("done")')
    assert build_t.prereqs == ()
    assert check_t.notes == ""
    assert check_t.recipe == ('print("tools.check")',)
    assert check_t.prereqs == ("build-it",)
    assert check_t.defaults == (("WIDTH", "60"),)


# ---- the real tools/tasks.py

def _real() -> list:
    return load_sections()


def test_the_real_listing_fits_eighty_columns():
    sections = _real()
    rendered = [render_all(sections, 80)]
    rendered += [render_section(s, 80) for s in sections if s.slug]
    for block in rendered:
        for line in block.splitlines():
            assert len(line) <= 80, line


def test_the_real_tasks_satisfy_every_invariant():
    check(_real())


def test_the_real_tasks_repeat_into_everyday():
    everyday = next(s for s in _real() if s.slug == "everyday")
    assert [t.name for t in everyday.targets if t.repeat], (
        "Everyday should repeat the common tasks")
    assert [t.name for t in everyday.listed()][0] == "verify-ch"


def test_the_real_tasks_have_notes_for_the_everyday_ones():
    targets = {t.name: t for s in _real() for t in s.targets}
    for name in ("verify", "gate", "sweep", "tools-upgrade"):
        assert targets[name].notes, name
        assert targets[name].recipe or targets[name].prereqs, name
    assert targets["verify"].recipe == ('py("tools.verify", '
                                        '*v.words("ARGS"))',)


def test_render_all_expands_every_section_and_folds_secondary():
    sections = _real()
    full = render_all(sections, 80)
    for section in sections:
        if section.slug:
            assert section.title in full
        for target in section.targets:
            shown = f"  {target.name} " in full
            assert shown is not target.secondary, target.name


def test_color_only_adds_escape_codes():
    """Stripping the codes from the colored listing gives the plain one,
    so color never moves a column or changes a wrap."""
    sections = _real()
    for plain, colored in [
        (render_all(sections, 80), render_all(sections, 80, ANSI)),
        (render_section(sections[1], 80),
         render_section(sections[1], 80, ANSI)),
    ]:
        assert "\x1b[" not in plain
        assert "\x1b[" in colored
        assert _ESCAPES.sub("", colored) == plain


def test_plain_palette_is_the_default():
    assert render_all(_real(), 80) == render_all(_real(), 80, PLAIN)


@pytest.mark.parametrize("slug", [s.slug for s in _real() if s.slug])
def test_every_real_section_renders(slug):
    section = next(s for s in _real() if s.slug == slug)
    assert section.listed(), f"section {slug} would render as an empty list"
    assert render_section(section).startswith(f"{slug}: {section.title}")


# ---- the time column

TIMES = {"eol": Timing("0.3s", "quick"),
         "build-thing": Timing("long", "long")}


def test_times_add_a_column_of_shared_width_and_a_legend():
    sections = SAMPLE.sections()
    lines = render_all(sections, 80, times=TIMES).splitlines()
    build_line = next(ln for ln in lines if ln.startswith("  build-thing"))
    eol = next(ln for ln in lines if ln.startswith("  eol"))
    assert build_line == "  build-thing  long  Build the thing"
    assert eol.startswith("  eol  0.3s  Check for CRLF")
    assert lines[-1].endswith("very long.") and LEGEND.startswith(lines[-2])
    assert render_all(sections, 80) == render_all(sections, 80, times={})


def test_time_column_is_colored_by_tier():
    sections = SAMPLE.sections()
    out = render_section(sections[1], 80, ANSI, TIMES)
    assert "[32m0.3s[0m" in out
    out = render_section(sections[0], 80, ANSI, TIMES)
    assert "[33mlong[0m" in out
    assert "[31m" not in out
