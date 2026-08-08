[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter order: the A/B/C/D comparison delays the chapter's payoff.**

Section: "Comparing Ordinary Classes and Data Classes" (and its four
subsections `A`, `B`, `C`, `D`), sitting between "Data Classes" and
"Immutability".

The chapter's claim is "a frozen data class turns a constraint into a type,
so the check runs once and can never be skipped."
That claim is set up by "A Value That Must Be Checked Everywhere" and
"A Class Is Not a Type", and it is cashed in by "A Type Is a Set of Values"
(`stars.py`).
Between the setup and the payoff sit about 200 lines of class-attribute
mechanics that do not move the claim forward at all: bare annotations vs.
class variables vs. generated fields vs. `ClassVar`.
The material is good, but it answers a question the reader has not asked yet.
Applying "motivation before mechanism," the reader is decoding
`show(D())` output with no reason to care.

Proposal: move the whole "Comparing Ordinary Classes and Data Classes"
section (through the end of "`D`: A Real `ClassVar`") to *after*
"A Type Is a Set of Values", or later still, after "Composing Types from
Types". The reader then meets it having already seen why a data class is
worth understanding in detail.

Price of the move, checked:

- No other chapter or Solutions file links to `#comparing-ordinary-classes-and-data-classes`
  or to any of the four subsection anchors. Only `#data-classes`,
  `#immutability`, `#a-type-is-a-set-of-values`,
  `#a-value-that-must-be-checked-everywhere`, `#composing-types-from-types`,
  `#enums-are-types-too`, `#dataclass-inheritance` and
  `#the-general-form-of-replace` are referenced from outside, and none of
  those move.
- `comparison.py` (`show()`) is used only by the four listings inside the
  section, so it travels with them.
- The section's opening sentence says "Four small classes make the
  differences concrete." After the move it would need to name the
  difference it is making concrete ("...the difference between a class body
  that declares fields and one that stores them").

Alternative, if you would rather not move it: leave it where it is but add
one sentence at the section head saying what it buys and that a reader in a
hurry can skip to "Immutability".

---

[] Reject

**"Defaults That Are Built, Not Shared" answers a question raised 200 lines
earlier.**

The question arises at the end of "When an `Enum` Beats a Data Class":

> `Months` carries a list of its twelve `Month`s,
> so its `months` field needs `field(default_factory=make_months)` rather than a default value,
> for reasons covered in [Defaults That Are Built, Not Shared](#defaults-built-not-shared).

The answer arrives six sections later, and that section then has to
re-establish the context it lost:

> `Months` in [When an `Enum` Beats a Data Class](#when-an-enum-beats-a-data-class)
> declares `months: list[Month] = field(default_factory=make_months)`.

That round trip (forward pointer, then a backward pointer to reconstruct the
example) is the standard tell that the section is in the wrong place.

Proposal: move "Defaults That Are Built, Not Shared" so it directly follows
"When an `Enum` Beats a Data Class". Then delete the forward link from
`Months`'s paragraph (the next section answers it immediately) and open the
moved section with "`Months` declares ..." instead of the re-establishing
sentence with the backward link.

Price: nothing external. The section carries an explicit
`{#defaults-built-not-shared}` anchor, so the anchor survives the move, and
grep shows the only reference to it is the one inside this chapter.
The section's own outbound link to
`[Functions](05_Functions.md#default-and-keyword-arguments)` is unaffected.

---

[] Reject

**`stars_unchecked.py`: `f1(6)` returns 11, and the prose walks past it.**

Section: "A Value That Must Be Checked Everywhere".

```python
print(f1(rating))
#: 11
```

`f1()` is one of the two *checked* functions, and it hands back 11: a value
that would be rejected as a rating anywhere else in the listing, and the
exact literal `f3()` is called with two lines later.
The prose blames only `f3()` ("`f3()` is what forgetting looks like"), so
the stronger point goes unmade: checking the argument does nothing about
the result. That is precisely what `stars.py` fixes later
("They do not test their result, because building the returned `Stars` runs
the check") and what `stars_class.py`'s postcondition exists for.

Proposal: add one sentence after "The `int` annotation says 'any integer,'
which is not what you mean.":

> Checking the argument also says nothing about the result:
> `f1(6)` returns 11, which no rating may be.

Also consider dropping `print(rating)` / `#: 6` from the listing. It shows
nothing and costs the reader a line.

---

[] Reject

**Design by Contract is described without its third clause, the invariant.**

Section: "A Class Is Not a Type".

> Checking arguments on the way in and results on the way out is the practice
> known as *Design by Contract* (DbC).

DbC is preconditions, postconditions, *and* class invariants, and the
invariant is the one this whole chapter is about: `1 <= number <= 10` is a
class invariant, and `_validate()` is a hand-rolled invariant check that
each method must remember to call.
Naming it would let the closing line land harder.

Proposal: extend the definition to "...on the way out, with a class
invariant that must hold between calls, is the practice known as *Design by
Contract* (DbC)", and add after "the contract is spread across every method
that touches the value":

> The invariant is the part this chapter replaces.
> `_validate()` states it, and every mutating method has to remember to call it.

---

[] Reject

**`check_day()` breaks the `subject`/`reason` contract the chapter just
defined.**

Section: "Enums Are Types Too" (`birth_date.py`), repeated in "When an
`Enum` Beats a Data Class" (`month_dataclass.py`).

The opening section defines the two fields precisely:

> `subject` is the rejected value as the caller rendered it, such as `Stars(11)`.
> `reason` explains the rejection when the name alone does not, such as `needs an @`.

But `check_day()` passes an entire explanatory sentence as `subject` and
leaves `reason` empty:

```python
    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days,
              f"{self.name} has no day {day.n}")
```

Confirmed at runtime: `e.subject == 'FEBRUARY has no day 31'`, `e.reason == ''`.
A handler reading `e.subject` for the rejected value gets prose.
`EmailAddress` and `FullName` in `person.py` follow the contract, so the two
uses disagree inside one chapter.

Recommended fix (both files):

```python
    def check_day(self, day: Day) -> None:
        check(day.n <= self.max_days, f"Day({day.n})",
              f"is past the end of {self.name}")
```

Alternative if you prefer the current wording of the message: keep the
sentence but move it into `reason` and render the value in `subject`,
`check(..., f"Day({day.n})", f"{self.name} has no day {day.n}")`, which is
slightly redundant but preserves the exact text.

Third alternative: loosen the definition at the top of the chapter to say
`subject` is "the rejected value, or the smallest phrase that identifies
it." I recommend against this one; the precise definition is what makes
`e.subject` useful.

No `#:` markers change either way. `check_day` failures are only exercised
through `pytest.raises(TypeFailure)`, with no message assertion, and
`month_dataclass.py`'s `check_day` is never called from its demo.
`month_dataclass.py` has the same issue one line earlier in
`check(self.max_days in (28, 30, 31), f"max_days {self.max_days}")`, which
would become `f"Month(max_days={self.max_days})"` plus a reason.

---

[] Reject

**The `NamedTuple` claim is stronger than the mechanism supports, and the
hole is more interesting than the claim.**

Section: "A `NamedTuple` Cannot Validate Itself".

> `typing.NamedTuple` forbids overriding the methods that build an instance,
> so validation must live in a factory function beside the type,
> where a caller can go around it.

A reader who knows the two-class workaround will object, and it does work:

```python
class _Stars(NamedTuple):
    number: int

class Stars(_Stars):
    def __new__(cls, number: int) -> Stars:
        check(1 <= number <= 10, f"Stars({number})")
        return super().__new__(cls, number)
```

`Stars(11)` now raises. But the guarantee still leaks, and that is the
better lesson. `_replace()` builds through `tuple.__new__` rather than
`cls.__new__`, so it skips the check entirely, and `copy.replace()` goes
through `_replace()`:

```
>>> s = Stars(5)
>>> s._replace(number=99)
Stars(number=99)
>>> copy.replace(s, number=99)
Stars(number=99)
```

Both confirmed on the pinned 3.15.

Proposal: after "because a factory function is advice rather than a gate,"
add a short paragraph:

> Subclassing the `NamedTuple` and defining `__new__()` on the subclass gets
> past the prohibition, and moves the hole rather than closing it.
> `_replace()` rebuilds through `tuple.__new__()`, not through your
> `__new__()`, so `copy.replace()` on a validated instance quietly produces
> an unvalidated one. A frozen data class has no such back door:
> `copy.replace()` runs the constructor, which runs `__post_init__()`.

That last sentence also ties the section to "The General Form of
`replace()`", which currently makes exactly that point about data classes
with nothing to contrast it against.

If you would rather not add the paragraph, at minimum soften "validation
must live in a factory function beside the type" to "validation has to live
outside the class body."

---

[] Reject

**`Month(7)` does not work, and the reader will try it.**

Section: "Enums Are Types Too".

The chapter explains carefully why each member is a `(number, days)` pair
(equal values become aliases) but does not say what that costs: the natural
`Month(7)` lookup by value now raises
`ValueError: 7 is not a valid Month`, which is why `of()` exists at all.
A reader who has seen `Color(1)` work in other enum examples will write
`Month(7)`, get an exception, and not connect it to the paragraph two
listings up.

Proposal: add one sentence to the paragraph that explains the pairs:

> The cost is that the member's value is no longer the month number, so
> `Month(7)` raises `ValueError`. `of()` is the replacement lookup.

---

[] Reject

**The attrs/Pydantic paragraph is in the wrong section.**

Section: end of "When an `Enum` Beats a Data Class".

The section argues Enum-vs-data-class and closes correctly with "Choose the
tool that makes the legal set easiest to express. For a small fixed set,
that is an `Enum`." Then a paragraph about validation libraries appears,
which has nothing to do with the Enum comparison. It is a good paragraph
attached to the wrong argument.

Proposal: move it to the end of "Composing Types from Types", where the
chapter has just finished showing hand-written `__post_init__` validation
and the reader is best placed to wonder what happens when the checks get
big. A second reasonable home is the "Where the Checks Went" conclusion,
next to the sentence about the edges of the program, since Pydantic's
selling point is exactly that boundary.

---

[] Reject

**No mention of `slots=True` in the chapter that teaches frozen data
classes.**

Sections: "Immutability", "More Data Class Tools".

`slots=True` is covered in [Performance](18_Performance.md), six chapters
later, including the fact that "`frozen=True` does not imply
`slots=True`". A reader building the validated types this chapter
recommends will make many small immutable objects, which is exactly the
case `slots=True` is for, and nothing here points at it.

Proposal: one forward link at the end of "Immutability":

> A frozen data class still carries a per-instance `__dict__`. Adding
> `slots=True` drops it, for less memory and faster attribute access;
> [Performance](18_Performance.md#... ) measures the difference.

Deliberately a pointer, not a treatment: the measurement belongs in
chapter 18.

---

[] Reject

**Exercise set: uneven coverage, and exercise 3 largely reproduces a
listing the chapter already contains.**

Section: "Exercises".

Coverage against the chapter's sections:

| Section | Exercise |
| --- | --- |
| A Type Is a Set of Values | 3, 6 |
| Composing Types from Types | 2 |
| Enums Are Types Too | 1 |
| Serializing to JSON | 4 |
| The General Form of `replace()` | 5 |
| Comparing Ordinary Classes / A-B-C-D | none |
| A `NamedTuple` Cannot Validate Itself | none |
| Inheritance and the Generated `__init__` | none |
| Defaults That Are Built, Not Shared | none |

Exercise 3 asks the reader to rewrite `stars_class.py`'s `Stars` as a frozen
data class, but `stars.py` in "A Type Is a Set of Values" is already that
rewrite. The only new work is turning the free function `f1()` into a
method. Either say so explicitly ("`stars.py` does this with free
functions; do it with a method instead, and ...") or replace it.

Proposal: replace exercise 3 with one that covers an uncovered section, and
add one more. Two candidates:

- Take `test_namedtuple_no_hook.py`'s `Stars` and make the subclass
  workaround (`class Stars(_Stars)` with `__new__`). Show that
  `Stars(11)` now raises but `copy.replace(Stars(5), number=99)` does not,
  then explain why the frozen data class has no equivalent hole.
- Give `Months` a second field with a `dict` default written as
  `= {}` and read the error; then fix it two ways, with
  `default_factory=dict` and with `default_factory=dict[str, Month]`, and
  say which one a checker can verify.

Note that `Solutions/12_Data_Classes_as_Types.md` exists and would need the
matching change; I did not touch it.

---

[] Reject

**`copy_replace_protocol.py`: `SHIFTS` names the shifts, then `__init__`
hardcodes them again.**

Section: "The General Form of `replace()`".

```python
SHIFTS: Final[dict[str, int]] = {"red": 16, "green": 8, "blue": 0}
...
    def __init__(self, red: int, green: int, blue: int) -> None:
        self.packed = (red << 16) | (green << 8) | blue
```

The three shift amounts appear twice, once as a named constant and once as
literals, and a reader working out what `SHIFTS` is for has to notice that
`__init__` does not use it. Not a bug, but the listing is teaching
`__replace__()` and this is a second, unrelated thing to work out.

Proposal:

```python
    def __init__(self, red: int, green: int, blue: int) -> None:
        channels = {"red": red, "green": green, "blue": blue}
        self.packed = sum(v << SHIFTS[k] for k, v in channels.items())
```

which also makes `__init__` and `channels` visibly inverse.
If that reads as too clever for the point being made, the simpler fix is to
drop `SHIFTS` from `__init__`'s concern by leaving the literals and adding
nothing: the current code is fine, it is only the unexplained near-duplication
that costs the reader.

---

[] Reject

**`dataclass_features.py` teaches three unrelated features in one listing.**

Section: "More Data Class Tools".

`asdict()`/`astuple()`, recursion into a nested list of data classes, and
`KW_ONLY` are three separate ideas in one block, with three separate
classes (`Point`, `Line`, `Config`).
Against "one new thing per listing" this is the chapter's clearest case.

Proposal: split at the `Config` boundary, into a listing for
`asdict()`/`astuple()` (`Point` and `Line`) and a listing for `KW_ONLY`
(`Config`), with the prose I added about the ordering rule attached to the
second. Low priority: this is a reference section and the reader is not
being asked to build an argument out of it.

---

[] Reject

**Small wording items.**

1. Line 9, chapter opening: "Checks to defend against the mess become
   scattered throughout your code." "The mess" has no antecedent yet, and
   "become scattered" hides who does the scattering. Suggest: "Defensive
   checks then spread through your code."

2. "A *data class* writes the boilerplate for a class that holds data."
   A data class does not write anything; the decorator does, and the next
   sentence says so. Suggest: "A *data class* removes the boilerplate from a
   class that holds data."

3. "Four small classes make the differences concrete, and add some insight
   to [Class Attributes](09_Class_Attributes.md)." A listing cannot add
   insight to a chapter. Suggest: "...and go further than
   [Class Attributes](09_Class_Attributes.md) did."

4. "This is one aspect of functional programming (see
   [Foundations](40_Functional_Foundations.md#immutability))." Every other
   cross-reference in the chapter uses the chapter's real title. Suggest
   "[Functional Foundations]".

---

## Cross-chapter

Nothing in this chapter requires a change to another chapter. Two
observations that touch chapters I did not edit, recorded so the ends of
those threads stay consistent:

- **Chapter 18 (Performance).** The `slots=True` proposal above would add a
  forward link from chapter 12 into
  `18_Performance.md`. Chapter 18 already says "`frozen=True` does not imply
  `slots=True`", so if the link is added, chapter 18's sentence would read
  better as a callback ("as [Data Classes as Types] noted"). I did not make
  that edit. The chapter-18 anchor to link to would need choosing; the
  `slots=True` discussion there starts around its line 764 and does not
  currently sit under a heading with a stable id.

- **Chapter 22 (Data Transfer Objects).** Chapter 12's `NamedTuple` finding
  above (the subclass workaround, and `_replace()` bypassing it) is
  relevant to 22's `NamedTuple`-vs-frozen contrast, which currently
  distinguishes them only by equality semantics and by validation.
  If the paragraph is added to 12, chapter 22 needs no change, but its
  "A `NamedTuple` Is Still a Tuple" section is where a reader would look
  for the `_replace()` hole. No edit made.
