"""`upgrade_tools.update_external()`: what each winget exit code leads to.

No test here starts winget. `subprocess.run` and `shutil.which` are
replaced, and each test states the exit codes winget returns.
"""
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from tools import upgrade_tools as ut

PANDOC = ("pandoc", "JohnMacFarlane.Pandoc", "pandoc", "https://x/install")


@dataclass
class FakeWinget:
    """Stands in for `subprocess.run`: one exit code per call, in order."""
    codes: list[int] = field(default_factory=list)
    calls: list[list[str]] = field(default_factory=list)

    def run(self, cmd: list[str]) -> SimpleNamespace:
        self.calls.append(cmd)
        return SimpleNamespace(returncode=self.codes.pop(0))


@pytest.fixture
def winget(monkeypatch: pytest.MonkeyPatch) -> FakeWinget:
    """Make winget the only package manager on PATH."""
    fake = FakeWinget()
    monkeypatch.setattr(
        ut.shutil, "which",
        lambda name: "winget.exe" if name == "winget" else None)
    monkeypatch.setattr(ut.subprocess, "run", fake.run)
    return fake


def terminal(monkeypatch: pytest.MonkeyPatch, attached: bool) -> None:
    monkeypatch.setattr(ut.sys.stdout, "isatty", lambda: attached,
                        raising=False)


@pytest.mark.parametrize("code", [0, ut.WINGET_ALREADY_LATEST,
                                  # The signed form subprocess can return:
                                  ut.WINGET_ALREADY_LATEST - 2**32])
def test_a_clean_upgrade_runs_winget_once_and_reports_no_failure(
    winget: FakeWinget, capsys: pytest.CaptureFixture[str], code: int,
) -> None:
    winget.codes = [code]
    ut.update_external(*PANDOC)
    assert len(winget.calls) == 1
    assert "--silent" in winget.calls[0]
    assert "Could not" not in capsys.readouterr().out


def test_a_failed_uninstall_with_no_terminal_prints_the_elevated_command(
    winget: FakeWinget, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    terminal(monkeypatch, attached=False)
    winget.codes = [ut.WINGET_UNINSTALL_FAILED]
    ut.update_external(*PANDOC)
    out = capsys.readouterr().out
    # No interactive retry: nobody is there to answer the prompt.
    assert len(winget.calls) == 1
    assert "administrator rights" in out
    assert "winget upgrade --id JohnMacFarlane.Pandoc --silent" in out
    assert "https://x/install" not in out


def test_a_failed_uninstall_at_a_terminal_retries_interactively(
    winget: FakeWinget, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    terminal(monkeypatch, attached=True)
    winget.codes = [ut.WINGET_UNINSTALL_FAILED - 2**32, 0]
    ut.update_external(*PANDOC)
    assert [cmd[-1] for cmd in winget.calls] == [
        "--silent", "--interactive"]
    assert "Could not" not in capsys.readouterr().out


def test_a_declined_interactive_retry_prints_the_elevated_command(
    winget: FakeWinget, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    terminal(monkeypatch, attached=True)
    winget.codes = [ut.WINGET_UNINSTALL_FAILED] * 2
    ut.update_external(*PANDOC)
    assert len(winget.calls) == 2
    assert "administrator rights" in capsys.readouterr().out


def test_any_other_failure_prints_the_install_link(
    winget: FakeWinget, capsys: pytest.CaptureFixture[str],
) -> None:
    winget.codes = [0x8A150014]  # No installed package found
    ut.update_external(*PANDOC)
    assert len(winget.calls) == 1
    assert "https://x/install" in capsys.readouterr().out
