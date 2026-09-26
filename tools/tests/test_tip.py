"""Tests for tools/tip.py: the command line, the runner, and timing."""
import subprocess
import sys
from unittest import mock

import pytest

from tools import tip
from tools.config import ROOT
from tools.tip import (
    NESTED, Registry, Runner, StepFailed, Vars, format_seconds, main,
    parse_argv, report, unknown)


def test_format_seconds_under_a_minute() -> None:
    assert format_seconds(0.04) == "0.0s"
    assert format_seconds(12.34) == "12.3s"
    assert format_seconds(59.96) == "60.0s"


def test_format_seconds_minutes_and_hours() -> None:
    assert format_seconds(92.4) == "1m 32s"
    assert format_seconds(600) == "10m 00s"
    assert format_seconds(3725) == "1h 02m 05s"


def test_report_success_and_failure() -> None:
    assert report("verify", 0, 92.4) == "tip verify: 1m 32s"
    assert (report("gate", 2, 40.06)
            == "tip gate: failed (exit 2) after 40.1s")


def test_parse_argv_splits_goals_from_assignments() -> None:
    goals, values = parse_argv(
        ["check", "CH=25 28", "output-check", "ARGS=--x=1", "MODEL="])
    assert goals == ["check", "output-check"]
    assert values == {"CH": "25 28", "ARGS": "--x=1", "MODEL": ""}


def test_vars_read_unset_as_empty_and_split_like_make() -> None:
    v = Vars({"CH": "25 28", "MODEL": ""})
    assert v.words("CH") == ["25", "28"]
    assert v.words("ARGS") == []
    assert v.get("MODEL", "default") == "default"
    assert v.get("CH") == "25 28"


def _registry(log: list[str]) -> Registry:
    reg = Registry()
    reg.section("S")

    def step(name: str, fail: int = 0):
        def fn(v: Vars) -> None:
            log.append(name)
            if fail:
                raise StepFailed(fail)
        return fn

    reg.task("extract", name="extract")(step("extract"))
    reg.task("ty", deps=("extract",), name="ty")(step("ty"))
    reg.task("lint", deps=("extract",), name="lint")(step("lint"))
    reg.task("bad", name="bad")(step("bad", fail=3))
    reg.task("after", deps=("bad",), name="after")(step("after"))
    return reg


def test_deps_run_first_and_once_per_invocation() -> None:
    log: list[str] = []
    runner = Runner(Vars(), _registry(log))
    runner.run("ty")
    runner.run("lint")
    assert log == ["extract", "ty", "lint"]


def test_a_failing_dep_stops_the_task() -> None:
    log: list[str] = []
    with pytest.raises(StepFailed) as failed:
        Runner(Vars(), _registry(log)).run("after")
    assert failed.value.code == 3
    assert log == ["bad"]


def test_unknown_suggests_close_names() -> None:
    assert "Did you mean verify" in unknown("verfy")


def test_main_rejects_an_unknown_task_before_running_anything(capsys):
    with mock.patch.object(tip.Runner, "run") as run:
        assert main(["verify", "nonesuch"]) == 2
    run.assert_not_called()
    assert "no task named 'nonesuch'" in capsys.readouterr().err


def test_a_positional_word_binds_the_tasks_variable() -> None:
    seen: dict[str, str] = {}

    def fake_run(self: Runner, name: str) -> None:
        seen.update(self.vars.values, task=name)

    with mock.patch.object(tip.Runner, "run", fake_run), \
            mock.patch.dict("os.environ", {NESTED: "1"}):
        assert main(["run-one", "box_view"]) == 0
    assert seen == {"task": "run-one", "F": "box_view"}


def test_an_explicit_assignment_beats_the_positional_word() -> None:
    seen: dict[str, str] = {}

    def fake_run(self: Runner, name: str) -> None:
        seen.update(self.vars.values)

    with mock.patch.object(tip.Runner, "run", fake_run), \
            mock.patch.dict("os.environ", {NESTED: "1"}):
        main(["run-one", "box_view", "F=other"])
    assert seen["F"] == "other"


def test_a_top_level_goal_prints_and_records_its_time(capsys) -> None:
    env = {k: v for k, v in __import__("os").environ.items() if k != NESTED}
    with mock.patch.object(tip.Runner, "run"), \
            mock.patch.dict("os.environ", env, clear=True), \
            mock.patch("tools.target_times.record") as record:
        assert main(["gate-status"]) == 0
    assert capsys.readouterr().out.startswith("tip gate-status: ")
    record.assert_called_once()


def test_a_nested_tip_prints_no_timing_line(capsys) -> None:
    with mock.patch.object(tip.Runner, "run"), \
            mock.patch.dict("os.environ", {NESTED: "1"}), \
            mock.patch("tools.target_times.record") as record:
        assert main(["gate-status"]) == 0
    assert "tip gate-status" not in capsys.readouterr().out
    record.assert_not_called()


def test_a_failing_step_reports_its_status(capsys) -> None:
    with mock.patch.object(tip.Runner, "run", side_effect=StepFailed(4)), \
            mock.patch.dict("os.environ", {NESTED: ""}):
        assert main(["gate-status"]) == 4
    assert "tip gate-status: failed (exit 4)" in capsys.readouterr().out


def test_run_echoes_the_command_and_marks_the_child_nested(capsys) -> None:
    with mock.patch("tools.tip.subprocess.call", return_value=0) as call:
        tip.run(["uv", "run", "python", "-m", "tools.x", "a b"])
    assert capsys.readouterr().out == 'uv run python -m tools.x "a b"\n'
    assert call.call_args.kwargs["cwd"] == ROOT
    assert call.call_args.kwargs["env"][NESTED] == "1"


def test_run_raises_step_failed_on_a_nonzero_exit() -> None:
    with mock.patch("tools.tip.subprocess.call", return_value=5):
        with pytest.raises(StepFailed) as failed:
            tip.run(["false"])
    assert failed.value.code == 5


def test_the_real_tasks_name_every_dep_and_no_helper() -> None:
    """Every dep is a task, and no task function shadows a step helper
    in tools/tasks.py (a task named `run` once replaced `run()`)."""
    import tools.tasks as tasks
    reg = tip.load()
    for t in reg.tasks.values():
        for dep in t.deps:
            assert dep in reg.tasks, (t.name, dep)
    for helper in ("run", "py", "tool", "invoke", "remove", "prose_files"):
        assert getattr(tasks, helper).__module__ in ("tools.tip",
                                                     "tools.tasks")
        assert getattr(tasks, helper) not in [t.fn for t in
                                              reg.tasks.values()], helper


def test_python_m_tools_tip_lists_the_tasks_when_piped() -> None:
    out = subprocess.run(
        [sys.executable, "-m", "tools.tip", "help", "--pick", "never"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    assert out.startswith("everyday: Everyday")
    assert "  verify-ch" in out


def test_python_m_tools_tip_runs_a_task() -> None:
    """Under `python -m`, tip.py is __main__, a second copy of the
    module; the task lookup must still find tools/tasks.py's tasks."""
    out = subprocess.run(
        [sys.executable, "-m", "tools.tip", "gate-status"],
        cwd=ROOT, capture_output=True, text=True,
        env={**__import__("os").environ, NESTED: "1"})
    assert "no task named" not in out.stderr
    assert out.returncode == 0, out.stderr
