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

## Step 3b: search the book for the same faults

Bruce approves fault lines on a page, not in the transcript
(`fault_review.html` beside this file; `tools/fault_review.py`'s
docstring has the mechanics). While the tag still exists:

1. Run `tip edit-patterns ARGS=--dry-run`. It lists every sentence
   Bruce rewrote in the pass (commits with a Co-Authored-By trailer are
   skipped) and records each before/after pair in
   `tools/data/edit_pairs.json`.
2. For each edit the capture step judged generalizable, propose a
   one-line fault: what the before-sentence got wrong, stated so it
   picks out that fault and not a shared word or shared punctuation
   ("Metadiscourse: a clause announces what the text itself is doing",
   not "ends in a colon"). Name what the edit changed, not a nearby
   property: chapter 30's "generated" line first said "in a passage
   that does not name the mechanism" when Bruce's own sentence named
   it. Propose a line for every card, including edits you judge local
   (an exercise renumbering, a fact correction): give those as
   `{"fault": "...", "local": true}` so the card says "I'd call this
   local" and Bruce decides. A card with no line cannot be approved,
   and on chapter 30's first page the four left blank read as broken;
   he wanted all four approved. Write the proposals to
   `build/fault_review/proposals.json` as a JSON object from pair key
   to fault line (or that object).
3. Run `uv run python -m tools.fault_review seed --since
   edit-start-NN --proposals build/fault_review/proposals.json`.
4. Copy `.claude/skills/edit-done/fault_review.html` to
   `build/fault_review/fault_review_NN.html` and publish the copy, with
   no `url`, `capabilities: {"db": {}}`, and icon `edit`. Each pass
   gets its own page and database this way; republishing a path a
   session already published would update that earlier page instead.
   Load each `build/fault_review/batch*.json` with one `ArtifactData`
   `batch`, give Bruce the link, and wait for him to say he is done.
5. Read the cards back with `ArtifactData` `list` on `cards`,
   `query.limit` 1000, `out_dir` `build/fault_review/read`, then run
   `uv run python -m tools.fault_review apply
   build/fault_review/read/cards`. It writes each approved line
   (edited or not) into `edit_pairs.json`, clears the ones marked
   Local edit, and lists the undecided.
6. Run `tip edit-patterns` (needs `TYPESAFE_API_KEY`; about five
   minutes). Report each searched pair's hit count and its strongest
   few hits from `build/edit_patterns.md`, and each `unclear` pair,
   whose fault line needs rewording before it can be searched. The
   hits are a worklist for Bruce; do not apply them. A long list is
   itself a review batch: offer a fix-triage page
   (`fix_triage.html` beside this file, `tools/fix_triage.py`, whose
   docstring has the steps). The session proposes a rewrite, a
   deletion, or "not this fault" for each hit (parallel agents, one per
   run of chapters, worked for 197 hits), Bruce decides on the page,
   and `fix_triage apply` edits the chapters; run `tip verify-ch` for
   each chapter it touched and commit per chapter.
   Tell the proposing agents what Bruce decided on the first page
   (2026-09-27, the metadiscourse fault): he cut 85 of the 132
   sentences the agents had marked "not this fault" and treated 175 of
   183 hits as real. So for metadiscourse, a chapter or section
   roadmap ("This chapter covers...", "The rest of this chapter..."),
   a sentence that only introduces the listing below it (his rule R7),
   and a "the next section..." pointer are the fault, and the usual
   fix is the cut: propose `{"delete": true}`, not `not_fault`, unless
   the sentence carries a fact nothing else states. Two cases still
   need a rewrite, not a cut: a sentence in a chapter's opening
   blockquote, whose epigraph gate needs two to four lines, and a
   sentence that is the only lead-in to a bulleted list or a table.
   Proposing agents are cautious by default; "when unsure, prefer
   not_fault" was the wrong instruction for this fault.

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
