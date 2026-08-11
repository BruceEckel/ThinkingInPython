[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/21_The_Pattern_Concept.md` in
the clean-slate sweep. The mechanical layer is sound: the chapter's one
listing (`strategy_is_a_function.py`) extracts, type-checks, lints, and
prints its `#: 3 6` marker deterministically. The Norvig footnote was
verified against the slide deck at norvig.com: the title is "Design
Patterns in Dynamic Programming" (Object World, May 5, 1996), slide 10
says "16 of 23 patterns are either invisible or simpler" in Dylan or
Lisp, and the seven left over (Adapter, Bridge, Composite, Decorator,
Memento, Prototype, Singleton) do include Singleton, as the footnote
claims. Python 2.2's iterator protocol (PEP 234), the Saint-Exupery
attribution to *Wind, Sand and Stars*, and the Factory chapter's
"builds both" claim (the hand-filled dictionary and the
`__init_subclass__()` registry are both in chapter 27) all check out.
One factual error surfaced, in the Pattern Taxonomy section: the
Structural item listed the Composite and Interpreter chapter whole, but
GoF files *Interpreter* under Behavioral, the chapter's own Behavioral
definition opens with "interpreting a language", and chapter 34 says
"Interpreter is the behavior". Applied below. No live blocks this run:
every finding had one defensible answer.

## Applied directly

- Pattern Taxonomy, Structural: the chapter-34 link now contributes
  only "the *Composite* half of", and *Interpreter* moved to the
  Behavioral item, mirrored on the existing *State*-beside-*Proxy*
  caveat ("*State* appears beside *Proxy* and *Interpreter* beside
  *Composite*, for reasons given below").
- Pattern Taxonomy, Behavioral: "multiple examples including" three
  patterns is now the full roster (Iterator, Template Method,
  Function Objects' *Command*, *Strategy*, and *Chain of
  Responsibility*, Observer, Visitor, Memento, *State*, and
  *Interpreter*),
  opened with "Most of the patterns in this book are behavioral". The
  Structural item's list claims to be exhaustive ("cover the
  structural patterns in this book"), so a three-example sample next
  to it read as the whole story and hid the biggest group. The
  alternative was keeping the "including" hedge and adding nothing.
- Pattern Taxonomy, Creational: "covers factory methods and factory
  classes" is now "covers the other four: *Factory Method*, *Abstract
  Factory*, *Prototype*, and *Builder*", which chapter 27's sections
  confirm; with Singleton that makes all five GoF creational patterns,
  and the old wording undersold two of them.
- Same item: the dangling modifier "By isolating the details of object
  creation, your code isn't dependent..." (the code does not do the
  isolating) is now a gerund subject: "Isolating the details of object
  creation means your code doesn't depend...".
- Design Principles, *Consistency*: added the linking first sentence
  "Every inconsistency in a design is one more arbitrary rule to
  remember." The old text jumped straight to random rules and their
  cost without connecting them to the principle's name.
- Pattern Evolution: "The ladder runs downward too" is now "The
  progression runs downward too"; the stages were introduced as a
  progression and "ladder" appeared nowhere else (same fix the
  chapter-18 review made for its own unintroduced "ladder").
- Pattern Evolution, stage 4: "This usually only appears after
  applying" is now "usually appears only after applying" (the "only"
  qualifies "after", not "appears").
- Intro: "the chapters after it supply the rest of the code" is now
  "the chapters that follow supply the rest of the code" ("it" could
  bind to the chapter or the listing).
- Ran `make reflow CH=21` over the edited prose.

## Considered and declined

- "the 1994 book *Design Patterns*": the book carries a 1995
  copyright (Norvig's sources slide cites 1995), but it was published
  in October 1994 and "the 1994 book" is the standard citation. Left
  as written.
- "Coupling happens" keeps its watch-list verb: it is the pithy point
  of the *Managed Coupling* bullet, that coupling is inevitable and
  the job is managing it.
- "a Python module already is one" (Norvig footnote) keeps "already":
  it carries the no-work-needed meaning the footnote exists to make.
- "A method should talk only to itself" (Law of Demeter) keeps
  "itself": reflexive and essential.
- Chapters 31 (State Machines) and 32 (Multiple Dispatching) stay out
  of the taxonomy roster: neither is one of GoF's 23 (state machines
  apply *State*; multiple dispatch is not a GoF pattern), and the
  roster enumerates the book's GoF coverage.
- The Design Principles list's unevenness (some bullets explained,
  some bare one-liners) reads as deliberate compression of a familiar
  authorial list; expanding the bare ones would double the section
  for no new claim.
