#!/usr/bin/env python
"""Report public class names that nothing outside their class uses.

A public name that only its own class mentions is usually an
implementation detail that should carry a leading underscore, so a
reader of the listing is not invited to rely on it. The check is the
book-wide scan that found `OnlyOnce.ran`, `Peekable.stored`, and
`Controller.states`.

For every class in `Examples/<chapter>/` and `Solutions/<chapter>/`
(recursive, `__pycache__` skipped, a chapter being a directory that
shares its name with a `Chapters/<chapter>.md`, appendices included),
the check collects each name the class defines: a method, a property,
a class attribute, a class-body annotation, or a `self.x` store. The
kind labels are `method`, `property`, `classattr`, and `attr` (a
`self.x` store), with a suffix for the decorators that matter: `/override`,
`/abstractmethod`, `/overload`, `/static`, and `/cls`.

A name is skipped when it starts with an underscore (which covers the
dunders). A field is skipped by design: a class-body annotation in a
`@dataclass` or `@record` class, or in a class whose bases include
`NamedTuple`, is a constructor parameter and part of the repr, so it is
always public. Any other name is used outside its class when `.name` or
`name=` appears anywhere in the chapter's code except the class's own
line range: another file in either tree, module-level code in the same
file, or another class in the same file. It is also used when it sits
inside a code span of `Chapters/<chapter>.md` or of
`Solutions/<chapter>/README.md`, where the prose names it. A name used
nowhere outside is a hit, reported as `path:line: Class.name (kind,
N references inside the class)`, where N counts the other lines of the
class body that mention the name.

The scan is literal and matches on the name alone, with no type
inference, so a hit is a question for a human, not a verdict. The shapes
that come back as judged keeps in the baseline:

- A stored constructor parameter is data the object carries, not an
  internal detail.
- Chapter 31's table-driven conditions and actions are named by the
  table, the prose, and the tests, not by an attribute access.
- A double-dispatch leg (the `eval_*` methods of Solutions 32) is called
  on another object from inside its own class: `item.eval_edict(self)`
  sits in `Edict`, so the one reference falls inside the class's line
  range.
- Chapter 17's introspection demos print or inspect a class's members,
  so the method matters to the demo even though no call names it.

Report-only: it prints the hits and exits 0, because the heuristic is
literal and no gate runs it. `--fail` exits 1 when a NEW hit is found.
It runs alone as `tip internal-names` and inside `tip prose`.

Every hit in the book was read once by a human, and the ones judged
keeps live in `tools/data/internal_names_baseline.txt`, so a run prints
only what is new. An entry is `path::Class.name` with no line number, so
a line shift leaves it alone, while renaming the class or the name
retires it and the renamed hit reports as NEW. An entry is a judged
keep, not an exemption from the rule. The default run prints each NEW
hit and a summary (`N new, M accepted`), and lists a `stale` entry that
matches no hit any more. `--all` prints every hit, marked NEW or
accepted. `--accept` appends every NEW hit to the baseline and drops the
stale entries, keeping the file sorted and free of duplicates.

    uv run python -m tools.internal_names           # new hits
    uv run python -m tools.internal_names --all     # every hit
    uv run python -m tools.internal_names --accept  # judged keeps
    uv run tip internal-names
    uv run tip internal-names-accept
"""

import argparse
import ast
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from tools.config import DATA_DIR, ROOT

BASELINE: Final = DATA_DIR / "internal_names_baseline.txt"
HEADER: Final = (
    "# Public class names that only their own class uses, which a\n"
    "# human read and judged to keep public: stored constructor\n"
    "# data, table-driven names, double-dispatch legs, demos that\n"
    "# introspect. An entry is not an exemption from the rule.\n"
    "# path::Class.name, with no line number, so a line shift leaves\n"
    "# an entry alone. Rewritten by `tip internal-names-accept`; read\n"
    "# the delta with `tip internal-names` before accepting.\n"
    "# See tools/internal_names.py.\n"
)
DATA_DECORATORS: Final = frozenset({"dataclass", "record"})
MARKED_DECORATORS: Final = frozenset(
    {"override", "abstractmethod", "overload"})
