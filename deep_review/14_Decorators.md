# Deep review: 14_Decorators.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Reconcile the exercises with `Solutions/14_Decorators.md`

**Kind:** exercise
**Where:** section "Exercises" (line ~870), and `Solutions/14_Decorators.md`
**Problem:** the chapter's exercises and the solutions file no longer correspond.
Exercise 1 asks for a `Mushroom` topping added to `pizza_decorator.py`;
Solution 1 is "A `Syrup` extra" built on a `Cappuccino` and an `Extra` base, from a coffee shop.
Exercise 3 asks for a coffee shop built with the object Decorator pattern;
Solution 3 is "A pizza shop, object *Decorator* pattern", and its explanation opens
"This is `coffee.py`'s shape exactly, renamed", naming a listing that does not exist in this chapter
(or anywhere else in `Chapters/`).
Exercises 2 and 4 do match their solutions.
Exercise 5 has no solution, which is normal for this book (chapters 13, 15, and 17 also stop one short).
The two halves look like they were swapped when the chapter's running example changed from coffee to pizza,
and nothing gates the correspondence, so a reader checking their answer to exercise 1 gets an unrelated one.
**Proposal:** swap the *solutions*, not the exercises, since the chapter's pizza running example is the one
the prose and the diagram are built on. Concretely, in `Solutions/14_Decorators.md`:
rewrite section 1 as the `Mushroom` topping added to `pizza_decorator.py`
(one class, `add_cost = 0.60`, then `Feta(Mushroom(Hawaiian()))` printing `$11.35`),
rewrite section 3 as the coffee shop (Espresso, Cappuccino, plus Whipped cream, Decaf, Extra shot),
and delete the dangling `coffee.py` sentence from section 3's explanation.
Alternative, cheaper but worse: swap exercises 1 and 3 in the chapter and repair the numbering,
which still leaves solution 1 answering a question the chapter does not ask
(Syrup on a Cappuccino instead of an extra shot plus whipped cream) and solution 3 rebuilding the pattern
from an inheritance base class rather than the `Protocol` the chapter teaches.
**Cost:** touches `Solutions/14_Decorators.md`, which this review was not allowed to edit.
The rewritten solution 3 should use the chapter's `Protocol`-based shape rather than the
`class Pizza` / `raise NotImplementedError` base it currently uses, so the solution teaches
what the chapter taught. Solution 1's `def __init__(self, drink) -> None` is also missing its
parameter annotation; fix it while it is open.

---

## 2. Warn about the forgotten parentheses on an argument-taking decorator

**Kind:** teaching
**Where:** end of section "Decorators That Take Arguments" (line ~230), or "A Class Decorator with Arguments" (line ~430)
**Problem:** the single most common decorator mistake is writing `@repeat` where `@repeat(times=3)` is meant.
The chapter shows the two-step evaluation carefully but never says what the one-step mistake does.
Verified on the pinned build, both forms fail silently at runtime: `@repeat` on `greet` binds `greet`
to `decorate` (function form) or to a `repeat` instance (class form), so `greet("Bob")` returns a
*wrapper function* and prints nothing at all. No exception, no traceback, and the reader is left
staring at missing output.
`ty` catches both: `error[invalid-argument-type] ... Expected `(...) -> Unknown`, found `Literal["x"]``.
That makes it a rare case where the chapter's typing discipline pays a visible debugging dividend,
which is worth saying out loud.
**Proposal:** add a short paragraph after the two-step explanation in "Decorators That Take Arguments":

    Forgetting the parentheses is the common mistake here.
    `@repeat` without them binds `greet` to `decorate`,
    so calling `greet("Bob")` passes `"Bob"` where `decorate` expects a function
    and hands back a wrapper instead of printing anything.
    Nothing raises an exception, so the only symptom is missing output.
    The annotations catch it: `ty` reports that `greet` expected a callable and got a `str`.

**Cost:** none. No new listing, so no marker to maintain. If you want a listing instead of prose,
it cannot carry a `#:` marker for the silent case (there is no output), so the prose form is stronger.

---

## 3. Move the method limitation before "Function Form or Class Form?"

