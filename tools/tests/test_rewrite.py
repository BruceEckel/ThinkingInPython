"""`tools.rewrite`'s skill preflight: a pass whose skill is not on
disk, or whose plugin is not installed or is disabled, is reported
before any headless session starts."""

import json
from pathlib import Path
from tools.rewrite import Pass, missing_skills

def repo_with_skill(tmp_path: Path, name: str) -> Path:
    root = tmp_path / "repo"
    (root / ".claude" / "skills" / name).mkdir(parents=True)
    (root / ".claude" / "skills" / name / "SKILL.md").write_text("x")
    return root


def home_with_plugin(tmp_path: Path, plugin: str, skill: str,
                     enabled: bool | None = True) -> Path:
    home = tmp_path / "home"
    install = home / "cache" / plugin
    (install / "skills" / skill).mkdir(parents=True)
    (install / "skills" / skill / "SKILL.md").write_text("x")
    plugins_dir = home / ".claude" / "plugins"
    plugins_dir.mkdir(parents=True)
    key = f"{plugin}@market"
    (plugins_dir / "installed_plugins.json").write_text(json.dumps(
        {"version": 2,
         "plugins": {key: [{"installPath": str(install)}]}}))
    settings: dict[str, object] = {}
    if enabled is not None:
        settings["enabledPlugins"] = {key: enabled}
    (home / ".claude" / "settings.json").write_text(json.dumps(settings))
    return home


def test_repo_skill_present_and_absent(tmp_path: Path) -> None:
    root = repo_with_skill(tmp_path, "literal")
    home = tmp_path / "empty-home"
    ok = Pass("literal", "literal", "")
    gone = Pass("positive", "positive", "")
    assert missing_skills([ok], root, home) == []
    [line] = missing_skills([gone], root, home)
    assert ".claude/skills/positive/SKILL.md" in line


def test_plugin_skill_installed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    home = home_with_plugin(tmp_path, "elements-of-style", "clearly")
    p = Pass("eos", "elements-of-style:clearly", "")
    assert missing_skills([p], root, home) == []


def test_plugin_skill_not_installed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    home = home_with_plugin(tmp_path, "other-plugin", "clearly")
    p = Pass("eos", "elements-of-style:clearly", "")
    [line] = missing_skills([p], root, home)
    assert "claude plugin install elements-of-style@" in line
    assert "--passes" in line


def test_plugin_disabled_in_settings(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    home = home_with_plugin(tmp_path, "elements-of-style", "clearly",
                            enabled=False)
    p = Pass("eos", "elements-of-style:clearly", "")
    assert len(missing_skills([p], root, home)) == 1


def test_plugin_with_no_settings_file_counts_as_enabled(
        tmp_path: Path) -> None:
    root = tmp_path / "repo"
    home = home_with_plugin(tmp_path, "elements-of-style", "clearly",
                            enabled=None)
    (home / ".claude" / "settings.json").unlink()
    p = Pass("eos", "elements-of-style:clearly", "")
    assert missing_skills([p], root, home) == []


def test_no_registry_means_missing(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    home = tmp_path / "bare-home"
    p = Pass("eos", "elements-of-style:clearly", "")
    assert len(missing_skills([p], root, home)) == 1
