"""Tests for tools/parsed_prose.py, with the spaCy half stubbed out.

A stub parser answers each text with one sentence of whitespace-split
tokens, so the tests check the plumbing: one text per paragraph, one
call for all uncached paragraphs, the cache file, its reuse, and the
unavailable-parser path.
"""

import json
from pathlib import Path
import pytest
from tools import parsed_prose
from tools.markdown import Document
from tools.parsed_prose import (
    ParserUnavailable,
    RawSentence,
    Sentence,
    Token,
    children,
    conj_verbs,
    coordinator,
    finite,
    parsed,
    subject_of,
    subtree,
)


@pytest.fixture(autouse=True)
def cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    cache_dir = tmp_path / "parses"
    monkeypatch.setattr(parsed_prose, "CACHE_DIR", cache_dir)
    return cache_dir


def tok(i: int, text: str, head: int, dep: str = "dep", pos: str = "X",
        tag: str = "X") -> dict[str, object]:
    return {"i": i, "text": text, "lemma": text, "pos": pos, "tag": tag,
            "dep": dep, "head": head, "idx": 0, "punct": False,
            "morph": ""}


class Spy:
    """A parser stub that records its calls."""

    def __init__(self) -> None:
        self.calls: list[list[str]] = []

    def __call__(self, texts: list[str]) -> list[list[RawSentence]]:
        self.calls.append(texts)
        out: list[list[RawSentence]] = []
        position = 0
        for text in texts:
            sentence: RawSentence = []
            for i, word in enumerate(text.split()):
                sentence.append({**tok(i, word, 0),
                                 "idx": position})
                position += len(word) + 1
            out.append([sentence])
        return out


def write(path: Path, text: str) -> Document:
    path.write_text(text, encoding="utf-8")
    return Document.parse(path)


def test_one_text_per_paragraph_and_a_cache_file(
        tmp_path: Path, cache: Path) -> None:
    spy = Spy()
    doc = write(tmp_path / "a.md", "# H\n\nOne two.\n\nThree\nfour.\n")
    [paras] = parsed([doc], spy)
    assert spy.calls == [["One two.", "Three four."]]
    assert [p.text for p in paras] == ["One two.", "Three four."]
    assert [len(p.sentences) for p in paras] == [1, 1]
    assert paras[1].lines[0] == 5 and paras[1].lines[-1] == 6
    [cached] = list(cache.glob("*.json"))
    assert "__" in cached.name and ":" not in cached.name
    data = json.loads(cached.read_text(encoding="utf-8"))
    assert len(data["hash"]) == 64 and len(data["paragraphs"]) == 2


def test_second_call_reuses_the_cache(tmp_path: Path) -> None:
    doc = write(tmp_path / "a.md", "One two.\n")
    first = Spy()
    parsed([doc], first)
    second = Spy()
    [paras] = parsed([doc], second)
    assert first.calls and second.calls == []
    assert paras[0].sentences[0].tokens[0].text == "One"


def test_a_changed_text_reparses_only_that_document(tmp_path: Path) -> None:
    a = write(tmp_path / "a.md", "One two.\n")
    b = write(tmp_path / "b.md", "Five six.\n")
    parsed([a, b], Spy())
    a = write(tmp_path / "a.md", "One two three.\n")
    spy = Spy()
    parsed([a, b], spy)
    assert spy.calls == [["One two three."]]


def test_all_uncached_paragraphs_share_one_call(tmp_path: Path) -> None:
    a = write(tmp_path / "a.md", "One.\n\nTwo.\n")
    b = write(tmp_path / "b.md", "Three.\n")
    spy = Spy()
    result = parsed([a, b], spy)
    assert spy.calls == [["One.", "Two.", "Three."]]
    assert [len(r) for r in result] == [2, 1]


def test_no_prose_never_calls_the_parser(tmp_path: Path) -> None:
    doc = write(tmp_path / "a.md", "```python\nx = 1\n```\n")
    spy = Spy()
    assert parsed([doc], spy) == [[]]
    assert spy.calls == []


def test_use_cache_false_writes_nothing(
        tmp_path: Path, cache: Path) -> None:
    doc = write(tmp_path / "a.md", "One two.\n")
    parsed([doc], Spy(), use_cache=False)
    assert not cache.exists()


def test_unavailable_parser_propagates(tmp_path: Path) -> None:
    doc = write(tmp_path / "a.md", "One two.\n")

    def gone(texts: list[str]) -> list[list[RawSentence]]:
        raise ParserUnavailable("uv: command not found")

    with pytest.raises(ParserUnavailable):
        parsed([doc], gone)


def sentence(*rows: dict[str, object]) -> Sentence:
    tokens = tuple(Token(**row) for row in rows)  # ty: ignore[invalid-argument-type]
    return Sentence(tokens, 0, 0)


def test_helpers_read_the_token_table() -> None:
    # "Remove it and you see": Remove(ROOT) it and(cc) see(conj) you
    s = sentence(
        tok(0, "Remove", 0, "ROOT", "VERB", "VB"),
        tok(1, "it", 0, "dobj", "PRON", "PRP"),
        tok(2, "and", 0, "cc", "CCONJ", "CC"),
        tok(3, "you", 4, "nsubj", "PRON", "PRP"),
        tok(4, "see", 0, "conj", "VERB", "VBP"),
    )
    root, see = s.tokens[0], s.tokens[4]
    assert [c.text for c in children(root, s)] == ["it", "and", "see"]
    assert subject_of(root, s) is None
    assert subject_of(see, s) == s.tokens[3]
    assert conj_verbs(root, s) == [see]
    assert coordinator(see, s) == "and"
    assert not finite(root, s) and finite(see, s)
    assert subtree(see, s) == {3, 4}


def test_finite_through_an_auxiliary() -> None:
    s = sentence(
        tok(0, "it", 2, "nsubj", "PRON", "PRP"),
        tok(1, "can", 2, "aux", "AUX", "MD"),
        tok(2, "run", 2, "ROOT", "VERB", "VB"),
    )
    assert finite(s.tokens[2], s)
