[[Reviewed]]
# Deep review: 25_Template_Method.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Point the `unittest` opener at `TestCase.run()`, not "the framework's runner"

**Kind:** teaching (correctness of an illustration)
**Where:** opening section, lines 10-15

**Problem:**
The paragraph just above defines a Template Method as "a method, defined in the base class,
that drives the application by calling other base-class methods, some of which you override."
The `unittest` illustration then says "The framework's runner is the template method."
That points at the wrong object. `unittest.TextTestRunner` is a separate object that calls into your test;
the method that calls `setUp()`, your test method, and `tearDown()` is `TestCase.run()`
(verified in the 3.15 stdlib: `run()` calls `self._callSetUp()`, `self._callTestMethod(testMethod)`, `self._callTearDown()`).
So the one stdlib example the chapter offers points away from the base class the reader subclasses,
which is where the definition just told them to look.

There is a second thing lost here. `TestCase.__init__()` does not run the test;
the runner calls `run()` on a finished object.
That is the design the chapter later recommends as the fix for the constructor trap,
sitting in the stdlib, unmentioned.

**Proposal:** replace lines 10-15 with:

```
Python's own `unittest` is an application framework of this kind.
You subclass `TestCase` and supply `setUp()`, your `test_*` methods,
and `tearDown()`.
`TestCase.run()` is the template method.
It calls `setUp()`, then your test method, then `tearDown()`,
and you never call that sequence yourself.
Constructing a `TestCase` runs nothing;
the test runner calls `run()` on the finished object,
a separation this chapter returns to below.
```

**Cost:** none. No other chapter cites this passage. The final sentence assumes proposal 2's heading exists or at least that the trap section stays where it is; if you reject that sentence, drop it and keep the rest.

---

## 2. Give the constructor trap its own heading

**Kind:** structure
**Where:** line 91, "Starting the engine from the constructor carries a trap."

**Problem:**
"The Fixed Algorithm" runs from line 17 to line 167 and carries five separate ideas
(the listing, call direction and the Hollywood Principle, the `@final` caveat, optional steps versus abstract ones,
the constructor trap, and LSP) with no landmarks.
The constructor trap is the part other chapters cite:
chapter 31 says "the construction-starts-the-engine choice that drew a warning in that chapter"
and links to `25_Template_Method.md` with no anchor, so a reader lands at the top of the chapter and hunts.
Chapter 39's pattern catalog has the same problem for two rows that point here.

**Proposal:** insert a subheading before line 91:

```
### Don't Start the Engine in the Constructor {#dont-start-the-engine-in-the-constructor}
```

and a second one before line 137 (`This pattern leans on the Liskov Substitution Principle`):

```
### Substitutability
```

**Cost:**
Chapter 31 line 70-73 and chapter 39 line 152 could then link to the anchor instead of the chapter,
which is a one-line edit in each and is not done here (out of scope for this review).
The explicit `{#id}` on the first heading is there because the auto-slug of an apostrophe-bearing heading is ugly;
drop it and let pandoc slug the heading if you prefer, but then check `heading_links.py` before linking to it.
Alternative: one heading only (the constructor trap), leaving the LSP paragraph inside the main section.

---

## 3. Reconcile "a forgotten step silently does nothing" with the LSP warning

**Kind:** teaching
**Where:** lines 83-89 and lines 137-144

**Problem:**
Line 85 tells the reader that a step left unoverridden silently does nothing, and presents that as the design's convenience.
Fifty lines later the LSP paragraph says an override "doing nothing the flow relies on" corrupts the fixed algorithm.
A first-time reader now holds two claims that look opposed and has no rule for telling the two cases apart.
The rule exists (a step the flow depends on belongs to an ABC as `@abstractmethod`;
only a genuinely optional step gets the `...` default) but the chapter states each half in a different place and never joins them.

The same LSP sentence is also hard to parse.
"An override that breaks that trust, doing nothing the flow relies on, or raising an exception where the base would not, corrupts the fixed algorithm"
reads at first as "doing nothing" being a modifier of "trust", and the reader has to back up.

**Proposal:** rewrite the LSP sentence (lines 141-143) to name both halves and to point back at the `...` default:

```
An override that breaks that trust corrupts the fixed algorithm even though the code still type-checks:
one that raises an exception where the base would not,
or one that leaves a step empty when the flow depends on the work.
That last case is the price of the `...` defaults above.
They make a step optional, and nothing distinguishes "deliberately empty" from "forgotten."
Where the algorithm cannot proceed without a step, `@abstractmethod` says so and Python enforces it.
```

Alternatives:

- Prose-only, smaller: split the confusing sentence into two and leave the reconciliation implicit.
- Demonstrate instead of explain: append a second subclass to `template_method.py` showing a partial override. Verified output:

  ```python
  class Quiet(ApplicationFramework):
      @override
      def customize2(self) -> None:
          print("Say no more, say no more!")

  Quiet()
  #: Say no more, say no more!
  #: Say no more, say no more!
  ```

  I do not recommend this one: it doubles the central listing's output to teach a point the `...` in the base class already makes visible.

**Cost:**
Touches nothing outside this chapter.
If proposal 2's "Substitutability" heading is rejected, this rewrite still applies unchanged.

---

## 4. Name Inversion of Control alongside the Hollywood Principle

**Kind:** teaching
**Where:** lines 72-75

