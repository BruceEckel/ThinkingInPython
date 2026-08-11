[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/37_Pattern_Refactoring.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty`, ruff, and pytest are clean on `build/examples/37_Pattern_Refactoring`
(5 tests) and on `build/solutions/37_Pattern_Refactoring`, and all six
runnable scripts run. The chapter's outbound references were each checked
against the current text of their targets, including chapters 33 and 34 as
re-reviewed on this branch: 13's "When Not to Match" does warn against a
`match` over an open set; 13 names the expression problem at the
`#dynamic-binding-vs.-pattern-matching` anchor; 32's "One Type or Many" draws
the exact-table-versus-MRO distinction this chapter cites; 31's engine table
and 28's event bus both key on the exact type as claimed; 27's registry
factory sits under `#the-pythonic-factory-a-dictionary` and links back to this
chapter's `#simulating-a-trash-recycler`; 33 still explains the `_`
registration name and now recommends a raising base function for the
no-sensible-default case. Incoming links from 21, 27, 28, and 33 all target
anchors that still exist (no heading was changed here, deliberately). The
`_images/trash_sorter` figure exists. The arithmetic in the prose holds
(sixty pounds of plastic, two of four pieces binned). No finding needs a
decision, so this file has no live blocks; everything found was either
applied directly or recorded below as considered and declined.

## Applied directly

- `trash.py`: `Trash` is now `@dataclass(frozen=True)` with a `weight: float`
  field; the hand-written field-assigning `__init__()` is gone. House rule: a
  class whose `__init__()` only assigns parameters to fields is a dataclass
  unless the manual form is the lesson, and here it was not (nothing in the
  prose mentioned it). The alternative was a justifying sentence for the
  manual form; the dataclass also lets the listing reinforce chapter 12's
  ClassVar-stays-out-of-`__init__()` fact, so it won.
- Same section: the prose now says `@dataclass` builds `__init__()` from the
  bare `weight: float` annotation while the two `ClassVar` attributes stay
  out of it, with a named link to [Data Classes as
  Types](../Chapters/12_Data_Classes_as_Types.md) (`#d-a-real-classvar`).
- Same section: the two paragraphs re-teaching ClassVar shadowing and
  MRO resolution are compressed into one, ending in a named link to chapter
  9's "ClassVar and Inheritance", which teaches all of it (including the
  no-need-to-restate-the-annotation point, nearly verbatim).
- `Solutions/37_Pattern_Refactoring.md`: the four exercise listings restate
  `Trash`, so all four are converted to the same frozen dataclass; solutions
  gates re-run clean.
- "The First Cut": one-line gloss for the file name (`rtti` is *run-time
  type identification*, the C++ name for discovering a type at runtime),
  which the chapter never explained.
- "When a new material joins the system, `Plastic` say," is now
  "say `Plastic`," (punctuation of the aside).
- "sorting must not enumerate it, which the next section does" is now
  "...and the next section shows a sorter that doesn't" (the "which" had no
  workable antecedent).
- `plastic_dropped.py` discussion: added the loud-versus-silent contrast the
  listing demonstrates but the prose left implicit: the registry accepted
  `Plastic` the moment the `class` statement ran, and had the class been
  missing, `create()` would have raised a `KeyError` at the first `Plastic:`
  line, a loud failure at parse time; only the `match` loses trash silently.
  Also "the trash it happened to recognize" is now "the trash it recognized".
- `CrushedAluminum` bin sentence restructured; the old "which a sorter
  usually needs, but is worth knowing" left its second clause with no
  subject.
- Visitor paragraph consolidated: "Visitor is the classic way... [Visitor]
  solves this problem. Visitor is elaborate." was three sentence-initial
  Visitors saying overlapping things; now the link sentence carries the
  claim and the paragraph's second 33 link is "that chapter".
- "the throwaway name explained in [Visitor]" is now "the placeholder name",
  matching 33's post-review wording ("the conventional placeholder for a
  name nobody will use"); 33 no longer says "throwaway".
- singledispatch fallback paragraph: added that "no special handling" is a
  genuine answer here, and that when no default makes sense, 33's advice is
  a base function that raises `NotImplementedError` so a forgotten
  registration fails at the first call. Without this, the chapter names the
  risk and walks away from it.
- "Choosing the Lightest Construct": the two one-line costs were stated
  twice in a row, and "In Python that construct..." pointed back at a
  referent four sentences gone; the paragraph now states the costs once and
  keeps "the lightest construct" adjacent to its claim.
- Exercise 1: "account for every pound of plastic `plastic_dropped.py`
  reports" inverted the listing's point (the plastic is what it fails to
  report); now "...that `plastic_dropped.py` loses". Also "why is that the
  right behavior for it?" is now "why is that failure correct?".
- Solutions prose: two uses of "wants" (don't-use list), "only ever",
  "full stop", "exactly `sum_value()`'s situation", and "the numbers each
  type happens to carry" all fixed. The remaining "pins the registry to
  exactly {...}" stays: a precise set match.
- Ran `make reflow CH=37` over the edited prose.

## Considered and declined

- Renaming `recycle_rtti.py` to a Python-facing name (`recycle_match.py`):
  the name is an echo of the chapter's *Thinking in Patterns* lineage, and
  the new one-line gloss buys the same clarity without touching `Examples/`
  and every mention in prose.
- "You can use a dictionary keyed by type:" stays: "you can" is allowed when
  the option is the news, and here the alternative design is the news.
- "a checker accepts `bins: Bins = {}` just as happily" stays: the idiom
  carries the checker-versus-runtime contrast the sentence is about.
- "in the *GoF* sense" stays in its short form rather than expanding to the
  full *GoF Design Patterns* title; the fragment is unambiguous and the full
  title would bloat the sentence.
- `create()` reads `cls.registry` while registration writes
  `Trash.registry`: consistent with 27's caveat, which requires the base
  name only on the *write* side (a `cls.` write would shadow); the read
  resolves through the MRO to the same dict either way.
- `sum_value()` both prints and returns: the dual role serves the scripts
  (print) and the tests (return) at once, and splitting it would add a
  listing with no new lesson.
