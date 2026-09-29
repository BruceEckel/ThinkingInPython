"""Tests for tools/run_examples.py's run_one()."""
from pathlib import Path

from tools.run_examples import run_one

HANGS_ONCE = """\
import time
from pathlib import Path
flag = Path("ran.flag")
if not flag.exists():
    flag.write_text("")
    time.sleep(600)
"""


def script(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "demo.py"
    p.write_text(body, encoding="utf-8")
    return p


def test_run_one_passes(tmp_path: Path) -> None:
    p = script(tmp_path, "print('hi')\n")
    assert run_one(p, "ch/demo.py", 30, tmp_path) == (
        "passed", "ch/demo.py", "")


def test_run_one_reports_the_last_stderr_line(tmp_path: Path) -> None:
    p = script(tmp_path, "raise ValueError('nope')\n")
    assert run_one(p, "ch/demo.py", 30, tmp_path) == (
        "failed", "ch/demo.py", "ValueError: nope")


def test_run_one_reruns_an_example_that_times_out(tmp_path: Path) -> None:
    p = script(tmp_path, HANGS_ONCE)
    assert run_one(p, "ch/demo.py", 3, tmp_path) == (
        "passed", "ch/demo.py", "")


def test_run_one_times_out_when_every_run_hangs(tmp_path: Path) -> None:
    p = script(tmp_path, "import time\ntime.sleep(600)\n")
    assert run_one(p, "ch/demo.py", 1, tmp_path) == (
        "timeout", "ch/demo.py", "")
