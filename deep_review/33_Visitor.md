# Deep review: 33_Visitor.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Close the loop the opening opens: why one dispatch replaces two

**Kind:** teaching
**Where:** end of section "The Pythonic Visitor: singledispatch" (after line ~211), before "Exercises"
**Problem:** The chapter opens with "The *Visitor* pattern uses *Multiple Dispatching*. People can confuse the two by looking at the implementation rather than the intent," and then never says what the intent difference is. It also never explains the largest question the second half raises: how a *single*-dispatch function can stand in for a pattern the first half built out of *double* dispatch. A reader who came from [Multiple Dispatching](32_Multiple_Dispatching.md) is left assuming `singledispatch` must be losing something. The chapter also ends on a test listing, with no closing section carrying an insight (chapters 32, 34 and 35 all end on a titled section that does).

**Proposal:** Add a closing section after the tests. Draft:

```markdown
## One Dispatch Is Enough

*Visitor* dispatches twice, and `singledispatch` dispatches once.
Nothing was lost in the trade.
The second dispatch in the classic pattern is not there because two
types are unknown; it is there because the operation has nowhere else
to live.
The visitor's type stands in for the operation, so the language must
resolve it at runtime along with the element's type.
Once an operation can be a function defined outside the hierarchy,
calling `nectar()` instead of `fragrance()` selects the operation
before anything runs, and only the flower's type is still unknown.
One dispatch covers it.

That is the intent difference the chapter opened with.
*Visitor* adds operations to a hierarchy you cannot edit, and its
double dispatch is the means.
*Multiple Dispatching* is the end in itself: two objects whose types
are both unknown until runtime have to interact, as in
`paper_scissors_rock.py`.
`singledispatch` dispatches on the first argument only, so it does
nothing for that second problem.
When two types must genuinely resolve together, use the table keyed by
a tuple of types from
[Multiple Dispatching](32_Multiple_Dispatching.md#one-type-or-many).
```

**Cost:** Adds a section heading, so any later cross-reference to it must use the anchor `#one-dispatch-is-enough`; nothing links to it today. Touches the chapter's ending, which is where the humanizer pass last worked. If you would rather not add a heading, the first paragraph alone can be dropped in as prose right after "`singledispatch` is the open-method mechanism that *Visitor* fakes."

---

## 2. Warn that an unregistered type falls to the default silently

**Kind:** teaching
**Where:** section "The Pythonic Visitor: singledispatch", paragraph beginning "Nothing touches `Flower`." (line ~192)
**Problem:** The chapter presents the `@singledispatch` default as a convenience and never says what it costs. Adding a new `Flower` subclass and forgetting to register it is not an error: it returns the base function's answer, with no exception, no warning, and nothing for `ty` to flag. That is the one way this design is worse than the alternatives the book recommends elsewhere: [Composite and Interpreter](34_Composite_and_Interpreter.md)'s `match` over a closed union gets `assert_never()` and a static error when a case is missing. A reader adopting `singledispatch` should know which of the two they are choosing.

**Proposal:** Add after "...falling back to the `Flower` default only when no ancestor is registered (the tests below pin this down)." Draft:

