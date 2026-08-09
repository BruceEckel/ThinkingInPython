When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

**Chapter-level, the biggest item: two of the five sections do not serve the
claim the intro makes, and the order buries the consequence that does.**

The intro states the claim in one sentence:
"This chapter asks what that machinery lets you claim about your code,
and how far those claims can go."
Run each section against it:

| Section | Assumes | Introduces | Serves the claim? |
|---|---|---|---|
| Referential Transparency | purity (40) | substitution, why `lru_cache` is sound | yes |
| Declarative Style | comprehensions (16) | what/how contrast | no |
| Pattern Matching as Destructuring | `match` (13), `Result` (42) | nothing new | no |
| Automatic Parallelism | purity (40), pools (19) | purity buys parallelism free | yes |
| An Assurance Spectrum | all of the above | four rungs, property-based testing | yes |

Declarative Style and Pattern Matching are the "functionality" thread from the
opening paragraph, not the assurance thread.
Nothing downstream depends on either: cut both and the spectrum still stands,
`parallel_pure.py` still runs, and the closing paragraph still lands.
Pattern Matching in particular introduces no new idea at all.
It restates chapter 13 and points at chapter 42, and its only claim about
assurance is the one I added in this pass, which is a *limit* on `match`.
Meanwhile Automatic Parallelism is the direct cash-out of Referential
Transparency and sits two sections away from it, with declarative material
wedged between.

Three ways to fix this. I recommend the first.

**Option A (recommended): reorder and merge.**
Referential Transparency → Automatic Parallelism → Declarative Style (with
Pattern Matching folded into it as two or three sentences) → An Assurance
Spectrum.
The chapter then reads as: here is the property, here is what it buys you for
free, here is the style that follows from it, here is how far you can push the
claims.
Price of the move, which I checked: heading anchors travel with their headings,
so reordering breaks nothing.
Inbound references are `Chapters/11_Testing.md:640` (`#an-assurance-spectrum`),
`Chapters/18_Performance.md:951` (`#declarative-style`) and
`Chapters/40_Functional_Foundations.md:69` (`#automatic-parallelism`); all three
survive a reorder, and folding Pattern Matching into Declarative Style removes
only `#pattern-matching-as-destructuring`, which nothing links to.

**Option B: restate the claim.**
Widen the intro's sentence so it covers both threads honestly, e.g.
"This chapter asks what that machinery lets you *say* — about the result you
want, and about the correctness you can claim."
Cheapest, changes no structure, but leaves the chapter a list of two topics.

**Option C: cut Declarative Style and Pattern Matching outright** and move the
SQL/NumPy paragraph into the Automatic Parallelism section, where "the runtime
is free to choose how" is already the point.
This is the honest minimum, but it takes the chapter from 12 KB to about 9 KB
and deletes an anchor chapter 18 links to.

[] Reject

---

**`property_check.py`: `encode()` and `decode()` are the same function, so the
law it demonstrates cannot fail.**

```python
def encode(text: str) -> str:
    return text[::-1]

def decode(text: str) -> str:
    return text[::-1]
```

`decode(encode(s)) == s` is then true by algebra for every `s`, with or without
the loop.
The prose says "it holds for every input the loop tries," which is accurate and
undersells the problem: it holds for every input there is, so the thousand
iterations are theater. A reader who notices this learns that property tests
pass, not that they catch anything.

`test_property.py` repeats both functions, so the same objection applies twice.

Proposed: make the pair a real inverse that is not an involution, so the
roundtrip is a genuine claim. A shift of one character is enough and keeps the
listing tiny:

> `encode()` returns `"".join(chr(ord(c) + 1) for c in text)` and `decode()`
> subtracts one.

Then the law says something, and the "avoid a property that restates the
implementation" warning later in the section has a body to be about.

