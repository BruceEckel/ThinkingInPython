When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Full four-pass review of `Chapters/07_Classes.md` (correctness, teaching,
house style, prose), with `deep_review_db.md` and the prior completed review
(`git show 4e6a9698:deep_review/~07_Classes.md`) read first as carry-forward.
The chapter is in good shape: the prior review's applied changes
(`forgot_self.py`, the `Typo` class, the staleness demo, the `__dict__`
caveat, exercise 6) all hold up, and every listing's gates pass. What this
round found were seams left by that review's own edits (a cross-reference the
accepted section move silently falsified, a duplicated paragraph around the
inserted `forgot_self.py`, a combined print that contradicts the "unchanged
calling code" prose) plus two small teaching gaps. Everything had one
defensible answer, so it is all applied; nothing needs a decision.

## Applied directly

- Inheritance: "the section after this one explains it" retargeted to a named
  same-file link, [Marking Overrides with `@override`]. The prior review's
  accepted move of the Compose section (commit 4e6a9698) put a section between
  the two and made the phrase false; the named link fails loudly next time.
- Inheritance, after the demo: added that Python never calls a base-class
  constructor automatically (unlike C++ and Java), what removing
  `super().__init__(text)` breaks (`self.s` never created, `AttributeError`
  on first read), and that a derived class with no constructor of its own
  inherits and runs the base version. The chapter's C++/Java framing invites
  exactly the auto-chaining assumption.
- After `forgot_self.py`: merged the two paragraphs that each said Python
  "passes the object reference automatically" (a seam from the prior review's
  insertion), putting the rule first and tying the error message's "1" to it.
- Constructor discussion: "`__new__()` ... which you rarely use" now points at
  [Singleton](24_Singleton.md) as one of the rare uses, so the claim has a
  destination.
- Marking Overrides section: added a one-sentence definition of decorator
  syntax with a link to [Decorators](14_Decorators.md). Chapter 7 is the
  book's first real decorator user (`@override`, `@property`, `@classmethod`,
  `@staticmethod`, `@cached_property`); chapter 2 only names the syntax in an
  operator aside.
- `property_setter.py`: split `print(c.radius, c.area)` back into the two
  separate `print()` lines of the first listing. The prose says "the two
  lines that read `c.radius` and `c.area` are the ones from the first
  listing, unchanged", and the combined print contradicted it; identical
  lines are the section's whole point.
- Compose section close: "but composition or a module-level function is
  almost always a clearer choice" now says "a helper object or a module-level
  function". The section's title uses "composing" for the import trick
  itself, so "composition" as the recommended alternative read as a
  contradiction.
- String Representation opener: "Printing an object that defines neither
  method" became "By default, printing an object"; the two methods had not
  been named yet.
- `Solutions/07_Classes.md`, solution 3: noted that the solution strips
  `simple2.py`'s constructor prints, so a reader who adds `Simple3` in place
  and predicts the two extra constructor lines is told why the traces differ.

## Considered and declined

- **Moving "Composing Methods with `import`" out from between Inheritance and
  the `@override` section.** The placement was proposed by the prior review
  and accepted by Bruce (4e6a9698), so it stands; the stale cross-reference it
  broke is fixed with the named link instead.
- **Explaining `del n.total` in the cached_property prose.** The prior review
  deliberately moved that explanation into the listing (`# Discard the cached
  value` plus the recompute output). Re-adding prose would undo a settled
  choice.
- **Tightening "it doesn't really care about interfaces".** The hedge survived
  the recent hedge-cutting commit (812dcd9d) over this exact chapter, so it is
  deliberate voice.
- **Retitling the Compose section to avoid the "composing"/"composition"
  clash.** Fixing the one clashing word in the closing sentence is cheaper
  than a heading change, and nothing links to the section's anchor.
- **Rewording exercise 3's `Simple3("x").show_twice()`.** The mismatch with
  the solution's constructor-free trace is closed by the solution note; the
  exercise reads naturally as written.
