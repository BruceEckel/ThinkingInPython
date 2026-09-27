"""Ask whether each linked section covers what its sentence credits it with.

`heading_links.py` proves an anchored link resolves, and
`check_claims.py` narrows the links whose text might claim something the
target does not say, for a human to read. This tool does the reading.
For every anchored link from one chapter to another, it hands TypeSafe
the sentence and the linked section and asks a Choice question with
three answers: `supports`, `contradicts`, `says_nothing`. It reports
the links that did not come back `supports`.

It reports and never gates. A `says_nothing` is often a link doing its
job loosely: an exercise that links "descriptor" to the nearest
descriptor example says nothing about the exercise's own classes. The
first run's real finding was chapter 42 linking "put the meaning in the
type" to Static Types' annotation-syntax section, when chapter 12 is
where the book argues it.

Answers are stored in `tools/data/link_support_verdicts.json`, keyed by
the sentence, the target, and the section's text, so an edit to either
end re-asks that link and nothing else. A section is cut at
`judgments.SECTION_LIMIT` characters; a link to a long chapter-level
section is judged on its opening.

    tip link-support                       # ask about new links, report
    tip link-support ARGS=--report         # report from the store only
    tip link-support ARGS="--report --all" # include low-confidence ones
"""

import argparse
import datetime
import sys
from dataclasses import dataclass
from typing import Any

from tools import judgments
from tools.check_self_reference import LINK, corpus, sentences
from tools.config import CHAPTERS_DIR, DATA_DIR
from tools.markdown import Document
from tools.repo import md_files

VERDICTS_FILE = DATA_DIR / "link_support_verdicts.json"
CONFIDENT = 0.5
"""Below this confidence a non-`supports` answer is left out of the
default report: the model spread its probability across answers."""

QUESTION = {
    "instructions": (
        "`sentence` links to another chapter of the same book, and "
        "`section` is the part of that chapter the link points at. Does "
        "`section` cover what `sentence` credits the linked chapter "
        "with? Judge only what the sentence says about the linked "
        "chapter; ignore what it says about its own chapter's code."),
    "criteria": {
        "supports": ("The section discusses or demonstrates what the "
                     "sentence credits it with."),
        "contradicts": ("The section states the opposite of what the "
                        "sentence credits it with."),
        "says_nothing": ("The section does not address what the "
                         "sentence credits it with."),
    },
}


@dataclass(frozen=True)
class Link:
    file: str
    line: int
    previous: str
    sentence: str
    label: str
    target: str
    anchor: str
    section: str

    @property
    def key(self) -> str:
        return judgments.key(self.target, self.anchor, self.sentence,
                             self.section)


def links() -> list[Link]:
    """Every anchored link into another chapter, once per sentence."""
    book = corpus()
    out: dict[str, Link] = {}
    for path in md_files([CHAPTERS_DIR]):
        previous = ""
        for line, text in sentences(Document.parse(path)):
            for m in LINK.finditer(text):
                target, anchor = m.group(2), m.group(3)
                chapter = book.get(target)
                if not anchor or target == path.name or chapter is None:
                    continue
                section = chapter.sections.get(anchor)
                if section is None:  # heading_links.py reports it
                    continue
                link = Link(path.name, line, previous, text, m.group(1),
                            target, anchor,
                            section[:judgments.SECTION_LIMIT])
                out.setdefault(link.key, link)
            previous = text
    return list(out.values())


def state(link: Link) -> dict[str, Any]:
    book = corpus()
    return {
        "current_chapter_title": judgments.title(book[link.file].text),
        "previous_sentence": link.previous,
        "sentence": link.sentence,
        "link": {"label": link.label,
                 "target_title": judgments.title(book[link.target].text)},
        "section": link.section,
    }


def progress(done: int, total: int) -> None:
    print(f"\r  {done}/{total}", end="", file=sys.stderr, flush=True)
    if done == total:
        print(file=sys.stderr)


def report(store: dict[str, dict[str, Any]], every: bool) -> None:
    shown = hidden = 0
    for v in store.values():
        if v["verdict"] == "supports":
            continue
        if v["confidence"] < CONFIDENT and not every:
            hidden += 1
            continue
        shown += 1
        print(f"{CHAPTERS_DIR.name}/{v['file']}:{v['line']}: "
              f"{v['verdict']} ({v['confidence']:.2f}) "
              f"-> {v['target']}#{v['anchor']}")
        print(f"    {v['sentence']}")
    total = len(store)
    print(f"\n{shown} of {total} links reported"
          + (f", {hidden} low-confidence hidden (--all shows them)"
             if hidden else ""))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", action="store_true",
                    help="report from the stored verdicts; ask nothing")
    ap.add_argument("--all", action="store_true",
                    help="include low-confidence answers in the report")
    args = ap.parse_args(argv)

    store = judgments.load(VERDICTS_FILE)
    if not args.report:
        current = links()
        live = {link.key for link in current}
        stale = [k for k in store if k not in live]
        new = [link for link in current if link.key not in store]
        for k in stale:
            del store[k]
        if new:
            answers = judgments.ask(
                [(state(link), {"support": QUESTION}) for link in new],
                progress)
            today = datetime.date.today().isoformat()
            for link, a in zip(new, answers):
                store[link.key] = {
                    "file": link.file, "line": link.line,
                    "target": link.target, "anchor": link.anchor,
                    "sentence": link.sentence,
                    "verdict": a["support"]["choice"],
                    "confidence": a["support"]["confidence"],
                    "asked": today,
                }
        for link in current:
            store[link.key]["line"] = link.line
        judgments.save(VERDICTS_FILE, store)
        print(f"{len(new)} asked, {len(stale)} pruned\n")
    report(store, args.all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
