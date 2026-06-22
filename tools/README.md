# Book tooling

Scripts that keep the book honest. They implement tasks **P1-1** (extract every
code example from the Markdown, run it, report failures), **P1-2** (render the
Markdown into a static HTML site), and **P1-3** (the CI gate that ties them
together) in `PUBLISHING_PLAN.md`.

## The idea

The Markdown chapters in `Markdown/` are the source of truth for the book's
prose *and* its code. A fenced block becomes an extractable file when its first
non-blank line is a path comment naming the file, relative to its chapter:

````markdown
```python
# trace.py
def trace(func): ...
```
````

The file is written under a directory named for the chapter it appears in (the
Markdown file's stem). So `# trace.py` in `08_Decorators.md` is extracted to
`08_Decorators/trace.py`. The slug carries no chapter prefix; the extractor adds
it. A slug may include a sub-path (`# mouse/mouse_action.py`) to group related
files within one chapter. Renaming or renumbering a chapter therefore moves its
example folder to match. Blocks without such a first line are illustrative
fragments and are ignored. Data files (`.txt`, `.dat`) tagged the same way are
extracted too, so examples that read them can run.

`Examples/` is the curated copy committed to git. `ExtractedExamples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

## Commands

Tooling is managed by [uv](https://docs.astral.sh/uv/). One-time setup:

```
uv sync          # create .venv with the dev tools (ty) pinned by uv.lock
```

To run GNU Make natively on Windows, install it with winget, which ships with
modern Windows and is the quickest setup. In Command Prompt or PowerShell, run:

```
winget install ezwinports.make
```

Restart the terminal to refresh the PATH, then run `make --version` to confirm.

With `make` (targets run through `uv run`); `make help` lists them all, most-used
first:

```
make verify     # sync Examples/, then every gate except the site build
make sync-ci    # like verify, plus the site build (the full gate)
make ci         # the full local gate: check, run, pytest, ty, ruff, site
make gate       # the gate without sync or site (check, run, pytest, ty, ruff)
make sync       # update the committed Examples/ tree from the Markdown
make check      # do the book's examples match the committed Examples/ tree?
make site       # render Markdown/ into build/site/
make examples   # extract then run (the full verification pass)
make test       # run the book's pytest examples
make ty         # type-check the extracted examples (must be clean)
make lint       # PEP 8 lint the extracted examples with ruff (must be clean)
make spell      # spell-check the prose and comments with codespell
make prose      # house-style lint the prose with Vale (needs the vale binary)
```

`make verify` is the everyday command after editing the book: it pushes your
Markdown changes out to `Examples/` (so the drift check passes), then runs every
gate except the site build. `make sync-ci` does the same and also builds the
site. `make ci` runs the gate (with site) without syncing first, so it still
fails on drift, the way GitHub Actions does.

## extract_examples.py

Default mode is **check**: nothing is written. It reports

* examples present in the book but missing from `Examples/`,
* examples whose book text differs from `Examples/`, and
* conflicting duplicates (the same path tagged twice with different content).

It exits non-zero on any of these, so CI catches prose/code drift. Pass
`--write` to materialize `ExtractedExamples/` (use `-o DIR` for another target).

## run_examples.py

Runs every `.py` under `ExtractedExamples/`, each in its own directory so the
examples' relative data paths resolve. Reports passed / skipped / timed-out /
failed and exits non-zero if anything fails or times out.

`test_*.py` and `conftest.py` are skipped here: they are pytest files, run by
`make test` (`uv run pytest ExtractedExamples`), not as standalone scripts. See
the Testing chapter.

* Narrow the run: `python tools/run_examples.py 16_State_Machines`
* Adjust the kill timeout: `--timeout 20` (default 15s)
* Parallelism: runs on all cores by default (`-j auto`); each example is its
  own subprocess, so this is safe. Use `-j 1` for serial, or `-j N` for a fixed
  count. (pytest runs serially by default; enable xdist with
  `make test PYTEST_N="-n auto"`.)

### Skipping examples that can't run unattended

Some examples open GUI windows, read stdin, or depend on dead frameworks. Skip
them two ways:

* an inline `# extract: no-run` line in the file, or
* a glob pattern in `tools/norun.txt`.

Only skip examples that cannot run even when correct. Examples that fail today
because of Python 2 syntax are **Phase 2 fixes** and should stay visible as
failures, not be skipped.

### Regression baseline

Most examples fail today (Phase 2 backlog), so a runner that is red on every
one of them gates nothing. `tools/examples_baseline.txt` records the set of
currently-failing examples. Two modes use it:

```
python tools/run_examples.py --baseline        # fail only on NEW breakage
python tools/run_examples.py --write-baseline   # regenerate the baseline
```

The book is now fully modernized, so the baseline is **empty** and CI runs a
strict pass: every example must run. The `--baseline` mechanism remains for
future bulk work (e.g. importing a batch of new, not-yet-fixed examples): record
them with `--write-baseline`, gate only regressions with `--baseline`, then trim
entries as you repair them.

## reflow_prose.py

Rewrites prose paragraphs in `Markdown/*.md` so each sentence sits on its own
line ("semantic line breaks"). This keeps edits and their diffs sentence-grained
instead of reflowing a whole hard-wrapped paragraph on every word change. Code
fences, indented code, tables, headings, list items, blockquotes, HTML blocks,
horizontal rules, and YAML front matter are left untouched; inline code spans
and footnotes are masked so their internal punctuation never triggers a split.

A sentence longer than `--width` (default 80) is broken further at top-level
clause punctuation (`,`, `;`, `:`), so no line is wide enough to wrap in an
editor. A greedy fill inserts only the breaks needed, and a minimum-length guard
keeps a short lead-in clause from being stranded on its own line; if the only
break points are too early to help, the sentence stays on one line. Punctuation
inside parentheses, brackets, inline code, or footnotes is never a break point.

A single newline inside a paragraph is a soft break (a space) under the site's
pandoc reader (`markdown+smart`), so reflowed prose renders identically. The
tool rewrites a file only when its whitespace-normalized text is unchanged, so
it can never add, drop, or alter a word; a file that fails that check is left
alone and reported.

```
make reflow-check        # report which chapters would change, no write
make reflow              # rewrite the whole book
make reflow CH=02        # rewrite one chapter (by number, name part, or path)
make reflow-check CH=02  # preview one chapter, no write
uv run python tools/reflow_prose.py --diff Tour   # diff a chapter by name part
```

A positional argument (or `CH=`) may be a file path or a chapter selector
matched against `Markdown/`: a number or stem prefix (`02`, `02_A_Python`) or a
substring (`Tour`). With no argument the whole book is processed.

## Spelling and prose style

Several layers, all optional and not part of the default CI gate.

**Spelling: codespell (`make spell`).** A uv-managed dev tool, so it runs through
`uv run`. It prints one line per suspected misspelling and exits non-zero if it
finds any, so **no output means clean** (a silent return to the prompt is a
pass). It matches a curated misspelling dictionary rather than a full one, so it
stays low-noise even over code comments and examples, but it will not catch an
unusual typo that is not on its list ("fixted" for "fixed"); for that there is
the full-dictionary check below. Configuration lives in `[tool.codespell]` in
`pyproject.toml`; words it flags wrongly (design-pattern terms like `adaptee`,
foreign-language quotes, deliberate code strings) are listed in
`tools/codespell-ignore.txt`. Scope it with `DOCS=`, for example
`make spell DOCS=Markdown/02_Tour.md`.

**Full-dictionary spelling: spellcheck.py (`make spell`).** Where codespell
knows only a curated list, `tools/spellcheck.py` (using the uv-managed
`pyspellchecker`) checks every prose word against a real English dictionary, so
a novel typo is caught. It checks prose only: code blocks, inline code,
footnotes, and link URLs are stripped via `md_prose`, so identifiers do not
flood it. Accepted terms (technical words, names, coined words) live in
`tools/wordlist.txt`, one lowercase word per line. When it flags a real term,
add it there; when it flags a typo, fix the prose. Use
`uv run python tools/spellcheck.py --summary` to see the unique unknowns by
count, which makes seeding the word list quick.

**Mechanical prose: prose_lint (`make spell`).** `tools/prose_lint.py` runs
alongside codespell and catches small mechanical slips a spell checker ignores:
more than one space between words, a space before `.`/`,`/`;`/`!`/`?`, more than
one blank line in a row, a period or comma left outside a closing quote, and
trailing whitespace (a two-space hard break is allowed). It shares the
`md_prose.py` classifier with `reflow_prose.py`, so fenced and indented code,
tables, blockquotes, and HTML are skipped, and inline code spans and footnotes
are ignored inside a prose line; headings and list-item text are checked but
their markers are not. It is report-only and exits non-zero on any finding. Run
it directly with `uv run python tools/prose_lint.py Markdown` (or a single file).

**House style: Vale (`make prose`).** Vale is a standalone binary, not a Python
package, so install it once (`winget install errata-ai.Vale`,
`brew install vale`, or see <https://vale.sh/docs/install>). Vale parses Markdown
and checks only text, never code spans or fenced code, so the rules never fire on
identifiers or examples. Spelling is left to codespell; Vale enforces house style
only. The rules live in `styles/House/` and are wired up by `.vale.ini`:

* `EmDash` (error): no `—`, `–`, or `--` used as a dash.
* `Filler` (warning): throat-clearing phrases ("this is the whole idea", and so on).

To add the community packages for passive-voice and usage checks, list them in
`.vale.ini` (`Packages = write-good, proselint`) and run `vale sync` once.

## check_line_endings.py

`.gitattributes` (`* text=auto eol=lf`) already keeps committed blobs LF on
every platform, so the repo and the Linux CI build are always LF. This tool
guards the **working tree**: on Windows an editor can write CRLF into a source
file, which is harmless to git but produces noisy warnings and inconsistent
local files. `make eol` reads `git ls-files --eol` (so it honors the binary
markers in `.gitattributes`) and fails if any tracked text file has CRLF or
mixed endings. It is part of the `make ci` gate. There is no auto-convert in the
build; run the fixer explicitly when the check flags something:

```
make eol       # check, exit 1 on CRLF (part of `make ci`)
make fix-eol   # convert any offenders to LF
```

## listing_format.py

The book favors dense listings: at most one blank line in a row, and no blank
line between import groups. Ruff's isort config (`no-lines-before`,
`lines-after-imports = 1`) enforces the import layout, but only on the extracted
`.py` files: it cannot rewrite the `Markdown/` source, and it does not check
blank-line counts between defs at all. This tool closes both gaps by checking
the Markdown directly. It is string-aware, so blank lines inside triple-quoted
strings are never touched, and it only looks at ```python blocks. It is part of
the `make ci` gate; like line endings, there is no auto-fix in the build:

```
make listings       # check, exit 1 on extra blank lines (part of `make ci`)
make fix-listings   # remove the offending blank lines
```

Do not run `ruff format` on the examples: it would re-expand to two blank lines
between top-level defs and undo the density. The gate runs `ruff check` (the
linter) only, which is happy with one blank line.

## banned_phrases.py

Fails the build if any phrase listed in `tools/banned_phrases.txt` appears
anywhere in `Markdown/`, prose and code alike (unlike Vale, which only sees
prose). Matching is a literal, case-sensitive substring; each occurrence is
reported as `path:line:col`. Use it to retire a construct book-wide, for example
`from __future__ import annotations`, which is unnecessary on Python 3.14. Edit
the phrases file to add or remove entries (blank lines and `#` comments are
ignored). It is part of the `make ci` gate.

