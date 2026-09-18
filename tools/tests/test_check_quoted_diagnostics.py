"""Tests for tools/check_quoted_diagnostics.py.

A quoted `ty` diagnostic is prose: nothing runs it, so a listing edit
that moves a quoted line goes unnoticed. The check compares each
quote's gutter lines with the extracted listing, keeps the deliberate
mismatches in a baseline, and reports the delta. These tests pin what
counts as a match, what is reported, and how the baseline behaves.
"""
from collections import Counter
from pathlib import Path

from tools import check_quoted_diagnostics as cqd
from tools.markdown import Document
from tools.report import Finding


def test_gutter_line_matches_ignore_span_bar_indent_and_ignores() -> None:
    assert cqd.gutter_matches("x = f(1)", "x = f(1)")
    assert cqd.gutter_matches("|     Need[A], str", "    Need[A], str")
    assert cqd.gutter_matches("x = f(1)", "x = f(1)  # type: ignore")
    assert cqd.gutter_matches("x = f(1)", "x = f(1)  # type: ignore[arg]")
    assert cqd.gutter_matches("x = f(1)", "# x = f(1)")
    assert not cqd.gutter_matches("x = f(2)", "x = f(1)")


def findings_for(md: Path, listing_dir: Path, text: str) -> list[Finding]:
    md.write_text(text, encoding="utf-8")
    cqd.TREES[md.parent.name] = listing_dir.parent
    try:
        return list(cqd.find(Document.parse(md)))
    finally:
        del cqd.TREES[md.parent.name]


def quoted(md: Path, listing_dir: Path, text: str) -> list[str]:
    return [f.message for f in findings_for(md, listing_dir, text)]


BLOCK = (
    "# text\n\n```text\n"
    "error[invalid-argument-type]: Argument is incorrect\n"
    " --> area.py:{n}:12\n"
    "  |\n"
    '{n} | print(area("3"))\n'
    "  |            ^^^ Expected `int`\n"
    "```\n")


def chapter_tree(tmp_path: Path) -> tuple[Path, Path]:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    (tree / "area.py").write_text(
        "# area.py\n\ndef area(w: int) -> int:\n    return w\n"
        'print(area("3"))\n', encoding="utf-8")
    return chapters / "05_F.md", tree


def test_matching_quote_is_silent_and_moved_line_is_reported(
        tmp_path: Path) -> None:
    md, tree = chapter_tree(tmp_path)
    assert quoted(md, tree, BLOCK.format(n=5)) == []
    hits = quoted(md, tree, BLOCK.format(n=4))
    assert len(hits) == 1
    assert "area.py:4 reads" in hits[0]


def test_missing_file_is_reported_once(tmp_path: Path) -> None:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    text = ("```text\nerror[x]: y\n --> gone.py:1:1\n"
            "1 | anything\n2 | more\n```\n")
    hits = quoted(chapters / "05_F.md", tree, text)
    assert len(hits) == 1
    assert "gone.py" in hits[0]


def test_bare_fence_and_warning_blocks_count(tmp_path: Path) -> None:
    chapters = tmp_path / "Chapters"
    chapters.mkdir()
    tree = tmp_path / "examples" / "05_F"
    tree.mkdir(parents=True)
    (tree / "w.py").write_text("a = 1\n", encoding="utf-8")
    text = "```\nwarning[deprecated]: z\n --> w.py:1:1\n1 | a = 2\n```\n"
    hits = quoted(chapters / "05_F.md", tree, text)
    assert len(hits) == 1 and "w.py:1 reads 'a = 1'" in hits[0]


# ── the baseline ─────────────────────────────────────────────────────────────

def test_entry_drops_the_markdown_line_number(tmp_path: Path) -> None:
    md, tree = chapter_tree(tmp_path)
    hit = findings_for(md, tree, BLOCK.format(n=4))[0]
    moved = findings_for(md, tree, "\n\n\n" + BLOCK.format(n=4))[0]
    assert hit.line != moved.line
    assert cqd.entry(hit) == cqd.entry(moved)
    assert cqd.entry(hit).split("\t", 1)[1] == hit.message


