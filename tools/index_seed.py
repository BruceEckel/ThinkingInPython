#!/usr/bin/env python
"""Seed `tools/data/index_terms.toml` from conventions the book follows.

This is a one-time seed that the author prunes, never a step the build
repeats. It ran once on 2026-10-16 to write the first term file;
after that the file is hand-edited, and running this again would
overwrite every pruned entry, so it refuses to write over an existing
file unless given `--force`. `tools/book_index.py` reads the file and
computes the locators on every build.

The seed is the mechanical harvest INDEXING.md calls option C,
packages 1 and 2 of its Recommendation:

- **Definitions** (`kind = "concept"`). Every italic span in
  `Chapters/`, since the book italicizes a term where it introduces
  it. Skipped: capitalized pattern names (the next group covers them;
  a lowercase *decorator* is Python's and stays), spans of
  more than four words (quotations, maxims, long titles), spans that
  hold a code span, and the `STOP` list of emphasis words, which the
  file keeps as its top-level `stop` so `tip index-report` skips them
  too. Singular and plural spans merge, and so do spellings that differ
  only by case. The heading keeps its capitals when the book
  capitalizes the term mid-sentence (*Liskov Substitution Principle*)
  and is lowercase otherwise. `match` holds the term and its plural.
- **Patterns** (`kind = "pattern"`). Every name in
  `tools/data/pattern_names.txt`; names that differ only by accent
  (Façade, Facade) share an entry.
- **Python names** (`kind = "python"`, `code = true`). Names written in
  inline code in the prose that are builtins or keywords, names a
  listing imports from the standard library, standard-library modules
  and their dotted attributes, special methods (`__init__`), names used
  in three or more chapters, and names that appear in a heading.
  Anything else, such as an example's own `greet()`, drops out. The
  heading takes the form the prose writes most often (`print()`,
  `@dataclass`, `Protocol`), and `match` holds the bare name, matched
  case-sensitively in code spans and listings. A dotted `typing.Protocol`
  folds into `Protocol` when both qualify. A name whose entry would
  carry more than `CEILING` locators (`print()`, `self`) is left out
  and listed in a comment at the top of the file, so the author can
  add it back with a tighter pattern or subentries.
- **PEPs** (`kind = "pep"`). Every `PEP \\d+` in the prose.

Usage:
    python -m tools.index_seed            # write the file if absent
    python -m tools.index_seed --force    # overwrite it
    python -m tools.index_seed --dry-run  # print the counts only
"""

import argparse
import builtins
import datetime
import json
import keyword
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from tools.book_index import (
    CODE_SPAN, SILENT_KINDS, TERMS_FILE, ChapterSource, Corpus, Term,
    book_chapters, locate, sort_key)
from tools.pattern_names import default_names, split_names
from tools.repo import write_text_lf

# Italic spans that are emphasis, not terms: function words, two
# verbs stressed in a list, and the book's own part names.
STOP = ("enable", "every", "exact", "first", "how", "include",
        "inside", "is", "n", "s", "what", "whether", "which",
        "Foundations", "Functional", "Patterns", "Techniques")
MAX_WORDS = 4
# A concept with more locators than this keeps only its italic
# occurrences, and a Python name with more is left out of the seed
# (see the module docstring).
CEILING = 25
PYTHON_NAME = re.compile(
    r"^(@?)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(\(\))?$")
DUNDER = re.compile(r"^__\w+__$")
# A code span naming a file (`ask_tell.py`) is a listing or a data
# file, not a Python name.
FILE_TYPES = frozenset({"py", "pyi", "md", "txt", "toml", "json",
                        "csv", "cfg", "ini", "yaml", "lock"})
IMPORT_FROM = re.compile(
    r"^\s*from\s+([\w.]+)\s+import\s+(\([^)]*\)|[^\n#]+)", re.MULTILINE)
