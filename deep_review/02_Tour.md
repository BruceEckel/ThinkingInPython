When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter opening, lines 3-5 — the "several that follow" list stops short of Part I.**

The opening says the tour covers "syntax and the scalar types here, then
containers, control flow, functions, modules, classes, and static typing."
[Introduction](01_Introduction.md) describes Part I as running through
"class attributes, and object cleanup" as well, so this list ends two
chapters early and a reader mapping it onto the table of contents finds
09 and 10 unaccounted for.

Proposed change: append the two, `"...classes, static typing, class
attributes, and object cleanup."` Alternative, if the shorter list is
deliberate because 09 and 10 are less tour-like: change "then" to "then,
over the chapters that follow," and drop the implication of completeness.
I recommend the first; it costs four words and removes the mismatch.

---

[] Reject

**Section "How to Read the Examples" (line 43) — the heading names a third of its content.**

The section has two unrelated halves. Lines 45-53 are the book's example
conventions (`#`, the filename first line, `#:` markers). Lines 55-82 are
Python's block syntax: parentheses around a conditional, the colon, the
indented suite, block-does-not-create-a-scope, indent depth, semicolons.
The second half is the real teaching content of the section and nothing in
the heading points a reader to it. Anyone scanning the chapter for "how
does Python delimit blocks" will skip a heading that reads like front
matter.

Proposed change: split at line 55 into two sections, keeping
`## How to Read the Examples` for lines 45-53 and adding
`## Indentation and Blocks` for lines 55-82. Price: no other chapter links
to `#how-to-read-the-examples`, so nothing breaks; the only cost is one
more entry in the site's chapter contents.

---

[] Reject

**Section "How to Read the Examples", lines 45-53 — duplicates the Introduction.**

[Introduction](01_Introduction.md)'s "The Examples" section already
explains the filename-comment convention (with the same
`Examples/<chapter>/` mapping) and the `#:` markers in more detail,
including that the build regenerates them. Chapter 02 restates both in
compressed form.

Proposed change: cut lines 45-53 down to the one thing the Introduction
does not say, that `#` is a comment to end of line like C++/Java `//`, and
replace the rest with a pointer:
`The filename first line and the `#:` output markers are explained in
[The Examples](01_Introduction.md#the-examples).`
Alternative: leave the repetition, on the grounds that a reader who skipped
the Introduction lands here first. I lean to cutting, since the chapter's
own listing at line 29 already demonstrates both conventions.

---

[] Reject

**`arithmetic.py` prose, lines 147-149 — "round down to the nearest integer" implies an `int` result.**

`//` is described as "floor division (divide, then round down to the
nearest integer)." The result is a whole number but not necessarily an
`int`: `7.0 // 2` is `3.0`, and `7 // 2.0` is `3.0`. A reader who takes the
parenthetical literally will be surprised the first time a float creeps
into the operands. The neighbouring claim that "`/` always produces a
`float`" has the same shape (true for the built-in numeric types this
chapter covers, not for `Decimal` or `Fraction`), but that one is harmless
at this level.

Proposed change: `(divide, then round down to a whole number; the result's
type follows the operands, so `7.0 // 2` is `3.0`)`.

---

[] Reject

**`bitwise.py`, lines 206-209 — the shift pair prints the same value twice.**

```python
print(bin(1 << 4))  # Left shift, same as 1 * 2 ** 4
#: 0b10000
print(bin(64 >> 2))  # Right shift, same as 64 // 2 ** 2
#: 0b10000
```

Both are 16, so two adjacent lines demonstrating opposite operators show an
identical marker. A reader checking their own arithmetic against the output
has to stop and confirm it is not a copy-paste slip in the book.

Proposed change: make the right shift land somewhere else, e.g.
`print(bin(0b110000 >> 2))` with `#: 0b1100`, which also keeps the operand
in the binary-literal notation the rest of the listing uses. Any second
value works; the point is only that the two markers differ.

---

[] Reject

**Section "Numbers and Arithmetic" — `+=` on a list is the lookalike the chapter sets up and never cashes.**

"Variables and References" teaches that `b = a` aliases and that lists are
mutable. Two sections later, `total += 5` introduces augmented assignment
as "like other languages." Between them sits the one place where Python
differs sharply and where the earlier section's aliasing lesson is decided:
`x += [3]` mutates the list in place, so every other name for it sees the
change, while `x = x + [3]` rebinds and leaves the original alone. For an
`int`, both forms rebind. This is exactly the near-miss a reader coming
from C or Java writes without noticing.

Proposed change: add three lines to the end of `arithmetic.py`,

```python
items = [1, 2]
alias = items
items += [3]  # In place, so alias sees it
print(alias)
#: [1, 2, 3]
```

and one sentence after the listing: "Augmented assignment on a mutable
object changes it in place, so every other name for it sees the change;
`items = items + [3]` would instead build a new list and leave `alias`
alone." I recommend the listing over prose alone, since the point is about
what a second name observes and that needs the second name on screen.
Alternative placement: at the end of "Variables and References" rather than
here, which keeps the aliasing material together at the cost of using `+=`
before augmented assignment is named.

---

[] Reject

**Section "Booleans, None, and Truthiness" — no exercise or listing reaches `complex`, and the chapter promises "the scalar types".**

