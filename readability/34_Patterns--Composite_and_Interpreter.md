> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Composite and Interpreter

The chapter carries few AI-writing tells.
The watch-list hits are all keeps under `readability_db.md`,
and the three edits below untangle "and" clauses that joined different subjects or put a conclusion before its rule.
This file holds no live block, so it is the record of what was applied directly and what was considered and left alone.

## Applied directly

- Line 335, different-subject "and": "`Operators` is a base class but not a member of `Expr`, and the split is on purpose" -> "`Operators` is a base class but, on purpose, not a member of `Expr`."
- Lines 431-433, rule before choice: "This chapter keeps structural comparison. A class gets either that or an `==` that builds a node, not both." -> "A class can have structural comparison or an `==` that builds a node, but not both. This chapter keeps structural comparison." The general constraint now comes first, and "that" no longer points back across a sentence.
- Line 558, different-subject "and": "The tree holds the structure and each walker supplies the meaning, so a new operation is one more walker" -> "The tree holds the structure. Each walker supplies the meaning, so a new operation is one more walker." The "so" now hangs on the walker clause it follows from.

## Considered and declined

- Line 156, "That self-reference makes the tree a tree." A short closing beat (§31/§32 by shape), but it states the claim the paragraph builds to: the recursive member allows arbitrary depth. Kept as a beat among longer sentences.
- Line 273, "*Interpreter* is *Composite* applied to language." Restates the chapter opening's "*Interpreter* is *Composite* with meaning attached" (§70 by shape). Kept: it re-establishes the frame at the section's start, after the long `pathlib` digression.
- Line 344, "even with a case for every node." On the avoid list, but the concession is the claim: the `match` is complete and still fails against an open base class.
- Line 569, "An interpreter need not produce a number or a string. It can produce another tree." A negative before the positive. Kept: the negation names the two outputs the reader has just seen, so the contrast carries the section's turn.
- Line 720, the three-walker paragraph. Confirmed keep on the 2026-10-04 Sweep Decisions page.
- Line 838, "Textbooks usually present the *Interpreter* pattern as..." A vague attribution by §5's shape. Kept: it describes the common framing, which the closing sentence then sets aside, and naming a source would add a fact the chapter does not make.
- Watch-list words "itself" (155, reflexive), "only for" (280, a ruled-fine shape), "real parser" (283, contrasted with Python's own parser), "already" (575, 634, temporal), and "plain"/"plainer" (631, 632, 637, 819, each against a node or a `Template`). All keeps under the recurring rules in `readability_db.md`.
- Line 412, SymPy, Polars, and SQLAlchemy as a triple (§10). The next sentence uses each item ("symbolically, over a whole column, or as SQL"), so the three are an inventory, not padding.