IMPORT = re.compile(r"^\s*import\s+([^\n#]+)", re.MULTILINE)
PEP = re.compile(r"\bPEP\s+(\d+)\b")
SENTENCE_END = ".!?:>\n"
# A list, quote, or table marker, and a link's opening bracket: what
# precedes an italic span that opens a list item or a table cell.
LEAD_MARK = re.compile(r"(?:[-*+>]|\d+[.)]|\|)?\s*\[?")


@dataclass
class Seed:
    term: str
    kind: str
    match: list[str]
    code: bool = False
    note: str = ""


@dataclass
class NameUse:
    chapters: set[str] = field(default_factory=set)
    forms: Counter[str] = field(default_factory=Counter)
    in_heading: bool = False


def plural(term: str) -> str:
    head, _, last = term.rpartition(" ")
    if re.search(r"(s|x|z|ch|sh)$", last):
        last += "es"
    elif re.search(r"[^aeiou]y$", last):
        last = last[:-1] + "ies"
    else:
        last += "s"
    return f"{head} {last}" if head else last


def singular_key(text: str) -> str:
    """The lowercase singular form two spellings merge under."""
    k = text.lower()
    for suffix, repl in (("ies", "y"), ("sses", "ss"), ("ches", "ch"),
                         ("shes", "sh"), ("xes", "x"), ("s", "")):
        if k.endswith(suffix) and not k.endswith("ss"):
            return k[:-len(suffix)] + repl
    return k


def fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def pattern_seeds(names: list[str]) -> list[Seed]:
    groups: dict[str, list[str]] = defaultdict(list)
    for name in names:
        groups[fold(name)].append(name)
    seeds = []
    for spellings in groups.values():
        # The accented spelling is the heading (Façade).
        spellings.sort(key=lambda s: (s == fold(s).title(), s))
        seeds.append(Seed(spellings[0], "pattern", spellings))
    return seeds


def concept_seeds(corpus: Corpus, names: list[str]) -> list[Seed]:
    pattern_spans = set(names) | {n + "s" for n in names}
    stop = {s.lower() for s in STOP}
    text = corpus.prose.text
    groups: dict[str, list[tuple[str, bool]]] = defaultdict(list)
    for start, end in corpus.italics:
        raw = text[start:end]
        if "  " in raw:     # a code span was masked inside it
            continue
        span = " ".join(raw.split()).strip(" ,;:.")
        span = re.sub(r"['’]s$", "", span)
        if (not span or len(span.split()) > MAX_WORDS
                or span in pattern_spans or span.lower() in stop
                or "[" in span or "]" in span):
            continue
        para_start = corpus.prose.starts[corpus.prose.at(start)]
        before = text[max(para_start, start - 80):start - 1].rstrip()
        initial = (start - 1 <= para_start or not before
                   or before[-1] in SENTENCE_END
                   or LEAD_MARK.fullmatch(before) is not None)
        groups[singular_key(span)].append((span, initial))
    seeds = []
    for uses in groups.values():
        midsentence_caps = [s for s, initial in uses
                            if not initial and s != s.lower()]
        lower_seen = any(s == s.lower() for s, _ in uses)
        if not lower_seen and (midsentence_caps
                               or not lowercase_word(uses, text)):
            forms = Counter(midsentence_caps or [s for s, _ in uses])
            term = singular_form(forms.most_common(1)[0][0], uses)
        else:
            forms = Counter(s.lower() for s, _ in uses)
            term = singular_form(forms.most_common(1)[0][0], uses)
        match = [term]
        if not term.endswith("s"):
            match.append(plural(term))
        found = locate(Term(term, "concept", tuple(match)), corpus)
        if len(found) > CEILING:
            # Too common a word to index every use: keep the
            # defining occurrences, where the term is italic.
            match = [italic_only(m) for m in match]
        seeds.append(Seed(term, "concept", match))
    return seeds


def italic_only(item: str) -> str:
    """A `re:` match item that finds `item` only as a whole italic span."""
    words = r"\s+".join(re.escape(w) for w in item.split())
    return rf"re:(?<=\*){words}(?=\*)"


