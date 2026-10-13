> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 11_Techniques--Testing (2026-10-13)

I checked each claim against its listing and against the installed `pytest` 9.1.1, `time-machine` 3.5.1, `ty` 0.0.86, and Python 3.15.0.
Still true: `127.62815624999999` after five rounds of 5%,
`Random(0).randint(1, 6) == 4`,
`ty` reporting `unresolved-attribute` on `v._Vault__pin` with the ignore removed,
and `datetime` rejecting attribute assignment (`cannot set 'now' attribute of immutable type 'datetime.datetime'`, also through `monkeypatch.setattr()`).
In Solutions, three claims hold:
the rename failures in exercises 4 and 5 (`KeyError: 'APP_SETTINGS_DIR'` and the `AttributeError` naming `ch11_weather`, both reproduced),
the bit-identical results at rates 0.0, 0.05, 0.5, and 1.0,
and the one-bit difference at 0.1 in exercise 2.
`tip verify-ch CH=11 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after.
Last round's exercise 6 block is in the chapter.
No live blocks.

## Applied directly

Chapter, correctness:

- "The Clock": `stopwatch.py` measured an interval with `time.time()`, while the same section says `time.monotonic()` and `time.perf_counter()` are the clocks that "measure elapsed intervals". `elapsed()` now reads `time.monotonic()`, `test_stopwatch.py` patches `"monotonic"`, and a new sentence says why: `time.monotonic()` keeps counting when someone resets the system clock, and `time.time()` jumps with the reset. The `time-machine` paragraph now says the consequence: `stopwatch.elapsed()` keeps changing under `travel()`, so patching or injection still pins it. (Close alternative: keep `time.time()` and turn the function into the age of a stored timestamp, which needs the wall clock.)

Chapter, teaching:

- "Testing for Exceptions": added that `pytest` applies `match=` with `re.search()`, so `"less than 250"` matches part of `balance 100 is less than 250`, and that a pattern copied from a message holding `.` or `(` needs `re.escape()`.
- "The Clock": "`datetime.now()` is harder to patch" now shows the near-miss a reader writes, `monkeypatch.setattr(datetime, "now", ...)`, and the `TypeError` it raises.
- "Sharing Fixtures with conftest.py": the section opened on where a `conftest.py` fixture is visible before saying what the file is for. It now opens with the motivation (several test files need one fixture) and says `pytest` loads the file on its own. "A directory has one `conftest.py`" became "at most one".
- "Fixtures Replace Setup and Teardown": "a fixture needs only its shape" did not say which shape. It now says the `yield` divides the fixture into the code before it and the code after it, and that the generator chapter comes later.

Chapter, prose:

- "Fixtures Replace Setup and Teardown": split the teardown paragraph at the seam between where cleanup goes and how a failing check reports itself; "there" became "after the `yield`".
- Same section: "not the `Account` it returns" became "the function returns", since "it" could point to the decorator.
- "The Clock": "as the test's second assertion shows" pointed by position; it now quotes `datetime.now() == datetime.now()`.
- "Filesystem and Environment": cleared the passive "it is marked `autouse=True`".
- "Stubs and Mocks": dropped "plain" from "A plain stub cannot make that check".

Solutions:

- Exercise 6: the "Test the boundary with a mock" step repeated the opening paragraph's zero-boundary argument. It now says only what `assert_not_called()` checks and how the zero case catches `<=`, under the heading "Check the silence with a mock".

## Considered and declined

- "goes looking for the clock" (opening) and "goes looking for something no caller handed it" ("Making Code Testable") are figurative, but they echo each other on purpose, and Solutions exercise 5 quotes the second as "the chapter's description of a function that is hard to test".
- No exercise covers a session or parametrized fixture, or the clock. Exercises 4 and 5 already practice injection against patching, and a clock exercise would repeat them with a different dependency.
- Chapter 39's *Dependency Injection* row links `#isolating-tests-from-the-world`, while the definition sits in the "Random Numbers" subsection under it. The link lands one screen above the definition, inside the section that teaches it.
- `*mark*` is italicized in "Parametrizing Tests", though "the `parametrize` mark" appears first in the preview after `test_account.py`. The preview is deliberately informal, and the term is defined where it is italicized.
- `pytest.approx()` also has an absolute tolerance of 1e-12, which the chapter omits. It matters only near zero, and no listing compares near zero.

## For the session

- `tip watch-words` reports a stale baseline entry for this chapter: `only: and a fixture needs only its shape`. The sentence is gone, so the entry can be removed from `tools/data/watch_words_baseline.txt`.
- `tip verify-ch`'s sync step rewrote `Examples/11_Techniques--Testing/stopwatch.py` and `test_stopwatch.py` to match the edited listings; commit them with the chapter.
