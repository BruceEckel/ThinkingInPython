[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/10_Cleanup.md`

This chapter reads as human technical prose throughout.
A full scan for Tier 1A, Tier 1B, and Tier 2 vocabulary (§7) turned up exactly one hit, `underscore`, and that one is inside the quoted CPython documentation blockquote describing leading-underscore globals, so it is exempt under the Self-Reference Escape Hatch.
There is no boldface, no curly quotes, no non-ASCII characters, no spaced ` -- `, no signposting or "let's" openers, no hedging stacks, no generic closer, and no banned repo phrases.
Sentence lengths vary, and the explanatory paragraphs are anchored to specific output lines rather than to abstractions, which is the opposite of the treadmill pattern.
One mild redundancy is the only thing worth Bruce's time, and it is borderline.

***

[] Reject

**Section:** Reliable Alternatives (paragraph immediately following the `weak_value.py` listing)
**Pattern:** §70 Interpretive Metadiscourse / low information density (P2)

Current:
> Storing each instance in a `WeakValueDictionary` tracks it without keeping it alive.

Proposed:
> Cut this sentence.

Why: Item 3 of the numbered list already says this two sentences before the listing ("A weak reference, which tracks an object without keeping it alive. / Here, a `WeakValueDictionary` counts live instances"), in nearly the same words, so the post-listing paragraph opens by repeating rather than advancing; cutting it makes the paragraph start on "The key is `id(self)` because...", which matches how the `finalizer.py` paragraph opens on new information. Borderline: the sentence does narrow the general claim about weak references to the specific container, so if Bruce wants the restatement as a re-entry point after the code, this is a legitimate reject.

***
