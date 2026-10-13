> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Deep review: 33_Patterns--Visitor (third review, 2026-10-13)

This third review follows `~33_Patterns--Visitor.r2.md` (2026-09-29), the 2026-10-08 outside review and its verdicts, the commerce sweep (375a8205), and the two listing-design rounds (8fdfe34a, eadf4b19).
`uv run tip verify-ch CH=33 ISOLATED=1` passed 27 of 27 before the edits and 27 of 27 after; `tip prose CH=33` reports 0 new hits.
Every extracted listing in `build/verify-ch-33/` was run directly and matches its `#:` markers.
Probes on `ty` 0.0.86, Pyright 1.1.414, and mypy 2.4.0 (run through `uv run --with mypy`, since mypy is no project dependency): `accept(self, visitor: Visitor)` draws `unresolved-attribute` on `visitor.visit` from all three; `nectar(42)` passes `ty` and Pyright, which both reveal `_SingleDispatchCallable[str]`, and mypy rejects it with `arg-type`, as the chapter says; `Corsage("rose")` draws `invalid-argument-type` against `Accepts`; Solutions exercise 3 without its `# type: ignore` draws `invalid-argument-type`.
`ast.NodeVisitor.visit()` was read in the installed stdlib.
Cross-chapter claims were checked against chapters 32 (`paper_scissors_rock.py`'s `Any` and `eval_*()` methods), 34 (`assert_never()` under "A Composite of Data Classes"), 37 (`recycling_note.py` and its `NotImplementedError` pointer back here), and the story figure's text.
One live block.

## Applied directly

Chapter:

- "The Price of the Empty Base", `ast.NodeVisitor` sentence: the quoted `getattr()` call left out its third argument. Now quotes `getattr(self, "visit_" + node.__class__.__name__, self.generic_visit)` as the stdlib writes it and says an unmatched node class falls back to `generic_visit()`, the same default-answer behavior the `singledispatch` section discusses.
- "Nothing edits `Flower`. Each operation is a separate function." moved from after the `_` paragraphs to directly after `visitor_singledispatch.py`. It states what the listing shows; the mechanism paragraphs (`register` reading the annotation, the `_` name) now follow it instead of separating it from its listing.
- Classic *Visitor*: "*double dispatch*" lost its italics. Chapter 32 introduces the term ("*double dispatching*"), so italics here marked a second introduction.
- "Where Visitor Still Fits": the section said the loop inside `accept()` is where the classic pattern fits but never said what that arrangement gives you. Added that every visitor reuses the one loop: a new visitor defines `visit()` for a single flower, and `Corsage.accept()` carries it through every nested element.
- "One Dispatch Is Enough": "When two types must genuinely resolve together" is now "When both types must resolve together at runtime". "genuinely" was an intensifier; "at runtime" names the condition the paragraph is about.

Solutions:

- Exercise 1: deleted the bold "Dispatch where the flower type matters." paragraph. It repeated the opening paragraph's point (only `eat()` answers differently by flower type, so only `eat()` dispatches) in nearly the same words. This leaves the watch-words baseline entry "only: Only CODE is a CODE function" stale.
- Exercise 2: "an operation takes fewer lines to add than a type, because an operation is a whole function and lives in one place" gave locality as the reason for the line count. The count comes from the registrations (one for `thorns()`, two for `Rose`). The paragraph now says so, scopes the comparison to this program ("Here"), and keeps locality as a separate point that leads into the expression-problem link.

## Live blocks

### 1. The heading "The Price of the Empty Base" is a commerce figure (R2)

"Price" stands for a consequence: the section explains what the `Any` gives up and where the Python form puts the operations.
The 2026-10-10 commerce sweep left the heading, and the watch-words baseline accepts the link text that echoes it (chapter line 33, Solutions exercise 3's hint), so no tool will raise it again.
`readability_db.md` records a declined retitle (`## What the Classic Shape Costs`) on different grounds: that title was vaguer and still named only the first paragraph.

Proposed heading: `## What the Python Form Gives Up`.
It covers both paragraphs (the `Any` gives up the visitor-side check; the operations move onto `Flower`, which the pattern exists to avoid), and it echoes the chapter's "In this Python form of the pattern" in the sentence that links the section.
The anchor becomes `#what-the-python-form-gives-up`; the two links to it are the chapter's own line 33 and Solutions exercise 3's "Where to look", and no other chapter or tool links it.
Alternative: `## What the Empty Base Gives Up`, which matches the first paragraph's wording but repeats the old title's mismatch with the second paragraph.
This is a block because it retitles your heading against an earlier decline.

Applied 2026-10-13 with the title Bruce chose: `## Two Departures from the Classic Shape`.

## Considered and declined

- The first review's declined rewrite (operations kept in the visitor instead of on `Flower`) stays declined.
- "A new `Visitor` subclass that reuses an existing operation, such as `Fly`" names `Fly` before the listing defines it. The next sentence introduces the listing, so the forward reference resolves within a few lines. Left.
- `Corsage`'s hand-written `__init__()` and public `elements` (internal-names baseline) were judged in earlier reviews. Left.
- Solutions exercise 3, "because `Beetle` inherits no `visit()` and so does not match the protocol": the negation is the claim. Left.

## For the session

- `tools/data/watch_words_baseline.txt` line 948 (`Solutions/33_Patterns--Visitor/README.md	only: Only CODE is a CODE function`) is stale after the exercise 1 deletion; `tip prose` reports it as stale.
- `tip prose` also reports a stale internal-names entry, `Examples/15_Techniques--Context_Managers/banner_cm.py::banner.title`, from outside this chapter.
