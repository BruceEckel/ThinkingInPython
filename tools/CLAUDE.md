# Working in tools/

Loaded when working under `tools/`. Moved from the root `CLAUDE.md`'s Traps.

- **`tools/*.py` is not linted by any gate.** Only `build/examples` is checked by
  `tip lint`/`tip ci`, so a `tools/` script can exceed the 70-char limit with
  nothing catching it (several already do). `ty` still matters there; run it
  directly, e.g. `uv run ty check tools/whatever.py`.
- **Kindle listings: only the real book is a valid test bed, and
  line-leading whitespace is half width there.** Send to Kindle (email)
  converts a tiny standalone probe EPUB differently from the full book
  (probes rendered `pre` in Bookerly whatever the CSS said; the book
  renders it monospace), so four probes gave answers the book then
  contradicted. Test a listing change by building the book with a probe
  chapter in front (a scratch script that monkeypatches
  `build_epub.book_markdown`/`epub_css`, then `build()`), never a
  separate small EPUB. Measured in the book on a Paperwhite: spaces or
  `&#160;` at the start of a line draw at ~0.54 of a character; the same
  whitespace after any glyph, even U+200B, draws full width; `ch` is
  unsupported (zero); `6em` came out ~8.4 characters, not 10; a named
  family before `monospace` (`"Courier New", Courier, monospace`) loses
  the monospace entirely. Hence `listing_html()` prefixes each indented
  line with `&#8203;` and keeps plain spaces, and `CODE_FONT` is the
  bare keyword. Project memory `kindle-listing-indentation` has the
  probe script layout.
  The Kindle also justifies a `pre` like prose, stretching the
  spaces (indent included) on any line that wraps, so `pre` sets
  `text-align: left`; and `CHAR_EM` is 0.72, the Paperwhite's
  figure, since a hang computed at 0.6 came out level with the
  code it continues (2026-09-26 photo).

## Moved from the root CLAUDE.md (2026-09-29)

These notes concern the tools themselves, so they load only when
working under `tools/`.

### Gate skip stamps

Since 2026-09-26 the gate skips work that cannot
find anything new (`tools/skip_stamps.py` has the policy): `verify`
passes `MARKERS=fresh` so the gate does not refresh the markers a
second time, the tools' own tests run only when `tools/` changed
since they last passed (tests marked `book` always run), and `run`
executes only listings without `#:` markers, with a full run of
every listing once a day, and `tip output` refreshes only chapters
whose Markdown or `utils/` changed since their markers last passed,
or all of them when the checker changed (the `tools` modules it
loads, `norun.txt`, `timing.txt`, `uv.lock`, `.python-version`). `tip gate RUN=full`, `tip ci`, and `tip release` turn the
shortcuts off (`TIP_FULL=1`), and `tip everything` does too, then
adds spell, prose (Vale), site, EPUB, and PDF, keeping going past a
failure (`tools/everything.py`). A new tools test that reads a
chapter, not a fixture, needs `@pytest.mark.book`; a listing that
reads another chapter's directory would break the marker skip,
whose digest covers only its own Markdown and `utils/`.

### Self-reference, link-support, and edit-pattern tools

