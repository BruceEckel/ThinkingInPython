When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

[] Reject

**Section: Test-Driven Development (TDD), lines 44-45.**
The section ends on "Once you have found a good path, / AI makes a thorough
test suite far cheaper to produce." This is the only mention of AI in the
chapter, it arrives with no setup, and nothing downstream uses it. As written
it reads as an aside dropped in at the end of a drafting session.

Proposed change: either cut the two lines, or finish the thought so it earns
its place, e.g.

> Once you have found a good path, the tests are cheap to add: describe
> the behavior you settled on and let an AI assistant draft the cases, then
> read them as specifications rather than as code.

Recommendation: cut it. The paragraph's argument ("TDD is wasteful while you
are still discovering the design") is complete without it, and a tooling
claim dates faster than the rest of the chapter.

---

[] Reject

**Listing: `account.py`, lines 63-86 — house-style audit.**
`Account.__init__()` does nothing but assign a defaulted parameter to a
field. The book's own style rule (`thinking-in-python-skill.md`, "Structure
and idiom") says such a class is a `@dataclass`, and that a manual form is
written only when the code is teaching the manual form, with the reason
stated nearby. Nothing here says why. `grep "def __init__(self" ` over this
chapter returns exactly this one plus `InsufficientFunds.__init__()`, which
is a legitimate manual form (it builds a message and calls `super()`).

The conversion is one line:

```python
@dataclass
class Account:
    balance: float = 0.0
```

Price of making the change, which is why I did not apply it:

- The traceback listing at lines 140-151 shows
  `where 100.0 = <account.Account object>.balance`. A dataclass gets a
  generated `__repr__`, so that line becomes
  `where 100.0 = Account(balance=100.0).balance`. The listing must be
  updated by hand; nothing gates a fenced `text` block.
- `Solutions/11_Testing.md` repeats the same hand-written `Account` three
  times (exercises 1, 2, 3) and would drift out of step.

Recommendation: keep the plain class, but add one clause saying why, so the
deviation reads as deliberate. For instance, after line 86: "`Account` is a
plain class rather than a `@dataclass` so its `repr` stays out of the way in
the failure reports below." Alternative: convert both the chapter and the
solutions and re-capture the traceback.

---

[] Reject

**Listing: `test_interest_uses_approx()`, lines 123-125, and the prose at
lines 191-195 — the floating-point example does not demonstrate the problem
it is introduced to solve.**

Verified on the pinned 3.15 build: `100.0 + 100.0 * 0.05` is exactly
`105.0`, so `assert funded.balance == 105.0` passes just as well as the
`pytest.approx()` version. A reader who tries it discovers that `approx()`
made no difference here, which undercuts "testing for exact equality is
unreliable." Every round rate on a round balance behaves the same way; I
checked 0.03, 0.045, 0.06, 0.07, 0.075, 0.08, 0.09, 0.12, 0.15 and all are
bit-exact.

A case that genuinely needs `approx()` has to accumulate error. Applying 5%
five times gives `127.62815624999999`, where exact equality against
`127.62815625` fails and `approx()` passes (both verified).

Proposed change: replace the test with one that compounds, and say so:

```python
def test_interest_compounds(funded: Account) -> None:
    for _ in range(5):
        funded.add_interest(0.05)
    assert funded.balance == pytest.approx(127.62815625)
```

with prose noting that the exact-equality form of this assertion fails,
because the fifth application lands on `127.62815624999999`.

Alternatives, if you would rather not disturb the flagship listing:
(a) keep `test_interest_uses_approx()` and add the compounding test beside
it, so the reader sees both the harmless case and the one that bites;
(b) keep the listing and add one sentence admitting that this particular
arithmetic happens to come out exact, and that `approx()` is the habit
rather than the rescue. Recommendation: (a).

---

[] Reject

**Section heading, line 157: "Testing for Exceptions and Floating Point".**
Two unrelated topics joined by "and". The section body even announces the
split itself ("Two situations come up repeatedly"), which is the tell.

