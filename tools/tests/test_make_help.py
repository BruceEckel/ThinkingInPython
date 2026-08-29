"""Tests for tools/make_help.py: parsing, the three-level listing, invariants.

The real Makefile is exercised at the end, so a heading or doc comment that
breaks the conventions fails here rather than at the next `make help`.
"""
import pytest

from make_help import (
    MAKEFILE, MAX_WIDTH, MIN_DOC, PROMOTED, check, entries, parse,
    render_all, render_index, render_section, terminal_width)

SAMPLE = """\
help:  ## Show this help
\t@echo hi

##@ Build and site

build-thing:  ## Build the thing
\t@echo build

hidden:  ##- A secondary target

##@ Style gates

eol:  ## Check for CRLF; `make fix-eol` converts them
fix-eol:  ##- Convert CRLF to LF
undocumented:
\t@echo nothing
"""


def test_parse_groups_targets_under_headings():
    sections = parse(SAMPLE)
    assert [s.slug for s in sections] == ["", "build", "style"]
    assert [s.title for s in sections] == ["", "Build and site", "Style gates"]
    assert [t.name for t in sections[1].targets] == ["build-thing", "hidden"]


def test_slug_is_the_headings_first_word_lowercased():
    assert parse("##@ Code examples (build/examples/)\nx:  ## d\n")[0].slug == (
        "code")


def test_undocumented_targets_are_left_out():
    assert "undocumented" not in {n for n, _ in entries(SAMPLE) if n}


def test_secondary_targets_stay_in_entries_but_leave_the_listing():
    """verify_targets.py enumerates through entries(), so `##-` must not
    remove a target from the smoke test."""
    assert "hidden" in {n for n, _ in entries(SAMPLE) if n}
    build = parse(SAMPLE)[1]
    assert [t.name for t in build.listed()] == ["build-thing"]


def test_entries_keeps_the_flat_shape_its_callers_expect():
    assert (None, "Build and site") in entries(SAMPLE)
    assert ("build-thing", "Build the thing") in entries(SAMPLE)


def test_render_section_shows_only_listed_targets():
    rendered = render_section(parse(SAMPLE)[1])
    assert "build-thing" in rendered
    assert "hidden" not in rendered


def test_duplicate_slugs_are_rejected():
    text = "##@ Style gates\na:  ## d\n##@ Style rules\nb:  ## d\n"
    with pytest.raises(SystemExit, match="share the slug"):
        check(parse(text))


def test_a_slug_that_shadows_a_target_is_rejected():
    """The Makefile's `help` guard would override that recipe."""
    text = "##@ Prose and spelling\nprose:  ## Lint with Vale\n"
    with pytest.raises(SystemExit, match="also a target name"):
        check(parse(text))


def test_missing_promoted_target_is_rejected():
    with pytest.raises(SystemExit, match="PROMOTED"):
        check(parse("##@ Build and site\nbuild-thing:  ## d\n"))


LONG = "##@ Style gates\nx:  ## " + "word " * 40 + "\n"


def test_doc_text_wraps_to_the_given_width():
    lines = render_section(parse(LONG)[0], 60).splitlines()
    assert len(lines) > 2
    assert all(len(line) <= 60 for line in lines)


def test_continuation_lines_align_under_the_doc_column():
    lines = render_section(parse(LONG)[0], 60).splitlines()[1:]
    start = lines[0].index("word")
    assert all(len(line) - len(line.lstrip()) == start for line in lines[1:])


def test_a_backticked_command_is_never_split_across_lines():
    text = "##@ Style gates\neol:  ## " + "pad " * 12 + "`make fix-eol` ok\n"
    for line in render_section(parse(text)[0], 60).splitlines():
        assert line.count("`") % 2 == 0, line
    assert "`make fix-eol`" in render_section(parse(text)[0], 60)


def test_a_hyphenated_target_name_is_never_split():
    text = "##@ Style gates\nfix-comment-spacing:  ## " + "pad " * 20 + "\n"
    body = render_section(parse(text)[0], 40)
    assert "fix-comment-spacing" in body
    assert "fix-comment-\n" not in body


def test_too_narrow_to_wrap_falls_back_to_one_long_line():
    """Below MIN_DOC the doc column would be shredded, so leave it alone."""
    lines = render_section(parse(LONG)[0], MIN_DOC).splitlines()
    assert len(lines) == 2


def test_width_is_capped_and_overridable():
    assert terminal_width(300) == 300
    assert terminal_width() <= MAX_WIDTH


def _real() -> list:
    return parse(MAKEFILE.read_text(encoding="utf-8"))


def test_the_real_listing_fits_eighty_columns():
    sections = _real()
    rendered = [render_index(sections, 80), render_all(sections, 80)]
    rendered += [render_section(s, 80) for s in sections if s.slug]
    for block in rendered:
        for line in block.splitlines():
            assert len(line) <= 80, line


def test_the_real_makefile_satisfies_every_invariant():
    check(_real())


def test_the_real_index_lists_every_section_and_promoted_target():
    index = render_index(_real())
    for section in _real():
        if section.slug:
            assert f"  {section.slug}" in index
    for name in PROMOTED:
        assert name in index


def test_render_all_expands_every_section_and_folds_secondary():
    sections = _real()
    full = render_all(sections, 80)
    for section in sections:
        if section.slug:
            assert section.title in full
        for target in section.targets:
            shown = f"  {target.name} " in full
            assert shown is not target.secondary, target.name


@pytest.mark.parametrize("slug", [s.slug for s in _real() if s.slug])
def test_every_real_section_renders(slug):
    section = next(s for s in _real() if s.slug == slug)
    assert section.listed(), f"section {slug} would render as an empty list"
    assert render_section(section).startswith(section.title)
