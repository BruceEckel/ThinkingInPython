> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/42_Functional_Error_Handling.md`

Second review of this chapter.
All four findings in `readability/~42_Functional_Error_Handling.md` were accepted
and applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one added `@final` and a generic error
parameter to `utils/result.py`, a `must_unwrap.py` listing, a `combining_two.py`
listing, a `safe_demo.py` split out of `utils/safe.py`, three exercises, a new
`## Which Failures Get a Result` heading, and a capability paragraph at the end.
It also moved `test_result.py` into "Composing With bind" and shrank the
narrowing paragraph after `noted_result.py` from nine lines to three.

Every finding was resolved directly and applied (listed below).
No blocks remain.

## Applied directly

- "`unwrap()` is what makes that literal" → "`unwrap()` makes that literal"
  (the cleft the global rule names; the verb sat right after it).
- The duplicate checker message now appears once instead of twice. The
  paragraph above `must_unwrap.py` ends at "so `func_a(i).unwrap()` fails the
  checker." (its "which reports that `unwrap` is not defined on `Err[str]` in
  the union" clause cut), and the follow-up below the listing keeps that
  clause, next to the line it describes. The follow-up also lost its closing
  sentence ("The comment suppresses a real error so the listing can show what
  the checker was preventing"), which restated its own opening sentence.
- `combining_two.py` follow-up: "That scoping is the reason for the nesting,
  and it is what a flat sequence of `bind()` calls could not give you." →
  "A flat sequence of `bind()` calls could not give you that, because each
  step would see only the value handed to it." (the cut line restated the
  previous sentence with subject and predicate swapped; the replacement
  explains the contrast instead of asserting it).
- "Which Failures Get a Result" closing: "What you can do now that you could
  not at the start of the chapter: write a function..." → "You can now write
  a function whose signature admits it can fail, and chain three of them
  without a single `try` in the calling code." (§70: the old opener was the
  review checklist's question quoted into the chapter).
- Narrowing paragraph after `noted_result.py`: "which checks because
  `@final` on the two classes lets the checker narrow a `Result` to exactly
  one of them" → "which checks because `@final` on the two classes rules
  out a value that inherits from both, leaving the checker one class to
  narrow to" (the narrowing effect was asserted twice in the chapter and
  explained nowhere; this restores one clause of the mechanism the deep
  review's shrink removed, at the point where the reader sees the
  consequence. The class-definition sentence stays as the short forward
  reference it is.)

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- The new monad sentences ("`Maybe` chains a value that might be absent,
  `Result` chains one that might have failed, and an async container chains one
  that has not arrived yet") are a rule of three, but the three are the three
  cases chapter 39's catalog entry names, so the count is the content. Not
  flagged.
- "Python's untagged spelling of a *sum type*" uses "spelling," which the global
  watch list bans as a metaphor for how something is written. Here it is the
  established type-theory sense (an untagged versus tagged encoding of the same
  construct) and it sits against "tagged union" three paragraphs later, so it is
  the technical term rather than the metaphor. Not flagged, but worth a second
  opinion since the word is on the do-not-use list.
- The `safe_demo.py` lead-in ("Decorating a function that raises an exception is
  all it takes") was checked against the imperative-plus-consequence ban; it is
  a statement, not a command followed by its result.
