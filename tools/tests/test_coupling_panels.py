"""Tests for tools/coupling_panels.py: the specs are self-consistent and
the chapters reference the panels the specs produce."""
from __future__ import annotations
import re
from tools.coupling_panels import CAPTIONS, PANELS, ROOT, render_all

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
