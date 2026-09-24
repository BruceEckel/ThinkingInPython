"""Tests for tools/check_tools.py: the per-machine install commands."""
from tools.check_tools import (
    TOOLS, Tool, install_commands, package_manager)

PANDOC = next(t for t in TOOLS if t.name == "pandoc")
TYPST = next(t for t in TOOLS if t.name == "typst")
VALE = next(t for t in TOOLS if t.name == "vale")
GH = next(t for t in TOOLS if t.name == "gh")


def test_one_manager_line_then_each_tool_without_a_package():
    lines = install_commands([PANDOC, TYPST, VALE, GH], "apt")
    assert lines[0] == "sudo apt install pandoc gh"
    assert lines[1] == TYPST.other and lines[2] == VALE.other
    assert len(lines) == 3


def test_winget_and_brew_fold_every_full_tool_into_one_line():
    assert install_commands([PANDOC, TYPST, VALE, GH], "winget") == [
        "winget install JohnMacFarlane.Pandoc Typst.Typst errata-ai.Vale "
        "GitHub.cli"]
    assert install_commands([PANDOC, TYPST, VALE, GH], "brew") == [
        "brew install pandoc typst vale gh"]


def test_no_manager_lists_each_tools_own_command():
    lines = install_commands([PANDOC, GH], None)
    assert lines == [PANDOC.other, GH.other]


def test_hint_names_the_managers_package_or_falls_back():
    assert PANDOC.hint("apt") == "sudo apt install pandoc"
    assert TYPST.hint("apt") == TYPST.other
    assert Tool("x", ["x"], "basic", "see the docs").hint("brew") == (
        "see the docs")


def test_package_manager_prefers_winget_then_brew_then_apt():
    def on_path(*names):
        return lambda name: name in names
    assert package_manager(on_path("winget"), "win32") == "winget"
    assert package_manager(on_path(), "win32") is None
    assert package_manager(on_path("brew", "apt-get"), "linux") == "brew"
    assert package_manager(on_path("apt-get"), "linux") == "apt"
    assert package_manager(on_path(), "linux") is None
    assert package_manager(on_path("brew"), "darwin") == "brew"


def test_every_tool_has_a_fallback_and_only_known_managers():
    for tool in TOOLS:
        assert tool.other, tool.name
        assert set(tool.packages) <= {"winget", "brew", "apt"}, tool.name
