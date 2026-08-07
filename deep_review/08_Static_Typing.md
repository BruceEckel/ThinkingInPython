When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Reported findings for `Chapters/08_Static_Typing.md`, in reading order.
Fixes already applied to the chapter (not repeated here): the `Unknown`
pronoun fix in Gradual Typing, `"3" * 4` wording, a paragraph naming the
`# ty:` comment convention, a paragraph saying `Final` blocks rebinding
but not mutation, the Protocol signature-is-part-of-the-shape sentence,
"identity test" in Narrowing, and two small prose tightenings in
Generics.

---

[] Reject

**Opening, line 6: "The examples up to this point have no type declarations" is
not true.**

`Chapters/02_Tour.md`'s `tstrings.py` (around line 352) is fully annotated:
`message: Template`, `def shout(template: Template) -> str:`, and
`parts: list[str] = []`. It is the only annotated listing before this chapter,
but it is there, and a reader who noticed it will trip on the claim. Chapter 2
also says a few lines earlier that the book "uses [static typing] from Static
Typing onward", so the two chapters disagree with 2's own listing.

Recommended fix, inside this chapter: soften to

    The examples up to this point have gone almost entirely without type
    declarations,
    which you might not miss on small programs.

Alternative (cheaper for this chapter, more work elsewhere): strip the
annotations from `02_Tour.md`'s `tstrings.py` so the claim becomes literally
true. See the Cross-chapter section at the end.

---

[] Reject

**Line 11: "The Python runtime ignores type hints, as long as they are properly
formed."**

Under PEP 649 (3.14+, which this book targets) the qualifier is now weaker than
it reads. An annotation naming a type that does not exist is not evaluated at
definition time at all; I confirmed on the pinned 3.15 build that

    def bogus(x: ThisNameDoesNotExist) -> AlsoMissing: ...

defines cleanly and only raises `NameError` when something reads
`bogus.__annotations__`. So "properly formed" now means no more than
"syntactically valid", and a reader coming from 3.9 will read it as "must name
real types".

Proposed change:

    The Python runtime ignores type hints; it does not even evaluate them
    until something asks for them.

This also sets up the summary table's later "quoting is optional under deferred
evaluation (PEP 649)" row, which currently arrives with no groundwork.

---

[] Reject

**Gradual Typing: `Any` and `object` are the chapter's most consequential
lookalike pair, and the contrast lives only in a summary table row.**

The summary says `object` is "Any object, but with no behavior assumed (safer
than `Any`)" and leaves it there. A reader who has just been told `Any` is
"compatible with everything" has no way to see why `object` differs, and the
common near-miss is reaching for `Any` when `object` is what was meant.

Proposed addition at the end of the Gradual Typing section:

    `Any` is not the same as `object`.
    Both accept every value,
    but `object` promises nothing about the value once you have it,
    so the checker rejects every operation you try on it.
    `Any` accepts every value and then permits every operation,
    which is what makes it an opt-out rather than a wide type.

---

[] Reject

**`### Variance` is in the wrong place: it uses `T` and `ty` diagnostics before
either is introduced.**

This is the chapter's clearest ordering defect. Writing one line per section
naming what it assumes and what it introduces, Variance's "assumes" column
holds two things that appear much later:

- `A list[T] is *invariant* in T`, and `Annotating a parameter Sequence[T]
  instead of list[T]`. Type parameters and the meaning of `T` are introduced in
  "Generic Functions and Classes", nine sections later.
- The `# ty:` comment in `variance.py` is the book's first use of that
  convention, and it lands two sections before "The Checker: `ty`" and three
  before "Catching Mistakes" explains how to read a diagnostic. (The paragraph
  I added to "Catching Mistakes" names the convention, so a reader who gets
  that far is retroactively covered, but the first encounter is still cold.)

It is also a difficulty inversion: the section immediately preceding it teaches
`def repeat(text: str, times: int) -> str`.

Recommendation: move `### Variance` to sit under "## Generic Functions and
Classes", after the `generic_box.py` listing and before
"### Type Parameter Defaults". By then `T` means something, `ty` has been
introduced, and "invariant in `T`" reads as a statement about a type parameter
instead of as new notation.

Price of the move:

- The `{#variance}` anchor is explicit, so both summary-table links to it
  survive. I grepped `Chapters/`, `Solutions/`, and `README.md`: no other file
  links `08_Static_Typing.md#variance`, so nothing outside this chapter breaks.
