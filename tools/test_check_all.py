"""Tests for tools/check_all.py (the registry and the combined runner)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pytest

from check_all import CHECKS, apply_fixes, by_name, main, run, select
from tools_markdown import Document

# A listing that trips three checks at once: two blank lines between
# imports, a trailing period, and a one-space inline comment gap.
DIRTY = (
    "Text.\n"
    "\n"
    "```python\n"
    "# demo.py\n"
    "import os\n"
    "\n"
    "\n"
    "x = 1   # trailing thing.\n"
    "```\n"
)

# ── registry ──────────────────────────────────────────────────────────────────

def test_every_check_has_a_unique_name() -> None:
    names = [check.name for check in CHECKS]
    assert len(names) == len(set(names))

def test_every_check_has_messages() -> None:
    for check in CHECKS:
        assert check.clean and check.problem and check.doc

def test_select_defaults_to_everything() -> None:
    assert select([]) == CHECKS

def test_select_by_name_preserves_request_order() -> None:
    assert [c.name for c in select(["banned", "listings"])] == [
        "banned", "listings",
    ]

def test_select_rejects_an_unknown_name() -> None:
    with pytest.raises(SystemExit, match="unknown check"):
        select(["nope"])

def test_by_name_covers_every_check() -> None:
    assert set(by_name()) == {c.name for c in CHECKS}

# ── running ───────────────────────────────────────────────────────────────────

def test_run_sorts_into_reading_order() -> None:
    doc = Document.from_text(DIRTY, Path("a.md"))
    findings = run(CHECKS, [doc])
    # Sorted by line even though different checks produced them.
    assert [f.line for f in findings] == sorted(f.line for f in findings)
    assert len(findings) == 3

def test_run_with_one_check_finds_only_its_own() -> None:
    doc = Document.from_text(DIRTY, Path("a.md"))
    findings = run(select(["comment-periods"]), [doc])
    assert len(findings) == 1
    assert "period" in findings[0].message

def test_run_on_clean_text_finds_nothing() -> None:
    doc = Document.from_text("```python\n# a.py\nx = 1  # fine\n```\n")
    assert run(CHECKS, [doc]) == []

# ── fixing ────────────────────────────────────────────────────────────────────

def test_apply_fixes_converges_to_clean(tmp_path: Path) -> None:
    p = tmp_path / "ch.md"
    p.write_text(DIRTY, encoding="utf-8")
    assert apply_fixes(CHECKS, [Document.parse(p)]) == 1
    # Re-parsing the rewritten file must now satisfy every check, which
    # only holds if each fixer saw the previous fixer's line numbers.
    assert run(CHECKS, [Document.parse(p)]) == []

def test_apply_fixes_leaves_a_clean_file_alone(tmp_path: Path) -> None:
    text = "```python\n# a.py\nx = 1  # fine\n```\n"
    p = tmp_path / "ch.md"
    p.write_text(text, encoding="utf-8")
    assert apply_fixes(CHECKS, [Document.parse(p)]) == 0
    assert p.read_text(encoding="utf-8") == text

# ── main ──────────────────────────────────────────────────────────────────────

def test_main_reports_and_exits_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "ch.md").write_text(DIRTY, encoding="utf-8")
    assert main(["--paths", str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "3 issue(s) in 1 file(s) from 4 check(s)." in out

def test_main_clean_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "ch.md").write_text("Fine.\n", encoding="utf-8")
    assert main(["--paths", str(tmp_path)]) == 0
    assert "clean" in capsys.readouterr().out

def test_main_list_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--list"]) == 0
    out = capsys.readouterr().out
    for check in CHECKS:
        assert check.name in out

def test_main_selects_a_single_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    (tmp_path / "ch.md").write_text(DIRTY, encoding="utf-8")
    assert main(["listings", "--paths", str(tmp_path)]) == 1
    assert "from 1 check(s)." in capsys.readouterr().out