```
make banned    # fail if any banned phrase is in the book (part of `make ci`)
```

## comment_periods.py

Enforces the comment-period policy in ```python listings: a one-line comment
ends without a period; only a multiline comment (two or more consecutive
full-line `#` comments) reads as sentences and keeps its periods. So it flags a
trailing period on an inline comment or a lone full-line comment, but leaves
multiline blocks alone. It is string-aware (a `#` inside a string is not a
comment) and skips an ellipsis (`...`). It is part of the `make ci` gate.

```
make comment-periods       # check (part of `make ci`)
make fix-comment-periods   # strip the trailing periods
```

## build_site.py

Renders `Markdown/*.md` into a browsable site under `build/site/` (git-ignored).
Pandoc converts each chapter; the script adds the title page, an ordered
contents list, a sidebar, previous/next links, and syntax-highlighting CSS.

The book's **Part dividers are generated here, not written in the Markdown.**
The `PARTS` map names Part I (Foundations, before chapter `02`), Part II
(Techniques, before `09`), and Part III (Patterns, before `17`); the builder
emits each heading in the table of contents before its starting chapter, with
the Introduction standing alone above Part I. So a chapter file with no "Part"
heading is correct: to move or rename a Part, edit `PARTS`, not the chapters.

Book images are referenced in the Markdown as `_images/<name>` with no
extension. The builder resolves each to the real file in `resources/images`
(`decorator` to `decorator.gif`), copies the referenced ones into
`build/site/images/`, and warns about any reference with no matching file.

