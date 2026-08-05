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

## Tier A

### A1 — lines 47, 143 — first-person plural in a second-person book

The book addresses "you." Two sentences slip into "we." Delete individual
rows you want left alone.

**line 47**

CURRENT
```text
We cover them here.
```

PROPOSED
```text
This book covers them.
```

### A2 — lines 84, 86, 87, 94 — "able to" five times in thirteen lines

Counting line 82's "unable to," the paragraph runs the same construction
five times. Line 86 also repeats "in the past" from line 79. Leaving
82 and one other alone keeps the rhythm. Delete individual rows you want
left alone.

**line 84**

CURRENT
```text
But with AI I've been able to explore and often implement every whim,
```

PROPOSED
```text
But with AI I can explore and often implement every whim,
```

**line 86**

CURRENT
```text
The result is much better than I've been able to achieve in the past.
```

PROPOSED
```text
The result is much better than anything I managed before.
```

**line 87**

CURRENT
```text
I'm able to keep going until I've tweaked everything that occurs to me.
```

PROPOSED
```text
I keep going until I've tweaked everything that occurs to me.
```

**line 94**

CURRENT
```text
I'm able to build my ideal book.
```

PROPOSED
```text
I can build my ideal book.
```

### A3 — line 98 — near-synonym triad

"Incorporated" and "integrated" say the same thing, and this is the
chapter's only list without a serial comma.

CURRENT
```text
Once Claude had incorporated,
translated and integrated my own work into the book,
```

PROPOSED
```text
Once Claude had translated and integrated my own work into the book,
```

### A4 — line 120 — stacked hedges

"Almost every" and "largely" hedge the same claim twice.

CURRENT
```text
Almost every chapter is largely self-contained,
```

PROPOSED
```text
Most chapters are self-contained,
```

### A5 — line 116 — filler phrase

"The knowledge contained in this book" is "the knowledge in this book"
(§23). The same edit normalizes "towards," the only instance in
`Chapters/`; the other four are "toward."

CURRENT
```text
I have found that the knowledge contained in this book has helped me guide AIs towards better solutions.
```

PROPOSED
```text
I have found that the knowledge in this book has helped me guide AIs toward better solutions.
```

### A6 — line 201 — stranded preposition

"With" ends the sentence and its object has moved.

CURRENT
```text
not in the code you end up with.
```

PROPOSED
```text
not in the code you produce.
```

### A7 — line 27 — "itself" as emphasis

"Either... or" already draws the contrast, so "in Python" alone says it.

CURRENT
```text
either in another language or in Python itself.
```

PROPOSED
```text
either in another language or in Python.
```

### A8 — line 178 — "book" twice in one clause

The subject is already "the book's build system."

CURRENT
```text
The book's build system extracts the book examples, then type-checks
```

PROPOSED
```text
The book's build system extracts the examples, then type-checks
```

## Tier B

### B1 — line 93 — the second gerund triad

Line 72 has "editing, rewriting, and adding" and line 93 has "directing,
rewriting, and editing." Same shape, two shared words, twenty lines apart.
Dropping one item from the later triad breaks the pattern. I lean toward
applying it, though which word goes is a coin toss: cutting "editing"
instead gives "my directing and rewriting."

CURRENT
```text
With Claude and my directing, rewriting, and editing,
```

PROPOSED
```text
With Claude and my directing and rewriting,
```

### B2 — lines 49, 92, 96 — intensifiers and throat-clearing

Three small ones. "Greatly" appears at 49 and 96; "fully" at 92 duplicates
"all its myriad"; "To be clear" at 96 announces the qualification that the
next sentence ("It did not make it trivial.") delivers. I lean toward all
three, but they are the kind of small thing that carries voice. Delete
individual rows you want left alone.


**line 92**

CURRENT
```text
but have never had the capacity to fully flesh out in all its myriad detail.
```

PROPOSED
```text
but have never had the capacity to flesh out in all its myriad detail.
```

**line 96**

CURRENT
```text
To be clear, using Claude greatly simplified and sped the writing process.
```

PROPOSED
```text
Using Claude greatly simplified and sped the writing process.
```

### B3 — line 139 — the second "itself"

Weaker than A7. "Stepping back to question" already says you are going after
the foundation, so "itself" is doing that work twice. Against it: "itself"
does mark the paradigm as opposed to the patterns built on it, which is the
sentence's point. I lean slightly toward applying.

CURRENT
```text
opens by stepping back to question object orientation itself,
```

PROPOSED
```text
opens by stepping back to question object orientation,
```

### B4 — line 183 — subject shifts mid-sentence

The condition addresses you and the main clause switches to "corrections."
I lean toward applying, since the surrounding paragraphs all speak to the
reader directly.

CURRENT
```text
If you find a mistake, corrections are welcome.
```

PROPOSED
```text
If you find a mistake, please send a correction.
```

### B5 — line 164 — participle tail

A §3 tail, and it makes the chapters do the waiting. Mild, since the
participle attaches to a real subject rather than adding fake depth.
I lean toward applying.

CURRENT
```text
waiting until [Static Typing](08_Static_Typing.md) introduces the syntax.
```

PROPOSED
```text
until [Static Typing](08_Static_Typing.md) introduces the syntax.
```

### B6 — line 64 — "mostly at PyCon" said twice

Line 136 states it again with more force ("Many of these chapters came from
presentations I've given, mostly at PyCon"). The parenthetical here is the
weaker of the two. I lean toward cutting it and letting 136 carry the fact.

CURRENT
```text
and presentations (mostly at PyCon).
```

PROPOSED
```text
and presentations.
```

### B7 — line 191 — "Most" opens two of three sentences

Lines 188 and 191 both open on "Most." I lean toward applying; the hedge
survives as "usually."

CURRENT
```text
Most ask you to change a small,
```

PROPOSED
```text
They usually ask you to change a small,
```

### B8 — line 6 — "cultivating"

The one word in the chapter on a watched list (§3's
"cultivating/fostering"). It is a real main verb with a real object here,
not a tacked-on tail, so this is close to a false positive. I lean weakly
toward "developing" because this sentence is the book's thesis and
"cultivating" is the fanciest word in it.

CURRENT
```text
It is about cultivating the judgment to choose the smallest thing that works.
```

PROPOSED
```text
It is about developing the judgment to choose the smallest thing that works.
```

## Housekeeping

1. **"towards" at line 116** is the only instance in all of `Chapters/`;
   chapters 19, 38, and 41 all use "toward." A5's PROPOSED already fixes
   it, so this needs no separate action unless you decline A5.
2. **Missing serial comma at line 98**, "incorporated, translated and
   integrated." The only one in the chapter. A3's PROPOSED removes the
   list, so this also resolves itself unless you decline A3.
3. **Semantic Line Break drift.** Lines 3, 85, 116, and 143 run past a
   clause boundary and would break further under `make reflow CH=01`.
   Lines 169 and 171 are long only because of a URL and a link target,
   so reflow cannot help those and they are fine as they are.
4. **Clean:** no double blank lines anywhere, no `[[ ]]` draft notes, no
   spaced ` -- `, no em dashes at all in this chapter, no curly quotes,
   no trailing whitespace.
5. **Low priority, not proposed:** line 121, "so you can read straight
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
