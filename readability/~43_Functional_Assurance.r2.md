> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/43_Functional_Assurance.md`

Second review of this chapter.
The findings in `readability/~43_Functional_Assurance.md` were all accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one reshaped the chapter: Automatic
Parallelism moved up to sit against Referential Transparency, Pattern Matching
was folded into Declarative Style, Property-Based Testing was promoted to a
top-level section, a fifth rung was inserted into the spectrum, and three
listings were added or rewritten (`not_transparent.py`, `shrinking.py`, and the
codec inside `property_check.py`). Every finding was in that new prose.

One correction was made during the apply rather than recorded here, because it
was a false claim rather than a style judgment. The chapter said `ty` narrows
`case Ok(answer)` on a `Result[float, Exception]` to `object`. That stopped
being true earlier in this same run, when the chapter-42 review added `@final`
to `Ok` and `Err`: `match` now reaches `float`, exactly as `isinstance()` does.
The sentence now says the two narrow equally well and credits `@final`.

Every finding was resolved directly and applied (listed below).
No blocks remain.

## Applied directly

- "because `@final` on the two classes is what lets either one land on a
  single class." → "lets either one narrow to a single class." (the cleft
  the global rule names, and "land on" is a "Don't use" metaphor; "narrow"
  is the literal verb the surrounding sentences use).
- `not_transparent.py` lead-in: "An impure function shows what the property
  is worth by lacking it:" → "Substitution stops working the moment a
  function reads or writes outside itself:" (the old sentence held three
  abstractions and an ambiguous "it"; the new one states the claim the
  listing then demonstrates, matching how the neighboring paragraphs open).
- Property-Based Testing: "Shrinking is easier to believe once you watch it
  happen, so here is a codec with a real bug in it:" → "The two listings
  above both pass, so nothing has shrunk yet. This codec has a bug:" (names
  the actual contrast, drops the §34 intensifier and the "here is a"
  announcement).
- "The machine searches for a counterexample, instead of forcing you to
  write one example at a time." → "The machine searches for a
  counterexample." (the trailing clause predates the new rung 2, which now
  states the example-at-a-time contrast where a reader coming from
  [Testing](11_Testing.md) is looking for their own practice on the ladder).

- Exercise 1 split into two: "Change `count_primes()`... How many distinct
  IDs do you get... Then replace `ProcessPoolExecutor` with
  `ThreadPoolExecutor` and explain the IDs you see instead" was one item
  carrying a code change, two questions, a second code change, and a third
  question. It is now exercise 1 (the process-pool change, comparison, and
  "run it three times before deciding what it means") and exercise 2 (the
  `ThreadPoolExecutor` swap), with exercises 2-6 renumbered to 3-7.
  `Solutions/43_Functional_Assurance.md` was split and renumbered to match:
  its old `## 1` became `## 1` (process pool only) and a new `## 2` (the
  thread-pool half, carrying the "thread pool reports exactly 1" paragraph
  that used to close the combined solution), and its old `## 2`-`## 6`
  became `## 3`-`## 7`. `check_solutions.py` confirms the two files line
  up. "Run it three times before deciding what it means" is new text: a
  single run makes the number look like a constant, and the whole lesson is
  that it is not.

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- The `shrinking.py` follow-up ends "That single character is the whole bug
  statement," which has the shape of a §32 aphorism. It restates a concrete fact
  the listing just printed (`sample='_'`) rather than generalizing beyond it,
  and it is the sentence that explains why shrinking matters. Not flagged.
- The new `not_transparent.py` prose was checked against the
  imperative-plus-consequence ban. It states the substitution as a condition
  ("The first `withdraw(30)` evaluates to `70`, so substituting `70` for it
  ought to change nothing") rather than commanding the reader and reporting the
  result. Clean.
- "A description of the result is also easier to check than a sequence of
  steps, because there is less of it to be wrong about" replaced the
  double-sense use of "functionality" that the deep review flagged. The
  replacement makes a checkable claim and does not reuse the thesis word. Worth
  confirming you are happy with the substitution, since the deleted sentence
  was the one place the chapter's title word appeared mid-chapter.
