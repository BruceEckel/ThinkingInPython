[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Opening section, lines 62-71: "You do not declare them this way in Python" is
still too broad after the fix I applied.**

I already changed "If you declare fields using the C++/Java style, they
implicitly become class-level fields" to "If you assign to a name in the class
body, C++/Java style, that name becomes a class-level field instead", because
the original was flatly wrong for the annotation-only form. What remains
unaddressed is the sentence two lines above it: "In C++ or Java you declare
object-level fields inside the class body but outside of the methods. You do
not declare them this way in Python."

A reader from Java will write `radius: float` in the class body, which is
correct modern Python and is exactly how chapter 9's `Tally` (`label: str`) and
every `@dataclass` field in chapter 12 declare per-instance state. It stores
nothing on the class, so it is not the trap this paragraph is warning about,
but the paragraph tells them it is.

Proposed change: after "shows what that shared storage does when you assign to
it.", add

> A bare annotation with no value,
> the form that does look like a C++ or Java field declaration,
> is a third thing again:
> it stores nothing anywhere and only records the type.
> [Class Attributes](09_Class_Attributes.md#declaring-shared-state-with-classvar)
> and [Data Classes as Types](12_Data_Classes_as_Types.md#data-classes) use it.

[[OK, but this is awkward:
> is a third thing again:
> it stores nothing anywhere and only records the type.
]]

Alternative, if that is too much machinery for chapter 7 (annotations are not
introduced until chapter 8): drop the added sentence and instead soften
"You do not declare them this way in Python" to "Assigning them this way in
Python does something different." I recommend the first version, because the
reader who is going to make this mistake makes it immediately, not after
chapter 9.

---

[] Reject

**Line 74: the deep link points at the wrong subsection.**

`a small inspection helper built in
[Metaprogramming](17_Metaprogramming.md#the-inspect-module)` lands the reader on
`## The `inspect` Module`, a general tour of `inspect`. The helper is actually
built in the subsection `### Building `display_object()`` (chapter 17,
line 1105), whose anchor is `#building-display_object`. Chapter 17's own
opening links to it that way.

Proposed change: `17_Metaprogramming.md#the-inspect-module` →
`17_Metaprogramming.md#building-display_object`.

I did not apply this because chapter 12 uses the identical wrong anchor and the
two should change together. See the Cross-chapter section at the end.

---

[] Reject

**Line 112: "multiple inheritance" is named and then never resolved.**

"(or classes, since Python supports multiple inheritance)" is the only place in
the book that offers multiple inheritance to the reader as something they might
do. There is no section on it anywhere. The nearest treatment is chapter 20's
one-paragraph diamond-problem aside, which exists to argue *against* it, and
chapter 17's metaclass-layout corner case. A reader who takes the parenthetical
at face value has nowhere to go.

Proposed change: extend the parenthetical to close the loop:

> (or classes, since Python supports multiple inheritance,
> which [Rethinking Objects](20_Rethinking_Objects.md) argues against
> in favor of protocols)

That is honest about the book's position and gives the term a destination. The
alternative is to drop the parenthetical entirely; I prefer the link, since
readers coming from C++ will ask.

---

[] Reject

**Lines 197-212: `override_intro.py` demonstrates only the case where nothing
goes wrong.**

The section's whole argument is that `@override` catches a typo or a renamed
base method. The listing shows a correct override, and its output,
`Derived.show`, is what you get with or without the decorator. The reader never
sees the error, so the listing carries none of the teaching; the prose after it
carries all of it.

The book already has an idiom for this: a commented-out line with the checker's
complaint next to it (chapter 8 line 187, chapter 9 line 133, chapter 17
line 478, chapter 27 line 589). Proposed change to the listing:

```python
# override_intro.py
from typing import override

class Base:
    def show(self):
        print("Base.show")

class Derived(Base):
    @override
    def show(self):
        print("Derived.show")

class Typo(Base):
    # @override  # "shwo" does not override anything
    def shwo(self):
        print("Typo.shwo")

Derived().show()
#: Derived.show
```

I confirmed under `ty` 0.0.65 that uncommenting the decorator produces
`error[invalid-explicit-override]: Method "shwo" is decorated with @override
but does not override anything`, and that leaving it commented keeps the
listing green under `ty`, `ruff`, and `validate_output.py`.
I left this as a proposal rather than applying it because it adds a class to
the chapter's smallest listing, which is a pacing call.

A cheaper variant, if the extra class is unwelcome: keep the listing as is and
add one sentence after "the checker reports an error", naming the diagnostic
the reader will see.

---

[] Reject

**Line 223: "It sets an `__override__` attribute on the method" overstates
what CPython does.**

`typing.override` in 3.15 is:

```python
try:
    method.__override__ = True
except (AttributeError, TypeError):
    # Skip the attribute silently if it is not writable.
    pass
return method
```

It *attempts* the assignment and swallows the failure for anything with
`__slots__`, a read-only property, or a builtin. That does not affect the
chapter's listing (a plain function always accepts it), but the sentence as
written invites introspection code that assumes the attribute is always there.

Proposed change: "It sets an `__override__` attribute" → "It tries to set an
`__override__` attribute (some callables refuse it)".

---

[] Reject

**Line 233: the Properties section promises a conversion it never shows.**

"You can expose a plain attribute and convert it to a computed one later,
without changing the calling code, using `@property`" is the section's thesis
and its selling point. `properties.py` then shows `radius` staying plain and
`area` being computed from birth. Nothing converts. The conversion does happen
in `property_setter.py`, on a *different* `Circle` that has quietly dropped
`area`, and the prose never connects the two.

 Restructure so one `Circle` runs through the section: plain `radius` and
   computed `area` first, then the same class with `radius` promoted to a
   property, keeping `area`. This makes the point far better but costs a
   rewritten second listing and its output markers.


---

[] Reject

**Lines 335-338: cached_property staleness is asserted, not demonstrated.**

"`cached_property` trades freshness for speed, so if `n.values` changes,
`total` becomes stale" is the one thing about `cached_property` a reader can
get burned by, and it is the one thing the listing does not show. Chapter 41
does show it (`x.n = 10  # Doesn't change the cached result`), but chapter 41 is
a reference tour and chapter 7 is where the reader learns the feature.

Proposed change: append to `cached_property_demo.py`

```python
n.values.append(20)
print(n.total)  # Still the old sum: the cache is stale
#: 30
del n.total  # Discard the cached value
print(n.total)
#: summing 4 values
#: 50
```

and cut "`del n.total` discards it, and the next access recomputes." from the
prose above, since the listing then says it. Verified: the output above is what
runs. This makes the listing the longest in the section, which is why it is a
proposal rather than an applied change.

---

[] Reject

**Properties section: `cached_property` silently requires an instance
`__dict__`.**

Nothing in the section says the cache is stored in `self.__dict__`, so a reader
who later meets `__slots__` (chapter 20's `@dataclass(frozen=True, slots=True)`,
which the book recommends) or a frozen dataclass will hit

```
TypeError: No '__dict__' attribute on 'S' instance to cache 'sq' property.
```

with no idea why. The chapter already says "The stored value lives on the
instance", which is the right hook.

Proposed change: extend that sentence to
> The stored value lives in the instance's `__dict__`,
> so a class that suppresses that dictionary, as
> [Rethinking Objects](20_Rethinking_Objects.md) does with `slots=True`,
> cannot use `cached_property`.

Frozen dataclasses fail for a second reason (the blocked `__setattr__`), which
I would not mention here.

---

[] Reject

**Lines 436-438: the `@dataclass` pointer sits in the wrong section.**

"For classes that are primarily a bundle of typed data, [Data Classes as
Types](12_Data_Classes_as_Types.md#data-classes) shows how `@dataclass` writes
the constructor and `__repr__()`" is the chapter's only acknowledgement that
almost every listing in it hand-writes what a dataclass would generate
(`Circle`, `Numbers`, `Point`, `Temperature`, `Compose` all have an `__init__()`
that does nothing but assign parameters). The house style calls an unexplained
deviation from the dataclass idiom a defect, so this pointer is load-bearing.

It currently lives at the end of "Static and Class Methods", whose subject is
`cls`. Nothing in that section is about data bundles or `__repr__()`.

Proposed change: move the sentence to the end of "String Representation",
immediately after "Define `__repr__()` on classes you debug, and add `__str__()`
only when users see the output." That is the point where the reader has just
hand-written both the constructor and the `__repr__()` the pointer names.
Cost: none that I can find; nothing links to it and no anchor references it.

---

[] Reject

**"Composing Methods with `import`" (line 443) ends the chapter on a section
its own prose disowns.**

"This is a curiosity more than a technique... composition or a module-level
function is almost always a clearer choice." Nothing else in the book
references `compose.py` or `utility.py`; I grepped `Chapters/`, `Solutions/`,
`tools/data/`, and `README.md`. So the chapter's last impression, right before
the exercises, is a technique the reader is told not to use, and no exercise
touches it.

Two options:

1. Move the section to immediately after "Inheritance". It reads well there as
   a counterpoint: inheritance is one way to get a method into a class, this is
   another, and neither is the default. The cost is small: `Compose.__repr__()`
   would then appear before the "String Representation" section that teaches
   `__repr__()`, so either that listing loses its `__repr__()` (printing
   `self.name` instead of `self`) or the move waits until after "String
   Representation".
2. Cut it. Nothing downstream notices.

I recommend (1) with the `__repr__()` dropped from `Compose` (the listing does
not need it; `f"utility.f() called on {self.name}"` would do), because the
curiosity does teach something real about class bodies being ordinary
namespaces. Applying either is a structural call, so I made no change.

Separately, the prose says "Multiple classes can reuse a method defined this
way" and then shows one class. Either show two or drop the claim.

---

[] Reject

**Missing: the near-miss every reader of this chapter writes at least once,
forgetting `self`.**

The chapter explains that the first parameter must be written explicitly
(line 41) and never shows what happens when it is not. The failure is a
`TypeError` that blames the caller for the callee's mistake:

```
TypeError: Missing.show() takes 0 positional arguments but 1 was given
```

A reader staring at `x.show()` with no arguments cannot decode "1 was given"
without being told. This is the single most common beginner error in the
chapter's subject matter, it is a two-line demonstration, and the chapter is
the only place in the book that could cover it.

Proposed addition, after the paragraph ending "you must go through `self`."
(line 46):

```python
# forgot_self.py

class Forgetful:
    def show():  # Missing the self parameter
        print("never runs")

try:
    Forgetful().show()
except TypeError as e:
    print(e)
#: Forgetful.show() takes 0 positional arguments but 1 was given
```

> The "1" is the object reference Python passed automatically.
> A method that omits `self` cannot receive it.

Verified against 3.15; the message is exact. This is a new listing, so its
placement is your call, but I would put it here rather than in an exercise: the
reader will hit it before they reach the exercises.

---

[] Reject

**Exercises: two of the chapter's sections have no exercise.**

The five exercises cover properties (1), classmethods (2), inheritance (3),
`cached_property` (4), and `__repr__`/`__str__` (5). Nothing covers
"Marking Overrides with `@override`" or `@staticmethod`, and `@override` is a
full section with a stated rule. Exercise 3 uses `@override` but only as
scenery; it would pass with the decorator deleted.

Proposed addition as exercise 6:

> 6.  In `override_intro.py`, misspell `Derived`'s method as `shwo()`,
>     keeping the `@override` decorator.
>     Run the program and confirm it still prints `Base.show`,
>     then run the type checker and read what it says.
>     Remove `@override` and confirm the checker goes quiet
>     while the program's behavior does not change.

This needs the reader to have a checker installed, which chapter 8 sets up, so
if that is a problem the exercise should say "when you reach
[Static Typing](08_Static_Typing.md)" or move to chapter 8's exercise set.

---

[] Reject

**Minor, lines 3-5 and 40: "Python methods require a reference to the current
object" is contradicted 350 lines later.**

The opening states the rule without qualification; "Static and Class Methods"
then introduces two kinds of method that take neither `self` nor an instance.
A careful reader notices. One clause fixes it: "Python methods require a
reference to the current object" → "Ordinary methods require a reference to the
current object". The later section then reads as the exception it is, rather
than a retraction.

---

## Cross-chapter

**`Chapters/12_Data_Classes_as_Types.md`, line 167.** It reads
`the inspection helper from [Metaprogramming](17_Metaprogramming.md#the-inspect-module):`
and has the same wrong anchor as chapter 7 line 74. If you take the chapter-7
anchor finding above, change this one in the same pass:
`#the-inspect-module` → `#building-display_object`. These are the only two deep
links in the book that name that anchor; `heading_links.py` passes either way,
since both headings exist.

**`Solutions/07_Classes.md`, solution 1, the paragraph after the listing.** It
says "`shrink(-2)` computes `10 / -2 == -5.0` and the setter rejects it, exactly
as if you had written `c.radius = -5.0` by hand." The listing calls `c.shrink(2)`
first, so `c.radius` is `5.0` when `shrink(-2)` runs and the computed value is
`-2.5`, not `-5.0`. The output marker (`caught: radius cannot be negative`) is
correct; only the explanation is wrong. Proposed change: "`shrink(-2)` computes
`5.0 / -2 == -2.5` ... exactly as if you had written `c.radius = -2.5` by hand."

I fixed the matching error in the chapter's exercise 1 text, which had said the
radius "would divide down to `-5`" and that `shrink(2)` leaves it at `5` rather
than `5.0`, so the two now disagree until the solution is updated.
