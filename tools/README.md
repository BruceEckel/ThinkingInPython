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

With `make` (targets run through `uv run`):

```
make check      # do the book's examples match the committed Examples/ tree?
make extract    # write ExtractedExamples/ from the Markdown
make run        # run every extracted .py, report failures
make examples   # extract then run (the full pass)
make site       # render Markdown/ into build/site/
make ty         # type-check the extracted examples (must be clean)
make ci         # what CI runs: drift, run, pytest, ty, ruff, site
```

Without `make` (e.g. Windows PowerShell), call the scripts through `uv run`:

```
uv run python tools/extract_examples.py            # = make check
uv run python tools/extract_examples.py --write    # = make extract
uv run python tools/run_examples.py                # = make run
uv run python tools/build_site.py                  # = make site
uv run ty check ExtractedExamples                  # = make ty
```

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

## build_site.py

Renders `Markdown/*.md` into a browsable site under `build/site/` (git-ignored).
Pandoc converts each chapter; the script adds the title page, an ordered
contents list, a sidebar, previous/next links, and syntax-highlighting CSS.

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

`.github/workflows/deploy.yml` builds the site and publishes it to GitHub Pages
at <https://bruceeckel.github.io/ThinkingInPython> on every push to `master`
(and on manual `workflow_dispatch`). It uses the GitHub Actions Pages flow:
`actions/upload-pages-artifact` uploads `build/site/`, then
`actions/deploy-pages` deploys it. The site is built fresh in CI, so the
generated HTML is never committed (`build/` stays git-ignored). All in-page
links are relative, so the project subpath (`/ThinkingInPython/`) just works.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request. It installs uv
(`astral-sh/setup-uv`, Python 3.14, cached), runs `uv sync --locked`, then
drives the harness with `uv run`. Hard gates: the drift check
(`extract_examples.py`), the example run (`run_examples.py`, all must pass), the
book's pytest examples (`pytest ExtractedExamples`), the type check (`ty check
ExtractedExamples`, zero diagnostics), the lint (`ruff check ExtractedExamples`,
zero findings), and the site build. Deliberate lint exceptions live in
`[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`. `make ci` runs the same
sequence locally.

## Current baseline

The first full run establishes the modernization backlog for Phase 2, captured
in `tools/examples_baseline.txt`: 55 examples pass, 67 fail or time out. The
failures are overwhelmingly Python 2 syntax (`print` statements, `has_key`),
Java leftovers (`0.75f` float literals, dangling `+` line continuations), and
Python 2 implicit relative imports (`from State import ...`). Each is a Phase 2
work item. Drift the checker found between the book and `Examples/`:
`Py4Prog/using_from.py` (tagged twice with different content),
`InitializationAndCleanup/cleanup.py`, and `InitializationAndCleanup/weakref.py`.
