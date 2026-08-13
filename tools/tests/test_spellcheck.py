"""Tests for tools/spellcheck.py's prose extraction.

Whether a word is in the dictionary is pyspellchecker's business. What
these cover is which text reaches it, since the misses that wasted the
most time were not words at all: a heading's `{#anchor}` slug, and the
unindented continuation lines of a multi-line HTML comment.
"""

from pathlib import Path

from spellcheck import collect, prose_text, tokens


def words(line: str) -> list[str]:
    text = prose_text(line)
    return tokens(text) if text is not None else []


# ── headings ──────────────────────────────────────────────────────────────────

def test_explicit_anchor_is_not_prose() -> None:
    line = ("## Measuring One Function with `sys.monitoring` "
            "{#measuring-one-function-with-sys-monitoring}")
    assert "sys" not in words(line)

def test_anchor_slug_splitting_a_contraction_is_not_prose() -> None:
    assert "dont" not in words("### Don't Start It {#dont-start-it}")

def test_heading_text_is_still_checked() -> None:
    assert "measuring" in words("## Measuring One Function {#anchor}")


# ── HTML comments ─────────────────────────────────────────────────────────────

def write(tmp_path: Path, body: str) -> Path:
    md = tmp_path / "chapter.md"
    md.write_text(body, encoding="utf-8")
    return md

def test_multiline_comment_continuation_is_skipped(tmp_path: Path) -> None:
    md = write(tmp_path,
               "Real prose here.\n"
               "\n"
               "<!-- TODO(deps): once it lands, extend\n"
               "rust/fastcount/demo.py (and this listing)\n"
               "to time it too. -->\n"
               "\n"
               "Closing prose.\n")
    found = [word for _, word in collect(md)]
    assert "fastcount" not in found
    assert "prose" in found

def test_one_line_comment_does_not_swallow_what_follows(tmp_path: Path) -> None:
    md = write(tmp_path, "<!-- vale House.EmDash = NO -->\nOrdinary prose.\n")
    assert "ordinary" in [word for _, word in collect(md)]

def test_fenced_code_is_still_skipped(tmp_path: Path) -> None:
    md = write(tmp_path, "Prose.\n\n```python\nzzzq = 1\n```\n")
    assert "zzzq" not in [word for _, word in collect(md)]
