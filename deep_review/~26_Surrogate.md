[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/26_Surrogate.md` in the
clean-slate sweep. The mechanical layer is sound: all eleven scripts
extract, type-check, lint, and run; the two test files pass; every `#:`
marker is deterministic. The chapter's checker-specific and runtime
claims were probed individually on the pinned toolchain and all hold:
`ty` rejects `run(b: Behavior)` handed a `Surrogate` with "protocol
member `f` is not defined on type `Surrogate`", the wording the chapter
uses; `Service.register(Proxy)` makes `isinstance()` answer `True`
against the `@runtime_checkable` Protocol, and a `__class__` property
makes it answer `True` against `Implementation`; a misspelled
`self._imp`, a `copy.copy()`, and a `pickle` round-trip all surface as
`RecursionError`, confirming both routes into the fallback-hook trap;
and the Python 3.12 `inspect.getattr_static()` claim matches
`proxy_identity.py`'s `False False`. The `__getattr__()` /
`__getattribute__()` contrast is consistent with what
[Data Transfer Objects](../Chapters/22_Data_Transfer_Objects.md) now
says about the `SimpleNamespace` stub. Cross-references into this
chapter's `#proxy` and `#state` anchors (chapters 8, 21, 24, 27, 29,
31, 39) all resolve, `Solutions/26_Surrogate.md` covers all seven
exercises, and the diagram asset exists
(`resources/images/surrogate.svg`). One meaning-changing editorial slip
surfaced, in the Kinds of Proxy list: the smart-reference item had lost
the "in order" that makes reference counting the *means* to
copy-on-write, leaving two unrelated purposes and a dangling "prevent
object aliasing". Applied below. No live blocks this run: every finding
had one defensible answer.

## Applied directly

- Kinds of Proxy, smart reference: "to keep track of the number of
  references..., to implement the *copy-on-write* idiom" is now
  "..., in order to implement...", restoring the original wording's
  causal link (counting references is how copy-on-write knows when to
  copy); the comma version read as two separate examples.
- The fallback-hook trap paragraph was one eight-clause sentence
  (condition, typo example, rebuild example, mechanism, and outcome all
  stacked). It is now the rule first (missing attribute inside
  `__getattr__()` recurses to `RecursionError`, not the
  `AttributeError` that would point at the cause), then the two routes
  as their own sentences: the typo, and `copy.copy()`/`pickle`
  rebuilding an instance without `__init__()` so no `_impl` exists.
  Both routes verified by probe. "the typo" became "the cause" because
  the rebuild route is not a typo.
- `proxy_setattr.py` prose: added the reason the attribute shrinks from
  `__implementation` to `_impl` (mangling rewrites identifiers, not
  string literals, so `object.__setattr__()` would need
  `"_WriteProxy__impl"` written by hand). The switch was silent two
  listings after the chapter said the double underscore matters.
  Verified both directions: the hand-mangled string works, the
  unmangled `"__impl"` string recurses.
- State section: "the checker verifies that `Implementation1` and
  `Implementation2` have everything `run()` calls" is now "supply
  everything the Protocol names". `run()` takes `Any`; the annotations
  on `first` and `second` are what the checker verifies, against
  `Behavior`.
- `CountingProxy` paragraph: "uses single underscores rather than the
  earlier proxies' `self.__implementation`" is now "keeps the single
  underscore"; `WriteProxy` and `Guarded` had switched two listings
  earlier, so "the earlier proxies" no longer described the neighbors.
- Test intro: "confirms calls reach the current implementation, and
  that `change_to()` swaps it" is now parallel ("confirms that ... and
  that ...").
- Dropped watch-list intensifiers: "even simpler" is now "simpler"
  (`__getattr__()` intro), and "`object` already defines `__str__()`"
  lost "already" (the preceding "nothing supplies a default" carries
  the contrast).
- Ran `make reflow CH=26` over the edited prose.

## Considered and declined

- No cross-link from the `__getattr__()`/`__getattribute__()` contrast
  back to chapter 22's `SimpleNamespace` parenthetical: 22's mention is
  one clause inside a typing aside, the contrast here stands on its
  own, and the two are consistent as written.
- The *virtual proxy* gets no listing while *protection proxy* and
  *smart reference* do. Exercise 1 has the reader build one, the
  Solutions file carries it, and a lazy-initialization listing would
  repeat the same `__getattr__()` shape a third time for no new
  mechanism.
- The opening "the *Proxy* is a special case of *State*" stays: it is
  the chapter's thesis, restated structurally at "A *Proxy* has only
  one implementation, while *State* has more than one" and cashed in by
  the conclusion.
- The demo classes (`Settings`, `Words`, `Document`,
  `Implementation1/2`) keep hand-written `__init__()`s rather than
  becoming dataclasses: they are minimal stand-ins for "some object
  with attributes and methods", and dataclass machinery would add a
  second topic to listings whose one new thing is delegation.
- "`run()` never changes and neither does `b`" keeps its watch-list
  "never": the sentence is the State pattern's point, that the caller
  and the surrogate are constant while behavior changes.
