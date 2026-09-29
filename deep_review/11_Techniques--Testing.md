> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 11_Techniques--Testing (2026-09-29)

Part of the book-wide review of chapters 01-29 and the appendices.
I checked each claim against its listing and against the installed `pytest` 9.1.1, `time-machine` 3.5.1, and `ty` 0.0.84.
Everything the chapter quotes holds today:
the assertion-rewriting report and its `test_account.py:11` line,
`Fixture "funded" called directly`, `1 passed, 1 error` for a failing teardown check,
the `AttributeError` from an autouse fixture used by its bare name (`'FixtureFunctionDefinition' object has no attribute 'withdraw'`),
the `approx()` default of 1e-6, `127.62815624999999` after five rounds of 5%,
exact results for every whole-percent rate from 0 to 100 on a balance of 100,
`Random(0).randint(1, 6) == 4`, `datetime` rejecting attribute assignment,
`time.monotonic()` and `time.perf_counter()` advancing under `travel(..., tick=False)`,
and `ty` reporting `unresolved-attribute` on `v._Vault__pin`.
`tip verify-ch CH=11` passes 24 of 24.
One block needs your decision.

## Applied directly

Chapter, teaching:

- "Random Numbers": the chapter used "injecting" and "injection" throughout without defining the term, and chapter 39's catalog row for *Dependency Injection* links to this section. Added a sentence after `dice_rng.py`'s discussion that names *dependency injection* and says what it is, so "As with randomness, injecting the clock" now follows a definition.
- "Filesystem and Environment": the section opened on `storage.py` with no lead-in, and the next paragraph's "The tests point it at" had no antecedent. Added a one-sentence lead-in naming what `storage.py` does, and "it" became `APP_DATA`.
- "Sharing Fixtures with conftest.py": `preloaded` takes a `request` parameter the prose never explained. Now says `request` is a built-in fixture that `preloaded` receives by naming it.
- "Stubs and Mocks": added the near-miss. A `Mock` accepts a call the real function would reject, so a test keeps passing after the signature changes; `create_autospec()` builds a mock that checks the signature. Verified both behaviors.

Chapter, prose:

- "Stubs and Mocks": the second and third sentences both said a mock records its calls. The first now says only that `unittest.mock` builds stubs and mocks, and "the call itself" is "the call".
- "Comparing Floating-Point Values": "and so is every other whole-percent rate" read as "every rate is `105.0`". Now "gives an exact result too".
- "The Clock": "Unlike `monkeypatch`, `time-machine` is a third-party dependency" overlooked that `pytest` is third-party too. Now "Unlike `monkeypatch`, which comes with `pytest`, `time-machine` is a separate dependency".
- Watch-list words whose deletion changes nothing: "that exact name", "what actually runs", "what Python actually stored", "this exact argument".

Solutions:

- Exercises 1, 2, 3: the local `Account` copies had a hand-written `__init__()` that only assigned `balance`, while the chapter's `Account` is a `@dataclass`. All three now follow the chapter listing.
- Exercise 3: `never_negative()` had no return annotation. Now `-> Iterator[Account]`, as `open_account()` has in the chapter.
- Exercise 5: `fetch` was typed `Callable[[str], io.IOBase]`, and typeshed declares `IOBase.read` as returning `Any`. Now `io.BufferedIOBase`, whose `read()` returns `bytes`; `BytesIO` and `urlopen()`'s response both fit.
- Exercise 5 prose: "Rename the import, move the call ..., and the patched test breaks" was an imperative followed by its consequence. Now a gerund subject.
- Exercise 4 prose: "what the function promises" is now "what the function does".
- Exercise 3 prose: "whether it passes or raises" gained its object; "is itself an assertion" lost "itself".
- Exercise 1 prose: dropped "at all" and the emphasis italics on "before".

## Blocks

### No exercise covers a mock, a session fixture, or the clock

The five exercises cover TDD, `parametrize` with `approx()`, a `yield` fixture,
the environment, and the network stub.
"Stubs and Mocks" has a listing and no exercise,
and `test_notifier.py` checks only the branch that sends.
The branch that stays silent is the one a mock is best at checking,
since a stub cannot report that it was never called.

Proposed exercise 6, appended so no number changes:

> 6.  `test_notifier.py` checks that a negative balance sends a message.
>     Write the test for the other branch:
>     a balance of zero or more sends nothing.
>     Then write the same test with a hand-written stub in place of the `Mock`.
>     What must the stub gain to make the check?

The solution uses `send.assert_not_called()`,
then a stub that appends to a list, which is a mock written by hand.

I did not add it because the chapter steers the reader away from `unittest.mock`
("This book patches with `monkeypatch` and prefers injection"),
and only you know whether leaving it without an exercise is part of that steer.

[] Reject

## Considered and declined

- `test_account.py` previews `parametrize` and a fixture in one listing, against "one new thing per listing". The prose says it is a preview, and three later sections refer back to its tests by name. Splitting it would strand those references.
- The comment "Make three tests, replacing "bad" with each list value" in `test_account.py` explains what prose could. It predates this review, so it stays.
- "White-Box and Black-Box Tests" shows name mangling and no white-box test. Chapters 24 and 26 link to this section for mangling, and a test that reads `_Vault__pin` would add a listing to make a point the prose makes in one sentence.
- `pytest.raises(...) as excinfo` is not taught. `match=` covers what the chapter needs.
- "A test is just a function ... A check is just Python's built-in `assert`": the repeated "just" is a deliberate parallel.
- "That failure is the point" in the TDD section states why the test runs before the code exists, so it is not filler.
- `pytest` also collects `*_test.py` files and `Test` classes. The chapter's "every `test_*.py` file ... every `test_` function" is a simplification that matches every listing in the book.
