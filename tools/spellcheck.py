#!/usr/bin/env python
"""Full-dictionary spell check of the book's prose.

codespell only knows a curated list of common misspellings, so a novel typo
("fixted") slips through. This checks every prose word against a real English
dictionary (pyspellchecker) plus a project word list, so anything not a known
word or an accepted term is reported.

It checks prose only. Fenced and indented code, tables, blockquotes, and HTML
are skipped via the tools.prose classifier; inline code spans, footnotes, and link
URLs are stripped from each line so identifiers and paths are not flagged.
Headings and list-item text are checked; their markers are not, and neither is
a heading's explicit `{#anchor}`, whose slug splits into non-words ("sys" out of
`sys-monitoring`). A multi-line HTML comment is tracked the way a fence is,
since the classifier is stateless and sees only its opening line.

Accepted terms (technical words, names, coined words) go in tools/data/wordlist.txt,
one lowercase word per line, with `#` comments allowed. Unknown words are
reported as `path:line` and a non-zero exit makes it a gate.

Whenever anything is unknown, the run ends with a paste-ready block: every
unique unknown word, one per line, sorted, with no locations or counts, so
the list can be pasted straight into tools/data/wordlist.txt after a quick skim
for real typos.

--add skips that paste step and writes the words into the wordlist file
directly (merged with what's already there, deduplicated, resorted). It
also runs codespell over the same paths, the way `make spell` does, and
writes every word codespell flags into its own list,
tools/data/codespell-ignore.txt, since the two checkers keep separate
lists and a word only codespell objects to (a class name such as
`OnlyOnce`, which codespell reads in code and this checker skips) would
otherwise still fail `make spell` after an --add. It exits 0 either way,
since after --add both lists are caught up by definition. It does not
distinguish a genuine term from a typo, so review both diffs
(`git diff tools/data/`) before committing, and revert any line that is
a typo rather than a term.

Usage:
    python -m tools.spellcheck               # check all of Chapters/
    python -m tools.spellcheck --summary     # unique unknowns, by count
    python -m tools.spellcheck --add         # accept every unknown word
    python -m tools.spellcheck Chapters/11_Techniques--Testing.md
"""
import argparse
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from spellchecker import SpellChecker

from tools.config import CHAPTERS_DIR, DATA_DIR, ROOT
from tools.prose import (
    FENCE, HEADING, HTML_COMMENT_CLOSE, HTML_COMMENT_OPEN, LIST_ITEM,
    is_prose_line, mask,
)
from tools.repo import add_paths_arg, md_files, write_text_lf

WORDLIST = DATA_DIR / "wordlist.txt"
CODESPELL_IGNORE = DATA_DIR / "codespell-ignore.txt"
# One codespell finding: `path:line: word ==> suggestion`. The path is
# non-greedy so a Windows drive letter's colon does not end it early.
_CODESPELL_HIT = re.compile(r"^.+?:\d+: (?P<word>\S+) ==> ")

_ANCHOR = re.compile(r"\{#[^}]*\}")              # a heading's explicit id
_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")   # [text](url) -> text
_URL = re.compile(r"(?:https?://|www\.)\S+")
_AUTOLINK = re.compile(r"<[^>\s]+>")
# A word: Unicode letters (so "façade" stays whole), with internal apostrophes.
_TOKEN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*")


def load_wordlist(path: Path) -> set[str]:
    words: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.split("#", 1)[0].strip().lower()
            if word:
                words.add(word)
    return words


def rewrite_wordlist(path: Path, words: set[str]) -> None:
    """Rewrite the wordlist file: keep the leading '#' comment block, replace
    the word list below it with `words`, sorted and deduplicated."""
    header: list[str] = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#") or not line.strip():
                header.append(line)
                continue
            break
    while header and not header[-1].strip():   # exactly one blank separator
        header.pop()
    body = sorted({w.strip().lower() for w in words if w.strip()})
    # No comment header (codespell-ignore.txt has none) means no blank
    # separator either, so the file starts at its first word.
    separator = [""] if header else []
    write_text_lf(path, "\n".join(header + separator + body) + "\n")


def parse_codespell(output: str) -> set[str]:
    """The words codespell flagged in its output, lowercased.

    codespell matches case-insensitively and reads its ignore file the
    same way, so the lowercase form is the one to store.
    """
    return {m["word"].lower()
            for line in output.splitlines()
            if (m := _CODESPELL_HIT.match(line))}