Proposed change: split into two short sections, "Testing for Exceptions" and
"Comparing Floating-Point Values", and drop the "Two situations come up
repeatedly in testing, / and both appear in `test_account.py`." bridge. Cost:
no chapter links to this heading (checked with grep across `Chapters/`), so
the anchor change is free.

---

[] Reject

**Sections "Parametrizing Tests" (line 197) and "Sharing Fixtures with
conftest.py" (line 283) — a lookalike pair the chapter uses but never
contrasts.**

`@pytest.mark.parametrize(...)` and `@pytest.fixture(params=[...])` both
"run the test once per value" and both appear within a few pages of each
other, so a reader has no way to know when to use which. The chapter states
each mechanism separately and leaves the choice unexplained.

Proposed change: one sentence after line 315 (the end of the `preloaded` explanation):

> `parametrize` multiplies the one test it decorates; a parametrized fixture
> multiplies every test that requests it, in this file and every other file
> that can see the `conftest.py`. Use the mark when the cases belong to one
> test, and the fixture when the same variation should sweep across a whole
> suite.

---

[] Reject

**Listing: `conftest.py`, lines 292-305 — three new things in one listing.**
The section introduces (1) fixtures shared through `conftest.py`,
(2) `scope="session"` and the reuse hazard, and (3) `params=` and
`request.param`. Each is unfamiliar, and the listing carries two of them
simultaneously with a paragraph of caveat between the code and its use.

Proposed change: split into two listings. The first `conftest.py` holds only
`bank_name` and demonstrates the "no import needed" point, which is what the
section is titled for. A second, smaller listing adds `preloaded` when
fixture parametrization is introduced. Cost: one extra fenced block and one
extra sentence of connective prose; `test_fixtures.py` stays as it is.

---

[] Reject

**Listing: `test_fixtures.py`, lines 316-327 — two unrelated assertions in
one test.**
`test_deposit_on_any_balance()` asserts the deposit arithmetic and then
asserts `bank_name`, which has nothing to do with deposits. The book's style
skill states the rule this breaks: "One behavior per test; a test with two
unrelated assertions hides which one actually failed." A testing chapter is
the worst place to model the thing it would tell you not to do.

Proposed change: drop `assert bank_name` and its trailing comment from the
test, and add a second one-line test that uses the session fixture on its
own:

```python
def test_bank_name_is_shared(bank_name: str) -> None:
    assert bank_name == "Crunchy Frog Credit Union"
```

That also gives the "nothing imports either fixture" sentence at line 329 two
clean examples instead of one crowded one.

---

[] Reject

**Section "Fixtures Replace Setup and Teardown", lines 275-278 — the
`autouse` mention is too thin to use.**
Three lines and an indented fragment with no listing, no motivating case, and
no statement of the one thing that trips people up: an autouse fixture runs,
but the test cannot see its return value unless it also names the fixture as
a parameter. A reader who tries `autouse=True` on `funded` and then writes
`funded.withdraw(40)` gets a `NameError`.

Proposed change: add that sentence, and name the case autouse is actually
for, which is a side effect rather than a value, e.g. resetting a global
registry or installing a `monkeypatch` every test needs. Alternative: cut the
`autouse` mention entirely and let the reader meet it in the pytest docs; it
is currently doing less work than the space it takes.

---

[] Reject

**Section "### The Clock", lines 476-493 — `clock.py`'s example is
tautological, and it changes the subject mid-comparison.**

Two problems in one place:

1. `def stamp(now: Callable[[], float]) -> float: return now()` has no
   behavior, so `assert clock.stamp(lambda: 100.0) == 100.0` asserts that a
   lambda returns its own constant. Nothing about the code under test is
   verified, and a reader cannot see what injection bought.