Cross-references between chapters use standard relative Markdown links to the
target chapter's `.md` file, for example `[the Factory chapter](18_Factory.md)`.
These render correctly on GitHub; the builder rewrites intra-book `.md` links to
`.html` so they also resolve in the site. External links (which carry a scheme)
are left alone.

Requires `pandoc` on PATH. Run `python tools/build_site.py` (or `make site`);
use `-o DIR` to build elsewhere. `make serve` builds nothing and serves the
existing `build/site/` at <http://localhost:8000>; `make local` builds, serves,
and opens a browser at the site.

## serve.py

Serves `build/site/` over HTTP for local preview. `make serve` runs it as-is;
`make local` builds the site first, then runs it with `--open` to launch a
browser. Use `--port N` for another port. It does not build anything, so run a
site build first if `build/site/` is missing.

### Publishing to GitHub Pages

The `deploy` job in `.github/workflows/ci.yml` publishes the site to GitHub
Pages at <https://bruceeckel.github.io/ThinkingInPython> on every push to
`master`. It uses the GitHub Actions Pages flow: `actions/upload-pages-artifact`
uploads `build/site/`, then `actions/deploy-pages` deploys it. The site is built
fresh in CI, so the generated HTML is never committed (`build/` stays
git-ignored). All in-page links are relative, so the project subpath
(`/ThinkingInPython/`) just works. See "Continuous integration" below for how
the build and publish steps relate to the opt-in test gates.

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `master`, every pull request,
and manual `workflow_dispatch`. The full example/test suite already runs on your
machine before you push (and Actions can be slow), so **the default CI path only
builds and publishes the site**. The workflow has these jobs:

