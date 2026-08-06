[[Reviewed]]
# Deep review: 11_Testing.md

**How to use this file:** delete a `##` block to reject that proposal, edit its text to change what gets implemented, leave it alone to accept it. Hand the file back when you are done.

---

## 1. Explain where a patch lands: a module object versus an imported name

**Kind:** teaching
**Where:** section "Random Numbers" (line ~339) and "Network Calls" (line ~493)
**Problem:** The chapter patches three things and the reader is given one rule, at the end, that appears to contradict the first two.
`test_dice.py` writes `monkeypatch.setattr(dice.random, "randint", ...)`, which reads as "patch randomness *for the dice module*."
It is not.
`import random` binds the one shared module object, so `dice.random is random` is `True` and the patch replaces `randint()` for every module in the process (verified: after that `setattr`, a direct `random.randint(1, 6)` returns 4).
`test_stopwatch.py` does the same with `time`.
Then the network section says "Patch the name at its point of use, `weather.urlopen()`, rather than the original in `urllib`," which works only because `from urllib.request import urlopen` copies the *function* into `weather`'s namespace.
A reader who takes the `dice.random` form as the model will write `monkeypatch.setattr(weather.urllib.request, "urlopen", ...)` and wonder why the two cases differ, or will believe a module-level patch is scoped when it is global.
This is the single most common monkeypatch confusion and the chapter has all the material for it but never joins the two halves.

**Proposal:** Add two sentences after `test_dice.py` (after "Patching the function gives you the value you want.", line ~354):

> `import random` binds the one module object every importer shares,
> so `dice.random` and `random` are the same object and the patch replaces `randint()` process-wide.
> `monkeypatch` restores the original when the test ends, which is what keeps that safe.

Then change the network paragraph (line ~493) to name the contrast rather than state a bare rule:

> `weather` imports the function with `from urllib.request import urlopen`,
> which copies it into `weather`'s own namespace,
> so `weather.urlopen` is the name the call site reads and the name to patch.
> Patching `urllib.request.urlopen` instead would leave `weather`'s copy untouched.
> The rule covers both cases: patch the name the calling code looks up.

**Alternatives:** (a) change `test_dice.py` to `monkeypatch.setattr(random, "randint", ...)`, dropping the misleading `dice.` prefix, and add only the network-side sentences; (b) move the "where to patch" paragraph up to the dice example and have the network section refer back to it.
**Cost:** none to code if the sentences-only version is taken. Alternative (a) edits `test_dice.py`, which nothing else references.

---

## 2. Show what a failing test actually prints

**Kind:** teaching
**Where:** section "pytest" (line ~131)
**Problem:** The chapter twice states the payoff of assertion rewriting ("a failure still shows you both sides of the comparison", "prints the expression and the actual values, so you rarely need a debugger") and never shows it.
Every listing in the chapter passes, so a reader finishes without having seen the one output that testing is *for*.
This is mechanism-versus-outcome: the reader is told the result and shown none of it.

**Proposal:** After "so you rarely need a debugger to see what went wrong." (line ~132), add a short paragraph and a non-extractable output block (no `# slug.py` first line, so the build ignores it).
Real output, captured from pytest 9.1.1 on this repo:

> Change the expected value in `test_deposit_increases_balance()` to `10` and the report names the line, the expression, and both sides:
>
> ```text
> ______________ test_deposit_increases_balance ______________
>
>     def test_deposit_increases_balance() -> None:
>         account = Account()
>         account.deposit(100)
> >       assert account.balance == 10
> E       assert 100.0 == 10
> E        +  where 100.0 = <account.Account object>.balance
>
> test_account.py:6: AssertionError
> ```
>
> The `where` line is the rewriting at work: `pytest` kept the sub-expression `account.balance` and its value, which a bare `assert` statement would have discarded.

**Cost:** none. The block is `text`, not `python`, so `extract_examples.py` skips it and no gate runs against it.

