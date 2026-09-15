---
name: edit-start
description: Open an editing pass on one chapter. Tags the current commit `edit-start-NN` so `/edit-done` can capture everything Bruce changes from here, reports the chapter's files and its baseline gate state, and flags an earlier pass still open. Use when Bruce says he is starting to edit, work on, or revise a chapter. The argument names the chapter by number or name and is required.
---

# Opening an editing pass on a chapter

Bruce is about to edit a chapter by hand.
His edits are the best evidence of how he wants the book written,
and `/bruce-edit-capture` mines them,
but only if the starting point is recorded before the first edit.
This skill records it as a local git tag,
`edit-start-NN`, on the current commit.
`/edit-done` reads that tag later.
A session that starts while the tag exists is told about it
by the `SessionStart` hook in `.claude/settings.json`,
so a request like "fix that sentence about closures"
goes to the chapter in progress without Bruce naming it.

The skill writes nothing under `Chapters/`, `Solutions/`, or `tools/`.
It creates one tag and runs read-only checks.

## Step 1: resolve the chapter

The argument is a chapter number (`28`), a stem prefix
(`28_Patterns`), or a name (`Function Objects`).
Resolve it to the two source files:

```
ls Chapters/NN_*.md Solutions/NN_*.md
```

A chapter without a Solutions file is fine; report it as such.
If the argument matches nothing, or more than one chapter, stop and say so.

## Step 2: check for a pass already open

```
git tag -l 'edit-start-*'
```

- `edit-start-NN` for this chapter already exists: leave it where it is
  and report when it was placed (`git tag -n1 edit-start-NN`, and
  `git log -1 --format=%cd edit-start-NN`). Moving it would drop
  the edits made since. Stop here; the rest of this skill has run once.
- A tag for a different chapter exists: report it, since Bruce may have
  forgotten to close that pass, but proceed. Two open passes are allowed.

## Step 3: note the working tree

```
git status --porcelain -- Chapters/NN_*.md Solutions/NN_*.md Examples/NN_* SolutionsCode/NN_*
```

Uncommitted changes to the chapter are not a problem:
the tag goes on the commit, and `/edit-done` diffs from the tag to the
working tree, so those changes are inside the pass.
Report them so Bruce knows they will be read as part of this pass.
Do not commit them and do not ask whether to.

## Step 4: place the tag

```
git tag -a edit-start-NN -m "Start of Bruce's editing pass on chapter NN (<Chapter Title>), <YYYY-MM-DD>"
```

Annotated, on `HEAD`, dated today.
The tag is local. Never push it; Bruce does every push himself,
and this tag is bookkeeping, not history.

## Step 5: record the baseline

Run the chapter's own checks so a red result after the pass is
attributable to the pass and not to something that was already wrong:

```
make check-ch CH=NN
make reflow-check CH=NN
uv run python -m tools.extract_examples --write
uv run python -m tools.validate_output Chapters/NN_*.md
```

Report only. A failure here is information for Bruce, not something
to fix now: fixing it would put my edits inside his editing pass, and
the capture would then have to sort mine from his. Say what failed and
offer to fix it after the pass closes, or now if he prefers.

## Step 6: report

One short block:

- the chapter's files;
- the tag and the commit it sits on;
- the baseline result (green, or what was red);
- uncommitted changes found in Step 3, if any;
- any other `edit-start-*` tag still open;
- how the pass closes: `/edit-done NN`.

Nothing else. No suggestions about the chapter's content;
that is the pass Bruce is about to do himself.
