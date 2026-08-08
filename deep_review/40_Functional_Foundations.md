When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**"Lambdas" sits after "Higher-Order Functions", which has already used three
of them.**

`higher_order.py` opens with `map(lambda n: n * n, numbers)` and the section's
own prose discusses lambda-versus-comprehension at length.
Only afterwards does a section define the term, and it has to open by
referring backwards ("The examples above used lambdas as inline arguments").
It is also the only section in the chapter with no listing.

Two ways to fix it. I recommend the first.

**Option A: move "Lambdas" to just before "Higher-Order Functions."**
Rewrite its second sentence from "The examples above used lambdas as inline
arguments, which is where they fit best" to something forward-looking
("The higher-order functions below take them as inline arguments, which is
where they fit best").
Cost: nothing outside this chapter. I checked every cross-reference into
chapter 40 — `#pure-functions`, `#immutability`, `#closures`,
`#functions-as-first-class-objects`, `#partial-application` and
`#leaving-a-gap-with-placeholder` are referenced from chapters 05, 12, 14,
18, 21, 28, 34, 41, 43, 44 and 47, but **`#lambdas` is referenced from
nowhere**, so the anchor can move freely.

**Option B: merge it into "Higher-Order Functions,"** immediately after the
`map()`/`filter()`-versus-comprehension paragraph, which is already making
the same judgement call.
That removes a section heading rather than moving one, and puts all the
"which form should I write" guidance in one place.
It also loses a scannable heading for a named language feature.

Either way, note the overlap with chapter 5's own Lambdas section (lines
349-373): 5 already shows `sorted(words, key=len)` and
`sorted(words, key=lambda w: w[-1])`, and this chapter's `higher_order.py`
repeats `sorted(words, key=len)` with a different word list. The new content
here is the locality argument and the "for anything larger, write a `def`"
rule, which is worth keeping; the `sorted(key=len)` line is not.

---

[] Reject

**The chapter has no conclusion, and no listing the reader could adapt.**

It ends with two lines inside "Composing Functions" —
"The standard library provides these building blocks ready-made;
[Toolkits](41_Functional_Toolkits.md) tours them." — and then Exercises.
Every section here is a correct explanation of one construct, and every
listing is a demonstration of that one construct in isolation. Nothing in the
chapter puts two of them together.

Ask the deep-review question directly: what can the reader do at the end that
they could not do at the start? The honest answer is "recognize six
constructs." Which is a fair result for a foundations chapter, except that
this one opens Part IV and the whole part's argument is that these pieces
*combine*.

Proposed closing section, "Putting the Pieces Together", holding one listing
(verified: runs, `ruff` clean at 70, `ty` clean):

```python
# pipeline.py
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

@dataclass(frozen=True)
class Reading:
    sensor: str
    celsius: float

def warmer_than(limit: float, r: Reading) -> bool:
    return r.celsius > limit

def to_fahrenheit(r: Reading) -> Reading:
    return Reading(r.sensor, r.celsius * 9 / 5 + 32)

def report(readings: Sequence[Reading]) -> list[str]:
    warm = filter(partial(warmer_than, 20.0), readings)
    return [f"{r.sensor} {r.celsius:.1f}"
            for r in map(to_fahrenheit, warm)]

data = [Reading("a", 18.0), Reading("b", 25.0), Reading("c", 30.5)]
print(report(data))
#: ['b 77.0', 'c 86.9']
print(data[0])
#: Reading(sensor='a', celsius=18.0)
```

Every idea in the chapter is present and doing work: a frozen dataclass for
the value, `Sequence` to state that `report()` only reads, two pure functions,
`partial()` to turn a two-argument predicate into the one-argument callable
`filter()` requires, and `map()`/`filter()` for the traversal. The second
`print()` is the payoff line — the input list is unchanged, so the whole
report can be recomputed, cached, or run on another core with no coordination.

The section could close with the one insight the chapter currently leaves
implicit: none of this is a different language. It is ordinary Python in
which each piece happens to depend on its arguments alone, and that single
property is what the next four chapters keep spending.