def lowercase_word(uses: list[tuple[str, bool]], text: str) -> bool:
    """Whether spans capitalized only at a sentence start are an
    ordinary words: "Class decorators" are, since the prose also
    writes "class" in lowercase, while "Java", "C++", and "C3
    linearization" are not."""
    for span, _ in uses:
        first = span.split()[0]
        if not (first[1:].isalpha() and span[1:] == span[1:].lower()):
            return False
    lower = uses[0][0].split()[0].lower()
    return re.search(rf"(?<!\w){re.escape(lower)}", text) is not None


def singular_form(term: str, uses: list[tuple[str, bool]]) -> str:
    """`term`, made singular when the book also writes the singular."""
    written = {s.lower() for s, _ in uses}
    key = singular_key(term)
    if key != term.lower() and key in written:
        return term[:len(key)] if term.lower().startswith(key) else key
    return term


def stdlib_imports(chapters: list[ChapterSource]
                   ) -> tuple[set[str], set[str]]:
    """(names, modules) the listings import from the standard library."""
    stdlib = set(sys.stdlib_module_names)
    names: set[str] = set()
    modules: set[str] = set()
    for ch in chapters:
        for m in IMPORT_FROM.finditer(ch.body):
            module = m.group(1)
            if module.split(".")[0] not in stdlib:
                continue
            modules.add(module)
            for item in m.group(2).strip("()").split(","):
                name = item.split(" as ")[0].strip()
                if name.isidentifier():
                    names.add(name)
        for m in IMPORT.finditer(ch.body):
            for item in m.group(1).split(","):
                module = item.split(" as ")[0].strip()
                if module.split(".")[0] in stdlib:
                    modules.add(module)
    return names, modules


def python_seeds(corpus: Corpus, chapters: list[ChapterSource]
                 ) -> tuple[list[Seed], list[str]]:
    """The Python names, and the ones left out for `CEILING`."""
    uses: dict[str, NameUse] = defaultdict(NameUse)
    for place in corpus.places:
        unit = place.unit
        if unit.kind in SILENT_KINDS or unit.kind == "listing":
            continue
        ch = corpus.chapters[place.chapter]
        lines = ch.body.split("\n")
        raw = (unit.title if unit.kind == "heading"
               else " ".join(lines[unit.first:unit.last + 1]))
        for m in CODE_SPAN.finditer(raw):
            content = m.group(0).strip("`").strip()
            name = PYTHON_NAME.match(content)
            if (name is None or len(name.group(2)) < 2
                    or name.group(2).rsplit(".", 1)[-1] in FILE_TYPES):
                continue
            use = uses[name.group(2)]
            use.chapters.add(ch.number)
            use.forms[f"{name.group(1)}{name.group(2)}{name.group(3) or ''}"] += 1
            use.in_heading |= unit.kind == "heading"
    builtin = {n for n in dir(builtins) if not n.startswith("_")}
    builtin |= set(keyword.kwlist) | (set(keyword.softkwlist) - {"_"})
    stdlib = set(sys.stdlib_module_names)
    imported, modules = stdlib_imports(chapters)

    def qualifies(name: str, use: NameUse) -> bool:
        first = name.split(".")[0]
        return (name in builtin or name in imported or name in modules
                or (first in stdlib and "." in name)
                or name in stdlib or bool(DUNDER.match(name))
                or len(use.chapters) >= 3 or use.in_heading)

    chosen = {n for n, u in uses.items() if qualifies(n, u)}
    # typing.Protocol folds into Protocol when both qualify.
    chosen = {n for n in chosen
              if not ("." in n and n.split(".")[0] in stdlib | modules
                      and n.rsplit(".", 1)[1] in chosen)}
    seeds: list[Seed] = []
    left_out: list[str] = []
    for name in chosen:
        form = uses[name].forms.most_common(1)[0][0]
        seed = Seed(form, "python", [name], code=True)
        term = Term(seed.term, "python", tuple(seed.match), code=True)
        count = len(locate(term, corpus))
        if count > CEILING:
            left_out.append(f"{form} ({count})")
        else:
            seeds.append(seed)
    left_out.sort(key=sort_key)
    return seeds, left_out


