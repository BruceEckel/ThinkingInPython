"""Tests for tools/coupling_panels.py: the specs are self-consistent,
their straight edges are straight, every gallery box sits inside its
cell, and the chapters reference the panels the specs produce."""
from __future__ import annotations
import re
from tools.coupling_panels import (GALLERY, GALLERY_H, GALLERY_W,
                                   PANELS, ROOT, Edge, Node, all_edge_problems,
                                   edge_problems, render_all)

CHAPTERS = ROOT / "Chapters"


def test_every_edge_names_two_nodes_of_its_panel() -> None:
    for ch, panel in PANELS.items():
        names = {n.name for n in panel.nodes}
        for e in panel.edges:
            assert e.a in names, (ch, e.a)
            assert e.b in names, (ch, e.b)


def test_each_pattern_chapter_references_its_panel_once() -> None:
    for ch in PANELS:
        md = next(CHAPTERS.glob(f"{ch}_*.md"))
        text = md.read_text(encoding="utf-8")
        tags = re.findall(rf"^!\[(.*)\]\(_images/coupling_{ch}\)$", text,
                          flags=re.M)
        assert len(tags) == 1, (md.name, len(tags))
        # A panel prints no caption; its SVG <title> is the alt text.
        assert tags[0] == "", md.name


def test_rendered_svg_has_a_title_and_no_size() -> None:
    for path, body in render_all().items():
        assert body.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox=')
        assert ' width="' not in body.split("\n")[0], path.name
        assert "<title>" in body, path.name


# Every drawing in the file, as (name, nodes, edges).
DRAWINGS = (
    [(f"chapter {ch}", p.nodes, p.edges) for ch, p in PANELS.items()]
    + [(f"gallery {c.title}", c.nodes, c.edges) for c in GALLERY])

# Edges left a little off straight on purpose, with the reason.
KNOWN_TILTS: dict[tuple[str, str, str], str] = {}
NEAR_MISS = 15  # centers closer than this on one axis should be equal


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


def test_every_tip_meets_its_box_and_no_edge_crosses_one() -> None:
    assert all_edge_problems() == []


def test_edge_problems_reports_a_crossing() -> None:
    nodes = (Node("a", 0, 0, w=40, h=20), Node("mid", 80, 0, w=40, h=20),
             Node("b", 160, 0, w=40, h=20))
    assert edge_problems(nodes, (Edge("a", "b", "thin"),)) == [
        "a -> b: crosses mid"]


def test_a_tip_reaches_a_rounded_box_at_any_angle() -> None:
    target = Node("t", 100, 100, w=90, h=40, kind="interface")
    for x, y in ((0, 0), (300, 20), (145, 300), (0, 240)):
        nodes = (Node("s", x, y, w=40, h=20), target)
        assert edge_problems(nodes, (Edge("s", "t", "realize"),)) == []


def test_a_legend_lists_only_what_its_panel_draws() -> None:
    labels = {"heavy": "names a concrete class",
              "thin": "names an interface",
              "realize": "satisfies it",
              "inherit": "inherits its internals"}
    for ch, panel in PANELS.items():
        svg = panel.svg("t")
        used = {e.kind for e in panel.edges}
        for kind, label in labels.items():
            assert (label in svg) == (kind in used), (ch, kind)
        marked = any(n.kind == "mark" for n in panel.nodes)
        assert (">does not change</text>" in svg) == marked, ch


def test_every_gallery_box_sits_inside_its_cell() -> None:
    for c in GALLERY:
        x0, y0 = 18 + GALLERY_W * c.col, GALLERY_H * c.row
        for n in c.nodes:
            assert x0 - 10 <= n.x and n.x + n.w <= x0 + GALLERY_W, (
                c.title, n.name)
            assert y0 + 32 < n.y and n.y + n.h <= y0 + GALLERY_H, (
                c.title, n.name)
