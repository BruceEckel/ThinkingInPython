"""Tests for tools/arrowheads.py: the check knows the four standard heads
in any color and rejects anything else, a head matches its line's
color, a tip stops short of its target, and shortening an edge takes off the length asked for while
keeping the head on the edge's line."""
from __future__ import annotations
import math
import pytest
from tools.arrowheads import (HEADS, MIN_GAP, MIN_LINE, marker_def,
                              marker_kinds, mismatched_heads, reverse_path,
                              short_edges, shorten_curve, shorten_line,
                              shorten_path_end, shorten_path_start,
                              tight_tips)


def test_every_standard_head_is_recognized_in_any_color() -> None:
    svg = "".join(marker_def(f"m-{k}", k, c)
                  for k, c in zip(HEADS, ["#1a1612", "#7a6e62",
                                          "#8b1a1a", "#1a1612"]))
    assert marker_kinds(svg) == {f"m-{k}": k for k in HEADS}


def test_a_hand_written_head_is_recognized_whatever_its_layout() -> None:
    one_line = " ".join(marker_def("x", "hollow", "#1a1612").split())
    assert marker_kinds(one_line) == {"x": "hollow"}


def test_the_old_paper_filled_triangle_is_nonstandard() -> None:
    old = ('<marker id="t" viewBox="0 0 10 10" refX="9" refY="5" '
           'markerWidth="11" markerHeight="11" orient="auto">'
           '<path d="M0,0 L10,5 L0,10 Z" fill="#f5f0e8" stroke="#1a1612" '
           'stroke-width="1"/></marker>')
    assert marker_kinds(old) == {"t": None}


def test_shorten_line_moves_the_end_back_along_the_line() -> None:
    assert shorten_line((0, 0), (30, 40), 10) == pytest.approx((24, 32))
    with pytest.raises(ValueError):
        shorten_line((0, 0), (3, 4), 10)


def test_shorten_curve_cuts_the_arc_length_from_the_end() -> None:
    pts = [(0.0, 0.0), (50.0, 80.0), (100.0, 0.0)]
    short = shorten_curve(pts, 12.4)
    assert short[0] == pts[0]
    # The new end lies on the old curve, about 12.4 back along it.
    assert 12 < math.dist(short[-1], pts[-1]) <= 12.4


def test_path_start_and_end_trim_the_right_segment() -> None:
    assert shorten_path_end("M0,0 L0,50 L40,50", 10) == "M0,0 L0,50 L30,50"
    assert shorten_path_start("M0,0 L0,50 L40,50", 10) == "M0,10 L0,50 L40,50"
    assert reverse_path("M1,2 L3,4 Q5,6 7,8") == "M7,8 Q5,6 3,4 L1,2"


def test_a_head_must_match_the_color_of_its_line() -> None:
    svg = (marker_def("ink", "filled", "#1a1612")
           + marker_def("gray", "filled", "#7a6e62")
           + '<line x1="0" y1="0" x2="9" y2="0" stroke="#7a6e62" '
             'marker-end="url(#gray)"/>'
           + '<path d="M0,0 L9,9" stroke="#7a6e62" '
             'marker-end="url(#ink)"/>')
    assert mismatched_heads(svg) == ["ink"]


def test_an_edge_must_show_a_line_behind_its_head() -> None:
    svg = (marker_def("m", "filled", "#1a1612")
           + f'<line x1="0" y1="0" x2="0" y2="{MIN_LINE - 1}" '
             'stroke="#1a1612" marker-end="url(#m)"/>'
           + '<line x1="0" y1="0" x2="0" y2="30" stroke="#1a1612" '
             'marker-end="url(#m)"/>'
           + '<line x1="0" y1="0" x2="0" y2="2" stroke="#c8bfb0"/>')
    assert short_edges(svg) == ["0,0 -> 0,7"]


def test_a_tip_on_the_border_is_tight_and_one_four_off_is_not() -> None:
    box = '<rect x="100" y="0" width="50" height="40"/>'
    reach = HEADS["filled"].trim  # the filled head reaches as far as it trims
    touching = (f'<line x1="0" y1="20" x2="{100 - reach}" y2="20" '
                'marker-end="url(#m)"/>')
    clear = (f'<line x1="0" y1="30" x2="{96 - reach}" y2="30" '
             'marker-end="url(#m)"/>')
    svg = marker_def("m", "filled", "#1a1612") + box + touching + clear
    assert tight_tips(svg) == ["tip 100.0,20.0: gap 0.0"]


def test_tight_tips_reads_circles_and_polylines() -> None:
    svg = (marker_def("m", "filled", "#1a1612")
           + '<circle cx="100" cy="0" r="20"/>'
           + '<polyline points="0,50 60,50 60,0 67.6,0" '
             'marker-end="url(#m)"/>')
    assert tight_tips(svg) == ["tip 80.0,0.0: gap 0.0"]


def test_a_start_diamond_may_sit_on_its_owner() -> None:
    svg = (marker_def("d", "diamond", "#1a1612")
           + '<rect x="0" y="0" width="40" height="40"/>'
           + '<line x1="40" y1="20" x2="120" y2="20" '
             'marker-start="url(#d)"/>')
    assert tight_tips(svg) == []


def test_a_background_rect_is_not_a_target() -> None:
    svg = ('<svg viewBox="0 0 200 100">'
           + marker_def("m", "filled", "#1a1612")
           + '<rect x="0" y="0" width="200" height="100"/>'
           + '<line x1="10" y1="50" x2="60" y2="50" marker-end="url(#m)"/>'
           + "</svg>")
    assert MIN_GAP > 0 and tight_tips(svg) == []
