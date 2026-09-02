When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

# Whole-book correctness sweep: open decisions

This file is the decision queue left over from a correctness sweep of all 47
chapters, run 2026-09-02. Scope was `Chapters/` only: every prose sentence
making a checkable factual claim about the code, about Python, about a
library, or about this book, verified by running it rather than by reading it.

It is deliberately **not** in `deep_review/`. The blocks below span nine
chapters, and `do-reviews` expects one file per chapter whose name matches the
chapter it applies to. Applying this one is a hand job, not a `do-reviews` run.

**Method.** Each chapter went to one fresh Opus agent with a report-only
brief. Every finding an agent returned was reproduced independently before
anything was applied, and the ones below are the findings that were reproduced
and then *not* applied, because the fact is settled but the remedy is not
mine to choose.

**Numbers.** 56 errors found and fixed, in nine commits (`7583395d` through
`e2e5ba75`). Zero false positives across 47 chapters. Seventeen chapters came
back clean: 01, 04, 15, 16, 21, 22, 23, 24, 25, 26, 31, 33, 39, 45, and the
three that returned only the blocks below. `make sweep` was green before the
sweep started and after it finished, which is the point: none of the 56 was
gate-detectable.

Line numbers below are current as of `e2e5ba75`.

---

## Applied directly

Recorded so a later review does not re-propose them. Each commit message
carries the evidence for its own group.

**Self-referential claims about the book (13).** 02:507 exercise 4 miscounted
`arithmetic.py`'s variables · 02:64 comprehensions missing from the list of
scope sources · 07:450 cited chapter 20 for `slots=True`, which never mentions
it · 08:599 `bytes` claimed absent from the rest of the book · 13:581 "every
`match` in this chapter" false twice over · 14:986 "decorators from earlier
chapters" are from chapter 18 · 20:520 "hundreds" of inherited methods is 48
attributes, 11 public · 28:403 "each test" was two of four · 37:528
`@register` absorbs a material, not an operation · 38:592 chapter 27 states
the recursion rather than showing it · 41:237 tracebacks and pytest are
unaffected by `@wraps` · 44:211 anchor pointed at the problem section, not the
solution · 47:2133 named a technique from a different section and omitted one.

**Misstated mechanisms (14).** 03:267 a hash is machine-word sized, not "a
small integer" · 03:709, 29:375, 47:1979 three separate claims that a
`# type: ignore` lets a listing run · 09:309 restating `ClassVar[int]` on an
override restores a check it does not "add nothing" to · 17:210 `ty` models a
`type()`-built class as unknown, not as the base · 19:1123 a computing thread
does release the GIL · 19:1661 all three executors override `submit()` ·
30:303 an `async` property setter is legal · 34:301 Pandas arithmetic is eager
· 35:44 constant deduplication, not folding · 38:109 `__init__` calls
`__post_init__` · 42:112 and 42:682 `@final` is not what narrows a `Result`.

**Self-contradictions (8).** 19:1123 (GIL, contradicted twice within eighty
lines) · 27:306 "`match` expression" against five other chapters · 36:392
`copy.replace()` on "any immutable value" · 37:414 "the one place the two
sorters disagree" · 38:1246, 38:1265, 38:1285 three exercises whose stated
outcomes `Solutions/38` already contradicts · 42:290 `Err.bind` "accepts any
callable" · 46:25 the two channels ride the yield channel.

**Everything else (21).** 02:382 string methods return values, not strings ·
02:416 `%` and `str.format()` do not share a mini-language · 06:454 `types.py`
does not shadow the stdlib · 11:326 `AttributeError`, not `NameError` ·
12:1220 the two frozen-inheritance mixes fail differently · 18:1208 seven
other listings are also un-run · 20:517 `items` is a public field · 28:338 a
trailing setting binds by keyword · 32:528 the exercise named the wrong
dimension · 35:91 the figure's two cells are not opposite corners · 35:162
only one direction is type-checked · 40:108 deleting the first reset changes
nothing · 43:259 Hypothesis excludes surrogates · 44:156 `match` forces
nothing · 44:245 one of the three approaches is not pure · 47:629 only
priority lives in `controller()` · and the rest recorded in the commits.

---

## 1. Chapter 47: the accessor-`Unknown` claim is false under the `ty` it names

**47:107**, with **47:110-111** and **47:2001** depending on it.

> but under `ty` 0.0.75 the answer comes back as `Unknown` and the checking quietly stops.

Under the installed `ty` 0.0.75 a direct Ability yield types precisely, and
checking continues:

```
name = yield from Ask("What is your name? ")   # reveal_type -> `str`
print(name + 1)   # error[unsupported-operator] ... Has type `str`
```

