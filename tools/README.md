# Book tooling

Scripts that keep the book honest: extract every code example from the
Markdown and run it, render the Markdown into a static HTML site, and gate
both in CI.

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

`Examples/` is the curated copy committed to git. `build/examples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

## Commands

Tooling is managed by [uv](https://docs.astral.sh/uv/). One-time setup:

```
uv sync          # create .venv with the dev tools (ty) pinned by uv.lock
```

Run `make check-tools` afterward to confirm everything resolved (`uv`, `ty`,
`ruff`, `pytest`); `make check-tools-full` also checks `pandoc` and `vale`,
needed only for `make site`/`make local` and `make prose`. See
[check_tools.py](#check_tools.py) below.

To run GNU Make natively on Windows, install it with winget, which ships with
modern Windows and is the quickest setup. In Command Prompt or PowerShell, run:

```
winget install ezwinports.make
```

Restart the terminal to refresh the PATH, then run `make --version` to confirm.

Run targets with `make` (they go through `uv run`); `make help` prints the
complete, categorized list, generated from the Makefile itself so it never
drifts out of date (see [make_help.py](#make_help.py) below). The everyday ones:

```
make verify     # sync Examples/, then every gate except the site build
make sync-ci    # like verify, plus the site build (the full gate)
make ci         # the full local gate: check, ty, ruff, run, pytest, site
```

`make verify` is the everyday command after editing the book: it pushes your
Markdown changes out to `Examples/` (so the drift check passes), then runs every
gate except the site build. `make sync-ci` does the same and also builds the
site. `make ci` runs the gate (with site) without syncing first, so it still
fails on drift, the way GitHub Actions does.

## make_help.py

Prints the categorized `make help` listing. In the Makefile, a target line
ending with a `## text` comment becomes one entry; a `##@ Name` comment
line starts a new category heading above the entries that follow it. It
replaces a `grep | awk` one-liner so `make help` has no dependency on a
POSIX toolchain being on PATH: every other target already requires Python
(via `uv run`), and this keeps `help` consistent with that.

```
make help   # categorized list of every documented target
```

## check_tools.py

Checks that the tools this project needs are actually installed and prints
a version line or a MISSING install hint for each. The basic tier is what a
reader needs for the everyday commands: `uv` itself, plus the uv-managed
dev tools (`ty`, `ruff`, `pytest`) that `uv run` resolves from `uv.lock`.
`make` and `git` are checked too but marked "assumed" (you already needed
both to get this far), so their absence doesn't fail the exit code. `--full`
adds the tools a book maintainer needs for the rest of `make help`: `pandoc`
(`make site`, `make local`) and the standalone `vale` binary (`make prose`).

```
make check-tools        # uv, ty, ruff, pytest (make/git checked, assumed)
make check-tools-full   # the above, plus pandoc and vale
```

## upgrade_tools.py

Updates the project's tools to their latest versions. `uv self update`
updates uv itself (a no-op with its own message if uv was installed via
pipx, Homebrew, or winget rather than its standalone installer). `uv lock
--upgrade` then `uv sync` upgrade every uv-managed dev tool (`ty`, `ruff`,
`pytest`, `codespell`, ...) to the latest version `pyproject.toml` allows,
rewriting `uv.lock`; review `git diff uv.lock` before committing. `pandoc`
and `vale` are standalone binaries uv does not manage, so this is
best-effort: it tries winget (Windows) or Homebrew, whichever is on PATH,
and falls back to printing the install link if neither works. `make` and
`git` are left alone, same as `check_tools.py`. For the pinned Python
version itself, use `upgrade_python.py` below instead.

```
make upgrade-tools   # update uv, ty/ruff/pytest/..., and (best-effort) pandoc/vale
```

## upgrade_python.py

Upgrades the pinned development Python and resyncs the environment. With no
argument, `make upgrade-python` fetches the latest patch of the minor pinned
in `.python-version` (e.g. the newest 3.14.x). With `TO=3.15`, it first
repins: rewrites `.python-version` and the `requires-python` floor in
`pyproject.toml`, then syncs. Either way it finishes by running `make
verify`. It runs through `uv run --no-project` so the orchestrating
interpreter is never the venv that `uv sync` is about to rebuild.

