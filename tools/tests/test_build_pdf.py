"""Tests for tools/build_pdf.py (the typst preamble).

The build itself shells out to pandoc and typst, so what is testable
here is the preamble the builder writes: a malformed footer fails the
whole book build with a typst error, and a stamp that leaks into an
unstamped build mislabels a casual PDF as a numbered release.
"""
from build_pdf import header_typst


def test_release_stamp_lands_in_the_footer() -> None:
    assert "Release 1.0" in header_typst("1.0")

def test_unstamped_build_has_no_release_text() -> None:
    assert "Release" not in header_typst(None)

def test_placeholder_never_survives() -> None:
    assert "<<stamp>>" not in header_typst("1.0")
    assert "<<stamp>>" not in header_typst(None)

def test_preamble_keeps_page_breaks_and_footer() -> None:
    # Both halves matter: without the show rule chapters run on, and
    # without the footer rule the book falls back to a bare number.
    for release in ("1.0", None):
        text = header_typst(release)
        assert "pagebreak(weak: true)" in text
        assert "#set page(footer: context {" in text
