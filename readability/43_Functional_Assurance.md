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
codec inside `property_check.py`). Every finding below is in that new prose.

One correction was made during the apply rather than recorded here, because it
was a false claim rather than a style judgment. The chapter said `ty` narrows
`case Ok(answer)` on a `Result[float, Exception]` to `object`. That stopped
being true earlier in this same run, when the chapter-42 review added `@final`
to `Ok` and `Err`: `match` now reaches `float`, exactly as `isinstance()` does.
The sentence now says the two narrow equally well and credits `@final`.

---

**Declarative Style, folded-in `match` paragraph: "is what lets either one land
on a single class" is a cleft the global rules name.**

> because `@final` on the two classes is what lets either one land on a single class.

Deleting "is what" leaves "because `@final` on the two classes lets either one
land on a single class," which means the same thing. The giveaway the rules
describe is present: a verb ("lets") immediately after the cleft.

This one is mine, from the correction described above, so it is a fair thing to
fix without ceremony.

Proposed change:

> because `@final` on the two classes lets either one land on a single class.

[] Reject

---

**Referential Transparency: `not_transparent.py`'s lead-in is a riddle.**

> An impure function shows what the property is worth by lacking it:

The sentence asks the reader to hold three abstractions at once (a function, a
property, the worth of the property) before they have seen the code, and
"by lacking it" arrives with two candidate referents for "it." A reader has to
reach the listing and come back.

Proposed change:

> The property is easier to see in a function that does not have it:

Alternative, naming the mechanism up front, which matches how the neighboring
paragraphs open:

> Substitution stops working the moment a function reads or writes outside itself:

I recommend the second. It states the claim the listing then demonstrates,
rather than promising that a demonstration is coming.

[] Reject

---

**Property-Based Testing: "so here is a codec with a real bug in it" is a
presentational aside, and "real" is doing no work.**

> Shrinking is easier to believe once you watch it happen,
> so here is a codec with a real bug in it:

"Here is a..." is the signposting pattern, and §34 covers the bare intensifier:
calling the bug "real" implies the chapter's other examples carry fake ones,
which is not the contrast intended. The contrast that *is* intended is with the
two passing listings above, where nothing fails.

Proposed change:

> The two listings above both pass, so nothing has shrunk yet.
> This codec has a bug:

That names the actual contrast, drops the intensifier, and cuts the
announcement.

[] Reject

---

**An Assurance Spectrum: the new rung 2 and rung 4 now explain the same
contrast twice.**

Rung 2, added by this pass:

> Each one pins a single input to a single answer,
> so the assurance you get is exactly as wide as the examples you think of.

Rung 4, which was already there:

> You state a law the code must obey,
> then check it against many generated inputs.

and then the section below it:

> The machine searches for a counterexample,
> instead of forcing you to write one example at a time.

The third quote was written when the list had no example-based rung, so it had
to introduce the contrast itself. Now that rung 2 states it, "instead of forcing
you to write one example at a time" is the second telling.

Proposed change: cut the trailing clause from the Property-Based Testing
section, leaving "The machine searches for a counterexample."

The rung 2 addition is the right place for the contrast, because it is where a
reader coming from [Testing](11_Testing.md) is looking for their own practice on
the ladder.

[] Reject

---

**Exercise 1: three questions in one numbered item.**

> Change `count_primes()` to return `(count, os.getpid())` and print the
> set of process IDs alongside the counts. How many distinct IDs do you
> get, and how does that compare to `os.process_cpu_count()`? Then replace
> `ProcessPoolExecutor` with `ThreadPoolExecutor` and explain the IDs you
> see instead.

The exercise is good and the answer is genuinely surprising (the solution
records 2, 3, and 3 distinct IDs across three runs on a 32-core machine). The
packaging is the problem: one item carries a code change, two questions, a
second code change, and a third question, and the reader has to keep the thread
while doing all four.

Proposed change: split into two exercises, 1 and 2, and renumber the rest.

> 1.  Change `count_primes()` to return `(count, os.getpid())` and print the
>     distinct process IDs alongside the counts. Compare that number to
>     `os.process_cpu_count()`, and run it three times before deciding what
>     it means.
> 2.  Replace `ProcessPoolExecutor` with `ThreadPoolExecutor` in the previous
>     exercise and explain the IDs you see instead.

Note the cost: renumbering exercises means renumbering every `## N.` heading in
`Solutions/43_Functional_Assurance.md`, and `check_solutions.py` gates that, so
the two files have to move together. That is the reason this is a proposal
rather than something I applied.

"Run it three times before deciding what it means" is added deliberately: a
single run makes the number look like a constant, and the whole lesson is that
it is not.

[] Reject

---

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
