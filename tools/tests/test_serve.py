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

The --bookmark save validates a POST body, writes `bookmark.json`, and
commits that file alone; the commit tests run in a temporary git repo.
"""
import shutil
import subprocess
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


SAMPLE = """\
# Title

## First {#first}

The clause catches `Failed`.

## Second

[A generator must finish](#close-requires) when it is told to,
and the clause catches `Failed` and lets
`GeneratorExit` pass.

```python
print(table[0](arg))  # [1]
```
"""


@pytest.fixture
def sample(tmp_path: Path) -> Path:
    md = tmp_path / "sample.md"
    md.write_text(SAMPLE, encoding="utf-8")
    return md


def test_a_passage_with_a_code_span_is_found(sample: Path) -> None:
    assert serve.locate(sample, "The clause catches Failed.") == 5


def test_a_passage_across_a_line_break_starts_on_its_first_line(
        sample: Path) -> None:
    assert serve.locate(sample, "lets GeneratorExit pass") == 10


def test_a_repeated_passage_resolves_under_its_heading(
        sample: Path) -> None:
    assert serve.locate(sample, "clause catches Failed", "First") == 5
    assert serve.locate(sample, "clause catches Failed", "Second") == 10


def test_link_text_matches_without_its_target(sample: Path) -> None:
    assert serve.locate(
        sample, "A generator must finish when it is told") == 9


def test_a_call_after_a_subscript_is_no_link_target(
        sample: Path) -> None:
    assert serve.locate(sample, "print(table[0](arg))  # [1]") == 14


def test_a_passage_the_file_lacks_is_not_located(sample: Path) -> None:
    assert serve.locate(sample, "no such words") is None
    assert serve.locate(sample, "   ") is None


@pytest.mark.book
def test_a_page_maps_to_its_markdown() -> None:
    chapter = next(CHAPTERS_DIR.glob("45_*.md"))
    assert serve.page_source(f"{chapter.stem}.html") == chapter
    assert serve.page_source(f"{chapter.stem}.solutions.html") == (
        SOLUTIONS_DIR / chapter.stem / SOLUTIONS_MD)
    assert serve.page_source("index.html") is None


MARK = {"page": "45_Effects--Generators.html", "title": "Generators",
        "heading": "Close", "heading_id": "close", "text": "A passage",
        "offset": 0.25, "source": "Chapters/45_x.md:12"}


def test_the_bookmark_message_holds_title_heading_and_source() -> None:
    assert serve.bookmark_message(MARK) == (
        "Bookmark: Generators › Close (Chapters/45_x.md:12)")


def test_the_bookmark_message_drops_what_is_empty() -> None:
    assert serve.bookmark_message({**MARK, "heading": ""}) == (
        "Bookmark: Generators (Chapters/45_x.md:12)")
    assert serve.bookmark_message({**MARK, "source": ""}) == (
        "Bookmark: Generators › Close")
    assert serve.bookmark_message(
        {**MARK, "heading": "", "source": ""}) == "Bookmark: Generators"


@pytest.fixture
def site(tmp_path: Path) -> Path:
    out = tmp_path / "site"
    out.mkdir()
    (out / MARK["page"]).write_text("<html></html>", encoding="utf-8")
    return out


@pytest.mark.parametrize("page", [
    "../45_Effects--Generators.html", "sub/45_Effects--Generators.html",
    "..\45_Effects--Generators.html", "45_Effects--Generators.md",
    "missing.html", "",
])
def test_a_bad_page_name_is_rejected(site: Path, page: str) -> None:
    with pytest.raises(ValueError):
        serve.clean_bookmark({**MARK, "page": page}, site)


def test_a_non_object_or_a_non_string_field_is_rejected(
        site: Path) -> None:
    with pytest.raises(ValueError):
        serve.clean_bookmark([], site)
    with pytest.raises(ValueError):
        serve.clean_bookmark({**MARK, "title": 3}, site)
    with pytest.raises(ValueError):
        serve.clean_bookmark({**MARK, "offset": "far"}, site)


def test_the_offset_is_clamped_and_rounded(site: Path) -> None:
    clean = serve.clean_bookmark
    assert clean({**MARK, "offset": 7}, site)["offset"] == 1.0
    assert clean({**MARK, "offset": -2}, site)["offset"] == 0.0
    assert clean({**MARK, "offset": 0.123456}, site)["offset"] == 0.123
    assert clean({**MARK, "offset": float("nan")}, site)["offset"] == 0.0


def test_the_text_is_collapsed_and_cut(site: Path) -> None:
    text = "  a \n b  " + "x" * 200
    clean = serve.clean_bookmark({**MARK, "text": text}, site)["text"]
    assert clean.startswith("a b xxx")
    assert len(clean) == serve.BOOKMARK_TEXT


def git_available() -> bool:
    return shutil.which("git") is not None


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    if not git_available():
        pytest.skip("git is not installed")
    root = tmp_path / "repo"
    root.mkdir()
    for args in (["init", "--quiet"],
                 ["config", "user.name", "Test"],
                 ["config", "user.email", "test@example.com"],
                 ["config", "commit.gpgsign", "false"]):
        subprocess.run(["git", *args], cwd=root, check=True)
    (root / "other.txt").write_text("one\n", encoding="utf-8")
    subprocess.run(["git", "add", "other.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "start"],
                   cwd=root, check=True)
    return root


def git_out(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True,
                          capture_output=True, text=True).stdout


def test_the_first_save_commits_and_an_identical_one_does_not(
        repo: Path) -> None:
    file = repo / "bookmark.json"
    assert serve.save_bookmark(MARK, repo, file) == (
        True, "saved and committed")
    assert git_out(repo, "log", "-1", "--format=%s") == (
        "Bookmark: Generators › Close (Chapters/45_x.md:12)\n")
    assert serve.load_bookmark(file) == MARK
    assert serve.save_bookmark(MARK, repo, file) == (False, "already saved")
    assert git_out(repo, "rev-list", "--count", "HEAD") == "2\n"
    moved = {**MARK, "offset": 0.5}
    assert serve.save_bookmark(moved, repo, file)[0]
    assert git_out(repo, "rev-list", "--count", "HEAD") == "3\n"


def test_a_save_leaves_other_modified_and_staged_files_out(
        repo: Path) -> None:
    (repo / "other.txt").write_text("two\n", encoding="utf-8")
    (repo / "staged.txt").write_text("new\n", encoding="utf-8")
    subprocess.run(["git", "add", "staged.txt"], cwd=repo, check=True)
    serve.save_bookmark(MARK, repo, repo / "bookmark.json")
    assert git_out(repo, "show", "--name-only", "--format=", "HEAD") == (
        "bookmark.json\n")
    status = git_out(repo, "status", "--short")
    assert " M other.txt" in status
    assert "A  staged.txt" in status


def test_a_failed_commit_is_reported_not_raised(tmp_path: Path) -> None:
    if not git_available():
        pytest.skip("git is not installed")
    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    file = plain / "bookmark.json"
    committed, message = serve.save_bookmark(MARK, plain, file)
    assert not committed
    assert message.startswith("saved, not committed: ")
    assert serve.load_bookmark(file) == MARK


def test_open_starts_at_the_bookmarked_page(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "45_Effects--Generators.html").write_text("", "utf-8")
    file = tmp_path / "bookmark.json"
    url = "http://localhost:8000/"
    assert serve.start_url(url, site, file) == url
    serve.write_bookmark({"page": "45_Effects--Generators.html"}, file)
    assert serve.start_url(url, site, file) == (
        f"{url}45_Effects--Generators.html#{serve.BOOKMARK_FRAGMENT}")
    serve.write_bookmark({"page": "missing.html"}, file)
    assert serve.start_url(url, site, file) == url
    serve.write_bookmark({"page": "../secret.html"}, file)
    assert serve.start_url(url, site, file) == url
