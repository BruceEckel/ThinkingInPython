"""Tests for tools/figure_gallery.py: the scan finds what the prose
references, the style reader sees what an SVG draws with, and the page
lists every figure once under its number."""
from __future__ import annotations
from pathlib import Path
from tools.figure_gallery import (Figure, Reference, read_style, render_html,
                                  scan)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 200"
     font-family="'JetBrains Mono', Consolas, monospace">
  <title>A box and an arrow</title>
  <defs><marker id="head" markerWidth="8"><path d="M0,0 L8,4 L0,8 z"
   fill="#1a1612"/></marker><marker id="spare" markerWidth="8"/></defs>
  <rect x="10" y="10" width="80" height="30" fill="none" stroke="#c8bfb0"
        stroke-width="1.3" rx="4"/>
  <line x1="90" y1="25" x2="200" y2="25" stroke="#1a1612" stroke-width="2.8"
        marker-end="url(#head)"/>
  <line x1="90" y1="60" x2="200" y2="60" stroke="#ff0000" stroke-width="1.3"
        stroke-dasharray="5,4" marker-end="url(#head)"/>
  <text x="20" y="30" font-size="12" fill="#7a6e62">label</text>
</svg>
"""


def test_read_style_collects_the_distinct_drawing_attributes() -> None:
    s = read_style(SVG)
    assert s.view_box == "0 0 700 200"
    assert s.titled and not s.sized_root
    assert s.colors == ["#1a1612", "none", "#c8bfb0", "#ff0000", "#7a6e62"]
    assert s.widths == ["1.3", "2.8"]
    assert s.dashes == ["5,4"]
    assert s.families == ["'JetBrains Mono', Consolas, monospace"]
    assert s.sizes == ["12"]
    assert s.markers == ["head", "spare"]
    assert s.marker_uses == {"head": 2}
    assert s.odd_colors == ["#ff0000"]
    assert s.flags == ["color outside the palette"]


def test_scan_pairs_references_with_files_and_reports_the_rest(
        tmp_path: Path) -> None:
    docs = tmp_path / "Chapters"
    docs.mkdir()
    (docs / "07_Part--One.md").write_text(
        "# One\n\n![first caption](_images/alpha)\n\ntext\n\n"
        "![ghost](_images/nowhere)\n", encoding="utf-8")
    (docs / "03_Part--Two.md").write_text(
        "# Two\n\n![shared](_images/alpha)\n", encoding="utf-8")
    images = tmp_path / "images"
    images.mkdir()
    (images / "alpha.svg").write_text(SVG, encoding="utf-8")
    (images / "orphan.svg").write_text(SVG, encoding="utf-8")
    (images / "notes.txt").write_text("not an image", encoding="utf-8")
    figs = scan([docs], images)
    assert [f.name for f in figs] == ["alpha", "nowhere", "orphan"]
    alpha, nowhere, orphan = figs
    assert alpha.refs[0].doc.name == "03_Part--Two.md"  # book order
    assert [r.line for r in alpha.refs] == [3, 3]
    assert alpha.style is not None
    assert nowhere.path is None and nowhere.refs[0].line == 7
    assert orphan.refs == [] and orphan.sort_key[0] == 10_000


def test_render_lists_each_figure_once_under_its_number(
        tmp_path: Path) -> None:
    svg = tmp_path / "beta.svg"
    svg.write_text(SVG, encoding="utf-8")
    figs = [
        Figure("beta", svg, [Reference(tmp_path / "Chapters" / "05_X--Y.md",
                                       9, "a `caption`")],
               read_style(SVG)),
        Figure("gamma", None, [Reference(tmp_path / "Chapters" / "06_X--Z.md",
                                         2, "missing one")]),
    ]
    page = render_html(figs, tool=None)
    assert page.count('id="beta"') == 1 and page.count('id="gamma"') == 1
    assert '<span class="num">1</span><code>beta.svg</code>' in page
    assert '<span class="num">2</span><code>gamma</code>' in page
    assert "NO FILE" in page
    assert "a `caption`" in page
    assert 'data-render="png" disabled' in page
    assert "no SVG rasterizer" in page


def test_every_figure_the_book_references_has_a_file() -> None:
    figs = scan()
    assert [f.name for f in figs if f.path is None] == []
    assert any(f.name == "observer_broadcast" for f in figs)