def codespell_unknown(paths: list[Path]) -> set[str]:
    """Run codespell over `paths` as `make spell` does and return the
    words it flags. Same interpreter, same working directory, so it
    reads the same [tool.codespell] config and ignore file."""
    proc = subprocess.run(
        [sys.executable, "-m", "codespell_lib", *map(str, paths)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode not in (0, 65):   # 65: findings; anything else broke
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"codespell exited {proc.returncode}")
    return parse_codespell(proc.stdout)


def prose_text(line: str) -> str | None:
    """The prose part of a line (heading/list markers stripped), or None.

    A heading's explicit `{#anchor}` goes too: it is an identifier, not
    prose, and its slug splits into words that are not (`sys-monitoring`
    gives "sys", `dont-start-the-engine` gives "dont").
    """
    heading = HEADING.match(line)
    if heading:
        return _ANCHOR.sub(" ", line[heading.end():])
    item = LIST_ITEM.match(line)
    if item:
        return item.group(4)
    if is_prose_line(line):
        return line
    return None


def tokens(text: str) -> list[str]:
    """Lowercased candidate words from one prose line."""
    masked, _ = mask(text)                       # drop inline code, footnotes
    masked = masked.replace("’", "'")       # normalize curly apostrophe
    masked = _LINK.sub(lambda m: f" {m.group(1)} ", masked)
    masked = _URL.sub(" ", masked)
    masked = _AUTOLINK.sub(" ", masked)
    out: list[str] = []
    for tok in _TOKEN.findall(masked):
        if tok.isupper():                        # acronym (TDD, MVC)
            continue
        if any(c.isupper() for c in tok[1:]):    # CamelCase / code-ish
            continue
        word = tok.lower()
        if word.endswith("'s"):                  # possessive
            word = word[:-2]
        word = word.strip("'")
        if len(word) >= 2:
            out.append(word)
    return out


def collect(path: Path) -> list[tuple[int, str]]:
    """(line_number, word) for every prose word in a file."""
    found: list[tuple[int, str]] = []
    in_fence = False
    in_comment = False
    marker = ""
    for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1):
        if in_fence:
            if FENCE.match(line) and line.strip().startswith(marker):
                in_fence = False
            continue
        if in_comment:
            in_comment = not HTML_COMMENT_CLOSE.search(line)
            continue
        if HTML_COMMENT_OPEN.match(line):
            in_comment = not HTML_COMMENT_CLOSE.search(line)
            continue
        fence = FENCE.match(line)
        if fence:
            in_fence = True
            marker = fence.group(1)[0] * 3
            continue
        text = prose_text(line)
        if text is not None:
            found.extend((lineno, w) for w in tokens(text))
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    add_paths_arg(ap)
    ap.add_argument("--wordlist", type=Path, default=WORDLIST,
                    help=f"accepted-words file (default: {WORDLIST.name})")
    ap.add_argument("--summary", action="store_true",
                    help="list unique unknown words with counts, not locations")
    ap.add_argument("--codespell-ignore", type=Path, default=CODESPELL_IGNORE,
                    help="codespell's ignore-words file, which --add also "
                         f"extends (default: {CODESPELL_IGNORE.name})")
    ap.add_argument("--add", action="store_true",
                    help="write every unknown word into --wordlist, and "
                         "every word codespell flags into --codespell-ignore "
                         "(both sorted, deduplicated) instead of reporting")
    args = ap.parse_args(argv)

    spell = SpellChecker()
    accepted = load_wordlist(args.wordlist)
    if accepted:
        spell.word_frequency.load_words(accepted)

    per_file = {p: collect(p) for p in md_files(args.paths)}
    every_word = {w for hits in per_file.values() for _, w in hits}
    unknown = spell.unknown(every_word) - accepted

    if args.add:
        if unknown:
            rewrite_wordlist(args.wordlist, accepted | unknown)
            print(f"Added {len(unknown)} word(s) to {args.wordlist}:")
            for word in sorted(unknown):
                print(f"  {word}")
        else:
            print("No unknown words; wordlist unchanged.")
        flagged = codespell_unknown(args.paths or [CHAPTERS_DIR])
        if flagged:
            ignored = load_wordlist(args.codespell_ignore)
            rewrite_wordlist(args.codespell_ignore, ignored | flagged)
            print(f"Added {len(flagged)} word(s) to {args.codespell_ignore}:")
            for word in sorted(flagged):
                print(f"  {word}")
        else:
            print("Nothing flagged by codespell; its ignore list unchanged.")
        if unknown or flagged:
            print("\nReview the diff before committing "
                  f"(git diff {DATA_DIR}) -- a real typo belongs in the "
                  "prose, not in either list.")
        return 0

    if args.summary:
        counts: Counter[str] = Counter()
        for hits in per_file.values():
            for _, w in hits:
                if w in unknown:
                    counts[w] += 1
        for word, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"{n:5}  {word}")
        print(f"\n{len(counts)} unique unknown word(s).")
    else:
        total = 0
        for path, hits in per_file.items():
            for lineno, word in hits:
                if word in unknown:
                    print(f'{path}:{lineno}: unknown word: "{word}"')
                    total += 1
        if total:
            print(f"\n{total} unknown word occurrence(s). "
                  "Fix the typos or add terms to tools/data/wordlist.txt.")

    if unknown:
        print("\nPaste into tools/data/wordlist.txt:")
        for word in sorted(unknown):
            print(word)
        return 1

    print("No spelling issues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
