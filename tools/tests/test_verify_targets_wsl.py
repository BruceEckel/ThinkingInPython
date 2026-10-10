"""Tests for tools/verify_targets_wsl.py: the path, the script, the run."""
import subprocess
from pathlib import PurePosixPath, PureWindowsPath

import pytest

from tools import verify_targets_wsl as wsl
from tools.verify_targets_wsl import main, mount_path, script


def test_mount_path_maps_a_drive_and_leaves_a_posix_path() -> None:
    assert (mount_path(PureWindowsPath(r"C:\git\ThinkingInPython"))
            == "/mnt/c/git/ThinkingInPython")
    assert (mount_path(PureWindowsPath(r"D:\Some Dir\x"))
            == "/mnt/d/Some Dir/x")
    assert mount_path(PurePosixPath("/home/b/x")) == "/home/b/x"


def test_script_resets_fast_forwards_then_runs() -> None:
    text = script("/mnt/c/git/Thinking In Python", "~/ThinkingInPython",
                  "master", ["--only", "gate", "ci"])
    lines = text.splitlines()
    assert lines[0] == "set -e"
    assert lines[1] == "cd ~/ThinkingInPython"
    assert lines[2] == "git checkout -- ."
    assert lines[3] == ("git fetch --quiet "
                        "'/mnt/c/git/Thinking In Python' master")
    assert lines[4] == "git merge --ff-only FETCH_HEAD"
    assert lines[5] == "uv run python -m tools.verify_targets --only gate ci"
    assert script("/mnt/c/x", "~/x", "master", []).endswith(
        "python -m tools.verify_targets")


def test_dry_run_prints_the_script_and_runs_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(wsl.subprocess, "run", _never)
    monkeypatch.setattr(wsl.shutil, "which", lambda name: None)
    assert main(["--dry-run", "--only", "gate"]) == 0
    out = capsys.readouterr().out
    assert "git merge --ff-only FETCH_HEAD" in out
    assert out.rstrip().endswith("tools.verify_targets --only gate")


def test_refuses_without_wsl(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(wsl.subprocess, "run", _never)
    monkeypatch.setattr(wsl.shutil, "which", lambda name: None)
    assert main([]) == 2
    assert "wsl is not on PATH" in capsys.readouterr().err


def test_runs_wsl_with_the_script_and_forwards_the_rest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], float]] = []

    def fake_run(
        argv: list[str], timeout: float,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((argv, timeout))
        return subprocess.CompletedProcess(argv, 3)

    monkeypatch.setattr(wsl.subprocess, "run", fake_run)
    monkeypatch.setattr(wsl.shutil, "which", lambda name: r"C:\w\wsl.exe")
    assert main(["--limit", "2", "--only", "gate", "--timeout", "5"]) == 3
    [(argv, timeout)] = calls
    assert argv[:4] == [r"C:\w\wsl.exe", "-e", "bash", "-lc"]
    assert argv[4].endswith("tools.verify_targets --only gate --timeout 5")
    assert f"cd {wsl.CLONE}" in argv[4]
    assert timeout == 120


def test_a_timeout_is_reported_as_a_failure(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    def slow(argv: list[str], timeout: float) -> None:
        raise subprocess.TimeoutExpired(argv, timeout)

    monkeypatch.setattr(wsl.subprocess, "run", slow)
    monkeypatch.setattr(wsl.shutil, "which", lambda name: "wsl")
    assert main(["--limit", "1"]) == 1
    assert "no result after 1 minute" in capsys.readouterr().err


def _never(*args: object, **kwargs: object) -> None:
    raise AssertionError("subprocess.run was called")
