---
name: chapter-editor
description: Run a round of the chapter editor page, where Bruce reads a whole chapter and marks text to rewrite, delete, or edit in place. Use when Bruce says "apply" (or "apply the round", "I sent it") with a chapter editor open, or asks to open a chapter in the editor. The argument names the chapter by number; with none, use the chapter in tools/data/chapter_editor.json whose page was sent.
---

# Chapter editor

The page (`chapter_editor.html` beside this file) shows a whole chapter, one block per paragraph, heading, list, or listing.
Bruce selects text and presses R (Rewrite, with an optional note), D (Delete), or E (edit that block's Markdown himself).
"Send round" sets the page's `meta/chapter` document to `status: "submitted"`, and he types `apply` in the terminal.
`tools/chapter_editor.py` moves the chapter between the Markdown and the page's database; its docstring has the data model.
The Markdown in `Chapters/` stays the source of truth.

`tools/data/chapter_editor.json` maps each chapter number to its page's artifact URL.
Every round below uses that URL.

## Opening a chapter

1. `tip editor-load CH=NN` (first load: every block).
2. Publish `build/chapter_editor/NN/chapter_editor_NN.html` with `capabilities: {"db": {}}`, `icon: "edit"`,
   and add the URL to `tools/data/chapter_editor.json`.
   A chapter that already has a page keeps its URL; republish with `url` only when the page template changed.
3. Write each `build/chapter_editor/NN/batch*.json` with one `ArtifactData` `batch` call, passing its entries as `writes`.
   The meta document comes last, so the page opens only once every block is in place.
4. Suggest `/edit-start NN` if no pass is open, so `/edit-done` captures the rounds.

## Applying a round (Bruce says "apply")

1. Set the page's status to applying: `ArtifactData` `update` on `meta/chapter` with `{"status": "applying"}`,
   pinned with `if_version` from step 2's read (so do step 2's reads first).
   The page then shows that the round is in progress.
2. Read the round, deleting the old `read/` first. `list` `meta` with `out_dir` `build/chapter_editor/NN/read`.
   Then `query` `blocks` twice, with `where` `marks != []` and then `edit != null` (`query.limit` 1000):
   `apply` needs only the marked and edited blocks, and a query result prints each one inline with its version.
   Save each of those blocks into `read/blocks/` with a `get` and the same `out_dir`.
   Do this before step 1's update, which needs the meta version the read returns.
   Save their versions as `read/versions.json`, `{"blocks/b0004": 4, "meta/chapter": 3}`,
   with `meta/chapter` at the version step 1's update returned.
   The store refuses a write to an existing document without its version, and `load` pins each write from this file.
   A block a round changed without a mark (a reflow) is not pinned by this; if a batch is refused for one, `get` it and add its version.
3. `tip editor-apply CH=NN`. It writes his in-place edits and deletions into the chapter, prints every cut
   with its surroundings, and lists the Rewrite marks and any conflicts.
   Read each cut: a deletion that leaves a broken sentence is flagged to Bruce in the reply, never silently patched.
4. Do the rewrites. Each is a quote with an optional note: rewrite the quoted text (widening to its sentence when the fault is there) to fix what the note says.
   With no note, find the fault the way `bare-pasted-phrase-is-a-review-request` describes: claim first, then clarity, then style.
   The global writing rules apply. Check any claim against the listing it describes.
   Handle each conflict by hand: the block changed in Zed during the round, so apply his intent to the current text.
5. `tip verify-ch CH=NN`, then commit the whole round as one commit, with the trailer.
   Judge the round by the chapter before and after it; who made which edit does not matter (Bruce, 2026-09-28).
6. `tip editor-load CH=NN`, then write its batch file(s) as in Opening step 3.
   The meta write reopens the page on the next round, with the changed blocks outlined.
7. Reply with the counts and each changed sentence as before → after, one line each, plus any flagged cut.
   Say what you guessed where a mark had no note.

## Rules

- Never run `load` over a round that has not been applied: it would drop his marks. `load` refuses without `--force`.
- Never write block documents while the page's status is `open`; he may be marking.
- Listings take Rewrite marks only. A Rewrite mark on a listing is a request to change the code in the Markdown block, then run the full verify loop.
- The page template is shared across chapters. After editing it, run `uv run python -m tools.chapter_editor page NN` for each open chapter and republish that copy to its URL; `load` also regenerates the copy.
- A change made to the chapter outside a round (a rename, a paragraph added on request) reaches an open page with `tip editor-load CH=NN ARGS=--refresh`,
  after checking the page has no marks or edits (`query` with `marks != []`, then `edit != null`).
  It stays in the round and outlines the change with the round's others; a plain or `--force` load would start the next round and drop the outlines Bruce has not read.
