[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/29_Changing_the_Interface.md`
in the clean-slate sweep. The mechanical layer is sound: all `#:`
markers validate, `ty`, ruff, and pytest are clean on
`build/examples/29_Changing_the_Interface`, every script runs, and all
cross-reference anchors resolve. The checker claims were probed
individually on the pinned `ty` (0.0.70) and all hold: removing the `/`
from `WhatIUse.op()` makes the `WhatIUse2.op()` rename an
`invalid-method-override` even with the `Any` annotation ("the
parameter named `what_i_have` does not match `what_i_want` (and can be
used as a keyword parameter)"), so the `/` really is what lets the
listing compile; annotating the override's parameter precisely as
`WhatIHave` is `invalid-method-override` with the Liskov info line, as
the prose says; a call to a whole-function `@deprecated` method gets
`warning[deprecated]`, so the listing's `# type: ignore` is needed; and
a call resolving to a `@deprecated` `@overload` gets no diagnostic from
`ty`, confirming "checker support for it lags the whole-function form,
so verify your checker reports it before relying on it." The runtime
claims also held: `warnings.deprecated` on a class warns on both
construction and subclassing (exercise 2's solution markers show the
two `DeprecationWarning`s), and PEP 565's `__main__`-only default
display matches "Python hides those by default outside `__main__` and
test runners." Cross-chapter ends are consistent: chapter 20's
`PairCoord` carries the comment "Adapter: uses composition, not
inheritance", chapter 21's "the remaining difference is intent" is what
the wrapper table cashes in, and chapter 26's ABC-vs-Protocol
comparison is where the intro's "compares those two" points.
`Solutions/29_Changing_the_Interface.md` covers all four exercises. One
factual error surfaced, in the deprecation section (first entry below).
No live blocks this run: every finding had one defensible answer.

## Applied directly

- Deprecation section: "A message is optional but should say what to
  use instead" is now "The message is required, and it should say what
  to use instead." Probe-verified: `warnings.deprecated` has signature
  `(message: str, /, *, ...)`, and a bare `@warnings.deprecated()`
  raises a `TypeError` (missing required positional argument
  `message`).
- Closing paragraph: "Deprecation is the move that is not safe" is now
  "Retiring an interface is the move that is not safe". The section
  spends a paragraph establishing that the deprecation mark is the safe
  part ("existing callers get a warning, not a break"), so calling
  deprecation unsafe contradicted it; retiring, the arc that ends in
  deletion, is the unsafe move, and it echoes the section title.
- Intro to the same section: "leaving it undocumented means nobody
  notices" is now "leaving it unmarked", tying into "marks a function,
  method, or class" one sentence later; the old interface is
  documented, the departure is what goes unmarked.
- `__getattr__()` trap: "recurses forever" is now "recurses to a
  `RecursionError`", matching what actually happens and chapter 26's
  wording for the same trap.
- Test intro: "both halves of that behavior" is now "both halves of the
  adapter's behavior"; the antecedent sat two paragraphs back, behind
  the dunder and copying traps.
- Exercise 2: "warns while `render()` no longer does" is now "warns
  while calling `render()` does not"; `render()` never warned in
  `deprecating.py` (`to_string()` did), so "no longer" pointed at a
  change that never occurred. The solution's prose already says "runs
  without a word", so it needed no change.
- PairCoord reference: "You have already seen a real one:" is now "You
  saw a real one in [Rethinking Objects]:" (watch-list "already"; the
  named chapter carries the back-reference).
- Deprecation listing prose: "records the warnings instead of printing
  them" is now "records the warnings and prints the record"; the
  listing does print, from `caught`, and the old wording read as if it
  printed nothing.
- Façade: "You can easily get this effect" dropped "easily".
- Adapter variations: "the choice among them is purely one of
  packaging" dropped "purely"; the previous sentence's "differ only in
  where the adaptation lives" carries the contrast.
- Ran `make reflow CH=29` over the edited prose.

## Considered and declined

- "A Façade often takes the form of a [Singleton] [Abstract Factory]"
  stays although `facade.py`'s class of static methods is structurally
  neither (nothing is instantiated, and no abstract interface exists).
  The sentence describes the common GoF-era form rather than labeling
  the listing, "get this effect" marks the listing as an
  approximation, and the module paragraph cashes in the Singleton half
  ("it loads once, and every importer shares the same module").
- "Adapter in Python" gets no Protocol listing to accompany "name the
  requirement with a `Protocol` listing `f()`": chapters 8 and 26 both
  show that substitution, and repeating it here would add a listing
  with no new mechanism.
- `ProxyAdapter` and `Adapter` keep hand-written `__init__()`s rather
  than becoming dataclasses: minimal wrapper stand-ins, the same call
  chapter 26 recorded for its proxies.
- The wrapper table's Adapter row keeps "What it adds: nothing", which
  a reader might contest since `f()` combines `g()` and `h()`: the
  "Remove it and you lose" column resolves it (only the fit is lost,
  no behavior), and exercise 4's solution spells the distinction out.
- "The approaches differ only in where the adaptation lives" keeps
  "only": the exclusion is the sentence's point.
