> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: A_Effect_Tracking (2026-10-16)

A full audit of the appendix's prose against the readability patterns.
`readability_db.md` was read first, and no earlier review of this appendix exists.
The prose is technical register with varied sentence lengths: no Tier 1A or Tier 2 vocabulary, no curly quotes, no spaced `--`, no signposting openers, no generic closer, and one watch-list word (a reader-addressed "want" at line 85, the `readability_db.md` carve-out).
Five sentences fired a rule with one sensible answer and were fixed in place.
Nothing needs your decision, so the file has no live blocks and serves as the applied-directly record.
`tip verify-ch CH=A` passes 21 of 21.

## Applied directly

- Line 19, "and" joining clauses with different subjects (a hidden contrast, "whereas" fits): "Tracking tells you which Effects a function can perform, and management lets you replace what those Effects do." -> two sentences.
- Line 242, one primary concept per paragraph and a pointer with two candidates: the paragraph on what an empty `row()` result can mean also carried the separate point that `quiet()`'s declaration is wrong. Split at that seam, and "The declaration is also wrong." (with `shout()` and `quiet()` both in play) -> "`quiet()`'s declaration is also wrong."
- Line 259, §70 interpretive metadiscourse: cut "Each one is larger than it first appears." after "a tool must solve five problems"; the five sections show the difficulty, and the sentence only told the reader how much weight to give them.
- Line 440, "and" joining clauses with different subjects (a hidden consequence, "so" fits): "it would fill all three roles, and you would have algebraic effect tracking" -> "it would fill all three roles and give you algebraic effect tracking".
- Line 481, "and" joining clauses with different subjects (a hidden contrast, "but" fits): "`Annotated` keeps the code ordinary and eager, and nothing verifies the row." -> two sentences, which also sets up the parallel with the native-system sentence that follows.

## Considered and declined

- Lines 53-60, the bold-led numbered list of three roles (§16 shape). Each bold lead is a full sentence, and the later prose names the items as "the first role", "the second and third roles", so the list is real list content.
- Lines 382-397, bold list labels ending in a period (§58). Each label ("Undeclared means pure.") is a full sentence, the rule's carve-out.
- Line 11, "showing how much of a type checker the tool would contain" (§3 participle tail). The phrase carries the appendix's thesis about the checker rather than fake depth; rewriting it as a second verb makes the sentence clumsier without adding clarity.
- Line 128, "Each piece of metadata is an ordinary expression, and `Annotated` keeps its value." Different subjects, but the clauses are two steps of one description (the expression is evaluated, its value is kept), and no "but", "so", or "while" fits.
- Line 136, "Each tool can therefore put its own object in the list, and every other tool ignores it." Two additive consequences of the PEP's rule, and the next sentence picks up "other tools".
- Line 235, "`greet()`'s row is right because I typed it correctly." First-person voice doing deliberate work: the row is only as right as the author who wrote it.
- Line 354, "A row that lists everything tells you nothing." Aphorism by shape (§32), but it states the concrete consequence of the two sentences before it (an unsubtracted row grows to every Effect in the program).
- Line 397, "says how long that took: a decade." A colon reveal by shape (§69), but the colon delivers what "how long" announced, which passes the global colon test.
- Lines 415-417, consecutive "That checker ..." / "That appendix's ..." openings. Each "That" points at the one appendix just named, and rewording either sentence would need a name the chapter does not use.
- Line 450, "Metadata is data, and its reader decides what it means." Aphoristic, but the next two sentences unpack it (a static reader, a runtime reader), so it is the paragraph's topic sentence.
