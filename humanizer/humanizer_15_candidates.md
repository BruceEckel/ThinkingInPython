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
an italics-for-emphasis misuse on the word "class." Two more items are
genuinely arguable and belong in Tier B. Everything else on the pattern
list, promotional language, rule-of-three padding, signposting, fragmented
headers, staccato drama, curly quotes, came back clean.

## Tier A

### A1 — lines 12, 172 — first-person plural ("we")

The book is second person throughout; both sites drop into "we," the same
pattern flagged and converted in chapters 46 and 47. Neither is a genuine
authorial aside worth keeping.

**line 12**

CURRENT
```text
This is far more reliable than using `__del__()`,
as we saw in [Cleanup](10_Cleanup.md).
```

PROPOSED
```text
This is far more reliable than using `__del__()`,
as shown in [Cleanup](10_Cleanup.md).
```

**line 172**

This one also announces what the prose is about to do ("We can write...")
instead of just presenting it, so the rewrite drops both the person slip
and the announcement in one pass.

CURRENT
```text
We can write a version with more features:
reporting which exception it swallowed,
and accepting no argument to mean "ignore everything."
It turns out to be useful enough to reuse elsewhere in the book,
so it lives in `utils/`, where any chapter can import it:
```

PROPOSED
```text
A version with more features reports which exception it swallowed,
and accepts no argument to mean "ignore everything."
It turns out to be useful enough to reuse elsewhere in the book,
so it lives in `utils/`, where any chapter can import it:
```

Delete individual rows you want left alone.

### A2 — line 228 — "class itself" (filler + emphasis italics)

This is close to the exact case `CLAUDE.md` calls out by name: "the class
itself" reads the same with "itself" cut. The italics on `class` add
emphasis rather than introducing a new term (`class` has been used
pervasively since chapter 1), and the sentence's own trailing "not an
instance of it" already carries the contrast the italics were reaching for.

CURRENT
```text
The annotations use `type[BaseException]`,
a [`type[...]`](08_Static_Typing.md#classes-as-values-type) annotation,
which means the exception *class* itself, such as `ZeroDivisionError`,
not an instance of it.
```

PROPOSED
```text
The annotations use `type[BaseException]`,
a [`type[...]`](08_Static_Typing.md#classes-as-values-type) annotation,
which means the exception class, such as `ZeroDivisionError`,
not an instance of it.
```

## Tier B

### B1 — line 8 — "actually"

On the watch list, but it may be earning its place: the sentence sets up a
contrast between "how to write your own context managers" and what `with`
"actually" does underneath, and the chapter goes on to reveal that
mechanism. A single watched word in isolation is weak evidence either way.
I lean toward cutting it since the sentence reads identically without it,
but this is closer to a coin flip than A1/A2.

CURRENT
```text
The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
runs setup before a block and cleanup after it,
even if the block raises an exception.
This chapter shows how to write your own context managers,
and what `with` actually does.
```

PROPOSED
```text
The `with` statement,
introduced in [Control Flow](04_Control_Flow.md#context-managers),
runs setup before a block and cleanup after it,
even if the block raises an exception.
This chapter shows how to write your own context managers,
and what `with` does.
```

### B2 — line 595 — italics on "production pool"

Unlike `*context manager*`, `*suppresses*`, and `*Object Pool*` elsewhere
in the chapter, "production pool" is not a term the book defines or reuses
(it appears nowhere else in `Chapters/`). The italics read as emphasis
contrasting this toy pool with a real one, not as a first-use term
introduction. I lean toward dropping the italics, but it's arguable that
naming the category is exactly the kind of "new concept" the italics
convention exists for.

CURRENT
```text
The second lease hands back the same object, not a new one.
A *production pool* adds refinements on this skeleton,
such as lazily creating items on first demand,
validating an item before lending it out,
and a timeout on `get()` so a starved borrower fails loudly instead of waiting forever.
```

PROPOSED
```text
The second lease hands back the same object, not a new one.
A production pool adds refinements on this skeleton,
such as lazily creating items on first demand,
validating an item before lending it out,
and a timeout on `get()` so a starved borrower fails loudly instead of waiting forever.
```

## Housekeeping

No `[[ ]]` draft notes, no curly quotes, no spaced ` -- `, and no double
blank lines before a heading anywhere in the chapter. Semantic Line Breaks
look intact throughout: every long line I checked (§10, §50, §202, §210,
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
