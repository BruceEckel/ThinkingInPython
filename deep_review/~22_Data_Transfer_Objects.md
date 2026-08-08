[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Intro, after `messenger_idiom.py` (the `m: Any` paragraph, ~line 41).**
The chapter tells the reader to annotate every *use site* (`m: Any`), then two
listings later explains that `SimpleNamespace` needs no annotation because
"its type declaration says so: reading any attribute yields `Any`."
A reader who connects those two facts will immediately ask why `Messenger`
can't say the same thing about itself, and the chapter never answers.

It can. Verified under `ty` 0.0.65: adding

    def __getattr__(self, name: str) -> Any: ...

to `Messenger` makes both `m.info` and `m.inof` type-check with no annotation
at the use site, exactly as `SimpleNamespace` does. Writes still fail
(`m.more = 11` is still `unresolved-attribute`); typeshed's `SimpleNamespace`
declares `__setattr__(self, name: str, value: Any) -> None` as well, which is
what buys the second half.

Proposed: one sentence at the end of that paragraph, so the `Messenger` /
`SimpleNamespace` comparison later has somewhere to land:

> You can move the `Any` into the class instead of repeating it at every use
> site, by declaring `__getattr__()` and `__setattr__()` that return and accept
> `Any`. That is exactly what the standard library's stub for
> `SimpleNamespace` does, which is why the next listing needs no annotation.

Cost: it slightly weakens the "the price of an ad-hoc attribute bag" line that
follows, since the price becomes "written once" rather than "paid everywhere."
The alternative is to leave the chapter as is and accept the unanswered
question. I recommend adding it, because chapter 33 leans on this chapter as
the canonical unavoidable `Any` and the reader should see that the `Any` is
unavoidable in *kind*, not merely inconvenient in placement.

---

[] Reject

**"The Standard-Library Versions", first line (~line 50).**
"In the standard Python library, `types.SimpleNamespace` is a `Messenger`."

The backticks make `Messenger` read as the class defined ten lines above, so
the sentence looks like a false claim about subclassing. The intended reading
is the pattern, which the chapter opened by naming in italics.

Proposed: drop the backticks and name the idea.

> In the standard Python library, `types.SimpleNamespace` is a ready-made
> Messenger.

---

[] Reject

**After `color_namedtuple.py` (~line 129), "Since the fields cannot be
mutated".**
The chapter asserts the immutability and then immediately moves on to
`_replace()`. Nothing in the listing shows the refusal, so a reader can only
take it on faith, and this is the one place in the chapter where the checker
does better than it does for the attribute bag.

Verified: `red.r = 9` raises `AttributeError: can't set attribute` at runtime,
*and* `ty` reports
`error[invalid-assignment]: Cannot assign to read-only property 'r' on object
of type 'Color'` statically.

Weighing against it: chapter 12 already states this at line 501 ("A
`typing.NamedTuple` also rejects assignment and is also hashable") and shows
the equivalent refusal for a frozen data class with real output. So this is a
restatement, and you may prefer to leave the assertion bare here. My
recommendation is still to add it, weakly.

Proposed: two lines at the end of `color_namedtuple.py`, before the
`_replace()` line so the ordering reads "you can't mutate, so here is how you
copy":

    try:
        red.r = 9  # type: ignore
    except AttributeError as e:
        print(type(e).__name__)
    #: AttributeError

plus a clause in the prose noting the checker catches it too. That contrast
is worth having: the `Messenger` bag catches nothing, the `NamedTuple` catches
this before the program runs.

(If you take this, the `# type: ignore` is required or `ty` fails the gate on
the deliberate error, the same shape as `frozen_leaky.py` in chapter 20.)

---

[] Reject

**Chapter structure: the "Use `SimpleNamespace` for..." paragraph
(~lines 145-154) is a conclusion sitting in the middle of the chapter.**

It summarizes all three record types, points at `TypedDict` and at chapter 12,
and reads like the last paragraph of the chapter. Two sections then follow,
and the last of them ends with a *second* piece of choose-between guidance
("Choose `NamedTuple` when tuple behavior is the goal... Choose a frozen
dataclass when..."). So the reader gets the verdict twice, first before the
evidence for it and then again after.

Every neighboring chapter closes with a titled section that does this job
once: chapter 24 "Which Should You Use?", chapter 27 "Which Factory Should You
Use?", chapter 26 "One Surrogate, Two Intents", chapter 23 "The Pattern That
Disappeared". Chapter 22 has no such section.

Proposed: move the paragraph to a new final section, `## Which Should You
Use?`, and merge the "Choose `NamedTuple` when... / Choose a frozen dataclass
when..." lines into it, leaving "A NamedTuple Is Still a Tuple" to end on the
`FrozenColor` / `FrozenDimensions` result. That gives the chapter one verdict,
after the evidence, in the place the rest of Part 3 puts it.

Price of the move, checked:
- Nothing later in the chapter refers back to that paragraph.
- The `TypedDict` and `12_Data_Classes_as_Types.md#a-type-is-a-set-of-values`
  links travel with it; `heading_links.py` still passes wherever they sit.
- Four other chapters link to headings inside chapter 22, and all four survive
  the move because no heading is removed or renamed:
  `19_Concurrency.md:995` -> `#returning-multiple-values`;
  `08_Static_Typing.md:584` and `12_Data_Classes_as_Types.md:955` ->
  `#the-standard-library-versions` (which keeps `color_namedtuple.py`, the
  listing both sentences actually point at);
  `12_Data_Classes_as_Types.md:505` -> `#a-namedtuple-is-still-a-tuple`
  (which keeps the equality contrast, the difference that sentence names).
  Adding a new final heading breaks nothing.
- "The Standard-Library Versions" then ends on the leading-underscore
  paragraph, which is a weaker close. If that bothers you, the alternative is
  to keep a one-line version of the verdict where it is and expand it at the
  end; I prefer the single-verdict version.

---

[] Reject

**"A NamedTuple Is Still a Tuple" (~line 191): the section covers equality
only, and equality is not the tuple behavior most likely to bite.**

The section's own title promises more than it delivers. Three other
consequences of "still a tuple" are near-misses a reader will actually hit,
all verified on the pinned 3.15:

- **Ordering is inherited too, and is equally type-blind.**
  `Color(1, 2, 3) < Dimensions(1, 2, 4)` is `True`. `sorted(colors)` silently
  orders by `r`, then `g`, then `b`, with nothing declaring that intent. A
  frozen dataclass refuses both: `FrozenColor(1,2,3) < FrozenColor(1,2,4)`
  raises `TypeError` unless you pass `order=True`, and even with `order=True`
  a cross-type comparison still raises. This is the same lesson as the
  equality one and costs two lines.
- **Concatenation degrades silently.** `Color(1, 2, 3) + (4,)` returns a plain
  `tuple`, not a `Color`, with no error.
- **`json.dumps()` writes an array, not an object.**
  `json.dumps(Color(1, 2, 3))` gives `[1, 2, 3]`;
  `json.dumps(Color(1, 2, 3)._asdict())` gives `{"r": 1, "g": 2, "b": 3}`.
  A `@dataclass` raises `TypeError: Object of type D is not JSON
  serializable` instead, which is the safer failure. This one matters because
  the guidance paragraph already tells the reader to think about JSON.
- (Sharpest, if you want only one:) `"%s" % Color(1, 2, 3)` raises
  `TypeError: not all arguments converted during string formatting`, because
  `%` consumes the record as its argument tuple.

Proposed: add the ordering pair to `still_a_tuple.py` (it belongs with the
equality pair and shares its setup), and add the `json.dumps` contrast as
prose with an inline example. I would leave concatenation and `%` out unless
you want the section to be a full catalog. Recommend ordering + JSON.

---

[] Reject

**"Returning Multiple Values" / the guidance paragraph: `dataclasses.asdict()`
is never mentioned, though `astuple()` is and `_asdict()` appears in a
listing.**

`red._asdict()` prints in `color_namedtuple.py` and the only prose about it is
the leading-underscore paragraph, which explains the name but not the use. The
guidance paragraph raises JSON and sends the reader to `TypedDict`. The
missing link between the two is that both record types convert to a dict:
`Color._asdict()` and `dataclasses.asdict()`.

Proposed: one clause in the guidance paragraph, e.g. after the `TypedDict`
sentence:

> When it only has to *become* a dict on the way out, `_asdict()` on a
> `NamedTuple` and `dataclasses.asdict()` on a data class each produce one.

---

[] Reject

**Exercises: two of the six are mechanical, and the chapter's sharpest claim
is unexercised.**

Exercise 2 (add `z: float`) and exercise 3 (add a `Fraction` `NamedTuple`
shaped like `Color`) both ask the reader to retype a pattern already on the
page; neither has a wrong answer to get. Meanwhile nothing exercises the
shallow-immutability point at ~line 133, which is the claim the chapter shares
with chapter 20 and the one a reader is most likely to get wrong in their own
code.

Proposed: replace exercise 3 with

> 3.  Add a `NamedTuple` called `Recipe` with fields `name: str` and
>     `steps: list[str]` to `color_namedtuple.py`. Mutate the `steps` list of
>     an instance and print the record. Then try to use the record as a
>     `dict` key and explain the result.

Exercise 2 can stay as warm-up. Also note that exercise 3's current name,
`Fraction`, collides with `fractions.Fraction`; if you keep the exercise,
rename it.

---

[] Reject

**Out of scope for this file, but flagged: `Solutions/22_Data_Transfer_Objects.md`
has solutions for exercises 1-4 only.**

The chapter has six exercises; the solutions file stops after 4. Every
neighboring chapter with a solutions file is complete (20: 6/6, 23: 8/8,
24: 4/4, 25: 3/3). Exercises 5 (bare `tuple[float, int]`) and 6 (predicting
the `Point3` and `FrozenColor` comparisons) need solutions written.

Also, solution 2 answers "update **both** `Point(...)` calls" by inventing a
second call; the chapter's `point_dataclass.py` only ever had one. I corrected
the exercise text in the chapter to say "the `Point(...)` call". The existing
solution still satisfies the corrected wording, so nothing in
`Solutions/` has to change for that, but it is worth a look when you write
solutions 5 and 6.

---

## Cross-chapter

[] Reject

**Target: `Chapters/03_Containers.md`, the `### namedtuple` section
(~line 462).**

It ends with:

> For records with defaults, methods, or type annotations, prefer a data class
> (see [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)).

All three of those are wrong as a reason to leave `namedtuple` behind, and
chapter 22 is where the reader finds out:

- `typing.NamedTuple` takes per-field type annotations. That is the whole
  point of chapter 22's `Color`.
- `typing.NamedTuple` supports field defaults
  (`g: int = 5`; `C._field_defaults` is `{'g': 5}`), and
  `collections.namedtuple("P", "a b", defaults=(9,))` does too.
- `typing.NamedTuple` supports methods; a `def` in the class body works
  normally. All three verified on the pinned 3.15.

The reader who takes chapter 3 at its word will never look at chapter 22's
`NamedTuple`, and chapter 22 in turn never contradicts chapter 3.

Exact change I would make in chapter 3, replacing that sentence:

> For a record with type annotations, defaults, or methods, write the class
> form, `typing.NamedTuple`
> (see [Data Transfer Objects](22_Data_Transfer_Objects.md)). Prefer a data
> class when the record should be mutable, or should be a distinct type that
> only equals its own kind
> (see [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes)).

I have not touched chapter 3.

---

[] Reject

**Target: none. Checked and consistent, recorded so the next review does not
re-derive it.**

- The load-bearing-`Any` thread 22 -> 33 is consistent. Chapter 33's
  "This `Any` is chosen, unlike the one in
  [Data Transfer Objects](22_Data_Transfer_Objects.md), where a bag of
  attributes named at runtime leaves no precise type to write" matches
  chapter 22's "The price of an ad-hoc attribute bag is that no checker knows
  your attribute names." Both verified against `ty` 0.0.65: `Messenger`
  attribute access is `unresolved-attribute` without the `Any`, and
  `SimpleNamespace` attribute access reveals `Any`. No change needed at
  either end. Chapter 33's link carries no anchor because chapter 22's `Any`
  discussion sits in the unheaded intro; if the review finding above about a
  final "Which Should You Use?" section is applied, that stays true, so the
  link is still fine.
- The frozen-is-shallow thread 20 -> 22 is consistent. Chapter 22's link
  targets `20_Rethinking_Objects.md#the-immutability-solution`, which is where
  `frozen_leaky.py` lives. I sharpened chapter 22's wording (the record is
  unhashable because it holds a list, not because anyone mutated it) without
  touching chapter 20.
