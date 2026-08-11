[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/20_Rethinking_Objects.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty`, ruff, and pytest are clean on `build/examples/20_Rethinking_Objects`,
and all 20 scripts run. Probes confirmed the chapter's checkable claims:
the `ty` message quoted in `newtype_boundary.py` matches the real
diagnostic ("Expected `UserId`, found `Literal[42]`"); commenting out a
`case` makes `assert_never()` report the missed shape by name
(`Circle & ~Rectangle` is not `Never`), which is what exercise 5 asks the
reader to observe; and a `@dataclass` version of `Plugged` does print
`_numbers` and `_bob` in its generated `__repr__`, as the prose claims.
All three external links resolve: both GitHub talk repositories, and the
DePaul PDF is Strachey's *Fundamental Concepts in Programming Languages*
(the 1967 Copenhagen lectures, printed in 2000), so "1967 lecture notes"
is accurate. Cross-chapter ends line up: chapter 38's `EDGE` room is
labeled a Null Object and links back here, `logging.NullHandler` is real,
and the Evolution section's history claims check out (Simula kept
standalone functions; Rust immutable bindings by default; `let`/`val` in
Swift and Kotlin; Go without general immutability). One probe overturned
prose instead of confirming it: the bare-annotation protocol claim told
half the story (first entry below).

## Applied directly

- "Protocols Generalize, Composition Adapts": the prose said `PairCoord`
  "satisfies the property form and fails the annotation form", implying
  frozen `Point` would pass a bare-annotation `Coord`. Probed with `ty`:
  `Point` fails it too ("the member does not accept writes of type
  `float`"), since a frozen dataclass rejects every assignment. The
  paragraph now says both classes fail the annotation form, which also
  strengthens its closing advice.
- "Prefer Composition to Inheritance": added the near-miss a reader would
  plausibly write, `extend()` calling `self.items.extend(more)` directly,
  which breaks the count again. The new sentences say what composition
  changes: the bug becomes local and readable instead of hiding in
  `list` internals. Without this, "nothing can slip past the counter"
  overclaims.
- shapes_match trade-off paragraph: named the expression problem with a
  link to Pattern Matching (chapter 13), where the term is taught;
  chapter 37 already references it the same way, so this ties an
  existing thread rather than starting one.
- LSP section: "Python has no compiler" is now "Python has no such
  compiler". CPython compiles to bytecode (chapter 18 says so), and the
  antecedent, "a statically typed compiler", sits two sentences up.
- `composition.py` prose: "which is what [The General Form of
  `replace()`] is for" ended on a stranded preposition inside a cleft;
  now "...rebuilding the `Address` and then the `Contact`. [The General
  Form of `replace()`] makes that rebuild routine."
- NewType paragraph: "Here, the same `# type: ignore` that passes the
  book build silences that diagnostic" needed two readings; now "In
  `newtype_boundary.py`, the `# type: ignore` silences that diagnostic
  so the rejected call can run anyway."
- Dynamic Typing intro: "the necessary method(s)" is now "the necessary
  methods", and "the only validity check happens at runtime" is now
  "comes at runtime".
- "Each protocol only names the shape it needs" is now "names only the
  shape it needs": the restriction belongs on what it names.
- Dropped "actually" twice ("whether the override behaves...", "what
  Python delivers...") and "ever" twice ("before the program runs",
  "no caller sees a `| None`").
- Ran `make reflow CH=20` over the edited prose.

## Considered and declined

- "Substitutability is the first thing OOP promised that no tool can
  check" sits beside "OOP made four promises" that do not list
  substitutability. Read several times and left alone: the sentence
  starts the chapter's running tally of unverifiable promises (the
  encapsulation leak and the protocol shape-versus-semantics split
  continue it), and substitutability is implicit in the fourth promise.
  Every clarification I drafted weakened the paragraph.
- Null Object: the near-miss `if logger is None: logger = NullLogger()`
  inside `total()` also removes the per-call guards. Declined a contrast
  sentence: the section's point is that `| None` leaves the signature,
  which that idiom does not achieve, and the prose already says no
  caller sees a `| None`.
- `CountingBox.extend(more: list[int])` could take `Iterable[int]`. Left
  as is: `list[int]` keeps the listing free of an extra import and
  matches the call it replaces.
- "*Subtype polymorphism* is what the four subsections below demonstrate"
  keeps its cleft: deleting "is what" breaks the sentence, and
  restructuring would break the term-first parallel with the parametric
  and ad-hoc paragraphs that follow.
- The `#:` markers gathered after the `if __name__` blocks in
  `point_distance.py` and `leaky.py` follow the book-wide convention
  (no indented marker exists anywhere in `Chapters/`), so they are not
  a violation of markers-hug-their-code.
- `leaky.py` and `plugged.py` keep their hand-written `__init__`s: the
  underscore-private fields behind properties are the lesson, and the
  prose covers the dataclass alternative and its `__repr__` leak.

No live blocks: nothing surfaced that needs a decision only you can
make.
