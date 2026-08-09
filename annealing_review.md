# Annealing review

A settling pass over every chapter, run sequentially after the deep-review and
readability reviews were applied.
Normally `/annealing` writes no file and reports in chat;
this run records every applied change here instead, one section per chapter.

Everything recorded here is **already applied** to `Chapters/`.
Revert anything you dislike from `git diff Chapters/`.
Findings that did not clear the confidence bar were discarded unreported,
per the skill.
Structural change (cutting, reordering, pacing) stayed out of bounds throughout.

Started from a clean tree at `e6642ba`.
No unapplied `deep_review/` file exists for any chapter, so nothing was blocked.

## Progress

| Chapter | Status | Applied |
|---|---|---|
| 01_Introduction | done | 1 |
| 02_Tour | done | 1 |
| 03_Containers | done | 1 |
| 04_Control_Flow | done | 2 |
| 05_Functions | done | 0 (annealed clean) |
| 06_Modules_and_Packages | done | 2 |
| 07_Classes | done | 1 |
| 08_Static_Typing | done | 0 (annealed clean) |
| 09 through 47 | pending | |

---

## 01_Introduction

**Verified clean:** the five-part structure matches `build_site.py` `PARTS`
(I/02, II/11, III/20, IV/40, V/44), and each part's prose description matches the
chapters it actually spans.
`Examples/14_Decorators/tracer.py` and `Examples/utils/result.py` both exist as
named.
"Most chapters end with a short Exercises section" holds: 45 of 47.
The `14_Decorators.md#maintaining-the-wrapped-interface` anchor resolves.

**Applied:**

