"""Tests for tools/coupling_panels.py: the specs are self-consistent,
their straight edges are straight, no box covers a note, and the
chapters reference the panels the specs produce."""
from __future__ import annotations
import re
from tools.coupling_panels import (CAPTIONS, GALLERY, GALLERY_H, GALLERY_W,
                                   PANELS, ROOT, Edge, Node, render_all)

CHAPTERS = ROOT / "Chapters"


def test_every_edge_names_two_nodes_of_its_panel() -> None:
    for ch, panel in PANELS.items():
        names = {n.name for n in panel.nodes}
        for e in panel.edges:
            assert e.a in names, (ch, e.a)
            assert e.b in names, (ch, e.b)


def test_every_panel_has_a_caption_and_every_caption_a_panel() -> None:
    assert set(CAPTIONS) == set(PANELS)


def test_each_pattern_chapter_references_its_panel_once() -> None:
    for ch in PANELS:
        md = next(CHAPTERS.glob(f"{ch}_*.md"))
        text = md.read_text(encoding="utf-8")
        tags = re.findall(rf"^!\[(.*)\]\(_images/coupling_{ch}\)$", text,
                          flags=re.M)
        assert len(tags) == 1, (md.name, len(tags))
        assert tags[0] == CAPTIONS[ch], md.name


def test_rendered_svg_has_a_title_and_no_size() -> None:
    for path, body in render_all().items():
        assert body.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox=')
        assert ' width="' not in body.split("\n")[0], path.name
        assert "<title>" in body, path.name


# Every drawing in the file, as (name, nodes, edges, note baseline x and
# y, note text), with the note placed where Panel.svg() and
# render_gallery() put it.
DRAWINGS = (
    [(f"chapter {ch}", p.nodes, p.edges, 10, p.height - 12, p.note)
     for ch, p in PANELS.items()]
    + [(f"gallery {c.title}", c.nodes, c.edges,
        18 + GALLERY_W * c.col, GALLERY_H * c.row + 256, c.note)
       for c in GALLERY])

# Edges left a little off straight on purpose, with the reason.
KNOWN_TILTS: dict[tuple[str, str, str], str] = {}
NEAR_MISS = 15  # centers closer than this on one axis should be equal
NOTE_SIZE = 10.5  # the notes' font size; a character is 0.6 of it wide


def tilt(e: Edge, a: Node, b: Node) -> float:
    """How far an unbent, unshifted edge's ends miss a common center line,
    or 0 when they meet it or the edge is meant to run diagonally."""
    if e.bend or e.shift:
        return 0
    return next((d for d in (b.cx - a.cx, b.cy - a.cy)
                 if 0 < abs(d) < NEAR_MISS), 0)


def test_a_straight_edge_is_straight() -> None:
    bad = []
    for name, nodes, edges, *_ in DRAWINGS:
        by_name = {n.name: n for n in nodes}
        for e in edges:
            d = tilt(e, by_name[e.a], by_name[e.b])
            if d and (name, e.a, e.b) not in KNOWN_TILTS:
                bad.append(f"{name}: {e.a} -> {e.b} off by {d:g}")
    assert bad == []


def test_every_known_tilt_still_exists() -> None:
    for name, a, b in KNOWN_TILTS:
        nodes, edges = next((ns, es) for n, ns, es, *_ in DRAWINGS
                            if n == name)
        by_name = {n.name: n for n in nodes}
        e = next(e for e in edges if (e.a, e.b) == (a, b))
        assert tilt(e, by_name[a], by_name[b]), (name, a, b)


def test_no_box_covers_its_note() -> None:
    bad = []
    for name, nodes, _, x, baseline, note in DRAWINGS:
        top, right = baseline - NOTE_SIZE, x + len(note) * 0.6 * NOTE_SIZE
        for n in nodes:
            if n.y + n.h > top and n.x < right and n.x + n.w > x:
                bad.append(f"{name}: {n.name} reaches {n.y + n.h:g}, "
                           f"the note starts at {top:g}")
    assert bad == []