Same for `yield from Need(Console)` (reveals `Console`) and `yield from
Flip()` (reveals `bool`). Inside the accessor, `yield from Ask(prompt)`
reveals `str`, so 110-111's "an assertion the type checker accepts rather than
a type it worked out" is false as well, and 2001's "two type-checker gaps"
becomes one.

The claim was true under `ty` 0.0.63. `git log -S` shows the version string
became 0.0.75 in `873a498b`, a commit that renamed Part V's files. It was
bumped mechanically, not re-probed. This is the failure mode `CLAUDE.md`
already warns about under "A `ty` upgrade is a book-wide event"; chapter 46's
line 676 alias probe I re-ran separately and it still holds.

Why this is yours and not mine: the passage argues that accessors exist to pin
down a type the checker cannot infer. The checker now infers it. What an
accessor is *for* becomes an open question (naming? uniformity? a stable place
to state the answer type?), and rewriting that argument is an editorial
decision about what the section teaches. Your standing rule is "just modernize
everything, no history of what didn't used to work," which rules out the easy
dodge of narrating the change.

A version I would defend, if you want a starting point: drop the `Unknown`
sentences entirely, and let the accessor earn its place on the grounds the
chapter already gives at 104-105, that it wraps one Ability and declares its
answer type in one spot.

`[] Reject`

---

## 2. Chapter 10: exercise 5's premise never happens

**10:432**

> Report when `B closed` now prints relative to `End of program`,

Performing exactly the edit the exercise specifies (`finalize(self, print,
name, "closed")` to `finalize(self, self.close)`) gives:

```
A opened
B opened
False True
End of program
```

`B closed` never prints, and neither does `A closed`. `close()` is
`self.closer()`, so the callback re-invokes an already-dead finalizer.

`Solutions/10_Foundations--Cleanup.md` silently makes a second change the
exercise never mentions: it rewrites `close()` to `print(self.name, "closed")`
and `a.close()` to `a.closer()`. Only with that extra edit does `B closed`
print after `End of program`.

So either the exercise grows to name both changes, or it is reworded to ask
what actually happens and the solution follows. The lesson survives either
way, since the bound method is what pins the object alive and that is the
half the exercise really wants. This one touches `Solutions/`, which was
outside the sweep's scope.

My recommendation: reword the exercise to ask which `closed` lines still
print and why, then fix the solution to match. Say so and I will do both.

`[] Reject`

---

## 3. Chapter 30: the `changed` flag is `java.util.Observable`, not GoF

**30:24-27**

> The classic design from *GoF Design Patterns* has three parts:
> an `Observer` interface every observer implements,
> an `Observable` base class carrying a `changed` flag,
> and a two-phase notification that sets the flag and then broadcasts:

GoF's Observer is `Subject` (Attach/Detach/Notify) plus `Observer` (Update),
with `SetState` calling `Notify` directly. The `setChanged()` / `hasChanged()`
/ `clearChanged()` / `notifyObservers()` protocol, and the name `Observable`
in place of GoF's `Subject`, are `java.util.Observable`. The listing that
follows is the Java library design.

Neither the agent nor I can open GoF from here, so this is reported rather
than applied. You wrote *Thinking in Java*, which covered `java.util.Observable`
at length, so you can settle in a second what would cost me an unreliable web
search. If it is Java's, the fix is small: attribute the flag protocol to
`java.util.Observable` and let GoF keep Subject/Observer.

[[Change this so that it follows the GoF pattern and remove references to Java if you can]]

`[] Reject`

---

## 4. Chapter 29: the inner-class adapter looks like Java, not GoF

**29:101**

> (GoF adds a fourth placement, an inner-class adapter the adaptee hands out, which is Java packaging for the same forwarding.)

GoF (1994) predates Java and uses C++ and Smalltalk. Its Adapter
implementation section covers class adapters, pluggable adapters (abstract
operations, delegate objects, parameterized adapters), and two-way adapters.
The sentence's own "which is Java packaging" is the tell: a 1994 book cannot
package anything in Java.

The fourth placement most plausibly comes from your own *Thinking in
Patterns* / *Thinking in Java* treatment. Same reasoning as block 3: reported,
not applied, because it is an attribution to a named work you know far better
than I can verify. If it is yours, the fix is one clause.

[[Change this so that it follows the GoF pattern and remove references to Java if you can]]


`[] Reject`

---

## 5. Chapter 37: exercise 7 contradicts itself, and its premise depends on placement

**37:536**