Reported, not applied, on all counts: a new section changes the chapter's
pacing, and where it goes is your decision. A cheaper version of the same fix
is to move the two-line Toolkits sign-off under a `## What You Can Now Do`
heading and add three sentences, with no new listing.

---

[] Reject

**`closures.py` shows the outcome but not the mechanism, and the prose now
depends on the mechanism.**

The listing prints `20 30`, from which a reader cannot tell whether `factor`
is stored on the function, recomputed, or looked up in some enclosing frame
that is still alive.
The corrected prose in this pass ("`inspect.getclosurevars(tally).nonlocals`
reports `{'count': 3}`") now asserts something the chapter never shows.

Proposed change to `closures.py` (verified on the pinned 3.15 build: runs,
deterministic, `ruff` clean, `ty` clean with no ignore needed —
`getclosurevars()` takes a plain callable, unlike `__closure__`, which `ty`
refuses on a value annotated `Callable[[int], int]`):

```python
# closures.py
import inspect
from collections.abc import Callable

def multiplier(factor: int) -> Callable[[int], int]:
    # The inner function captures factor from this scope:
    def multiply(n: int) -> int:
        return n * factor
    return multiply

double = multiplier(2)
triple = multiplier(3)
print(double(10), triple(10))
#: 20 30
print(inspect.getclosurevars(double).nonlocals)
#: {'factor': 2}
print(inspect.getclosurevars(triple).nonlocals)
#: {'factor': 3}
```

The two dicts make "each returned function remembers its own `factor`" a
thing the reader can see rather than a thing the prose claims.

Reported rather than applied because it changes an existing listing's output
markers and adds an import to a deliberately minimal listing, both of which
are your call. If you take it, the sentence "`double` and `triple` are the
same code with different captured values" can point at the output instead of
asserting it.

---

[] Reject

**"Pure Functions", `why_pure.py`: the listing proves the easy half and the
convincing half is missing.**

The lead-in now ends "And you test it with a single assertion and no fixture,
since there is nothing to set up or restore:", and the listing shows exactly
that — two asserts on a second pure function.
But "no fixture" only means something next to the code that *does* need one,
and the chapter has that code sitting twenty lines above in `withdraw()`.
As written, `why_pure.py` introduces a new function (`slope`) to re-prove
what `double()` already proved, and the section ends with no prose after it.

Proposed replacement (verified: runs, `ruff` clean at 70, `ty` clean,
prints `ok`):

```python
# why_pure.py
def slope(rise: int, run: int) -> float:
    return rise / run

total = 0
def running_total(n: int) -> int:
    global total
    total += n
    return total

# The pure function needs no setup and no teardown:
assert slope(10, 2) == 5.0
assert slope(10, 2) == 5.0
# The impure one needs a reset before each check:
total = 0
assert running_total(5) == 5
total = 0
assert running_total(5) == 5
print("ok")
#: ok
```

with a following line such as
"Delete either `total = 0` and the second assertion fails.
That line is the whole fixture, and purity is what removes it."

Two alternatives if you dislike a second impure function in the chapter:

- Reuse `withdraw()` directly, resetting `balance` between asserts. Cheaper
  conceptually, but the listing then either duplicates `withdraw()` or
  imports `pure_functions`, whose module-level `print()` calls would land in
  this listing's output.
- Convert it to `test_purity.py` with two pytest functions, which matches the
  book's "tests live in their own `test_*.py` file" rule and would give this
  chapter its first test. Costs a `pytest` step the chapter does not
  currently need, and loses the `#:` marker.

I recommend the first.

Separately, worth knowing when you touch this listing: `slope(rise, run)` is
character-for-character the function chapter 44 opens
`divide_by_zero_impurity.py` with, where it is used to ask whether raising
an exception breaks purity. If `slope` stays here, a forward pointer
("[Are Exceptions Impure?](44_Effect_Management.md#are-exceptions-impure)
comes back to this exact function") turns an accidental repeat into a thread.

---

[] Reject

**"Closures": the missing-`nonlocal` failure cannot become a listing, which is
why it was handled in prose instead. Here is what I tried, in case you want to
push it further.**

Forgetting `nonlocal` is the most likely thing the reader does next, so I
drafted a `forgot_nonlocal.py` near-miss listing using the `exceptions.ignore`
helper that `immutability.py` and `hashable.py` already use. It cannot ship:

- `ty` rejects the code outright with
  `error[unresolved-reference]: Name 'count' used when not defined`, so the
  listing would need a `# type: ignore` to pass the gate — on the one line the
  listing exists to draw attention to.
- The runtime message is 74 characters, so the `#:` marker line is 77 and
  fails `ruff`'s 70-character limit. Truncating the message throws away the
  half that makes the point.

So I applied the prose form instead (manifest item 19): the paragraph now
quotes the runtime message verbatim and adds that `ty` catches the same
mistake statically, on the offending line, before the program runs. Both
strings are verified on the pinned 3.15 / `ty` 0.0.65 build.

If you want the demonstration anyway, the workable shape is a listing whose
*point* is the checker rather than the traceback: keep the `# type: ignore`,
add `# noqa: E501` to the marker line, and let the prose say that the ignore
comment is suppressing a real error. I did not draft it because a listing that
needs two suppressions to exist is usually the chapter telling you it should
stay prose.

---

[] Reject

**Exercises: two full sections have none, and `Placeholder` has one of five.**

Coverage today: 1 Pure Functions, 2 Functions as First-Class Objects,
3 Closures, 4 Composing Functions, 5 Leaving a Gap with `Placeholder`.
Nothing exercises **Immutability** (the second-longest section, and the one
carrying the `Final`-is-shallow trap that the book repeats from chapter 20) or
**Higher-Order Functions** (`map`/`filter`/`sorted`, plus the
comprehension-versus-higher-order judgement the section spends a paragraph on).
Meanwhile a `###` subsection gets a full exercise of its own.

Proposed additions:

> 6.  In `immutable_types.py`, add `CONFIG: Final[list[int]] = [1, 2]` and a
>     line that appends to it. Run `ty`, and explain why it reports nothing
>     when `MAX_SIZE = 200` on the next line is an error. Then change the
>     annotation so appending *is* rejected.
> 7.  In `higher_order.py`, replace the `map()` and `filter()` calls with
>     comprehensions, and the `sorted(key=len)` call with one that sorts by
>     last letter. Then delete the `list()` around the `map()` call, print the
>     result, and say what you see and why.

Exercise 7 is deliberately the near-miss: the reader produces
`<map object at 0x...>` themselves rather than reading about it.

Reported rather than applied because the exercise set's size and difficulty
curve are a pacing decision.

---

[] Reject

**"Functions as First-Class Objects", after `dispatch.py`: the chapter's
biggest untaught lookalike pair is a dict of functions versus `match`/`case`.**

`dispatch.py`'s prose says a table of functions "replaces a long `if`/`elif`
chain."
Chapter 13 says the same thing about `match`, and its very first listing
(`http_status.py`) is literally a dispatch on a literal `int`.
The repo's own style skill states the rule the other way round: "Dispatch on
a literal with `match`/`case`, with a `case _:` default, not an `if`/`elif`
chain."
A reader arriving from 13 will ask which one they are supposed to use, and
this chapter never says.

The distinction is real and short: a `match` is code, so a new case means
editing the function; the table is data, so a new case means adding a row,
possibly at import time from another module, possibly at runtime. That is
exactly why the registry in 27 is a dict and not a `match`.

Proposed addition after "The dispatch code never changes.":

> [Pattern Matching](13_Pattern_Matching.md) solves the same `if`/`elif`
> problem with `match`, and the two are not interchangeable.
> A `match` is code: adding an operator means editing the function, and the
> checker sees every case.
> The table is data: adding an operator means adding a row, which another
> module can do at import time and a test can do at runtime.
> Choose `match` when the set of cases is fixed and known to the compiler,
> and a table when the set is meant to grow from outside.

Reported rather than applied because it adds a paragraph to a short section
and because you may be deliberately holding the contrast for chapter 27.

---

[] Reject

**`composing.py`: `compose()` is hard-wired to `Callable[[int], int]` where the
book's own style rule asks for PEP 695 type parameters.**

`thinking-in-python-skill.md`: "Use type parameters (`def f[T](...)`,
`class C[T]`) when a function or wrapper should carry the element type
through." `compose()` is the textbook case of a wrapper that should carry
types through, and the monomorphic version quietly teaches that composition
only works within one type — which is the opposite of the section's claim
that "you build larger behavior by naming a new composition."

Verified generic version (runs, `ruff` clean at 70, `ty` clean, and
`reveal_type(compose(label, increment))` gives `(int, /) -> str`):

```python
# composing.py
from collections.abc import Callable

def compose[T, U, V](
    f: Callable[[U], V], g: Callable[[T], U]
) -> Callable[[T], V]:
    # Return a function that runs g, then feeds the result to f:
    def composed(x: T) -> V:
        return f(g(x))
    return composed

def increment(n: int) -> int:
    return n + 1
def double(n: int) -> int:
    return n * 2
def label(n: int) -> str:
    return f"<{n}>"

increment_then_double = compose(double, increment)
print(increment_then_double(10))
#: 22
print(compose(label, increment_then_double)(10))
#: <22>
```

The second `print()` is what earns the generics: the checker verifies that
`label` accepts what `increment_then_double` produces, and the composed
function's own type is `(int) -> str`, not `(int) -> int`.

Two reasons you might not want this. It adds three type parameters to the
chapter's last listing, when "one new thing per listing" argues for keeping
it plain. And exercise 4 asks the reader to build
`compose(square, increment_then_double)`, which still works verbatim either
way but reads differently once composition can change the type.

Alternative if you want the point without the listing change: leave
`composing.py` alone and add the generic version as exercise 6
("Rewrite `compose()` with type parameters so that
`compose(str, increment)` type-checks. What does `ty` report for the result's
type?").

---

[] Reject

**"Partial Application": `.func`, `.args` and `.keywords` are claimed here and
demonstrated one subsection later, only partly.**

The prose says `partial()` "keeps the bound arguments as data you can
inspect, through its `.func`, `.args`, and `.keywords` attributes."
`partial.py` shows none of them. `placeholder.py` then shows `.args` alone,
and for the `Placeholder` case rather than the keyword case, so the reader
never sees the `.keywords` dict the sentence is actually about.

Proposed two lines at the end of `partial.py` (verified output):

```python
print(square.func.__name__, square.keywords)
#: power {'exponent': 2}
```

This is the difference from a lambda the sentence is selling: `lambda n:
power(n, 2)` is opaque, and `square` tells you what it wrapped and with what.

Reported rather than applied because it lengthens an existing listing whose
current job is one clean idea.

---

[] Reject

**"Leaving a Gap with `Placeholder`": the section is written in a past tense
that raises a version question it never answers.**

"so fixing the third argument *used to mean* fixing the first two", "had no
recourse", "the one `partial()` *could not previously* express."
`functools.Placeholder` arrived in Python 3.14. A reader on 3.12 or 3.13 will
copy this listing and get an `ImportError`, and nothing on the page tells them
why.

Proposed change: add the version to the sentence that introduces it, e.g.
"`functools.Placeholder` (Python 3.14 and later) is a marker that reserves a
position for the caller:".

Reported rather than applied because I could not find a settled convention in
the book for when a version is called out inline — chapter 41's `partial`
entry gives none, while several chapters do mark 3.13+/3.15 features — so
this is a house-style call rather than a correction.

---

[] Reject

**Intro, second paragraph: the arc preview stops at 44 and omits the last
three chapters, so the reader's map of Part IV/V is wrong from line 21.**

The paragraph currently names Toolkits (41), Error Handling (42), Assurance
(43), and Effect Management (44).
The functional arc actually runs 40 through 47:
44 *opens* Part V ("Effects" in `build_site.py`'s `PARTS`), and 45
(Generators), 46 (Stateless) and 47 (Stateless in Practice) are the chapters
where the machinery this chapter builds is finally cashed in.
Chapter 47 closes by pointing back here
("That is the property this book has been circling since
[Foundations](40_Functional_Foundations.md#pure-functions)"), so the far end
of the thread already exists; only this end is missing.

A reader finishing 43 has no idea three more chapters are coming, and a
reader who wants to know where purity actually *buys* something is sent to
43 (an argument) rather than 46/47 (a working system).

Proposed change: end the paragraph with one more sentence, e.g.

> Those four chapters are Part IV.
> Part V then takes the same discipline further:
> [Effect Management](44_Effect_Management.md) tracks a function's effects in
> its type, [Generators](45_Generators.md) supplies the mechanism Python
> already has for describing a computation without running it, and
> [Stateless](46_Stateless.md) and
> [Stateless in Practice](47_Stateless_in_Practice.md) build a checked Effect
> system on top of it.

(That means moving the existing Effect Management clause out of the Part IV
list, which is the substantive part of the change: right now 44 is presented
as the fourth chapter of this part when it is the first chapter of the next.)

Reported rather than applied because it changes the shape of the chapter's
opening promise-of-contents paragraph, which is pacing, and because you may
prefer to keep the preview short on purpose.

---

[] Reject

**MANIFEST — not a proposal. Changes already applied to
`Chapters/40_Functional_Foundations.md` in this pass.**
(All gates re-run and passing: `validate_output.py --tree build/private/40`,
`ruff`, `ty`, `heading_links.py`, `banned_phrases.py`, and
`extract_examples.py` reports chapter 40 in sync. No code listing was changed,
so `Examples/` needed no sync.)

1.  Intro: "a fold from `functools` or `itertools`" replaced with "a cache
    from `functools`, or a sliding window from `itertools`" — "fold" is
    undefined FP jargon in the arc's opening paragraph, and both replacements
    are things chapter 41 actually shows (`cache`, `pairwise`).
2.  "Pure Functions", payoff paragraph reordered so the sentence the colon
    attaches to is the one `why_pure.py` demonstrates. Previously the
    paragraph ended on the caching claim and the listing showed testing. Added
    the link to `functools.cache` and the note that it is wrong on an impure
    function.
3.  "Immutability", opening: added that the immutability of a tuple is
    shallow (`([1], 2)` holds a list anyone can append to). The chapter taught
    shallow freezing for `Final` only.
4.  "Immutability", after `immutable_types.py`: added that `Sequence[int]`
    constrains the callee and not the caller, who still holds the `list` and
    can append to it at any time, including from another thread. The previous
    text ("a constraint the checker enforces, even when the value passed in is
    a mutable `list`") invites the opposite reading.
5.  "Immutability", hashability lead-in rewritten: "unlocks abilities a
    mutable value lacks" → two named properties (a stable hash, sharing
    without a defensive copy). "Abilities" is a formal term in chapters 46/47
    and should not be spent loosely at the start of the arc.
6.  "Immutability", after `hashable.py`: **corrected a misconception the
    listing was reinforcing.** "A `list` can do neither" left the reader with
    "mutable implies unhashable," which is false — a plain mutable instance
    hashes by identity and works as a dict key. Replaced with the actual rule:
    contents-based equality is what removes hashing, which is why `list` and
    an unfrozen `@dataclass` both get `__hash__ = None`, and why `frozen=True`
    gets both back. Verified: `Mutable.__hash__ is None` for an unfrozen
    dataclass; `Plain(1)` works as a key after `p.x = 99`.
7.  "Immutability", closing sentence: "the standard library uses tuples and
    frozen dataclasses" replaced with a claim about how such values are
    normally written. The stdlib barely uses frozen dataclasses.
8.  "Functions as First-Class Objects": the vague "This is the structure
    behind dispatch tables" (circular — the listing *is* a dispatch table)
    replaced with a named link to
    `27_Factory.md#the-pythonic-factory-a-dictionary`.
9.  "Higher-Order Functions": added that `map()` and `filter()` return
    one-shot iterators, so `print(map(...))` shows `<map object at 0x...>` and
    a second pass yields nothing with no error, linked to
    `23_Iterators.md#generators`; noted that `sorted()` must return a list.
    The chapter wrapped every call in `list()` and never said why.
10. "Higher-Order Functions": the `map(str.strip, lines)` recommendation now
    says the two forms are not the same object — comprehension gives a list,
    `map()` gives a chainable iterator.
11. "Higher-Order Functions": "provide separation of concerns" → "separate the
    walking from the work," matching the sentence that follows it.
12. "Closures", after `closures.py`: added that `multiply()` reads `factor`
    and is still pure, because `factor` is fixed at capture — reconciling the
    section with the chapter's own definition of purity as "arguments alone,"
    which nothing had done.
13. "Closures": **corrected a false claim, twice.** "The captured variable is
    reachable only through the returned function, so no other code can read or
    overwrite it" and "Nothing outside `increment()` can reach that state" are
    both wrong. Verified on the pinned build:
    `inspect.getclosurevars(tally).nonlocals` is `{'count': 3}`, and
    `tally.__closure__[0].cell_contents = 100` makes the next `tally()` return
    `101`. Rewritten to say the variable has no name in any enclosing scope, so
    ordinary code cannot reach it, and then to state plainly that this is the
    same kind of privacy as a leading underscore, not a lock.
14. "Closures", after `counter.py`: added that `increment()` is impure and
    deliberately so, and that the contrast with `withdraw()` is the lesson —
    one mutates a name any code can touch, the other a name only it can touch.
    The chapter previously presented hidden mutable state approvingly, three
    sections after opening with a warning against it.
15. "Partial Application": added the near-miss. `partial(power, 2)` binds
    `base`, so `square(5)` would compute `2 ** 5` (verified: `32`). The
    chapter used a keyword without saying why until the next subsection.
16. "Leaving a Gap with `Placeholder`": **corrected the stated reason for the
    trailing-placeholder rule.** "a gap at the end is an unbound parameter"
    contradicts the feature — a gap in the middle is also an unbound
    parameter, and that is the point. Read CPython 3.15's `functools.py`:
    `_partial_new` raises `TypeError("trailing Placeholders are not allowed")`
    because a trailing gap is redundant, not because it is unfilled.
    `__call__` appends the call's arguments after the bound ones, so
    `partial(clamp, 0, Placeholder)` would mean exactly what
    `partial(clamp, 0)` means (verified: `partial(clamp, 0)(150, 100)` is
    `100`). Rewritten to say so.
17. "Composing Functions": "Composition scales by addition" (cryptic) →
    "Composition grows by adding a stage rather than by enlarging one."
18. Three over-long new lines broken at a top-level `,`/`:` for Semantic Line
    Breaks.
19. "Closures", `nonlocal` paragraph: quoted the runtime message verbatim
    ("cannot access local variable 'count' where it is not associated with a
    value") instead of only characterising it, and added that `ty` reports
    `Name 'count' used when not defined` on the `count += 1` line before the
    program runs. Both verified on `ty` 0.0.65 / Python 3.15.0b2. The
    paragraph previously told the reader the message was unhelpful without
    showing it, and never mentioned that the checker catches the mistake at
    the right place.

Also checked and found clean, so no change was made: no use of the "promise"
metaphor anywhere in the chapter (and none introduced); no "reach for"; every
`#:` marker matches stdout on a direct run of the extracted script; no
listing deviates from `thinking-in-python-skill.md` unexplained (the two
`# type: ignore` comments in `placeholder.py` are still required by `ty`
0.0.65 and are explained in the following paragraph); the chapter's
`Final`-is-shallow, frozen-dataclass and closure threads agree with their
other ends in chapters 20, 22, 28 and 44; and chapter 41 defers to this
chapter for both `partial` and `Placeholder` rather than contradicting it.
