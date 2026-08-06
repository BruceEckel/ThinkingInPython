[[Reviewed]]
# Deep review: 08_Static_Typing.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Teach variance in prose, or stop pointing the table at sections that never mention it

**Kind:** teaching
**Where:** section "Containers" table (lines ~465, ~469), pointing back at "Type Hints" (line ~49)
**Problem:** Two summary rows introduce the book's only mention of variance anywhere:
`list[T]` is "*invariant*, so `list[Circle]` is not a `list[Shape]`", and `Sequence[T]` etc. are
"*covariant* ... so `list[Circle]` satisfies `Sequence[Shape]`". Both send the reader to a
section for the explanation: the first to [Type Hints](#type-hints), which shows only
`list[int]` and `dict[str, float]`; the second to `23_Iterators.md#iteration-is-built-in`,
which does not discuss variance either. I grepped the whole book: "invariant"/"covariant" in
the typing sense appear nowhere except these two rows. So a reader who hits the surprise
(and it is a surprise: `ty` itself emits `list` is invariant in its type parameter,
Consider using the covariant supertype `collections.abc.Sequence` and links to its own FAQ)
has nowhere in the book to go.

**Proposal:** add a short subsection to "Type Hints", right after the
`list[int]`, `dict[str, float]`, `tuple[int, ...]`, `str | None` sentence, with a listing.
Verified against `ty` 0.0.65: `draw_all(circles)` checks, `mutate(circles)` fails with the
diagnostic quoted above.

```python
# variance.py
from collections.abc import Sequence

class Shape:
    pass

class Circle(Shape):
    pass

def draw_all(shapes: Sequence[Shape]) -> int:
    return len(shapes)

def add_square(shapes: list[Shape]) -> None:
    shapes.append(Shape())

circles: list[Circle] = [Circle(), Circle()]
print(draw_all(circles))
#: 2
# ty: expected "list[Shape]", found "list[Circle]":
add_square(circles)  # type: ignore
```

with prose along these lines:

> A `list[Circle]` is not a `list[Shape]`, which surprises most people the first time.
> The reason is that a `list` can be written to.
> `add_square()` would append a `Shape` to a list its caller believes holds only circles.
> Refusing the call is what keeps that from happening.
> A read-only shape has no such problem, so `Sequence[Shape]` accepts a `list[Circle]`.
> Annotating a parameter `Sequence[T]` instead of `list[T]` says the function only reads,
> and it accepts more callers as a result.

Then change both table rows' "see" targets to this new subsection.
Alternative, if the chapter is already long enough: leave the table rows as the only
mention and change their `see` targets so they at least do not point at sections that
say nothing about it (drop the link from the `list[T]` row, and point the
`Sequence[T]` row at [Type Hints](#type-hints) only if you add the prose).
**Cost:** one new listing and a new anchor. Nothing else in the book links to a variance
section, so nothing breaks. This is also the point where `Sequence` vs `list` in a
signature gets its rationale, which chapters 14, 20, and 23 currently assume.

---

## 2. Move "The Checker: `ty`" and "Catching Mistakes" up, right after "Type Hints"

**Kind:** structure
**Where:** sections "The Checker: `ty`" (line ~104) and "Catching Mistakes" (line ~118)
**Problem:** The chapter's most convincing listing is `area("3", 4)` returning `"3333"`,
and it sits seven sections in. Before reaching it the reader decodes gradual typing,
annotation syntax, narrowing, and `Final` with no demonstration of what any of it buys.
"Narrowing" in particular is machinery that exists to satisfy a checker the reader has not
yet run. The chapter also introduces `ty` twice with two different links: the opening
paragraph says "this book uses [Astral's `ty`](https://docs.astral.sh/ty/)", and section 6
says "This book uses [`ty`](https://github.com/astral-sh/ty), Astral's fast checker".

**Proposal:** new order: Gradual Typing, Type Hints, The Checker: `ty`, Catching Mistakes,
Narrowing, Constants with Final, Structural Typing with Protocols, and the rest unchanged.
Then cut the duplicate `ty` introduction: keep the opening paragraph's forward pointer to
one sentence and let "The Checker: `ty`" carry the link and the description, or vice versa.
Alternative: leave the order alone and instead front-load a two-line version of the
`area()` failure in the opening, before "Gradual Typing", as the motivating hook.
**Cost:** anchors travel with their headings, so all inbound links keep resolving.
Ten chapters link into this one; none link to `#the-checker-ty`, `#catching-mistakes`,
or `#constants-with-final`. `15_Context_Managers.md:214` links to `#narrowing`, which
still resolves after the move. The one real dependency is that `narrowing.py`'s prose
never mentions the checker's output, so nothing there needs rewriting to sit later.

---

## 3. Connect `Any` and `Unknown`: the reader will see the second word and not the first

**Kind:** teaching
**Where:** section "Gradual Typing" (line ~20) and "Type Parameter Defaults" (line ~362)
**Problem:** "Gradual Typing" says the checker treats unannotated code as "the type `Any`,
which is compatible with everything." Three hundred lines later, "Type Parameter Defaults"
says a bare `Stack` leaves `T` unsolved and "the checker falls back to `Unknown`."
The two names are never connected, and `Unknown` is the one the reader will meet in
practice: verified on `ty` 0.0.65, `reveal_type()` on an unannotated function reports
`def shout(text) -> Unknown`, and `Unknown` appears in no Python documentation, since it
is `ty`'s name for an `Any` that was inferred rather than written.

**Proposal:** add one sentence at the end of the "Gradual Typing" paragraph:

> `ty` calls this inferred form `Unknown` when it reports a type,
> to distinguish it from an `Any` you wrote yourself.
> They behave the same: both are compatible with everything.

**Cost:** none. It also makes exercise 5 land, since that exercise's whole payoff is a
`reveal_type()` reporting `Unknown` instead of `str`.

---

## 4. Warn that `isinstance()` against a `Protocol` does not work by default

**Kind:** teaching
**Where:** section "Structural Typing with Protocols" (line ~186, after `protocols.py`)
**Problem:** The section teaches "any object with that shape qualifies" and closes with
"Protocols preserve the flexibility of dynamic typing but add the early warning of static
type checking." The obvious next thing a reader tries is `isinstance(obj, Drawable)`, which
raises a `TypeError` at runtime unless the Protocol carries `@runtime_checkable`. The
chapter's only mention of `@runtime_checkable` is one summary-table row 300 lines later
that points at chapter 26. This is the near-miss the section should head off where the
reader is standing.

**Proposal:** add two sentences after "so they are of the correct shape.":

> A `Protocol` is a checking-time construct, so `isinstance(Circle(), Drawable)`
> raises a `TypeError` instead of answering.
> Decorating the Protocol with `@runtime_checkable` allows the call, at the cost of a
> weaker check: see [Surrogate](26_Surrogate.md#proxy).

**Cost:** none. Chapter 26 already covers the caveat that a runtime check only verifies
the methods exist, so this is a pointer, not a duplication.

---

## 5. Show one real `ty` diagnostic

**Kind:** teaching
**Where:** section "The Checker: `ty`" (line ~110)
**Problem:** The chapter is about a tool whose output the reader never sees. "It complains
where the hints and the code disagree, and is quiet when they agree" describes the outcome;
nothing shows the mechanism. Every listing prints its runtime result, which is the one thing
type checking does not change, so a reader could finish the chapter without knowing what a
type error looks like. Exercise 2 asks them to produce one and "read the error", with no
model of what they are about to read.

**Proposal:** after `    ty check`, show the actual diagnostic for `area.py` with the ignore
comment removed (verified verbatim on `ty` 0.0.65):

```
error[invalid-argument-type]: Argument to function `area` is incorrect
 --> area.py:4:12
  |
4 | print(area("3", 4))
  |            ^^^ Expected `int`, found `Literal["3"]`
info: Function defined here
```

and one line naming the parts: a rule name in brackets, the offending line, and the
expected-versus-found pair.
**Cost:** the block is version-specific text that no gate checks, so a `ty` upgrade can
make it stale silently. Trimming it to the two `error`/`Expected` lines reduces that risk.
This works best paired with proposal 2, which puts this section next to `area.py`.

---

## 6. Explain `-> None` in prose the first time a listing uses it

**Kind:** teaching
**Where:** section "Type Hints" (line ~51)
**Problem:** `-> None` first appears in `type_aliases.py`'s `def paint(...) -> None`, then in
five later `__init__` methods, and is never explained. The prose says an arrow gives "the
return type", so a reader could reasonably read `-> None` as "returns the value `None`
specifically" rather than "returns nothing useful", and wonder why every `__init__` declares
it. The summary table's `None` row answers this, 400 lines later.

**Proposal:** extend the sentence at line ~49 to cover it:

> A function that returns nothing declares `-> None`,
> which is why every `__init__()` in this chapter's listings ends that way.

**Cost:** none.

---

## 7. Give the chapter a conclusion instead of ending on a reference table

**Kind:** structure
**Where:** after "Type Hint Summary" (line ~552), before "Exercises"
**Problem:** The chapter's last prose is four lines about `Optional`/`Union`/`List` being
older spellings. The reader closes on a lookup table with no statement of what they can now
do or when to bother. "Gradual Typing" opens the chapter with the judgment call ("add hints
where they earn their keep") and nothing returns to it after the reader knows what the
options cost.

**Proposal:** a short closing section, titled for its content rather than "Summary",
that answers the question the chapter raises but does not settle: how much to annotate.
Roughly: annotate what crosses a boundary (function signatures, public attributes, anything
another file imports) and let the checker infer the rest; a local whose type is obvious from
its initializer gains nothing from an annotation; the value of a hint is proportional to the
distance between where the value is created and where it is used.
**Cost:** one new section and anchor. Nothing links to the end of this chapter.

---

## 8. Fix the `type[C]` summary row, which reads as a broken sentence

**Kind:** prose
**Where:** "Containers" table (line ~471)
**Problem:** The row reads "The class object `C` is not an instance, see [Classes as
Values](#classes-as-values-type)". Every other Meaning cell is a noun phrase; this one is
a declarative sentence that states a fact about `C` rather than saying what the annotation
means.
**Proposal:** `| `type[C]` | The class object `C`, not an instance of it, see [Classes as Values](#classes-as-values-type) |`
**Cost:** none.

---

## 9. Separate `TypeGuard` from `TypeIs` in the narrowing row

**Kind:** prose
**Where:** "Type narrowing" table (line ~527)
**Problem:** "A boolean predicate that narrows a type when it returns `True`" describes
`TypeGuard`. `TypeIs` (PEP 742) narrows in both branches, which is the reason it exists and
the reason it is now the one to use for most predicates. Collapsing them hides the only
distinction a reader needs to choose between them.
**Proposal:** `| `TypeGuard[T]`, `TypeIs[T]` | A boolean predicate that narrows a type: `TypeGuard` narrows only where it returns `True`, `TypeIs` narrows both branches |`
**Cost:** none.

---

## 10. Say which `Final` form the book prefers

**Kind:** code
**Where:** section "Constants with Final" (line ~101)
**Problem:** `final_constants.py` shows `MAX_RETRIES: Final = 3` and `GREETING: Final[str] =
"hello"` as equal options, and the prose presents them that way. Every other constant in the
book uses the explicit `Final[T]` form, which is the house rule. A reader following this
chapter's neutral framing will write the bare form and then find it nowhere else.
**Proposal:** append to the sentence at line ~101: state that the explicit form is what the
rest of the book uses, because it declares the intended type rather than accepting whatever
the initializer happens to be, and the difference shows up when the initializer is a literal
that the checker would otherwise narrow.
**Cost:** none. The listing keeps both forms, which it needs to make the contrast.

---

## 11. Name the chapter that established the ALL_CAPS convention

**Kind:** prose
**Where:** section "Constants with Final" (line ~83)
**Problem:** "The naming convention shown earlier used ALL_CAPS to signal a constant" points
at chapter 2's naming section (`Chapters/02_Tour.md:387`, "If something represents a
constant, use all uppercase letters"). "Shown earlier" goes stale silently if chapters move,
and gives a reader who missed it nothing to go back to.
**Proposal:** replace "shown earlier" with a named link to the section of
[Tour](02_Tour.md) that covers naming, so `heading_links.py` gates it.
**Cost:** the target heading may need an explicit `{#id}`; check its auto-slug first.

---

## 12. Add an exercise on narrowing or on `Literal`

**Kind:** exercise
**Where:** section "Exercises" (line ~554)
**Problem:** The five exercises cover protocols, reading a `ty` error, generics, `Self`, and
type-parameter defaults. Nothing exercises narrowing, `type[C]`, `Final`, or the `type`
statement, and narrowing is the section a reader is most likely to need on their own code.
**Proposal:** add one exercise, e.g.: in `type_aliases.py`, call `paint(grid, (2, 3),
"purple")` and run `ty check`; read the error, then widen `Color` to admit `"purple"` and
confirm the error goes away. A narrowing alternative: in `narrowing.py`, rewrite `shout()`
to take `str | int` and return the string uppercased or the integer doubled as text, using
`isinstance()` to narrow, and confirm `ty` accepts both branches.
**Cost:** none.

---

## 13. Split `type_defaults.py` into two listings

**Kind:** code
**Where:** section "Type Parameter Defaults" (line ~331)
**Problem:** One listing teaches class type-parameter defaults (`Stack[T = str]`, with both
the defaulted and the explicit call) and then, after a blank line, a second unrelated
construct: a defaulted `type` alias (`type Pair[T = int]`). Three `#:` groups and two ideas
in one block. The prose covers both, but the reader's attention splits.
**Proposal:** move the `Pair` half into its own listing after the paragraph ending "which
matters most for a class whose parameter has one common answer: callers who want that
answer write nothing, and the annotation stays precise," and keep the sentence "The same
applies to a `type` alias, as `Pair` shows" as its introduction.
**Cost:** a new extracted file name, so `Examples/` and any `norun.txt` entry need the sync
run. Exercise 5 names `type_defaults.py` and would still apply to the `Stack` half.

---

## Already fixed directly (no decision needed)

- line ~198: deleted a duplicated sentence in "Classes as Values". The paragraph said
  "A class is also a value, so you can pass it to a function, store it in a variable, and
  call it to make an instance." and then repeated "You can pass it to a function, store it
  in a variable, and call it to make an instance." verbatim as the next sentence.
- line ~458: corrected the `Never`/`NoReturn` summary row. It said "`Never` is the broader
  'impossible' type", but the typing specification states that `Never` and `NoReturn` are
  the same type and that checkers must treat them identically; `Never` is a bottom type, so
  "broader" points the wrong way. The row now says they are one type under two names, with
  `NoReturn` the return-position spelling.

## Verified, no change needed

- All eleven extracted listings run clean and every `#:` marker matches stdout exactly.
- `ty check` on `build/examples/08_Static_Typing` and `ruff check` both pass (`ty` 0.0.65).
- `heading_links.py` and `banned_phrases.py` pass; `reflow_prose.py --diff` reports no
  changes, so the prose is Semantic-Line-Breaks compliant.
- Every claim about checker behavior was probed on `ty` 0.0.65 and holds: the `Final`
  reassignment error, `area("3", 4)`, `n.upper()` on a `T`-inferred `int`, a `Protocol`
  rejecting a class with no `draw()`, `class Table[K = str, V]` being a syntax error,
  `-> Tally` in place of `-> Self` breaking the `.report()` chain, and both the
  `Stack[str]`-with-default and `Stack[Unknown]`-without-default results behind
  exercise 5.
- The `# ty: <paraphrased diagnostic>` comment style in `final_constants.py` and `area.py`
  matches the convention in chapters 9, 11, and 20; it is a paraphrase everywhere, not a
  quotation, so it is not stale.
- Every outbound cross-reference resolves and its target still covers what the row claims,
  including `35_Flyweight.md#intrinsic-and-extrinsic-state` for `cast()` (that section
  still discusses `cast()` even though the `cast()` call itself was removed when
  `ty` 0.0.63 landed).
- The hand-written `__init__` methods in `generic_box.py`, `type_defaults.py`, and
  `self_type.py` would be dataclasses under the house rule, but dataclasses are not
  introduced until chapter 12, so the manual form is correct here.
