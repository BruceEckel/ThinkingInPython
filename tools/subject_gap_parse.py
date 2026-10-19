#!/usr/bin/env python
"""Parse paragraphs with spaCy and list each subject held open from its verb.

This is the spaCy half of `tools/subject_gap.py`, and it runs in a
throwaway environment, not the project's: the book pins a Python that
spaCy has no wheel for, so `subject_gap.py` starts this file with
`uv run --no-project --python 3.12 --with spacy ...` and talks to it
over JSON. It therefore imports nothing from `tools/`.

Input on stdin: `{"gap": 9, "texts": ["paragraph", ...]}`. Output on
stdout: one list per paragraph, each hit a dict with the subject
head's character offset in the paragraph (`offset`), the subject and
verb words, the number of words between them (`gap`), the dependency
labels of the subject's postmodifiers (`kinds`), and the sentence.

A hit is a nominal subject (`nsubj` or `nsubjpass`) whose head verb
follows it, with at least `gap` non-punctuation tokens between, nearly
all of them inside the subject's own subtree: a relative clause, a
participle, a prepositional chain, an appositive, or a parenthetical
hanging off the subject. An adverbial between subject and verb does
not count, since the subject is not what the reader is holding open.
"""

import json
import sys

import spacy  # ty: ignore[unresolved-import]

PUNCT_SLACK = 1
"""Tokens in the gap allowed to lie outside the subject's subtree."""


def main() -> None:
    request = json.load(sys.stdin)
    gap = int(request["gap"])
    nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])
    results = []
    for doc in nlp.pipe(request["texts"]):
        hits = []
        for sent in doc.sents:
            for tok in sent:
                if tok.dep_ not in ("nsubj", "nsubjpass"):
                    continue
                verb = tok.head
                if verb.i <= tok.i:
                    continue
                words = [t for t in sent
                         if tok.i < t.i < verb.i and not t.is_punct]
                if len(words) < gap:
                    continue
                owned = {t.i for t in tok.subtree}
                outside = [t for t in words if t.i not in owned]
                if len(outside) > PUNCT_SLACK:
                    continue
                kinds = sorted({c.dep_ for c in tok.children
                                if c.i > tok.i and not c.is_punct})
                hits.append({
                    "offset": tok.idx,
                    "subject": tok.text,
                    "verb": verb.text,
                    "gap": len(words),
                    "kinds": kinds,
                    "sentence": " ".join(sent.text.split()),
                })
        results.append(hits)
    json.dump(results, sys.stdout)


if __name__ == "__main__":
    main()
