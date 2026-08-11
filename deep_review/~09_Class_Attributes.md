[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/09_Class_Attributes.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
ruff and `ty` are clean on `build/examples/09_Class_Attributes`, and all
eight scripts run. The chapter's three claims about `ty` were re-verified
with probes against the build tree on the pinned toolchain: `a.total = 99`
on a `ClassVar` reports "Cannot assign to ClassVar `total` from an instance
of type `Tally`" (matching the listing's comment), `self.total = 5` inside
a method is rejected while `self.total += 1` passes with zero diagnostics
(so `counter_near_miss.py` and its prose are right), and deleting the
`label` annotation still infers `str` from the parameter. A class-body
`Final[int]` was also probed: `ty` rejects reassignment through both the
instance and the class, so "shared *and* not reassignable" holds. The
inbound anchors other chapters use (#declaring-shared-state-with-classvar,
#a-bare-annotation-declares-it-does-not-create,
#class-attributes-are-not-default-values) are untouched. The edits below
are prose and teaching repairs; no listing changed, so `Examples/` is
unchanged. No findings met the bar for a live block.

## Applied directly

- ClassVar section: explained the `[CV]` tag at its first appearance in
  the book ("for *class variable*, marks an attribute whose storage is on
  the class") and tied the second display's tags to the fallback rule
  ("`label`, stored on `a`, carries no `[CV]`, while `total`, found by
  fallback, keeps it"). The tag previously debuted here unexplained;
  chapters 12 and 17 explain it, but both come later.
- Reworked the paragraph after `dataclass_no_annotation.py`, which pivoted
  mid-paragraph from the no-annotation `B` to `real_defaults.py`'s
  annotated `B` without saying so: "What changes is the generated
  `__init__()`, which assigns `self.x` on every instance" is false for the
  listing it followed (that `__init__()` assigns nothing; `vars(b)` is
  `{}`). The rewrite names the referent switch ("The annotated field in
  `real_defaults.py` also leaves a class attribute behind, as its last
  line shows"), which also finally explains that listing's
  `vars(B)["x"], vars(B())["x"]` line, and adds the class-assignment
  hazard the no-annotation form keeps.
- Methods paragraph: "That is why `display_object()` reports attributes
  and methods separately even though both live in the same dictionary"
  claimed the lookup rule explains the display's split, which it does not;
  now "reports attributes and methods separately, but both live in the
  same class dictionary, which is why assigning `a.show = something`
  would shadow the method". Also linked `display_object()` to
  [Classes](07_Classes.md), where the reader met it.
- Real Per-Object Defaults: after "The annotation marks a field", added
  "Without the decorator, the same annotated assignment stays a shared
  class attribute, as `Cart` showed", closing the annotation-times-
  decorator square the two sections otherwise leave implicit.
- Inheritance: "A class body stands to its base class as an instance
  stands to its class" now reads "A subclass stands to its base class";
  the analogy relates classes, not a body of code.
- `shared_mutable.py` prose: cut two sentences that restated the
  append-reads-then-mutates mechanism just explained, keeping the
  punchline as "Reading is the half with no protection: shadowing starts
  with an assignment, and `.append()` makes none."
- "and leaves the one that has behind" (a garden-path clause) is now
  "while the shadowed one keeps its own value".
- "which is why `class_var.py` writes `Tally.total += 1` with the class
  name spelled out" is now "increments through the class name" (banned
  "spelled").
- Conclusion: "which dictionary did the value land in?" is now "which
  dictionary holds the value?" (banned "land"), and "write the spelling
  that says so" is now "write the declaration that says so".
- "catches the accidental shadowing ... before it happens" is now "turns
  the accidental shadowing from the earlier example into a check-time
  error" (names the mechanism, drops "happen").
- "all are clearer with `ClassVar` on them" contradicted the `Final`
  recommendation two sentences later; now "each is clearer with the
  sharing declared", and `Final[int]` links to
  [Static Typing](08_Static_Typing.md#constants-with-final), which owns it.
- "`vars(obj)` returns that dictionary" had its antecedent four clauses
  back; now "`vars()` returns an object's own attribute dictionary".
- "Both listings define a class `A`" made the reader hunt for which two;
  now "This listing's `A` and the one in `inside_objects.py`".
- Dropped "itself" from "The default value itself is still built once".
- Exercise 7: "so the counter actually counts" is now "so the shared
  counter moves", echoing the prose's "the shared counter never moves"
  and dropping "actually".
- Ran `make reflow CH=09` over the edited prose.

## Considered and declined

- A `Final[int]` class-constant listing: the mention is prose-only, but
  chapter 08 owns `Final` and a listing here would add a second new
  construct to a section about `ClassVar`; the added link covers it.
- "assigning calls its setter" in the property aside presumes a setter
  exists; chapter 07 teaches that a getter-only property rejects writes,
  so the shorthand is safe for a reader arriving in order.
- Exercise 5 needs `from dataclasses import field`, which no listing in
  this chapter shows. The exercise supplies the field expression
  verbatim, the import error is self-explanatory, and the solution
  spells it out; adding it to the exercise text would solve the exercise
  for the reader.
- "ty rejects a direct `self.total = 5`, but it passes the augmented
  form" is version-dependent, but the book states current-tool behavior
  plainly and a `ty` upgrade is already a book-wide sweep event, so no
  hedge was added. *(Postscript below: the upgrade arrived the same
  day.)*
- The bug-framing paragraph ("A class attribute reads like a default
  right up until...") re-establishes context after the methods and
  property asides, a mild ordering tell; but the asides lean directly on
  the dictionary discussion above them, and the property aside hands
  back cleanly ("The rest of this chapter is about ordinary values"), so
  the order stands.
- `class_attribute_confusion.py` and its neighbors carry inline comments
  narrating each step; the comments predate this review and the marker
  interleaving depends on them, so they were left alone.

## Postscript (2026-08-10): ty 0.0.70 closed the augmented-assignment gap

This review verified against the environment's ty of the moment; the
lock already pinned 0.0.70, which flags `self.total += 1` on a
`ClassVar` (`invalid-attribute-access`). The opening paragraph's
"passes with zero diagnostics" no longer holds. The chapter was
updated after the merge: `counter_near_miss.py` carries a
`# type: ignore`, the "the one the checker misses" claim now states
that `ty` rejects the augmented form, exercise 7 asks what `ty`
reports instead of why it accepted the code, and
`Solutions/09_Class_Attributes.md` exercise 7 was rewritten to match.
`Solutions/12_Data_Classes_as_Types.md` exercise 6 (`self.built += 1`
on a frozen class) picked up the same treatment.
