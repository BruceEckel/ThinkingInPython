[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Exercises 1 to 4 belong to chapter 32, not this chapter.**

Four of the six exercises are *Multiple Dispatching* problems inherited from
*Thinking in Patterns*, where Visitor and Multiple Dispatching shared a chapter:

- 1 and 2 build the `Dwarf`/`Elf`/`Troll` interaction system "using *Multiple
  Dispatching*." Nothing in chapter 33 teaches how to build one; the technique
  is chapter 32's `paper_scissors_rock.py`.
- 3 and 4 are explicitly about `paper_scissors_rock.py` versus
  `paper_scissors_rock_table.py`, both of which are chapter 32 listings, and
  exercise 3 opens by linking to chapter 32 to establish its own premise.

Apply the skill's test: each exercise should be answerable from this chapter.
Only 5 and 6 are. Meanwhile chapter 33's actual content — double dispatch in
`flower_visitors.py`, the `Any`/`Protocol` trade, the silent default, the
"one dispatch is enough" argument — is covered by two exercises, both of them
about `singledispatch`.

Proposed change: move exercises 1 to 4, and their solutions, to chapter 32,
where they would follow the existing `Lizard` exercises naturally (32's
exercise 2 already asks the reader to compare the method version against the
table version, which is exercise 3's question in miniature). Renumber 5 and 6
to 1 and 2 here, and add the two new exercises below.

Price of the move, which is real and worth weighing:

- `Solutions/33_Visitor.md` sections 1 to 4 move to `Solutions/32_Multiple_Dispatching.md`
  and renumber; sections 5 and 6 renumber to 1 and 2.
- `Solutions/33_Visitor.md`'s exercise 4 answer links to
  `32_Multiple_Dispatching.md#one-type-or-many`; that link becomes same-file
  `#one-type-or-many` once moved.
- The exercise files themselves (`exercise_1.py` through `exercise_4.py`) move
  between solution trees, so `make prune-examples` will want a run afterward.
- Chapter 32 would then have nine exercises and chapter 33 four, which is
  lopsided but honest about where the material lives.

I did not touch either file, per the scope rules. If you would rather not move
them, the cheaper alternative is to leave them where they are and add a line to
the exercise heading saying they carry chapter 32's material forward, so a
reader who cannot answer them knows to go back rather than concluding they
missed something here.

---

[] Reject

**Chapter-level, order: the `Any`/`Protocol` discussion should come before
"Notice where the behavior lives," not after it.**

The untitled opening section runs four beats in this order:

1. the double-dispatch walkthrough (`The accept()/visit() pair is the double
   dispatch`),
2. "Notice where the behavior lives," whose last line is
   "the primary hierarchy ends up carrying code it was supposed to be spared,"
3. the `Any` paragraph, the indented `Protocol` fragment, and the price of
   keeping `Any`,
4. the section break into "The Pythonic Visitor: singledispatch."

Beat 2's closing line is the chapter's indictment of *Visitor* and the reason
`singledispatch` follows. Beat 3 then interposes a typing digression between
that line and the section that cashes it in, so the reader arrives at
`singledispatch` having most recently read about `Protocol`s rather than about
the primary hierarchy carrying code it should not.

The gap also runs the other way. A reader meets `visitor: Any` on the seventh
line of `flower_visitors.py` and wants an explanation immediately; it arrives
about sixty lines later, after two unrelated paragraphs. Both problems are
fixed by the same move.

Proposed change: swap beats 2 and 3, so the order becomes walkthrough →
`Any`/`Protocol` → "Notice where the behavior lives" → section break.
Cost of the move: nothing. No listing depends on the order, no term is defined
in one and used in the other, and no other chapter references either passage.
Only the paragraph order in one Markdown file changes.

Reported rather than applied, since reordering is your call.

---

[] Reject

**`flower_visitors.py`: `Bug`, `Pollinator` and `Predator` are inert, and
`Bee` and `Fly` carry the same body.**

```python
class Bug(Visitor):
    pass
class Pollinator(Bug):
    pass
class Predator(Bug):
    pass

class Bee(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

class Fly(Pollinator):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)
```

No code in the listing, and no sentence in the chapter, ever names `Bug`,
`Pollinator` or `Predator`. They are three classes of pure scaffolding in a
book whose style skill says to cut scaffolding, and the reader has no way to
tell whether the three-level hierarchy matters to the pattern (it does not) or
is decoration (it is). At the same time `Bee` and `Fly` repeat one method body
verbatim, which the comments acknowledge ("Bee pollinates:", "Fly also
pollinates:") without saying why the duplication is kept.

Three ways out. I recommend B.

**Option A: delete the middle layer.** `Bee`, `Fly` and `Worm` subclass
`Visitor` directly. Shortest listing, but it loses the fact that the visitor
side is a hierarchy at all, which is half of why the pattern needs a second
dispatch.

**Option B (recommended): make the middle layer load-bearing.** Move `visit()`
up to where the operation is actually decided:

```python
class Bug(Visitor):
    pass

class Pollinator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.pollinate(self)

class Predator(Bug):
    def visit(self, flower: Flower) -> None:
        flower.eat(self)

class Bee(Pollinator):
    pass
class Fly(Pollinator):
    pass
class Worm(Predator):
    pass
```

The output is unchanged, the duplicate body is gone, and the three middle
classes now earn their place: `Pollinator` *is* the operation, and `Bee` and
`Fly` are two concrete visitors that share it. It also sharpens the chapter's
own thesis, because the class that names the operation is now visibly a class
where `singledispatch` uses a function name. The cost is that the classes named
in the demo (`Bee()`, `Fly()`, `Worm()`) become empty, which reads slightly
less like GoF's ConcreteVisitor.

**Option C (cheapest): keep the code and explain it.** One sentence after the
listing, e.g. "The visitor side is a hierarchy because the classic pattern
allows visitors to be grouped and substituted; here `Pollinator` and `Predator`
only classify." This removes the puzzlement without touching the listing.

---

[] Reject

**The double dispatch is described but never shown: proposed
`dispatch_trace.py`.**

The prose narrates both hops accurately ("the worm's type chose `eat()`, and
the flower's type chose which `eat()` runs"), but nothing in the output lets a
reader confirm it. Twelve lines of `Xxx pollinated by Yyy` show only results.
Apply the deep-review test: could a reader narrate the mechanism from the
output alone? No; they can only take the paragraph's word for it. Chapter 32
solved exactly this problem twice, with a traced listing (`radd_dispatch.py`
prints `__add__(...)`/`__radd__(...)` on every hop) and with the
`_images/double_dispatch` diagram. Chapter 33 has neither, even though its
dispatch is the more confusing of the two, because the two hops run in the
opposite order from GoF's.

Proposed new listing, verified: it runs clean, its markers are exact and
deterministic across runs, and it passes `ruff` and `ty` in `build/private/33`.
It depends on the `if __name__ == "__main__"` guard I added to
`flower_visitors.py` (see the manifest), without which importing it would
replay the whole demo.

```python
# dispatch_trace.py
from flower_visitors import Chrysanthemum, Gladiolus, Worm

worm = Worm()
for flower in (Chrysanthemum(), Gladiolus()):
    print(type(worm).visit.__qualname__,
          "then", type(flower).eat.__qualname__)
    flower.accept(worm)
#: Worm.visit then Chrysanthemum.eat
#: Chrysanthemum is toxic to Worm
#: Worm.visit then Flower.eat
#: Gladiolus eaten by Worm
```

Two lines of output per flower name the method each dispatch actually reached.
The second pair is the one that earns the listing: `Flower.eat`, not
`Gladiolus.eat`, is the visible form of the sentence already in the chapter,
"the flower-side dispatch goes back to having nothing to say."

Where it goes is your call. My suggestion is immediately after the
`accept()`/`visit()` paragraph and before "Notice where the behavior lives,"
with a lead-in of one sentence, e.g. "Printing the qualified name of each
method the two hops reach makes the pair visible."

Alternative if you would rather not add a listing: commission a diagram on the
model of `_images/double_dispatch`, showing `flower.accept(worm)` →
`Worm.visit` → `Chrysanthemum.eat` with the two resolution points marked. That
costs no example and no output markers, but it cannot show the `Flower.eat`
fallback case, which is the more instructive half.

---

[] Reject

**The opening section has no heading and now runs about 150 lines.**

Everything from the chapter title down to "## The Pythonic Visitor:
singledispatch" is one unbroken run: the motivation, the flagship listing, the
double-dispatch walkthrough, where the behavior lives, and the `Any`/`Protocol`
discussion. Neighbouring chapters break at roughly half that length, and the
book's own table of contents therefore offers a reader nothing between "Visitor"
and "The Pythonic Visitor."

Proposed change: a `##` heading before "One annotation in the listing looks like
a shortcut and is not," titled for its content, e.g. **"The Price of the Empty
Base"** or **"Why `accept()` Takes `Any`"**. The second needs an explicit
`{#id}` because of the backticks and the parentheses (CLAUDE.md's anchor rule),
so prefer the first unless you want the mechanism in the title.

Price of the change: it adds an anchor other chapters could later target, and
nothing currently links into that region, so nothing breaks. If you also take
the reorder proposal above, the heading should move with the `Any` block so it
still sits directly over it.

---

[] Reject

**`test_visitor.py` sits after what reads like the section's closing
paragraph.**

The singledispatch section ends its argument at

> As with [Pattern Refactoring](37_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s
> recycling-note example,
> `singledispatch` is the open-method mechanism that *Visitor* fakes.

which is a summing-up, and then the test listing and its three-sentence lead-in
follow it. The reader has already been told the section is over.

Two fixes, pick one:

- **Move the test up**, so it lands directly after "The default is also the
  risk" paragraph's alternatives and before "*Visitor* still has a place."
  The test's stated purpose (registered types, the default, independent
  dispatch, inheritance) is precisely a check of the claims in that paragraph,
  so it reads as evidence rather than an appendix. Cost: nothing references the
  test by position.
- **Move the two closing paragraphs down**, past the test, into the first
  paragraph of "One Dispatch Is Enough," which is where "*Visitor* still has a
  place" belongs anyway. Cost: "One Dispatch Is Enough" gets longer and its
  first line stops being the crisp
  "*Visitor* dispatches twice, and `singledispatch` dispatches once."

I prefer the first.

---

[] Reject

**No exercise covers the `Any`-to-`Protocol` swap, which is a whole subsection
of the chapter.**

The chapter spends the last third of its opening section on why `accept()` takes
`Any`, shows the `Protocol` that removes it, and then declines to use it. That
is the one thing in the chapter a reader is most likely to want to do to their
own code, and nothing asks them to do it.

Proposed exercise, to sit with the two `singledispatch` ones:

> Rewrite `flower_visitors.py` with the `Visits` protocol in place of `Any`,
> so `accept()` declares what it needs.
> Then add a `Beetle(Bug)` with no `visit()` method and pass it to
> `accept()`.
> Which version reports the mistake, and when?

I verified both halves against the pinned 3.15 build and `ty` 0.0.65: the
`Protocol` version type-checks clean and runs to the same output, and passing a
`visit()`-less `Bug` is accepted by the checker under `Any` and fails at runtime
with `AttributeError: 'Bug' object has no attribute 'visit'` (that failure is
now named in the chapter prose; see the manifest).

---

[] Reject

**"The default is also the risk" paragraph: the union-annotation sentence is
wedged into the wrong argument.**

The paragraph runs: default is a risk → raise `NotImplementedError` instead →
`match` plus `assert_never()` catches it statically → **union annotation
registers several types at once** → adding an operation costs a function →
adding a flower costs a class plus registrations → use `singledispatchmethod`
for a method.

The union sentence is a registration mechanic. It answers "how do I write a
registration," not "what do I do about the silent default," and it sits between
two sentences that are both about the default. A reader tracking the argument
has to park it and resume.

Proposed change: move

> A union annotation, `flower: Gladiolus | Ranunculus`,
> registers one implementation for several types at once.

up into the `_` paragraph, which is already the chapter's account of how a
registration is written, appending it after "so nothing is lost." I verified the
form still works on the pinned 3.15 build: registering
`def _(flower: Gladiolus | Ranunculus)` puts both classes in `nectar.registry`
and both dispatch to that one implementation.

Reported rather than applied because moving a sentence between paragraphs
changes the pacing of both.

---

[] Reject

**Optional: the dispatch table is invisible.**

`nectar.registry` and `nectar.dispatch(SomeType)` let a reader inspect what
`@singledispatch` built, and the chapter's claim about inheritance
("an unregistered subclass uses its nearest registered ancestor") is currently
asserted in prose and pinned only by a pytest assertion. Three lines appended to
`visitor_singledispatch.py`'s demo would make it self-evident:

```python
    print(sorted(t.__name__ for t in nectar.registry))
    print(nectar.dispatch(Ranunculus) is nectar.dispatch(Flower))
#: ['Chrysanthemum', 'Gladiolus', 'object']
#: True
```

Verified output. I am reporting rather than applying it because it lengthens the
listing's demo for a point the tests already make, and because the `object` in
that first line needs the explanation I added to the prose anyway. Take it only
if you want the mechanism visible in the listing itself.[[yes]]

---

## Cross-chapter

[] Reject

**The 22 → 33 load-bearing-`Any` thread: checked, consistent, with one latent
fragility.**

I read both ends. Chapter 22's `messenger_idiom.py` needs `m: Any` because
`Messenger` replaces its own `__dict__` with `**kwargs`, so no set of attribute
names exists to declare, and 22 states the price plainly ("A typo like `m.inof`
is a runtime `AttributeError`, not a static error"). Chapter 33's summary of
that — "a bag of attributes named at runtime leaves no precise type to write" —
is accurate, and its contrast (33's `Any` is chosen, 22's is not) holds. Nothing
at the 22 end needs changing.

The one fragility: 33 links to `22_Data_Transfer_Objects.md` with no anchor,
because the paragraph it means sits in 22's untitled opening section and there
is no heading to target. Per CLAUDE.md, a whole-file link degrades silently if
22 is ever split, and the reader lands at the top of a chapter and has to hunt.
If you ever give 22's opening section a heading, point this link at it. I would
not add a heading to 22 solely for this, and I did not touch chapter 22.

For the record, the nearer precedent is chapter 32, not 22:
`paper_scissors_rock.py` carries the same *chosen* `Any` with the same
`Protocol` escape one chapter earlier. I added a cross-reference to it in the
chapter (see the manifest), since a reader who just read 32's "Note what the
`Any` annotations cost" would otherwise wonder why 33 presents the same trade
as new.

---

[] Reject

**MANIFEST, not a proposal: what this pass already applied to
`Chapters/33_Visitor.md`.**

Everything below is in the chapter now and passes `validate_output.py`, `ruff`,
`ty`, `pytest`, `heading_links.py`, `banned_phrases.py` and
`reflow_prose.py --diff`.

1.  `flower_visitors.py`: wrapped the demo in `if __name__ == "__main__":`, so
    the module is importable. Its sibling `visitor_singledispatch.py` in the
    same chapter and its counterpart `paper_scissors_rock.py` in chapter 32
    both already had the guard; this one did not, and importing it replayed the
    whole demo. Output and `#:` markers unchanged.
2.  "Python has no overloading" → "Python has no method overloading, since a
    second `def visit()` replaces the first". The flat claim contradicted the
    `singledispatch` section thirty lines later and `typing.overload`; the added
    clause says what is actually meant and pre-explains why `@nectar.register`
    can reuse `_`.
3.  "A `Protocol` removes the `Any` in four lines" → "for two new lines and an
    import". The fragment adds two lines and needs `Protocol` imported; four was
    counting the re-shown `Flower`.
4.  Named the price of the chosen `Any`, which the chapter previously alluded to
    without stating: `Gladiolus().accept(Bug())` passes the type checker and
    fails at runtime with `AttributeError: 'Bug' object has no attribute
    'visit'`. Verified both halves. Added the cross-reference to chapter 32's
    identical `Any`.
5.  Added a bridge before `visitor_singledispatch.py` saying the flowers are the
    same three but the operations are new and there are two of them, so a reader
    expecting a translation of the first listing is not left comparing the wrong
    things. (Exercise 5 is where the actual translation happens.)
6.  "A `match` over a closed union of types goes further and catches it before
    the program runs" → added "with `assert_never()` in the `case _`". The
    `match` alone catches nothing statically; chapter 34's `filesystem.py`, the
    linked target, gets its guarantee from `assert_never()`.
7.  Added, after "a forgotten registration shows up as a wrong result rather
    than a failure": `@singledispatch` registers the base implementation under
    `object`, not under the `Flower` in its annotation, so `nectar(42)` returns
    `42: no nectar`, and the checker does not object because the dispatcher
    declares `Any` parameters. Both verified on the pinned build.
8.  "Adding a new flower is a class and, where needed, a one-line registration"
    → "a class, plus one registration for each operation that needs more than
    the default". A registration is three lines, which is what
    `Solutions/33_Visitor.md`'s exercise 6 counts, and the cost scales with the
    number of operations, which is the expression-problem point that solution
    ends on.
9.  `functools.singledispatchmethod` is now a named link to
    [`41_Functional_Toolkits.md#singledispatchmethod`](../Chapters/41_Functional_Toolkits.md#singledispatchmethod)
    and says it dispatches on the first argument after `self`. That difference
    is the whole lookalike-pair hazard and was stated in neither chapter.
10. "*Visitor* still has a place: when you truly cannot define functions over
    the hierarchy, or you need the `accept()` hook for some other reason" → "when
    the elements must drive the traversal themselves from inside `accept()`, or
    when a framework you do not own already calls that hook". The old first case
    is near-vacuous in Python (you can always define a function over a
    hierarchy), and `Solutions/33_Visitor.md`'s exercise 5 says so itself.
11. `test_visitor.py`: collapsed `test_nectar_registered_types` and
    `test_nectar_default_for_unregistered` into one
    `@pytest.mark.parametrize`d `test_nectar_registered_and_default`, mirroring
    the `fragrance` test three lines below it. Nothing explained why one
    operation was tested with parametrize and the other with two multi-assert
    functions. Suite goes from 7 passing tests to 9.
