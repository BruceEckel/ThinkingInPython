When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Intro, third paragraph: the chapter promises requirement-driven evolution and
never delivers a requirement.**

The intro says:

> The example is a trash sorting simulation, and it evolves across the chapter:
> an initial solution, then successive redesigns as new requirements appear.

and the conclusion cashes that in:

> This chapter discovered its vectors one requirement at a time,
> rather than predicting them up front.

No requirement ever actually appears.
`recycle_rtti.py` is replaced because the prose judges it flawed on sight,
not because anything changed;
`Plastic` is only ever hypothetical ("when a new material joins the system, `Plastic` say"),
and the Visitor section's requirement is a supposition
("Suppose the `Trash` hierarchy is fixed").
So the chapter is a sequence of designs with commentary,
which is a fine thing to be, but not what the intro says it is.

Two ways out. I recommend the first.

**Option A (recommended): make `Plastic` land, once, between the two sorters.**
After `recycle_rtti.py` and its critique, add three lines to `trash.dat`
(a `plastic.dat`, or a second data file, to leave `trash.dat` alone)
and a `class Plastic(Trash): value = 0.15`, then re-run the `match` sorter and show it
dropping every piece of plastic on the floor.
That turns "Any you miss will silently drop trash on the floor" from an assertion
into an output the reader can read.
The dictionary version then arrives as the fix for a failure they have seen,
which is exactly the arc the intro advertises.
Cost: one new listing plus a data file, `#:` markers for the new run,
and exercise 1 loses its first half (it currently asks the reader to do the
`Plastic` experiment) so it would need rewriting toward the singledispatch side.
`Solutions/37_Pattern_Refactoring.md` exercise 1 would need the same rewrite.
I did not draft this, because where a new listing goes is your call.

**Option B (cheap): soften the intro and the conclusion.**
Change "as new requirements appear" to "as you ask what will change next,"
and "discovered its vectors one requirement at a time" to
"named its vectors one at a time, by asking what the next change would cost."
Two lines, no new code, and the chapter stops claiming an arc it does not have.

---

[] Reject

**`parse_trash.py`: the header comment restates the prose directly above it.**

The listing opens with

```python
# parse_trash.py
# Read "Name:weight" lines into Trash objects through the registry.
```

and the sentence immediately before the block is

> Parsing it into `Trash` objects goes through the registry,
> so the parser never mentions a concrete material.

`thinking-in-python-skill.md` ("New descriptions belong in prose, not comments")
puts descriptions like this in the prose and keeps only the `# path/slug.py`
marker in the code, and here the prose already carries it word for word.
It is the only descriptive header comment in the chapter's five listings.

Proposed change: delete the second comment line.
Reported rather than applied because the style skill also says not to edit
comments already sitting in existing example code without being asked.

---

[] Reject

**`parse_trash.py`: `filename: str` makes the test stringify a `Path`.**

```python
def parse(filename: str) -> list[Trash]:
    for line in Path(filename).read_text().splitlines():
```

The body already works with anything `Path()` accepts, but the annotation says
`str`, so `test_parse_trash.py` has to write

```python
items = parse(str(data))
```

after building `data` as a `tmp_path / "trash.dat"`.
Converting a `Path` back to a `str` to hand it to a function that immediately
rebuilds the `Path` is the sort of thing the book teaches readers not to write.

Recommended fix: widen the annotation to `filename: str | Path`
and drop the `str(...)` in the test.
The three call sites (`recycle_rtti.py`, `recycle_dict.py`, `recycling_note.py`)
keep their pleasant `parse("trash.dat")` form and nothing else changes.

Alternative: `def parse(path: Path)` throughout, with `parse(Path("trash.dat"))`
at all three call sites. Stricter, but it puts `Path(...)` noise in three
listings whose subject is sorting, not file handling.

Not applied because it edits code in four listings, which felt like your call
rather than mine on a judgment item.

---

[] Reject

**`trash.py`: `create()` is a `@classmethod` that never uses `cls`.**

```python
@classmethod
def create(cls, name: str, weight: float) -> Trash:
    return Trash.registry[name](weight)
```

