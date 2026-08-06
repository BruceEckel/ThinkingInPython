[[Reviewed]]
# Humanizer candidates: Chapters/45_Generators.md

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

This chapter is clean of the classic AI-vocabulary and content-padding
tells: no §1-§12 language, no boldface-header lists, no curly quotes,
no emoji, no fragmented headers, no signposting, no aphorism formulas.
Two real structural findings survived a full read: a person-consistency
slip ("we"/"our" leaking into the book's second-person voice, two sites)
and a recurring stranded preposition ("where it came from" / "what it
asks for", four sites) that matches a hard rule in `CLAUDE.md` rather
than a soft AI-tell judgment call. Tier B is empty; nothing else rose to
a genuine judgment call. The largest single finding is the stranded
preposition, since it repeats four times across the chapter with the
identical shape.

## Tier A

### A1 — lines 104-105, 378 — person consistency (we/our -> you/the)

The book is second person throughout. These two sites drop into
first-person plural, the same slip the precedent chapters (46, 47)
had and converted.

**lines 104-105**

CURRENT
```text
With `NewType` we can give each channel a distinct type,
so the annotation states the arrangement and a checker enforces it.
```

PROPOSED
```text
With `NewType` you can give each channel a distinct type,
so the annotation states the arrangement and a checker enforces it.
```

**line 378**

CURRENT
```text
We can apply `yield from` to our `interview()` example:
```

PROPOSED
```text
You can apply `yield from` to the `interview()` example:
```

Delete individual rows you want left alone.

### A2 — lines 226, 423, 425, 513 — stranded prepositions

`CLAUDE.md`'s "No stranded prepositions" rule names this exact shape
("what it is for") as the banned pattern: a sentence ending on a
preposition whose object was fronted as "where"/"what". All four
sites here fit that description precisely, and two of them (423, 425)
are an intentional parallel pair describing the same mechanism from
both sides, so the fix should keep the parallelism, not break it.

**line 226**

CURRENT
```text
Notice that `interview()` does not know where the answers come from.
```

PROPOSED
```text
Notice that `interview()` does not know where the answers originate.
```

**line 423**

CURRENT
```text
which knows nothing about where it came from.
```

PROPOSED
```text
which knows nothing about where it originated.
```

**line 425**

CURRENT
```text
which also knows nothing about where it came from.
```

PROPOSED
```text
which also knows nothing about where it originated.
```

**line 513**

CURRENT
```text
the question stops being what a function does and becomes what it asks for.
```

PROPOSED
```text
the question stops being what a function does and becomes what it requests.
```

Delete individual rows you want left alone. The line 513 fix also
happens to echo "request", the EMS term the chapter introduces in
italics at line 182, so it isn't an arbitrary word swap.

## Tier B

None. Nothing in this chapter rose to a genuine "he could go either
way" call once the two Tier A patterns above were pulled out. The
usual Tier B candidates for this book (fragmented headers, declined
signposting) don't have instances here to weigh.

## Housekeeping

1. Two forward references to "the next chapter" (line 19: "The next
   chapter builds an Effect system on all three"; line 514: "That is
   the question the next chapter puts into the type system"). Since
   this chapter was split out of what is now chapter 46 (Stateless),
   these currently point correctly at 46, but worth a human check that
   the split didn't leave either one meaning something else.
2. Semantic Line Break outlier at line 526 (exercise 3): a single
   154-character line with no internal break
   ("...after adding a third `yield from collect("gamma")` to `both()`
   and extending the loop to `[1, 2, 3, 4, 5]`."), noticeably longer
   than the rest of the chapter's wrapped prose. `make reflow CH=45`
   would tighten it; no gate catches it.
3. No `[[ ]]` draft notes, no double blank line before any heading, no
   spaced ` -- `, and no em dash at all in this chapter (nothing to
   preserve or flag on that front).

## Considered and not flagged

- **Italics on *request* and *answer* (line 182).** These introduce
  the chapter's two EMS terms for the first time; the rest of the
  chapter uses them unitalicized. Correct use of the "first-use only"
  rule, not an emphasis violation.
- **"the plain `str`" (line 109).** Draws a real contrast against the
  `NewType`-wrapped `Question`/`Answer`/`Result` names introduced two
  sentences earlier: the checker sees three distinct types, but at
  runtime there is only "the plain `str`". Keeps its place under the
  CLAUDE.md exception for a genuine contrast.
- **"It has no dictionary, no `input()` call, and no network
  connection" (line 227).** A three-item list, but each item is a
  distinct concrete fact ruling out a different real mechanism, not
  padding to hit a count of three.
- **The running "conversation" metaphor** (generator-as-conversation,
  introduced line 13 and threaded through "states what it needs",
  "the driver", "answers"). This is a sustained structural device the
  chapter builds on, not a one-off aphorism formula ("X is the Y of
  Z"); dismantling it would remove the chapter's organizing idea, not
  fix a tell.
- **"This chapter covers..." (lines 16-20).** Declarative scope-setting
  ("This chapter covers the full three-channel annotation, the loop
  that carries such a conversation, and `yield from`..."), not a
  conversational announcement like "Let's dive in." The §28 pattern
  targets chatbot chumminess, not a textbook's opening scope sentence.
- **No fragmented headers.** Every heading in this chapter is followed
  directly by substantive content (e.g. "### The Return Channel" leads
  with what the return channel is, not a one-line restatement of the
  heading). Nothing here to weigh either way on the per-instance call
  from 46/47.
- **Mid-sentence "reports where the machine got to" (exercise 7, line
  547).** Same shape as the A2 pattern, but the preposition isn't
  sentence-final (the clause continues, "...rather than requesting
  something the machine needs"), so `CLAUDE.md`'s rule as written
  doesn't reach it. Left alone; flagging it would mean extending the
  rule past what it says.

## Scan coverage

Clean on every word-level list checked: the §7 AI-vocabulary set,
§1-§6 content-padding tropes (significance/legacy, notability,
"-ing" superficial analysis, promotional language, vague attribution,
challenges-and-future-prospects), §8 copula avoidance, §9 negative
parallelism and tailing negation, §10 rule-of-three overuse, §11
elegant variation, §12 false ranges, §15 boldface, §16 inline-header
lists, §19 curly quotes, §18 emojis, §20-§22 chatbot/servile
communication artifacts, §23-§25 filler and hedging, §27 persuasive
authority tropes, §28 signposting, §29 fragmented headers, §31
staccato drama, §32 aphorism formulas, §33 rhetorical openers, and the
global `CLAUDE.md` watch list (already/even/never/only/actually/
itself/exactly/plain/promise/has to/is what/the "nothing else"
family). No em dashes appear anywhere in this chapter, so §14 has
nothing to check. A rerun can skip all of the above and focus on
person consistency and stranded prepositions if the chapter changes.
