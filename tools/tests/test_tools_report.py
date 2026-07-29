"""Tests for tools/tools_report.py (Finding formatting and the reporter)."""
from pathlib import Path

import pytest

from tools_report import Finding, report

# ── Finding.format ────────────────────────────────────────────────────────────

def test_format_line_only() -> None:
    # The path prints as os.fspath renders it, so the separator is the
    # platform's; that is what the tools have always printed.
    path = Path("Chapters/46_Stateless.md")
    f = Finding(path, 12, "something is wrong")
    assert f.format() == f"{path}:12: something is wrong"

def test_format_with_col() -> None:
    f = Finding(Path("a.md"), 3, "banned phrase", col=7)
    assert f.format() == "a.md:3:7: banned phrase"

def test_format_with_code() -> None:
    f = Finding(Path("a.md"), 3, "wordy", col=7, code="P001")
    assert f.format() == "a.md:3:7: P001 wordy"

def test_format_code_without_col() -> None:
    f = Finding(Path("a.md"), 3, "wordy", code="P001")
    assert f.format() == "a.md:3: P001 wordy"

def test_col_zero_is_printed_not_dropped() -> None:
    # None means "no column"; 0 is a column, so falsiness must not decide.
    assert Finding(Path("a.md"), 1, "m", col=0).format() == "a.md:1:0: m"

# ── report ────────────────────────────────────────────────────────────────────

def test_report_clean_prints_clean_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert report([], clean="All good.", problem="{n} bad.") == 0
    assert capsys.readouterr().out == "All good.\n"

def test_report_findings_exit_one_and_summarize(
    capsys: pytest.CaptureFixture[str],
) -> None:
    findings = [
        Finding(Path("a.md"), 1, "first"),
        Finding(Path("b.md"), 2, "second", col=4),
    ]
    assert report(findings, clean="ok", problem="{n} problem(s). Fix them.") == 1
    assert capsys.readouterr().out == (
        "a.md:1: first\n"
        "b.md:2:4: second\n"
        "\n2 problem(s). Fix them.\n"
    )

def test_report_counts_a_generator_it_consumes_once(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Checks yield lazily; the count must come from iteration, not len().
    findings = (Finding(Path("a.md"), i, "x") for i in (1, 2, 3))
    assert report(findings, clean="ok", problem="{n} found.") == 1
    assert capsys.readouterr().out.endswith("\n3 found.\n")

def test_report_problem_without_placeholder_is_left_alone(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert report([Finding(Path("a.md"), 1, "x")],
                  clean="ok", problem="Something is wrong.") == 1
    assert capsys.readouterr().out.endswith("\nSomething is wrong.\n")
