#!/usr/bin/env python
"""Parse paragraphs with spaCy and print every sentence's dependency table.

This is the spaCy half of `tools/parsed_prose.py`, and it runs in a
throwaway environment, not the project's: the book pins a Python that
spaCy has no wheel for, so `parsed_prose.py` starts this file with
`uv run --no-project --python 3.12 --with spacy ...` and talks to it
over JSON. It therefore imports nothing from `tools/`.

Input on stdin: `{"texts": ["paragraph", ...]}`. Output on stdout: one
entry per text, a list of sentences, each a list of tokens. A token is
a dict with `i` (its index within the sentence), `text`, `lemma`,
`pos`, `tag`, `dep`, `head` (the index within the sentence of its
head; the root points at itself), `idx` (its character offset within
the paragraph), `punct` (is it punctuation), and `morph` (its
morphology as a string, such as `Tense=Pres|VerbForm=Fin`).

The rules that read the table live in the checks (`subject_gap.py`,
`sentence_shapes.py`), so a new rule never needs a new parse.
"""

import json
import sys

import spacy  # ty: ignore[unresolved-import]


def main() -> None:
    request = json.load(sys.stdin)
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    results = []
    for doc in nlp.pipe(request["texts"]):
        sentences = []
        for sent in doc.sents:
            start = sent.start
            sentences.append([
                {
                    "i": tok.i - start,
                    "text": tok.text,
                    "lemma": tok.lemma_,
                    "pos": tok.pos_,
                    "tag": tok.tag_,
                    "dep": tok.dep_,
                    "head": tok.head.i - start,
                    "idx": tok.idx,
                    "punct": bool(tok.is_punct),
                    "morph": str(tok.morph),
                }
                for tok in sent
            ])
        results.append(sentences)
    json.dump(results, sys.stdout)


if __name__ == "__main__":
    main()