2. The `monkeypatch` half of the comparison patches `stopwatch.elapsed()`,
   and the injection half introduces a different function, `stamp()`. The two
   approaches are never applied to the same code, so the reader cannot line
   them up. The randomness subsection does this correctly: `dice.roll()` and
   `dice_rng.roll()` are the same function, patched then injected.

Proposed change: make the injected version the same computation as the
patched one, and give it behavior worth asserting:

```python
# clock_injected.py
from collections.abc import Callable

def elapsed(start: float, now: Callable[[], float]) -> float:
    return now() - start
```

```python
# test_clock_injected.py
import clock_injected

def test_elapsed() -> None:
    assert clock_injected.elapsed(40.0, lambda: 100.0) == 60.0
```

Then the prose can say plainly that the patched test and the injected test
check the identical arithmetic, and only the injected one needs no
`monkeypatch`. Cost: renames two example files (`clock.py`,
`test_clock.py`), which are not referenced from any other chapter.

---

[] Reject

**Section "### Random Numbers", line 443 — the seeded value collides with the
patched one.**
`test_dice.py` forces `randint()` to return 4, and four listings later
`test_dice_rng.py` asserts `dice_rng.roll(random.Random(0)) == 4`. A reader
can reasonably conclude that 4 is significant, or that the seeded generator
was chosen to agree with the stub.

Proposed change: one clause after line 449, e.g. "The 4 here is simply what
`Random(0)` produces first; as above, you record the value the seed gives you
rather than picking it." Alternative: change the stub in `test_dice.py` to
return something else (3), so the two numbers cannot be confused. I prefer
the clause, since it reinforces the point made two paragraphs earlier.

---

[] Reject

