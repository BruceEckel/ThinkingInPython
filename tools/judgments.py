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

Asking needs `typesafe-sdk` and a `TYPESAFE_API_KEY`. `api_key()` looks
in the process environment first, then, on Windows, in the user's
registry environment (`HKCU\\Environment`), where a variable set through
System Properties lives. A process started from a parent that predates
the variable inherits no copy of it, so on 2026-09-29 a Claude Code
session saw the key missing that every earlier session had found.
The SDK stays out of `pyproject.toml`: it builds `pydantic-core` from
source on the pinned Python, which a fresh cloud session cannot do, and
nothing but these two commands uses it. Their tip tasks add it with
`uv run --with typesafe-sdk`. Reading the store needs neither.
"""

import asyncio
import hashlib
import json
import os
import random
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from tools.repo import write_text_lf

CONCURRENCY = 8
RETRIES = 4
SECTION_LIMIT = 12_000
"""Characters of a linked section a question sees. A chapter-level
section with many subsections runs past this, and the tail is cut."""


API_KEY_ENV = "TYPESAFE_API_KEY"


def registry_key() -> str | None:
    """The user-scope value of `API_KEY_ENV` on Windows, else None."""
    if sys.platform != "win32":
        return None
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            value, kind = winreg.QueryValueEx(k, API_KEY_ENV)
    except OSError:
        return None
    if kind == winreg.REG_EXPAND_SZ:
        value = winreg.ExpandEnvironmentStrings(value)
    return value or None


def api_key() -> str:
    """Find the key and put it in the environment, where the SDK reads it.

    Exits naming every place it looked when none has the key.
    """
    if value := os.environ.get(API_KEY_ENV):
        return value
    if value := registry_key():
        os.environ[API_KEY_ENV] = value
        return value
    places = ["the process environment"]
    if sys.platform == "win32":
        places.append(r"the user's registry environment (HKCU\Environment)")
    sys.exit(f"No {API_KEY_ENV} found. Looked in: {', '.join(places)}.")


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

    A question's kwargs build a Choice, or a Score or a Noul when they
    carry `"type": "score"` or `"type": "noul"`. Returns, per request,
    `{question_id: answer}` in request order, where a Choice answer is
    `{"choice", "confidence", "probabilities"}`, a Score answer is
    `{"score", "confidence", "probabilities"}`, and a Noul answer is
    `{"noul"}`, the probability of yes. The SDK retries rate limits and
    overloads itself.
    """
    api_key()
    # Not in .venv; the tip tasks add it (see the docstring).
    from typesafe_sdk import (  # ty: ignore[unresolved-import]
        AsyncTypeSafeClient, Choice, Noul, Score, TypeSafeAPIConnectionError,
        TypeSafeAPITimeoutError, TypeSafeInternalServerError)

    def build(q: dict[str, Any]) -> Any:
        fields = {k: v for k, v in q.items() if k != "type"}
        kind = {"score": Score, "noul": Noul}.get(q.get("type", ""), Choice)
        return kind(**fields)

    def read(a: Any) -> dict[str, Any]:
        if a.type == "noul":
            return {"noul": round(a.noul, 3)}
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
                    # The SDK retries 429 and 529 but not a 502 from
                    # the gateway or a dropped connection, and one
                    # failure here used to abort a 10,000-question
                    # batch five minutes in, keeping none of it.
                    for attempt in range(RETRIES + 1):
                        try:
                            r = await client.system_one(
                                state=state,
                                questions={k: build(q) for k, q
                                           in questions.items()})
                            break
                        except (TypeSafeInternalServerError,
                                TypeSafeAPIConnectionError,
                                TypeSafeAPITimeoutError):
                            if attempt == RETRIES:
                                raise
                            await asyncio.sleep(2 ** attempt
                                                + random.random())
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
