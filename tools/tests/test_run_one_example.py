"""Tests for tools/run_one_example.py's search."""
from pathlib import Path

import pytest

import tools.run_one_example as roe


@pytest.fixture
def trees(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A chapter tree and a Solutions tree, plus build copies."""
    files = [
        "Examples/utils/benchmark.py",
        "Examples/03_Foundations--Containers/deque_timing.py",
        "Examples/38_Patterns--Simulation/robot_explorer/maze_view.py",
        "Examples/47_Effects--Stateless_in_Practice/research_by_hand.py",
        "SolutionsCode/03_Foundations--Containers/exercise_1.py",
        "SolutionsCode/38_Patterns--Simulation/exercise_1.py",
        "SolutionsCode/47_Effects--Stateless_in_Practice/research_by_hand.py",
        "build/examples/99_Only--In_Build/fresh.py",
    ]
    for f in files:
        (tmp_path / f).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / f).write_text("print('hi')\n", encoding="utf-8")
    ex, sol = tmp_path / "Examples", tmp_path / "SolutionsCode"
    bex, bsol = tmp_path / "build/examples", tmp_path / "build/solutions"
    monkeypatch.setattr(roe, "ROOT", tmp_path)
    monkeypatch.setattr(roe, "TREES", {
        ex: ex / "utils", sol: ex / "utils",
        bex: bex / "utils", bsol: bex / "utils"})
    monkeypatch.setattr(roe, "PASSES", ((ex, sol), (bex, bsol)))
    return tmp_path


def names(paths: list[Path], root: Path) -> list[str]:
    return [p.relative_to(root).as_posix() for p in paths]


def test_a_bare_name_finds_the_listing(trees: Path) -> None:
    assert names(roe.candidates("maze_view"), trees) == [
        "Examples/38_Patterns--Simulation/robot_explorer/maze_view.py"]


def test_the_py_suffix_is_optional(trees: Path) -> None:
    assert roe.candidates("maze_view.py") == roe.candidates("maze_view")


def test_solutions_answers_are_searched(trees: Path) -> None:
    assert names(roe.candidates("exercise_1"), trees) == [
        "SolutionsCode/03_Foundations--Containers/exercise_1.py",
        "SolutionsCode/38_Patterns--Simulation/exercise_1.py"]


def test_a_chapter_number_picks_one(trees: Path) -> None:
    assert names(roe.candidates("38/exercise_1"), trees) == [
        "SolutionsCode/38_Patterns--Simulation/exercise_1.py"]


def test_a_tree_name_picks_chapter_or_solution(trees: Path) -> None:
    assert len(roe.candidates("research_by_hand")) == 2
    assert names(roe.candidates("Solutions/47/research_by_hand"), trees) == [
        "SolutionsCode/47_Effects--Stateless_in_Practice/research_by_hand.py"]
    assert names(roe.candidates("Examples/research_by_hand"), trees) == [
        "Examples/47_Effects--Stateless_in_Practice/research_by_hand.py"]


def test_pieces_of_a_path_match_in_part(trees: Path) -> None:
    assert names(roe.candidates("Containers/deque"), trees) == [
        "Examples/03_Foundations--Containers/deque_timing.py"]


def test_the_build_trees_are_a_fallback(trees: Path) -> None:
    assert names(roe.candidates("fresh"), trees) == [
        "build/examples/99_Only--In_Build/fresh.py"]


def test_names_a_listing_needs_an_exact_name(trees: Path) -> None:
    assert roe.names_a_listing("maze_view")
    assert roe.names_a_listing("38/exercise_1")
    assert not roe.names_a_listing("maze")  # Only a part of a name
    assert not roe.names_a_listing("verfy")


def test_a_solution_uses_the_chapter_trees_utils(trees: Path) -> None:
    path = roe.candidates("38/exercise_1")[0]
    tree = roe.tree_root(path)
    assert tree is not None and tree == trees / "SolutionsCode"
    assert roe.TREES[tree] == trees / "Examples/utils"