def test_delta_reports_new_and_gone_against_the_baseline(
        tmp_path: Path) -> None:
    md, tree = chapter_tree(tmp_path)
    hit = findings_for(md, tree, BLOCK.format(n=4))
    now, new, gone = cqd.delta(hit, Counter())
    assert sum(new.values()) == 1 and not gone
    accepted = now
    now, new, gone = cqd.delta(hit, accepted)
    assert not new and not gone
    now, new, gone = cqd.delta([], accepted)
    assert not new and sum(gone.values()) == 1


def test_baseline_round_trips_through_the_file(tmp_path: Path) -> None:
    path = tmp_path / "baseline.txt"
    entries = Counter({"Chapters/05_F.md\tarea.py:4 reads 'x', quote shows 'y'": 2,
                       "Solutions/05_F.md\tgone.py missing": 1})
    cqd.write_baseline(entries, path)
    text = path.read_text(encoding="utf-8")
    assert text.startswith("# Quoted ty diagnostics")
    assert cqd.load_baseline(path) == entries
    assert cqd.load_baseline(tmp_path / "absent.txt") == Counter()


def pragma_hits(tmp_path: Path, before: str, after: str = "") -> list[str]:
    """The `--pragmas` report for one quote made without the pragma."""
    md, tree = chapter_tree(tmp_path)
    listing = tree / "area.py"
    listing.write_text(
        listing.read_text(encoding="utf-8").replace(
            'print(area("3"))', 'print(area("3"))  # type: ignore'),
        encoding="utf-8")
    md.write_text(before + BLOCK.format(n=5).removeprefix("# text\n\n")
                  + after, encoding="utf-8")
    cqd.TREES[md.parent.name] = tree.parent
    try:
        return [f.message
                for f in cqd.find_unmentioned_pragmas(Document.parse(md))]
    finally:
        del cqd.TREES[md.parent.name]


def test_quote_without_the_pragma_needs_the_prose_to_say_so(
        tmp_path: Path) -> None:
    hits = pragma_hits(tmp_path, "`ty` now rejects the call:\n\n")
    assert len(hits) == 1
    assert "area.py:5 carries a `# type: ignore`" in hits[0]


def test_a_mention_above_the_quote_is_enough(tmp_path: Path) -> None:
    assert pragma_hits(
        tmp_path, "Without the `# type: ignore`, `ty` rejects it:\n\n") == []


def test_a_mention_below_the_quote_is_enough(tmp_path: Path) -> None:
    assert pragma_hits(
        tmp_path, "`ty` rejects it:\n\n",
        "\nThe `# type: ignore` silences that diagnostic.\n") == []


def test_a_heading_ends_the_prose_a_quote_can_claim(tmp_path: Path) -> None:
    hits = pragma_hits(
        tmp_path,
        "If you remove the `# type: ignore`, nothing changes.\n\n"
        "## 2. Another exercise\n\n`ty` rejects it:\n\n")
    assert len(hits) == 1


def test_a_listing_with_no_pragma_is_not_a_pragma_hit(
        tmp_path: Path) -> None:
    md, tree = chapter_tree(tmp_path)
    md.write_text(BLOCK.format(n=5), encoding="utf-8")
    cqd.TREES[md.parent.name] = tree.parent
    try:
        assert list(cqd.find_unmentioned_pragmas(Document.parse(md))) == []
    finally:
        del cqd.TREES[md.parent.name]


def test_a_scoped_run_ignores_other_files_baseline_entries() -> None:
    here = cqd.ROOT / "Chapters" / "30_Patterns--Observer.md"
    mine = "Chapters/30_Patterns--Observer.md\ta.py:1 reads 'x'"
    other = "Solutions/46_Effects--Stateless.md\tb.py:2 reads 'y'"
    accepted = Counter([mine, other])
    assert cqd.scoped(accepted, [here]) == Counter([mine])
    # Without the scoping, `other` would come back as GONE
    now, new, gone = cqd.delta([], cqd.scoped(accepted, [here]))
    assert gone == Counter([mine])
    assert not new
