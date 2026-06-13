# Book tooling

Scripts that keep the book honest. They implement tasks **P1-1** (extract every
code example from the Markdown, run it, report failures), **P1-2** (render the
Markdown into a static HTML site), and **P1-3** (the CI gate that ties them
together) in `PUBLISHING_PLAN.md`.

## The idea

The Markdown chapters in `Markdown/` are the source of truth for the book's
prose *and* its code. A fenced block becomes an extractable file when its first
non-blank line is a path comment:

````markdown
```python
# Decorator/nodecorators/CoffeeShop.py
class Espresso: pass
...
```
````

The path (`Decorator/nodecorators/CoffeeShop.py`) is taken relative to the
example tree. Blocks without such a first line are illustrative fragments and
are ignored. Data files (`.txt`, `.dat`) tagged the same way are extracted too,
so examples that read them can run.

`Examples/` is the curated copy committed to git. `ExtractedExamples/` is a
throwaway tree (git-ignored) regenerated from the Markdown for running.

## Commands

With `make`:

```
make check      # do the book's examples match the committed Examples/ tree?
make extract    # write ExtractedExamples/ from the Markdown
make run        # run every extracted .py, report failures
make examples   # extract then run (the full pass)
make site       # render Markdown/ into build/site/
make ci         # what CI runs: drift check, regression run, site build
```

Without `make` (e.g. Windows PowerShell), call the scripts directly:

```
python tools/extract_examples.py            # = make check
python tools/extract_examples.py --write    # = make extract
python tools/run_examples.py                # = make run
python tools/build_site.py                  # = make site
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

* Narrow the run: `python tools/run_examples.py StateMachine`
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

CI runs `--baseline`, so the pipeline is green today and goes red the moment a
change breaks something that currently works. When Phase 2 repairs an example,
the runner reports it as "now passes": trim it from the baseline (or rerun
`--write-baseline`) so future regressions of it are caught.

## build_site.py

Renders `Markdown/*.md` into a browsable site under `build/site/` (git-ignored).
Pandoc converts each chapter; the script adds the title page, an ordered
contents list, a sidebar, previous/next links, and syntax-highlighting CSS.

Book images are referenced in the Markdown as `_images/<name>` with no
extension. The builder resolves each to the real file in `resources/images`
(`decorator` to `decorator.gif`), copies the referenced ones into
`build/site/images/`, and warns about any reference with no matching file.

Requires `pandoc` on PATH. Run `python tools/build_site.py` (or `make site`);
use `-o DIR` to build elsewhere.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request under Python
3.14. Hard gates: the regression run (`run_examples.py --baseline`) and the
site build. Advisory for now (each has a known backlog): the drift check and
`ty`. `make ci` runs the same sequence locally.

## Current baseline

The first full run establishes the modernization backlog for Phase 2, captured
in `tools/examples_baseline.txt`: 55 examples pass, 67 fail or time out. The
failures are overwhelmingly Python 2 syntax (`print` statements, `has_key`),
Java leftovers (`0.75f` float literals, dangling `+` line continuations), and
Python 2 implicit relative imports (`from State import ...`). Each is a Phase 2
work item. Drift the checker found between the book and `Examples/`:
`Py4Prog/using_from.py` (tagged twice with different content),
`InitializationAndCleanup/cleanup.py`, and `InitializationAndCleanup/weakref.py`.
