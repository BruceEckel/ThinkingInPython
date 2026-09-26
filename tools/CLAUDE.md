# Working in tools/

Loaded when working under `tools/`. Moved from the root `CLAUDE.md`'s Traps.

- **`tools/*.py` is not linted by any gate.** Only `build/examples` is checked by
  `make lint`/`make ci`, so a `tools/` script can exceed the 70-char limit with
  nothing catching it (several already do). `ty` still matters there; run it
  directly, e.g. `uv run ty check tools/whatever.py`.
- **Kindle listings: only the real book is a valid test bed, and
  line-leading whitespace is half width there.** Send to Kindle (email)
  converts a tiny standalone probe EPUB differently from the full book
  (probes rendered `pre` in Bookerly whatever the CSS said; the book
  renders it monospace), so four probes gave answers the book then
  contradicted. Test a listing change by building the book with a probe
  chapter in front (a scratch script that monkeypatches
  `build_epub.book_markdown`/`epub_css`, then `build()`), never a
  separate small EPUB. Measured in the book on a Paperwhite: spaces or
  `&#160;` at the start of a line draw at ~0.54 of a character; the same
  whitespace after any glyph, even U+200B, draws full width; `ch` is
  unsupported (zero); `6em` came out ~8.4 characters, not 10; a named
  family before `monospace` (`"Courier New", Courier, monospace`) loses
  the monospace entirely. Hence `listing_html()` prefixes each indented
  line with `&#8203;` and keeps plain spaces, and `CODE_FONT` is the
  bare keyword. Project memory `kindle-listing-indentation` has the
  probe script layout.
