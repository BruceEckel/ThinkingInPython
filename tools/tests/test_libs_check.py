"""Tests for tools/libs_check.py and the library half of tool_stamp.py.

`libs_check` reads uv.lock and asks PyPI for each library's latest
release. These tests never reach the network: `rows()` takes the lookup
as an argument, and the one test of `pypi_latest()` stubs `urlopen`.
"""
import io
import urllib.error

import pytest

from tools import libs_check, tool_stamp

LOCK = '''
version = 1

[[package]]
name = "stateless"
version = "0.6.1"

[[package]]
name = "numpy"
version = "2.5.3"

[[package]]
name = "ruff"
version = "0.16.8"

[[package]]
name = "thinking-in-python"
source = { virtual = "." }
'''


def test_locked_versions_keeps_the_libraries_and_drops_the_rest() -> None:
    assert libs_check.locked_versions(LOCK) == {
        "stateless": "0.6.1", "numpy": "2.5.3"}


def test_rows_pair_each_locked_version_with_the_lookup() -> None:
    latest = {"stateless": "0.7.0", "numpy": "2.5.3"}
    assert libs_check.rows(
        libs_check.locked_versions(LOCK), latest.get) == [
        ("stateless", "0.6.1", "0.7.0"), ("numpy", "2.5.3", "2.5.3")]


def test_pypi_latest_reads_the_version_field(
        monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(url: str, timeout: float) -> io.BytesIO:
        assert url.endswith("/stateless/json")
        return io.BytesIO(b'{"info": {"version": "0.7.0"}}')
    monkeypatch.setattr(libs_check.urllib.request, "urlopen", fake_urlopen)
    assert libs_check.pypi_latest("stateless") == "0.7.0"


def test_pypi_latest_is_none_when_pypi_is_unreachable(
        monkeypatch: pytest.MonkeyPatch) -> None:
    def offline(url: str, timeout: float) -> io.BytesIO:
        raise urllib.error.URLError("no route")
    monkeypatch.setattr(libs_check.urllib.request, "urlopen", offline)
    assert libs_check.pypi_latest("stateless") is None


def test_main_reports_behind_and_unknown_and_still_exits_zero(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        libs_check, "current", lambda: libs_check.locked_versions(LOCK))
    latest = {"stateless": "0.7.0"}
    monkeypatch.setattr(libs_check, "pypi_latest", latest.get)
    monkeypatch.setattr(
        libs_check, "rows",
        lambda locked: [(n, v, latest.get(n)) for n, v in locked.items()])
    assert libs_check.main() == 0
    out = capsys.readouterr().out
    assert "stateless" in out and "latest 0.7.0   behind" in out
    assert "latest unknown" in out
    assert "--upgrade-package" in out


def test_library_lines_note_a_move_the_stamp_missed() -> None:
    lines = tool_stamp.library_lines(
        {"stateless": "0.7.0", "numpy": "2.5.3"},
        {"stateless": "0.6.1", "numpy": "2.5.3"})
    assert lines == [
        "  stateless: 0.7.0 (was 0.6.1 at the last tools-upgrade)",
        "  numpy: 2.5.3"]
