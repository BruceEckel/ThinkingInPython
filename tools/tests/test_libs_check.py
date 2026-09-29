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

from tools import libs_check, tasks, tool_stamp
from tools.tip import StepFailed, Vars

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


def stub_report(monkeypatch: pytest.MonkeyPatch, *, behind: bool,
                tty: bool, answer: str) -> list[str]:
    """Stub the stamp, PyPI, the terminal, and the reply to the offer."""
    asked: list[str] = []
    monkeypatch.setattr(tool_stamp, "read_stamp", lambda: {})
    monkeypatch.setattr(
        tool_stamp, "last_upgrade",
        lambda: (tool_stamp.datetime.now(), {}, "tools-upgrade"))
    monkeypatch.setattr(
        tool_stamp, "upgrade_report",
        lambda stamped: {"ty"} if behind else set())
    monkeypatch.setattr(tool_stamp, "interactive", lambda: tty)

    def reply(prompt: str) -> str:
        asked.append(prompt)
        return answer
    monkeypatch.setattr("builtins.input", reply)
    return asked


@pytest.mark.parametrize(("behind", "tty", "answer", "status", "asks"), [
    (True, True, "y", tool_stamp.UPGRADE_REQUESTED, True),
    (True, True, "", 0, True),
    (True, False, "y", 0, False),
    (False, True, "y", 0, False),
])
def test_offer_asks_only_a_person_and_only_when_behind(
        monkeypatch: pytest.MonkeyPatch, behind: bool, tty: bool,
        answer: str, status: int, asks: bool) -> None:
    asked = stub_report(monkeypatch, behind=behind, tty=tty, answer=answer)
    assert tool_stamp.report(
        nag_only=False, days=14, offer=True) == status
    assert bool(asked) == asks


def test_no_offer_without_the_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    asked = stub_report(monkeypatch, behind=True, tty=True, answer="y")
    assert tool_stamp.report(nag_only=False, days=14) == 0
    assert not asked


def test_interactive_is_false_in_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CI", "1")
    assert not tool_stamp.interactive()


@pytest.mark.parametrize(("code", "upgrades"), [
    (tool_stamp.UPGRADE_REQUESTED, True), (None, False)])
def test_tools_status_task_runs_the_upgrade_only_on_yes(
        monkeypatch: pytest.MonkeyPatch, code: int | None,
        upgrades: bool) -> None:
    ran: list[str] = []

    def step(module: str, *args: str) -> None:
        assert args == ("--offer",)
        if code is not None:
            raise StepFailed(code)
    monkeypatch.setattr(tasks, "py", step)
    monkeypatch.setattr(tasks, "invoke", lambda name, v: ran.append(name))
    tasks.tools_status(Vars())
    assert ran == (["tools-upgrade"] if upgrades else [])


def test_tools_status_task_passes_other_failures_on(
        monkeypatch: pytest.MonkeyPatch) -> None:
    def step(module: str, *args: str) -> None:
        raise StepFailed(1)
    monkeypatch.setattr(tasks, "py", step)
    with pytest.raises(StepFailed):
        tasks.tools_status(Vars())