The opening promises "syntax and the scalar types here." The chapter covers
`int`, `float`, `bool`, `str`, and `None`. `complex` is a built-in scalar
type with literal syntax (`3+4j`) and it appears exactly once in the whole
book, in [Static Typing](08_Static_Typing.md)'s table of built-in type
names, where it is used without ever having been introduced.

Proposed change: one line in `arithmetic.py`,
`print((3 + 4j) * 1j)` with `#: (-4+3j)`, and half a sentence: "A trailing
`j` makes an imaginary literal, so `complex` is a built-in type too, though
this book does not use it further." Alternative: drop "scalar types" from
the chapter opening and say "the built-in numbers, strings, and `None`",
which is cheaper and equally honest. I mildly prefer the second.

---

[] Reject

**Section "t-Strings", lines 405-410 — the reason to care arrives after the machinery.**

The section opens on the `Template` object, walks its `strings` and
`interpolations` attributes, defines `shout()`, and only in the closing
paragraph says "The reason to care is safety rather than shouting." A
reader decodes three screens of API with no motive, and the `shout()` demo
is explicitly disowned as soon as the motive lands.

Proposed change: move the safety paragraph (lines 405-408) to immediately
after the section's opening paragraph, before the listing, so it reads:
f-string decides the text too early → a consumer that gets the parts
separately can quote, escape, or reject values → here is what the parts
look like. Keep the forward link to
[Composite and Interpreter](34_Composite_and_Interpreter.md#a-template-is-a-tree)
where it is, at the end. Price: none that I can find. The `{#t-strings}`
anchor is referenced from chapter 34 and stays put; no listing or term
moves.

---

[] Reject

**Section order inside "Strings" — "Common String Operations" is last, after the most advanced material.**

The order is Strings → f-Strings → t-Strings → Common String Operations.
`strip()`, `split()`, `join()`, and `in` are the simplest content in the
section and they sit behind `Template` iteration and `Interpolation`
objects. Read straight through, the difficulty curve rises for two
subsections and then drops off a cliff.

Proposed change: move `### Common String Operations` up so it directly
follows the `strings.py` material and precedes `### f-Strings`. Price:
nothing links to `#common-string-operations` from another chapter (checked
against `Chapters/` and `Solutions/`), and the only external anchor into
this part of the chapter is `#t-strings` from chapter 34, which is
unaffected. The one loss is that f-strings and t-strings stop being
adjacent to the plain-string introduction; they stay adjacent to each
other, which is the pairing that matters.

---

[] Reject

**Section "f-Strings", line 352 — the format spec claims three things and shows one.**

"The format spec after a colon controls width, precision, and alignment."
`fstrings.py` demonstrates precision (`:.0f`) only. A reader cannot write a
width or an alignment from this, and width-plus-alignment is the spec's
most common use in the kind of table-printing code this book writes later.

Proposed change: add one line to `fstrings.py`,

```python
print(f"|{name:>10}|{score:<8.1f}|")
#: |     Alice|91.5    |
```

and extend the sentence: "`>` right-aligns and `<` left-aligns within the
given width." Alternative: trim the claim to "controls precision and
formatting" and leave the listing alone, which is cheaper but leaves the
reader with less.

---

[] Reject

**Exercises — the set does not cover strings at all.**

Four exercises: references/aliasing, truthiness, f-strings, naming. The
chapter's two largest string subsections, t-Strings and Common String
Operations, get nothing, and t-Strings is the chapter's only genuinely
new-to-most-readers material.

Proposed change: add a fifth exercise against `tstrings.py`, for example:

```
5.  In `tstrings.py`, write a second consumer, `quoted(template)`,
    that wraps every interpolated value in single quotes and leaves
    the literal text alone, then print `quoted(message)`.
    Explain why an f-string cannot be post-processed the same way.
```

This needs a matching entry in `Solutions/02_Tour.md`, which is outside
this review's scope; the solution is a four-line variation on `shout()`.
Alternative, if a fifth exercise is too many: retarget exercise 3, which is
the lightest of the four, at `tstrings.py` instead of `fstrings.py`.

---

[] Reject

**Spellcheck flags "uppercases" (line 402) — a `tools/` change, not a chapter change.**

`uv run python tools/spellcheck.py Chapters/02_Tour.md` reports
`unknown word: "uppercases"`. The word is correct English and the sentence
is the right one; the dictionary is simply missing the inflection. This is
the only spellcheck hit in the chapter. `make spell` is not part of
`verify`/`gate`, so nothing is failing today, but the hit will recur on
every run.

Proposed change: add `uppercases` to `tools/data/wordlist.txt`. I did not
make this edit because `tools/` is out of scope for a chapter review.

---

## Cross-chapter

[] Reject

**`Chapters/08_Static_Typing.md`, line 517 — `complex` and `bytes` appear in a table without ever being introduced.**

The built-in-types row lists `int`, `str`, `float`, `bool`, `bytes`,
`complex`. Neither `bytes` nor `complex` is introduced anywhere in Part I;
chapter 02 covers the other four. This is only worth acting on if the
`complex` finding above is accepted in its first form (add a `complex`
line to `arithmetic.py`). If chapter 02 gains that line, no change is
needed in 08. If chapter 02 instead narrows its "scalar types" claim, then
08's table row is the reader's first encounter with both names and could
carry a parenthetical: "(`bytes` and `complex` are not used elsewhere in
this book)". I did not touch chapter 08.