def pep_seeds(corpus: Corpus) -> list[Seed]:
    numbers = {int(m.group(1)) for m in PEP.finditer(corpus.prose.text)}
    return [Seed(f"PEP {n}", "pep", [f"PEP {n}"]) for n in sorted(numbers)]


def toml_string(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def toml_list(items: list[str]) -> str:
    return "[" + ", ".join(toml_string(i) for i in items) + "]"


def render(seeds: list[Seed], left_out: list[str]) -> str:
    today = datetime.date.today().isoformat()
    out = [
        "# The book's index entries, read by tools/book_index.py.",
        f"# Seeded by tools/index_seed.py on {today}; edit by hand from",
        "# here on (the seeder does not run again). One [[entry]] table",
        "# per entry: term, kind (concept, pattern, python, pep), match",
        "# (plain strings on word boundaries, or `re:` regexes), and",
        "# optional under, see, see_also, code. book_index.py's",
        "# docstring has the rules; `tip index-report` checks the file.",
        "#",
        f"# Python names left out of the seed for more than {CEILING}",
        "# locators each (add one back with subentries or a tighter",
        "# match):",
    ]
    line = "#  "
    for item in left_out:
        if len(line) + len(item) + 2 > 72:
            out.append(line.rstrip(","))
            line = "#  "
        line += f" {item},"
    out += [line.rstrip(","), "",
            "# Italic spans that are emphasis, not terms.",
            f"stop = {toml_list(sorted(STOP, key=str.lower))}", ""]
    titles = {"concept": "Definitions: italic terms",
              "pattern": "Design patterns",
              "python": "Python names",
              "pep": "PEPs"}
    for kind in ("concept", "pattern", "python", "pep"):
        group = sorted((s for s in seeds if s.kind == kind),
                       key=lambda s: sort_key(s.term))
        out += [f"# {'-' * 66}", f"# {titles[kind]}", f"# {'-' * 66}", ""]
        for seed in group:
            out += ["[[entry]]", f"term = {toml_string(seed.term)}",
                    f'kind = "{seed.kind}"',
                    f"match = {toml_list(seed.match)}"]
            if seed.code:
                out.append("code = true")
            out.append("")
    return "\n".join(out)


def seed() -> tuple[list[Seed], list[str]]:
    chapters = book_chapters()
    names, excluded = split_names(default_names())
    corpus = Corpus(chapters, excluded)
    seeds = pattern_seeds(names)
    taken = {s.term for s in seeds}
    for s in concept_seeds(corpus, names):
        if s.term not in taken:
            seeds.append(s)
            taken.add(s.term)
    python, left_out = python_seeds(corpus, chapters)
    for s in python + pep_seeds(corpus):
        if s.term not in taken:
            seeds.append(s)
            taken.add(s.term)
    return seeds, left_out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing term file")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the counts and write nothing")
    args = ap.parse_args(argv)
    seeds, left_out = seed()
    by_kind = Counter(s.kind for s in seeds)
    for kind, n in sorted(by_kind.items()):
        print(f"{kind:<8} {n}")
    print(f"python names left out over {CEILING} locators: "
          f"{len(left_out)}")
    if args.dry_run:
        return 0
    if TERMS_FILE.exists() and not args.force:
        print(f"error: {TERMS_FILE.name} exists; the seed is a one-time "
              "step (pass --force to overwrite the pruned file)")
        return 1
    write_text_lf(TERMS_FILE, render(seeds, left_out))
    print(f"Wrote {TERMS_FILE.relative_to(TERMS_FILE.parents[2])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