```markdown
The default is also the risk.
A new `Flower` subclass that nobody registers gets the default answer
with no exception and no static complaint, so a forgotten
registration shows up as a wrong result rather than a failure.
When there is no sensible answer for an unregistered type, give the
base function a `raise NotImplementedError(f"no nectar rule for
{type(flower).__name__}")` instead of a fallback string, and the
omission fails at the first call.
A `match` over a closed union of types goes further and catches it
before the program runs
([Composite and Interpreter](34_Composite_and_Interpreter.md#a-composite-of-data-classes)),
at the price of a set of types no one else can extend.
```

**Cost:** Forward-references chapter 34, which is fine (13, 20 and 32 already forward-reference this chapter). If you want the point without the forward reference, cut the last sentence. The `raise` suggestion contradicts nothing in the listing, which keeps its string default deliberately.

---

## 3. Correct the double-dispatch walkthrough: `accept()` performs no dispatch here

**Kind:** teaching
**Where:** paragraph after `flower_visitors.py` (lines ~105-108)
**Problem:** The text says "`accept()` resolves the flower's type, then `visit()` resolves the visitor's type, and the `pollinate()` or `eat()` call inside `visit()` dispatches on the flower's type." That names three resolutions for a mechanism with two. `accept()` is defined once on `Flower` and no subclass overrides it, so calling it selects nothing: the flower's type is resolved once, later, by `pollinate()`/`eat()`. A reader who traces the code and finds only two overridden methods will think they have missed something, and a reader who has seen the pattern elsewhere will wonder why `accept()` is not overridden per element as GoF shows it.

**Proposal:** Replace lines ~105-108 with:

```markdown
The `accept()`/`visit()` pair is the *double dispatch*.
`accept()` hands the concrete flower to the visitor,
`visit()` resolves the visitor's type,
and the `pollinate()` or `eat()` call inside `visit()` resolves the flower's type.
In the classic pattern every element class overrides `accept()`, which is where the element's type is resolved;
here one inherited `accept()` is enough, because the flower's type is resolved a step later.
```

**Cost:** Same paragraph as proposal 4. If both are accepted, apply 3 first and let 4's sentences follow this text. Nothing else in the book describes this listing's dispatch order.

---

## 4. Say why the operations sit on the flower side

**Kind:** teaching
**Where:** paragraph after `flower_visitors.py` (lines ~105-115), and the listing comment "# The Flower hierarchy cannot be changed:" (line ~29)
**Problem:** The opening states the premise: a primary hierarchy you cannot change, to which you want to add new polymorphic methods. The listing then puts `accept()`, `pollinate()` *and* `eat()` on `Flower`, and the new behavior (toxicity) inside `Chrysanthemum`. So the operations the visitors supposedly add already live in the hierarchy the comment says cannot change. An attentive reader will notice that the example does not do what the premise promised, and the chapter says nothing about it. The reason is worth teaching: the classic form keeps the operation bodies in the visitor by overloading `visit()` once per element type, and Python has no overloading, so the type-specific behavior moves to the flower side.

**Proposal:** Add two sentences at the end of that paragraph:

```markdown
Notice where the behavior lives.
The classic pattern overloads `visit()` once per flower type and keeps each operation's body in the visitor,
so the only addition to the primary hierarchy is `accept()`.
Python has no overloading, so this version puts the type-specific behavior in `pollinate()` and `eat()` on the flowers instead,
and the visitors choose between them.
Whichever way you write it, the primary hierarchy ends up carrying code it was supposed to be spared.
```

Alternative (smaller): leave the prose and change the listing comment to `# The Flower hierarchy is fixed apart from accept():`, which at least stops the code from asserting something the next four lines contradict. This is weaker: it fixes the contradiction without teaching the reason.

**Cost:** Lengthens the chapter's most-read paragraph by four lines. Overlaps proposal 3 (same paragraph). The last sentence is a judgement about the pattern; delete it if you would rather not editorialize before the `singledispatch` section makes the same case with code.

---

## 5. Show the `Protocol` that replaces the `Any`, or say why the `Any` stands

**Kind:** teaching
**Where:** paragraph beginning "One annotation in the listing is required for the code to type-check." (lines ~117-126)
**Problem:** The paragraph names two fixes for the `Any` (an abstract `visit()` on the base, or a `Protocol`) and then adopts neither, calling the `Any` "the quiet price of the empty base, the same bargain [Data Transfer Objects](22_Data_Transfer_Objects.md) paid." The comparison does not hold up: chapter 22's `Any` is forced by the design, since a bag of attributes named at runtime cannot be described statically, while this one is a choice. The book spends chapter 8 and the house style insisting on precise types, so a reader who has absorbed that will want the four-line `Protocol` here, and the chapter tells them it exists without showing it.

**Proposal:** Show the `Protocol` inline, verified to pass `ty` on the current listing:

```markdown
A `Protocol` removes the `Any` in four lines:

class Visits(Protocol):
    def visit(self, flower: Flower) -> None: ...

class Flower:
    def accept(self, visitor: Visits) -> None:
        visitor.visit(self)

The listing keeps `Any` because the empty `Visitor` base is what the classic pattern looks like,
and seeing the price is part of the point.
```

(as an indented snippet or a fenced block without a `# slug.py` first line, so it is not extracted as an example). Then cut or soften the "same bargain" sentence, since 22's `Any` was forced and this one is chosen.

Alternative: keep the paragraph as-is and only fix the comparison, replacing "the same bargain [Data Transfer Objects] paid for its attribute bag" with a sentence saying this `Any` is chosen rather than forced, unlike 22's.

**Cost:** The `Any` here is one end of the load-bearing-`Any` thread that runs 22 → 33, so weakening the reference to 22 loosens that thread; the alternative above keeps the link while making the difference honest. A snippet inside prose is not extracted or gated, so it must be right by inspection: the version above was checked with `uv run ty check` against the full listing and passes.

---

## 6. Give the exercises something to do with `singledispatch`

**Kind:** exercise
**Where:** section "Exercises" (lines ~265-286)
**Problem:** All four exercises are Multiple Dispatching problems: Dwarf/Elf/Troll interaction, weapons and battles, and two that ask about `paper_scissors_rock_table.py` from chapter 32. None touches `singledispatch`, `accept()`, or the flower listings, so the half of the chapter that carries its argument is untested and the exercise set does not cover the chapter's main claim.

**Proposal:** Add two exercises. Draft:

```markdown
5.  Rewrite `flower_visitors.py` with `singledispatch`:
    make `pollinate()` and `eat()` functions defined outside the `Flower` hierarchy,
    with `Chrysanthemum`'s toxicity a registered implementation of `eat()`.
    Which classes and which methods disappear?
6.  Add a `Rose` to `visitor_singledispatch.py` with abundant nectar and a strong fragrance,
    then add a third operation, `thorns()`, over all four flowers.
    Count the lines each change costs,
    and say which of the two `@singledispatch` makes cheaper.
```

**Cost:** `Solutions/33_Visitor.md` currently answers exercises 1-4 and would need two more entries with working, gated listings. Exercise 6 is the one that cashes the promise chapters 13 and 20 make when they say this chapter "explores" the add-a-type-versus-add-an-operation trade-off; today the chapter states it in two lines and moves on.

---

## 7. Two wordings that make a reader stop

**Kind:** prose
**Where:** line ~19 and line ~117
**Problem:** "This virtualizes the operations performed upon the primary hierarchy" uses a C++ verb for dynamic binding that this book does not use anywhere else, and "performed upon" is stiffer than the surrounding prose. "One annotation in the listing is required for the code to type-check" reads as though only one annotation in the listing matters to the checker, when the point is that one parameter had to be typed `Any` rather than with a real type.

**Proposal:** Line ~19: "The operations on the primary hierarchy become dynamically bound." Line ~117: "One annotation in the listing looks like a shortcut and is not."

**Cost:** None. Both are single-line replacements. Line 19 is original *Thinking in Patterns* prose, so reject this if you want to keep that voice.

---

## 8. Name chapter 37's example correctly

**Kind:** prose
**Where:** line ~210
**Problem:** "As with [Pattern Refactoring](37_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s price-and-weight example" points at a section whose example is `recycling_note()`. Price and weight appear there as operations that *could* be added, and as exercise 2. A reader who follows the link looks for a price-and-weight listing that is not there.

**Proposal:** "As with [Pattern Refactoring](37_Pattern_Refactoring.md#adding-operations-visitor-and-why-python-skips-it)'s recycling-note example".

**Cost:** None.

---

## 9. Two small things in `flower_visitors.py`

**Kind:** code
**Where:** `flower_gen()` (lines ~77-80)
**Problem:** `flwrs = Flower.__subclasses__()` uses a vowel-dropped abbreviation that appears nowhere else in the book, and `for i in range(n)` binds a loop variable nothing uses. The sibling generator in [Multiple Dispatching](32_Multiple_Dispatching.md), `item_pair_gen()`, writes `items` and `for _ in range(n)`, and this chapter goes on to explain `_` as the name for something nobody will use.

**Proposal:**

```python
def flower_gen(n: int) -> Iterator[Flower]:
    flowers = Flower.__subclasses__()
    for _ in range(n):
        yield random.choice(flowers)()
```

**Cost:** None. Output is unchanged (the module-level `flower` loop variable is a different scope), and both listings still lint and type-check. Left as a proposal rather than a direct fix because neither is a stated house-style rule.

---

## Already fixed directly (no decision needed)

- line ~108: "lands back on the flower's type" used `lands`, a word on the watch list's do-not-use tier. Now "dispatches on the flower's type". (Proposal 3 rewrites this sentence again if you accept it.)