- **The Examples, output-marker paragraph.** "appears in the run of markers below
  the block" → "after the loop or the `import`". The chapter establishes "block"
  two paragraphs earlier as the whole fenced listing ("Every code block that
  begins with a filename comment"), so "below the block" read as *at the end of
  the listing*, which contradicts the markers-hug-their-code convention the
  sentence is there to explain. Naming the loop and the `import` removes the
  collision.

---

## 02_Tour

**Verified clean:** floor division and remainder signs (`-7 // 2` is `-4`,
`-7 % 2` is `1`, sign of `%` follows the divisor); banker's rounding in both
`round()` and the f-string format spec, which is what makes `{score:.0f}` on
`91.5` print `92`; `~x == -x - 1` and the `bin()` sign-and-magnitude rendering;
the `Template` piece sequence in `tstrings.py` (`('', ' scored ', '%')`, empty
literal skipped on iteration, `shout()` output).
All five exercises name variables and files that exist.

**Applied:**

- **Naming Conventions.** "The one exception is class names, which are
  `CapWords`" → "Class names are `CapWords`". The count was wrong: constants
  (`THIS_IS_A_CONSTANT`) are described in the immediately preceding paragraph and
  are already a departure from `snake_case`, and the *following* paragraph adds
  callable-style classes that use `snake_case` after all. Dropping the count
  loses nothing and stops the section contradicting its neighbors.

---

## 03_Containers

**Verified clean:** every set-algebra result and its method equivalent; the
`Counter` repr ordering; `deque(maxlen=3)` window contents; the live
`MappingProxyType` view; shallow-immutability behavior (`hash()` on a tuple
holding a list raises `TypeError`); dict `|` asymmetry.
Both threshold booleans have wide margins (`set_time * 100 < list_time` on an
O(n) vs O(1) scan at n=200,000; `deque_time * 20 < list_time` on O(n²) vs O(n)),
so neither is at risk of the flip described in `CLAUDE.md`.
All 23 example files exist, and `report()` resolves to `Examples/utils/benchmark.py`.

**Applied:**

- **Lists, before `list_traps.py`.** "Two ways of building a `list` produce
  surprises." → "Two list operations produce surprises." The promised pair is the
  `*` repetition trap and removing-while-iterating, and the second is not a way of
  *building* a list. The listing's other half (`[[0] for _ in range(3)]`) is the
  fix, not a second surprise, so the original sentence had no honest referent for
  its count.

---

## 04_Control_Flow

**Verified clean:** the Collatz trace in `while_loop.py` (six printed values, six
steps); the `zip(strict=True)` message text; the list-mutation skip in
`mutating_while_looping.py` (one of the two `2`s survives) and the dict's
`RuntimeError`; all three exception-chaining joining lines; the `isdigit()` /
`int()` disagreement running in both directions (`"-5"` rejected by one, `"²"`
accepted by one). Every exercise names a listing that exists.

**Applied:**

- **Placeholders, first paragraph.** "you have none to run yet**:**" → "yet**.**"
  The colon promised the listing, but a whole paragraph about `...` intervened
  before any code arrived. This is an edit seam: the `...` paragraph was clearly
  added between the `pass` sentence and its example, and the original colon was
  left pointing at nothing. The second paragraph's colon already introduces the
  listing correctly.
- **Loops, after `looping.py`.** "re-looks-up the item on every line that needs
  it" → "looks the item up again on every line that needs it." "re-looks-up" is
  not a construction English supports; the replacement preserves the meaning
  exactly.

---

## 05_Functions

**Annealed clean.** No finding cleared the bar.

One claim was worth verifying rather than trusting, and it survived: the chapter
states that each `sentinel()` call builds a new object even for the same name, so
`default is sentinel("MISSING")` is always false. PEP 661 sentinels are widely
described as caching per name and module, which would have made this wrong. Run
against the pinned interpreter (3.15.0rc1), `sentinel('MISSING') is
sentinel('MISSING')` is `False` and the repr is the bare name, so both the prose
and the `#: MISSING` marker are right as written. Recorded here so a later pass
does not "fix" a correct sentence.

Also verified: `bad_append.__defaults__` printing `([1, 2],)`, the `tally()`
positional/keyword split, the `all_markers.py` binding, and both `sorted()` key
orderings in `lambdas.py`.

---

## 06_Modules_and_Packages

**Verified clean:** the `from`-snapshot behavior in `from_snapshot.py`; the
`sys.modules` identity claims; every package listing's load-order markers.
`sys.lazy_modules` is real on the pinned build and reports deferred names, so the
PEP 810 paragraph is accurate.

**Applied:**

- **`PYTHONPATH` section.** The `-P` clause was moved out of the middle of the
  `sys.path` ordering into its own sentence at the end. The paragraph enumerates
  the search order (script directory, then `PYTHONPATH`, then installed
  packages), and the `-P` aside was spliced between the first and second items,
  so the reader lost the list mid-count. Every fact is retained.
- **`package_only.py`** (code block). `#: initializing a_package` moved from the
  clump at the listing's end up to the `import a_package` line that produces it.
  Every neighboring package listing in this chapter already hugs its markers this
  way; this one was the outlier. Re-synced and re-validated (`1 ok, 0 failed`).

---

## 07_Classes

**Verified clean:** the full `Simple2` override chain in `demo_simple2.py`
(including the four-line `show_twice()` trace); `cached_property` staleness and
the `del`-then-recompute sequence; `Circle(10).area` at 314.159 through both the
plain-attribute and validated-property versions; the `from_fahrenheit(212)`
conversion.

**Applied:**

- **`@override` at run time.** "It tries to set an `__override__` attribute on the
  method (some callables refuse it), for anything that wants to find overrides by
  introspection, and returns the same function object." → main clause first ("It
  returns the same function object"), with the attribute-setting subordinated and
  the purpose clause reattached to what it modifies. The original stranded "for
  anything that wants to find overrides" behind a parenthetical, so the sentence
  needed a second reading; it also used "wants" for a non-agent.

---

## 08_Static_Typing

**Annealed clean.** No finding cleared the bar.

Two things worth recording so a later pass does not undo them:

- **"where they earn their keep" (Gradual Typing) stays.** It looked like a
  candidate, since the chapter-26 deep review removed "earns its keep" from that
  chapter's conclusion at your instruction. But the figure appears **12 times**
  across the book (9 in `Chapters/`, 3 in `Solutions/`: 16, 21, 34, 40 twice, 41
  twice, 47, and this one). That makes it established vocabulary rather than a
  slip, and rewriting one instance would be a voice change, which annealing puts
  out of bounds. The chapter-26 removal was local to that chapter's conclusion.
- **The missing blank line after `# area.py` is load-bearing.** House style would
  suggest adding one, but the chapter quotes `ty`'s diagnostic verbatim including
  `--> area.py:6:12`, and the call sits on line 6 only because that blank line is
  absent. Adding it would silently falsify the quoted error block.

---

## Verification

`make reflow` on 01 through 08 (one paragraph rewrapped in 02 and one in 07, both
from the edits), `heading_links.py` → "Anchor links OK", `banned_phrases.py` →
"No banned phrases found".
The one code-block edit (06) was re-extracted and re-validated against a real run.
`heading_links.py` → "Anchor links OK", `banned_phrases.py` → "No banned phrases
found".
No fenced ```python block and no `#:` marker was touched in any of the three, so
the example tree is unaffected.