A third rule, `grounding`, fires when a sentence links to a chapter that
contains *none* of the code terms the sentence names. It finds the real
thing (chapter 07's case), and it also fires on sentences whose terms
belong to the *linking* chapter: all 41 of its findings on 2026-09-27.
Since that date a model tells the two apart. `tip grounding-triage`
(`tools/grounding_triage.py`, TypeSafe, needs `TYPESAFE_API_KEY`) asks
about each finding with no stored verdict and commits the answer to
`tools/data/grounding_verdicts.json`. The gate reads that file offline: a
sentence judged to attribute its terms to the target is SR004 and fails,
one judged to credit only an idea drops out, and one with no verdict yet
stays SR002, which `tip self-reference-report` lists and the gate does
not. So a new misattribution passes the gate until someone runs the
triage; run it after editing a sentence that links another chapter.
`ARGS=--calibrate` re-asks five planted misattributions and every stored
case, for a model or wording change.

`tip link-support` (`tools/link_support.py`) asks the neighboring
question of every anchored cross-chapter link: does the linked section
cover what the sentence credits it with? It reports and never gates,
and caches in `tools/data/link_support_verdicts.json`. Its first run
found chapter 42 linking "put the meaning in the type" to annotation
syntax in chapter 08. `tools/prose_calibration.py` asks five questions of
sentences Bruce rewrote in his editor commits and of neighbors he left
alone: four Scores (subject-verb distance, ambiguous pointers, skipped
steps, overloaded claims) and a Noul, `would_rewrite`, that shows six
before/after pairs from `bruce_edit_db.md` and asks whether he would
rewrite the sentence.
It reports on the half of the commits the examples did not come from.
On 2026-09-27 (115 restructured rewrites, 299 controls) `would_rewrite`
led at AUC 0.66 ± 0.03, unchanged by length banding; pointers and
skipped steps were near 0.58, subject-verb distance near chance.
On 2026-10-03 (110 restructured rewrites, 294 controls) the added
`overloaded` question scored AUC 0.59 ± 0.03, 0.58 within length
bands. That trails `would_rewrite` (0.63) and sits just under
pointers (0.62) and skipped steps (0.61).
The same day three Nouls took the wordings of the riff prose linter's
rules that had read well on chapter 30 (`preamble`, `fractal_summary`,
`comma_tail`), asked with the sentence's paragraph and heading as
`edit_patterns.py` asks: 0.54, 0.50, and 0.56 on the restructured
rewrites, so none of them tracks what Bruce rewrites, and `comma_tail`
alone reaches the Score questions' range.
That is enough to rank sentences for a human, not to edit on. Rerun it
before letting a model score steer a prose pass.

`tip edit-patterns` (`tools/edit_patterns.py`, `/edit-done` step 3b)
turns each sentence Bruce rewrites into a search: the before/after
pair joins `tools/data/edit_pairs.json`, and once it carries a one-line
`fault` it is checked against its own before and after and then
searched for across `Chapters/`. Without a fault line the search
matches surface features (chapter 30's metadiscourse cut matched 158
sentences for ending in a colon); with one, the metadiscourse pair's
top hits were real metadiscourse. The fault line's wording decides the
precision, so a loose hit list means rewording the fault, not raising
the 0.7 floor. Since 2026-09-27 a question sees the sentence's
paragraph and section heading, not only its neighbors. That cleared
the chapter 12 false alarms a passage-conditioned fault ("in a
passage that does not already name the mechanism") had drawn, and it
raised scores generally: the appositive and metadiscourse faults went
from 69 and 77 hits to 139 and 127, and the chain-to-condition
fault's list took in sentences already in "If you" form. Bruce then
labeled ten sampled hits for each of six faults on a blind labeling
page (scores hidden, order shuffled), and each labeled pair now
carries its own `floor` and a `floor_basis`, 0.62 for R21 up to 0.84
for R2; `REPORT`'s docstring gives the rule. Reading the hits myself
had got R21 backward: I called its colon hits the wrong shape, and he
marked nine of ten right. For three of the six faults the score did
not put the right hits first, so a floor is a rough filter and a long
hit list is still a review batch. `ARGS=--from-rules`
searches for `bruce_edit_db.md`'s promoted rules, each rule's title,
Test, and Keep-when lines as the fault and, as its example, the
sighting the pair check separates best (the longest sighting, used
first, gave R12 its counter-example). With paragraphs, 14 of 19
rules were searchable; R9 found its own sighting's shape ("sets a
single attribute that nothing reads"); R5 cannot find its bullets,
which the scan skips. Fixing the R17 hits it listed (commit 7af64701)
left one hit: chapter 07's gerund-subject sentence, which the rule
allows. The search reports; it never edits. All four tools share
`tools/judgments.py`, and the SDK
joins only their runs, through `uv run --with typesafe-sdk`: it builds
`pydantic-core` from source on the pinned Python, so it stays out of
`pyproject.toml`.

### Traps

- **A session can start without `TYPESAFE_API_KEY` although it is set.**
  The key lives in the user's Windows environment (`HKCU\Environment`),
  and a process inherits the environment its parent held when it started,
  so a Claude Code session launched from an older shell sees no key.
  Since 2026-09-29 `judgments.api_key()`, which `ask()` calls first, falls
  back to that registry value, so every TypeSafe tool finds the key
  anyway. A "No TYPESAFE_API_KEY found" that names both places means the
  key is truly unset; don't work around it by pasting it into a command.

- **`validate_output.py` on the whole tree can leak `__del__` output between
  chapters.** It `exec()`s every block's code against a fresh `namespace` dict
  reused as that block's globals. A class defined there forms a reference
  cycle with its own globals (`SomeClass.method.__globals__ is namespace`),
  so plain refcounting never frees it; CPython's cyclic collector runs on its
  own schedule and can finalize it while a *different*, later block's stdout
  is being captured, corrupting that block's output. The fix lives in
  `validate_output.py` itself: drop the last reference to a block's
  `namespace` and call `gc.collect()` (see `collect_now()`) right after the
  block finishes, before moving on. Chapter 10 (Cleanup)'s `cleanup.py` is
  the example that demonstrates this (it deliberately relies on `__del__`
  timing being unpredictable), so it is the usual trigger if this regresses.
- **`run_examples.py` and `validate_output.py`: never pass a relative
  `--tree`.** It goes on `PYTHONPATH` and breaks once an example changes cwd.
  `validate_output.py` manifests this as `ModuleNotFoundError` on a `utils/`
  helper (`No module named 'greeter'` across every block that imports one),
  which reads as a broken listing rather than a bad flag; an absolute
  `--tree` fixes all of them at once. GUI/interactive examples are skipped via
  `tools/data/norun.txt` (keep those paths current when chapters are renumbered).
- **`tip help` is generated from `tools/tasks.py`, not hand-written.** A
  task is a function under `@task("one-line doc")`, placed after the
  `section("Name")` call it belongs under; the decorator's doc is the
  listing row, the docstring is the long-form help the picker's `?`
  shows, and the body is the recipe shown under it. Bare `tip`
  and `tip help` both list every section; `tip help style` lists
  one section (the slug is the heading's first word, lowercased, and
  two sections may not share one).
  A task whose Python name would shadow a step helper takes `name=`
  (the `run` task is `def run_all(...)` with `name="run"`, since
  `run()` is the helper that runs a command).
  A new task goes in the section for its job, with an `also()` in Everyday if it becomes a daily command.
  `secondary=True` folds a task out of the listing when a sibling's doc names it.
  `tools/tip_help.py`'s docstring covers the listing and the time column,
  `tools/help_picker.py`'s the picker.
  `tools/README.md`'s own "Commands" section deliberately does not re-list every
  target either (it did once, and went stale); it shows only the everyday few and
  points to `tip help` for the rest. Don't re-expand it into a full manual copy.
- **`reflow_prose.py` already exists.**
  Before writing a script to reflow prose across the book, check
  `tools/reflow_prose.py` first: it already masks inline code/links/footnotes,
  protects an abbreviation list, and greedily packs clauses to fit a width
  instead of breaking every comma (a naive "break at every comma" script
  fragments simple lists like "insights, idioms, and patterns" into three
  lines, a regression, not a fix). Its `SINGLE_LETTER_WORDS` set holds single
  uppercase letters that are real words (`"C"`, the language) rather than
  initials like "B."; extend it if a new one causes a missed sentence split.

### The tip runner

- `tip` replaces make (branch `explore-python-runner`, 2026-09-26):
  `tools/tasks.py` holds every task and documents every gate
  (`tip help`), and `tools/tip.py` runs them. `uv tool install
  --editable .` puts `tip` on PATH, in its own environment outside
  `.venv`; inside the repo `uv run tip ...` works with no install.
  Variables keep make's form (`tip verify-ch CH=28`), each step runs
  through `uv run` from the repo root and is echoed first, a task's
  `deps` run once per invocation, and the first failing step stops the
  run. Every goal named on the command line ends with
  `tip <goal>: 12.3s`. Steps run with `TIP_NESTED=1`, and a nested
  `tip` prints no timing line, so `verify.py` and `sweep_checks.py`
  (which run each step as `python -m tools.tip NAME`) time their own
  steps.