**Problem:**
Chapter 39's catalog has a row `| [Inversion of Control](25_Template_Method.md) | Let a framework call your code rather than the reverse. |`,
and the term "Inversion of Control" appears nowhere in this chapter.
A reader following that link finds the idea under a different name and cannot confirm they are in the right place.
The term is also the one they will meet in framework documentation everywhere else.

**Proposal:** after line 74 ("we'll call you."), add:

```
The general name for this reversal is *Inversion of Control*:
the framework holds the flow of control and calls into your code,
rather than your code calling into a library.
```

**Cost:** none. Adds a term the chapter can then be linked to by name; chapter 39's row becomes accurate without editing it.

---

## 5. Say what the function version does that `@final` cannot

**Kind:** teaching
**Where:** section "Passing the Steps as Functions", trade-off paragraph at lines 206-212

**Problem:**
Lines 77-81 tell the reader the `@final` lock is the checker's guarantee, not Python's:
a subclass that overrides `run()` really does replace the algorithm at runtime.
`run_framework()` has no such gap. There is no inheritance channel through which a caller can replace the loop.
The trade-off paragraph compares the two forms on state and grouping only,
so the reader never learns that the function version answers the caveat raised earlier in the chapter.

**Proposal:** add to the trade-off paragraph, after line 210:

```
The function version also closes the gap in `@final`.
A caller supplies the steps and cannot replace the loop,
because there is no subclass through which to replace it.
The fixed algorithm is fixed by structure rather than by a decorator the runtime ignores.
```

**Cost:** none; strengthens the connection between the chapter's two sections, which currently read as two independent takes on the same problem.

---

## 6. Point at the runtime way to lock the algorithm

**Kind:** teaching
**Where:** lines 77-81, the `@final` caveat

**Problem:**
The paragraph ends on "one more reason to make `ty` or another checker part of the build,"
which leaves the reader with no option when a checker is not in the build.
Chapter 17 already showed `__init_subclass__()` refusing a subclass at class-creation time,
and the same technique locks a method rather than a class. Verified:

```python
class Framework:
    def __init_subclass__(cls, **kwargs: object) -> None:
        if "run" in cls.__dict__:
            raise TypeError("run() is final; override the steps")
```

A subclass that defines `run()` raises a `TypeError` when the class body is executed.

**Proposal:** append one sentence to line 81:

```
When you need the interpreter to refuse an override, the `__init_subclass__()` technique from
[Making a Class Final](17_Metaprogramming.md#making-a-class-final) applies to a method too:
raise an exception when `"run" in cls.__dict__`.
```

Alternative: add it as a listing rather than a sentence. I would not, since chapter 17 already carries the listing and this chapter's claim is a pointer, not a new mechanism.

**Cost:** the cross-reference already exists at line 22, so the anchor is known good. Adds a second link to the same section, which is fine but worth noticing.

---

## 7. Add an exercise on the checker-only guarantee

**Kind:** exercise
**Where:** "Exercises", after line 227

**Problem:**
The two exercises cover the subclass form, the function form, and the constructor trap.
Nothing exercises the chapter's other two claims: that `@final` binds only under the checker, and the direction of calls.
The `@final` claim is the one a reader is most likely to over-trust,
because "the checker rejects any subclass that overrides it" reads like a language guarantee.

**Proposal:** add:

```
3.  Subclass `ApplicationFramework` and override `run()` with a version that
    calls `customize2()` before `customize1()`. Run it, then run `ty` over it.
    Which of the two, Python or `ty`, objects to the change? What does that
    tell you about where the fixed algorithm's guarantee comes from?
```

**Cost:** needs a matching entry in `Solutions/25_Template_Method.md`, which currently has two answers. Not written here.

---

## 8. Fix the ambiguous pronoun in the trade-off paragraph

**Kind:** prose
**Where:** lines 206-208

**Problem:**
"Both the Template Method and the function version have a fixed algorithm and varying steps.
If they share state, build on each other, or come as a coherent group, the subclass is clearer."
"They" means the steps, but the nearest plural subject is "the Template Method and the function version,"
so the sentence reads wrong on first pass.

**Proposal:** change "If they share state" to "If the steps share state".

**Cost:** none.

---

## 9. Disambiguate "the first file" in exercise 1

**Kind:** exercise
**Where:** lines 216-223

**Problem:**
The framework "opens every file but the last for reading," so every file except the last is an input.
Sub-exercise (b) then says "Search the files for words given in the first file,"
which makes the first file both an input to be searched and the word list to search for.
The solution resolves it one way (word list read once, before the loop) but the exercise text does not say so.

**Proposal:** change sub-exercise (b) to:

```
    2.  Treat the first file as a list of search words, one per line,
        and report which of those words appear in each remaining input file.
```

**Cost:** the existing solution text already describes this reading, so nothing there needs to change.

---

## Already fixed directly (no decision needed)

Nothing. The chapter's gates all pass as it stands:

- `ruff check`, `ty check`, and `pytest` clean on `build/examples/25_Template_Method`.
- All three runnable listings reproduce their `#:` markers exactly.
- `heading_links.py` and `banned_phrases.py` clean; no em-dashes; no watch-list words.
- Both technical claims about `@final` verified against the pinned toolchain:
  `ty` 0.0.65 reports `override-of-final-method` on an overriding subclass,
  and at runtime the override takes effect (`@final` only sets `__final__ = True`).
- The cross-chapter thread holds: chapter 31 (`state_machine.py`) names the constructor trap
  taught here, explains why its own `StateMachine.__init__()` is safe (stateless singleton states),
  and warns that a `State` reading machine attributes revives it.
