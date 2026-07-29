#!/usr/bin/env python3
"""One parsed view of a Markdown file, shared by every tool that reads one.

Before this module, each checker opened a chapter, split it into lines its
own way, and walked its fences with its own loop. Seven tools therefore
did the same parse of the same 45 files, and "what counts as a python
block" had several near-copies that could drift apart.

`Document.parse()` does that work once. A `Document` holds the file's
text, its lines, and its fenced `Block`s; a `Block` knows its language,
where it sits in the file, its content lines, and the slug naming the
file it extracts to. A check is then a function from a `Document` to
`Finding`s (see tools_report.py), which makes it callable from a test
with no filesystem at all.

Line convention: `lines` comes from ``text.split("\\n")``, not
``splitlines()``. The difference matters for the fixers. Only the
``split("\\n")`` form round-trips exactly, since ``"\\n".join(doc.lines)``
reproduces `text` including whether the file ended with a newline, so a
fixer can rewrite a few lines and put the rest back untouched. The cost
is a trailing empty string for a file ending in a newline, which is
normal for this convention and is what comment_periods.py,
comment_spacing.py and listing_format.py already assumed.

Named tools_markdown for the same reason as tools_config/tools_repo/
tools_pycode/tools_report: it must never collide with a book listing's
own filename through Python's sys.modules cache. See tools_repo.py's
docstring for the failure that caused those renames.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from md_prose import is_prose_line
from tools_config import PATH_LINE_RE, RUST_PATH_LINE_RE

# A fence opening or closing at any indent, capturing the language word.
# Indent-tolerant because the book has one (chapter 17's indented ```cpp).
FENCE = re.compile(r"^\s*```(\w+)?\s*$")
FENCE_CLOSE = re.compile(r"^\s*```")

# Languages a ```fence can carry that mean "a Python listing". No ```py
# fence exists in the book today, but validate_output.py has always
# accepted both, so both are accepted here rather than leaving two rules.
PYTHON_LANGS = frozenset({"python", "py"})


@dataclass(frozen=True)
class Block:
    """One fenced code block, located within its file."""

    lang: str
    """The fence's language word: "python", "text", "" for a bare fence."""

    open_at: int
    """0-based index of the opening fence line."""

    end: int
    """0-based index of the closing fence, or len(lines) if unclosed."""

    lines: list[str]
    """The content between the fences, excluding both fence lines."""

    @property
    def start(self) -> int:
        """0-based index of the block's first content line."""
        return self.open_at + 1

    @property
    def is_python(self) -> bool:
        return self.lang in PYTHON_LANGS

    @property
    def slug(self) -> str | None:
        """The relative path this block's first content line names.

        `# trace.py` for a Python block, `// fastcount/src/lib.rs` for a
        Rust one. None when the first content line is not a path comment,
        which is how a listing says it is a fragment rather than a file.
        """
        pattern = RUST_PATH_LINE_RE if self.lang == "rust" else PATH_LINE_RE
        for line in self.lines:
            if line.strip():
                m = pattern.match(line.rstrip("\n\r"))
                return m.group(1).replace("\\", "/") if m else None
        return None

    def line_number(self, index: int) -> int:
        """The file's 1-based line number for content line `index`."""
        return self.start + index + 1


@dataclass(frozen=True)
class Document:
    """A Markdown file parsed once: its text, its lines, its blocks."""

    path: Path
    text: str
    lines: list[str]
    blocks: list[Block]

    @classmethod
    def parse(cls, path: Path) -> "Document":
        return cls.from_text(path.read_text(encoding="utf-8"), path)

    @classmethod
    def from_text(cls, text: str, path: Path = Path("<text>")) -> "Document":
        """Parse `text` directly, so a test needs no file on disk."""
        lines = text.split("\n")
        blocks: list[Block] = []
        i, n = 0, len(lines)
        while i < n:
            m = FENCE.match(lines[i])
            if m is None:
                i += 1
                continue
            j = i + 1
            while j < n and not FENCE_CLOSE.match(lines[j]):
                j += 1
            blocks.append(Block(
                lang=m.group(1) or "",
                open_at=i,
                end=j,
                lines=lines[i + 1:j],
            ))
            i = j + 1
        return cls(path=path, text=text, lines=lines, blocks=blocks)

    def python_blocks(self) -> Iterator[Block]:
        """Every ```python block, in file order."""
        return (b for b in self.blocks if b.is_python)

    def in_fence(self) -> list[bool]:
        """Per line, whether it is a fence line or inside a block.

        The complement is the file's prose and headings, which is what
        `prose_lines()` walks.
        """
        flags = [False] * len(self.lines)
        for block in self.blocks:
            stop = min(self.end_of(block), len(self.lines))
            for k in range(block.open_at, stop):
                flags[k] = True
        return flags

    @staticmethod
    def end_of(block: Block) -> int:
        """One past the block's closing fence line."""
        return block.end + 1

    def prose_lines(self) -> Iterator[tuple[int, str]]:
        """(1-based line number, line) for each ordinary prose line.

        Skips fenced blocks entirely, then applies md_prose's rule, so
        headings, lists, tables, block quotes and indented code are left
        out along with the code.
        """
        fenced = self.in_fence()
        for index, line in enumerate(self.lines):
            if not fenced[index] and is_prose_line(line):
                yield index + 1, line

    def rendered(self, lines: list[str] | None = None) -> str:
        """`lines` (default: this document's) joined back into file text.

        The inverse of the `split("\\n")` in `from_text`, so a fixer that
        edits a few entries writes back a file identical everywhere else.
        """
        return "\n".join(self.lines if lines is None else lines)
