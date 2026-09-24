"""Tests for tools/check_tools.py: the per-machine install commands."""
from unittest import mock

from tools import check_tools
from tools.check_tools import (
    TOOLS, Tool, install_commands, install_hint, package_manager)

PANDOC = next(t for t in TOOLS if t.name == "pandoc")
TYPST = next(t for t in TOOLS if t.name == "typst")
VALE = next(t for t in TOOLS if t.name == "vale")
GH = next(t for t in TOOLS if t.name == "gh")


RASTER = next(t for t in TOOLS if t.name == "svg rasterizer")


def test_one_manager_line_then_each_tool_without_a_package():
    """Ubuntu packages gh and a rasterizer; pandoc, typst, and vale
    come from their release archives."""
    lines = install_commands([PANDOC, TYPST, VALE, GH, RASTER], "apt")
    assert lines[0] == "sudo apt install gh librsvg2-bin"
    assert lines[1:] == [PANDOC.other, TYPST.other, VALE.other]


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
    assert GH.hint("apt") == "sudo apt install gh"
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


def test_a_tool_with_alternatives_answers_from_any_of_them():
    def only(name):
        return lambda cmd: "resvg 0.45" if cmd[0] == name else None
    with mock.patch.object(check_tools, "first_line", only("inkscape")):
        assert RASTER.version() == "resvg 0.45"
    with mock.patch.object(check_tools, "first_line", only("nothing")):
        assert RASTER.version() is None
        assert PANDOC.version() is None


def test_install_hint_is_the_managers_command_for_this_machine():
    with mock.patch.object(check_tools, "package_manager", lambda: "brew"):
        assert install_hint("typst") == "brew install typst"
        assert install_hint("svg rasterizer") == "brew install resvg"
    with mock.patch.object(check_tools, "package_manager", lambda: None):
        assert install_hint("gh") == GH.other


def test_too_old_reads_the_first_numeric_word():
    assert PANDOC.too_old("pandoc 2.9.2.1")
    assert not PANDOC.too_old("pandoc 3.11")
    assert not PANDOC.too_old("pandoc")           # nothing to judge
    assert not TYPST.too_old("typst 0.1.0")       # no minimum set