PROPERTY_DECORATORS: Final = frozenset({"property", "cached_property"})

ATTRIBUTE_USE = re.compile(r"\.(\w+)")
KEYWORD_OR_STORE = re.compile(r"\b(\w+)\s*=(?!=)")
PROSE_CODE_SPAN = re.compile(r"`[^`\n]*`")
WORD = re.compile(r"\w+")


@dataclass(frozen=True, slots=True)
class Definition:
    """A public name a class defines, and where."""
    name: str
    line: int
    kind: str


@dataclass(frozen=True, slots=True)
class Hit:
    """A class name used nowhere outside its class."""
    path: str
    line: int
    owner: str
    name: str
    kind: str
    internal: int

    @property
    def key(self) -> str:
        """The baseline line: no line number."""
        return f"{self.path}::{self.owner}.{self.name}"


def display(path: Path) -> str:
    """The path relative to the repo root when it lies under it."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def chapters() -> list[str]:
    """Names of the chapters (appendices too) that have code to scan."""
    stems = {p.stem for p in (ROOT / "Chapters").glob("*.md")}
    found = {
        d.name for tree in ("Examples", "Solutions")
        if (ROOT / tree).is_dir()
        for d in (ROOT / tree).iterdir() if d.is_dir()
    }
    return sorted(stems & found)


def code_files(chapter: str) -> list[Path]:
    """Every .py file of a chapter in both trees, `__pycache__` skipped."""
    files: list[Path] = []
    for tree in ("Examples", "Solutions"):
        folder = ROOT / tree / chapter
        if folder.is_dir():
            files.extend(
                p for p in sorted(folder.rglob("*.py"))
                if "__pycache__" not in p.parts)
    return files


def prose_words(chapter: str) -> frozenset[str]:
    """Every word inside a code span of the chapter and its solutions."""
    texts = []
    for path in (ROOT / "Chapters" / f"{chapter}.md",
                 ROOT / "Solutions" / chapter / "README.md"):
        if path.exists():
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
    return frozenset(
        word for span in PROSE_CODE_SPAN.findall("\n".join(texts))
        for word in WORD.findall(span))


def decorator_names(
    node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> set[str]:
    """The last name of each decorator, called or not."""
    names: set[str] = set()
    for decorator in node.decorator_list:
        target = decorator
        while isinstance(target, ast.Call):
            target = target.func
        if isinstance(target, ast.Attribute):
            names.add(target.attr)
        elif isinstance(target, ast.Name):
            names.add(target.id)
    return names


def base_name(base: ast.expr) -> str:
    """The last name of a base class expression, or an empty string."""
    if isinstance(base, ast.Attribute):
        return base.attr
    return base.id if isinstance(base, ast.Name) else ""


def method_kind(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """`method` or `property`, plus the suffixes for its decorators."""
    decorators = decorator_names(node)
    kind = "property" if decorators & PROPERTY_DECORATORS else "method"
    if marked := decorators & MARKED_DECORATORS:
        kind += "/" + ",".join(sorted(marked))
    if "staticmethod" in decorators:
        kind += "/static"
    elif "classmethod" in decorators:
        kind += "/cls"
    return kind


def definitions(cls: ast.ClassDef) -> list[Definition]:
    """The public names a class defines; the first definition wins."""
    is_field_class = bool(decorator_names(cls) & DATA_DECORATORS) or any(
        base_name(b) == "NamedTuple" for b in cls.bases)
    found: dict[str, Definition] = {}

    def add(name: str, line: int, kind: str) -> None:
        if not name.startswith("_"):
            found.setdefault(name, Definition(name, line, kind))

    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            add(node.name, node.lineno, method_kind(node))
        elif (isinstance(node, ast.AnnAssign)
              and isinstance(node.target, ast.Name)):
            if not is_field_class:
                add(node.target.id, node.lineno, "classattr")
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    add(target.id, node.lineno, "classattr")
    for node in ast.walk(cls):
        if (isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and isinstance(node.ctx, ast.Store)):
            add(node.attr, node.lineno, "attr")
    return list(found.values())


def uses(source: str) -> dict[str, list[int]]:
    """For each name, the 1-based lines that use it as `.name` or `name=`."""
    index: dict[str, list[int]] = defaultdict(list)
    for number, text in enumerate(source.splitlines(), 1):
        names = set(ATTRIBUTE_USE.findall(text))
        names.update(KEYWORD_OR_STORE.findall(text))
        for name in names:
            index[name].append(number)
    return index


def chapter_hits(chapter: str) -> list[Hit]:
    """Every unused-outside public class name in one chapter."""
    sources: dict[Path, str] = {}
    trees: dict[Path, ast.Module] = {}
    for path in code_files(chapter):
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            trees[path] = ast.parse(text)
        except SyntaxError:
            continue
        sources[path] = text
    if not trees:
        return []
    index = {path: uses(text) for path, text in sources.items()}
    prose = prose_words(chapter)
    hits: list[Hit] = []
    for path, tree in trees.items():
        lines = sources[path].splitlines()
        for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
            first, last = cls.lineno, cls.end_lineno or cls.lineno
            for d in definitions(cls):
                if d.name in prose:
                    continue
                if any(
                    d.name in found
                    and any(not (other == path and first <= n <= last)
                            for n in found[d.name])
                    for other, found in index.items()
                ):
                    continue
                word = re.compile(rf"\b{re.escape(d.name)}\b")
                internal = sum(
                    1 for n in range(first, min(last, len(lines)) + 1)
                    if n != d.line and word.search(lines[n - 1]))
                hits.append(Hit(display(path), d.line, cls.name, d.name,
                                d.kind, internal))
    return hits


def find() -> list[Hit]:
    """Every hit in the book, sorted by path, line, and name."""
    hits = [h for chapter in chapters() for h in chapter_hits(chapter)]
    return sorted(hits, key=lambda h: (h.path, h.line, h.name))


def load_baseline(path: Path | None = None) -> set[str]:
    """The accepted keys, without comments or blank lines."""
    path = path or BASELINE
    if not path.exists():
        return set()
    return {
        line for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def write_baseline(entries: set[str], path: Path | None = None) -> None:
    """The header plus the sorted entries, with LF line endings."""
    path = path or BASELINE
    body = "".join(f"{entry}\n" for entry in sorted(entries))
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fail", action="store_true",
                    help="exit 1 when any NEW hit is found")
    ap.add_argument("--all", action="store_true",
                    help="print every hit, marked NEW or accepted")
    ap.add_argument("--accept", action="store_true",
                    help="add the NEW hits to the baseline and drop "
                         "stale entries")
    args = ap.parse_args(argv)
    found = find()
    baseline = load_baseline()
    current = {h.key for h in found}
    new = [h for h in found if h.key not in baseline]
    stale = sorted(baseline - current)
    if args.accept:
        write_baseline((baseline - set(stale)) | {h.key for h in new})
        print(f"Baseline: added {len(new)}, dropped {len(stale)} "
              f"stale, in {display(BASELINE)}")
        return 0
    for h in found:
        accepted = h.key in baseline
        if accepted and not args.all:
            continue
        mark = "accepted" if accepted else "NEW"
        print(f"{mark:8} {h.path}:{h.line}: {h.owner}.{h.name} "
              f"({h.kind}, {h.internal} references inside the class)")
    for entry in stale:
        print(f"stale    {entry}")
    print(f"{len(new)} new, {len(found) - len(new)} accepted"
          + (f", {len(stale)} stale" if stale else ""))
    return 1 if args.fail and new else 0


if __name__ == "__main__":
    raise SystemExit(main())
