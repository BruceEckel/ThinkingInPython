> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 20_Patterns--Rethinking_Objects (2026-09-29)

Nothing here needs your decision, so the file has no live blocks.
I checked each claim against its listing, against the sections it links in chapters 7, 8, 12, 13, 18, 29, 32, 33, 34, 38, and 42, and against `ty` 0.0.84 with a probe file
(the read-write protocol form rejecting both `Point` and `PairCoord`,
the frozen assignment `test_immutable.py` routes around,
both `stringify()` overloads, the `NewType` rejection, `t: object` failing on `display()`,
and the `assert_never()` report for a missing case).
The three external links resolve.
`tip verify-ch CH=20` passes 24 of 24.

## Applied directly

Chapter, corrections:

- "The Liskov Substitution Principle": "Two later tests pin down guarantees no type checker sees" contradicted the chapter's own later sentence that the type checker rejects `immutable.bob.name = "Ralph"`. Now "runtime guarantees", which holds for both tests.
- "Plugging Leaks Is Tedious": a shallow copy of a list of `Bob`s "plugs nothing" overstated it, since the copy does protect the list. Now it says what is protected and what is shared.
- "Prefer Composition to Inheritance": "the base class's other method" read as though `list` had two methods. Now "another of the base class's methods".
- Same section: "`CountingList` inherits dozens it didn't write, and gets one wrong" undercounted. `insert()`, `+=`, and `*=` skip the counter too, and exercise 7 asks the reader to find a second one. Now "more than one of them skips the counter". "`CountingBox` forwards every operation by hand" became "each operation it offers", since it forwards two.
- "Abstract Base Classes": "Inheriting from `ABC` makes `Shape` abstract" credited the base class with what `@abstractmethod` does; an `ABC` subclass with no abstract method instantiates. The sentence now names both, and says a subclass cannot be instantiated until it defines `area()`.
- "What Is Polymorphism?": "Python's version of ad-hoc polymorphism is `@overload`" sat three paragraphs above "`singledispatch` is ad-hoc polymorphism's other Python form". Now "Python's form of function overloading is `@overload`".

Chapter, teaching and order:

- "The Immutability Solution": the representation-hiding caveat sat between the section's opening claim and the listing, and its example ("swap `numbers` from a `tuple`") described a listing the reader had not seen. It also separated the lead-in sentence from the listing it introduces. The caveat now closes the section's argument, after `frozen_leaky.py`, and the opening says encapsulation exists "mainly" because of mutability, so the opening no longer says "only" a page before the second reason arrives. Alternative considered: leaving the caveat in place without its example.
- Exercise 2 repeated `frozen_leaky.py` (a `list` field in a frozen class: `append()` works, `hash()` fails). The chapter names two quiet changes in `immutable.py`, the `tuple` and the frozen `Bob`, and demonstrates only the first. Exercise 2 now covers the second: remove `frozen=True` from `Bob`, watch `immutable.bob.name = "Ralph"` succeed, and watch `hash(immutable)` fail. The closing question is unchanged. No prose in the book refers to this exercise by number.

Chapter, listings:

- `immutable.py`: the two-line comment read "...no append. and .bob.name..."; the first line now ends with a comma.
- `distance_protocol.py`: the "Adapter" comment sat between `@record` and `class PairCoord`. It now sits above the decorator.

Chapter, prose:

- Two "itself" flourishes in the frozen-is-shallow paragraph, one in exercise 4; "genuinely separate functions"; "already solve the problem" in Guidelines.
- "each only checks the one method it needs" gave the checking to the functions. Now each function's parameter names the one method.
- "silences that diagnostic" pointed three paragraphs back. Now "`ty`'s diagnostic".
- "A frozen dataclass with a validating `__post_init__`" became "data class" and `__post_init__()`, matching the rest of the chapter.
- 'This is what "bundling behavior with state" buys' lost "is what" and "buys".

Solutions:

- Exercise 1: both listings had an unannotated `__init__()` and property. They now carry the annotations `leaky.py` and `plugged.py` carry.
- Exercise 2: new listing and prose for the new exercise. The record-exceptions entry (`exercise_2.py Immutable`) still matches. The closing paragraph on who makes immutability deep is unchanged.
- Exercise 5: the prose described the `assert_never()` report without showing it. It now quotes `ty`'s diagnostic, whose inferred type `Square & ~Rectangle & ~Circle` names the missing case.
- Exercise 6: `object | None` is `object` to a type checker. The cache now holds `str` values, so `str | None` says something. Added two sentences separating the `None` a miss returns from the `None` the null object removes, since the chapter's own rule is that absence a caller acts on stays in the type.
- Exercise 7: "`list.__init__` with an iterable" is not a route into this `CountingList`, whose `__init__()` takes no arguments. Replaced with `*=`. Added the reason `__setitem__()` is unannotated.
- Exercise 8: "`fill()` now runs on both classes, and that is what substitutability means" overclaimed: `fill()` returns 2 where a `Stack` caller expects 5. The solution now says so, which supports its own conclusion that `BoundedStack` should not be a subclass. "keeps that promise" became "keeps that guarantee", and "honest" is gone.
- Exercises 3 and 4: an imperative-plus-consequence sentence and a run of intensifiers ("actually", "entirely", "itself", "only ever").

## Considered and declined

- A `test_stack_contract.py` listing for "No tool catches this, but a test can." The test fails by design on `BoundedStack`, so the gate would need an `xfail` marker, and that marker is a second topic in a listing whose one point is the contract. Exercise 8 covers the ground.
- "A `@dataclass` version of `Plugged` ... `__repr__` prints `_numbers` and `_bob` directly, leaking the internals yet again." Printing a value discloses it and hands out no reference, so this is a different leak from the one the section is about. The sentence reads as your framing from the talk, and it is true as written.
- "*Subtype polymorphism* is what the four subsections below demonstrate." A type theorist might file the `Any` and union-with-`match` subsections elsewhere. The sentence defines its own sense ("any type that fits a shape") and the four subsections fit it.
- `shapes_oo.py` has no function with a polymorphic parameter, although the section defines polymorphism through one. The loop variable does the same job, and a wrapper function would add lines without adding a point.
- The `# ty: expected "UserId", found "Literal[42]":` comment uses double quotes where `ty` prints backticks. Chapter 8 sets that form for every `# ty:` comment.
- The four "promise" section themes, the hand-written `__init__()` in `leaky.py` and `plugged.py`, and the long-form `@dataclass(frozen=True)` in `immutable.py` and `frozen_leaky.py` are standing rulings.
