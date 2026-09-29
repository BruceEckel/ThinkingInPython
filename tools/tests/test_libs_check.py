"""Tests for tools/libs_check.py and the PyPI half of tool_stamp.py.

`libs_check` reads uv.lock and asks PyPI for each package's latest
release; `tip tools-status` reports the comparison. These tests never
reach the network: `rows()` takes the lookup as an argument, the tests
of `pypi_latest()` stub `urlopen`, and the report's test stubs
`pypi_latest()` and `uv_version()`.
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


def test_locked_versions_reads_any_named_package() -> None:
    assert libs_check.locked_versions(LOCK, ("ruff", "ty")) == {
        "ruff": "0.16.8"}


def test_package_lines_note_behind_and_a_move_the_stamp_missed() -> None:
    lines = tool_stamp.package_lines(
        [("stateless", "0.7.0", "0.7.0"), ("numpy", "2.5.3", "2.5.4"),
         ("uv", "0.9.30", None)],
        {"stateless": "0.6.1", "numpy": "2.5.3"})
    assert lines == [
        "  stateless      0.7.0     latest 0.7.0"
        "   (was 0.6.1 at the last tools-upgrade)",
        "  numpy          2.5.3     latest 2.5.4   behind",
        "  uv             0.9.30    latest unknown (PyPI unreachable)"]


def test_upgrade_report_names_the_fix_for_each_kind_behind(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(tool_stamp, "uv_version", lambda: "0.9.30")
    monkeypatch.setattr(
        libs_check, "current",
        lambda names=libs_check.LIBRARIES:
            libs_check.locked_versions(LOCK, names))
    latest = {"uv": "0.9.31", "ruff": "0.16.8", "stateless": "0.7.0",
              "numpy": "2.5.3"}
    monkeypatch.setattr(libs_check, "pypi_latest", latest.get)
    tool_stamp.upgrade_report({})
    out = capsys.readouterr().out
    assert "uv             0.9.30    latest 0.9.31   behind" in out
    assert "ruff           0.16.8    latest 0.16.8\n" in out
    assert "`tip tools-upgrade`" in out
    assert "--upgrade-package" in out
