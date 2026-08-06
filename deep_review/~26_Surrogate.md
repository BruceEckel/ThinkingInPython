# Deep review: 26_Surrogate.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Add a listing behind the corrected `isinstance()` claim

**Kind:** code
**Where:** section "Proxy", the "Identity has the same gap" paragraph (line ~213)
**Problem:** I corrected an outright error here (see "Already fixed" below): the chapter claimed
an `isinstance()` check against a `@runtime_checkable` `Protocol` *passes* on a `__getattr__()`
proxy. Since Python 3.12 that check uses `inspect.getattr_static()` and never calls
`__getattr__()`, so it fails. The corrected claim is now the only paragraph in the Proxy section
with no listing behind it, and it contradicts what a reader just learned from `proxy_protocol.py`
two pages earlier ("with `@runtime_checkable`, `isinstance()` does so at runtime"). A reader who
has been told twice that structural checks work will not believe a bare sentence saying they
don't, and this is a failure they will hit for real: `hasattr()` says `True`, the call works, and
`isinstance()` still says no.
**Proposal:** add this listing right after the corrected paragraph. Verified: runs clean, output
matches, longest line 61 characters.

```python
# proxy_identity.py
from typing import Any, Protocol, runtime_checkable

@runtime_checkable
class Service(Protocol):
    def f(self) -> None: ...

class Implementation3:
    def f(self) -> None: print("Implementation.f()")

class Proxy3:
    def __init__(self) -> None:
        self.__implementation = Implementation3()
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

p = Proxy3()
p.f()
#: Implementation.f()
print(hasattr(p, "f"))
#: True
print(isinstance(p, Implementation3), isinstance(p, Service))
#: False False
```

followed by one line of prose:

> The call works and `hasattr()` finds the method, yet neither check recognizes the proxy.
> A surrogate is verified by using it, not by asking what it is.

**Cost:** one new file, `Examples/26_Surrogate/proxy_identity.py`. Chapter 8's typing table
(`08_Static_Typing.md:511`) points at `26_Surrogate.md#proxy` for `@runtime_checkable`; the anchor
is unchanged, but that row now points at a section that also shows the construct's limit, which is
an improvement rather than a break. No other chapter makes the old claim (I grepped
`runtime_checkable` across `Chapters/`).

---

## 2. Move the Proxy-only material out of the "State" section and give the chapter a titled close

**Kind:** structure
**Where:** section "State", from line ~305 ("The difference between *Proxy* and *State*...") to
line ~417 (end of `test_counting_proxy.py`)
**Problem:** three quarters of the "State" section is not about State. Under that heading sit the
GoF list of four Proxy uses, `counting_proxy.py`, the generic-proxy paragraph, the
`__getattr__()`/`__getattribute__()` contrast, the chapter's concluding paragraph, and then
`test_counting_proxy.py` *after* the conclusion. A reader scanning headings to find "what is a
smart reference" will not look under "State", and a reader who reaches the closing paragraph
("*GoF Design Patterns* gives *Proxy* and *State* different structures...") gets pulled back into
a test listing afterward. The chapter also has no titled closing section, unlike its neighbors.
**Proposal:** three cuts, no rewriting of the prose itself.

