#!/usr/bin/env python3
"""Link a listing's name in the prose to the listing itself.

The prose names its listings in backticks: "the dictionary in
`shape_table.py`". Every such name is unique across the chapters
(check_unique_slugs.py enforces one basename per listing), so a mention
has one target, and the site and EPUB builds can turn the code span
into a link with no change to the Markdown. This module is that
rewrite, shared by build_site.py and build_epub.py:

- `listing_id()` derives a stable HTML id from a block's path comment.
- `listing_index()` maps every basename and full slug the chapters
  define to its (chapter stem, id).
- `fence_ids()` gives each slugged fence pandoc attributes carrying
  that id, for the site, where pandoc renders the block;
  `site_rewrite()` runs it after the linking, the order that works.
- `link_line()` and `link_mentions()` rewrite each `name.py` code span
  outside a fence, and outside an existing link, into a link to the
  listing, with the class `listing-link` for the stylesheet.

Only a code span holding the bare name is a mention. `from registry
import make` names the module, not the listing, and stays code.

The PDF build (build_pdf.py) passes `listing_links=False`: pandoc's
typst writer drops the ids, so a link there would name a label typst
cannot find and the compile would fail.
"""
import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping

from tools.markdown import Document

# A chapter's file stem and the id of one of its listings.
type Target = tuple[str, str]
# How a link reaches a target from the page being built.
type Href = Callable[[str, str], str]

ID_UNSAFE = re.compile(r"[^\w.-]")
# A code span holding only a listing name, with or without its path.
MENTION = re.compile(r"`([\w./-]+\.py)`")
# An inline link, kept whole so a mention inside its text stays put.
LINK_SPAN = re.compile(r"(\[[^\]]*\]\([^)]*\))")
FENCE = re.compile(r"^(\s*)```(\w*)\s*$")
LINK_CLASS = "listing-link"


def listing_id(slug: str) -> str:
    """The id a listing's block carries, from its `# path/name.py` line.

    A slash is not valid in an id, so `mouse/MouseAction.py` becomes
    `listing-mouse-MouseAction.py`. The period stays: pandoc accepts it
    in an identifier and every link regex in the build already allows
    it in an anchor.
    """
    return "listing-" + ID_UNSAFE.sub("-", slug)


def listing_index(docs: Iterable[tuple[str, Document]]
                  ) -> dict[str, Target]:
    """Every name a mention can use, mapped to its chapter and id.

    Both the full slug and its basename are keys, so `mouse/MouseAction.py`
    and `MouseAction.py` reach the same block. A name that two chapters
    both define is left out: a link to either would be a guess, and
    check_unique_slugs.py reports the collision on its own.
    """
    found: defaultdict[str, list[Target]] = defaultdict(list)
    for stem, doc in docs:
        for block in doc.blocks:
            slug = block.slug
            if slug is None:
                continue
            target = (stem, listing_id(slug))
            for key in {slug, slug.rsplit("/", 1)[-1]}:
                if target not in found[key]:
                    found[key].append(target)
    return {key: targets[0]
            for key, targets in found.items() if len(targets) == 1}


def site_href(here: str) -> Href:
    """Links for the site, where each chapter is its own page."""
    def href(stem: str, anchor: str) -> str:
        page = "" if stem == here else f"{stem}.html"
        return f"{page}#{anchor}"
    return href


def epub_href(stem: str, anchor: str) -> str:
    """Links for the EPUB, one document whose listing ids are unique."""
    return f"#{anchor}"


def link_line(line: str, index: Mapping[str, Target],
              href: Href) -> str:
    """Rewrite the listing mentions in one prose line into links."""
    def repl(m: re.Match[str]) -> str:
        target = index.get(m.group(1))
        if target is None:
            return m.group(0)
        return f"[{m.group(0)}]({href(*target)}){{.{LINK_CLASS}}}"

    parts = LINK_SPAN.split(line)
    return "".join(p if i % 2 else MENTION.sub(repl, p)
                   for i, p in enumerate(parts))


def link_mentions(text: str, index: Mapping[str, Target],
                  href: Href) -> str:
    """Rewrite every listing mention outside a fence in `text`."""
    doc = Document.from_text(text)
    fenced = doc.in_fence()
    lines = list(doc.lines)
    for i, line in enumerate(lines):
        if not fenced[i]:
            lines[i] = link_line(line, index, href)
    return "\n".join(lines)


def site_rewrite(text: str, index: Mapping[str, Target],
                 here: str) -> str:
    """Both site rewrites, links first.

    `fence_ids()` turns a fence opener into the attribute form, which
    `Document` does not read as a fence, so linking after it would see
    every prose line as code and change nothing.
    """
    text = link_mentions(text, index, site_href(here))
    return fence_ids(text)


def fence_ids(text: str) -> str:
    """Give each slugged fence in `text` pandoc attributes with its id.

    ```` ```python ```` becomes ```` ``` {#listing-name.py .python} ````,
    which pandoc renders as a `div` carrying that id around the
    highlighted block. A fence naming no file is left alone, and so is
    one already written in the attribute form.
    """
    doc = Document.from_text(text)
    lines = list(doc.lines)
    for block in doc.blocks:
        slug = block.slug
        if slug is None:
            continue
        m = FENCE.match(lines[block.open_at])
        if m is None:
            continue
        attrs = f"#{listing_id(slug)}"
        if m.group(2):
            attrs += f" .{m.group(2)}"
        lines[block.open_at] = f"{m.group(1)}``` {{{attrs}}}"
    return "\n".join(lines)
