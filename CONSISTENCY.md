# Book-Altitude Consistency Review

2026-08-30. Eight parallel agents mapped all 47 chapters (terms introduced,
concepts assumed, cross-references, promises, duplicate teaching), on top of
mechanical link and relative-reference scans. Nineteen confident fixes were
applied directly (duplicated draft sentences in ch17 and ch47, the ch30
backward-reference-phrased-as-forward, the `display_object` provenance
conflict, "dataclass" as a one-word noun, and others; see commit `2e502ecc`).
Everything below needs Bruce's judgment. Each issue carries a recommendation
and a `[] Reject` box; check the box to reject, and an unchecked box means
the recommendation can be applied.

## Naming collisions and conventions

1. **"Foundations" names both Part I and chapter 40's H1.** Chapters 40-43
   use short H1s (Foundations, Toolkits, Error Handling, Assurance), and
   inbound link text varies: ch16 says "Functional Foundations"; ch18, ch28,
   and ch34 say "Foundations". Pick one convention, or retitle one of the two
   "Foundations".

   **Recommendation:** Keep the short H1s inside Part IV, where context
   disambiguates, but use "Functional Foundations" as link text everywhere
   outside Part IV (fix ch18, ch28, ch34 to match ch16).

   [] Reject

2. **GoF citation coverage.** "*GoF Design Patterns*" is the canonical form
   and holds almost everywhere. But chapters 22, 25, 30, 31, 32, 35, and 36
   cite GoF nowhere: ch36 presents a "classic" Memento uncredited, ch25
   presents Template Method with no GoF mention, and ch22's "Data Transfer
   Object" (a Fowler-era term, not GoF) is unattributed.

   **Recommendation:** Add a one-clause *GoF Design Patterns* attribution
   wherever the word "classic" introduces a form (ch25, ch30, ch36), and
   attribute "Data Transfer Object" to Fowler's *Patterns of Enterprise
   Application Architecture* in ch22. Leave ch31/32/35 alone; they present
   nothing labeled classic.

   [] Reject

3. **"dunder" vocabulary.** Defined twice (ch06 and ch07), used before
   definition (ch02's `__bool__`/`__len__`), avoided entirely by ch15
   ("protocol methods"), and load-bearing in ch17. Ch07 also mixes "field"
   and "attribute" and introduces "special methods" as a second name.

   **Recommendation:** Keep ch06 as the definition and shrink ch07's
   re-gloss to a plain back-use. Standardize on "dunder" for the category,
   keeping "protocol methods" only where a specific named protocol is meant
   (ch15's usage survives on that reading). In ch07, settle on "attribute",
   keeping "field" only in the C++/Java comparison sentence.

   [] Reject

4. **Ability capitalization** in ch46/47: singular "Ability" is always
   capitalized, the plural is almost always lowercase ("abilities",
   "a cast of abilities"). Deliberate?

   **Recommendation:** Capitalize the plural ("Abilities") wherever it means
   the concept, a mechanical sweep over ch46/47. If the lowercase plural is
   deliberate, reject this and nothing else changes.

   [] Reject

5. **"channel" is overloaded** across the 45/46 boundary: generator channels
   (yield/send/return) vs Effect channels (Ability/error). Each chapter is
   internally consistent; the collision happens within two pages.

   **Recommendation:** One bridging clause at ch46's first "channel" use:
   these are channels in a new sense, the two things an `Effect` declares,
   not the three channels a generator carries.

   [] Reject

6. **"boundary function"** in ch47 names two different idioms: a
   `@throws`-lifting wrapper (`draw()`) and a supply-and-run edge function
   (`outcome()`/`play()`).

   **Recommendation:** Reserve "boundary function" for the supply-and-run
   edge (it matches the established "the edge" vocabulary) and rename
   `draw()`'s role to a "lifting wrapper" at its two mentions.

   [] Reject

7. **Tool-naming policy is uneven.** Some chapters name `ty` for specific
   diagnostics, others only say "the type checker"; ch12 says "the linter"
   without naming ruff; ch13 quotes an exact ruff diagnostic string (fragile
   across upgrades); ch18 mixes bare `python -m` and `uv run python` in
   reader-facing commands.

   **Recommendation:** Adopt ch08's rule book-wide: "the type checker"
   generically, `ty` when quoting or naming a diagnostic. Name ruff at
   ch12's "the linter". Paraphrase ch13's exact ruff message so upgrades
   cannot stale it. Show `uv run python` in every ch18 reader command.

   [] Reject

8. **"finalizer"** in ch10 covers three different things: `__del__` methods,
   an explicit `close()`, and `weakref.finalize` objects.

   **Recommendation:** Reserve "finalizer" for `weakref.finalize` objects;
   say "the `__del__()` method" and "an explicit cleanup method" for the
   other two. Three small edits in ch10.

   [] Reject

## Duplicate teaching (restructure candidates)

1. **ABC-fails-at-instantiation vs Protocol-fails-at-use** is fully taught in
   both ch26 and ch27, on top of the ch08/ch20 foundations. The strongest
   duplicate pair found.

   **Recommendation:** Keep ch26's treatment (it comes first and is tied to
   `Partial()`). In ch27, keep the `games.py`/`games2.py` listings but
   compress the surrounding prose to a reminder plus a link to ch26.

   [] Reject

2. **Type-based special-method lookup** gets paragraph-depth treatment in
   both ch24 (`__call__`) and ch26 (dunder bypass).

   **Recommendation:** Keep ch26's full treatment (the bypass is its
   subject). Trim ch24's to one sentence with a forward link to ch26's
   dunder-bypass section.

   [] Reject

