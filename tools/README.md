# Book tooling

Scripts that keep the book's code examples honest. They implement task **P1-1**
in `PUBLISHING_PLAN.md`: extract every code example from the Markdown, run it,
and report what fails.

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
```

Without `make` (e.g. Windows PowerShell), call the scripts directly:

```
python tools/extract_examples.py            # = make check
python tools/extract_examples.py --write    # = make extract
python tools/run_examples.py                # = make run
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

## Current baseline

The first full run establishes the modernization backlog for Phase 2. As of the
initial run: 55 examples pass, ~69 fail. The failures are overwhelmingly Python
2 syntax (`print` statements, `has_key`), Java leftovers (`0.75f` float
literals, dangling `+` line continuations), and Python 2 implicit relative
imports (`from State import ...`). Each is a Phase 2 work item. Drift the
checker found between the book and `Examples/`: `Py4Prog/using_from.py` (tagged
twice with different content), `InitializationAndCleanup/cleanup.py`, and
`InitializationAndCleanup/weakref.py`.
