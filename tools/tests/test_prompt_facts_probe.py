"""Tests for tools/prompt_facts_probe.py (no real `agy` call)."""
import json
import subprocess
import sys
from pathlib import Path
import pytest
from tools import prompt_facts_probe as probe
from tools.config import ROOT
from tools.prompt_facts_probe import (
    HEADING,
    RUNS_INTRO,
    build_message,
    parse_facts,
    parse_verdicts,
    report_lines,
    save_run,
)

FIXTURE = f"""Review the chapter.

{HEADING}

- first fact; with a semicolon
- second fact
- third fact

A trailing paragraph.
- not a fact
"""


def result_line(result: dict[str, object]) -> str:
    """One NDJSON `result` event, as `agy` prints it."""
    return json.dumps({"event": "result", "result": result}) + "\n"


class FakeAgy:
    """Replaces `subprocess.run`, answering from a script of stdouts."""

    def __init__(self, stdouts: list[str], returncode: int = 0) -> None:
        self.stdouts = list(stdouts)
        self.returncode = returncode
        self.calls = 0

    def __call__(
        self, argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        stdout = self.stdouts[self.calls]
        self.calls += 1
        return subprocess.CompletedProcess(
            argv, self.returncode, stdout=stdout, stderr=""
        )


REPLY = result_line({
    "status": "SUCCESS",
    "response": "1. TRUE: yes\n2. FALSE: no, in 3.14\n3. TRUE: ok",
})


def run_main(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *extra: str
) -> int:
    prompt = tmp_path / "prompt.md"
    prompt.write_text(FIXTURE, encoding="utf-8")
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setattr(probe, "find_agy", lambda: "agy")
    monkeypatch.setattr(
        sys, "argv", ["probe", "--prompt", str(prompt), *extra])
    return probe.main()


def test_parse_facts_reads_the_bullets_in_order() -> None:
    assert parse_facts(FIXTURE) == [
        "first fact; with a semicolon", "second fact", "third fact"]


def test_parse_facts_requires_the_heading() -> None:
    with pytest.raises(ValueError, match="no line"):
        parse_facts("- a bullet\n")


def test_parse_facts_on_the_real_prompt() -> None:
    path = ROOT / "tools" / "data" / "outside_review_prompt.md"
    facts = parse_facts(path.read_text(encoding="utf-8"))
    assert len(facts) >= 10
    assert "sentinel()" in facts[0]


def test_build_message_numbers_facts_and_drops_the_framing() -> None:
    message = build_message(["alpha", "beta"])
    assert "1. alpha\n2. beta" in message
    for word in ("TRUE", "FALSE", "UNSURE"):
        assert word in message
    assert "Treat these as valid" not in message


def test_parse_verdicts_tolerates_formatting() -> None:
    reply = ("1. TRUE: fine\n"
             "**2.** FALSE: it is a SyntaxError\n"
             "3) unsure\n"
             "junk line\n"
             "9. TRUE: out of range\n")
    assert parse_verdicts(reply, 3) == {
        1: ("TRUE", "fine"),
        2: ("FALSE", "it is a SyntaxError"),
        3: ("UNSURE", ""),
    }


def test_report_lines_marks_disputed_and_missing() -> None:
    lines = report_lines(
        ["a", "b", "c"],
        {1: ("TRUE", ""), 2: ("FALSE", "wrong in 3.14")},
    )
    row2 = next(i for i, ln in enumerate(lines) if "FALSE" in ln)
    assert lines[row2].split()[2] == "no"
    assert "wrong in 3.14" in lines[row2 + 1]
    row3 = next(ln for ln in lines if "NONE" in ln)
    assert row3.split()[2] == "no"
    assert "2 of 3" in lines[-1]


def test_main_prints_the_table(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = FakeAgy([REPLY])
    monkeypatch.setattr(probe.subprocess, "run", fake)
    assert run_main(monkeypatch, tmp_path) == 0
    assert fake.calls == 1
    assert "1 of 3 statements still disputed" in capsys.readouterr().out


def test_dry_run_calls_nothing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = FakeAgy([REPLY])
    monkeypatch.setattr(probe.subprocess, "run", fake)
    assert run_main(monkeypatch, tmp_path, "--dry-run") == 0
    assert fake.calls == 0
    assert probe.DEFAULT_MODEL in capsys.readouterr().out


def test_refuses_under_ci(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fake = FakeAgy([REPLY])
    monkeypatch.setattr(probe.subprocess, "run", fake)
    prompt = tmp_path / "prompt.md"
    prompt.write_text(FIXTURE, encoding="utf-8")
    monkeypatch.setenv("CI", "1")
    monkeypatch.setattr(sys, "argv", ["probe", "--prompt", str(prompt)])
    assert probe.main() == 1
    assert fake.calls == 0


def test_save_run_starts_the_file_once_and_appends_each_run(
    tmp_path: Path,
) -> None:
    log = tmp_path / "runs.md"
    save_run(log, "model-a", ["row 1", "summary"])
    save_run(log, "model-b", ["row 1", "summary"])
    text = log.read_text(encoding="utf-8")
    assert text.startswith(RUNS_INTRO)
    assert text.count("# Prompt facts probe runs") == 1
    assert text.index("## model-a, ") < text.index("## model-b, ")
    assert text.count("```\nrow 1\nsummary\n```") == 2
    assert "\r" not in log.read_bytes().decode("utf-8")


def test_save_option_appends_the_table(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake = FakeAgy([REPLY])
    monkeypatch.setattr(probe.subprocess, "run", fake)
    log = tmp_path / "runs.md"
    assert run_main(monkeypatch, tmp_path, "--save", str(log)) == 0
    text = log.read_text(encoding="utf-8")
    assert "1 of 3 statements still disputed" in text
    assert f"## {probe.DEFAULT_MODEL}, " in text
    assert f"appended to {log}" in capsys.readouterr().out