3. **Name mangling**: ch11 owns it; ch24 links it, then re-explains it from
   scratch 250 lines later.

   **Recommendation:** Cut ch24's re-explanation to a clause that leans on
   the ch11 link it already made.

   [] Reject

4. **Mutating-while-iterating** is taught from scratch in both ch03 (list)
   and ch04 (list and dict), with no cross-reference between them.

   **Recommendation:** Keep both (first contact vs the dict extension), but
   ch04's section opens with a back-link to ch03's listing.

   [] Reject

5. **Shallow/deep copy**: ch02 intro, ch20 treatment, ch36 full tutorial
   again.

   **Recommendation:** Keep ch36's tutorial (Memento needs it fresh at hand)
   but open it with a back-link to ch20 framing it as a recap in a new
   context.

   [] Reject

6. **`sys.modules` caching**: ch06 owns it; ch31 re-explains it (in a
   two-files-collision context that arguably earns its keep).

   **Recommendation:** Keep ch31's explanation, add the ch06 link at its
   start.

   [] Reject

7. **`__init_subclass__`**: ch37 re-explains it inline with no ch17 link, and
   ch27's self-registration section substantially re-covers ch17's.

   **Recommendation:** Add the ch17 link to ch37's two-sentence gloss. Leave
   ch27 alone; it already links ch17 and its extra failure modes (unimported
   plugin, name collision, MRO trap) are its own material.

   [] Reject

## Assumed-before-taught (front-to-back reader debts)

1. **ch11 (Testing) carries the heaviest debts**: `@dataclass` one chapter
   before ch12 with no forward link, and decorator syntax
   (`@pytest.fixture`, `@pytest.mark.parametrize`) three chapters before
   ch14, unlinked. (The yield-fixture debt now carries an Iterators link.)

   **Recommendation:** Two forward-link parentheticals: at the first
   `@dataclass` use, point to ch12; at the first fixture decorator, note
   that the `@` line is a decorator ch14 explains and here only marks the
   function.

   [] Reject

