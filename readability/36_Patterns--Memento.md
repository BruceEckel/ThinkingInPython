> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 36_Patterns--Memento (2026-10-16)

A full audit of the chapter's prose against the readability patterns.
No completed review of this chapter exists, so `readability_db.md` was read first; it holds no chapter 36 entry, and its recurring keeps cover the watch-list hits below.
The chapter is technical register with varied sentence and paragraph lengths, no Tier 1A or Tier 2 vocabulary, no curly quotes, no spaced `--`, no boldface, no signposting openers, and no generic closer.
Three sentences fired a rule with one sensible answer and were fixed in place; nothing needs your decision, so the file has no live blocks and serves as the applied-directly record.
`tip verify-ch CH=36 ISOLATED=1` passes 27 of 27.

## Applied directly

- Line 22, "and" joining clauses with different subjects: "shows a getter handing out a reference where the caller expects a copy, and a memento depends on that difference." -> two sentences, "... expects a copy. A memento depends on that difference."
- Line 147, treadmill (§70 restatement): "though a frozen memento raises an exception on an accidental edit. Assigning different strokes to the memento raises a `FrozenInstanceError`." said one thing twice -> "though a frozen memento raises a `FrozenInstanceError` on an accidental edit."
- Line 380, "and" hiding a contrast ("while" fits): "[*Flyweight*] shares immutable values among objects that exist at once, and *Memento* shares them among successive states." -> two sentences at the comma.

## Considered and declined

- Line 6, aphorism shape (§32): "Undo is a feature users expect and programmers dread." The chapter's opening beat, in the author's voice; the next sentence defines the pattern.
- Line 43, §34 "real": "`list(todo)` makes a real copy". The contrast is named in the sentence before (`saved = todo` binds a second name); recurring keep.
- Line 168, `FrozenInstanceError` stated again after the line 147 edit: "`Memento` is a record, so reassigning `checkpoint.strokes` raises `FrozenInstanceError` at runtime." Kept: it is one of the two runtime differences the "Why `Memento` Is a Class" section weighs against an alias, and it carries the chapter's link to the `record` definition.
- Line 164, `only` before a code span: "A parameter typed `Memento` accepts only a `Memento`". The "only a X" shape was ruled fine (2026-10-04), and the restriction is the claim, set against `tuple[str, ...]` accepting any tuple one sentence earlier.
- Lines 347 and 362-363, commerce words: "`k` edits held in the history cost `O(k^2)` pointers", "cost about two million pointers", "costs two thousand". A measured memory quantity, which rule R2 keeps.
- Line 410, §39 self-labeling: "since opacity is the pattern's whole point." The chapter's opening defines the caretaker as storing mementos without reading their contents, so the clause restates a stated premise rather than inflating one; "whole" is voice.
- Line 506, §12 false range: "from `int` to a full `Drawing`". A real scale from a bare value to a compound record, and `test_history.py` uses `int` states.
- Line 740, colon delivering a summary (§69): "Pickle's convenience comes from leaving one job to you: matching the class on load to the class on save." The colon delivers the one job the lead-in counts, and the sentence closes the drift walkthrough with its consequence.
- Line 817, closing generalization (§25): "Whenever you see rewind, rollback, or restore, something produces mementos." Each verb maps to an example in the paragraph (checkout, savepoints, game rewind), so the triple is an inventory, not padding.
