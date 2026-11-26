#!/usr/bin/env python
"""Count syllables with the CMU Pronouncing Dictionary.

This is the dictionary half of `tools/reading_level.py`, and it runs in
a throwaway environment, not the project's: the project adds no
dependency for a report-only survey, so `reading_level.py` starts this
file with `uv run --no-project --python 3.12 --with cmudict ...` and
talks to it over JSON. It therefore imports nothing from `tools/`, the
way `tools/spacy_parse.py` does.

Input on stdin: `{"words": ["table", "namespace", ...]}`. Output on
stdout: `{"counts": {"table": 2, ...}}`, one entry for each word the
dictionary has and none for a word it lacks. The count is the number of
phones in the dictionary's first pronunciation of the word that end in
a digit, the stress mark of a vowel.
"""

import json
import sys

import cmudict  # ty: ignore[import-not-found]


def syllables(phones: list[str]) -> int:
    """The vowels in one pronunciation: phones that end in a stress digit."""
    return sum(1 for phone in phones if phone[-1].isdigit())


def main() -> None:
    request = json.load(sys.stdin)
    entries = cmudict.dict()
    counts: dict[str, int] = {}
    for word in request["words"]:
        pronunciations = entries.get(word.lower())
        if pronunciations:
            counts[word] = syllables(pronunciations[0])
    json.dump({"counts": counts}, sys.stdout)


if __name__ == "__main__":
    main()