```
make upgrade-python           # latest patch of the pinned minor, then verify
make upgrade-python TO=3.15   # repin to a new minor, then verify
```

## extract_examples.py

Default mode is **check**: nothing is written. It reports

* examples present in the book but missing from `Examples/`,
* examples whose book text differs from `Examples/`, and
* conflicting duplicates (the same path tagged twice with different content).

It exits non-zero on any of these, so CI catches prose/code drift. Pass
`--write` to materialize `build/examples/` (use `-o DIR` for another target).

## run_examples.py

Runs every `.py` under `build/examples/`, each in its own directory so the
examples' relative data paths resolve. Reports passed / skipped / timed-out /
failed and exits non-zero if anything fails or times out.

`test_*.py` and `conftest.py` are skipped here: they are pytest files, run by
`make test` (`uv run pytest build/examples`), not as standalone scripts. See
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

Only skip examples that cannot run even when correct, such as ones needing a
GUI or user input. A newly broken example should stay visible as a failure,
not be skipped.

### Regression baseline

Most examples failed during the Phase 2 modernization, so a runner that was
red on every one of them would have gated nothing.
`tools/examples_baseline.txt` records the set of then-failing examples. Two
modes use it:

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
`tools/codespell-ignore.txt`. Scope it with `CH=`, for example
`make spell CH=02`.

**Full-dictionary spelling: spellcheck.py (`make spell`).** Where codespell
knows only a curated list, `tools/spellcheck.py` (using the uv-managed
`pyspellchecker`) checks every prose word against a real English dictionary, so
a novel typo is caught. It checks prose only: code blocks, inline code,
footnotes, and link URLs are stripped via `md_prose`, so identifiers do not
flood it. Accepted terms (technical words, names, coined words) live in
`tools/wordlist.txt`, one lowercase word per line. When it flags a real term,
add it there; when it flags a typo, fix the prose. Use
`uv run python tools/spellcheck.py --summary` to see the unique unknowns by
count, which makes seeding the word list quick. `make spell-add` automates the
"add it there" step: it accepts every unknown word into the wordlist, sorted
and deduplicated. It cannot tell a real term from a typo, so always review
`git diff tools/wordlist.txt` before committing.

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

## capitalize_comments.py

Enforces that a prose comment in a ```python listing starts with a capital. The
prose-vs-code judgment is a heuristic, so it skips code-identifier first words,
single letters, and keywords, and continuation lines of a multiline comment. Its
unavoidable false positives (program output like `# total = 7`, an identifier
reference like `# n is the counter`, schematic notation like `# name -> subclass`)
are listed by comment text in `tools/comment_caps_allow.txt` and skipped. It is
part of the `make ci` gate.

```
make comment-caps       # check (part of `make ci`)
make fix-comment-caps   # capitalize the flagged comments
```

When the checker is wrong, add the comment's text to the allowlist; when it is
right, capitalize the comment (or run `make fix-comment-caps`).

## check_anchors.py

Verifies that every heading-anchor link resolves to a real heading, so a typo
does not ship as a dead in-page link. Markdown can link to a heading with
`[text](#id)` (same file) or `[text](07_Static_Typing.md#id)` (another chapter).
The tool reproduces pandoc's anchor rule (lowercase, spaces to hyphens,
punctuation and backticks removed, leading non-letters dropped), honors an
explicit `{#id}` on a heading, collects every id, and checks each `#anchor`
link against it. A bad cross-file link also reports a missing target file. It is
part of the `make ci` gate; there is nothing to auto-fix.

```
make anchors    # check (part of `make ci`)
```

To make an anchor stable against rewording, give the target heading an explicit
id: `## Heading {#stable-id}`, then link `(chapter.md#stable-id)`.

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
target chapter's `.md` file, for example `[Factory](18_Factory.md)`.
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
  (`pytest build/examples`), the type check (`ty check build/examples`,
  zero diagnostics), and the lint (`ruff check build/examples`, zero
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
