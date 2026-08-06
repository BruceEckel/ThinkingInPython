[[Reviewed]]
# Humanizer candidates: Chapters/15_Context_Managers.md

Run date: 2026-08-05. Source: `humanizer` skill (blader/humanizer, adapted).

## How to use this

Each edit is a `###` block with a CURRENT and a PROPOSED fence.
Delete any block you don't want, save the file, and hand it back to me.
I apply what survives, verbatim, and run `make verify`.

The CURRENT fences are exact copies from the chapter,
so don't hand-edit inside them or the match will fail.
If you want a different wording, edit the PROPOSED fence instead
and I will use yours.

Tier A is what I'd apply. Tier B is genuinely arguable, delete freely.
Housekeeping is not humanizer output; separate list at the end.

## Verdict

This chapter is close to clean. The scan found two small first-person-plural
slips ("we saw," "We can write") of the kind chapters 46 and 47 already
converted to impersonal phrasing, and one clear filler "itself" paired with
an italics-for-emphasis misuse on the word "class." One more item was
genuinely arguable and belonged in Tier B. Everything else on the pattern
list, promotional language, rule-of-three padding, signposting, fragmented
headers, staccato drama, curly quotes, came back clean.

All Tier A and Tier B edits have been applied.

## Housekeeping

No `[[ ]]` draft notes, no curly quotes, no spaced ` -- `, and no double
blank lines before a heading anywhere in the chapter. Semantic Line Breaks
look intact throughout: every long line checked (§10, §50, §202, §210,
§221) is one clause with no internal comma to break at, not drift. Nothing
to report.

## Considered and not flagged

- **Line 218, "leaves only `Types`," and line 553, "It only tracks
  custody."** Both draw a real contrast (against `ALL` and against "never
  creates or destroys," respectively), so `only` earns its place. Left
  alone.
- **Line 42, "The yielded value is what `as` binds."** This is the exact
  keep-case in `CLAUDE.md` ("is what" followed by a noun phrase that can't
  attach without it). Not a finding.
- **Line 61, "How does `with` know what to run?"** A rhetorical question
  framing the section, not a theatrical "Honestly?" hook (§33). No
  standalone pause-and-reveal. Left alone.
- **Line 497, "Lending is the dangerous half."** One short sentence for
  emphasis, not a run of them (§31 needs several in a row). Left alone.
- **Line 559-560, "The pool becomes the throttle that limits concurrent
  use, which is how real database connection pools behave."** A near miss
  for the §32 aphorism formula ("X becomes a Y"), but it states a concrete,
  checkable mechanism rather than reaching for vague profundity, and the
  clause right after it grounds the claim in a real-world comparison. Left
  alone.
- **Lines 441-449, the `contextlib` bullet list.** Near miss for §16
  (inline-header vertical list), but each bullet leads with an actual API
  name in code font, not a generic bolded label like "**Performance:**",
  and each description is substantive. Left alone.
- **Lines 491, 596-598, groups of three examples.** ("database
  connections, worker processes, licensed sessions"; the three production-pool
  refinements.) Ordinary technical enumeration, not the padded §10
  rule-of-three. Left alone.
- **Every heading followed by its opening sentence** ("The Protocol,"
  "Cleanup Is Guaranteed," "The `contextlib` Toolkit," etc.). None restate
  the heading before the real content starts (§29); each opens with
  substantive claims. Left alone.
- **"As shown above" at lines 445 and 446.** Repeated twice for `ExitStack`
  and `ContextDecorator`. Mildly repetitive but factual and not a clustered
  tell on its own; not worth a block.

## Scan coverage

Zero hits across: undue-significance puffery (§1), notability/media
coverage (§2), superficial -ing endings (§3), promotional/advertisement
language (§4), vague attributions (§5), "Challenges" boilerplate (§6),
§7 AI-vocabulary words other than "actually" (no *delve*, *crucial*,
*tapestry*, *testament*, *pivotal*, *intricate*, *fostering*, *garner*,
*enhance*, *underscore*, *showcase*, *landscape*), copula avoidance (§8),
negative parallelisms and tailing negations (§9), rule-of-three overuse
(§10), elegant variation (§11), false ranges (§12), boldface overuse (§15),
inline-header lists (§16), emojis (§18), curly quotes (§19), collaborative
chatbot artifacts (§20), knowledge-cutoff disclaimers (§21), sycophantic
tone (§22), filler phrases (§23), excessive hedging (§24), generic positive
conclusions (§25), hyphenated-pair overuse (§26), persuasive authority
tropes (§27), fragmented headers (§29), diff-anchored writing (§30),
staccato drama (§31), and rhetorical openers (§33). Structural review
covered the whole chapter, not just the flagged lines.
