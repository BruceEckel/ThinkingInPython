"""Tests for tools/verify_targets.py's failure excerpt.

A failed target's summary shows the log's tail, which for Vale is a
screen of warnings and a count. The excerpt also shows the error lines
above the tail, so the cause appears without opening the log.
"""
from tools.verify_targets import excerpt

VALE = """
 Chapters/31_Patterns--State.md
 12:3  warning  'is left' may be passive voice.  write-good.Passive

 Chapters/32_Patterns--Multiple_Dispatching.md
 170:36  warning  'are fixed' may be passive.  write-good.Passive
 404:65  error    'for free' is a cliche.  proselint.Cliches
""" + "\n".join(f" {n}:1  warning  filler" for n in range(30))


def test_error_above_the_tail_is_shown_with_its_file() -> None:
    out = excerpt(VALE, lines=5)
    assert "404:65  error" in out
    assert " Chapters/32_Patterns--Multiple_Dispatching.md" in out
    assert "31_Patterns--State.md" not in out
    assert out.index("error") < out.index("Last lines:")

def test_no_error_lines_gives_the_tail_alone() -> None:
    text = "\n".join(f"line {n}" for n in range(40))
    assert excerpt(text, lines=3) == "line 37\nline 38\nline 39"

def test_error_inside_the_tail_is_not_repeated() -> None:
    text = "\n".join(["a", "b", "x.py:3: error[bad]", "c"])
    assert excerpt(text, lines=3) == "b\nx.py:3: error[bad]\nc"

def test_error_lines_are_capped() -> None:
    text = "\n".join(["E: FAILED"] * 20 + ["end"])
    out = excerpt(text, lines=1, max_errors=4)
    assert out.count("FAILED") == 4
    assert "16 more error line(s)" in out
