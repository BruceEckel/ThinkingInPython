"""`--accept` writes each baselined check's own header.

Each of the five baselined parse checks passes its `BASELINE` and
`HEADER` to `parse_check.run()`. A check that wires in the wrong
header, or none, writes a baseline that fails to say what it holds.

The run is given no paths, so it reads the whole book by default.
The test patches `parse_check.prose_paths`, which `run()` calls, to
return one tmp fixture file, and patches the module's `find` to yield
the findings under test, so the real rules and spaCy stay out of it.
The stub parser handed to `main()` is never called. The module's
`BASELINE` is patched to a tmp file, which `run()` receives through
the module global at call time.
"""

import importlib
from collections.abc import Iterator
from pathlib import Path
import pytest
from tools import parse_check
from tools.markdown import Document
from tools.parse_check import PROSE_CHECKS, key
from tools.parsed_prose import RawSentence
from tools.report import Finding
from tools.stranded_prepositions import display

MESSAGE = "[HIT] one: A sentence."


def no_parser(texts: list[str]) -> list[list[RawSentence]]:
    raise AssertionError("the parser must not run")


@pytest.mark.parametrize("name", PROSE_CHECKS)
def test_accept_writes_the_checks_header(
    name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = importlib.import_module(name)
    fixture = tmp_path / "a.md"
    fixture.write_text("Some prose.\n", encoding="utf-8")
    base = tmp_path / "base.txt"
    hits: list[tuple[int, str]] = []

    def fake_find(docs: list[Document], *rest: object) -> Iterator[Finding]:
        for line, text in hits:
            yield Finding(docs[0].path, line, text)

    monkeypatch.setattr(module, "BASELINE", base)
    monkeypatch.setattr(module, "find", fake_find)
    monkeypatch.setattr(parse_check, "prose_paths", lambda args: [fixture])

    assert module.main(["--accept"], no_parser) == 0
    assert base.read_text(encoding="utf-8") == module.HEADER
    assert b"\r" not in base.read_bytes()

    hits.append((1, MESSAGE))
    assert module.main(["--accept"], no_parser) == 0
    text = base.read_text(encoding="utf-8")
    assert text.startswith(module.HEADER)
    assert text.removeprefix(module.HEADER) == (
        key(display(fixture), MESSAGE) + "\n")
