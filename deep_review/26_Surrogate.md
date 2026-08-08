When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Line numbers below refer to `Chapters/26_Surrogate.md` **after** the four fixes
I already applied (listed at the end of this file, under "Already applied").

[] Reject
**Lines 511-513 — the conclusion's last claim reads backwards.**

    The separate implementation hierarchy that *GoF Design Patterns* uses
    earns its keep when you do not control the implementing code.
    When you do, the single generic surrogate above is simpler
    and just as flexible.

If you do not control the implementing code, a shared base class is the one
thing you cannot impose on it — that is precisely when you need structural
conformance (`Protocol`) or bare `__getattr__()` forwarding. As written the
sentence recommends the option the circumstance rules out, and it also
undercuts the chapter's own `Protocol` section, which introduced structural
typing as the answer for "the implementation needs no base class."

I can see the reading that makes it true — *others* write the implementations
against a base class *you* own, as plugin authors do — but "do not control"
normally means "cannot modify," and the two readings point opposite ways.

Proposed, if the plugin reading is what you meant:

    The separate implementation hierarchy that *GoF Design Patterns* uses
    earns its keep when other people write the implementations
    and you need the base class to state what they owe you.
    When you write both sides, the single generic surrogate above is simpler
    and just as flexible.

Proposed, if the wrapping-third-party-code reading is what you meant, the
conclusion inverts:

    The separate implementation hierarchy that *GoF Design Patterns* uses
    needs both sides under your control.
    A `Protocol` gets the same guarantee without the inheritance,
    and the single generic surrogate above gives up the guarantee entirely
    in exchange for working on anything.

I did not pick one because the two say different things about the chapter.

[] Reject
**Lines 70-108 — `proxy_interface.py` contains no proxy.**
The listing is introduced as the way to give `Proxy` a common interface, and
the prose after it talks about "when the `Proxy` delegates a call the
implementation cannot answer," but no `Proxy` appears anywhere in the file. The
opening diagram (line 12) draws the surrogate *and* the implementations
deriving from one base; every listing in the chapter shows only the
implementation half of that picture, so the diagram's left branch is never
realized in code.

Proposed, in order of preference:

1.  Add three lines to `proxy_interface.py` so the reason for the ABC is
    visible: a `class Proxy: def __init__(self, service: Service) -> None:`
    that stores the argument and forwards `f()` and `g()`, with the demo
    passing `Complete()`. The `TypeError` from `Partial()` then reads as "the
    proxy could never have been handed a broken implementation," which is the
    sentence at line 106-108.
2.  Or leave the listing alone and add one sentence after line 16 saying the
    base class is only load-bearing on the implementation side in Python, and
    the listings therefore show only that side. Cheaper, and it also answers a
    reader comparing the diagram to `proxy_1.py`.

I did not do either, because (1) adds a listing and (2) changes the framing of
the opening, and both are pacing calls.

[] Reject
**Lines 397-455 — the chapter never shows a Proxy controlling access, which is
the one thing it says a Proxy is for.**
Line 507 ("*Proxy* fronts for one implementation to control access to it"),
line 25 ("*Proxy* is used to control access to its implementation"), and
chapter 29's disambiguation table ("access control ... remove it and you lose
control over when and whether the call gets through") all rest on a capability
no listing in this chapter demonstrates. `CountingProxy` observes; it never
refuses. The virtual proxy and the protection proxy are named in the numbered
list at 402-414 and then handed to the exercises.

The gap matters because it is exactly what separates Proxy from Decorator and
Adapter in chapter 29's table: a Decorator adds behavior, a Proxy decides
whether the call happens at all. Without a listing, "access control" is a
phrase rather than a mechanism, and the reader cannot narrate the difference.

