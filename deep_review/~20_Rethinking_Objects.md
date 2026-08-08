[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**"The four OOP promises" is a numbered list the chapter never announces.**

Section: the seam between "The Liskov Substitution Principle" and
"Encapsulation Leaks" (and then the openings of "Methods or Functions?",
"Prefer Composition to Inheritance", and "Polymorphism Without Inheritance").

The chapter's spine is four numbered promises: encapsulation, methods,
reuse through inheritance, polymorphism. But the first the reader hears of a
list is the sentence "The first OOP promise is encapsulation," arriving cold
after an LSP section that talked about neither promises nor a count. Each
later section then re-establishes its place in a list the reader was never
handed ("The second...", "The third...", "The fourth..."). A reader who is
told up front that four claims are about to be taken in turn reads each
section as a step in an argument; without it, the ordinals read as a tic.

The LSP section also ends abruptly. `lsp_violation.py` lands, three sentences
explain it, and the next line is a new `##` heading on an unrelated subject.
One paragraph fixes both problems at once.

Proposal: add a closing paragraph to "The Liskov Substitution Principle",
after "The subclass matched the signature and broke the contract behind it.":

> Substitutability is only the first crack.
> OOP made four promises: encapsulation, behavior bundled into the object as
> methods, reuse through inheritance, and polymorphism.
> The next sections take them one at a time,
> and ask in each case what Python actually delivers and what it costs.

Cost: none to anchors or cross-references. `25_Template_Method.md` and
`29_Changing_the_Interface.md` link to `#liskov-substitution`, and the
heading does not change. Alternative, if you would rather not spend a
paragraph: put "OOP made four promises. This is the first." into the opening
line of "Encapsulation Leaks" and leave LSP alone. I prefer the first
version because it also gives LSP an ending.

---

[] Reject

**"They let code live outside classes, which reduces duplication" states the
consequence and drops the reason.**

Section: "Evolution", the paragraph on Rust/Swift/Go/Kotlin.

Why does letting code live outside a class reduce duplication? The reader has
to supply the missing step: a free function serves every type that fits,
where a method has to be written again on each class that needs it. That step
is exactly what the rest of the chapter is about ("Methods or Functions?",
"Protocols Generalize"), so the sentence is a free forward reference being
left on the table.

Proposal: replace the sentence with

> They let code live outside classes,
> so one function can serve many types instead of being rewritten as a method
> on each.

---

[] Reject

**"Two quiet changes in the listing" names neither change for thirty lines.**

Section: "The Immutability Solution", the paragraph beginning "Two quiet
changes in the listing do as much work as `frozen=True`."

The sentence sets up a question ("which two?") and the answer arrives after
the shallow-freezing explanation and the whole of `frozen_leaky.py`: "That is
why `numbers` became a `tuple` and `Bob` was also frozen." That is a long
hold for a small reveal, and the reader spends `frozen_leaky.py` half-looking
for the answer instead of reading the listing.

Proposal: name them in the setup sentence and let the rest of the passage
explain why they were needed:

> Two quiet changes in the listing do as much work as `frozen=True`:
> `numbers` is a `tuple`, not a `list`, and `Bob` is frozen too.

Then change the payoff line "That is why `numbers` became a `tuple` and `Bob`
was also frozen." to "That is why those two changes were needed."

This is a pacing call, so it is yours: if the delayed reveal is deliberate,
reject and the passage still works.

---

[] Reject

**"Prefer Composition to Inheritance" breaks `CountingList` and then never
fixes it.**

Section: "Prefer Composition to Inheritance", between `counting_list.py` and
`composition.py`.

`counting_list.py` shows a concrete failure: subclass `list`, override
`append()`, and `extend()` walks straight past your counter. The prose
diagnoses it well. Then the section says "Before inheritance, there was
composition" and shows `composition.py`, which is `Contact`/`Name`/`Address`
value composition. That is a good listing for a different point. It does not
answer the question `counting_list.py` just raised, which is: *so how do I
count appends?*

The composition answer is delegation, and it is three lines: hold a list
instead of being one, and expose only what you meant to expose.

Proposal: insert a listing between the two, with prose:

```python
# counting_box.py
from dataclasses import dataclass, field

@dataclass
class CountingBox:
    items: list[int] = field(default_factory=list)
    appends: int = 0

    def append(self, item: int) -> None:
        self.appends += 1
        self.items.append(item)

    def extend(self, more: list[int]) -> None:
        for item in more:
            self.append(item)

box = CountingBox()
box.append(1)
box.extend([2, 3])
print(len(box.items), box.appends)
#: 3 3
```

> `CountingBox` holds a list instead of being one.
> Nothing arrives from a base class, so nothing can slip past the counter:
> the only way into `items` is a method this class wrote.
> The cost is visible and finite.
> Every operation callers need has to be forwarded by hand,
> where the subclass got hundreds for free and got one of them wrong.

Note the marker is `3 3`, against `counting_list.py`'s `3 1`, which makes the
contrast the point of the pair. I verified the listing runs, type-checks, and
lints at width 70. Placement is yours: it could also go after
`composition.py`, though it reads better as the immediate answer.

Alternative, if you would rather not add a listing: add a sentence after
"...no checker reports." saying that the composition fix is to hold a list
rather than be one, forwarding the operations you actually want. That is
cheaper but the reader does not see the `3 3`.

---

[] Reject

**The failure `counting_list.py` demonstrates is never named.**

Section: "Prefer Composition to Inheritance", the paragraph after
`counting_list.py`.

"It inherited an implementation and now depends on how that implementation is
written" is a precise description of the *fragile base class problem*, which
is the term the reader will meet everywhere else. The chapter names LSP, the
diamond problem, the Adapter, and the Null Object; this one goes unnamed, and
a reader who later hears "fragile base class" will not connect it back.

Proposal: end that paragraph with

> This is the *fragile base class* problem:
> a base class cannot change its own internals without risking every subclass
> that came to depend on them.

---

[] Reject

**`composition.py` teaches five things at once.**

Section: "Prefer Composition to Inheritance", `composition.py`.

The listing introduces composition, `dataclasses.replace()`, *nested*
`replace()`, value equality, and hashability/dict-key use, in one block with
five markers. Every one of them is worth teaching, but the "one new thing per
listing" test fails badly here: the reader who is still absorbing "a `Contact`
holds a `Name` and an `Address`" is asked to also parse a nested `replace()`
call broken across two lines.

Proposal: split it. Keep composition plus the equality/hash payoff in
`composition.py` (the two things the prose calls "the payoff"), and move the
`replace()` half into its own short listing with its own paragraph, since the
copy-with-changes cost is a separate argument. Alternatively, cut the
`replace()` half from this chapter entirely and rely on
[The General Form of `replace()`](12_Data_Classes_as_Types.md#the-general-form-of-replace),
which chapter 12 already covers, keeping one sentence here to point at it.
I lean toward the second: this chapter is arguing composition-over-inheritance,
and `replace()` is chapter 12's material being re-run.

---

[] Reject

**The `### Protocols` subsection carries six topics under one heading.**

Section: "Polymorphism Without Inheritance" → "Protocols".

Under one `###` heading the reader gets: `protocols_typed.py`, the
nominal-vs-structural comparison, multiple protocols and the diamond problem
(`multi_protocol.py`), the name-collision blind spot
(`protocol_collision.py`), `NewType` (`newtype_boundary.py` plus its test),
and the protocol-vs-LSP semantic-half argument. That is most of the chapter's
best material sitting where a reader scanning headings will not find it, and
`newtype_boundary.py` in particular is not about protocols at all.

Proposal: add a `#### What the Shape Does Not Say` (or similar) heading
immediately before "That same structural check has a blind spot," so the
collision → `NewType` → semantic-half arc reads as its own unit.

Cost, checked: `23_Iterators.md:631` links to
`20_Rethinking_Objects.md#protocols`. A new `####` after it does not move or
rename that anchor, so the link still resolves. Using `####` rather than
`###` keeps the new heading out of the top-level structure that other
chapters point into.

---

[] Reject

**"What Is Polymorphism?" defines the word after four sections have used it.**

Section: "What Is Polymorphism?", currently between "Polymorphism Without
Inheritance" and "Null Object".

The chapter announces "The fourth OOP promise is polymorphism," then spends
four subsections showing ABCs, dynamic typing, protocols, and pattern
matching, and only then asks what polymorphism actually is and hands over the
parametric / ad-hoc / subtype taxonomy. This is the classic
where-the-question-arises-versus-where-it-is-answered gap: the reader wants
the definition at the top of the promise, not at the bottom.

Proposal: move "What Is Polymorphism?" (including `overload_example.py` and
the `singledispatch` paragraph) to sit immediately *after* the one-line
"The fourth OOP promise is polymorphism." and before `### Abstract Base
Classes`, demoting it to a `###` subsection of "Polymorphism Without
Inheritance". The reader then meets the three kinds first and reads the four
listings as instances of them.

Price of the move, checked:

- `32_Multiple_Dispatching.md:19` links to `#what-is-polymorphism`. Moving a
  section does not change its slug, so the link survives; demoting `##` to
  `###` also leaves the slug alone. Verify with `heading_links.py`.
- The paragraph "*Subtype polymorphism* was demonstrated in [Polymorphism
  Without Inheritance](#polymorphism-without-inheritance)" becomes a
  self-reference and must be reworded to point forward, e.g. "*Subtype
  polymorphism* is what the next four listings show."
- The forward links to `08_Static_Typing.md#generic-functions-and-classes`
  and `33_Visitor.md#the-pythonic-visitor-singledispatch` are unaffected.
- Cheaper alternative if the move is too disruptive: leave the section where
  it is and add one sentence under "The fourth OOP promise is polymorphism."
  saying that the word covers three distinct things and that
  [What Is Polymorphism?](#what-is-polymorphism) sorts them out at the end of
  the section. That closes the gap by telling the reader the answer is
  coming, which is the minimum the lens asks for.

---

[] Reject

**`Loggable` and `Logs` are two logging-shaped protocols in one chapter, and
neither is about the other.**

Sections: `multi_protocol.py` (defines `Loggable`, whose method is
`describe()`) and `null_logger.py` (defines `Logs`, whose method is `log()`).

`Loggable` reads as "can be logged" but is really "can describe itself," and
it appears roughly 250 lines before `Logs`, which really is about logging.
The chapter's other protocol names are all clean (`Coord`, `Displayable`,
`Priced`, `Serializable`, `Weighted`), so this pair is the one place a reader
could flip back and think the two are related.

Proposal: rename `Loggable` to `Describable` in `multi_protocol.py`, its
`audit()` parameter annotation, and the prose sentence "Nothing forces
`Invoice` below to acknowledge `Priced`, `Serializable`, or `Loggable`." No
other chapter references `Loggable`; I checked. `Logs` then stands alone and
`describe()` gets a name that matches what it does.

---

[] Reject

**Exercise 2 asks the reader to re-derive `frozen_leaky.py`.**

Section: "Exercises", exercise 2.

Exercise 2 is: change `numbers: tuple[int, ...]` to `list[int]`, run
`ty check`, notice it does not object, demonstrate the leak with `append()`,
restore the tuple. `frozen_leaky.py`, forty lines earlier in the same
chapter, is that exercise already worked. The closing question ("Who, then,
is responsible for making immutability go all the way down?") is the part
that earns its place.

Proposal: keep the closing question and change the work to something the
chapter did not already do. Since the prose now says a frozen data class
holding a list is unhashable, the natural version is:

> 2. In `immutable.py`, change `numbers: tuple[int, ...]` to `list[int]`.
>    Show that `ty check` still passes, that `append()` works, and that
>    `hash(immutable)` now raises, so the frozen instance can no longer be a
>    dict key. Restore the `tuple`.
>    Who, then, is responsible for making immutability go all the way down?

Note this needs a matching edit to
`Solutions/20_Rethinking_Objects.md`, section "2. A mutable field in a frozen
data class", which I did not touch.

---

[] Reject

**Three sections have no exercise, and one of them is the chapter's title
argument.**

Section: "Exercises".

Mapping the six exercises onto the chapter: 1 → Encapsulation Leaks /
Plugging Leaks, 2 → The Immutability Solution, 3 → protocol collision +
`NewType`, 4 → Protocols Generalize, 5 → Pattern Matching on a Union, 6 →
Null Object. Nothing exercises "The Liskov Substitution Principle", nothing
exercises "Methods or Functions?", nothing exercises "Prefer Composition to
Inheritance", and nothing exercises the polymorphism taxonomy or `@overload`.
Four of the six cluster on the protocol/immutability half. The
composition-over-inheritance gap matters most: it is the chapter's loudest
guideline and the reader never has to do it.

Proposal: add two, and consider dropping nothing (six to eight is still
reasonable for a chapter this size):

> 7. In `counting_list.py`, add a `__setitem__` count as well, then find a
>    second `list` method that changes the contents without going through
>    either override. Rewrite `CountingList` to hold a list instead of
>    inheriting from one, and show that the counts are now correct for every
>    route in.
> 8. In `lsp_violation.py`, make `BoundedStack` obey the Liskov Substitution
>    Principle without removing the limit: keep the base contract that
>    `push()` always succeeds, and expose "full" some other way. Then say
>    what you gave up, and whether `BoundedStack` should have been a subclass
>    of `Stack` at all.

Both need matching entries in `Solutions/20_Rethinking_Objects.md`, which I
did not touch.

---

[] Reject

**Optional: demonstrate the unhashability claim instead of asserting it.**

Section: "The Immutability Solution", `frozen_leaky.py`.

I added prose stating that `hash(fl)` raises a `TypeError` and that a
`FrozenLeaky` cannot be a dict key. Chapters 3, 12, and 22 all make that same
claim and all three cite *this* section as the place it is demonstrated, so
the listing is arguably the right home for it:

```python
try:
    hash(fl)  # A list field makes the whole instance unhashable
except TypeError as e:
    print(type(e).__name__)
#: TypeError
```

appended after the existing `FrozenInstanceError` block.

I left the listing alone deliberately: `frozen_leaky.py`'s frozen-is-shallow
demonstration is depended on by chapters 22, 35, and 36, and adding to it is
your call rather than mine. Adding the block does not disturb those
references (they cite the section anchor, not line numbers), and I confirmed
the behavior on the pinned 3.15: `hash(FrozenLeaky([1, 2]))` raises
`TypeError: unhashable type: 'list'`.

---

[] Reject

**The LSP definition simplifies parameters and returns in a way a careful
reader will trip on.**

Section: "The Liskov Substitution Principle", the sentence "An override
accepts the same arguments, returns the same kinds of results, and raises no
surprising exceptions."

LSP as usually stated is looser in both directions: an override may accept
*more* than the base (contravariant parameters) and return *less*
(covariant returns), and `@override` in Python enforces exactly that
asymmetry, which is why `29_Changing_the_Interface.md:127` says that
*narrowing* what a method accepts breaks substitutability. A reader who takes
"the same arguments" literally and then reads chapter 29 has a small
contradiction to resolve.

Proposal: loosen the sentence to match:

> An override may accept more than the base does but never less,
> returns a result the caller can use where the base's result was expected,
> and raises no surprising exceptions.

Low priority. The current wording is a fine first approximation and the
chapter is not a type-theory chapter; reject if you would rather keep the
short version.

## Cross-chapter

Nothing in another chapter needs to change. Two things checked and cleared:

- `03_Containers.md:584`, `12_Data_Classes_as_Types.md:493`, and
  `22_Data_Transfer_Objects.md:136` all cite
  `20_Rethinking_Objects.md#the-immutability-solution` as demonstrating that
  a frozen record holding a list is *unhashable*, and that section did not
  say so. Rather than change those three, I added the missing sentence to
  chapter 20, which is the end all three point at. No edit is needed
  elsewhere.
- Every `##` heading in this chapter is linked from at least one other
  chapter (13, 21, 23, 24, 25, 29, 32, 34, 35, 36, 39, 40, 44 between them
  cover `#liskov-substitution`, `#encapsulation-leaks`,
  `#the-immutability-solution`, `#protocols-generalize-composition-adapts`,
  `#prefer-composition-to-inheritance`, `#polymorphism-without-inheritance`,
  `#protocols`, `#what-is-polymorphism`, `#null-object`, `#guidelines`). No
  heading in this review is renamed, and the one proposed move (finding on
  "What Is Polymorphism?") preserves its slug.

## Note on the deep-review skill (not a chapter finding)

`.claude/skills/deep-review/SKILL.md`'s accrued notes say "the registry
factory's import-time-registration and name-collision caveats live in 27 and
back the registries in 20/37". Chapter 20 contains no registry; the word
appears nowhere in it. That half of the note looks stale, probably from a
renumber. Chapter 37's registry is real. [[fix this]]
