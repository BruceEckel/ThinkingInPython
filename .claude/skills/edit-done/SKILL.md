---
name: edit-done
description: Close an editing pass opened by `/edit-start`. Diffs the chapter from its `edit-start-NN` tag to the working tree, runs `/bruce-edit-capture` over that diff, runs the verify loop and commits what it changes, then deletes the tag. Use when Bruce says he is done, finished, or through editing a chapter. The argument names the chapter by number or name; with no argument, the single open tag is used.
---

# Closing an editing pass on a chapter

`/edit-start` placed a tag `edit-start-NN` where Bruce began editing.
Everything from that tag to the working tree is his pass:
the commits he made along the way and whatever is still uncommitted.
This skill turns that pass into editing practice, checks that the
chapter still builds, and removes the tag.

## Step 1: find the pass

```
git tag -l 'edit-start-*'
```

- An argument names the chapter: use `edit-start-NN`; if it does not
  exist, stop and say the pass was never opened, and offer
  `/bruce-edit-capture NN` on his recent commits instead.
- No argument and one tag: use it, and say which chapter it is.
- No argument and several tags: ask which chapter, listing them.
- No tag at all: say so and stop.

Resolve the chapter files as `/edit-start` does:
`Chapters/NN_*.md` and, if present, `Solutions/NN_*.md`.

## Step 2: establish the diff

One diff covers the whole pass, committed and not:

```
git diff --word-diff=porcelain --ignore-all-space edit-start-NN -- Chapters/NN_*.md Solutions/NN_*.md
```

For provenance, list the commits inside the range:

```
git log --format='%h%x09%an%x09%s%x09%(trailers:key=Co-Authored-By,valueonly)' edit-start-NN..HEAD -- Chapters/NN_*.md Solutions/NN_*.md
```

A commit without a `Co-Authored-By: Claude` trailer is Bruce's own.
Commits I made inside the range (a verify commit, a marker refresh)
are not his edits; note them so the capture can set them aside.

If the diff is empty, say so, delete the tag (Step 5), and stop.

## Step 3: capture

Invoke the `bruce-edit-capture` skill with the range
`edit-start-NN..HEAD` and tell it that the working tree is part of the
pass, so it uses the diff from Step 2 rather than `HEAD` alone.
That skill owns the rest of this step: it classifies the edits,
proposes at most eight entries, and writes `bruce_edit_db.md` only after
Bruce approves. Do not shortcut its report.

## Step 4: verify and commit

Bruce's edits can leave a stale `#:` marker, a paragraph that needs
reflow, or a listing that no longer checks. Run the chapter-scoped
loop, which is the same fixers and gates as `tip verify` narrowed to
this chapter and its Solutions file, in a few seconds:

```
tip verify-ch CH=NN
```

Use the whole-book loop instead, `tip verify`, when the pass reached
outside the chapter. Two signs, both read from the diff in Step 2 with
its path filter removed (`git diff --stat edit-start-NN`): a changed
file under `Chapters/` or `Solutions/` that is not this chapter's, or
a change inside this chapter that other chapters depend on, such as a
renamed listing, a heading another chapter links to, or a `utils/`
helper. `verify-ch` says so itself when it fails, and it never writes
the gate stamp.

Then read `git diff --stat`. If the loop changed files (a reflow, a
marker refresh, a synced `Examples/` copy), commit them together with
any of Bruce's uncommitted edits to the same files, in one commit,
with the attribution trailer. His uncommitted edits are not split out
or flagged; project memory `bruces-working-tree-edits-commit-together`
records that decision. Never push.

A failure `verify` cannot self-heal (a listing that no longer runs, a
marker the prose contradicts) is reported with its output, and the fix
is proposed, not applied, unless Bruce asks. His edits are the
authority on what the chapter should say.

## Step 5: delete the tag

Only after the capture round is complete (the store written, or Bruce
has said there is nothing to keep) and the verify result is reported:

```
git tag -d edit-start-NN
```

If Bruce wants to keep editing after all, leave the tag and say so;
the next `/edit-done` will start from the same place.

## Step 6: report

- the pass: chapter, number of commits, whether the tree was dirty;
- the capture's counts and what was written to `bruce_edit_db.md`;
- the verify result and the commit made, if any;
- that the tag is gone, or why it stayed.