`cls` is bound and discarded; the body hard-codes `Trash`.
Nothing catches this (`ruff` has no rule on it here, `ty` is happy), but the
decorator is doing no work, and a reader who has just been told that
`__init_subclass__()` is *implicitly* a classmethod is primed to look closely
at the explicit one two lines below.

Recommended fix: `return cls.registry[name](weight)`.
The dict is found through the MRO and is the same object either way, so
behavior is identical and the decorator earns its place.

Alternative: make it a module-level `def create(name, weight)`, which is what
[Factory](27_Factory.md#the-pythonic-factory-a-dictionary)'s `make()` does with
the same registry. That is more consistent with chapter 27 but loses the
`Trash.create(...)` reading the parser depends on.

---

[] Reject

**`recycling_note.py`: the `seen` set is bookkeeping unrelated to the point.**

```python
seen: set[type[Trash]] = set()
for t in parse("trash.dat"):
    if type(t) not in seen:
        seen.add(type(t))
        print(recycling_note(t))
```

Four lines and a second data structure exist only to stop the demo printing
twenty-two nearly identical lines.
The listing's subject is single dispatch; the deduplication is a distraction,
and it is the one part of the listing a reader has to decode before they can
read the part that matters.

Proposed change: drop `seen` and the `parse()` call and iterate the registry
the chapter already built:

```python
for cls in Trash.registry.values():
    print(recycling_note(cls(1.0)))
```

That is two lines instead of five, it prints exactly one note per material,
and it re-uses the registry rather than introducing a new mechanism.
The `#:` markers change to registry insertion order:

```
#: Aluminum: crush and bale
#: Paper: no special handling
#: Glass: sort by color, then crush
#: Cardboard: flatten and bundle
```

Cost: `parse` and `parse_trash` drop out of this listing's imports, so the
chapter's last listing no longer touches the data file.
Reported rather than applied because it rewrites an existing listing's output.

---

[] Reject

**"Adding Operations", first paragraph: the motivating premise contradicts the
chapter it sits in.**

> Suppose the `Trash` hierarchy is fixed
> (maybe it comes from a third-party library)
> and you want to add new behaviors to it without editing it

Everything before this point has been built on the opposite premise: `trash.py`
is ours, and the chapter has just spent two sections showing that adding a
material to it costs one class definition.
Asking the reader to now imagine they cannot touch it undercuts the running
example, and it is not even the strongest reason to use `singledispatch` here.
The real reason is the one the section's own last paragraph implies: an
operation that varies by material does not have to live on `Trash`, so
`Trash` does not accumulate `price()`, `note()`, `hazard()`, and everything
else the plant eventually needs.

Proposed replacement for the "Suppose ..." sentence:

> `Trash` should not grow a method for every question the plant learns to ask.
> Recycling instructions, disposal hazards, and transport volume are all
> operations that vary by material, and none of them belong in `trash.py`.
> Visitor is the classic way to add them from outside, and it is the harder
> way of the two available here.

Then the following paragraph's "[Visitor](33_Visitor.md) solves this problem"
still lands, and the third-party-library case can survive as a parenthesis if
you want to keep the classic motivation.

(Applied in this pass, independently: the sentence's examples used to be
"price it, weigh it, print recycling instructions," and pricing and weighing
are exactly the two operations exercise 2 concludes must *not* use single
dispatch. They now read "print recycling instructions, flag a disposal hazard."
See the manifest at the end.)

---

[] Reject

**"Visitor is elaborate: a `Visitor` base class with one `visit()` overload per
material" describes a Visitor the book never shows.**

Two sentences in this section describe the same imaginary implementation:

> a `Visitor` base class with one `visit()` overload per material,
> an `accept()` method added to every element,
> and *double dispatch* to route each piece to the correct `visit()`.

and, later,

> No `Visitor` class exists, no `accept()` method bolted onto every material,
> and no decorator gymnastics to fake overloading.

Neither matches `flower_visitors.py` in [Visitor](33_Visitor.md), which is where
the link sends the reader.
There, each *visitor* class has exactly one `visit()`, and the per-element
behavior lives in overridden methods on `Flower` (`pollinate()`, `eat()`).
The "one overload per element" arrangement is GoF's C++/Java form, which Python
cannot spell at all without the "decorator gymnastics" the second sentence
mocks. So the paragraph derides a design it also asserts Visitor has, and the
reader who clicks through finds a third thing.

There is a second problem with "no decorator gymnastics to fake overloading":
the alternative being praised is four decorators deep. A reader who has just
counted `@singledispatch` and three `@recycling_note.register` lines will not
believe the sentence.

Recommended fix: say which form is being described, and drop the third clause.

> Visitor is elaborate.
> In its C++ and Java form a `Visitor` base class declares one overload per
> material, every element grows an `accept()` method,
> and *double dispatch* routes each piece to the correct overload.
> Python has no method overloading, so even writing that down takes work
> ([Visitor](33_Visitor.md) shows the shape the book's version settles on).

and later:

> Compare this to a Visitor implementation.
> No `Visitor` class exists, no `accept()` method bolted onto every material,
> and no second dispatch to arrange.

Alternative, cheaper: keep the first description but add "in Java or C++"
to it, and change the third clause of the later sentence to
"and nothing added to `Trash` at all."

Not applied because it rewrites four lines of your prose in a section whose
rhythm is deliberate.

---

[] Reject

**"Choosing the Lightest Construct" never names the two constructs the chapter
chose.**

The conclusion is entirely at the level of advice: vector of change, lightest
construct, a pattern earning its keep.
It is good advice, and a reader who skims it cannot tell which chapter it
closes. Neither `type(t)` nor `singledispatch` appears in it, and neither does
the word `Trash`.
The deep-review test for a conclusion is whether it names the capability the
reader gained; this one names a habit of mind instead.

Proposed addition, after "in a problem (here, new types versus new operations)
and choosing the lightest construct that isolates it.":

> Here that meant two lines of Python.
> A dictionary keyed by `type(t)` absorbs new materials,
> and a `@singledispatch` function absorbs new operations.
> Neither is a pattern in the *GoF* sense, and between them they cover both
> vectors of change the trash sorter has.

Reported rather than applied because it changes the pacing of the closing
section, which is yours to set.

---

[] Reject

**Exercise 1 asks the reader to confirm the wrong two files, and understates
what changes.**

> 1.  Add a `Plastic` material with a per-pound value.
>     Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,
>     and that only `trash.dat` and (optionally)
>     a one-line `recycling_note()` registration do.

Two problems.

First, `recycle_rtti.py` is the file the exercise should be about.
The section that introduces it stakes its whole argument on "Any you miss will
silently drop trash on the floor," and the reader is never asked to watch that
happen. Confirming that `recycle_dict.py` is unaffected proves the easy half;
watching `recycle_rtti.py` print correct-looking totals with every piece of
plastic missing proves the half the chapter cares about.

Second, "only `trash.dat` and (optionally) a one-line registration" is not
true: `test_trash.py::test_subclasses_self_register` asserts the registry is
exactly `{"Aluminum", "Paper", "Glass", "Cardboard"}` and fails the moment
`Plastic` is defined. That is a *good* failure — a self-registering design
telling you it registered — and worth saying, not worth hiding.

Proposed replacement:

> 1.  Add a `Plastic` material with a per-pound value and some `Plastic:NN`
>     lines to `trash.dat`.
>     Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,
>     then run `recycle_rtti.py` and account for every pound of plastic it
>     reports. Which test in `test_trash.py` fails, and why is that the right
>     behavior for it?

If you take this, `Solutions/37_Pattern_Refactoring.md`'s exercise 1 needs the
extra two answers (the `match` sorter silently discards plastic because no
`case` matches it and there is no `case _`; `test_subclasses_self_register`
fails because it pins the exact registry contents).
I did not touch `Solutions/`, per the scope rules.

---

[] Reject

**Exercises: nothing exercises the chapter's own lookalike pair.**

The three exercises cover adding a type (1), when *not* to use single dispatch
(2), and moving dispatch onto an object (3).
Nothing asks about the difference the chapter now names explicitly: the bins
dictionary matches the exact class, `singledispatch` follows the MRO.
That difference is the one thing in the chapter a reader can get wrong in
production code without any tool telling them.

Proposed exercise 4:

> 4.  Derive `CrushedAluminum` from `Aluminum` and run both `recycle_dict.py`
>     and `recycling_note.py` over data containing it.
>     Explain why it gets its own bin but not its own note.
>     Then change `recycle_dict.py` so a subclass shares its parent's bin,
>     without naming any material in the sorting loop.

The last clause has a clean answer (give `Trash` a
`bin: ClassVar[type[Trash]]` that each material sets, and key on `t.bin`),
which is also a small lesson in choosing your own key instead of accepting
`type(t)`.

---

[] Reject

**Minor prose and reference notes, none applied.**

1.  Intro, second paragraph:
    "Many patterns in *GoF Design Patterns* work around the limitations of
    statically typed languages without multiple dispatch."
    Multiple dispatch is the limitation that matters for *Visitor*, but not for
    the other pattern this chapter dissolves. The registry factory is about
    classes being first-class values, and the dictionary sorter is about
    `type(t)` being a usable key. Suggest "the limitations of statically typed
    languages: single dispatch, closed classes, and types that are not values."

2.  "The First Cut": "the registry keeps `Trash` deliberately open" attributes
    the openness to the registry. An ordinary base class is already open; the
    registry is what makes the openness *usable*. Suggest "and `Trash` is
    deliberately open, which is the point of the registry."

3.  "The First Cut" ends "Testing for all of them means you are doing
    polymorphism's job by hand." The fix in the next section is not
    polymorphism, it is a dictionary keyed by type, so the aphorism points
    somewhere the chapter does not go. It is a good line; consider
    "...means you are doing dispatch's job by hand," which covers both.

4.  The figure sits above `trash.py`, but its alt text and its right-hand
    panel are about `bins` and `type(t)`, which arrive two sections later.
    Front-loading the payoff is defensible; if you want it, a half-sentence
    under the figure ("the right-hand half is the sorter two sections from
    now") would stop a reader hunting for `bins` in the listing below it.

5.  The chapter reads `trash.dat` by a bare relative name, so all three sorter
    listings only run with the chapter directory as the working directory.
    The harness chdir's, so no gate notices. Not worth `Path(__file__).parent`
    clutter in three listings, but worth knowing if a reader reports it.

---

[] Reject

**Cross-chapter thread checks: results.**

Verified, no action needed at either end:

-   Exact-type dict dispatch, 31 → 32 → 37.
    `Chapters/31_State_Machines.md` ("the lookup keys on `type(event)` exactly:
    a dictionary probe, not an `isinstance()` walk") and
    `Chapters/32_Multiple_Dispatching.md` ("the table matches the class
    exactly") both agree with this chapter's `bins[type(t)]` paragraph, and the
    two links from here resolve.
-   The registry factory, 27 → 37.
    `Chapters/27_Factory.md` links here at
    `#simulating-a-trash-recycler`, which still exists; its
    import-time-registration and name-collision caveats are correct for
    `Trash.registry` too. This chapter's back-link was bare
    (`[Factory](27_Factory.md)`) and now points at
    `#the-pythonic-factory-a-dictionary`, where those caveats live.
-   The Visitor thread, 33 → 37. `Chapters/33_Visitor.md` links here at
    `#adding-operations-visitor-and-why-python-skips-it`; that heading is
    unchanged. The mismatch between 33's Visitor *listing* and this chapter's
    Visitor *description* is a separate block above.

One correction to the accrued notes rather than to a chapter:
the note in `.claude/skills/deep-review/SKILL.md` says the registry-factory
thread backs "the registries in 20/37."
`Chapters/20_Rethinking_Objects.md` contains no registry and no
`__init_subclass__`; its only related links are two pointers to 33's
`singledispatch` section. The "20" end of that thread appears to be stale.

---

[] Reject

**MANIFEST — not a proposal. Everything applied to
`Chapters/37_Pattern_Refactoring.md` in this pass, in file order.**

-   `[Factory](27_Factory.md)` is now
    `[Factory](27_Factory.md#the-pythonic-factory-a-dictionary)`, the section
    that holds the registry and its caveats.
-   New paragraph after `trash.py` explaining `Bins`, which the chapter used
    three times and never named, and why a `type` statement can mention
    `Trash` above the `class` statement (lazy right side, PEP 695), with a link
    to [The `type` Statement](08_Static_Typing.md#the-type-statement).
-   "Python implicitly makes `__init_subclass__` a classmethod, so `cls`
    doesn't need an `@classmethod` decorator" said the parameter needed the
    decorator. Now: "so it needs no `@classmethod` decorator and its first
    parameter is the new subclass."
-   Dropped "just" from "The `ClassVar` annotation just tells type checkers…".
-   "It treats each subclass's assignment as filling in that same classvar" →
    "It reads each subclass's assignment as overriding that declared
    attribute", which stops contradicting "creates its own class attribute"
    two sentences earlier.
-   "`sum_value()` … relies on polymorphism (`t.value`, `t.weight`) and never
    asks what type each piece is" was contradicted by the listing's own
    `type(t).__name__`. Now says it uses the type only to label the printed
    line, never to decide what to do.
-   "which the next section arranges" → "which is what the next section does."
-   New sentences at the end of "Let a Dictionary Do the Sorting": the `match`
    sorter and the dictionary sorter disagree about subclasses
    (`case Aluminum()` matches any subclass; `bins[type(t)]` does not), so the
    swap is a redesign rather than a rename. Verified by running both.
-   New paragraph in the same section: `defaultdict(list)` is what creates each
    bin, `Bins` is an alias for a plain `dict` so `bins: Bins = {}`
    type-checks, and that version raises `KeyError` on the first piece.
    Verified.
-   "Adding Operations" opener: "This chapter has changed *types* cheaply so
    far" → "So far the chapter has made new *types* cheap", and the
    types-versus-operations trade is now named as the expression problem with a
    link to
    [Pattern Matching](13_Pattern_Matching.md#dynamic-binding-vs.-pattern-matching),
    which is where the book defines it.
-   The motivating list "price it, weigh it, print recycling instructions" →
    "print recycling instructions, flag a disposal hazard": pricing and
    weighing are the two operations exercise 2 concludes must not use single
    dispatch.
-   Comma added: "`functools.singledispatch`, which dispatches on the type of
    its first argument".
-   "a throwaway name [Visitor](…) explains" → "the throwaway name explained in
    [Visitor](…)".
-   New sentences after the `recycling_note.py` listing: an unregistered
    material gets the default with no exception and no checker complaint (the
    risk 33 spells out), and adding `Plastic` costs one registration per
    operation that must answer differently — Python does not escape the
    expression problem, it makes both sides cost a line.
-   "Adding a `price()` or `weight()` operation means writing another
    single-dispatch function" → "Adding another operation that varies by
    material…", because the original contradicted this section's own closing
    advice and exercise 2's answer.
-   New paragraph after the Visitor comparison: the chapter's two dispatches
    disagree about subclasses (`bins[type(t)]` exact, `singledispatch` through
    the MRO, so a `CrushedAluminum` gets its own bin but `Aluminum`'s note),
    linked to
    [Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many).
    Both behaviors verified on the pinned 3.15 build.
-   "`singledispatchmethod` does the same thing as a method" →
    "`functools.singledispatchmethod` provides the same dispatch in method
    form."
-   `tools/reflow_prose.py --write` run on this chapter only; it touched the
    four paragraphs added above and nothing else.

No listing, `#:` marker, test, or heading changed, so no anchor moved and no
other chapter's cross-references are affected.
`validate_output.py`, `ruff`, `ty`, `pytest`, `heading_links.py`,
`banned_phrases.py`, and `reflow_prose.py --diff` are all clean.
