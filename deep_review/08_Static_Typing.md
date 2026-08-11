When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Full four-pass review of `Chapters/08_Static_Typing.md` (correctness, teaching,
house style, prose), with `deep_review_db.md` read first as carry-forward.
The standing exemption for this chapter (the missing blank line after
`# area.py` keeps the quoted diagnostic's line 6 true) was respected;
the listing is untouched.
The chapter is technically sound throughout.
Every checker claim was re-verified against the pinned toolchain
(`ty` 0.0.69, CPython 3.15.0b4):
the quoted `area.py` diagnostic reproduces verbatim;
`isinstance()` against a non-runtime-checkable `Protocol`
raises the stated `TypeError`;
`class Table[K = str, V]` is a `SyntaxError` at compile time as claimed;
exercise 5's "no error either way" holds
(`reveal_type` shows `str` with the default, `Unknown` without);
exercises 7 and 8 behave as described;
and "the examples up to this point have gone almost entirely without type
declarations" is accurate (chapter 2's tour has a few, chapters 3-7 none).
All gates pass.
Every finding had one defensible answer, so everything is applied;
nothing needs a decision.

## Applied directly

- Intro: "type hints, which look like static type checking in other
  languages" became "look like the type declarations of statically typed
  languages"; a hint (syntax) can resemble a declaration, not the act of
  checking, and the corrected phrase sharpens the next sentence's contrast
  (the runtime ignores them).
- Catching Mistakes: extended the quoted diagnostic to the full `ty` output
  (verified character-for-character against 0.0.69). It previously cut off
  at a dangling "info: Function defined here" with no location under it;
  the full form shows the checker pointing back at the parameter
  declaration, and the enumeration sentence below now names that third part.
- Catching Mistakes: the `# ty:` shorthand convention now covers both forms
  it is used with ("whether commented out or suppressed with
  `# type: ignore`"); its first use, `area.py`, keeps the line live with
  `# type: ignore` rather than commenting it out, so the old wording did
  not describe it.
- Classes as Values: added one sentence separating the word `type`'s two
  roles in the listing, the annotation `type[Shape]` (for the checker)
  against the builtin call `type(shape)` in the demo (at runtime). Both sit
  in the same twelve lines and nothing distinguished them.
- Generic Functions: "A useful annotation returns a type that matches..."
  became "makes the return type match..." (an annotation does not return),
  and "A *type parameter* correctly specifies the returned type" became
  "expresses the connection", answering the preceding "`Any` cannot express
  that connection" directly.
- How Much to Annotate: "`count: int = 0` says less than `count = 0` does"
  became "says no more than"; the annotated form says the same thing at
  greater length, not less. Added a parenthetical noting that the first
  listing's `total: int = 0` was demonstrating the syntax, not a
  recommendation, so the chapter does not appear to break its own advice.
- Gradual Typing: "`object` promises nothing" became "guarantees nothing"
  (the promise metaphor), and "which is what makes it an opt-out" dropped
  the filler "is what".
- Intro: dropped "even" from "does not even evaluate them".
- Classes as Values: dropped the "So" that opened a second consecutive
  consequence sentence ("...so you can pass it... So an annotation
  needs...").
- The `type` Statement: dropped "exactly" from "behaving exactly like
  `int`"; the interchangeability was established one sentence earlier.
- Variance: "Refusing the call is what keeps that from happening" dropped
  the filler "is what".
- The `Self` Return Type: "the class you called this method on" became
  "the class on which you called this method" (stranded preposition).

## Considered and declined

- **Rewording `area.py`'s `# ty:` shorthand to the expected/found style of
  the other two shorthands** (`protocols.py`, `variance.py`). Its
  "argument of type "str" is not assignable to "int"" phrasing is a
  conceptual summary sitting directly above the verbatim diagnostic, so the
  reader maps one onto the other immediately; the shorthand convention
  paragraph explicitly calls these summaries, not quotes.
- **Trimming the Constants with Final opener.** Its first sentence and the
  clause before the listing both say reassignment fails the check, but the
  paragraph between them carries the real content (ALL_CAPS is convention,
  `Final` is enforcement), and the repetition frames it rather than pads it.
- **Adding exercises for `Final` or `type[C]`.** The eight exercises cover
  the chapter's main claims (protocols, diagnostics, generics, `Self`,
  defaults, `Literal` aliases, variance, narrowing); a `Final` exercise
  would replicate exercise 2's shape with less to learn, and each addition
  drags `Solutions/08_Static_Typing.md` along.
- **Retitling "Hints Are Not Enforced at Run Time".** It is a declarative
  clause heading rather than the book's usual noun phrase, but it states
  the section's one fact plainly, and "at run time" matches the book's
  two-word adverbial convention.
