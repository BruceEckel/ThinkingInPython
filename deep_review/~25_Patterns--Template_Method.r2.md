> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 25_Patterns--Template_Method (2026-10-13)

This round has no live blocks.
I checked every claim against its listing, ran each extracted script directly from `build/verify-ch-25/` and compared it with its `#:` markers (all match), and probed the chapter's type-checker claims with `ty` 0.0.86 under `uv run` (Python 3.15.0).
The `ty` claims all still hold: `unresolved-attribute` on `run.__final__`, `invalid-explicit-override` for a misspelled `@override`, `override-of-final-method` (Solutions exercise 3 quotes it word for word), `call-non-callable` for an abstract class, and `missing-argument` for `run_framework()`.
A runtime probe confirmed the `@final` placement paragraph: the check misses `@final` on a property and `@final` above `@classmethod`/`@staticmethod`, and it catches `@final` written below them.
`difflib` scores `customer` against `customize2` at 0.78 against a 0.6 cutoff, as the chapter says.
`tip verify-ch CH=25 ISOLATED=1` passes 27 of 27 before and after, and `tip prose CH=25` reports no new hits.

## Applied directly

Chapter, corrections:

- "The Anchored Algorithm": "It declares that no subclass may override the template method" spoke of the decorator in general but named one method, and the chapter never said that `run()` is this listing's template method. The paragraph now says what `@final` declares on any method, then names `run()` as the template method in `framework.py`.
- `class Hijack` paragraph: "fails because a subclass that replaces the anchor moves the algorithm..." gave the reason the check exists as the reason the class fails. The class fails because the `run()` it replaces carries `__final__`, and the design reason now sits in its own sentence.
- `@final` placement paragraph: "marks the function that `getattr()` returns" was loose for `@classmethod`, where `getattr()` returns a bound method that passes the attribute lookup through to the function. It now says "directly or through a bound method".
- "Hooks and the Misspelled Override": "Among the remaining names, only one that nearly matches..." left the reader to work out which names remained. Rewritten to describe the third case (close to an inherited name, not matching it) directly. "The `class Typo` statement also raises" had no first case for its "also"; it now says why `Typo` fails (`customise1` comes close to `customize1`).

Chapter, teaching:

- `@abstractmethod` paragraph: added the version a reader who knows older code would write, a required step whose body raises `NotImplementedError`. That subclass constructs and type-checks, and the omission surfaces only when `run()` reaches the step.
- After `template_method.py`: "The client supplies `customize1()` and `customize2()` in the derived class" repeated the sentence before the listing. Replaced with the mechanism: `MyApp` defines no `run()`, and the inherited `run()` calls the steps `MyApp` supplies.
- "Substitutability": the lead-in listed three failures as flat statements ("It raises an exception...") and never said which one the listing shows. Now it says that a subclass breaks the trust when it does any of the three, and that `faithless_step.py` shows the third.

Chapter, prose:

- Figure paragraph: "In the second frame each arrow is a call through `self`": frame 1 draws the same `self.` arrows. Now "In the first two frames..., and in the second those calls reach the subclass's methods."
- *Strategy* paragraph: "the algorithm stays put, and only its steps come from outside" is now "stays in `run_framework()`, and the caller supplies the steps."

Solutions:

- Exercise 4: Java's `throws` clause holds overrides to the declared list only for checked exceptions. A `RuntimeException`, the closest Java analog of `Exploder`'s `RuntimeError`, passes through it unchecked. Added "for checked exceptions".

## Considered and declined

- **Exercise 1's search policy reads the word file outside the framework.** The exercise says "treat the first file as a list of search words", and the solution has the client split that file off before calling the framework. The solution says so and why (the framework treats every input alike). A stateful first-call `process()` would follow the wording more literally but would be fragile, and the 2026-09-29 review accepted this design.
- **Moving the Hollywood Principle paragraph above `test_template_method.py`.** It explains the inversion that `template_method.py` shows, but moving it would separate the test from the listing it tests, which the last review placed together on purpose.
- **The comments in `template_method.py` and `premature_engine.py`.** They are pre-existing teaching comments. The house rule moves new explanations to prose and leaves existing comments alone.
- **"falls into a trap" in the engine section.** The next two sentences spell out the mechanism, so the phrase works as a lead-in and has no literal replacement that reads better.
- **"The `...` defaults make a step optional, and nothing distinguishes..." in "Substitutability".** That sentence describes the `...` default alone, and the `@abstractmethod` remedy is a section earlier and in exercise 4. Naming it here would answer the exercise in advance.

## For the session

- `tip watch-words` now lists three stale baseline entries for this chapter, all `only` hits that the rewrites removed ("only for the type checker", "only its steps come from outside", "only one that nearly matches"). The baseline needs a refresh, which I did not run.
- No cross-chapter errors found. The links to chapters 07, 17, 20, 24, and 28 resolve, and each target supports its claim: chapter 20's "Abstract Base Classes" explains the empty `__slots__`, and chapter 24's "Double-Checked Locking and Eager Creation" contrasts eager and lazy creation.