---

## 3. Teach `pytest.raises(..., match=...)` and keeping the block narrow

**Kind:** teaching
**Where:** section "Testing for Exceptions and Floating Point" (line ~139)
**Problem:** The chapter shows `pytest.raises(SomeType)` and stops there, which leaves two gaps.
First, the test passes when *any* statement in the `with` block raises that type, so a reader who wraps several lines gets a test that can pass for the wrong reason.
Second, `InsufficientFunds` was given a formatted message carrying the balance and the amount, and nothing in the chapter ever checks it; `match=` is the tool for that, and chapter 12 already uses `match="Cannot overwrite"` with no introduction anywhere.

**Proposal:** Extend the exceptions paragraph with a sentence pair and one listing:

> Keep the `with` block down to the single call that should fail.
> Any statement inside it that raises the expected type passes the test, including one that fails for an unrelated reason.
> `match=` takes a regular expression checked against the exception's message, so the test can confirm which failure occurred and not just its type:

```python
# test_overdraft_message.py
import pytest
from account import Account, InsufficientFunds

def test_overdraft_reports_the_shortfall() -> None:
    account = Account(100)
    with pytest.raises(InsufficientFunds, match="less than 250"):
        account.withdraw(250)
    assert account.balance == 100
```

> The assertion after the block belongs outside it: a failed withdrawal must leave the balance alone, and that check has nothing to do with the exception.

Verified passing against the chapter's `account.py`.
**Cost:** one new listing and one new extracted file; `Account(100)` reuses the existing class unchanged. Exercise 1 asks for "an overdraft that leaves both accounts unchanged," which this listing now models, so the exercise may want rewording to stay a real exercise.

---

## 4. Warn that a session-scoped fixture is shared, not rebuilt

**Kind:** teaching
**Where:** section "Sharing Fixtures with conftest.py" (line ~253)
**Problem:** The chapter carefully teaches isolation for the default scope ("Each test gets its own freshly built `funded` account, so tests cannot leak state into each other"), then introduces `scope="session"` with the single upside, "useful for expensive resources."
The example value is a `str`, so nothing shows the cost.
A reader who applies `scope="session"` to a database handle or an `Account` gets exactly the cross-test leakage the chapter warned about two sections earlier, and the chapter never says so.

**Proposal:** Extend the sentence at line ~253:

> `pytest` builds the `scope="session"` fixture once and reuses it,
> which is useful for expensive resources.
> The reuse is the risk as well as the point:
> every test receives the same object, so one test that mutates it changes what the next test sees.
> Keep session fixtures to values nothing modifies, like `bank_name`,
> or to a resource with its own reset, and leave anything a test writes to at the default per-test scope.

**Cost:** none.

---

## 5. Say how `test_account.py` finds `account.py`

**Kind:** teaching
**Where:** section "pytest" (line ~128)
**Problem:** `from account import Account` works because pytest's default `prepend` import mode puts the test file's own directory at the front of `sys.path` when the file is not inside a package.
A reader copying this layout into a project with a `src/` directory, or with `__init__.py` files, gets `ModuleNotFoundError: No module named 'account'` and has nothing in the chapter to diagnose it with.
One sentence closes the gap and it is a question every reader hits on their first real suite.

**Proposal:** After "Run the test suite by typing `pytest` in the project directory." (line ~128), add:

> `pytest` puts each test file's own directory at the front of `sys.path`,
> which is why `from account import Account` works with no packaging and no path setup,
> as long as `account.py` sits beside `test_account.py`.

Confirmed against pytest 9.1.1: `--import-mode` still defaults to `prepend`.
**Cost:** none.

---

## 6. Replace "Tests extend the language" with something the reader can use

**Kind:** prose
**Where:** opening (line ~5)
**Problem:** "Tests extend the language" is the fourth sentence of the chapter and nothing explains it.
The sentence after it ("They state what the code is supposed to do, and check it") is a different claim, not the explanation, so a reader either skips the line or stops to decode a metaphor that is never cashed in.

