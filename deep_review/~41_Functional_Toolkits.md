[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/41_Functional_Toolkits.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty` and ruff are clean on `build/examples/41_Functional_Toolkits`, and the
chapter has no test files or third-party imports (every listing is stdlib).
The version-dependent and numeric claims were each verified by probe on the
pinned 3.15 beta: `partial` in a class body binds `self` for the keyword form
(the 3.14 descriptor change) and the positional form fails with the exact
`AttributeError: 'int' object has no attribute 'value'` the prose quotes; the
`reduce()`, `batched(strict=True)`, and `zip(strict=True)` error messages are
verbatim; an instrumented undecorated `fib(30)` makes 2,692,537 calls; the
bare `sentinel("MISSING")` in `itertools_zip_longest.py` is legal because
`sentinel` is a builtin on 3.15 (no import missing); and `product()` really
does consume its inputs before its first yield (a noisy generator printed
before the constructor returned). The circle-method arithmetic holds
(`n - 1` rounds, `n * (n - 1) / 2` pairs, for even `n`; see the applied
list), the 21-of-21 / 14-repeats figures are consistent (7 rounds times 5
pair-meetings is 35, and 35 - 21 = 14), and the Kirkman claim is right
(triple systems exist only for `n ≡ 3 (mod 6)`). Inbound anchors from 33,
39, 40, 43, and 47 (`#singledispatchmethod`, `#the-functools-toolkit`,
`#cache`, `#lru_cache`, `#case-study-pairing-rotations`) all still resolve;
no heading was changed. The `recursion.py` two-lessons exemption in
`deep_review_db.md` was honored and is not re-flagged. The db's note that
chapter 41 has no exercises is overtaken: the chapter now has six, and
`Solutions/41_Functional_Toolkits.md` exists and gates. No finding needs a
decision, so this file has no live blocks; everything found was either
applied directly or recorded below as considered and declined.

## Applied directly

- `reduce` section: added a two-line gloss on `operator.add` (`+` as a
  function; the `operator` module supplies one per operator, so a fold never
  needs `lambda a, b: a + b`). The chapter imports `operator` twice and no
  chapter in the book explains the module.
- Circle method: scoped the `n - 1`-rounds claim to an even number of
  players (perfect matchings do not exist for odd `n`) and added the
  classical phantom-player bye for an odd roster, which also gives the later
  "join-instead-of-sit-out choice" phrase its referent.
- `product` section: added the eager-input caution, probe-verified:
  `product()` reads its inputs completely before yielding its first tuple,
  so `product(count(1), "AB")` hangs at the call. The chapter is about
  laziness, and this is the one catalog entry a reader would compose with
  `count()` and be surprised.
- `cycle` section: added the matching buffering caution (saves each element
  on the first pass, so the whole input stays in memory for as long as the
  cycle lives), the other lazy-looking tool that buffers.
- `accumulate` section: added the lookalike link to `reduce()`: accumulate
  is reduce with the intermediate results kept, and its last value is what
  `reduce()` would return.
- `zip_longest` section: "a distinct sentinel" now links to chapter 5's
  Default and Keyword Arguments, where `sentinel()` was introduced; the
  listing uses it with no import (3.15 builtin) and no other pointer.
- `student_pairs.py`: renamed the module-level `met` list to `meetings`; it
  collided with the `met()` helper defined inside `group_rounds()` in the
  same listing. Hoisted `distinct = set(meetings)`, which also keeps the
  print under the 70-character limit. Output markers unchanged.
- `cached_property` section: "mutating a property doesn't recalculate the
  cached result" is now "changing an attribute the property read doesn't
  recalculate the cached result"; the demo assigns to `x.n`, not to the
  property.
- `repeat` section: "The fixed form is a list you would have written" is now
  "replaces the list you would have written" (`repeat()` yields an iterator,
  not a list).
- Conclusion: "a sliding window is `pairwise()`" is now "a width-two sliding
  window" (`pairwise()` is only ever width two).
- `functools` intro: "Caching logic, an eviction policy, a dispatch table:
  each hides..." (was two "each one" sentences in a row); serial comma in
  "`reduce()`, `partial()`, and the two caches".
- `reduce` section: "instead of raising" is now "instead of raising an
  exception" (house rule: raise takes an object).
- `cache` section: "This only works correctly for pure functions" is now
  "This works correctly only for pure functions" (modifier placement);
  "the counts show what that bought" is now "show what caching saved"
  ("buy" is on the watch list).
- `partialmethod` section: "here happens to work" is now "here works too"
  ("happen" watch list; the fragility is carried by the next sentence).
- `singledispatch`: dropped "at all"; `singledispatchmethod`: "never on
  `self` itself" is now "never on `self`".
- `tee` section: dropped "anyway" from "stores the whole sequence anyway"
  (the next sentence draws that conclusion).
- `nested_sum` prose: "says nothing at all about depth" is now "says nothing
  about depth".
- `make reflow CH=41` run over the new prose.

## Considered and declined

- **The `reduce` example folds addition, the one case the next sentence
  says not to use `reduce()` for.** A fold with no dedicated built-in
  (running `max` by key, merging dicts) would avoid teaching a tool on its
  own counterexample. Declined: the catalog entry's job is the mechanics in
  two lines, the prose draws the `sum()`/`math.prod()` boundary immediately,
  and the new `operator` gloss gives the entry its added value without a
  longer listing.
- **The twin intros repeat "already ... already"** ("already written and
  already correct" in `functools`, "already tuned in C and already correct"
  in `itertools`). Reads as a deliberate echo binding the two catalogs; left
  alone.
- **`groupby` prose says it "only merges neighbors"** where "groups
  consecutive runs" is the more precise verb. The meaning is clear in
  context and the first line of the section already says "consecutive";
  left alone.
- **"1-factorize a complete graph into perfect matchings" is redundant** (a
  1-factorization is by definition into perfect matchings). Kept: the tail
  glosses the jargon for readers meeting the term here.
- **`permutations` entry says "Every ordering of `r` elements" while the
  demo omits `r`** (default is the full length). The phrasing matches the
  `combinations` entry and the demo output makes the default obvious; left
  alone.