Reported rather than applied because it touches two listings and their markers,
and because you may want `[::-1]` precisely for being obviously reversible at a
glance. If you keep `[::-1]`, one sentence would close the gap: "Both functions
are the same reversal, so this law cannot fail; it is here to show the shape of
a property, not to catch a bug."

[] Reject

---

**"Referential Transparency": the section defines the property and then only
shows a case where it holds. The near-miss is missing.**

`referential_transparency.py` substitutes `5` for `add(2, 3)` and gets the same
answer, which is what the reader already expected.
Nothing in the chapter shows substitution *failing*, so "you can replace it
with its value without changing the program's behavior" stays an abstraction.
The chapter has the perfect counterexample one chapter back: `withdraw()` from
[Foundations](40_Functional_Foundations.md#pure-functions), which the
Automatic Parallelism section already recalls by name forty lines later.

Verified listing (runs, deterministic, `ruff` clean at 70, `ty` clean,
`validate_output.py` accepts both markers unchanged):

```python
# not_transparent.py
balance = 100

def withdraw(amount: int) -> int:
    global balance
    balance -= amount
    return balance

print(withdraw(30) + withdraw(30))
#: 110
balance = 100
print(70 + withdraw(30))
#: 140
```

with prose after it such as:

> The first `withdraw(30)` evaluates to `70`, so substituting `70` for it ought
> to change nothing. It changes `110` into `140`. `withdraw()` is not
> referentially transparent, and neither is any expression containing it, which
> is why the substitution reasoning above stops at the first impure call.

The numbers deliberately match `pure_functions.py` in chapter 40, so the reader
recognizes the function.

Reported rather than applied because where a new listing goes is your call, and
because it doubles the section's code for a point you may prefer to leave to
chapter 40. A cheaper alternative is one sentence with no listing:
"Substitute `70` for the first `withdraw(30)` in `withdraw(30) + withdraw(30)`
and the answer moves from `110` to `140`."

[] Reject

---

**"Declarative Style": the section shows the *what* and only describes the
*how*, and it is the one section in the chapter with no listing.**

"The loop that filters and appends says *how*" — the loop never appears.
The reader is asked to compare two things when only one is on the page, in a
book whose method is to put both on the page.
The section is also cross-referenced from
`Chapters/18_Performance.md:951` ("This is the declarative trade from
Assurance"), so it is a destination, not a throwaway.

Recommended fix, no listing: finish the contrast inline, e.g.

> `squares = []`, then `for n in numbers:`, then `if n % 2 == 0:`, then
> `squares.append(n * n)` says *how*.
> `[n * n for n in numbers if n % 2 == 0]` says *what*, which is
> "the squares of the even numbers."

Alternative, a listing: four lines of loop and one comprehension with a shared
`#:` marker. I did not draft it because
[Comprehensions](16_Comprehensions.md) already owns that listing and repeating
it here buys the reader nothing they have not seen.

[] Reject

---

**"Property-Based Testing" is a `###` under another section, and it is the only
thing in the chapter the reader can go and do.**

Ask the deep-review question directly: what can the reader do at the end that
they could not do at the start?
Referential transparency, declarative style and pattern matching are all
recognition, not capability. `parallel_pure.py` is a demonstration of something
chapter 19 already taught.
The single new capability is "write a property test," and it lives in a
third-level subsection, reached after four rungs of preamble, with three of the
chapter's four exercises hanging off it.

Proposed: promote `### Property-Based Testing` to `## Property-Based Testing`.
The spectrum then ends at its own last rung and the technique gets a top-level
home matching its weight.

Cost, which is the reason this is reported and not applied: the promoted
heading changes nothing about the anchor (`#property-based-testing` is derived
from the same text either way), so no link breaks — but the spectrum's rung 3
currently links *down into* its own subsection
(`[*property-based testing*](#property-based-testing)`), and that link reads
differently once the target is a sibling section rather than a child.

**A change in another file, which I did not make:**
`Chapters/11_Testing.md:640` points at
`43_Functional_Assurance.md#an-assurance-spectrum` for property-based testing,
which lands the reader on the four-rung list one screen above the actual
material. It should point at `#property-based-testing`, whether or not the
heading is promoted.

[] Reject

---

**"Property-Based Testing": shrinking is the reason to use Hypothesis, and the
chapter only asserts it.**

"When a law fails, Hypothesis reports the failing input and shrinks it to the
smallest example that still fails" is the sentence that sells the tool, and
`test_property.py` passes, so the reader never sees a shrink.
The whole subsection shows two green runs.

Verified listing (runs; `ruff` clean at 70; `ty` clean, including
`e.__notes__`; `validate_output.py` accepts the markers unchanged; identical
output on six consecutive runs and under a changed `PYTHONHASHSEED`):

```python
# shrinking.py
from hypothesis import given, settings, strategies

def encode(text: str) -> str:
    return text.replace(" ", "_")

def decode(text: str) -> str:
    return text.replace("_", " ")

@settings(derandomize=True, database=None)
@given(strategies.text())
def roundtrip(sample: str) -> None:
    assert decode(encode(sample)) == sample

try:
    roundtrip()
except AssertionError as e:
    print(e.__notes__[0])
#: Failing test case: roundtrip(
#:     sample='_',
#: )
```

with prose such as:

> This `encode()` has a real bug: an underscore that was in the input comes
> back as a space.
> Hypothesis finds it and then keeps cutting the failing input down until
> nothing can be removed without the test passing again, so what it reports is
> `'_'` and not the forty-character string it happened to fail on first.
> That single character is the bug statement.
> `derandomize=True` fixes the search so this book gets the same answer every
> run, and `database=None` keeps it from replaying a case saved by an earlier
> run; a real test wants neither.
> `roundtrip()` is called directly, inside a `try`, because a `test_` function
> that fails is supposed to fail the build.

Three things to weigh before taking this:

- It would make **exercise 3 redundant**, which asks the reader to falsify
  `s.upper().lower() == s.lower()` and report the shrink. Keep the exercise:
  the laws are different, and the exercise's answer is a Unicode fact rather
  than a code bug. (For the record, the shrink there is `'ﬀ'`
  with `database=None`, and `'µ'` if a previous run left one in
  `.hypothesis/`, which is itself worth knowing.)
- The shrink target is a Hypothesis implementation detail. `'_'` is stable on
  6.164.0, but a version bump could move it, and the self-healing marker gate
  would rewrite it silently. Treat any `git diff` on those two markers as a
  signal to re-read the prose.
- It adds a fifth listing to a chapter with four, all inside one subsection.

Where it goes is your call; my suggestion is immediately after the paragraph
beginning "`@given(strategies.text())` feeds `test_roundtrip()`", before the
"family of reusable property shapes" paragraph.

[] Reject

---

**Intro, second paragraph: this chapter closes Part IV and never says what
comes next.**

The paragraph names 40, 41 and 42 and then says "This chapter asks what that
machinery lets you claim about your code."
`build_site.py`'s `PARTS` makes 44 the start of Part V, so a reader finishing
43 is at a part boundary with no signpost: they do not know that
[Effect Management](44_Effect_Management.md), [Generators](45_Generators.md),
[Stateless](46_Stateless.md) and
[Stateless in Practice](47_Stateless_in_Practice.md) exist, or that 44 opens by
listing every place the book has argued for purity — this chapter's own
argument, continued.

The natural place is the last paragraph of the chapter rather than the intro,
since that paragraph is already the Part IV summation
("The thread running through these chapters is not that functions are
special").
Proposed sentence to end it:

> Part V takes the same discipline one step further and asks the type checker
> to enforce it: [Effect Management](44_Effect_Management.md) puts a function's
> effects in its signature, and the chapters after it build a checked system on
> that idea.

Reported rather than applied because it changes the chapter's closing beat,
which is pacing.
(This is the other end of the finding in `deep_review/40_Functional_Foundations.md`
about the arc preview stopping at 44; take them together or not at all.)

[] Reject

---

**"An Assurance Spectrum": the rung most readers actually stand on is missing.**

The four rungs are local reasoning, type checking, property-based testing, and
formal proof. Ordinary example-based tests — the entire subject of
[Testing](11_Testing.md) — appear nowhere, even though rung 3 is introduced by
contrast with them ("instead of forcing you to write one example at a time")
and chapter 11 sends the reader here.
A reader who has just finished 11 will read this list and conclude their unit
tests were not on the ladder at all.

Proposed: insert a rung between 1 and 2, numbered 2, and renumber the rest:

> 2. Next are tests over chosen examples, the subject of
>    [Testing](11_Testing.md).
>    Each one pins a single input to a single answer, so the assurance you get
>    is exactly as wide as the examples you thought of.

That also makes rung 4's "instead of forcing you to write one example at a
time" a comparison with something the list has named.

Reported rather than applied because adding a rung changes the shape of the
chapter's central list, and because you may have left tests out deliberately on
the grounds that a test is not a claim about *every* input.

[] Reject

---

**"Automatic Parallelism": `parallel_pure.py` proves the answers agree and
never shows that anything ran in parallel.**

The listing's payoff is `assert parallel == serial`, which would also pass if
`pool.map()` silently ran everything in the main process.
The reader has to take "which the operating system places on separate cores" on
faith. Apply the mechanism-vs-outcome test: from the output `[1229, 2262, 3245,
4203]` alone, nobody can narrate the mechanism.

Wall-clock timing is out (the house rule in `thinking-in-python-skill.md` says
so, and this chapter would need a warm pool to be fair).
The cheap honest alternative is process identity: have `count_primes()` return
`(count, os.getpid())` and print `len(pids) > 1`.
I did not propose it as a chapter listing because that boolean is `False` on a
one-core machine and the self-healing marker gate would quietly rewrite it,
which is exactly the failure mode `CLAUDE.md` warns about for
`gil_threads.py`.

Recommendation: put it in the exercises instead of the chapter, replacing
exercise 1 (see the exercises block below), so the reader produces the evidence
on their own machine and no marker depends on the core count.

[] Reject

---

**`test_property.py` copies `encode()` and `decode()` out of
`property_check.py` and the chapter does not say why.**

The obvious reader move is `from property_check import encode, decode`, and it
is wrong here: importing that module runs its thousand-iteration loop and its
`print()` at import time, inside the test run.
That is the book's own "importable modules carry no top-level demo" rule
(`thinking-in-python-skill.md`) being broken by `property_check.py` and paid
for by `test_property.py`.

Two fixes. I recommend the first.

- One clause of prose: "The two functions are repeated here rather than
  imported, because importing `property_check.py` would run its loop."
- Split `property_check.py` the way the rule says: a `codec.py` holding
  `encode()`/`decode()`, and the loop in a separate file that imports it, with
  `test_property.py` importing the same module. Correct, and three files for a
  four-line point.

[] Reject

---

**Exercises: three of four exercise one subsection, and exercise 1 is already
answered in the Solutions file.**

Coverage today: 1 Automatic Parallelism, 2/3/4 Property-Based Testing.
Nothing exercises Referential Transparency, Declarative Style, or Pattern
Matching. Exercise 1 ("add a fifth limit, `50_000`, and confirm
`parallel == serial` still holds") is a one-token edit whose outcome the reader
can predict without running it, and
`Solutions/43_Functional_Assurance.md` prints the answer.

Proposed replacement for exercise 1, which makes the parallelism visible
instead of re-asserting it (this is the same idea as the mechanism finding
above):

> 1.  Change `count_primes()` to return `(count, os.getpid())` and print the
>     set of process IDs alongside the counts. How many distinct IDs do you
>     get, and how does that compare to `os.process_cpu_count()`? Then replace
>     `ProcessPoolExecutor` with `ThreadPoolExecutor` and explain the IDs you
>     see instead.

Proposed additions for the uncovered sections:

> 5.  Write a function that is *not* referentially transparent without using
>     `global`: one that reads `datetime.now()`, and one that reads an
>     environment variable. For each, name the substitution that would change
>     the program's behavior, then rewrite it so the value arrives as an
>     argument.
> 6.  Take the `describe()` function from
>     [Error Handling](42_Functional_Error_Handling.md#matching-on-the-error)
>     and rewrite its `match` as `isinstance()` tests. Count the lines, then
>     run `ty` on both and compare what each one knows about the value inside
>     the `Ok`.

Exercise 6 is deliberately the one that reports a result *against* `match`,
which is the honest finding and the one the section now mentions.

Reported rather than applied because the size and difficulty curve of an
exercise set is a pacing decision.

[] Reject

---

**"Declarative Style": "functionality" is used in a second, incompatible
sense.**

The intro sets the word up as a claim about science: "One definition of science
is 'what works'... theories that fit the data, are predictive, and are
falsifiable," and the conclusion cashes it as "code you can read, check, and
test as statements about what is true."
Line 72 uses it for something else entirely: "This is the broader
'functionality' you want. Describe the result, and let the machine arrange the
steps."
Describing a result rather than a sequence has nothing to do with
falsifiability, so the word carries two meanings twelve lines apart, with the
quotation marks implying they are the same one.

Proposed change: drop the sentence, or replace it with a claim that is true of
declarative code, e.g. "A description of the result is also easier to check
than a sequence of steps, because there is less of it to be wrong about."

Reported rather than applied because "functionality" is the chapter's thesis
word and only you can say which sense you meant.

[] Reject

---

**A change in another file, which I did not make:
`Solutions/43_Functional_Assurance.md` answers exercise 1 only.**

The file is 39 lines and stops after the fifth-limit answer. Exercises 2, 3 and
4 — the three Hypothesis ones, which are the chapter's real content and the
only ones a reader is likely to get stuck on — have no solutions.
Exercise 3 in particular has a specific right answer worth publishing:
`strategies.text()` shrinks `s.upper().lower() == s.lower()` to a single
character, and the Unicode fact behind it (a character whose uppercase form has
a different lowercase form, or a ligature whose uppercase form is two
characters) is not something a reader will derive unaided.

Verified on the pinned build: with `database=None` the shrink is `'ﬀ'`
(U+FB00, whose `.upper()` is `'FF'`), and with a `.hypothesis/examples`
database already holding a hit it is `'µ'` (U+00B5, whose `.upper()` is Greek
capital mu). Both are correct answers, which is itself a useful thing for the
solution to say.

[] Reject

---

**MANIFEST — not a proposal. Changes already applied to
`Chapters/43_Functional_Assurance.md` in this pass.**

(Gates re-run and passing after the last edit:
`extract_examples.py --write -o build/private/43`,
`validate_output.py --tree build/private/43`, `ruff check` at line length 70,
`ty check`, `pytest` (1 passed), `heading_links.py`, `banned_phrases.py`.
No code block changed, so `Examples/` needs no sync. No "promise" metaphor and
no "reach for" were present or introduced; every `#:` marker was confirmed
against a direct run of the extracted script.)

1.  "Referential Transparency": "a compiler can cache the call" → "an
    implementation is free to cache the call", plus two lines saying CPython
    does none of it on its own, because nothing marks `add()` as pure, so you
    ask for the reuse yourself. The old sentence invites the reader to believe
    Python optimizes pure calls; it does not, and the `lru_cache` paragraph
    that follows only makes sense once that is said.
2.  "Pattern Matching as Destructuring": added the assurance-side limit. `ty`
    narrows `case Ok(answer)` on a `Result[float, Exception]` to `object`,
    losing the `float`, which is why chapter 42's later listing uses
    `isinstance()`. Verified with `reveal_type()` against the extracted
    chapter-42 tree on `ty` 0.0.65: the `match` arm reveals `object`, the
    `isinstance` arm reveals the precise type. A section praising `match` with
    no mention of this sat one chapter after 42 says the opposite.
3.  "Automatic Parallelism": "`map()` runs the four calls" → "`list(map(...))`
    runs the four calls", since `map()` alone runs nothing.
4.  "Automatic Parallelism": added a paragraph on what purity does *not* buy —
    every argument and result is pickled, the function travels by name, a
    `lambda` or a closure fails with `PicklingError`, a `functools.partial`
    survives, and the `if __name__ == "__main__"` guard exists because each
    worker imports the module. All four verified on the pinned build
    (`pickle.dumps` on a partial succeeds; on a lambda and on a closure it
    raises `PicklingError`; `pool.map(lambda ...)` raises the same). This is
    the near-miss for a chapter that has spent 40-42 teaching lambdas,
    closures and `partial`, and `Solutions/43_Functional_Assurance.md` already
    depends on the fact without the chapter ever stating it. The existing
    pointer to [Concurrency](19_Concurrency.md#parallelism) now closes the
    paragraph, since chapter 19 already explains all of it in detail.
5.  "An Assurance Spectrum", rung 2: "Running `ty` ... demonstrates that proof
    for a useful class of mistakes" replaced. Python's Curry-Howard is partial
    — an `Any`, a `cast()`, or data from outside the program leaves a gap no
    checker can close, so the theorem holds only as far as the annotations do.
    A chapter about how far your claims reach cannot present gradual typing as
    proof without the caveat.
6.  "An Assurance Spectrum", rung 4: "Rocq" → "Rocq (formerly Coq)". The
    project renamed in 2025 and readers who know the tool know the old name.
7.  "Property-Based Testing": **corrected a false claim.** The chapter said
    Hypothesis supplies "awkward ones a hand-written loop misses, such as the
    empty string and unusual Unicode", but `property_check.py` draws its size
    from `random.randint(0, 8)`, so it produces the empty string roughly 111
    times in its thousand iterations. Replaced with the limitation that is
    real: the loop draws from the five-letter alphabet chosen above, and
    Hypothesis draws from the whole of `str`. Verified against
    `hypothesis/strategies/_internal/core.py`: `text()` defaults to
    `characters(codec="utf-8")`, the full Unicode range minus surrogates.
8.  "Property-Based Testing": added that Hypothesis runs a hundred cases by
    default, a tenth of the hand-written loop's thousand, and still covers
    more ground. Verified: the `default` profile registers
    `max_examples=100` and this repo registers no profile of its own. Without
    this the reader compares 1000 against an unknown and assumes the tool is
    winning on volume, when the point is that it is winning on aim.
9.  Exercise 4: **corrected a false instruction.** "note how the seeded
    generator keeps failures reproducible" describes `property_check.py`'s
    `random.seed(42)`, not Hypothesis, which the exercise is actually about.
    Replaced with the real mechanism and a task that exercises it: break the
    function, run twice, confirm the same counterexample, because Hypothesis
    records a failing case under `.hypothesis/` and replays it first.
    Verified by running a deliberately failing `@given` test under `pytest`
    and confirming `.hypothesis/examples/` is written.

Also checked and found clean, so no change was made: `count_primes()` is
correct and `[1229, 2262, 3245, 4203]` is right for the four limits; every
`#:` marker in the chapter matches a direct run; the `hypothesis` test passes
under `pytest`; every cross-chapter link resolves (`heading_links.py`); no
listing deviates from `thinking-in-python-skill.md` unexplained; headings are
title case and untouched; no em dash was added or removed.

[] Reject