- `variance.py` defines its own `Shape`/`Circle`, so it does not depend on
  where it sits. (`class_values.py` separately defines its own pair; that
  duplication is unaffected either way.)
- "## Type Hints" loses its only subsection and ends on the
  "Containers and optional types read the way you say them" paragraph, which
  reads fine as a close.
- One sentence in the moved section, "Annotating a parameter `Sequence[T]`
  instead of `list[T]` says the function only reads", is the practical takeaway
  and is currently stranded early; after the move it lands next to the generics
  advice it belongs with.

Weaker alternative, if the move is unwanted: keep Variance where it is but
spell `T` out as `Shape` in that section's prose ("`list[Shape]` is
*invariant*, `Sequence[Shape]` is *covariant*"), removing the forward
dependency on type-parameter notation without moving anything.

---

[] Reject

**`variance.py`: `draw_all()` does not draw.**

It takes a `Sequence[Shape]` and returns `len(shapes)`. The name promises the
one thing the body does not do, and the return type `-> int` is the tell. It
costs nothing to name it for what it does:

    def count(shapes: Sequence[Shape]) -> int:
        return len(shapes)

with `print(count(circles))` below. The prose does not name `draw_all()`, so
only the listing changes. (`draw()` on `Circle`/`Square` in `protocols.py` is a
different listing and stays.)

---

[] Reject

**"## The Checker: `ty`" never says how to get `ty`, but two exercises tell the
reader to run it.**

The section shows the bare command

        ty check

and moves on. Exercise 2 says "remove the `# type: ignore` comment and run
`ty check` on the file", and exercises 5 and 6 do the same. A reader who has
not installed anything is stuck at the first exercise that matters.

Proposed addition after the command:

    `uvx ty check` runs it without installing anything,
    and `uv tool install ty` puts it on your path.

