"""Cached TypeSafe judgments about the book's prose.

Two tools ask a model a question about a sentence:
`grounding_triage.py` asks whether a sentence attributes code names to
the chapter it links, and `link_support.py` asks whether a linked
section covers what the sentence credits it with. Both answer the kind
of question `check_self_reference.py` and `check_claims.py` can only
narrow, because the answer depends on reading.

This module holds what the two share: a verdict store in
`tools/data/`, a key that survives reflowing, and one function that
sends a batch of questions to TypeSafe concurrently.

The store is committed, which makes the gate offline. A verdict is
keyed by a hash of everything the question saw, so an edit to the
sentence (or, for link support, to the linked section) retires the old
verdict and leaves that sentence unjudged until someone runs the tool
again. A reflow changes only line breaks, which the key ignores.

Asking needs `typesafe-sdk` and a `TYPESAFE_API_KEY` in the environment.
The SDK stays out of `pyproject.toml`: it builds `pydantic-core` from
source on the pinned Python, which a fresh cloud session cannot do, and
nothing but these two commands uses it. Their tip tasks add it with
`uv run --with typesafe-sdk`. Reading the store needs neither.
"""

import asyncio
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from tools.repo import write_text_lf

CONCURRENCY = 8
SECTION_LIMIT = 12_000
"""Characters of a linked section a question sees. A chapter-level
section with many subsections runs past this, and the tail is cut."""


def key(*parts: str) -> str:
    """A stable id for one question's inputs, blind to line breaks."""
    joined = "\x00".join(" ".join(p.split()) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def load(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, store: Mapping[str, Mapping[str, Any]]) -> None:
    """Write sorted by file and line, so a diff reads in book order."""
    ordered = dict(sorted(
        store.items(), key=lambda kv: (kv[1]["file"], kv[1]["line"], kv[0])))
    write_text_lf(path, json.dumps(ordered, indent=1, ensure_ascii=False)
                  + "\n")


def ask(
    requests: Sequence[tuple[dict[str, Any], dict[str, Any]]],
    progress: Callable[[int, int], None] = lambda done, total: None,
) -> list[dict[str, dict[str, Any]]]:
    """Answer each (state, {question_id: question kwargs}) pair.

    A question's kwargs build a Choice, or a Score when they carry
    `"type": "score"`. Returns, per request, `{question_id: answer}` in
    request order, where a Choice answer is `{"choice", "confidence",
    "probabilities"}` and a Score answer is `{"score", "confidence",
    "probabilities"}`. The SDK retries rate limits and overloads itself.
    """
    # Not in .venv; the tip tasks add it (see the docstring).
    from typesafe_sdk import (  # ty: ignore[unresolved-import]
        AsyncTypeSafeClient, Choice, Score)

    def build(q: dict[str, Any]) -> Any:
        fields = {k: v for k, v in q.items() if k != "type"}
        return Score(**fields) if q.get("type") == "score" else Choice(
            **fields)

    def read(a: Any) -> dict[str, Any]:
        probabilities = {o: round(p, 3) for o, p in a.probabilities.items()}
        head = ({"score": round(a.score, 3)} if a.type == "score"
                else {"choice": a.choice})
        return {**head, "confidence": round(a.confidence, 3),
                "probabilities": probabilities}

    async def run() -> list[dict[str, dict[str, Any]]]:
        gate = asyncio.Semaphore(CONCURRENCY)
        done = 0
        async with AsyncTypeSafeClient() as client:
            async def one(state: dict[str, Any],
                          questions: dict[str, Any]
                          ) -> dict[str, dict[str, Any]]:
                nonlocal done
                async with gate:
                    r = await client.system_one(
                        state=state,
                        questions={k: build(q)
                                   for k, q in questions.items()})
                done += 1
                progress(done, len(requests))
                return {k: read(a) for k, a in r.answers.items()}
            return await asyncio.gather(
                *(one(s, q) for s, q in requests))

    return asyncio.run(run())


def title(text: str) -> str:
    """A chapter's H1, which a question shows in place of its filename."""
    return next((line[2:].strip() for line in text.splitlines()
                 if line.startswith("# ")), "")
