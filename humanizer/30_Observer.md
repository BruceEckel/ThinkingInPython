[[Reviewed]]
# Humanizer candidates: Chapters/30_Observer.md

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

This chapter is close to clean. Two Tier A findings, two Tier B, three
housekeeping notes. The word-level half of the skill found nothing at
all: no §7 vocabulary, no em dashes, no curly quotes, no boldface, no
promotional or sycophantic language. The largest real finding is the
two-site `we` slip in the async and visual-example sections; everything
else is a single small instance.

## Tier A

### A1 — line 161 — tailing negation fragment

"no error anywhere" is tacked onto the end of the sentence as a
verbless fragment rather than written as a clause, the same shape as
the skill's "no guessing" example.

CURRENT
```text
so the next observer is silently skipped, no error anywhere.
```

PROPOSED
```text
so the next observer is silently skipped, and nothing signals the loss.
```

### A2 — two sites — first person plural

The book is second person. Both are plain editorial `we`, not the kind
of deliberate first-person aside the earlier chapters kept. Delete
either row you want left alone.

**line 216**

CURRENT
```text
For this example, we only need a coroutine to pause at `await` while others run:
```

PROPOSED
```text
For this example, you only need a coroutine that pauses at `await` while others run:
```

**line 307**

CURRENT
```text
`tkinter` plays no part here, so we can test the model without a GUI.
```

PROPOSED
```text
`tkinter` plays no part here, so you can test the model without a GUI.
```

## Tier B

### B1 — line 196 — participle tail

"doing the forgetting automatically" reads as a reduced relative clause
tacked onto the sentence rather than written out. Mild; the meaning is
already clear either way.

CURRENT
```text
or weak references (`weakref.WeakMethod`) doing the forgetting automatically.
```

PROPOSED
```text
or weak references (`weakref.WeakMethod`), which forget automatically.
```

### B2 — line 274 — "exactly"

On the watch list, but it states a real logical identity (calling an
`async` function produces exactly an awaitable, nothing looser), which
is the carve-out `CLAUDE.md` allows. I lean toward keeping it, same
call as the equivalent hit in chapter 27.

CURRENT
```text
which is exactly what calling an `async` function produces.
```

PROPOSED
```text
which is what calling an `async` function produces.
```

## Housekeeping

1. **Semantic Line Break drift.** Line 433 runs to 168 characters with
   an unused break point at "between players / or to keep track of...",
   and line 439 runs to 111 with an unused break at "an exception /
   and the second...". `make reflow CH=30` fixes both; no gate catches
   this.
2. **No double blank lines.** Heading spacing is uniform throughout
   (one blank line before each of the four `##` headings).
3. **No `[[ ]]` draft notes, no spaced ` -- `, and no em dashes at all.**
   §14 had nothing to preserve and nothing to flag.

## Considered and not flagged

- **"the *Observer* pattern amounts to nothing more than a list of
  callbacks" (line 97).** This is the exact sentence `CLAUDE.md` names
  as the keeper case for "nothing more than": the diminishing is the
  point. Left alone on purpose.
- **"values in, values out" (line 305).** A staccato pair, but it names
  a real property of a pure function (inputs mapped to outputs), the
  same shape as "garbage in, garbage out." Not manufactured drama.
- **"The list of callbacks becomes a line of waits" (line 203).** Reads
  close to an aphorism formula, but the metaphor is concrete and
  accurate (sequential blocking really does queue up waits), not vague
  profundity standing in for a claim.
- **"The `list()` copy inside `notify()` is a single word doing quiet
  work" (line 155) and "Two more realities of Observer deserve a
  sentence each" (line 187).** Both are single instances of a creative,
  slightly personifying turn of phrase. Neither stacks with others, and
  both carry real information about what follows. The skill's own
  guidance says one short emphatic or unusual sentence is not a tell on
  its own.
- **Repeated italics on *Observer*/*observer*/*observable* (lines 3, 5,
  15, 18, 21, 31, 33, 97).** Matches the book's convention of
  italicizing a pattern name on every mention, not just first use,
  which chapter 27's review already established as exempt from the
  strict first-use rule. Lines 31 and 33 re-italicize *observer* and
  *observable* specifically because the paragraph is redefining them in
  Python terms against the classic definition from the opening; that's
  a real second introduction, not emphasis.
- **"never" at lines 10 and 189.** Both state a genuine architectural
  absolute (the observable never needs to know observer types; a
  stopped loop never reaches later observers), not an intensifier.
- **The two-item list at lines 9-10.** Not a rule-of-three; two real,
  distinct properties.
- **"only" (eight sites, e.g. lines 200, 283, 297, 381, 418).** Each is
  a genuine restriction with a real contrast nearby (only prints vs.
  later I/O observers, only the shared contract vs. the rest of each
  file). None read as filler.
- **"itself" (line 157 and the line 174 code comment).** Both reflexive
  and load-bearing: an observer detaching itself is literally the
  subject acting on itself.
- **Chapter-opening roadmap ("This chapter shows the Pythonic version
  first, then extends it... It closes with...", lines 25-27).**
  Describes the chapter's actual structure rather than a conversational
  "let's dive in" announcement. Standard technical-book scaffolding,
  not the §28 tell.
- **§29 fragmented headers.** Checked all four `##` headings
  (`The Pythonic Observer: a List of Callables`, `Observer and I/O`,
  `A Visual Example of Observers`, `Exercises`). None open with a
  sentence that just restates the heading.

## Scan coverage

The word-level half of the skill was entirely clean: no §7
AI-vocabulary hits, no curly quotes, no emoji, no boldface anywhere in
the chapter, no promotional or sycophantic language, no filler phrases,
no hedging stacks, no false ranges, no elegant variation, no copula
avoidance, no predicate hyphenation, no generic upbeat conclusion, and
no em dashes to consider. No stranded prepositions found. Everything
above is structural: one tailing negation, one person slip (two
sites), and two mild Tier B calls.
