[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Chapter-level, the biggest item: the flagship listing does the thing the
chapter tells you not to do, and the fixed version never appears.**

The chapter opens by praising `unittest` for the separation
("Constructing a `TestCase` runs nothing; the test runner calls `run()` on the
finished object"), then the very next listing, `template_method.py`, has
`ApplicationFramework.__init__()` call `self.run()`.
The prose under it endorses that flatly:
"The base-class constructor starts the engine (`run()`), which drives the
application."
Thirty lines later a whole subsection is titled
"Don't Start the Engine in the Constructor," and it ends with
"The reliable fix changes the framework: separate construction from starting,
and have the client call `run()` explicitly on a fully built object."
That fix is then never shown.
The only place in the book where it is written down is
`Solutions/25_Template_Method.md`, exercise 2 (`exercise_2_redesign.py`).
Meanwhile the chapter's own test still carries
`Recorder()  # Constructing it runs the framework`, two paragraphs after the
warning, which reads as an endorsement.

A first-time reader finishes the chapter unsure whether starting the engine
from the constructor is the Template Method or a mistake, because the chapter
says both and demonstrates only the mistake.
There is a second, quieter cost: with `run()` both public, `@final`, and
called from `__init__()`, a reader who writes the natural
`app = MyApp()` followed by `app.run()` runs the whole algorithm twice, and
nothing in the chapter warns them.
`template_method.py` is also carrying four new things at once (`@final`,
`@override`, the `...` step defaults, and the constructor-starts-the-engine
idiom), one of which the chapter later disavows.

Two ways out. I recommend the first [[do this]].

**Option A (recommended): make `ApplicationFramework` the good design.**
Drop `__init__()` from `ApplicationFramework` entirely and end the listing
with `MyApp().run()`.
The prose under it becomes something like:

> Construction builds the object; `run()` starts the engine that drives the
> application.
> The client supplies `customize1()` and `customize2()`, and the application
> runs.
> In a GUI program that engine is the main event loop.

`premature_engine.py` still stands on its own, since its `Framework` is a
*different* framework that does start in the constructor, and the subsection
then explains why `ApplicationFramework` is written the way it is instead of
warning about the design the reader just saw endorsed.
Cost of the move: `test_template_method.py` needs `Recorder().run()` and its
comment changes to something like `# The client starts the engine`; the
`#:` markers are unchanged (same output, same order);
`Solutions/25_Template_Method.md`'s `exercise_3.py` copies
`ApplicationFramework` inline, so it would want the same edit for consistency
(it will still build either way, since it does not import the chapter's
version); exercise 2 keeps working verbatim, because it is written against
`premature_engine.py`, not `ApplicationFramework`; chapter 31's back-reference
("the construction-starts-the-engine choice that drew a warning in that
chapter") reads correctly either way.

**Option B (cheap): keep the classic form, but stop endorsing it.**
Leave the listing alone and replace the paragraph at the top of page,
currently

> The base-class constructor starts the engine (`run()`),
> which drives the application.

with

> The base-class constructor starts the engine (`run()`),
> which drives the application.
> That is the classic form of this pattern, and it carries a trap that
> [Don't Start the Engine in the Constructor](#dont-start-the-engine-in-the-constructor)
> takes apart.

and change the test's comment from `# Constructing it runs the framework` to
`# Construction starts the engine, per the base class`.
This costs three lines and removes the whiplash, but leaves the book with no
listing of the design it recommends.

(Already applied in this pass, and independent of which option you take: the
intro's "a separation this chapter returns to below" is now a named link to
the subsection, so a reader who notices the contradiction can jump straight
to it.)

---

[] Reject

**"Passing the Steps as Functions": the section stops without a chapter
conclusion.**

Every neighbouring pattern chapter closes with a short section that names
what the reader now knows: 23 "The Pattern That Disappeared," 24 "Which
Should You Use?", 26 "One Surrogate, Two Intents," 27 "Which Factory Should
You Use?", 30 "What Stayed Constant." Chapter 25 runs straight from the
class-versus-function trade-off into Exercises. It is also the shortest
chapter in this part by a wide margin (~260 lines against 530-900).

A closing section would be the natural home for the one insight the chapter
currently leaves implicit: the fixed algorithm is only ever as fixed as the
mechanism holding it. Structure fixes it (the function version), a checker
fixes it (`@final`), the interpreter fixes it (`__init_subclass__`), and
discipline fixes it (LSP, which no tool checks at all). Those four are
already in the chapter, scattered; naming them together in four sentences
under a heading like "What Actually Fixes the Algorithm" would let the reader
leave with a way to choose, not just a pattern they recognize.

Reported rather than drafted, since a new section changes the chapter's
pacing and that is your call.

---

[] Reject

**`premature_engine.py`: the marker prints a type name where the message
would teach the mechanism.**

The listing ends with

```python
except AttributeError as e:
    print(type(e).__name__)
#: AttributeError
```

The prose then has to explain what the reader could have read off the output:
"`step()` reads `self.name` one line before the constructor assigns it."
`print(e)` gives `'Greeter' object has no attribute 'name'`, which names the
attribute, names the class, and makes the paragraph a confirmation rather
than a translation.

I checked determinism specifically, since CLAUDE.md's trap list recommends
`type(e).__name__` for messages that can vary: this one is fixed text from
CPython's `object.__getattribute__`, with no "did you mean" suggestion in
`str(e)` (the suggestion is added by the traceback formatter, not the
exception). Three consecutive runs on the pinned 3.15 build produced the
identical string.

Proposed change: `print(e)` and `#: 'Greeter' object has no attribute 'name'`.
Reported rather than applied because it edits an existing listing's output
marker, which is your call rather than mine.

---

[] Reject

**Exercises: nothing exercises Substitutability.**

The three exercises cover the two mechanisms (1), the constructor trap (2),
and `@final`'s enforcement boundary (3). "Substitutability" is a full
section of the chapter with no exercise against it, and it is the part of
the chapter that no tool can check for the reader, which is exactly why
practising it matters.

Proposed exercise 4:

> 4. Write two subclasses of `ApplicationFramework` that both type-check but
>    break the fixed algorithm: one whose `customize1()` raises an exception
>    the base never raises, and one that leaves `customize2()` at its `...`
>    default when the flow depends on it.
>    Neither is reported by `ty`. What would have to be true of the base
>    class for a checker to catch either one?

---

[] Reject

**End of "Substitutability": `test_template_method.py` is in the wrong
section, or needs a bridge.**

The test exercises `template_method.py`, which is three sections back, and
its lead-in — "The test supplies a recording subclass and verifies the fixed
flow" — says nothing about substitutability.
It reads as a listing that got parked wherever the section boundary happened
to fall.

Two fixes, pick one:

- **Move it** to the end of "The Fixed Algorithm," right after the
  `...`-defaults paragraph and before the two `###` subsections, so the
  listing, its explanation, and its test sit together and the two
  subsections are pure commentary on them.
  Cost: nothing else references it, and no anchors change.
- **Bridge it** where it stands, by making the lead-in earn the section:
  "`Recorder` is the faithful substitute the section describes: it fills the
  steps and changes nothing about the flow, so the test can assert the flow."

I prefer the move.[[do that]]

---

[] Reject

**"A caution about the `@final` lock" paragraph: two small precision items.**

1.  "it binds only under the type checker" — *binds* is legalistic and is
    the only place in the chapter that reaches for a metaphor instead of the
    literal statement. Suggest "it holds only under the type checker."

2.  "At runtime Python ignores it" contradicts chapter 17, which is more
    precise about the same decorator: "At runtime it only marks the class,
    setting `__final__ = True` ... Nothing enforces it."
    The method form behaves the same way; I confirmed
    `Framework.run.__final__` is `True` on the pinned 3.15 build.
    "Ignores" is defensible shorthand, but the two chapters describing the
    same decorator differently is the kind of thing a careful reader notices.
    Suggest "At runtime Python only records the mark and enforces nothing,"
    which also sets up exercise 3's question about who objects.

---

[] Reject

**"The Fixed Algorithm," first paragraph: the `@final` link points at the
class form.**

> The `@final` decorator from `typing` locks the template method so a subclass
> cannot change the overall flow
> (see [Making a Class Final](17_Metaprogramming.md#making-a-class-final)).

That section of chapter 17 only ever puts `@final` on a class
(`@final class B`), and its title says so.
A reader who follows the link to check the decorator finds no example of
`@final` on a method and has to infer that it applies there too.
The later paragraph in this chapter does the same thing for
`__init_subclass__()` but says explicitly "applies to a method too," which is
the right move.

Proposed change: make the first reference say the same thing, e.g.

> The `@final` decorator from `typing`, used on a class in
> [Making a Class Final](17_Metaprogramming.md#making-a-class-final), works on
> a single method too: it locks the template method so a subclass cannot
> change the overall flow.

Verified: `ty` 0.0.65 reports
`error[override-of-final-method]: Cannot override \`Framework.run\`` for a
subclass that overrides a `@final` method, so the claim is sound; only the
cross-reference is doing less work than it looks like.

---

## Cross-chapter

[] Reject

**`Solutions/25_Template_Method.md`, exercise 3: the quoted `ty` diagnostic
is stale.**

The solution shows

```
error[invalid-override]: Cannot override final method `run`
```

`ty` 0.0.65 (the version in this workspace) emits

```
error[override-of-final-method]: Cannot override `ApplicationFramework.run`
info: `ApplicationFramework.run` is decorated with `@final`, forbidding overrides
```

I reproduced this by running `ty` over the solution's own `exercise_3.py`
with the `# type: ignore` removed. Both the rule name and the message text
changed. This matters more than a usual stale quote because the chapter's
exercise 3 explicitly tells the reader to run `ty` themselves and compare, so
the reader will see a different string from the one the answer shows.

Change I would make in `Solutions/25_Template_Method.md`: replace the quoted
block with the 0.0.65 text above. I did not touch it, per the scope rules.

---

[] Reject

**`Chapters/31_State_Machines.md`, the paragraph after `state_machine.py`:
use the named anchor for the back-reference.**

31 currently says:

> The constructor also runs the initial state,
> the construction-starts-the-engine choice that drew a warning in that chapter.

The content is correct and consistent with 25 — I checked both ends of this
thread and they agree. The reference is a bare relative phrase, though, and
25 now carries an explicit anchor,
`{#dont-start-the-engine-in-the-constructor}`, on the section that holds the
warning.

Change I would make in `Chapters/31_State_Machines.md`:

> the construction-starts-the-engine choice that
> [drew a warning in that chapter](25_Template_Method.md#dont-start-the-engine-in-the-constructor).

Per CLAUDE.md, a named link fails loudly at `heading_links.py` if the section
is ever renamed, while the relative phrase goes stale silently. I did not
touch chapter 31, per the scope rules.
