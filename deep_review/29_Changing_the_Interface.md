When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

`[] Reject`

**Adapter — `adapter.py` teaches four unfamiliar things at once.**

The chapter's first listing is 73 lines and introduces, simultaneously:
the Adapter idea itself, positional-only parameters (`/`),
`Any` as a deliberate Liskov escape hatch,
multiple inheritance used as a class adapter,
and a nested class handed out by an accessor.
The reader meets all of that before seeing one working adapter.
The two paragraphs after the listing ("Two details in the listing repay attention")
exist entirely to unpick the parts that are *not* about Adapter,
which is the tell.

This is the skill's "One new thing per listing" and "Escalating difficulty"
lenses: the section opens at full complexity and then explains its way back down.

Proposed change: split the listing in two.
`adapter.py` keeps `WhatIHave`, `WhatIWant`, `ProxyAdapter`, `WhatIUse`
and the Approach-1 call (the object adapter, the smallest thing that makes the point).
`adapter_variations.py` carries approaches 2, 3 and 4 with their demo lines.
The object-adapter/class-adapter paragraph then sits with the listing that shows both,
and the positional-only/`Any` paragraph sits with the listing that needs it.

Price of the rearrangement, checked: low.
Nothing outside the chapter names `adapter.py`
(`Solutions/29_Changing_the_Interface.md` names only `getattr_adapter.py`;
`39_Pattern_Catalog.md` links the `#adapter` section anchor, which is unaffected;
`tools/data/norun.txt` has no chapter-29 entry).
The `#:` markers move with their `print` lines unchanged.

Alternative, if the split feels like too much surgery:
keep one listing but move the `/`-and-`Any` paragraph into a short
subsection of its own, so the Adapter argument is not interrupted by a
type-checker digression.

---

`[] Reject`

**Adapter — `WhatIWant` is a third, weakest form of "declared interface", unremarked.**