**Proposal:** Cash the claim in, since it is a real point about a dynamically typed language:

> A type checker verifies the claims you can write as annotations.
> Tests verify the rest: that a withdrawal reduces the balance, that an overdraft is refused.
> They state what the code is supposed to do, and check it.

**Alternatives:** (a) cut the sentence and go straight to "They state what the code is supposed to do, and check it"; (b) keep the line and add one sentence of explanation after it.
**Cost:** none.

---

## 7. Add an exercise on isolation

**Kind:** exercise
**Where:** section "Exercises" (line ~574)
**Problem:** Three of the chapter's ten-odd pages cover isolating tests from the filesystem, the environment, randomness, the clock, and the network, along with the argument that injecting a dependency beats patching it.
None of the three exercises touches any of that; all three exercise `Account`.
The set clusters on the first half of the chapter.

**Proposal:** Add a fourth exercise:

> 4.  Write `settings_path()`, which returns `Path(os.environ["APP_CONFIG"]) / "settings.ini"`,
>     and test it with `monkeypatch` and `tmp_path`.
>     Then rewrite the function to take the directory as an argument and test it again.
>     Which test would survive a change to the environment variable's name?

**Cost:** needs a matching entry in `Solutions/11_Testing.md` (the existing three all have solutions).

---

## 8. Name `unittest.mock` once, and define "stub"

**Kind:** teaching
**Where:** section "Network Calls" (line ~477), or a sentence in "Isolating Tests from the World"
**Problem:** The chapter's isolation toolkit is `monkeypatch` plus dependency injection, which is a defensible choice, but `unittest.mock` is what the reader will meet in every existing codebase and in most search results.
Saying nothing leaves them thinking the book's approach and the world's approach are unrelated.
"Stub" also arrives undefined at line ~477 ("swaps `urlopen()` for a stub").

**Proposal:** Add a short paragraph at the end of "Network Calls":

> A stand-in like `fake_urlopen()` is called a *stub*: it answers with a canned value and records nothing.
> The standard library's `unittest.mock` builds stubs for you, along with *mocks* that also record how they were called,
> and you will meet it in most existing code.
> This book patches with `monkeypatch` and prefers injection where the code can be changed,
> because a function that takes its clock or its fetcher as an argument needs no patching library at all.

**Cost:** none; no new listing.

---

## 9. Prose pass: seven small edits

**Kind:** prose
**Where:** scattered
**Problem:** Watch-list words and a few phrasings that read out of character.
**Proposal:** Apply as a group, or strike any line to reject it.

- line ~33: "not a verification step you skip when you happen to feel good about the code you just wrote" → "not a verification step you skip when the code looks right to you." ("happen" is on the watch list, and the sentence runs long.)
- line ~44: "AI makes generating tests far more viable once you have found a good path, and makes a thorough test suite easier to produce." Both halves say the same thing. → "Once you have found a good path, AI makes a thorough test suite far cheaper to produce."
- line ~139: `The first is "this call should cause an exception."` → `The first is "this call should raise an exception."` ("cause an exception" is not how the rest of the book says it.)
- line ~228: "Less code generally makes tests easier to read and verify." A generic claim that adds nothing after "Fixtures eliminate duplicated setup." → cut it, or replace with the specific point: "A test that names `funded` states what it needs and nothing about how to build it."
- line ~354: "Patching the function gives you the value you want." Restates the listing. → cut, or fold into proposal 1's replacement text.
- line ~458: "for code already steeped in `datetime`" → "for code built around `datetime`." ("steeped in" is a metaphor doing a literal job.)
- lines ~537-540: the name-mangling paragraph says twice that `ty` cannot see the rewrite (line ~517 said it once already). Cut the second: "...so `v._Vault__pin` reads it successfully." and let the earlier sentence carry the point.

