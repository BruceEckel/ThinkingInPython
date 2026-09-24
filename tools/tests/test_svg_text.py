"""Tests for tools/svg_text.py: a text box follows the monospace advance
and the anchor, tspan runs join into one line, and only text that
crosses the viewBox or another text box is reported."""
from __future__ import annotations
import pytest
from tools.svg_text import clipped, collisions, text_boxes


def svg(body: str, view: str = "0 0 200 100") -> str:
    return f'<svg viewBox="{view}">{body}</svg>'


def test_a_box_is_point_six_em_per_character_from_its_anchor() -> None:
    [start, middle, end] = text_boxes(svg(
        '<text x="10" y="20" font-size="10">abcd</text>'
        '<text x="100" y="20" font-size="10" text-anchor="middle">abcd</text>'
        '<text x="190" y="20" font-size="10" text-anchor="end">abcd</text>'))
    assert (start.left, start.right) == pytest.approx((10, 34))
    assert (middle.left, middle.right) == pytest.approx((88, 112))
    assert (end.left, end.right) == pytest.approx((166, 190))
    assert (start.top, start.bottom) == pytest.approx((12.5, 22))


def test_tspan_runs_and_entities_join_into_one_line() -> None:
    [box] = text_boxes(svg('<text x="0" y="20" font-size="10">\n'
                           '  <tspan>for </tspan>\n  <tspan>e</tspan>'
                           ' &#8594;</text>'))
    assert box.text == "for e →"


def test_clipped_names_text_past_any_edge() -> None:
    body = ('<text x="190" y="50" font-size="10">wide</text>'
            '<text x="100" y="5" font-size="10">high</text>'
            '<text x="50" y="50" font-size="10">fits</text>')
    assert clipped(svg(body)) == ["wide", "high"]


def test_collisions_skip_stacked_lines_and_find_overlap() -> None:
    body = ('<text x="10" y="20" font-size="11.5">Money</text>'
            '<text x="10" y="33.5" font-size="11">/ add_money</text>'
            '<text x="30" y="36" font-size="11">overlap</text>')
    assert collisions(svg(body)) == [("/ add_money", "overlap")]