2. **ch19** uses the iterator protocol and generator mechanics (ch23/45
   territory) with only one parenthetical pointer.

   **Recommendation:** Accept the protocol pointer as sufficient; add one
   matching parenthetical at `shared_generator.py` pointing to ch23's
   generator section.

   [] Reject

3. **ch16** names `TypeIs`/`TypeGuard` with zero explanation; verify ch08's
   narrowing section introduces them. It also drops the async-generator
   comprehension form with no ch19 link.

   **Recommendation:** If ch08's narrowing section names them, add that link
   in ch16; if not, add a five-word gloss instead. Add a ch19 link at the
   async-generator sentence.

   [] Reject

4. **ch22** uses the `__getattr__`/`__setattr__` stub trick before ch24/26
   teach the fallback hook.

   **Recommendation:** Add a forward link to ch26's forwarding section at
   the stub-trick sentence.

   [] Reject

5. **ch28** depends on ch40 for closures, `partial`, and `Placeholder` via
   forward links; the `Placeholder` sentence is hard to follow without ch40.

   **Recommendation:** Keep the closure and `partial` forward links (they
   carry inline glosses), but give `Placeholder` a one-clause description
   ("a sentinel that reserves a positional slot") so the sentence stands
   alone.

   [] Reject

6. **ch17** says "You have used metaclasses already", citing ABC and Enum;
   ABC's real teaching is ch20, three chapters later.

   **Recommendation:** Rest the claim on Enum (ch12) and give the ABC
   mention a forward link to ch20's Abstract Base Classes section.

   [] Reject

7. **`# type: ignore` / `# ty:` conventions** are defined in ch08 but used
   from ch03 onward with ad-hoc local glosses. One sentence in ch01's
   Examples section would retire all of them.

   **Recommendation:** Add that sentence to ch01's Examples section: some
   early listings carry `# type: ignore` or `# ty:` comments, which
   Static Typing defines; until then they only mark lines a type checker
   would flag.

   [] Reject

8. **ch29** names `__reduce__()` as the copy/pickle fix with no explanation
   or link anywhere in the book.

   **Recommendation:** Replace the bare name with a clause: `__reduce__()`,
   the hook `pickle` and `copy` consult, whose details are beyond this book.

   [] Reject

9. **ch06** `app_settings.py` carries unflagged annotations pre-ch08 (ch01
   says early chapters "mostly omit" hints; this is the only unflagged case).

   **Recommendation:** Accept as covered by ch01's "mostly omit"; no change.

   [] Reject

## Chapter-level oddities

1. **ch20 fully teaches Null Object one chapter before ch21 defines
   "pattern"**, and ch21's taxonomy never mentions it. Check ch39 indexes
   Null Object to ch20.

   **Recommendation:** One sentence in ch21 acknowledging *Null Object* as a
   non-GoF pattern the previous chapter already used, and a ch39 catalog row
   linking it to ch20 if one is missing.

   [] Reject

2. **ch39 ends Part III cold**; ch40 does all the bridging. Deliberate?

   **Recommendation:** Accept; a catalog is reference matter and ch40's
   opening does the bridging well. At most, one closing sentence in ch39
   pointing at Part IV.

   [] Reject

3. **ch42 has no forward pointer** to ch43 or Part V, though ch44 reuses its
   `Result`/`@safe` machinery heavily; the hand-off lives only in ch40 and
   ch43.

   **Recommendation:** One closing sentence in ch42: Assurance examines what
   the discipline lets you claim, and Effect Management builds on this
   `Result` machinery.

   [] Reject

4. **ch17's opening line** "Other (special) objects create objects." gives
   "Other" no antecedent at the start of a chapter.

   **Recommendation:** Rewrite the opener to supply the antecedent, e.g.:
   "Objects come from classes. Classes are objects too, created by other,
   special objects."

   [] Reject

5. **ch18** "Ask your AI to convert the hot Python function" is a register
   outlier; deliberate?

   **Recommendation:** Keep it; the pragmatism fits the book and the advice
   is real. Reject the issue rather than the sentence.

   [] Reject

