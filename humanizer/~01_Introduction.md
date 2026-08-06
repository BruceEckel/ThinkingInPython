[[Reviewed]]
# Humanizer candidates: Chapters/01_Introduction.md

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

The chapter is mostly clean. No em dashes, no curly quotes, no emoji, no
boldface lists, no hedging stacks, and one AI-vocabulary hit in 217 lines.
The largest finding is repetition rather than slop: five "able to" / "unable
to" constructions inside thirteen lines of the AI Trigger Warning section,
alongside "in the past" twice and two overlapping gerund triads. Two
first-person-plural slips ("We cover them here," "what problem we are
solving") break the book's second person. Everything else is small.
The personal sections read as unmistakably human and I left them alone.

All Tier A and Tier B edits have been applied.

## Housekeeping

1. **Semantic Line Break drift.** Lines 3, 85, 116, and 143 run past a
   clause boundary and would break further under `make reflow CH=01`.
   Lines 169 and 171 are long only because of a URL and a link target,
   so reflow cannot help those and they are fine as they are.
2. **Clean:** no double blank lines anywhere, no `[[ ]]` draft notes, no
   spaced ` -- `, no em dashes at all in this chapter, no curly quotes,
   no trailing whitespace.
3. **Low priority, not proposed:** line 121, "so you can read straight
   through, or jump to a chapter that interests you," has a comma before
   "or" joining two verb phrases with one subject. Correct either way.

## Considered and not flagged

- **No em dashes in this chapter at all.** §14 had nothing to preserve and
  nothing to flag.
- **Lines 17-19**, "Python has functions. / A Singleton is a module. / A
  Visitor is a function that dispatches on type." A staccato run of three
  and two "X is a Y" formulas (§31, §32). Kept: it is the book's thesis in
  miniature, and each sentence names a chapter the reader can go read.
- **Line 29**, "clear, idiomatic, and a pleasure to maintain." A broken
  parallel: two adjectives, then a noun phrase. Kept, because the break is
  what gives the sentence its warmth.
- **Line 85**, "from things as seemingly straightforward as inserting a new
  chapter to ones as daunting as that commented-output system." Reads like
  a §12 false range, but easy-to-hard is a real scale and both endpoints
  are named, concrete examples.
- **Line 90**, "I've become the director of the movie instead of an actor
  in it." An aphorism formula (§32). Kept: specific, personal, and
  defensible, which the skill lists as a human signal.
- **Line 59**, "Eventually I even wrote a message confirming I was not
  going to complete it." "Even" is on the avoid-if-possible list; here it
  carries the self-deprecation the sentence exists for.
- **Lines 107-113**, the "future of books" paragraph. Has a staccato pair
  ("I hardly do. / If I need something, I ask AI.") and ends on hope, which
  could read as §25. Kept: admitting he hardly reads programming books
  himself is the opposite of upbeat filler, and the closing hope is a real
  wish rather than a send-off.
- **§29 fragmented headers, two near-misses.** "Who This Book Is For"
  followed by "I am writing for the programmer who...", and "Exercises"
  followed by "Most chapters end with a short "Exercises" section." Both
  restate their heading, but each also carries content with nowhere else to
  go, and cutting the sentence would leave the section with no opening. 46
  and 47 split on this pattern, so I left both alone rather than guess.
- **Rule-of-three lists** at lines 7, 15, 64, 70, 72, and 145-147. The
  chapter leans on triads harder than most, which is why the verdict names
  the pattern, but each of these is a real enumeration. Only the
  near-synonym triad at 98 is proposed.
- **Lines 67 and 75**, "This book never would have happened without the
  help of Claude" and "Without it, this book wouldn't exist." The same
  claim eight lines apart. Kept: the first is an acknowledgment, the second
  answers readers who dislike AI, so each does different work.
- **"already" x6** (20, 26, 115, 127, 143, 192). Every one marks a real
  prior state.
- **"only" x4** (17, 22, 112, 196) and **"never" x4** (35, 65, 67, 92).
  All load real contrasts or real absolutes.
- **"happen" x2** (67, 194). Both idiomatic; no better verb.
- **Italics.** Four uses, all part titles (*Foundations*, *Techniques*,
  *Patterns*, *Functional Programming*). No emphasis italics anywhere.
- **Line 193**, "add a class, break an invariant on purpose, extend a
  table, rewrite one function two ways." A four-item asyndetic list that
  could look mechanical. Kept: the items are concrete and varied, and a
  four-item list is the opposite of the rule-of-three tell.

## Scan coverage

The word-level half of the skill found almost nothing. One hit on the
watched-vocabulary lists ("cultivating," B8). No curly quotes, no emoji,
no boldface, no inline-header vertical lists, no promotional or
notability language, no vague attributions, no weasel words, no copula
avoidance, no negative parallelism worth flagging, no sycophancy, no
collaborative-chat artifacts, no knowledge-cutoff disclaimers, no
persuasive-authority tropes, no §28 announcements, no §30 diff-anchored
writing, no hyphenated-pair overuse (the two compounds present,
"inheritance-heavy" and "already-working," are both attributive). Every
finding above is repetition, person, or a small filler construction.
