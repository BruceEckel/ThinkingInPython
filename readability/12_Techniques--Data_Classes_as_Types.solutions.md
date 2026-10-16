> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/12_Techniques--Data_Classes_as_Types/README.md`,
2026-10-16.
The prose carried few AI-writing tells: five wording fixes and four
rewraps of over-long lines went in directly, and no finding needed
Bruce's judgment, so this file holds no live block and serves as the
applied-directly record.
The claims about `Year`'s range, the four leap-year tests, `from_json()`,
`__replace__()`, the `ClassVar` signature, the third test in
"A `NamedTuple` Cannot Validate Itself", and the chapter's
`isinstance()` check were read against the listings and the chapter
and hold, apart from the signature claim corrected below.
`tip verify-ch CH=12 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 34, awkward predicate: "only when the year is leap" became
  "only in a leap year".
- Line 134, treadmill (restatement): cut "and it is the one century
  year that `Year` accepts." Line 25, in the same Solution step, says
  it nine lines of prose earlier.
- Line 490, "and" joining clauses with different subjects (global
  rule): "It passes the raw JSON value to `EmailAddress(...)`, and
  `EmailAddress`'s own `__post_init__()` runs the same check" became
  two sentences, the second with "then", since the relation is a
  consequence.
- Line 718, accuracy against the listing's `#:` output: "the one
  parameter that the generated signature takes" became "the one
  parameter after `self` in the generated signature". The printed
  signature is `(self, number: int) -> None`, which has two parameters.
- Line 958, treadmill: cut "The type test runs first." It restates the
  bold label "Test the type before the range" word for word in
  declarative form; the paragraph's reason follows directly.
- Lines 243, 245-247, 732, 843-845, 964-965, wrapping: five lines
  ran to 80-100 columns against the file's hand-wrap at about 70, and
  were rewrapped with no change to the wording.

## Considered and declined

- The trap-first opening of each Solution step (solutions 2, 3, 8)
  followed by bold labels that restate the fix (line 193 against
  243, lines 306-307 against 349-350, lines 907-908 against 953-954):
  this is the Solutions files' usual shape, where the opening shows the
  wrong version failing and the labeled paragraphs walk the listing.
  Not a treadmill.
- Hint and Solution repeating a fact (line 15 and line 25 on 2000
  being the one century year `Year` accepts; line 511 and line 595 on
  the rebuild going through `__init__()`): the steps open one at a
  time, so each states what it needs.
- Lines 191-192 and 905-906, the identical sentence on `expect()`
  raising an `AssertionError`: consistent wording for the same
  mechanism across exercises, not synonym cycling in reverse.
- Line 13, "and `Year` needs a method": the two clauses are additive,
  two things the reader must build, both following from the "so".
- Lines 28-29, "Once 2100 arrives, `Year` will accept it, and 2100 is
  a common year": the "and" pairs two facts that together justify the
  full rule. Stating "a divisibility-by-4 rule would call it
  leap" would add an inference the file leaves to the reader.
- Line 381, "Watch which code raises the `TypeFailure`: the
  constructor of `EmailAddress`, not `from_json()`": the colon delivers
  the answer the lead-in names.
- Line 847, "when you want the checker to confirm": "want" addressed
  to the reader is the recorded carve-out.
- §15 boldface: the bold step labels are a Solutions convention.
- Lines 866-868: the hint's last sentence is broken over three lines
  where the other hint sentences sit on one; rewrapping changes no
  wording, so it was left alone.
