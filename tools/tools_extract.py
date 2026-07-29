#!/usr/bin/env python3
"""The machinery both extractors share: route blocks to files, write, check.

extract_examples.py and extract_rust.py were structural mirrors. Each had
its own file dataclass, its own result dataclass, its own extract loop,
its own write-if-changed, its own compare-against-a-tree, and its own
copy of the "conflicting duplicate path" report. The two differed in
three things only: which blocks they claim, what relative path a claimed
block lands at, and which root that path is relative to.

Those three are the `Router` and the root argument here. A router looks
at one parsed `Block` and returns the relative path it should extract to,
or None to pass. Routers are tried in order and the first non-None wins,
so a tool with more than one rule (extract_rust.py claims ```rust blocks
*and* ```python blocks whose slug starts with "rust/") lists them in
priority order rather than writing a branching loop.

What is deliberately *not* here: the destructive wipe of a build/
directory, stray-file detection, and pruning. Those belong to
extract_examples.py alone, because only it owns a fully derived tree.
rust/ holds real, hand-maintained project files (Cargo.toml and friends)
that no book block generates, so a generic "delete what the book does not
produce" would be a foot-gun there.

Named tools_extract for the same reason as the other tools_* modules: it
must never collide with a book listing's filename through Python's
sys.modules cache. See tools_repo.py's docstring.
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from tools_markdown import Block, Document
from tools_repo import write_text_lf

Router = Callable[[Document, Block], str | None]
"""Where a block extracts to, relative to the tool's root, or None to pass."""


@dataclass(frozen=True)
class ExtractedFile:
    """One block, resolved to the file it becomes."""

    path: str
    """Relative to the tool's root, forward slashes."""

    content: str
    """Verbatim block text, with exactly one trailing newline."""

    source_md: str
    """Name of the Markdown file the block came from."""

    language: str
    """The fence's language word."""


@dataclass(frozen=True)
class Conflict:
    """Two blocks claiming one path with different content."""

    path: str
    first: str
    second: str


@dataclass
class ExtractResult:
    files: dict[str, ExtractedFile] = field(default_factory=dict)
    conflicts: list[Conflict] = field(default_factory=list)
    fragments: int = 0
    """Blocks no router claimed: illustrative listings, not files."""


def block_content(block: Block) -> str:
    """A block's text, normalized to exactly one trailing newline."""
    return "\n".join(block.lines).rstrip("\n") + "\n"


def extract(
    docs: Iterable[Document], routers: Sequence[Router],
) -> ExtractResult:
    """Route every block of every document to its file.

    The first block to claim a path wins; a later block claiming the same
    path with different text is recorded as a conflict rather than
    silently overwriting, since which one the reader meant is not
    something this can decide.
    """
    result = ExtractResult()
    for doc in docs:
        for block in doc.blocks:
            rel = next(
                (r for r in (route(doc, block) for route in routers)
                 if r is not None),
                None,
            )
            if rel is None:
                result.fragments += 1
                continue
            content = block_content(block)
            existing = result.files.get(rel)
            if existing and existing.content != content:
                result.conflicts.append(
                    Conflict(rel, existing.source_md, doc.path.name)
                )
                continue
            result.files[rel] = ExtractedFile(
                rel, content, doc.path.name, block.lang
            )
    return result


def write_tree(result: ExtractResult, root: Path) -> int:
    """Write every extracted file under `root`. Returns how many changed.

    Unchanged files are left alone so their mtimes stay put, which keeps
    tools that watch timestamps from seeing the whole tree churn.
    """
    written = 0
    for extracted in result.files.values():
        dest = root / extracted.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (not dest.exists()
                or dest.read_text(encoding="utf-8") != extracted.content):
            write_text_lf(dest, extracted.content)
            written += 1
    return written


def check_against(
    result: ExtractResult, root: Path,
) -> tuple[list[str], list[str]]:
    """Compare the extracted files to what is under `root`.

    Returns (missing, changed): paths the book produces that are absent,
    and paths whose committed text no longer matches the book.
    """
    missing: list[str] = []
    changed: list[str] = []
    for extracted in result.files.values():
        dest = root / extracted.path
        if not dest.exists():
            missing.append(extracted.path)
        elif dest.read_text(encoding="utf-8") != extracted.content:
            changed.append(extracted.path)
    return missing, changed


def report_conflicts(result: ExtractResult) -> None:
    """Print the duplicate-path report, if there is anything to report."""
    if not result.conflicts:
        return
    print(f"\n{len(result.conflicts)} conflicting duplicate path(s) "
          "(same path, differing content):")
    for conflict in result.conflicts:
        print(f"  ! {conflict.path}  "
              f"({conflict.first} vs {conflict.second})")


def report_drift(
    missing: list[str], changed: list[str], *, noun: str, where: str,
) -> None:
    """Print the missing/changed report against a tree named `where`."""
    if missing:
        print(f"\n{len(missing)} {noun}(s) in the book but not under "
              f"{where}/:")
        for path in missing:
            print(f"  + {path}")
    if changed:
        print(f"\n{len(changed)} {noun}(s) whose book text differs from "
              f"{where}/:")
        for path in changed:
            print(f"  ~ {path}")
