When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/39_Pattern_Catalog.md` in the
clean-slate sweep. The chapter has no code listings, so the editing pass
was a claims audit: every linked row was checked against the current,
post-sweep text of its target chapter, and every unlinked intent line
against the literature it cites. All anchors resolve
(`tools/heading_links.py` reports "Anchor links OK"), including the ç in
`#façade`. The chapters corrected earlier in this sweep still agree with
the catalog: chapter 21's taxonomy now files Interpreter under
Behavioral and the catalog's Behavioral placement matches; chapter 27's
corrected GoF Factory Method sentence ("subclass different types of
factories from the basic factory") remains compatible with the row's
GoF intent and its `#polymorphic-factories` anchor; chapter 34's
"Composite is the data, Interpreter is the behavior" framing is intact
and consistent with the split placement of those two rows. The unlinked
rows check out against their sources: the Architectural table is the
complete POSA1 set of eight, every Fowler row is in PoEAA, every
Hohpe-and-Woolf row is in EIP, and rows are alphabetical in every
table. The one inbound link (21:288, "a name-and-intent index of the
wider literature, with a link to this book's coverage wherever there is
one") describes what the chapter delivers. Per the standing rejection
in `deep_review_db.md`, no conclusion or exercises were proposed. No
finding needed a decision, so this file has no live blocks.

## Applied directly

- Intro: "the *Creational*/*Structural*/*Behavioral* split questioned
  there" now reads "that chapter calls *Creational* straightforward and
  questions the other two", matching what 21's taxonomy section says
  (it exempts Creational and questions only the other two labels).
- State Machine moved out of "Behavioral (GoF)" into "Other Patterns
  and Idioms": GoF has no State Machine pattern, and the intro's own
  rule is "each name sits where its source puts it". With it gone the
  three GoF tables hold the complete 23-pattern GoF set. (The
  alternative, keeping it beside State for proximity, lost to the
  chapter's stated rule.)
- State Machine intent is now "Drive an object through a fixed set of
  states in response to inputs": chapter 31 presents the per-state
  design and the table design as equals (31:835-855 declines to pick),
  so "from a transition table" named only half its coverage.
- State Machine added to the problem-index row "Choosing behavior at
  runtime", so the move out of the GoF table does not cost it
  findability.
- MVC retargeted from `30_Observer.md#a-visual-example-of-observers` to
  the chapter: that section is a two-way model-view split that never
  mentions MVC or a controller (input handling sits inside the view,
  30:515-517); MVC is named in the chapter opening (30:16-17).
- Multiton intent is now "Manage a pool of singletons, one per key":
  the linked section's pool keys on constructor-argument tuples and
  grows without bound (35:220), so "a fixed set of named singletons"
  contradicted it twice, and "fixed set" collided with the chapter's
  own "A Fixed Set: Enum" heading, which names a different construct.
- RAII intent is now "Acquire a resource in a constructor and release
  it in the destructor": the old "Tie a resource's lifetime to an
  object's scope" conflated object lifetime with lexical scope, and
  the new form states the C++ idiom the name abbreviates. The link to
  chapter 15 stands: context managers are Python's replacement for the
  concern, which is the same relationship other rows have to their
  coverage.
- "Patterns Python Absorbed": Prototype moved up beside Factory Method,
  restoring the chapter order the closing line ("each chapter above
  works one case") implies; it had dangled last, after chapters 33 and
  35, while linking to 27.
- Closing paragraph: "Python already supplies the piece their inventors
  set out to supply" is now "Python includes the piece their inventors
  set out to supply", dropping the supplies/supply repeat and the
  filler "already".

## Considered and declined

- **DTO keeps Fowler's intent** ("Carry data between processes in one
  batched object") though chapter 22 frames the DTO as an in-process
  package for return values. The row sits in the Fowler table, where
  every intent is Fowler's; the link marks the book's treatment, which
  may differ in emphasis. Rewriting the intent to the book's framing
  would make this the one row in the table not describing its source.
- **State keeps GoF's wording** ("when its internal state changes")
  though chapter 26 teaches an externally driven swap
  (`s.change_to(StateB())`). The intro says the intent lines exist so
  you can look a pattern up in the literature, so they follow the
  source, not the book's variation.
- **Thread-Specific Storage stays linked** to
  `#context-that-follows-the-call-chain`, a section that teaches
  `ContextVar` and argues against `threading.local` by name
  (19:768-771). Same shape as Double-Checked Locking, whose linked
  section recommends against it: the catalog's preamble ("Listing a
  pattern here is not a recommendation") covers coverage that
  supersedes the pattern.
- **Special Case shares `#null-object`** with Null Object though
  chapter 20 never uses Fowler's name. Fowler files Null Object as an
  instance of Special Case, and that section is the book's nearest
  coverage of the mechanism ("`NullLogger` defines silence once,
  instead of every call site defining it").
- **Registry keeps Fowler's intent** ("A well-known object others use
  to find services or data") though 27's registry holds classes for
  creation. A class registry is an instance of the well-known-object
  idea, and no better anchor exists in the book.
- **Thread Pool keeps `#one-task-many-backends`** though that section
  stresses backend interchangeability over worker reuse. It is where
  `ThreadPoolExecutor` is actually used; the chapter's other mentions
  (19:1018, 19:1377) are single-sentence asides in sections about
  other things.
- **Dependency Injection keeps `#isolating-tests-from-the-world`**
  rather than moving to `#making-code-testable`. The linked section
  holds the injected-clock listings, where a reader watches injection
  happen; the alternative section states the principle in one sentence
  but demonstrates nothing new.
- **Fluent Interface (27's Builder section) and RAII (chapter 15) land
  on coverage that never uses those names.** Adding the terms to those
  chapters was declined as outside a catalog row's scope: the catalog
  maps names to the book's treatment of the concern, and the treatment
  standing under another name is normal here (the intro's "look it up
  in the literature" carries the naming).
- **The Prototype absorbed row keeps `dataclasses.replace()`** though
  that half of the claim is supported in `#builder` (27:742-746,
  "`replace()` is Prototype and Builder rolled into one function")
  rather than in the linked `#prototype` section. The claim is true
  and the row links the pattern's section, not the sentence.
- **Chapter-level links stay chapter-level** (Blackboard, Monad, and
  others) though deeper anchors exist (`#the-rat-and-the-blackboard`,
  `#composing-with-bind`): the catalog links whole chapters when the
  chapter is the coverage, and mixing depths per row would trade
  consistency for little.
- **No conclusion or exercises**: standing rejection in
  `deep_review_db.md`; the chapter deliberately ends on its closing
  table's argument.
