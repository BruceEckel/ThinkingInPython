# Book-Altitude Consistency Review

2026-08-30. Eight parallel agents mapped all 47 chapters (terms introduced,
concepts assumed, cross-references, promises, duplicate teaching), on top of
mechanical link and relative-reference scans. Nineteen confident fixes were
applied directly (duplicated draft sentences in ch17 and ch47, the ch30
backward-reference-phrased-as-forward, the `display_object` provenance
conflict, "dataclass" as a one-word noun, and others; see the commit).
Everything below needs Bruce's judgment.

## Naming collisions and conventions

1. **"Foundations" names both Part I and chapter 40's H1.** Chapters 40-43
   use short H1s (Foundations, Toolkits, Error Handling, Assurance), and
   inbound link text varies: ch16 says "Functional Foundations"; ch18, ch28,
   and ch34 say "Foundations". Pick one convention, or retitle one of the two
   "Foundations".
2. **GoF citation coverage.** "*GoF Design Patterns*" is the canonical form
   and holds almost everywhere. But chapters 22, 25, 30, 31, 32, 35, and 36
   cite GoF nowhere: ch36 presents a "classic" Memento uncredited, ch25
   presents Template Method with no GoF mention, and ch22's "Data Transfer
   Object" (a Fowler-era term, not GoF) is unattributed.
3. **"dunder" vocabulary.** Defined twice (ch06 and ch07), used before
   definition (ch02's `__bool__`/`__len__`), avoided entirely by ch15
   ("protocol methods"), and load-bearing in ch17. Ch07 also mixes "field"
   and "attribute" and introduces "special methods" as a second name.
4. **Ability capitalization** in ch46/47: singular "Ability" is always
   capitalized, the plural is almost always lowercase ("abilities",
   "a cast of abilities"). Deliberate?
5. **"channel" is overloaded** across the 45/46 boundary: generator channels
   (yield/send/return) vs Effect channels (Ability/error). Each chapter is
   internally consistent; the collision happens within two pages.
6. **"boundary function"** in ch47 names two different idioms: a
   `@throws`-lifting wrapper (`draw()`) and a supply-and-run edge function
   (`outcome()`/`play()`).
7. **Tool-naming policy is uneven.** Some chapters name `ty` for specific
   diagnostics, others only say "the type checker"; ch12 says "the linter"
   without naming ruff; ch13 quotes an exact ruff diagnostic string (fragile
   across upgrades); ch18 mixes bare `python -m` and `uv run python` in
   reader-facing commands.
8. **"finalizer"** in ch10 covers three different things: `__del__` methods,
   an explicit `close()`, and `weakref.finalize` objects.

## Duplicate teaching (restructure candidates)

1. **ABC-fails-at-instantiation vs Protocol-fails-at-use** is fully taught in
   both ch26 and ch27, on top of the ch08/ch20 foundations. The strongest
   duplicate pair found.
2. **Type-based special-method lookup** gets paragraph-depth treatment in
   both ch24 (`__call__`) and ch26 (dunder bypass).
3. **Name mangling**: ch11 owns it; ch24 links it, then re-explains it from
   scratch 250 lines later.
4. **Mutating-while-iterating** is taught from scratch in both ch03 (list)
   and ch04 (list and dict), with no cross-reference between them.
5. **Shallow/deep copy**: ch02 intro, ch20 treatment, ch36 full tutorial
   again.
6. **`sys.modules` caching**: ch06 owns it; ch31 re-explains it (in a
   two-files-collision context that arguably earns its keep).
7. **`__init_subclass__`**: ch37 re-explains it inline with no ch17 link, and
   ch27's self-registration section substantially re-covers ch17's.

## Assumed-before-taught (front-to-back reader debts)

1. **ch11 (Testing) carries the heaviest debts**: `@dataclass` one chapter
   before ch12 with no forward link, and decorator syntax
   (`@pytest.fixture`, `@pytest.mark.parametrize`) three chapters before
   ch14, unlinked. (The yield-fixture debt now carries an Iterators link.)
2. **ch19** uses the iterator protocol and generator mechanics (ch23/45
   territory) with only one parenthetical pointer.
3. **ch16** names `TypeIs`/`TypeGuard` with zero explanation; verify ch08's
   narrowing section introduces them. It also drops the async-generator
   comprehension form with no ch19 link.
4. **ch22** uses the `__getattr__`/`__setattr__` stub trick before ch24/26
   teach the fallback hook.
5. **ch28** depends on ch40 for closures, `partial`, and `Placeholder` via
   forward links; the `Placeholder` sentence is hard to follow without ch40.
6. **ch17** says "You have used metaclasses already", citing ABC and Enum;
   ABC's real teaching is ch20, three chapters later.
7. **`# type: ignore` / `# ty:` conventions** are defined in ch08 but used
   from ch03 onward with ad-hoc local glosses. One sentence in ch01's
   Examples section would retire all of them.
8. **ch29** names `__reduce__()` as the copy/pickle fix with no explanation
   or link anywhere in the book.
9. **ch06** `app_settings.py` carries unflagged annotations pre-ch08 (ch01
   says early chapters "mostly omit" hints; this is the only unflagged case).

## Chapter-level oddities

1. **ch20 fully teaches Null Object one chapter before ch21 defines
   "pattern"**, and ch21's taxonomy never mentions it. Check ch39 indexes
   Null Object to ch20.
2. **ch39 ends Part III cold**; ch40 does all the bridging. Deliberate?
3. **ch42 has no forward pointer** to ch43 or Part V, though ch44 reuses its
   `Result`/`@safe` machinery heavily; the hand-off lives only in ch40 and
   ch43.
4. **ch17's opening line** "Other (special) objects create objects." gives
   "Other" no antecedent at the start of a chapter.
5. **ch18** "Ask your AI to convert the hot Python function" is a register
   outlier; deliberate?
6. **ch44 coins "implicit inputs"** as a synonym and never uses it again
   ("side causes" is the working term everywhere, including ch46/47).
7. **ch46** juxtaposes `Console`'s "`print_line()` and `read_line()`
   accessors" with "implements `input()` as well as `print()`" two sentences
   later; both are presumably true of the library, but unbridged it reads as
   a contradiction.
8. **ch46/47 pin behavior claims to "under `ty` 0.0.70"** in four places; the
   repo is past 0.0.75. The claims may still hold, but every ty upgrade
   stales them.
9. **ch26** spells the private implementation attribute four ways across
   listings (`__implementation`, `_implementation`, `_impl`, `_doc`); only
   one change is explained.
10. **`singledispatchmethod`** is treated three inconsistent ways: inline
    unlinked (ch32), linked to ch41 (ch33), mentioned unlinked (ch37).
11. **`__subclasses__()`** is used unexplained in ch32 and ch33; its
    introduction is inline in ch27. Consider links.
12. **Enum's home** is ch12's "Enums Are Types Too", but ch12's own Enum
    usage doesn't announce it and ch13 uses Enum without a link.
13. **ch47** links "partial handling" to `46#emptying-the-channels`; the
    layered-supply technique it invokes is actually demonstrated in ch46's
    Dependency Injection consequences. Consider retargeting.
14. **The parameterize-spelling policy** for the whole book lives in a ch17
    footnote.
15. **ch41's Memoization row in ch39** links to `#the-functools-toolkit`
    though the finer `#cache` anchor exists.

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
