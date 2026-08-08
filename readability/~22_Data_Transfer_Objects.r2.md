[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/22_Data_Transfer_Objects.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human prose.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no significance
inflation, and the new `## Which Should You Use?` section reads as the verdict
it was moved there to be.
Four findings, all in sentences written during the deep review.

***

[] Reject

**Section:** The Standard-Library Versions (paragraph after `color_namedtuple.py`)
**Pattern:** §70 Interpretive Metadiscourse (P1)

Current:
> Assigning to a field raises an `AttributeError`,
> and `ty` reports it before the program runs,
> which is the one place in this chapter where the checker does better than it does for the attribute bag.

Proposed:
> Assigning to a field raises an `AttributeError`,
> and `ty` reports it before the program runs.
> The attribute bag caught nothing; a declared field catches this.

Why: the trailing clause rates the fact instead of stating it, and it talks
about the chapter rather than about the code.
It also repeats "does" twice in six words.
This one needs your call because the clause is carrying a real contrast that
the deep review asked for, so deleting it outright would lose the point:
the `Messenger` bag catches no typo, while a `NamedTuple` field catches a
write before the program runs.
The proposal keeps the contrast and drops the commentary.
The alternative is to cut the clause and let the two `AttributeError` facts
stand alone, since the reader met the bag's silence twelve paragraphs earlier.

***

[] Reject

**Section:** Intro, the `m: Any` paragraph
**Pattern:** paragraph doing two jobs, and a stub detail closing it (P2)

Current:
> `Any` switches the checker off for `m`.
> You can move that `Any` into the class instead of repeating it at every use site,
> by declaring a `__getattr__()` that returns `Any` and a `__setattr__()` that accepts one.
> Declaring only the first leaves the write, `m.more = 11`, still rejected.
> The standard library's stub for `SimpleNamespace` declares both,
> using `__getattribute__()` for the reading half.
> The price of an ad-hoc attribute bag is that no checker knows your attribute names.

Proposed: keep the relocation, drop the typeshed mechanics.
> `Any` switches the checker off for `m`.
> You can move that `Any` into the class instead of repeating it at every use site,
> by declaring a `__getattr__()` that returns `Any` and a `__setattr__()` that accepts one.
> Declaring only the first leaves the write, `m.more = 11`, still rejected.
> The standard library's stub for `SimpleNamespace` declares both,
> which is why the next listing needs no annotation.
> The price of an ad-hoc attribute bag is that no checker knows your attribute names.

Why: the paragraph was about why `m: Any` is needed, and now also explains how
to avoid writing it, which is a second subject.
The last new sentence is the weakest part: "using `__getattribute__()` for the
reading half" is a typeshed implementation detail that answers a question the
reader has not asked, and "the reading half" is an odd construction.
Your call, because the detail is accurate and load-bearing if you want the
reader to match this against the real stub, and my replacement drops it.
A third option is to keep the detail and split the relocation into its own
short paragraph after the price sentence, so each paragraph has one subject.
Note that the proposed last clause duplicates the "which is why this listing
needs no annotation to type-check" sentence two listings later; if you take it,
that later clause should lose its "which is why" half.

***

[] Reject

**Section:** A NamedTuple Is Still a Tuple (the ordering paragraph)
**Pattern:** §7 odd word choice, breaking a parallel already on the page (P2)

Current:
> Ordering arrives from `tuple` the same way, and is as type-blind as equality.

Proposed:
> Ordering is inherited the same way, and is as type-blind as equality.

Why: the section opens with "A `NamedTuple` inherits its equality from
`tuple`", so the ordering sentence should reuse "inherits" rather than
introduce "arrives from" for the identical relationship.
"Arrives" also reads as motion where the point is derivation.

***

[] Reject

**Section:** A NamedTuple Is Still a Tuple (the JSON paragraph)
**Pattern:** §11 repetition, one verb doing two different jobs (P2)

Current:
> Tuple behavior reaches serialization too.
> `json.dumps(Color(1, 2, 3))` writes the array `[1, 2, 3]`,
> since `json` sees a sequence and the field names never reach the output.

Proposed:
> Tuple behavior shows up in serialization too.
> `json.dumps(Color(1, 2, 3))` writes the array `[1, 2, 3]`,
> since `json` sees a sequence and the field names never reach the output.

Why: "reaches" and "reach" sit in adjacent sentences carrying unrelated
meanings, the first figurative and the second literal.
The literal one is the better use, so the figurative one moves.