**Kind:** structure
**Where:** sections "Function Form or Class Form?" (line ~456) and "A Limitation: Methods Need a Descriptor" (line ~487)
**Problem:** the comparison section tells the reader "The form you choose is mostly a matter of taste"
and "Both forms preserve the wrapped function's exact signature for the type checker",
and then the very next subsection shows that one of the two forms breaks outright on methods.
A reader who stops at the comparison, which reads like the section that settles the question,
carries away the wrong conclusion. The limitation is not a matter of taste.
**Proposal:** swap the two subsections so "A Limitation: Methods Need a Descriptor" comes first,
then have "Function Form or Class Form?" close on the limitation rather than ignore it:
change "The form you choose is mostly a matter of taste" to something like
"Outside of methods, the form you choose is mostly a matter of taste",
and add a closing sentence naming the limitation as the one hard reason to pick the function form.
Alternative, if the order should stay: leave the sections where they are and only add the qualifier
plus a forward pointer ("one exception follows") to the comparison section.
**Cost:** `Chapters/17_Metaprogramming.md:434` links
`14_Decorators.md#a-limitation-methods-need-a-descriptor`, and the anchor survives a move,
so `heading_links.py` stays green. No other chapter names either heading.

---

## 4. Show that the decorator body runs at definition time

**Kind:** teaching
**Where:** after `typical_decorator.py`, section opening (line ~70)
**Problem:** the chapter's most-likely reader misconception is that a decorator runs when the decorated
function is called. Nothing in the first three sections disproves it: every listing calls the decorated
function immediately, so decoration time and call time are indistinguishable in the output.
The distinction only surfaces on line ~262 ("the constructor runs once, at decoration") and again in
`run_once.py` near the end, both far past the point where a reader forms the wrong model.
**Proposal:** add one small listing right after `typical_decorator.py` whose output separates the two
phases, along the lines of:

```python
# decoration_time.py
from collections.abc import Callable

def announce(func: Callable) -> Callable:
    print(f"Decorating {func.__name__}")  # type: ignore
    def wrapper() -> None:
        print("Calling")
        func()
    return wrapper

@announce
def cheese() -> None:
    print("Wensleydale")

print("Definitions done")
cheese()
#: Decorating cheese
#: Definitions done
#: Calling
#: Wensleydale
```

with two sentences of prose: the `Decorating` line prints before `Definitions done`,
so `announce` ran while Python was still executing the `def`, not when `cheese()` was called;
only the body of `wrapper()` waits for the call.
**Cost:** one new listing in the chapter's opening run, which is currently very light and fast-moving,
so this is the one place where an extra listing costs pacing. The listing needs the full verify loop
(sync, markers, `ty`, `ruff` at 70 columns, `run_examples`). It also introduces `func.__name__` and its
`# type: ignore` a section earlier than "Maintaining the Wrapped Interface" currently does, which the
prose there explains; either move that one-sentence explanation up or drop the `__name__` from this
listing and print a fixed string.

---

## 5. Say why a class attribute satisfies a `Protocol` property

**Kind:** teaching
**Where:** section "The Decorator Pattern", after `pizza_decorator.py` (line ~805)
**Problem:** `Pizza` declares `cost` and `description` as `@property`, but `Margherita` and `Hawaiian`
satisfy it with class attributes (`cost = 8.00`) while `Topping` satisfies it with real properties.
The prose says only "Both the plain pizzas and the toppings satisfy it structurally",
which does not answer the question a reader looking at the two forms side by side will ask.
This is a genuinely useful fact about `Protocol`, verified under the pinned `ty`: a read-only
`@property` member states that reading the name yields the given type, so any readable attribute
matches, whether it is a property, a class attribute, or an instance attribute.
**Proposal:** add after the "structurally" sentence:

    A read-only `@property` in a `Protocol` requires that reading the name produce that type,
    and says nothing about how. `Margherita` supplies `cost` as a class attribute
    and `Topping` computes it in a property; both read as a `float`, so both match.

