"""Tests for tools/serve.py's --watch watcher.

The watcher polls both Markdown trees. A solutions edit rebuilds its
chapter (whose one pandoc run also rewrites the solutions page), a
chapter and its solutions file changed in one tick rebuild once, and a
rebuild that raises an exception is reported in the terminal instead of
disappearing, which is what it did before 2026-10-10.
"""
from pathlib import Path

import pytest

from tools import build_site, serve
from tools.config import CHAPTERS_DIR, SOLUTIONS_DIR, SOLUTIONS_MD

STEM = "30_Patterns--Observer"
CHAPTER = CHAPTERS_DIR / f"{STEM}.md"
SOLUTIONS = SOLUTIONS_DIR / STEM / SOLUTIONS_MD


def test_a_solutions_file_maps_to_its_chapter() -> None:
    assert serve.source_chapter(SOLUTIONS) == CHAPTER


def test_a_chapter_maps_to_itself() -> None:
    assert serve.source_chapter(CHAPTER) == CHAPTER


@pytest.mark.book
def test_the_watcher_lists_both_markdown_trees() -> None:
    watched = serve.watched_sources()
    assert CHAPTER in watched
    assert SOLUTIONS in watched


def make_watcher(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                 before: dict[Path, float], after: dict[Path, float],
                 ) -> tuple[serve.Watcher, list[Path]]:
    """A Watcher that sees `before` at construction and `after` on its
    next poll, with the rebuild replaced by a recorder."""
    snapshots = iter([before, after, after])
    monkeypatch.setattr(serve, "snapshot", lambda: next(snapshots))
    rebuilt: list[Path] = []

    def record(md: Path, out_dir: Path, chapter_toc: bool) -> bool:
        rebuilt.append(md)
        return True

    monkeypatch.setattr(build_site, "rebuild_chapter", record)
    monkeypatch.setattr(build_site, "build", lambda *a: pytest.fail(
        "a Markdown edit must take the incremental path"))
    return serve.Watcher(tmp_path, chapter_toc=False), rebuilt


def test_a_solutions_edit_rebuilds_its_chapter_once(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    before = {CHAPTER: 1.0, SOLUTIONS: 1.0}
    watcher, rebuilt = make_watcher(monkeypatch, tmp_path, before,
                                    {CHAPTER: 1.0, SOLUTIONS: 2.0})
    token = watcher.token
    watcher.tick()
    assert rebuilt == [CHAPTER]
    assert watcher.token != token


def test_a_chapter_and_its_solutions_rebuild_once(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    before = {CHAPTER: 1.0, SOLUTIONS: 1.0}
    watcher, rebuilt = make_watcher(monkeypatch, tmp_path, before,
                                    {CHAPTER: 2.0, SOLUTIONS: 2.0})
    watcher.tick()
    assert rebuilt == [CHAPTER]


def test_a_failed_rebuild_is_reported_and_polling_goes_on(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
        capsys: pytest.CaptureFixture[str]) -> None:
    before = {CHAPTER: 1.0}
    watcher, _ = make_watcher(monkeypatch, tmp_path, before,
                              {CHAPTER: 2.0})

    def explode(md: Path, out_dir: Path, chapter_toc: bool) -> bool:
        raise RuntimeError("pandoc said no")

    monkeypatch.setattr(build_site, "rebuild_chapter", explode)
    token = watcher.token
    watcher.tick()  # Must not raise an exception
    out = capsys.readouterr()
    assert "pandoc said no" in out.err
    assert "Rebuild failed" in out.out
    assert watcher.token == token