(Worth confirming the exact incantation against Astral's install docs before
this lands; I did not verify it on this machine, which has `ty` only inside the
book's own `uv` project.)

---

[] Reject

**`protocols.py`: the chapter asserts the rejection but does not show it, and
this listing is the one place where showing it matters most.**

The prose says "If you pass an object without a `draw()` to `render()`, `ty`
rejects it." Every other negative claim in this chapter is demonstrated with a
commented-out line and a `# ty:` comment (`variance.py`, `area.py`,
`final_constants.py`). The chapter's central structural-typing claim is the one
left as an assertion.

Proposed addition to the end of `protocols.py`:

    class Blob:
        def paint(self) -> str:
            return "blob"

    # ty: expected "Drawable", found "Blob":
    # render(Blob())

I verified the real diagnostic under `ty` 0.0.65:

    error[invalid-argument-type]: Argument to function `render` is incorrect
    info: type `Blob` is not assignable to protocol `Drawable`
    info: └── protocol member `draw` is not defined on type `Blob`

`Blob` also makes the point sharper than passing `object()` would: it is a
plausible class that a reader might expect to work because it "draws", just
under a different method name.

Cost: four lines in the listing, and exercise 1 (add a `Triangle` with its own
`draw()`) now has a neighbor showing the failing case, which strengthens it.

---

[] Reject

**Two narration comments in the listings, against the house style.**

`thinking-in-python-skill.md` says a comment explaining what a line does or why
belongs in the prose after the block, and "Never narrate what the next line
does." Two survive here:

- `protocols.py`: `def render(shape: Drawable) -> str:  # Accepts anything with
  draw()` — this is a design explanation, and the paragraph directly below
  already makes the same point.
- `class_values.py`: `return kind()  # Instantiate the class` — pure narration
  of the line it sits on; the prose below already says "Calling `kind()` then
  produces an instance."

Both can be deleted with no loss. Flagging rather than deleting because the
style skill also says not to edit comments already sitting in example code
without being asked about that specific comment.

The teaching-annotation comments elsewhere (`# T is int`, `# A Box[str]`,
`# No brackets, so T is str`, `# Pair means Pair[int]`) are a different thing
and should stay: they name the inferred type, which is the point of the
listing.

---

[] Reject

**"Constants with Final", last sentence: the stated difference between
`Final` and `Final[T]` cannot be reproduced with this book's checker.**

    The rest of the book uses the explicit `Final[T]` form,
    which declares the intended type instead of accepting whatever the
    initializer produces.
    The difference shows up when the initializer is a literal that the checker
    would otherwise narrow.

Under `ty` 0.0.65 there is no such difference. I probed both forms:

    A: Final = 3            # ty reveals Literal[3]
    B: Final[int] = 3       # ty reveals Literal[3] as well

and the chapter's own pair behaves the same way: `MAX_RETRIES: Final = 3`
reveals `Literal[3]` and `GREETING: Final[str] = "hello"` reveals
`Literal["hello"]`, not `str`. A function taking `Literal[3]` accepts both `A`
and `B` with no diagnostic.
`ty` narrows a `Final` to its initializer's literal type whether or not you
spelled the type out, because the name can never be rebound.

The claim *is* correct against the typing spec, and mypy 1.20.2 (also installed
here) shows it exactly as written: `A` reveals `Literal[3]?`, `B` reveals
`int`, and passing `B` to a `Literal[3]` parameter errors. So the sentence is
not wrong, it is unverifiable by a reader following the book's own toolchain,
and a reader who tries exercise-style poking at it will conclude the book is
wrong.

There is a second problem independent of the checker: the sentence says the
difference "shows up" without saying which way it cuts. Inferring gives the
*narrower* type, so the explicit form is the looser one, and the paragraph
leaves the reader unable to say why the book prefers it.

Recommended replacement, which is demonstrable under `ty` and states the
consequence:

    The difference shows up when the initializer's own type is not the type you
    mean.
    `CACHE: Final = []` infers `list[Unknown]`,
    so nothing that goes into the list is checked;
    `CACHE: Final[list[str]] = []` says what the list holds,
    and the checker enforces it.

Verified under `ty` 0.0.65: the bare form reveals `list[Unknown]` and accepts
`CACHE.append(3)`; the explicit form reveals `list[str]` and rejects it.

Alternative, if you want to keep the literal framing: say plainly that `ty`
does not currently distinguish the two for literal initializers and that other
checkers do. I would not, since the container case is both true everywhere and
the reason the rule exists.

---

[] Reject

**"Naming Types: The `type` Statement": `Literal` is taught as the way to spell
a closed set, with no pointer to `Enum`.**

`type Color = Literal["red", "blue", "green", "yellow"]` is the chapter's
demonstration, and the book's own style guide says the opposite is usually
right: "Closed set of constants with behavior attached: `Enum`/`StrEnum`, not
`Literal[...]`. An enum carries identity and methods." `Enum` arrives in
[Data Classes as Types](12_Data_Classes_as_Types.md#enums-are-types-too), four
chapters later, so a reader leaves this chapter with `Literal` as the answer.

Proposed addition after the `Color` paragraph:

    A `Literal` union is the lightest way to close a set of values.
    Once those values need behavior or an identity of their own,
    an `Enum` is the better fit;
    [Data Classes as Types](12_Data_Classes_as_Types.md#enums-are-types-too)
    makes the comparison.

The chapter already forward-links to 13, 14, 22, 26, 35, and 38, so one more
forward link is in character.

---

[] Reject

**Same section: the "never a bare scalar rename" rule is missing.**

The style guide says `type X = ...` aliases are for compound shapes (tuples,
dicts, callables, unions) and "never a bare scalar rename like
`type Symbol = str`". The chapter teaches the construct with three good
examples, all compound, and then says only that an alias is "a new name, not a
new type". A reader takes that as license for `type UserId = int`, which buys
nothing and reads like a distinct type to anyone skimming.

Proposed sentence, appended to the "A `type` alias is a new name" paragraph:

    That is why an alias earns its place on a compound shape and not on a bare
    rename: `type UserId = int` looks like a new type in a signature while
    behaving exactly like `int`.

This also makes the existing parenthetical about `NewType` land harder, since
`NewType("UserId", int)` is the thing the reader actually wanted.

---

[] Reject

**"### Type Parameter Defaults": no version note, unlike its neighbor.**

The section immediately below says "Before Python 3.12 you wrote type
parameters with `TypeVar` and `Generic`", which dates PEP 695. Type parameter
defaults are PEP 696 and are newer: Python 3.13. A reader on 3.12 who copies
`class Stack[T = str]` gets a `SyntaxError` with nothing in the chapter to
explain it.

Proposed sentence at the end of the section, before the `**P` paragraph:

    Type parameter defaults arrived in Python 3.13, one release after the
    bracket syntax itself.

While confirming this I verified the section's closing claim, which is correct:
`class Table[K = str, V]` is a genuine `SyntaxError` on the pinned build
("non-default type parameter 'V' follows default type parameter"), not a
runtime `TypeError`.

---

[] Reject

**Summary, "Basic types": `int` is accepted wherever `float` is declared, and
the table does not say so.**

This is the single most surprising thing about the built-in scalar
annotations, and readers hit it within a day of starting. Verified under `ty`
0.0.65: `def f(x: float)` accepts `f(3)` with no diagnostic, `def g(x:
complex)` accepts both `3` and `3.0`, and the relation does not run the other
way — `def h(x: int)` rejects `h(3.0)`.

Proposed change to the first row's Meaning cell:

    The built-in types, annotated by name alone, with no type parameter;
    an `int` is accepted where a `float` is declared, and an `int` or `float`
    where a `complex` is, but not the reverse

---

[] Reject

**Summary, "Containers": `Generator[Y, S, R]` is missing.**

The row lists `Sequence[T]`, `Iterable[T]`, `Iterator[T]`, `Mapping[K, V]`, and
stops. `Generator` is the one the book leans on hardest later —
[Generators](45_Generators.md) needs the three-parameter form, and the style
guide devotes a subsection to it ("Two-way generators get the full
three-parameter annotation") — and this table is where a reader looks it up.

Proposed new row after the `Sequence`/`Iterable` row:

    | `Generator[Y, S, R]` | A generator's yield, send, and return types;
    `Iterator[T]` is enough when it only produces values, see
    [Generators](45_Generators.md#annotating-a-generator) |

The anchor exists: `45_Generators.md` opens with `## Annotating a Generator`,
which auto-slugs to `annotating-a-generator`.

---

[] Reject

**Section order: "How Much to Annotate" is the chapter's conclusion and it
sits behind the reference tables.**

The chapter's real closing insight — annotate what crosses a boundary, and
"the value of a hint is proportional to the distance between where a value is
created and where it is used" — is the best paragraph in the chapter, and a
reader reaches it only after scrolling through eleven summary tables that are
explicitly reference material ("The book uses only a handful of these, but the
rest turn up in other code").

Recommendation: swap the two, so the order is ... → "Hints Are Not Enforced at
Run Time" → "How Much to Annotate" → "Type Hint Summary" → "Exercises". The
argument then ends where the reader is still reading, and the reference block
sits at the back where reference blocks belong.

Price: nothing links to `#how-much-to-annotate` or to the summary's `##`
heading from outside this chapter; the six deep links from other chapters all
point at `###` subsections inside the summary (`#containers`,
`#dictionary-and-record-shapes`, `#typing-decorators-and-directives`), which
move with it. `heading_links.py` will confirm.

---

[] Reject

**Exercises cluster on the second half of the chapter.**

Mapping the six exercises onto sections: Protocols (1), Catching Mistakes (2),
Generics (3), `Self` (4), Type Parameter Defaults (5), the `type` statement
(6). Nothing exercises Variance, Narrowing, `Final`, `type[C]`, or "How Much to
Annotate" — and Variance and Narrowing are the two sections a reader is most
likely to have half-understood.

Proposed addition (would also need a solution in
`Solutions/08_Static_Typing.md`, which I did not edit):

    7.  In `variance.py`, change `add_square()`'s parameter annotation to
        `Sequence[Shape]` and uncomment the call.
        Explain why `ty` now accepts the call and why `shapes.append(...)`
        no longer type-checks.

That one exercise covers the section's whole point — invariance, covariance,
and the reason a read-only annotation buys you callers — in one edit the reader
makes themselves.

A second candidate, if you want Narrowing covered too:

    8.  In `narrowing.py`, replace `if text is not None:` with `if text:`
        and run `ty check`.
        Explain why the empty string now takes the other branch even though
        the checker is satisfied either way.

---

## Cross-chapter

**`Chapters/02_Tour.md`** — related to the first finding above. `tstrings.py`
(the listing starting around line 352) is fully annotated: `message: Template`,
`def shout(template: Template) -> str:`, `parts: list[str] = []`. Twenty-six
lines earlier the same chapter says static typing is what "this book uses from
[Static Typing](08_Static_Typing.md) onward", and chapter 8 opens by saying the
examples so far have none.

If you would rather fix it there than soften chapter 8's sentence, the change
in `02_Tour.md` is to drop the three annotations from `tstrings.py`:

    message = t"{name} scored {score:.0f}%"
    ...
    def shout(template):
        parts = []

That listing has no other typed construct, and dropping them leaves the
t-string point intact. It does need `ty check` re-run on chapter 2, since
`piece.value` and `piece.format_spec` currently resolve through the
`Interpolation` narrowing and may or may not still check once `template` is
untyped. I did not make or test this change; it is chapter 2's to make.
