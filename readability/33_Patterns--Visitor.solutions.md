> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/33_Patterns--Visitor/README.md`,
2026-10-16.
The prose carried few AI tells. The findings were two "and" joins that
hid a consequence or a contrast, one awkward sentence, one restated
paragraph opening, and a run of lines far past the file's 70-column
hand-wrap. Every fix had one sensible answer and went in directly, so
this file holds no live block and serves as the applied-directly record.
Claims touched were checked against `flower_visitors.py` in the chapter
and the solution listings. `tip verify-ch CH=33 ISOLATED=1` passed,
27 of 27.

## Applied directly

- Line 105, awkward construction: "`Bee`, `Fly`, and `Worm` exist to be
  types for the `visit()` dispatch to resolve" became "exist as the
  types on which the `visit()` call dispatches". Checked against
  `flower_visitors.py`, where `visit()` resolves through `Bee`, `Fly`,
  or `Worm` to the `Pollinator` or `Predator` method.
- Line 198, "and" hiding a consequence: "both fall back to their
  defaults, and the demo prints" became "..., so the demo prints".
- Lines 280-281, "and" joining clauses with different subjects (a
  contrast): "Methods on a class keep a new type in one place, and
  functions over a hierarchy keep a new operation in one place" became
  two sentences.
- Lines 417-421, treadmill: the paragraph opened by restating lines
  406-408 ("`Any` gives up every check on the visitor side, so a bad
  visitor ... shows up as a runtime `AttributeError` instead"). Cut the
  restatement and moved what it added into the next sentence: "Two fixes
  restore the checks that `Any` turns off on the visitor side:". "gives
  up" became "turns off", the literal mechanism. The close alternative
  was to keep the restatement as the exercise's closing summary.
- Hand-wrap at about 70 columns: lines 105, 110-115, 199-200, 262-267,
  275-277, 350, 395-396, and 406-410 ran from 80 to 110 columns or broke
  mid-clause at short widths. Rewrapped; wording unchanged apart from
  the entries above.

## Considered and declined

- Line 15, watch word `only`: "Only that one needs `@singledispatch` and
  `register`." A sentence-initial "Only" stating a real restriction, a
  ruled-fine shape.
- Lines 109-111, "You lose one thing: ... When that matters, pass the
  function instead". The second sentence half-takes back the loss, but
  the paragraph then names the one gain a `Visitor` object keeps
  (choosing an operation at runtime) and shows the function-based
  replacement, so the framing holds.
- Line 111, "`op = eat` works." A short beat among longer sentences, not
  a staccato run.
- Line 95, colon: "Everything on the visitor side disappears: seven
  classes ..." delivers the inventory the lead-in names; the count
  matches `flower_visitors.py` (`Visitor`, `Bug`, `Pollinator`,
  `Predator`, `Bee`, `Fly`, `Worm`, and the two `visit()` methods).
- Line 199, "the wrong answer arrives as ordinary output": "arrives" is
  a mild figure, but the sentence names the mechanism (both checkers
  accept the program), so it stays.
- Lines 275-277, "the new type's two registrations sit in two places":
  the new type also adds a class in a third place. The sentence counts
  registrations only, and its contrast with the operation's one place
  holds, so it stays.
- The bold step labels ("**Add a type.**", "**Declare the visitor's
  interface.**", "**Demonstrate the runtime failure.**"), §15: a
  Solutions convention across the README files.
