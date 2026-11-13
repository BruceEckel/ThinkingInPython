"""An authored `[]{#id}` span is an anchor a link can name."""
from pathlib import Path

from tools.heading_links import anchors, find, span_anchors
from tools.markdown import Document

TEXT = (
    "## Native\n\n"
    "[]{#koka-greeting}[Koka](https://example.org) has Effects:\n\n"
    "```koka\n// koka/greet.kk\n[]{#in-fence}\n```\n\n"
    "Pandoc writes a span as `[]{#in-code}`.\n\n"
    "[]{#ix-12-3}An index target.\n\n"
    "See [the program](#koka-greeting) and [nothing](#in-fence).\n"
)


def doc() -> Document:
    return Document.from_text(TEXT, Path("Chapters/44_X.md"))


def test_span_id_is_collected_outside_fences_and_code() -> None:
    assert span_anchors(doc()) == {"koka-greeting"}


def test_anchors_holds_heading_and_span_ids() -> None:
    assert anchors(doc()) == {"native", "koka-greeting"}


def test_link_to_a_span_resolves_and_a_fenced_one_does_not() -> None:
    messages = [f.message for f in find(doc())]
    assert len(messages) == 1
    assert "#in-fence" in messages[0]
