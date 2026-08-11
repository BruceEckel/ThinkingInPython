When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/11_Testing.md` in the clean-slate
sweep. The mechanical layer is sound: the chapter's one `#:` marker validates,
`ty` and ruff are clean on `build/examples/11_Testing` (verified on both the
pinned 0.0.69 and today's 0.0.70, where the `# type: ignore` on
`v._Vault__pin` is still used, so "`ty` does not model this rewriting" still
holds), all 26 tests pass under pytest 9.1.1, and all 9 scripts run. The
chapter's behavioral claims were re-verified by probe: the failure report in
the text block matches pytest 9's output line for line (including
`test_account.py:11: AssertionError`), a directly-called fixture reports
`Fixture "funded" called directly`, a failing teardown assertion prints
`1 passed, 1 error`, `random.Random(0).randint(1, 6)` is 4, five compounded
5% applications produce `127.62815624999999`, and `time-machine` imports and
passes on the pinned 3.15 beta. One numeric claim was measurably wrong and is
fixed below. The rest of the round is prose and teaching repairs; no listing
changed, so `Examples/` is untouched. No findings met the bar for a live
block.

## Applied directly

- Floating-point section: "and so is every other round rate on a round
  balance" overclaimed. Probed: on a balance of 100.0 every whole-percent
  rate is exact, but on 10.0 five rates (46%, 56%, 59%, 83%, 92%) miss the
  correctly-rounded decimal. Now "every other whole-percent rate on this
  starting balance", which is the verified claim.
- After the first `test_account.py` listing: added a two-line preview naming
  `parametrize` and the `funded` fixture as features with their own sections
  later. A first-time reader hits `@pytest.mark.parametrize` and a fixture
  parameter with no explanation until pages later; the preview says the
  explanation is coming.
- "Five applications of 5% land on ..." now "produce" (banned "land").
- TDD section: "The tests seem to lose their importance" became "Once the
  code works, the tests feel less important" (second "seem" in three
  sentences, and the new form states the reason later never comes).
- TDD section: "what direction a program will take you" mixed two idioms;
  now "what direction the program will take".
- Fixtures: "a test that calls `funded()` itself fails" dropped "itself";
  "still has to appear" became "must still appear".
- Filesystem section: "which is what lets `monkeypatch.setenv()` redirect
  it" lost "is what"; "at import time, which happens before any test body
  runs" lost "which happens"; "would move nothing" became "would change
  nothing".
- Random section: "which is what keeps that safe" lost "is what".
- Exceptions section: "it would never run at all" dropped "at all".
- Network section: "so no request ever leaves the machine" dropped "ever".
- Conclusion: "which `pytest --cov` wires up for you" now names the
  `pytest-cov` plugin, since a bare `pytest --cov` with no plugin installed
  errors out and the old phrasing read as built-in.
- Ran `make reflow CH=11` over the edited prose.

## Considered and declined

- `unittest.mock` gets two sentences and no listing. Deliberate: the chapter
  states its preference for `monkeypatch` and injection, and a mock listing
  would teach an API the book then advises against.
- The `# Make three tests, replacing "bad" with each list value` comment in
  `test_account.py` narrates rather than directs, but it predates this
  review and the style rule leaves existing comments alone.
- "It discovers every `test_*.py` file" omits pytest's second default
  pattern (`*_test.py`). The chapter teaches the convention it uses;
  the second pattern is tool-manual detail.
- `pytest.approx()`'s absolute-tolerance default (1e-12) is unmentioned.
  "A relative difference of 1e-6, unless you pass `rel=` or `abs=`" is a
  fair simplification at this altitude.
- "How This Book Runs Its Tests" is four lines of meta. It answers the
  question the chapter raises about its own listings and stops; left alone.
- `name_mangling.py` has a blank line between the header comment and
  `class Vault:`; ten other chapters use the same shape for import-free
  listings, so it is the convention, not a deviation.