`class WhatIWant: def f(self) -> None: ...` is instantiable, and its `f()`
silently does nothing. [Surrogate](26_Surrogate.md#proxy) spends two listings
on exactly this choice for a surrogate's implementation: an ABC forces
completeness at construction, a `Protocol` needs no base class at all.
Here the reader is shown the one form that neither book chapter recommends,
with nothing said about it, in a chapter titled "Changing the Interface".

Proposed change: one sentence after the listing, e.g.
"`WhatIWant` is a bare placeholder rather than an ABC or a `Protocol`,
because this listing is about *where* the adaptation lives, not how the target
interface is declared; [Surrogate](26_Surrogate.md#proxy) compares those two."

I did not apply this because the silence may be deliberate: the listing is the
GoF shape translated, and naming every way it is un-Pythonic before the
"Adapter in Python" section could steal that section's punchline.

---

`[] Reject`

**Exercises — nothing exercises the chapter's two conceptual claims.**

The three exercises cover `getattr_adapter.py`, `deprecating.py` and
`facade.py`, one listing each. Neither the object-adapter/class-adapter
distinction (the point of `adapter.py`) nor the wrapper disambiguation table
(the point of "Telling the Wrappers Apart") is exercised, and those are the two
things a reader should be able to *do* after this chapter.

Proposed exercise 4:

> 4.  Here are three wrappers: one logs each call and forwards it unchanged,
>     one exposes a `read()` over an object that only has `next_chunk()`,
>     and one refuses calls unless a flag is set. Classify each as Proxy,
>     Decorator, Adapter, or Façade using the "remove it and you lose" test
>     from the table, and say what you would lose in each case.

Not applied: a new exercise needs a matching entry in
`Solutions/29_Changing_the_Interface.md`, which is outside this review's scope.

---

`[] Reject`

**Adapter — the one-sentence Proxy paragraph is orphaned, and its subject is unclear.**

> This takes liberty with the term "[Proxy](26_Surrogate.md#proxy),"
> because *GoF Design Patterns* asserts that a Proxy must have an identical
> interface with the object for which it is a surrogate.

"This" has no antecedent in the preceding paragraph, which is about monotonous
output; the thing taking the liberty is the *name* `ProxyAdapter`, mentioned
sixty lines earlier. "an identical interface with the object" is also not
English the book uses elsewhere; GoF's phrasing is "the same interface as".

Proposed change:

> The name `ProxyAdapter` takes a liberty with the term
> "[Proxy](26_Surrogate.md#proxy)":
> *GoF Design Patterns* requires a Proxy to have the same interface as the
> object it speaks for.

and attach it to the class-adapter paragraph rather than leaving it as a
standalone one-sentence paragraph.

---

`[] Reject`

**Adapter in Python — `getattr_adapter.py` runs a demo when the test imports it.**

`test_adapter.py` does `from getattr_adapter import Adapter, WhatIHave`,
and `getattr_adapter.py`'s top level prints `gh` and `g`, so those two lines are
emitted during collection on every pytest run. The house style is explicit:
"Importable modules carry no top-level demo. If a module is both a library and
a demonstration, split it."

I did **not** apply the usual `if __name__ == "__main__":` guard, because this is
a two-chapter convention rather than a chapter-29 defect:
[Surrogate](26_Surrogate.md)'s `state.py` and `counting_proxy.py` have the same
shape (top-level demo plus a `test_*.py` that imports them), and 31's
`StateMachine` listings do too. Fixing 29 alone makes the pair inconsistent.

Proposed change, if you want it: add the guard to `getattr_adapter.py`,
`state.py`, `counting_proxy.py` and the chapter-31 pair together,
in a single pass, and check that `validate_output.py` still matches the `#:`
markers (it `exec()`s each block, so `__name__` inside a guarded block needs
verifying before committing to this).

---

`[] Reject`

**Adapter — the forward pointer fires two paragraphs early.**

"...and the next section argues Python lets you skip most of the packaging too."
ends the "output is deliberately monotonous" paragraph,
but two more paragraphs follow before `### Adapter in Python`.
A reader who takes the pointer at face value reads the next two paragraphs
looking for the argument it promised.

Proposed change: move the "The output is deliberately monotonous..." paragraph
down so it sits immediately above `### Adapter in Python`,
after the Proxy aside and after "Two details in the listing repay attention".
The forward pointer then lands on the section it names.
(If the `adapter.py` split above is applied instead, this resolves on its own.)

---

`[] Reject`

**Façade — `facade.py`'s `A` is a mutable dataclass while `checkout.py`'s three are frozen.**

```python
@dataclass
class A:
    x: object
```

Nothing mutates `A`, and every dataclass in the very next listing is
`@dataclass(frozen=True)`. The house style is frozen unless mutation is the
point, and the inconsistency sits inside one section.

Proposed change: `@dataclass(frozen=True)` on `A`.
Output is unaffected (`A(x=1)`).
Note `Solutions/29_Changing_the_Interface.md`'s exercise-3 answer copies the
same shape into `shop.py` as `@dataclass class _A` / `_B`; if `A` becomes
frozen, those should follow.

---

`[] Reject`

**Retiring the Old Interface — `warnings.deprecated()`'s version is never stated.**

`warnings.deprecated()` arrived in Python 3.13 (PEP 702);
`typing_extensions.deprecated` is the back-port. The book targets 3.15, so this
is not a correctness problem, but the chapter states version availability for
other recent features and a reader on 3.11 or 3.12 will try this and fail.

Proposed change: one clause on first mention, e.g.
"`warnings.deprecated()` (Python 3.13 and later; `typing_extensions.deprecated`
before that) marks a function, method, or class as on its way out".

---

`[] Reject`

**Prose — "repay attention" is the book's only use of the phrase.**

"Two details in the listing repay attention." `repay` appears nowhere else in
`Chapters/`. It is correct English but a shade more literary than the
surrounding voice. Minor; flagging it for your ear rather than proposing a
specific replacement, since the obvious plainer versions ("are worth a closer
look") are blander than the original.

---

## Cross-chapter

`[] Reject`

**`Chapters/06_Modules_and_Packages.md` — `__all__` is never taught anywhere in
the book, but the module-façade material depends on it.**

`__all__` appears in no chapter. `Solutions/29_Changing_the_Interface.md` uses
it twice in the exercise-3 answer ("a real module either sets `__all__` or
imports as `import dataclasses`", and "it comes with the underscore convention,
`__all__`, and one-time initialization built in") with no prior definition,
which is a "used before it is taught" case.

My 29 edit now names it in one clause in the module-façade paragraph
("an `__all__` list of the public names states the same boundary explicitly"),
which is enough for that section but is not where the term belongs.

Change to make: a short paragraph in chapter 6 covering what module-level
export control actually is — the leading underscore is a convention that only
affects `from module import *`, `__all__` is the explicit list, and neither
prevents `module._name` — so that 24 (module as singleton), 29 (module as
façade) and the 29 solutions can all point at one place.

---

`[] Reject`

**`Chapters/26_Surrogate.md`, lines 66-68 — sends the reader to chapter 29 to
learn something chapter 29 contradicts.**

26 currently reads:

> It isn't necessary that `Implementation` have the same interface as `Proxy`.
> As long as `Proxy` is somehow "speaking for" the class to which it forwards
> method calls, it satisfies the basic idea
> (this statement is at odds with the definition for *Proxy* in
> *GoF Design Patterns*).
> When you are choosing between *Proxy* and *Adapter*,
> the interface is still the question that separates them:
> [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart).

Three lines after arguing that a Proxy's interface need not match, 26 tells the
reader the interface is what separates Proxy from Adapter. 29's closing
paragraph in that very section takes 26's side and says the opposite:
"the Adapter is what a Proxy becomes once you stop insisting on the interface."

I have edited the 29 end of the thread so it now resolves the tension there
(new sentences: "That leaves the 'What it adds' column to separate them: a Proxy
controls access to one implementation, an Adapter makes one type fit a caller
that expects another. Name a wrapper for why it is there, not for its shape.").
The 29 wording works under either 26 phrasing, so this is safe to leave as-is,
but 26's sentence would read better as:

> Under GoF's stricter definition the interface is what separates *Proxy* from
> *Adapter*; under the looser one used here it is the intent.
> [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart)
> sorts out both readings.

Change to make: replace 26's "When you are choosing between *Proxy* and
*Adapter*, the interface is still the question that separates them:" with the
two sentences above. No other change in 26.

---

`[] Reject`

**`Chapters/14_Decorators.md`, end of `## The Decorator Pattern` — the thread
has no link from this end.**

29's disambiguation table cites
`[Decorator](14_Decorators.md#the-decorator-pattern)`, and 26 links forward to
`29_Changing_the_Interface.md#telling-the-wrappers-apart`. Chapter 14 has no
link forward to it, so a reader who meets the object Decorator in 14 and later
meets a `__getattr__` wrapper has nothing pointing at the disambiguation.

I verified 14's substance against 29's table and found nothing to correct:
`Topping` satisfies the `Pizza` `Protocol` structurally, so 29's Decorator row
("Interface: same", "What it adds: behavior") is accurate for 14's listing, and
so is "Remove it and you lose the added behavior".

Change to make: one sentence at the end of 14's Decorator Pattern section
(a natural spot is beside the existing "[Factory](27_Factory.md#builder) has its
own `Pizza`" paragraph):

> A Decorator keeps the wrapped object's interface and adds behavior.
> Proxy, Adapter and Façade wrap the same way and differ in intent;
> [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart)
> sorts the four.

---

`[] Reject`

**`.claude/skills/deep-review/SKILL.md`, accrued notes — the chapter-29 entry is
stale.**

The note reads "29 ends with the wrapper disambiguation map
(Proxy/Decorator/Adapter/Façade) that leans on 26 and 14."
29 does not end there: "Retiring the Old Interface" follows it and is the
chapter's closing section. The chapter's own opening paragraph carried the same
stale claim ("the chapter ends by sorting the four apart"), which I fixed to
"a later section sorts the four apart", so the note and the chapter drifted
together.

I left the section order alone, deliberately: the intro frames the chapter as
"adding an interface is the safe half; the other half is telling callers the old
one is going away", and the deprecation section is that second half, so it
belongs last. Only the note (and the intro sentence) were wrong.

Change to make: reword the accrued note to "29's wrapper disambiguation map
(Proxy/Decorator/Adapter/Façade) leans on 26 and 14", dropping "ends with".