Proposed listing, verified clean under `ty`, `ruff` (70 cols), and its
markers. It fits before `counting_proxy.py` (protection before smart
reference, matching the numbered list's order) and collides with no exercise:
exercise 1 is the virtual proxy, exercise 5 is the connection pool.

```python
# protection_proxy.py
from typing import Any, Final

READ_ONLY: Final[frozenset[str]] = frozenset({"read"})

class Document:
    def read(self) -> str: return "contents"
    def erase(self) -> None: print("erased")

class Guarded:
    def __init__(self, doc: Document, *, admin: bool) -> None:
        self._doc = doc
        self._admin = admin
    def __getattr__(self, name: str) -> Any:
        if not self._admin and name not in READ_ONLY:
            raise PermissionError(name)
        return getattr(self._doc, name)

guest = Guarded(Document(), admin=False)
print(guest.read())
#: contents
try:
    guest.erase()
except PermissionError as e:
    print(type(e).__name__, e)
#: PermissionError erase
Guarded(Document(), admin=True).erase()
#: erased
```

The prose that earns it is one sentence: the counting proxy watches the call
go by, this one decides whether it goes by at all, and that decision is what
makes a wrapper a Proxy rather than a Decorator.

If you would rather not add a listing, the cheaper fix is to say plainly at
line 452-455 that this chapter shows only the smart reference and the
exercises build the other three, so the reader knows the omission is
deliberate.

[] Reject
**Lines 457-465 — `__getattr__()` vs `__getattribute__()` answers a question
the reader asked 300 lines earlier.**
`__getattr__()` is introduced at line 146. Any reader who has met
`__getattribute__()` (or who looks up "attribute hook") wants the distinction
there, and the chapter's fallback-vs-intercept explanation is what makes the
`proxy_writes.py` read/write asymmetry at line 261 make sense in the first
place — the read hook is a *fallback*, which is exactly why the write went to
the proxy. Sitting in "Kinds of Proxy," it reads as an aside about
`CountingProxy` rather than the mechanism behind three earlier listings.

Proposed: move lines 457-465 (down to "machinery a surrogate rarely needs") to
immediately after line 184, changing `self._impl` and `self.calls` to
`self.__implementation`, which resolves normally there for the same reason.

Price of the move, checked:

- The `RecursionError` paragraph (466-473) should stay where it is: it feeds
  exercise 4, and it names `self._imp` from `counting_proxy.py`. It needs a
  one-clause reopener ("The fallback hook has a trap of its own:") since it
  would no longer follow the sentence it currently continues.
- Nothing else in `Chapters/` or `Solutions/` references this passage by
  position; chapter 29's back-reference is to the special-method limit and to
  the `RecursionError` trap, both of which stay put.

[] Reject
**Lines 138-148 — the interface material's payoff evaporates one listing
later, and the chapter does not say so until line 368.**
Lines 70-144 spend two listings teaching how to pin down the implementation's
shape, with an ABC and with a `Protocol`. Line 146 then switches to
`__getattr__()`, which erases the entire benefit at the proxy boundary: no
declaration on `Proxy2` can make `p.f()` checkable. The chapter states this
correctly, but in the *State* section, 220 lines later ("The hop through the
surrogate is where the guarantee is lost"). A reader who has just been sold on
`Protocol` and is now writing a `__getattr__()` proxy has no idea the two
choices trade off, and no reason to expect the answer that far away.

Proposed: two sentences after line 184, where the question arises.

    The interface work above still pays on the implementation side:
    the checker verifies that whatever you hand the proxy has the methods.
    It stops paying at the proxy itself.
    `p.f()` goes through `__getattr__()`, whose return type is unknown,
    so nothing the proxy declares can make that call checkable.
    Explicit forwarding, as in `proxy_1.py`, is the version a checker can see
    through; `__getattr__()` trades that for reach.

Then line 368-373 in the State section can shorten to a back-reference. This
is the single change in this file I would most like made; I left it as a
proposal only because it adds a paragraph and shortens another, which is a
pacing decision.

[] Reject
**Lines 365-373 — two claims in the State typing paragraph overstate, and the
paragraph recommends something the listing does not do.**

1.  "Every annotation here is `Any`" — `state.py` also has `name: str` and
    four `-> None`s. "Every annotation that carries the implementation is
    `Any`" is what is meant.
2.  "which the Proxy section argued against" — the Proxy section argued *for*
    a declared interface, but four of its own listings (`proxy_2.py`,
    `dunder_bypass.py`, `proxy_writes.py`, `proxy_identity.py`) annotate with
    `Any`, so pointing back at it as the authority is confusing. The book's
    typing guidance is the real referent.
3.  "Declaring the implementations against a `Protocol` still pays, because
    the checker then verifies each one has the methods `run()` calls" —
    `state.py` does not declare a `Protocol`, so the chapter advises a step it
    then omits, with no note that it omitted it.

Proposed for (1) and (2):

    The annotations that carry the implementation are all `Any`,
    which the book's typing guidance treats as a last resort.

Proposed for (3): either add a three-line `Protocol` to `state.py` and
annotate `run(b: ...)` against it (which would also demonstrate the split the
paragraph describes), or add "`state.py` skips it to keep the delegation in
view" so the omission is deliberate on the page. I lean toward the first: it
turns the paragraph's advice into something the reader can see.

[] Reject
**Lines 516-536 — no exercise touches *State*, and exercise 3 has no support
in the chapter.**
The chapter's thesis is that Proxy and State are one structure; State gets a
section, a listing, and a test. All six exercises are Proxy. A reader who does
the exercise set practices half the chapter.

Exercise 3 ("Create a simple copy-on-write implementation") is also the only
one whose subject appears nowhere in the chapter except as five words inside
the *Smart reference* bullet at line 413. The solution is by some distance the
longest in `Solutions/26_Surrogate.md` and introduces an ownership-count
design the chapter never mentions.

Proposed: add a State exercise, and consider whether exercise 3 should be
scoped down or moved.

    Extend `Surrogate` in `state.py` so `change_to()` rejects an
    implementation missing a method the current one has,
    and explain why the type checker could not have caught that swap.

That exercise is answerable from the chapter (it uses `dir()` or a `Protocol`
check plus the "the hop through the surrogate is where the guarantee is lost"
paragraph) and it exercises the one State-specific piece of machinery.

Also unexercised: the write gap (`__setattr__()`) and the identity gap
(`isinstance()`), both of which got a listing each. Exercise 6 covers the
dunder gap; a parallel exercise for one of the other two would even out the
coverage of the "three things delegation does not forward" run.

[] Reject
**Lines 62-68 — the Proxy/Adapter sentence contradicts the paragraph it ends.**

    It isn't necessary that `Implementation` have the same interface as `Proxy`.
    ...
    When you are choosing between *Proxy* and *Adapter*,
    the interface is still the question that separates them:
    [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart).

Three sentences say the interface does not have to match, then the fourth says
the interface is what separates Proxy from Adapter. A reader who takes the
first three at face value has just been told the distinguishing test is one
this chapter rejects, with no signal that the two sentences are speaking from
different definitions. Chapter 29 resolves it explicitly ("Surrogate takes the
looser view of the first row"), but that is 250 pages of reading away.

Proposed: make the change of frame visible in the sentence itself.

    That is a looser definition than *GoF Design Patterns* uses,
    and under GoF's stricter one the interface is exactly what separates
    *Proxy* from *Adapter*:
    [Telling the Wrappers Apart](29_Changing_the_Interface.md#telling-the-wrappers-apart).

That keeps the forward link, keeps the parenthetical's point, and stops the
paragraph from arguing with itself.

[] Reject
**Lines 270-308 — the identity gap is diagnosed with no escape hatch.**
The section proves `isinstance()` never sees through a surrogate, ends on
"code that asks `isinstance()` sees only the proxy's own class," and stops. The
reader whose framework calls `isinstance()` is left with a dead end. Two exits
exist and I verified both on the pinned 3.15:

- `Service.register(Proxy3)` makes `isinstance(p, Service)` `True`. It works
  for a `Protocol` too, because `_ProtocolMeta.__instancecheck__` tries
  `_abc_instancecheck` before it reaches `getattr_static()`.
- A `__class__` property returning the implementation's class makes both
  `isinstance(p, Implementation)` and `isinstance(p, Service)` `True`.

Proposed: two sentences after line 306, no listing.

    Two escapes exist, and both lie.
    `Service.register(Proxy3)` tells the ABC machinery to answer `True`
    without checking anything,
    and a `__class__` property returning the implementation's class makes
    `isinstance()` answer for the wrong object.
    Each satisfies the runtime check and neither satisfies a type checker,
    which is the honest summary: a surrogate is not the thing it fronts for,
    and code that needs it to be should ask for a method instead.

If you would rather not hand a reader `__class__`-spoofing at all, keep only
the `register()` half.

[] Reject
**Lines 267-268 — the forwarding `__setattr__()` is described but never
shown, and the described version is the one that fails.**

    A surrogate that must forward writes defines `__setattr__()` as well,
    and that method has to let the proxy's own attributes through
    or the assignment in `__init__()` recurses.

That is accurate and I verified the failure, but it leaves the reader with a
warning and no working idiom, immediately after a listing that showed the
broken behavior. The chapter's own "near-miss" is the obvious next thing a
reader writes, and it dies with `RecursionError` rather than a useful message.
I confirmed on the pinned 3.15:

    class Naive:
        def __init__(self, impl: Any) -> None:
            self._impl = impl                 # RecursionError right here
        def __getattr__(self, name: str) -> Any:
            return getattr(self._impl, name)
        def __setattr__(self, name: str, value: Any) -> None:
            setattr(self._impl, name, value)

Proposed listing, verified clean under `ty`, `ruff` (70 cols), and its
markers, to follow line 268:

```python
# proxy_setattr.py
from typing import Any

class Settings2:
    def __init__(self) -> None:
        self.level = "low"

class WriteProxy:
    def __init__(self, impl: Any) -> None:
        object.__setattr__(self, "_impl", impl)
    def __getattr__(self, name: str) -> Any:
        return getattr(self._impl, name)
    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._impl, name, value)

settings = Settings2()
p = WriteProxy(settings)
p.level = "high"
print(p.level, settings.level)
#: high high
```

Worth noting in the prose: the `# type: ignore` that `proxy_writes.py` needed
is gone, because declaring `__setattr__()` is what tells the checker the proxy
accepts arbitrary attributes. That is the static half closing at the same time
as the runtime half, and it makes the point of line 264-266 land.
(Rename `Settings2`/`WriteProxy` if the suffix-dropping finding above is
taken.)

[] Reject
**Lines 427-433 — `counting_proxy.py` uses `self._impl` 250 lines after the
chapter argued the double underscore earns its place.**
Line 181-184 says the double underscore on `self.__implementation` "earns its
place here: the name mangles ... so it cannot collide with an attribute the
implementation carries." Every other proxy in the chapter follows that
(`proxy_1.py`, `proxy_2.py`, `dunder_bypass.py`, `proxy_writes.py`,
`proxy_identity.py` all use `self.__implementation`). `CountingProxy` uses
`self._impl` and `self.calls`, both single-underscore, and both shadow an
implementation attribute of the same name, which is the collision the earlier
paragraph warned about.

This is the house-style trigger: an unexplained deviation from an idiom the
book just justified.

Proposed: leave it as it is and add one clause where the reader will notice,
after line 455 — something like "`CountingProxy` uses single underscores so
the recursion trap below can name `self._imp` without the mangling getting in
the way." Renaming to `self.__impl` is the other option, but it drags exercise
4 and line 468 (`a misspelled self._imp`) along with it, and mangled names in
a typo demo are harder to read, so I do not recommend it. Either way the
deviation should stop being silent.

[] Reject
**Lines 150-165, 243-250, 287-295 — the numbered class names are noise, and
they run out of order.**
Reading order gives `Proxy` (`proxy_1.py`), `Proxy2` (`proxy_2.py`), `Proxy`
again (`dunder_bypass.py`), `Proxy4` (`proxy_writes.py`), then `Proxy3`
(`proxy_identity.py`); implementations run `Implementation`,
`Implementation2`, `Words`, `Settings`, `Implementation3`, `Implementation`.
Each listing is its own module, so nothing collides and the suffixes buy
nothing. Two concrete costs:

- `Proxy4` is introduced before `Proxy3`, which reads like a missing listing.
- `Implementation2.f()` prints `Implementation.f()`. A reader who is checking
  the output against the code has to stop and decide whether that is a bug.

Proposed: drop every numeric suffix. `Implementation` and `Proxy` in each
file, `Settings`/`Words` where the domain name is better. Prose that has to
change with it: line 177 (`Proxy2` names no method of `Implementation2`),
line 183 (`_Proxy2__implementation` becomes `_Proxy__implementation`),
line 265 (`Proxy4` declares no `level`), and the `proxy_identity.py` marker
`#: False False` is unaffected because `isinstance(p, Implementation3)`
becomes `isinstance(p, Implementation)` with the same answer.
`dunder_bypass.py`'s `#: True` marker depends on the class being named
`Proxy`, which the rename preserves.
Reported rather than applied because it touches five listings and four prose
sentences, and the suffixes may be a deliberate hand-hold.

## Other files

These are outside `Chapters/26_Surrogate.md`, so I did not touch them.

**`Solutions/26_Surrogate.md`.** Three small style items, none of which change
any output:

- Line 90: `from __future__ import annotations` in `exercise_3.py`. Annotations
  are lazy by PEP 649 on the book's Python and the style skill says forward
  references need no quotes and no `__future__` import. I confirmed the file
  runs and type-checks with the line deleted.
- Lines 14, 93, 98: bare `list` (`def query(self) -> list:`,
  `data: list`, `data: list | None = None`). The book's typing rules ask for a
  parameterized `list[int]` / `list[object]`.
- Line 216: `raise PoolExhausted(f"all {POOL_SIZE} in use")` reads the module
  constant while the pool's real capacity is the `size` argument, so a
  `Pool(3)` would report "all 2 in use." Store the size on the pool and use it,
  or drop the number from the message.

## Cross-chapter

**Chapter 29 (`29_Changing_the_Interface.md`) — no edit required; two notes.**

1.  The disambiguation map at 29:302-312 is consistent with this chapter as it
    now stands. Its Proxy row cites GoF's same-interface definition and then
    says "Surrogate takes the looser view of the first row," which is the
    correct summary of 26:62-68. If you take my first finding above (making
    the change of frame explicit at 26:66-68), 29 needs no matching change —
    the two ends still agree, and 29's sentence stops being the only place the
    disagreement is named. The anchors both ends use (`26_Surrogate.md#proxy`,
    `29_Changing_the_Interface.md#telling-the-wrappers-apart`) resolve;
    `heading_links.py` is clean.
2.  `29_Changing_the_Interface.md:181` says "`__getattr__()` reading
    `self._adaptee` recurses forever on an instance built without
    `__init__()`, which is what `copy.copy()` and `pickle` do." I verified
    that (`copy.copy`, `copy.deepcopy`, and `pickle.loads(pickle.dumps(...))`
    all raise `RecursionError` on a `__getattr__` proxy on the pinned 3.15),
    and I added the same `copy.copy()`/`pickle` clause to 26:470 so the
    abstract case is concrete where the trap is taught. That makes 29's
    mention a repeat. **My recommendation is to leave 29 alone**: its sentence
    adds the `__reduce__()` remedy and applies the trap to an Adapter, which
    is a different context. If you would rather de-duplicate, the edit in 29
    is to shorten "which is what `copy.copy()` and `pickle` do" to "as
    [Surrogate](26_Surrogate.md#proxy) notes" — but that is a change in 29 and
    I have not made it.
3.  If the Proxy/Decorator boundary matters to you earlier than chapter 29,
    26 currently never mentions Decorator. Its one forward link (26:68) points
    at the whole table, which does include the Decorator row, so this is
    covered but only by implication. A reader building a `__getattr__()`
    wrapper in chapter 26 who read chapter 14's pizza Decorator has no
    signpost. This would be a change in 26, not 29, and I list it here only
    because it is part of the same thread; I did not make it because the
    forward link already reaches the answer.

**Chapter 11 (`11_Testing.md`) — no edit required; note only.**
I added a named link at 26:182 to
`11_Testing.md#white-box-and-black-box-tests` for name mangling, matching what
`24_Singleton.md:339` already does. That anchor is now load-bearing from three
chapters. Chapter 11's reviewer proposed moving the "White-Box and Black-Box
Tests" section; the anchor derives from the heading text, not its position, so
the move is safe, but a retitle would break all three links.

## Already applied

Four fixes are in `Chapters/26_Surrogate.md` already; they are recorded here so
this file is a complete account of the review, not for you to apply again.

1.  Line 176-180. "`Proxy2` is completely generic, and not tied to any
    particular implementation" contradicted the listing, whose `__init__()`
    constructs `Implementation2()`. Reworded so the genericity claim attaches
    to the forwarding, with a sentence naming the tie that remains and how a
    constructor argument removes it.
2.  Line 271. "`isinstance(p, Words)` is `False`" named a class from two
    listings earlier while `p` came from the listing just above and the
    listing just below uses `Implementation3`. Replaced with a general
    statement that the listing then demonstrates.
3.  Line 470. Named `copy.copy()` and `pickle` as the concrete case of "an
    instance built without `__init__()`," verified on the pinned 3.15. See the
    chapter 29 note above.
4.  Line 475-476. "counts only callable accesses" described behavior the test
    does not check and the proxy does not have: the count happens when the
    returned wrapper is *called*, not when the attribute is read. Reworded to
    "counts calls without counting a plain attribute read."

All gates pass after these: extract (in sync), `validate_output.py`, `ty`,
`ruff`, `pytest`, `run_examples.py`, `heading_links.py`, `banned_phrases.py`,
`reflow_prose.py`.
