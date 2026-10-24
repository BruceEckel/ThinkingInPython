"""Tests for tools/serve.py's --watch watcher.

The watcher polls both Markdown trees. A solutions edit rebuilds its
chapter (whose one pandoc run also rewrites the solutions page), a
chapter and its solutions file changed in one tick rebuild once, and a
rebuild that raises an exception is reported in the terminal instead of
disappearing, which is what it did before 2026-10-10. A chapter rebuild
leaves the book's index page stale, and the first request for that page
rebuilds it (since 2026-10-18, when the ten-second whole-book match had
made every save a ten-second wait). A save that lands while a rebuild
runs gets a rebuild of its own on the next poll (since 2026-10-24, when
the watcher re-snapshotted after each rebuild and so took that save as
already built).

The --watch supervisor restarts the server when the build code changes.
A restart that dies, because the save caught a `tools/` module mid-edit,
waits for the next change to the build code instead of ending the
session, which it did before 2026-10-24.
"""
from itertools import chain, repeat
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
    snapshots = chain([before], repeat(after))
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


def test_a_save_during_a_rebuild_rebuilds_again(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    watcher, rebuilt = make_watcher(monkeypatch, tmp_path, {CHAPTER: 1.0},
                                    {CHAPTER: 2.0})
    # The second save lands while the first rebuild runs: any snapshot
    # after the first poll sees it.
    polls = chain([{CHAPTER: 2.0}], repeat({CHAPTER: 3.0}))
    monkeypatch.setattr(serve, "snapshot", lambda: next(polls))
    watcher.tick()
    watcher.tick()
    assert rebuilt == [CHAPTER, CHAPTER]


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


def test_a_chapter_rebuild_leaves_the_index_page_for_its_next_request(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    before = {CHAPTER: 1.0}
    watcher, _ = make_watcher(monkeypatch, tmp_path, before,
                              {CHAPTER: 2.0})
    index_rebuilds: list[Path] = []
    monkeypatch.setattr(build_site, "rebuild_index_page",
                        lambda out_dir: index_rebuilds.append(out_dir))
    assert not watcher.index_stale
    watcher.tick()
    assert watcher.index_stale
    assert index_rebuilds == []
    watcher.refresh_index()
    assert index_rebuilds == [tmp_path]
    assert not watcher.index_stale
    watcher.refresh_index()
    assert index_rebuilds == [tmp_path]


class FakeChild:
    """A server process whose `poll()` answers from a script."""

    def __init__(self, polls: list[int | None]) -> None:
        self.polls = chain(polls, repeat(polls[-1]))
        self.pid = 0

    def poll(self) -> int | None:
        return next(self.polls)


def run_supervisor(monkeypatch: pytest.MonkeyPatch,
                   children: list[FakeChild],
                   snapshots: list[dict[Path, float]]) -> tuple[int, int]:
    """Run `supervise()` over scripted children and code snapshots;
    return its exit code and the number of servers it started."""
    started = iter(children)
    count = 0

    def popen(*args: object, **kwargs: object) -> FakeChild:
        nonlocal count
        count += 1
        return next(started)

    polls = chain(snapshots, repeat(snapshots[-1]))
    monkeypatch.setattr(serve, "code_files", lambda: [])
    monkeypatch.setattr(serve, "code_snapshot", lambda files: next(polls))
    monkeypatch.setattr(serve.subprocess, "Popen", popen)
    monkeypatch.setattr(serve.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(serve, "stop", lambda child: None)
    return serve.supervise([]), count


def test_a_restart_that_dies_waits_for_the_next_code_change(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    code = Path("build_site.py")
    broken, fixed = {code: 2.0}, {code: 3.0}
    children = [FakeChild([None]), FakeChild([1]), FakeChild([None, 0])]
    snapshots = [{code: 1.0}, broken, broken, broken, broken, fixed]
    assert run_supervisor(monkeypatch, children, snapshots) == (0, 3)
    assert capsys.readouterr().out.count("waiting for the next") == 1


def test_a_first_server_that_dies_ends_the_session(
        monkeypatch: pytest.MonkeyPatch) -> None:
    code = Path("build_site.py")
    assert run_supervisor(monkeypatch, [FakeChild([1])],
                          [{code: 1.0}]) == (1, 1)