**Cost:** none.

---

## 10. The chapter ends on a build note rather than a closing thought

**Kind:** structure
**Where:** section "How This Book Runs Its Tests" (line ~567)
**Problem:** The last section before the exercises is four lines about this repository's build.
It is useful context, but it means the chapter's final word is about the book's infrastructure rather than about testing, and the reader is never told what they can now do that they could not before.
"Property-Based Testing," the section before it, is a three-sentence forward pointer, so the last two sections in a row hand the reader off elsewhere.

**Proposal:** Keep the build note but add two or three closing sentences after it, naming the capability gained: the reader can now take an untested function, identify what it depends on (clock, randomness, filesystem, network), replace those dependencies at the boundary, and pin the rest with a handful of parametrized cases.
Retitle if the added material warrants it.

**Alternatives:** (a) move "How This Book Runs Its Tests" up to just after the `pytest` section, where it explains why the reader can trust the listings, and end the chapter on the black-box/property-based material; (b) leave as is.
**Cost:** none for the added sentences. Alternative (a) moves a section, but nothing links to its heading.

---

## 11. Comments in the listings narrate the code the prose already explains

**Kind:** code
**Where:** `test_account.py` (line ~103), `test_teardown.py` (lines ~207-209)
**Problem:** House style keeps descriptions in prose and leaves comments for tool directives and the file marker.
Four comments here narrate: `# Make three tests, replacing "bad" with each list value:` (which also ends on a colon, unlike every other one-line comment in the chapter), and `# Setup, before the yield` / `# The test runs with this value` / `# Teardown, after the test`, whose content is repeated word for word in the paragraph directly below the listing.
**Proposal:** Drop the three teardown comments, since lines ~217-220 already say "Everything before the `yield` is setup. Everything after it runs once the test finishes."
Keep the `parametrize` comment (it lands before the reader has met `parametrize`, which is explained two sections later) but drop its trailing colon.
**Alternatives:** leave all four; they are clearly deliberate teaching aids and this is a chapter for beginners.
**Cost:** touches two extracted files; no test depends on the comments.

---

## 12. `Account` hand-writes an `__init__` that `@dataclass` would generate

**Kind:** code
**Where:** `account.py` (line ~71)
**Problem:** House style says a class whose `__init__()` only assigns parameters or defaults to fields is a `@dataclass`, and that a deliberate deviation should say why.
`Account.__init__` assigns one parameter with one default.
The deviation is almost certainly right here (dataclasses are not taught until chapter 12, one chapter later, and chapter 7 only forward-references them), but nothing in the chapter says so, and the next style sweep will flag it again.
**Proposal:** Leave the class as written and add nothing to the chapter; instead this note records the decision so it is not re-litigated.
If you would rather the reader see it, a half-sentence works: "`Account` is written out longhand because `@dataclass` is not introduced until [Data Classes as Types](12_Data_Classes_as_Types.md)."
**Cost:** none either way.

---

## Already fixed directly (no decision needed)

- line ~428: "because `datetime` is a built-in type" was the wrong reason. `datetime.datetime` is not a built-in type; it resists patching because it is a C-implemented immutable type. Verified: `datetime.datetime.now = ...` raises `TypeError: cannot set 'now' attribute of immutable type 'datetime.datetime'`. Now reads "because `datetime` is an immutable C type that rejects attribute assignment".
- line ~550: "The `Account` tests are black-box which means they never read a private attribute." was missing the comma before the non-restrictive "which" clause. Split onto two lines with the comma restored, per Semantic Line Breaks.

Gates run before editing, all green against the pre-edit tree: `pytest` (23 passed), `ruff check`, `ty check`, `name_mangling.py` output matches its `#:` markers. After the edits: `reflow_prose.py --diff 11` reports 0 paragraphs, `banned_phrases.py` clean, `heading_links.py` clean. Both edits are prose-only, so `Examples/` is untouched.