> Add the `Plastic` material and its `plastic.dat` lines to `recycle_dict.py`.
> Confirm that `recycle_dict.py` and `parse_trash.py` need no changes,

Two problems. The first two sentences contradict each other: add it *to*
`recycle_dict.py`, then confirm `recycle_dict.py` needs no changes.

Second, performed literally (adding `class Plastic(Trash)` to
`recycle_dict.py`, as `plastic_dropped.py` does), no test fails: neither
`test_trash.py` nor `test_parse_trash.py` imports `recycle_dict`, so `Plastic`
never enters the registry during the test run. Adding `Plastic` to `trash.py`
instead gives `1 failed, 3 passed`, `test_subclasses_self_register` reporting
"Extra items in the left set: 'Plastic'". `Solutions/37` answers from the
`trash.py` placement.

So the exercise means `trash.py` and says `recycle_dict.py`. Fixing it is a
one-word change plus untangling the first two sentences, but which file the
exercise intends is your call, and the `Solutions/` coupling means I would
rather you confirm than guess.

[[I actually haven't been following the exercises so do your best to untangle this one]]

`[] Reject`

---

## 6. Chapter 36: exercise 4's variant corrupts after a save, not after a restore

**36:167-171**

> The third test checks for the sharing bug.
> If the memento shares a mutable list with the sketch,
> as in the variant that exercise 4 explores,
> drawing after a restore corrupts the snapshot.

Exercise 4 changes only `Memento` to hold the list instead of a tuple copy, so
`save()` stops copying but `restore()` still does
(`self.strokes = list(memento.strokes)`). After a restore the sketch and the
memento hold different lists, so drawing after a restore does *not* corrupt
the snapshot. Running that variant against the three tests:

```
test_restore_rewinds_state           FAIL: got ['a', 'b']
test_memento_ignores_later_drawing   FAIL: got ['a', 'b']
test_drawing_after_restore_spares_memento  FAIL: got []   (type mismatch [] != (), not corruption)
```

The first test catches it first, not the third. Corruption after a restore
needs `restore()` to stop copying too, which the exercise does not ask for.

The conditional itself is fine as a general statement; what is wrong is
attaching it to exercise 4's variant. The narrow fix is to drop "as in the
variant that exercise 4 explores". The broader question, whether exercise 4
should break both `save()` and `restore()` so the sentence becomes true, is
about what you want the exercise to teach.

[[I actually haven't been following the exercises so do your best to untangle this one]]


`[] Reject`

---

## 7. Chapter 08: `object` does not reject *every* operation

**08:35**

> but `object` guarantees nothing about the value once you have it,
> so the type checker rejects every operation you try on it.

`repr(o)`, `str(o)`, `o == 5`, `hash(o)`, and `o.__class__` all check clean on
an `object`-annotated value; only type-specific operations like `o + 1` are
rejected.

Reported rather than applied because the sentence is doing rhetorical work:
it pairs with "`Any` permits every operation instead" on the next line, and
the rejects-every / permits-every parallel is what carries the contrast. The
Opus agent flagged it MEDIUM; the Fable agent weighed it and declined it as
standard simplification. Both readings are defensible, and it is your voice.

If you want it exact without losing the parallel: "rejects every operation
beyond `object`'s own" keeps the rhythm and is true.

`[] Reject`

---

## 8. Chapter 05: a starred argument may follow a keyword argument

**05:114**

> At the call site, every keyword argument must come after the positional ones.

`f(b=2, *[1])` compiles and runs, printing `call: 1 2`. Iterable unpacking may
legally appear after keyword arguments; only explicitly written positional
arguments must precede them, which is what the very next line's
`connect(port=80, "web.example.com")` `SyntaxError` illustrates.

Reported rather than applied because the counterexample needs the `f(b=2,
*[1])` form nobody writes, and correcting it means adding a `*`-unpacking
caveat to a Foundations explanation that has not taught `*` unpacking yet
(that comes at line 333). The cost to a first-time reader may exceed the
benefit.

[[Can we somehow say this is an overview and there are other detaails not appropriate to cover here?
Or some other hand-waving that keeps us from overwhelming the reader in this introductory part]]

`[] Reject`

---

## 9. Chapter 47: the tools table omits `stateless.time.sleep()`

**47:1812**

> Here is every tool from both chapters that acts on a description:

`stateless.time.sleep()` builds a description
(`Depend[Need[Time] | Async, None]`), is imported by `sleep_effect.py`, and is
discussed in chapter 46, but no table row covers it. It is the same shape as
`need()` and `wait()`, both of which sit in the "Four build a description"
row. Every other stateless callable used across the two chapters does appear.

Adding a row means restating the row's count ("Four build a description"), so
it is a small edit with a knock-on. Reported rather than applied because
whether the table means to be exhaustive over the library or over the two
chapters' listings is your intent, not a fact I can check.

[[apply]]

`[] Reject`

---

## 10. Chapter 39: the unlinked-name legend has a counterexample

**39:25**

> An unlinked name means the pattern appears only in this catalog.

The unlinked row "Curiously Recurring Template Pattern (CRTP)" (39:177) does
appear elsewhere: chapter 17's footnote `[^crtp]` names it in italics, shows a
C++ `Singleton<T>` listing, and spends four paragraphs on why Python's eager
`class` evaluation offers no equivalent. The unlinked "Mixin" row (39:187) is
a weaker second case: chapter 17's `mixin.py` shows a `Mixin` class added by
multiple inheritance, though that section teaches metaclass layout rules
rather than the mixin idiom.

Reported rather than applied because the remedy is awkward either way: a
footnote has no anchor to link to, so the choice is between softening the
legend and restructuring. "Appears only in this catalog" may also be intended
to mean "has no section of its own," which is true of both rows.

[[restructure]]

`[] Reject`

---

## Considered and declined

Real observations that I judged should not be acted on, recorded so a later
pass does not raise them again.

- **14:821**, decorating a `functools.partial` or a `__call__` instance.
  Decoration genuinely succeeds for all three named callables; only *calling*
  the result fails, because `report`'s wrapper reads `func.__name__`. The
  sentence says "decorates," so it is under-qualified, not false.
- **15:511**, "A decorator like `repeat` or `hijack` can do all three."
  Neither example does all three alone (`hijack`'s wrapper takes no
  parameters; `repeat` always calls the function at least once). But the
  subject is "a decorator like," the claim is about what the form permits,
  and between them the two examples demonstrate all three capabilities.
  "can do any of the three" would tighten it if you ever want to.
- **30:281**, the `weakref.WeakMethod` cross-reference. `WeakMethod` appears
  nowhere else in the book, and the cited chapter 10 section covers
  `WeakValueDictionary` and `WeakSet` instead. But the sentence reads "for
  weak references, see Cleanup," and that section is exactly about weak
  references.
- **41:1007**, `@cache` on `met()`. Decorating it never reaches the stale
  answer the sentence predicts, because `group: list[str]` is unhashable and
  the first call raises `TypeError`. The impurity argument is sound and is the
  point; `Solutions/41` deliberately separates the two ("the exception says
  nothing about purity").
- **43:146**, "[Concurrency] covers all of this." Chapter 19 covers four of
  the five points but never mentions `functools.partial` ("functools" appears
  nowhere in it). It does cover the pickling and `__main__`-guard material the
  paragraph is about.
- **45:129**, "The first call must therefore be `next()`." `send(None)` also
  starts a fresh generator, which the chapter's own `send_none_is_next.py`
  demonstrates ten lines later. Simplify-then-refine, with the refinement
  immediately adjacent.
- **21:182**, "Most of the patterns in this book are behavioral." Counting
  gives roughly 10 behavioral against 11 others, so a plurality rather than a
  majority, but the classification is contestable enough not to be a fact to
  correct.

## Outside the sweep's scope

Found while verifying, in files the sweep did not cover. Recorded, not acted on.

- **`Solutions/42`, exercise 3.** Its justification for abandoning the generic
  `Ok`/`Err` says "`ty` reports that gap as an error," but a straightforward
  `Result[str, list[str]]` implementation passes `ty`.
- **`Solutions/10` and `Solutions/36`** are coupled to blocks 2 and 6 above and
  will need edits if those blocks are applied.

## Two follow-ups this sweep argues for

Neither is a chapter edit, so neither is a block.

1. **A gate for self-referential claims.** Thirteen of the 56 were prose
   asserting something about another chapter that the chapter does not
   contain. `check_claims.py` deliberately skips this shape: it compares link
   *text* against target *headings*, never a prose assertion about a target's
   contents. A checker that flags "chapter N does/shows/uses X" and verifies N
   mentions X would have caught 07:450 and 14:986 outright and would run in
   the gate for free.
2. **Record the model result.** `tools/rewrite.py`'s `MODEL_NOTES` justifies
   Fable for the judgment passes, on evidence about editing restraint. For
   verification the calibration inverted it: on chapters 08, 09, 16, and 26,
   Opus found three real errors that Fable read past, with zero false
   positives from either model. Verification fails by not looking hard enough,
   which is the opposite failure mode from over-editing, so the existing A/B
   does not transfer. `CLAUDE.md`'s routing table has no row for claim
   verification.