6. **ch44 coins "implicit inputs"** as a synonym and never uses it again
   ("side causes" is the working term everywhere, including ch46/47).

   **Recommendation:** Drop the "implicit inputs" synonym; keep "side
   causes".

   [] Reject

7. **ch46** juxtaposes `Console`'s "`print_line()` and `read_line()`
   accessors" with "implements `input()` as well as `print()`" two sentences
   later; both are presumably true of the library, but unbridged it reads as
   a contradiction.

   **Recommendation:** Verify the stateless library's actual names, then add
   a bridging clause: the accessors are the Effect-side functions, and
   `print()`/`input()` are the methods the concrete `Console` implements.

   [] Reject

8. **ch46/47 pin behavior claims to "under `ty` 0.0.70"** in four places; the
   repo is past 0.0.75. The claims may still hold, but every ty upgrade
   stales them.

   **Recommendation:** Re-probe the four claims on the current ty, update
   the version numbers, and add these four spots to the ty-upgrade checklist
   in CLAUDE.md so the next upgrade sweeps them.

   [] Reject

9. **ch26** spells the private implementation attribute four ways across
   listings (`__implementation`, `_implementation`, `_impl`, `_doc`); only
   one change is explained.

   **Recommendation:** Add one sentence acknowledging the shortening to
   `_impl` where it first appears; renaming the listings themselves is churn
   without payoff.

   [] Reject

10. **`singledispatchmethod`** is treated three inconsistent ways: inline
    unlinked (ch32), linked to ch41 (ch33), mentioned unlinked (ch37).

    **Recommendation:** Make ch32's inline explanation the primary one and
    add the ch41 link there; keep ch33's link; add the link at ch37's
    mention.

    [] Reject

11. **`__subclasses__()`** is used unexplained in ch32 and ch33; its
    introduction is inline in ch27. Consider links.

    **Recommendation:** Add "(introduced in [Factory])" at the first use in
    each of ch32 and ch33.

    [] Reject

12. **Enum's home** is ch12's "Enums Are Types Too", but ch12's own Enum
    usage doesn't announce it and ch13 uses Enum without a link.

    **Recommendation:** Open ch12's Enum section with a sentence claiming
    the introduction, and link it from ch13's first Enum use.

    [] Reject

13. **ch47** links "partial handling" to `46#emptying-the-channels`; the
    layered-supply technique it invokes is actually demonstrated in ch46's
    Dependency Injection consequences. Consider retargeting.

    **Recommendation:** Retarget the link to ch46's dependency-injection
    section.

    [] Reject

14. **The parameterize-spelling policy** for the whole book lives in a ch17
    footnote.

    **Recommendation:** Move the policy to ch11, where `parametrize` first
    appears, and have ch17's footnote point there.

    [] Reject

15. **ch41's Memoization row in ch39** links to `#the-functools-toolkit`
    though the finer `#cache` anchor exists.

    **Recommendation:** Retarget ch39's Memoization row to `#cache`.

    [] Reject

## Verified clean (no action needed)

- All explicit cross-chapter links resolve (`heading_links.py` green), and
  every spot-checked content claim matched: the 242,785 Fibonacci calls
  (ch18 vs ch44), `Thermometer` and `recolored` in ch30,
  `GameElementFactory` in ch27, `student_pairs.py`'s seed in ch41,
  `threading.synchronized_iterator()` in ch19, and the `slope()` promise
  (ch40 to ch44).
- The 45/46 split left no stale relative references anywhere; both of ch45's
  "next chapter" promises are delivered by ch46.
- The exact-type dispatch motif (28, 31, 32, 37) is threaded with accurate
  links at every step.
- Pattern-name italics conventions hold across Part III, and ch21's coverage
  contracts (Factory covers four creational patterns; Function Objects shows
  Command, Strategy, and Chain of Responsibility) are honored.
