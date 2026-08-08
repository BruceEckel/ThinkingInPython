[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Six fixes were applied to `Chapters/14_Decorators.md` directly and are not
repeated as findings; they are listed at the end of this file for the record.

---

[] Reject

**Section: "Decorators That Take Arguments" — the forgotten-parentheses
paragraph points the reader at the wrong diagnostic.**

The chapter says:

> The annotations catch it:
> `ty` reports that `greet` expected a callable and got a `str`.

That is true, but it is the *second* error. Checked here with ty 0.0.65,
`@repeat` without parentheses produces two diagnostics, and the first one lands
on the decorator line itself and names the actual mistake:

```
error[invalid-argument-type]: Argument to function `repeat` is incorrect
  --> _probe.py:13:1
   |
13 | @repeat
   | ^^^^^^^ Expected `int`, found `def greet(name: str) -> str`
```

The one the chapter quotes appears four lines lower, at `greet("Bob")`, and
says `Expected (...) -> Unknown, found Literal["Bob"]` — which is a harder
thing to read back to the missing `()`.

Proposal: replace the last sentence of that paragraph with

> The annotations catch it, and they catch it at the decoration rather than at
> the call: `ty` reports that `repeat` expected an `int` for `times` and got a
> function.

Alternative, if you want both: keep the existing sentence as a second one, so
the reader learns that the downstream call is also flagged.

---

[] Reject

**Section: "Decorators That Take Arguments" — `times=0` is treated as a fact of
life rather than a design choice.**

The chapter says:

> That first call happens unconditionally,
> so `times=0` and a negative `times` still call `func` once, not zero times.

and `test_repeat.py` pins that behavior in with `(0, 1)` and `(-1, 1)` rows. The
stated reason is a typing constraint (`result` must hold an `R`), but the
consequence is that `@repeat(times=0)` silently means "once", which is the
opposite of what a reader would expect and is the kind of thing the rest of the
book validates at the boundary.

Proposal: add one line to `repeat()` (and to `repeat_class.repeat.__init__()`):

```python
if times < 1:
    raise ValueError(f"times must be >= 1, got {times}")
```

and change the two parametrize rows to a `pytest.raises(ValueError)` case, then
replace the "still call `func` once" sentence with a sentence saying the
argument is validated where it arrives, at decoration time, so the failure is
reported at the `@` line rather than at some later call.

Cost: two listings and two test listings change; the "This shares `repeat.py`'s
edge case" sentence before `test_repeat_class.py` becomes "This validates
`times` the same way `repeat.py` does."

Alternative, if you want to keep the current behavior: say plainly that it is a
deliberate simplification rather than presenting it as a consequence of the
return type, since it is not — `times < 1` could raise instead.

---

[] Reject

**Section: "Decorators as Classes" / `method_decoration.py` — `Logged`
contradicts the lowercase-decorator rule the section just stated.**

The section opens with:

> These classes are named in lowercase, against the usual `PascalCase` rule,
> because a decorator is used like a function at the call site.
> `property`, `staticmethod`, and `functools.partial` are all lowercase classes
> for that reason.

`trace`, `count_calls`, and `repeat` all follow it. Three listings later,
`method_decoration.py` introduces `Logged` and applies it as `@Logged`, which is
the exact case the rule covers, with no explanation. This is the sort of
unexplained deviation that reads as drift rather than as a point being made.

Recommended fix: rename `Logged` to `logged` in the listing and in the three
prose mentions ("`Example.method` is a `Logged` instance", "So `example.method(5)`
really calls `Logged.__call__(...)`", and "a `__call__`-based class, like
`Logged` above, does not" in "Decorators You Already Know"). The `#:` marker is
unaffected — the `TypeError` names `Example.method`, not the decorator.

Alternative: keep `Logged` and add half a sentence saying the capital is
deliberate here because this one is a counterexample, not a decorator you would
ship. I prefer the rename; the counterexample is still a decorator at its call
site, which is what the rule is about.

---

[] Reject

**Section: "A Limitation: Methods Need a Descriptor" — the working case is
asserted but never shown.**

The section shows the class form failing on a method, then says:

> A function needs none of this: it is already a descriptor,
> so `wrapper()` in the function form binds to an instance like any other
> method.

The reader has just watched the failure in full, with the exception text, and
now has to take the success on faith. The contrast is the whole point of the
section, and it is one-sided.

Proposal: add a short listing immediately after that sentence, using the
already-defined `tracer.trace`:

```python
# method_function_form.py
from tracer import trace

class Example:
    @trace
    def method(self, x: int) -> int:
        return x

example = Example()
print(example.method(5))
#: -> method(<...>, 5)
#: <- method = 5
#: 5
```

The `repr` of the instance is not stable, so the listing needs a `__repr__` on
`Example` (or a `@dataclass`) before the marker can be pinned; adding
`def __repr__(self) -> str: return "Example()"` makes the first marker line
`-> method(Example(), 5)`, which incidentally shows the reader that `self`
arrived, which is the thing being claimed.

Cost: one new listing plus the `norun`/sync round trip. It also makes exercise 5
land better, since the reader will have seen both halves.

---

[] Reject

**Section: "Function Form or Class Form?" — a restated sentence and a run of
clipped ones.**

Two separate things in one short section.

First, the closing sentence of the opening paragraph repeats what the paragraph
already said:

> The arguments go to the constructor, and the function arrives later,
> at `__call__()`.
> The function form hides this shift inside an extra nested `def`.
> The class form makes it visible.
> The function moves from `__init__()` to `__call__()` when the decorator gains
> arguments.

The last line is the second line said again, and it lands after two sentences
that have moved on to the comparison. Proposal: cut it, or move it up to
directly follow "The arguments go to the constructor..." as the summary of that
pair.

Second, the `@rule` paragraph is five short sentences in a row, which reads
unlike the surrounding prose:

> That argument-capturing class-based decorator scales up to small frameworks.
> A build tool or task runner can offer a `@rule(target, *deps)` decorator.
> Its constructor records the target and dependencies.
> Its `__call__()` registers the decorated function in a class-level table with
> that metadata.
> A driver later walks the table to run things in order.
> The decorator becomes the registration mechanism for the whole system.

"That argument-capturing class-based decorator" also has no clear referent; the
preceding sentence is about "the class form" generally. Proposal:

> The class form with arguments scales up to small frameworks.
> A build tool can offer a `@rule(target, *deps)` decorator whose constructor
> records the target and its dependencies,
> and whose `__call__()` registers the decorated function in a class-level table
> with that metadata.
> A driver walks the table later and runs the rules in order,
> so the decorator becomes the registration mechanism for the whole system.

---

[] Reject

**Chapter-level: "Stacking Decorators" sits after the class digression, and the
four middle transitions are unstated.**

Writing one line per section for what it assumes and what it introduces, nothing
later appears in an earlier "assumes" column — the chapter is sound on that
test. What it is weak on is *why each section follows the one before*. The intro
→ "Maintaining the Wrapped Interface" → "Decorators That Take Arguments" run has
a real argument (the naive wrapper loses the identity; then it needs to be
configurable). "Decorators as Classes" is justified too ("a decorator is any
callable"). But the next four sections open with no reason:

- "Stacking Decorators": "You can apply more than one decorator."
- "Decorating Classes": "You can apply a decorator to a class instead of a
  function."
- "Decorators Are Just Function Calls": restates the intro's desugaring.
- "The Decorator Pattern": this one *is* justified, by contrast with `@`.

Proposal, in order of how much I would do: [[do 1 & 2]]

1. Move "Stacking Decorators" up, to directly follow "Decorators That Take
   Arguments", and rewrite `stacking.py` and `test_stacking.py` to import from
   `tracer` and `repeat` rather than `trace_class` and `repeat_class`. The
   output is identical (verified: `tracer.trace` prints the same `->`/`<-`
   lines and `repeat.repeat(times=2)` repeats the body the same way), and it
   completes the function-decorator arc — wrap, preserve, configure, compose —
   before the class form arrives as a variation. "Decorators as Classes" then
   flows straight from stacking's "each wrapper preserves the interface of what
   it wraps" into "a decorator is any callable that accepts one argument."
   Price: the two stacking listings change their imports; the sentence "Stacking
   works because each wrapper preserves the interface" stays valid; no other
   chapter links to `#stacking-decorators` (checked), so no cross-references
   break. The class section loses the incidental demonstration that class-form
   decorators stack, which one sentence in "Function Form or Class Form?" can
   replace.
2. Give "Decorating Classes" a one-sentence opener tying it to what came before,
   e.g. "Everything so far decorated a function. The `@` line does not care:
   a `class` statement is decorated the same way, and the decorator receives
   the class object."


If you take only one of these, take (1).

---

[] Reject

**Section: "Decorating Classes" — `register.py` carries the two registry traps
that chapter 27 spells out, and 14 is where the reader meets them first.**

`register.py` keys on `cls.__name__` and registers at import time. Chapter 27
tells the reader both consequences, for its `__init_subclass__` registry:

> a subclass defined in another module joins the registry only when that module
> is imported. The classic failure is a plugin that "never registered" ... The
> registry also keys on `cls.__name__` alone, so two classes that share a name,
> from different modules, silently overwrite each other.

Chapter 14 comes first, so this is the reader's first name-keyed registry, and
it says nothing. Given the chapter already forward-references 17 for
`__init_subclass__` two lines later, a pointer costs almost nothing.

Proposal: after "it exists only for the side effect of recording the class.",
add:

> A registry filled this way is only as complete as the imports that ran:
> a class in a module nobody imported never registers.
> Keying on `cls.__name__` also means two same-named classes from different
> modules overwrite each other.
> [Factory](27_Factory.md#the-pythonic-factory-a-dictionary) returns to both.

The heading in 27 is "The Pythonic Factory: a Dictionary"; `heading_links.py`
will confirm the slug when this lands.

Alternative, if you would rather keep the section to two sentences: drop the
caveats and just add the cross-reference sentence.

---

[] Reject

**Section heading: "Decorators Are Just Function Calls" — a diminisher in a
heading, and the title does not name the section's content.**

Two small things. "Just" is the diminisher the style watch list flags, and
here it is load-bearing enough to be worth rewording rather than deleting. More
usefully, the section's content is two genuine surprises — the thing decorated
need not come from a `def`, and the thing returned need not be callable — and
the current title names neither; it restates the desugaring the chapter opened
with, which is why the section's first sentence has to re-establish that context
("as the `@hijack` example showed at the start of this chapter").

Proposal: retitle to "What `@` Does Not Require", and open with the two
surprises rather than the recap:

> `@` puts two constraints on what it decorates and none at all on what comes
> back.

No cross-reference names this heading (checked: nothing links to
`#decorators-are-just-function-calls`), so the rename is free.

---

[] Reject

**Section: "Decorators You Already Know" — the closing sentence contradicts the
paragraph it closes.**

The paragraph says `@property`, `@cached_property`, `@staticmethod`, and
`@classmethod`

> return a descriptor instead of a plain wrapper

and then closes with

> They are ordinary decorators,
> built from the closures and callables this chapter covered.

The descriptor protocol is exactly the piece this chapter did *not* cover — the
chapter said so itself in "A Limitation: Methods Need a Descriptor" and sent the
reader to chapter 17. As written, the closing sentence takes back the
distinction the paragraph just drew.

Proposal:

> Understanding any of these needs no new syntax.
> They are ordinary decorators;
> the only machinery this chapter did not cover is the descriptor protocol the
> first four of them return,
> which [Metaprogramming](17_Metaprogramming.md#learning-a-name-with-__set_name__)
> takes up.

---

[] Reject

**Exercises — exercise 5 needs material this chapter does not teach, and is the
one exercise with no solution.**

> 5.  Give `trace_class.trace` a `__get__()` method so it works correctly when
>     applied to an instance method.

The chapter names `__get__()` three times and never shows one; the descriptor
protocol is taught in chapter 17, which the reader has not reached. Every other
exercise is answerable from this chapter. `Solutions/14_Decorators.md` has
solutions 1, 2, 3, 4, and 6 — 5 is the only gap, which suggests it was hard to
answer from here too.

Proposal:

- replace it with an exercise the chapter does support. The best unclaimed
  candidate is the decorator that works both with and without parentheses
  (`@memo` and `@memo(maxsize=10)`), which is a real thing readers need to write
  and which exercises the two-step call the chapter spends a page on.

`Solutions/14_Decorators.md` needs the missing entry. I did not
touch `Solutions/`.

---

[] Reject

**Exercise 1 — `slots_report` is named for something it does not do.**

> 1.  Write a class decorator `slots_report` that prints the name of each class
>     it decorates and returns it unchanged

Nothing in the exercise, or in the solution, touches `__slots__`. The name
promises a slots report and delivers a name print, which will send at least some
readers to look up `__slots__` before they realize it is not involved.

Proposal: rename to `announce` (or `report_class`). This also touches
`Solutions/14_Decorators.md`, whose exercise-1 heading, listing, and `#:`
markers all use the name; I did not edit `Solutions/`.

---

## Cross-chapter

Nothing in this chapter requires an edit to another chapter. Two items to be
aware of if the neighboring chapters get edited:

- **`Solutions/14_Decorators.md`** (not a chapter, but out of my scope): it has
  no solution for exercise 5, and its exercise-1 solution types the class
  decorator as `def slots_report[T: type](cls: T) -> T`. This pass changed the
  chapter's own `register` from `(cls: type) -> type` to
  `def register[T](cls: type[T]) -> type[T]` (see the applied list below).
  Both spellings are correct; if you want them to match, `type[T]` is the form
  the style skill names ("Use `type[C]` when a class object is passed or
  stored") and the one the chapter now uses.
- **`Chapters/27_Factory.md`** owns the import-time-registration and
  name-collision caveats that back the registries in 20 and 37. The finding
  above proposes 14 pointing at 27 rather than restating them. No edit to 27 is
  needed either way; only the anchor in the proposed sentence has to be checked
  against 27's heading before it lands.
- **`Chapters/29_Changing_the_Interface.md`**'s wrapper-disambiguation table row
  for Decorator ("same" interface, adds "behavior") is consistent with what this
  chapter says in "The Decorator Pattern". No change needed.

---

## Applied in this pass (no action needed, listed for the record)

1. **Near-miss the reader would hit immediately.** The chapter's first three
   wrappers take no parameters, and `*args, **kwargs` then appears in `tracer.py`
   with only its *typing* explained. A reader copying `add_behavior` onto a
   function with parameters gets
   `TypeError: wrapper() takes 0 positional arguments but 2 were given`
   (verified). Added a short paragraph after `typical_decorator.py` naming the
   limit, quoting the error, and pointing at
   [Unpacking Arguments](05_Functions.md#unpacking-arguments).
2. **`update_wrapper` vs `wraps` was described along the wrong axis.** The old
   text said `update_wrapper()` "does for a class instance what `functools.wraps`
   does for a function," which suggests the split is instance-vs-function. It is
   not: `wraps(f)` is `partial(update_wrapper, wrapped=f)`, so the split is
   "decorator form" vs "call it directly," and the class form uses the direct
   call because there is no inner function to decorate. Rewritten to say that.
3. **`register` erased the decorated class's type.** With
   `def register(cls: type) -> type`, `reveal_type(Espresso)` is `type` and
   `Espresso()` is `Any` (verified under ty 0.0.65) — in the one chapter whose
   theme is preserving the wrapped interface for the checker. Changed to
   `def register[T](cls: type[T]) -> type[T]` and added three lines of prose
   saying what `T` buys, mirroring the `**P`/`R` explanation earlier in the
   chapter.
4. **`test_pizza_decorator.py` compared money with `==`.** Chapter 11 teaches the
   opposite ("comparing floating-point numbers, where testing for exact equality
   is unreliable ... `pytest.approx()`") and chapter 37 follows it. The current
   prices happen to be exact binary fractions so the tests pass, but a reader
   adding a `0.20` and a `0.10` topping gets a failing test with no idea why
   (`8.00 + 0.20 + 0.10 == 8.30` is `False`). Switched the three cost assertions
   to `pytest.approx()`.
5. **"Only a `def` or a `class` can follow `@`"** reads as a claim about the
   decorator expression, which since PEP 614 is nearly unrestricted; the intended
   claim is about the decorated statement. Reworded to "A decorator line must sit
   directly above a `def` or a `class`". The syntax-error claim itself is
   correct: both a bare assignment and a `type` alias under `@` fail to compile
   on 3.15 (verified); `async def` and `class` are fine.
6. Ran `reflow_prose.py --write 14` over the result.

Verified but not changed:

- Every `#:` marker in the chapter reproduces exactly; no marker was rewritten.
- All three "the checker rejects this" claims are true under ty 0.0.65:
  `add("x")` / `add(2, 3, 4)` against the `ParamSpec` wrapper, `@repeat` without
  parentheses, and `example.method(5)` against `trace_class.trace`.
- Both the function form and the class form really do preserve the signature:
  `reveal_type` gives `(name: str) -> str` for `@repeat(times=3)` on the function
  form and `(name: str) -> str` for the class form, so "Both forms preserve the
  wrapped function's exact signature" holds despite `repeat`'s `**P`/`R` being
  unconstrained by its own parameter list.
- `inspect.signature()` follows `__wrapped__` through both forms, and
  `add.__wrapped__(2, 3)` works, as the chapter claims.
- `@staticmethod` above and below a function-form decorator both work on 3.15
  (staticmethod objects are callable since 3.10), so there is no ordering trap to
  warn about there.
