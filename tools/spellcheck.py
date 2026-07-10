#!/usr/bin/env python
"""Full-dictionary spell check of the book's prose.

codespell only knows a curated list of common misspellings, so a novel typo
("fixted") slips through. This checks every prose word against a real English
dictionary (pyspellchecker) plus a project word list, so anything not a known
word or an accepted term is reported.

It checks prose only. Fenced and indented code, tables, blockquotes, and HTML
are skipped via the md_prose classifier; inline code spans, footnotes, and link
URLs are stripped from each line so identifiers and paths are not flagged.
Headings and list-item text are checked; their markers are not.

Accepted terms (technical words, names, coined words) go in tools/wordlist.txt,
one lowercase word per line, with `#` comments allowed. Unknown words are
reported as `path:line` and a non-zero exit makes it a gate.

Whenever anything is unknown, the run ends with a paste-ready block: every
unique unknown word, one per line, sorted, with no locations or counts, so
the list can be pasted straight into tools/wordlist.txt after a quick skim
for real typos.

--add skips that paste step and writes the words into the wordlist file
directly (merged with what's already there, deduplicated, resorted). It
still exits 0 either way, since after --add the wordlist is caught up by
definition. It does not distinguish a genuine term from a typo, so review
the diff (`git diff tools/wordlist.txt`) before committing, and revert any
line that is actually a typo rather than a fix in the prose.

Usage:
    python tools/spellcheck.py               # check all of Chapters/
    python tools/spellcheck.py --summary     # unique unknowns, by count
    python tools/spellcheck.py --add         # accept every unknown word
    python tools/spellcheck.py Chapters/09_Testing.md
"""
import argparse
import re
from collections import Counter
from pathlib import Path

from spellchecker import SpellChecker

from tools_config import TOOLS_DIR
from md_prose import FENCE, HEADING, LIST_ITEM, is_prose_line, mask
from tools_repo import add_paths_arg, md_files

WORDLIST = TOOLS_DIR / "wordlist.txt"

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
    path.write_text("\n".join(header + [""] + body) + "\n", encoding="utf-8")


def prose_text(line: str) -> str | None:
    """The prose part of a line (heading/list markers stripped), or None."""
    heading = HEADING.match(line)
    if heading:
        return line[heading.end():]
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
    marker = ""
    for lineno, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), 1):
        if in_fence:
            if FENCE.match(line) and line.strip().startswith(marker):
                in_fence = False
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
    ap.add_argument("--add", action="store_true",
                    help="write every unknown word into --wordlist "
                         "(sorted, deduplicated) instead of reporting them")
    args = ap.parse_args(argv)

    spell = SpellChecker()
    accepted = load_wordlist(args.wordlist)
    if accepted:
        spell.word_frequency.load_words(accepted)

    per_file = {p: collect(p) for p in md_files(args.paths)}
    every_word = {w for hits in per_file.values() for _, w in hits}
    unknown = spell.unknown(every_word) - accepted

    if args.add:
        if not unknown:
            print("No unknown words; wordlist unchanged.")
            return 0
        rewrite_wordlist(args.wordlist, accepted | unknown)
        print(f"Added {len(unknown)} word(s) to {args.wordlist}:")
        for word in sorted(unknown):
            print(f"  {word}")
        print("\nReview the diff before committing "
              f"(git diff {args.wordlist}) -- a real typo belongs in the "
              "prose, not the wordlist.")
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
                  "Fix the typos or add terms to tools/wordlist.txt.")

    if unknown:
        print("\nPaste into tools/wordlist.txt:")
        for word in sorted(unknown):
            print(word)
        return 1

    print("No spelling issues.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