**Section placement: "White-Box and Black-Box Tests" (line 581).**
This section defines the vocabulary that justifies how the `Account` tests
were written from the first page, and it introduces no machinery of its own.
Sitting after the whole of "Isolating Tests from the World", it reads as an
appendix, and its payoff line ("The `Account` tests are black-box, which
means they never read a private attribute") points back four sections.

Proposed change: move it to immediately after the exceptions/floating-point
material, before "Parametrizing Tests" — or, more conservatively, before
"Isolating Tests from the World". Then "Isolating Tests from the World" reads
as the natural consequence: you test through the public surface, so you have
to control what that surface reaches for.

Price of the move, checked:

- `Chapters/24_Singleton.md:339` links to
  `11_Testing.md#white-box-and-black-box-tests`. The anchor is derived from
  the heading text, not its position, so the link keeps working. Nothing else
  in `Chapters/` or `Solutions/` names this section.
- The section defines nothing that earlier sections use, and depends on
  nothing except the existence of the `Account` tests, which precede both
  candidate positions.
- `name_mangling.py` moves with it; it has no dependents.

So the move is cheap. The only real cost is that the chapter's conceptual
digression then interrupts the run of pytest mechanics, which is an argument
for the more conservative position.

---

[] Reject

**Section "How This Book Runs Its Tests" (line 645) — the chapter's
conclusion is buried under an infrastructure heading.**
Lines 646-649 are about this repository's build. Lines 651-658 are the
chapter's conclusion, and a good one: they name the capability the reader
gained and end on the best line in the chapter ("a function that is hard to
test is usually one that goes looking for something it was never handed").
Under a heading that promises build notes, a reader skimming for content will
skip both.

Proposed change: split into two sections. Keep "How This Book Runs Its Tests"
as the four-line build note, then start a new `##` section titled for its
content — "Making Code Testable" — holding the closing paragraph.

---

[] Reject

**Front-load the payoff (opening, lines 3-17).**
The chapter's most convincing claim is its last sentence: a function that is
hard to test is one that goes looking for something it was never handed. The
opening argues for tests on the familiar safety-net grounds, which a reader
who picked up this chapter probably already accepts.

Proposed change: put a one-line version of the payoff in the opening, after
line 11, so the reader knows the chapter is about design and not only about
`pytest` syntax. For example: "Tests also push back on the design. A function
you cannot test easily is usually one that goes looking for the clock, the
filesystem, or the network instead of being handed them." Leave the full
version where it is.

---

[] Reject

**Missing: how to run less than the whole suite.**
Line 128 is the chapter's only instruction on running tests: "Run the test
suite by typing `pytest` in the project directory." The first thing a reader
needs once a suite is more than a page long is how to run one test, rerun
only the failures, and stop at the first error. None of `-k`, `-x`, `-v`,
`--lf`, or `-q` appears anywhere in the chapter.

Proposed change: three or four lines after the discovery paragraph at
line 135:

> `pytest -k overdraft` runs only the tests whose names contain "overdraft",
> `pytest -x` stops at the first failure, and `pytest --lf` reruns just the
> tests that failed last time. Those three cover most of a working day.

---

[] Reject

**Missing: coverage, and skip/xfail marks.**
Two gaps a reader will hit immediately in real work and cannot answer from
this chapter:

1. Nothing says how you find out what is *not* tested. One sentence naming
   `coverage.py` and `pytest --cov` would close it, with the usual caveat
   that a covered line is not a tested line.
2. `@pytest.mark.skip`, `@pytest.mark.skipif`, and `@pytest.mark.xfail` are
   the other marks a reader meets in any existing suite, and `parametrize` is
   the only mark the chapter shows. One sentence naming them, and saying that
   `xfail` records a known bug so the suite stays green without deleting the
   test, is enough.

Proposed change: add both as a short paragraph, either at the end of
"Parametrizing Tests" (for the marks) and the end of the chapter (for
coverage), or as one small "What Else Is In pytest" section before "Property-
Based Testing". Recommendation: the marks belong with `parametrize`, since
that is where the reader learns what a mark is; coverage belongs near the
conclusion.

---

[] Reject

**Exercises (line 661) — coverage of the chapter's claims is uneven.**
Exercises 1-3 all work on `Account` and cover TDD, `parametrize`, and
`yield` fixtures. Exercise 4 covers `monkeypatch`/`tmp_path`/injection.
Nothing exercises `pytest.raises(match=)`, `conftest.py` and fixture scope,
stubbing a boundary function (the `urlopen` pattern, which is the chapter's
most transferable technique), or the white-box/black-box distinction.

Proposed change: add one exercise on stubbing a boundary, which is the
technique most likely to be needed and the one with no exercise at all:

> 5.  `weather.current_temp()` calls `urlopen()`. Write a second function
>     that takes a fetcher as an argument instead, and test both: one with
>     `monkeypatch`, one with a plain function passed in. Then rename
>     `weather.urlopen` to `weather.fetch` and see which test still passes.

That last clause makes the same point exercise 4 makes about the environment
variable's name, applied to a different kind of dependency.

---

## Cross-chapter

**`Solutions/11_Testing.md`, exercise 2 explanation (out of scope for this
review; reported, not changed).**

The solution says:

> `pytest.approx()` absorbs the ordinary floating-point rounding in
> `100 * 1.05` versus `100 + 100 * 0.05`, so the test checks the intended
> relationship instead of exact bit-for-bit equality.

Verified on the pinned build: for all four parametrized rates (0.0, 0.05,
0.5, 1.0), `100 + 100 * rate` and `100 * (1 + rate)` are bit-identical, so
there is no rounding for `approx()` to absorb and the test would pass with
`==`. This is the same defect as the chapter finding above, in the same
arithmetic.

Suggested change in that file: either pick rates where the two forms
genuinely differ, or replace the sentence with an honest one — that
`approx()` is used because the general relationship it checks is not
guaranteed to be exact, not because these four cases round.

**`Chapters/24_Singleton.md:339`** links to
`11_Testing.md#white-box-and-black-box-tests`. If the section-move finding
above is accepted, no edit is needed there: the anchor is derived from the
heading text and the heading text does not change. Recorded here only so the
link is not missed if the heading is ever retitled.
