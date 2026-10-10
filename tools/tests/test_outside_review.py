"""Tests for tools/outside_review.py (rerunning transient `agy` failures)."""
import json
import subprocess
from pathlib import Path

import pytest

from tools import outside_review
from tools.outside_review import OUTPUT_LIMIT_ERROR, review_with_retries

CHAPTER = Path("Chapters/30_Patterns--Observer.md")


def result_line(result: dict[str, object]) -> str:
    """One NDJSON `result` event, as `agy` prints it."""
    return json.dumps({"event": "result", "result": result}) + "\n"


TOKEN_LIMIT = result_line({
    "status": "ERROR",
    "error": f"Generation stopped: the model {OUTPUT_LIMIT_ERROR}.",
})
DENIED = result_line({
    "status": "SUCCESS",
    "response": "",
    "denied_actions": [{"action": "run_command"}],
})
SUCCESS = result_line({
    "status": "SUCCESS",
    "response": "## Review\n\n1. fine",
    "usage": {},
    "duration_seconds": 3,
})
QUOTA = result_line({"status": "ERROR", "error": "quota"})


class FakeAgy:
    """Replaces `subprocess.run`, answering from a script of stdouts."""

    def __init__(self, stdouts: list[str], returncode: int = 0) -> None:
        self.stdouts = list(stdouts)
        self.returncode = returncode
        self.calls = 0

    def __call__(
        self, argv: list[str], **kwargs: object
    ) -> "subprocess.CompletedProcess[str]":
        stdout = self.stdouts[self.calls]
        self.calls += 1
        return subprocess.CompletedProcess(
            argv, self.returncode, stdout=stdout, stderr=""
        )


def install(monkeypatch: pytest.MonkeyPatch, fake: FakeAgy) -> None:
    monkeypatch.setattr(outside_review.subprocess, "run", fake)


def review(out_dir: Path, retries: int) -> bool:
    return review_with_retries(
        CHAPTER, ["agy"], "msg", "model", out_dir, 10, "", retries
    )


def test_transient_failures_are_rerun_until_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakeAgy([TOKEN_LIMIT, DENIED, SUCCESS])
    install(monkeypatch, fake)
    assert review(tmp_path, retries=2)
    assert fake.calls == 3
    saved = tmp_path / "30_Patterns--Observer.md"
    assert "## Review" in saved.read_text(encoding="utf-8")


def test_each_attempt_is_numbered_in_the_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    install(monkeypatch, FakeAgy([TOKEN_LIMIT, DENIED, SUCCESS]))
    assert review(tmp_path, retries=2)
    out = capsys.readouterr().out
    assert "attempt 1/3" in out
    assert "attempt 2/3" in out
    assert "attempt 3/3" in out
    assert "rerunning (2/3)" in out


def test_giving_up_after_the_last_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = FakeAgy([DENIED, DENIED, DENIED])
    install(monkeypatch, fake)
    assert not review(tmp_path, retries=2)
    assert fake.calls == 3
    assert not (tmp_path / "30_Patterns--Observer.md").exists()
    assert "giving up after 3 attempt(s)" in capsys.readouterr().out


def test_other_error_is_final_and_not_rerun(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakeAgy([QUOTA, SUCCESS])
    install(monkeypatch, fake)
    assert not review(tmp_path, retries=2)
    assert fake.calls == 1


def test_zero_retries_makes_one_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = FakeAgy([DENIED, DENIED, DENIED])
    install(monkeypatch, fake)
    assert not review(tmp_path, retries=0)
    assert fake.calls == 1
    assert "attempt 1/1" in capsys.readouterr().out


def test_nonzero_exit_is_final_even_with_a_good_reply(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakeAgy([SUCCESS, SUCCESS], returncode=1)
    install(monkeypatch, fake)
    assert not review(tmp_path, retries=2)
    assert fake.calls == 1