**Cost:** none. The claim is about `Protocol`, taught in
[Static Typing](08_Static_Typing.md#structural-typing-with-protocols), which the paragraph already links.

---

## 6. Annotate `Topping.add_cost` as a `ClassVar`

**Kind:** code
**Where:** `pizza_decorator.py`, section "The Decorator Pattern" (line ~750)
**Problem:** `class Topping: add_cost = 0.0`, overridden per subclass, is the exact shape the house style
names for `ClassVar`, and the book applies it consistently elsewhere:
`Chapters/37_Pattern_Refactoring.md:41` has `value: ClassVar[float] = 0.0` on a base with per-subclass
overrides and a paragraph explaining that subclasses need not redeclare it.
Chapter 14 deviates with no stated reason, so a reader comparing the two listings sees the rule
applied in one place and not the other.
**Proposal:** change `add_cost = 0.0` to `add_cost: ClassVar[float] = 0.0` on `Topping`,
adding `ClassVar` to the `from typing import Protocol` line. Subclasses keep bare `add_cost = 0.50`.
Verified: `ty` accepts this and the output markers do not change.
Leave `Margherita.cost`, `Margherita.description`, `Hawaiian.cost`, and `Hawaiian.description`
unannotated, since those are the pizza's own data satisfying the `Protocol` rather than a
shared constant, and annotating all five would bury a minimal pattern illustration in typing.
Alternative: annotate all five as `ClassVar` for internal consistency within the listing,
at the cost of four more lines of noise.
**Cost:** the listing gains one import name. If proposal 5 is also accepted, the two sit in the same
paragraph and should be written together.

---

## 7. Explain the lowercase decorator class names

**Kind:** prose
**Where:** section "Decorators as Classes", after the opening paragraph (line ~262)
**Problem:** `class trace`, `class count_calls`, and `class repeat` are lowercase, against both PEP 8
and the house rule that classes are `PascalCase`. The convention is real (Python's own `property`,
`staticmethod`, `classmethod`, and `functools.partial` are lowercase classes used as decorators),
but the chapter never says so, and a reader who has been holding the naming rule since
[Static Typing](08_Static_Typing.md) sees it broken three times without comment.
`Logged` in `method_decoration.py` is `PascalCase`, which makes the inconsistency visible inside
the same section.
**Proposal:** add one sentence to the section opening:

    These classes are named in lowercase, against the usual `PascalCase` rule,
    because a decorator is used like a function at the call site.
    `property`, `staticmethod`, and `functools.partial` are all lowercase classes for that reason.

**Cost:** none, unless you would rather rename the classes to `Trace`, `CountCalls`, and `Repeat`,
which would break the deliberate parallel with `tracer.py`'s function-form `trace` that the
"Function Form or Class Form?" comparison depends on, and would touch `stacking.py`,
`test_trace_class.py`, `test_count_calls.py`, `test_repeat_class.py`, and `test_stacking.py`.

---

## 8. Broaden the exercise set

**Kind:** exercise
**Where:** section "Exercises" (line ~870)
**Problem:** two of five exercises build the object Decorator pattern (1 adds a topping, 3 builds a
coffee shop from scratch), and three of five sit in the last third of the chapter. Nothing exercises
the function form of a decorator with arguments, `functools.wraps`, `**P`, or class decoration,
which is half the chapter's material.
**Proposal:** replace exercise 1 (the `Mushroom` topping, which is a one-line change and the weakest
of the five) with a class-decoration exercise:

    1.  Write a class decorator `slots_report` that prints the name of each class it decorates
        and returns it unchanged, then apply it to two small classes.
        Compare what it can do to what `register` does.

and add a sixth exercise on decorator arguments in the function form:

    6.  Write a `retry(times)` decorator in the function form that calls the wrapped function
        again when it raises an exception, up to `times` attempts, and re-raises the last
        exception when they all fail. Check that `__name__` survives.

Alternative, if the exercise count should stay at five: keep exercise 1 and drop exercise 3,
whose answer is exercise 1 done at greater length.
**Cost:** `Solutions/14_Decorators.md` needs matching sections, and proposal 1 already reopens that
file. Renumbering shifts every solution heading.

---

## 9. Note the missing `return wrapper`

**Kind:** teaching
**Where:** section "Decorators as Classes" opening, or after `typical_decorator.py` (line ~70)
**Problem:** a decorator that falls off the end without returning the wrapper binds the decorated
name to `None`, and the next call raises `TypeError: 'NoneType' object is not callable`
from the call site rather than from the decorator, so the traceback points nowhere useful.
It is the second-most-common decorator bug after proposal 2's missing parentheses,
and it is a natural companion to the chapter's insistence that `@` is a rebinding.
**Proposal:** one sentence after the `add_behavior` explanation:

    A decorator that forgets its `return wrapper` binds `cheese` to `None`,
    and the failure surfaces at the next call to `cheese()`, not at the decoration that caused it.

**Cost:** none. Skip this one if proposal 2 is accepted and you want only one "common mistake"
aside in the chapter; the two are similar in spirit and back to back they read as a checklist.

---

## 10. Prose repairs

**Kind:** prose
**Where:** scattered, listed with current line numbers
**Problem:** small wording problems, none wrong enough to fix without a decision.
**Proposal:** apply the following:

- line ~39: `Calling `cheese()` runs `doesnt_matter` which never calls `func`` needs a comma
  before the non-restrictive `which`. Line ~40's "The original `cheese()` behavior never happens"
  reads better as "The original body of `cheese()` never runs."
- line ~144: "a bare `Callable` is not guaranteed to have a `__name__` attribute" describes
  `func: Callable[P, R]`, which is not bare. Drop "bare".
- line ~148: "Testing verifies that the wrapper reports the original function's name,
  and it still returns the original result" has a broken parallel. Suggest
  "The tests verify two things: the wrapper reports the original function's name,
  and it still returns the original result."
- line ~223: "but nothing calls itself" is cryptic without naming the misconception it answers.
  Suggest "so the two `@` lines are two separate calls, not one recursive one."
- line ~392: "The class form provides a valuable benefit when the decorator takes arguments"
  is inflated. Suggest "The class form pays off when the decorator takes arguments."
- line ~720: "A module-level constant computed without a decorator is usually clearer for anything
  simpler" leaves "anything simpler" hanging. Suggest "For anything simpler, a module-level
  constant computed the ordinary way reads better."
- line ~849: `@property`, `cached_property`, `@staticmethod` mixes the `@` prefix inconsistently
  within one list, and `functools.cache` / `functools.lru_cache` at line ~859 drop it too.
  Pick one form for the whole paragraph.
- line ~849: "(see [Classes](07_Classes.md#properties), [Classes](07_Classes.md#static-and-class-methods))"
  repeats the link text. Suggest "(see [Properties](07_Classes.md#properties) and
  [Static and Class Methods](07_Classes.md#static-and-class-methods))".
- line ~863: "None of these needed new syntax to understand" has a dangling subject.
  Suggest "Understanding any of these needs no new syntax."

**Cost:** none.

---

## 11. Mention `__wrapped__`

**Kind:** teaching
**Where:** section "Maintaining the Wrapped Interface", after the `wraps` paragraph (line ~120)
**Problem:** the chapter establishes that `wraps` makes the wrapper indistinguishable from the
original, then never says how to get past the wrapper when that is what you want.
A reader who needs to test or introspect the undecorated function has no route.
**Proposal:** add one sentence: `wraps` and `update_wrapper()` also set `__wrapped__` on the wrapper,
pointing at the original, so `add.__wrapped__(2, 3)` calls the function without the tracing,
and `inspect.signature()` follows the chain automatically.
**Cost:** none, though it is a detail rather than a mechanism, and the chapter is already
carrying `wraps`, `update_wrapper()`, and `**P` in the same section.

---

## Cross-chapter thread: checked, no action

`Chapters/29_Changing_the_Interface.md:262` says a Decorator "keeps the interface and layers on behavior",
linking `14_Decorators.md#the-decorator-pattern`. Both halves are established here:
the chapter's opening paragraph (line ~81) states the interface-preserving requirement,
"Stacking Decorators" (line ~567) turns it into the reason layers compose,
and `pizza_decorator.py`'s `Pizza` `Protocol` makes it a checked property rather than an assertion.
The anchor resolves. Proposal 5 would strengthen the `Protocol` half but nothing there is wrong.

---

## Already fixed directly (no decision needed)

- line ~258: "A decorator must be a callable that takes a function and returns a callable" was wrong
  in both halves, and the chapter contradicts it twice later: `register` takes a class,
  and `run_once` returns a `str`, which "Decorators Are Just Function Calls" presents as the point.
  Replaced with "A decorator is any callable that accepts one argument."
- line ~489 and ~533: the chapter claimed the class form does not work on methods and named
  `repeat_class` among the decorators that were kept off methods for that reason. `repeat_class.repeat`
  does work on methods, verified at runtime and under `ty`, because its `__call__()` returns a function
  and a function is already a descriptor. Narrowed the claim to an instance that replaces the function,
  dropped `repeat_class` from the list, and added two lines saying why the argument-taking class form
  escapes.

Verified and unchanged: all thirteen runnable listings produce output matching their `#:` markers
(run individually against the freshly synced `build/examples/14_Decorators`),
`ty check` and `ruff check` pass clean, all 20 tests pass,
`heading_links.py` and `banned_phrases.py` are green after the edits.
Also verified independently: `@` above a bare assignment and above a `type` alias are both
`SyntaxError` as the chapter claims (line ~652), and `ty` does report a missing argument plus a
type mismatch on `example.method(5)` for `trace_class.trace` as the chapter claims (line ~535).