1. Insert `## Kinds of Proxy` before line ~305 ("The difference between *Proxy* and *State* is in
   the problem each one solves."). That sentence is the natural pivot: it needs both patterns
   shown, and everything after it is Proxy material.
2. Move `test_counting_proxy.py` and its two-line introduction (lines ~390-417) up, to sit
   directly after the `__getattr__()`/`__getattribute__()` paragraph (after line ~378), matching
   how `test_state.py` follows `state.py` immediately.
3. Insert a heading before the closing paragraph at line ~380, so it becomes the chapter's
   conclusion. `## One Surrogate, Two Intents` fits the paragraph's argument.

Alternatives, if the split feels like too many headings for a short chapter: keep one new heading
only (the conclusion) and move the GoF-uses list plus `counting_proxy.py` up into the "Proxy"
section, before "## State". That reads cleanly too, but it costs the "The difference between
*Proxy* and *State*" hinge sentence, which would have to be rewritten or dropped.
**Cost:** the `#proxy` anchor is untouched, so the links from `08_Static_Typing.md:511`,
`29_Changing_the_Interface.md:99`, `:171`, and `:260` all keep working. New headings mean new
anchors that nothing yet links to. Exercise 2 names `counting_proxy.py`, which does not move
files, only position.

---

## 3. Say that `__getattr__()` delegation forwards reads, not writes

**Kind:** teaching
**Where:** section "Proxy", after the `dunder_bypass.py` discussion (line ~211)
**Problem:** the chapter teaches two limits of `__getattr__()` delegation (special methods,
identity) and omits the one a reader hits first in real code. `__getattr__()` is a read hook only,
so `p.level = "high"` stores on the proxy and the implementation never sees it. Worse, the write
then *shadows* the delegated read: every later `p.level` finds the proxy's copy and stops there,
so the proxy and the object it fronts silently disagree. Nothing in the chapter warns about this,
and every listing here happens to be read-only, so the gap is invisible.
**Proposal:** add a short listing plus two sentences after the `dunder_bypass.py` paragraph.
Verified: runs clean, output as shown, longest line 51 characters.

```python
# proxy_writes.py
from typing import Any

class Settings:
    def __init__(self) -> None:
        self.level = "low"

class Proxy4:
    def __init__(self, impl: Any) -> None:
        self.__implementation = impl
    def __getattr__(self, name: str) -> Any:
        return getattr(self.__implementation, name)

settings = Settings()
p = Proxy4(settings)
print(p.level)
#: low
p.level = "high"
print(p.level, settings.level)
#: high low
```

> `__getattr__()` is a read hook.
> The assignment stores `level` on the proxy, where the next lookup finds it,
> so the proxy stops consulting the implementation and the two disagree.
> A surrogate that must forward writes defines `__setattr__()` as well,
> and that method has to let the proxy's own attributes through
> or the assignment in `__init__()` recurses.

**Cost:** one new file, `Examples/26_Surrogate/proxy_writes.py`. It adds a third "limit of
`__getattr__()`" to a run of two, which lengthens that stretch of the Proxy section; if that is
too much, the prose alone without the listing still closes the gap.

---

## 4. Distinguish the loud dunder failure from the silent one

**Kind:** teaching
**Where:** section "Proxy", "One limit: special methods bypass `__getattr__()`" (lines ~170-211)
**Problem:** the prose groups `len(p)` and `print(p)` together as "do not delegate", but they fail
differently, and the difference is what matters. `len(p)` raises a `TypeError` that points at the
problem. `print(p)` succeeds and prints `<...Proxy object at 0x...>`, because `object` supplies a
`__str__()` and the lookup on `type(p)` therefore finds one. The listing demonstrates only the
loud case, so a reader leaves believing bypassed dunders announce themselves. The dangerous half
of the rule is the half that does not raise an exception: any dunder `object` already defines
(`__str__`, `__repr__`, `__eq__`, `__hash__`) quietly answers for the proxy instead of the
implementation.
**Proposal:** add two lines to `dunder_bypass.py` and one sentence of prose. Verified stable:

```python
print("Proxy object at" in str(p))
#: True
```

> `len(p)` reports the miss because nothing supplies a default `__len__()`.
> `print(p)` cannot: `object` already defines `__str__()`,
> so the lookup on `type(p)` finds that one and the proxy prints as itself.
> A bypassed dunder that `object` defines fails silently, which is the worse case.

An alternative demo line, if you prefer naming the mechanism over showing the symptom:
`print(type(p).__str__ is object.__str__)` with `#: True`.
**Cost:** touches an existing listing and its markers, so the extracted `dunder_bypass.py` and its
`#:` runs need re-syncing. No cross-references.

---

## 5. Say why `state.py` drops back to `Any` after the Protocol argument

**Kind:** teaching
**Where:** section "State", `state.py` (line ~231) and the "The demo uses the first
implementation" paragraph (line ~280)
**Problem:** the Proxy section spends two listings and three paragraphs establishing that a
`Protocol` is the right way to type a surrogate's implementation, and closes on structural typing
suiting the pattern. Then `state.py` types the implementation, the replacement, the
`__getattr__()` return, and `run()`'s parameter all as `Any`, with no comment. A reader who took
the Protocol lesson seriously will read this as the book contradicting itself, or will assume
`Any` is fine here and copy it. The real answer is worth stating: `__getattr__()` returns `Any` by
construction, so no annotation on the surrogate recovers static checking of `b.f()`. Typing the
*implementations* against a `Protocol` is still worth doing, and that is where the checking
survives.
**Proposal:** one short paragraph after `state.py`, before the test:

> Every annotation here is `Any`, which the Proxy section argued against.
> The reason is `__getattr__()`: whatever it returns is unknown at the type level,
> so `b.f()` cannot be checked no matter how the surrogate is annotated.
> Declaring the implementations against a `Protocol` still pays,
> because the checker then verifies each one has the methods `run()` calls;
> the hop through the surrogate is where the guarantee is lost.

**Cost:** none to code. Adds a paragraph to a section that is currently listing-heavy and
prose-light, which is probably an improvement.

---

## 6. Reconcile this chapter's Proxy definition with chapter 29's disambiguation map

**Kind:** teaching
**Where:** section "Proxy", the "It isn't necessary that `Implementation` have the same interface"
paragraph (lines ~58-63)
**Problem:** this chapter deliberately loosens Proxy: "It isn't necessary that `Implementation`
have the same interface as `Proxy`... (this statement is at odds with the definition for *Proxy*
in *GoF Design Patterns*)." Chapter 29's "Telling the Wrappers Apart" then separates the family on
the strict GoF criterion: "A Proxy keeps the wrapped object's interface and controls access to it.
... An *Adapter* changes the interface into the one you need." Read in order, the reader is given
a Proxy whose interface may differ, and then told forty pages later that keeping the interface is
what distinguishes a Proxy from an Adapter. Neither chapter acknowledges the other's position.
**Proposal:** in this chapter, after the "at odds with *GoF Design Patterns*" parenthetical, add:

> The loose reading is about what the pattern requires, not about how to name your wrapper.
> When you are choosing between *Proxy* and *Adapter*,
> the interface is still the question that separates them:
> [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart).

That is a forward link, which the book already does elsewhere (25 to 31), and it also gives this
chapter the "see also" for the wrapper family that it currently lacks in both directions: chapter
29 links here three times and gets nothing back.
**Cost:** chapter 29's "Telling the Wrappers Apart" heading has no explicit `{#id}`, so the
auto-slug is `#telling-the-wrappers-apart`; `heading_links.py` gates this, so a wrong guess fails
loudly rather than silently. If you would rather fix the tension on chapter 29's side instead,
this proposal should be deleted and the note carried there.

---

## 7. Prose nits

**Kind:** prose
**Where:** five spots, listed below
**Problem:** small wording snags, none of them errors.
**Proposal:**

- line ~99: "instead of failing later when the `Proxy` tries to delegate a call it cannot."
  The sentence ends on an elliptical "cannot" with nothing to complete it. Suggest: "instead of
  failing later, when the `Proxy` delegates a call the implementation cannot answer."
- lines 9 and 18: "The basic idea is simple." and "Structurally, the difference between *Proxy* and
  *State* is simple." Two "is simple" claims nine lines apart. Suggest cutting the second to
  "Structurally, *Proxy* and *State* differ in one respect." and letting the next sentence say what
  it is.
- line ~371: "machinery a surrogate almost never needs." "Never" is on the avoid-if-possible tier.
  Suggest "machinery a surrogate rarely needs."
- line ~387: "You need the separate implementation hierarchy that *GoF Design Patterns* uses only
  when you do not control the implementing code." The "only" reads as attaching to "uses" on first
  pass. Suggest: "The separate implementation hierarchy that *GoF Design Patterns* uses earns its
  keep when you do not control the implementing code."
- line ~358: "the lookups not found directly on the proxy". Lookup consults the proxy's class and
  its MRO, not the instance alone, so "directly on the proxy" understates it. Suggest "not found on
  the proxy or its class."

**Cost:** none.

---

## 8. The chapter's opening diagram shows a structure no listing uses

**Kind:** structure
**Where:** the opening, lines 10-16
**Problem:** the intro says "From a base class, you derive the surrogate along with the class or
classes that provide the actual implementation" and shows a diagram of exactly that. No listing in
the chapter does it. `Proxy` and `Implementation` share no base in `proxy_1.py`; `Surrogate` in
`state.py` derives from nothing; the concluding paragraph says outright that you need the separate
hierarchy only when you do not control the implementing code. So the reader's first picture of the
pattern is the one the chapter spends the rest of its length arguing against, and it is never
retracted until the final paragraph.
**Proposal:** add one sentence after the diagram, so the reader knows the picture is GoF's shape
rather than the shape they are about to write:

> That is the shape *GoF Design Patterns* draws.
> Python does not need the shared base, as the listings below show,
> but it is the clearest way to see what a surrogate is.

**Cost:** none. The alternative, moving or dropping the diagram, costs more than it buys: the
picture does explain the idea, and the concluding paragraph already lands the retraction.

---

## 9. Exercises: two have no solution, and none exercises the delegation limits

**Kind:** exercise
**Where:** section "Exercises" (line ~419)
**Problem:** `Solutions/26_Surrogate.md` answers exercises 1, 2, and 3. Exercises 4 (the
`RecursionError` typo) and 5 (the DBMS connection pool) have no solution written. Separately, the
Proxy section's three limits (special methods, identity, and, if proposal 3 lands, writes) are
taught and then never exercised; exercise 4 is the only one that touches the mechanism rather than
an application of it.
**Proposal:** add one exercise covering the dunder limit, which is the one a reader will hit while
doing exercise 5:

> 6.  `dunder_bypass.py`'s `Proxy` cannot answer `len(p)`.
>     Give it a `__len__()` that forwards to the implementation,
>     and confirm `len(p)` returns 2.
>     Then explain why `__getattr__()` could not have supplied it.

And write solutions for exercises 4 and 5 (a note for the Solutions file, not this chapter).
**Cost:** `Solutions/26_Surrogate.md` gains entries. I did not touch that file.

---

## 10. `self.__implementation` and `self._impl` in the same chapter

**Kind:** code
**Where:** `proxy_1.py`, `proxy_2.py`, `dunder_bypass.py`, `state.py` use `self.__implementation`;
`counting_proxy.py` uses `self._impl`
**Problem:** the house style reserves a double leading underscore for name mangling rather than
general privacy, and the chapter uses both conventions for the same role with no explanation. The
inconsistency is load-bearing in one direction the chapter never mentions: mangling to
`_Proxy2__implementation` is what keeps the proxy's own storage from colliding with a delegated
attribute name, which is a real reason a surrogate might want it.
**Proposal:** lowest-cost fix is one sentence where `proxy_2.py` is introduced, naming the reason:

> The name mangles to `_Proxy2__implementation`,
> so it cannot collide with an attribute the implementation carries.

Alternative: standardize on `_impl` throughout and drop the point. I recommend against that; the
mangling is genuinely useful here, and the chapter's `RecursionError` discussion already leans on
readers understanding where the proxy's own attributes live.
**Cost:** the recommended fix touches no code. The alternative renames an attribute in four
listings.

---

## Already fixed directly (no decision needed)

- lines 213-224: the claim that `isinstance()` against a `@runtime_checkable` `Protocol` *passes*
  on a `__getattr__()` proxy was wrong. Since Python 3.12 that check uses
  `inspect.getattr_static()`, which reads class and instance dictionaries directly and never
  invokes `__getattr__()`, so the check fails. Verified on the pinned 3.15.0b4:
  `isinstance(p, HasF)` is `False` while `hasattr(p, "f")` is `True` and `p.f()` runs. Rewrote the
  paragraph to state the real behavior and dropped its closing line ("One more reason structural
  typing suits this pattern"), which the correction reverses. No other chapter repeats the claim.

Checks run before and after (read-only, no `make`, no `--write`): `ruff check`, `ty check`, and
`pytest` on `build/examples/26_Surrogate` all pass; all seven runnable listings produce output
matching their `#:` markers; `heading_links.py` and `banned_phrases.py` both clean.