* **`site` (always runs):** installs uv (`astral-sh/setup-uv`, Python 3.14,
  cached) and pandoc, runs `uv sync --locked`, and builds the static site. On a
  push to `master` it hands the site to the `deploy` job, which publishes it to
  GitHub Pages. Pull requests build the site but do not deploy.
* **`gates` (opt-in only):** the full suite, the same one `make ci` runs
  locally: the drift check (`extract_examples.py`), the example run
  (`run_examples.py`, all must pass), the pytest examples
  (`pytest ExtractedExamples`), the type check (`ty check ExtractedExamples`,
  zero diagnostics), and the lint (`ruff check ExtractedExamples`, zero
  findings). Deliberate lint exceptions live in
  `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`.
* **`prose` (opt-in only):** the same checks as `make spell` and `make prose`.
  codespell spell-checks `Markdown/` (config in `[tool.codespell]`, ignore list
  in `tools/codespell-ignore.txt`) and fails on a spelling error. It then
  installs the Vale binary and runs the house-style rules in `styles/House/`;
  Vale fails the job on an em-dash (error level) and prints the filler
  findings as warnings. Shares the gates trigger.

`deploy` depends only on `site`, not on `gates` or `prose`, so publishing is
never blocked by the opt-in checks. The trade-off is that a push can publish even if an example
would fail a gate, which is why you run `make ci` locally first.

### Requesting the full gates in CI

The `gates` job runs only when you ask for it, in either of two ways:

* **Manually:** on the repo's **Actions** tab, select **CI**, click **Run
  workflow**, and leave the `run_gates` input at its default of `true`. From the
  command line that is:

  ```
  gh workflow run ci.yml -f run_gates=true
  ```

* **From a push:** include the marker `[full-ci]` anywhere in the commit message
  of the push, for example:

  ```
  git commit -m "Rework the Visitor example [full-ci]"
  ```

Either way, treat CI as a second opinion: run `make ci` locally first.

### Suggested workflow

Day to day:

1. Make your changes by editing `Markdown/` (the source of truth for prose and
   code alike).
2. Run `make sync-ci`: it pushes any code-block edits out to `Examples/`, then
   runs the full gate (drift, run, pytest, ty, ruff, site). Use plain `make ci`
   when you want to confirm there is no drift rather than paper over it.
3. When it is green, commit and push, including any updated `Examples/` files.
   The default CI path just rebuilds and publishes the site; it does not re-run
   the gates, so the push is fast.
4. Only when you want CI to re-check the suite itself (an environment-specific
   change, say, or a release) request the gates: add `[full-ci]` to the push
   commit message, or trigger the workflow manually as shown above.

## Current baseline

The first full run establishes the modernization backlog for Phase 2, captured
in `tools/examples_baseline.txt`: 55 examples pass, 67 fail or time out. The
failures are overwhelmingly Python 2 syntax (`print` statements, `has_key`),
Java leftovers (`0.75f` float literals, dangling `+` line continuations), and
Python 2 implicit relative imports (`from State import ...`). Each is a Phase 2
work item. Drift the checker found between the book and `Examples/`:
`Py4Prog/using_from.py` (tagged twice with different content),
`InitializationAndCleanup/cleanup.py`, and `InitializationAndCleanup/weakref.py`.
