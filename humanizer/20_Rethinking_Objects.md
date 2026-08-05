[[Reviewed]]
# Humanizer candidates: Chapters/20_Rethinking_Objects.md

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

Mostly clean, and dense with deliberate craft (the recurring "OOP
promise" framing, the italics-as-term-introduction discipline, four
parallel "Prefer X over Y" guidelines). The real findings are small:
a scattered "we"/"our" leaving the book's second person in three
places, one metaphorical "promise" that CLAUDE.md's rule targets
directly, one verbatim §7 AI-vocabulary hit ("crucial"), one
seven-sentence choppy run, and one participle tail. No curly quotes,
no em-dash issues, no emoji, no boldface-list abuse, no signposting,
no `[[ ]]` notes. The single biggest finding is the person-consistency
cluster: three separate "we"/"our" slips in an otherwise second-person
(or, in the opening, first-person-singular "I") chapter.

## Tier A

### A1 — lines 12, 168-170, 526 — person consistency ("we"/"our" slips)

The chapter opens in first person singular ("I spent... I wrote...")
and elsewhere addresses the reader as "you." Each site below drops
into "we"/"our" mid-thought. Delete individual rows you want left
alone.

**line 12**

Also drops "actually," a §7/watch-list word doing no work here.

CURRENT
```text
First, however, I want to question how much of that machinery we actually need.
```

PROPOSED
```text
First, however, I want to question how much of that machinery you need.
```

**lines 168-170**

Also removes the "but look at what X are doing" opener, the same
construction flagged separately at A2 for line 883.

CURRENT
```text
Now the internals are safe, but look at what we are doing.
We add private fields, getters, and defensive copies,
all to stop other code from changing our data.
```

PROPOSED
```text
Now the internals are safe, but at a cost: private fields, getters,
and defensive copies, all to stop other code from changing your data.
```

**line 526**

The sentence right before this one already says "you'll get an
exception"; this one switches to "we" mid-paragraph.

CURRENT
```text
If we use `t: object` (the safe top type),
```

PROPOSED
```text
If you use `t: object` (the safe top type),
```

### A2 — line 883 — theatrical opener echoing line 168

The same "but look at what X does" construction appears twice in the
chapter (line 168, handled in A1). CLAUDE.md's precedent applies this
kind of fix freely.

CURRENT
```text
But look at what the `None` branch does: nothing.
```

PROPOSED
```text
The `None` branch does nothing.
```

### A3 — line 836 — "promise" as a metaphor

CLAUDE.md bans "promise" as a metaphor for a guarantee, naming
"declares" as the replacement for exactly this case (an annotation).
This is distinct from the chapter's recurring "OOP promise" framing
(see Considered and not flagged), which names an actual numbered
running conceit rather than a stray metaphor.

CURRENT
```text
Each `@overload` line is a promise to the type checker,
not a function that runs.
```

PROPOSED
```text
Each `@overload` line is a declaration for the type checker,
not a function that runs.
```

### A4 — line 951 — "crucial" (§7 AI vocabulary)

Verbatim hit on the §7 high-frequency AI-vocabulary list. Dropping it
loses nothing the sentence needs.

CURRENT
```text
OOP also normalized the crucial idea of types,
```

PROPOSED
```text
OOP also normalized the idea of types,
```

### A6 — lines 54-55 — participle tail

"Reducing duplication" is a real consequence, not filler, but it's
still the tacked-on "-ing" shape §3 describes. A "which" clause reads
as a claim rather than an afterthought.

CURRENT
```text
They compose data structures instead of inheriting implementation,
and they let code live outside classes, reducing duplication.
```

PROPOSED
```text
They compose data structures instead of inheriting implementation.
They let code live outside classes, which reduces duplication.
```

## Tier B

### B1 — line 282 — broken parallel in the "OOP promise" refrain

Four headings each open with "The Nth OOP promise is..." The first
("is encapsulation: hide the data...") and third ("is reuse through
inheritance") use a noun phrase; this one alone switches to a
that-clause. I lean toward taking it since the other three establish
the pattern, but the that-clause also reads naturally on its own, and
forcing rigid parallelism across four fairly different sentences may
not be worth the churn.

CURRENT
```text
The second OOP promise is that behavior belongs inside the object, as methods.
```

PROPOSED
```text
The second OOP promise is behavior inside the object, as methods.
```

## Housekeeping

None found. No double blank lines before headings (checked every
heading transition in the file), no `[[ ]]` draft notes, no spaced
` -- `, no em dashes at all in the chapter, and no curly quotes
(grepped the whole file; every quotation mark is straight). A scan
for lines carrying more than one sentence (a mid-line period followed
by a capitalized word) found none, so there's no Semantic Line Break
drift to report.

## Considered and not flagged

- **The "OOP promise" refrain itself** (lines 36, 70, 84, 282, 381,
  443). "Promise"/"promises" recurs as a deliberate numbered
  structural conceit spanning the whole chapter (four OOP promises:
  encapsulation, methods, inheritance, polymorphism), set up before
  the enumeration even starts ("makes no substitutability promises,"
  "the base class... promises"). This is the controlling metaphor for
  the chapter's organization, not the stray "promise = guarantee" tell
  CLAUDE.md's rule targets. Only the unrelated, isolated use at line
  836 (A3 above) is a different, narrower metaphor and gets flagged.
- **"The fourth OOP promise is polymorphism."** (line 443). Bare,
  one-clause, no elaboration, unlike its siblings at lines 84 and 282.
  Reads like it could be a fragmented header (§29), but it introduces
  by far the longest and most-developed section in the chapter, so
  the terseness plays as a deliberate teaser rather than padding.
  Left alone.
- **Guidelines' closing bullet** ("Prioritize simplicity, clarity, and
  maintainability, to produce reliability."). Breaks the "Prefer X
  over Y" parallel of the four bullets above it, but it's doing
  different work: a synthesizing principle behind the four
  preferences, not a fifth preference. Forcing it into the same
  "Prefer... over..." shape would invent a contrast that isn't there.
  Left alone.
- **Italics used correctly throughout.** *Simula*, *Smalltalk*, *C++*,
  *Java*, the *Liskov Substitution Principle*, *shallow* (of a copy),
  the *diamond problem*, *nominal*/*structural*, *Subtype*/*Parametric*/
  *ad-hoc polymorphism*, *function overloading*, and the *Null Object*
  pattern are each a first-use term introduction, consistent with
  CLAUDE.md's rule. None are emphasis-only.
- **Rule-of-three-shaped groupings** (`charge()`/`persist()`/`audit()`
  at line 628; "return a description... finish rather than block...
  describe the object..." at line 723). Each count is structurally
  necessitated by the code or the argument, not an invented triad.
  Left alone.
- **Awkward double comma** ("made sense for the problem, and the
  hardware, of its time," lines 20-21). Reads oddly, but it isn't any
  of the listed AI patterns, just an idiosyncratic aside. Out of scope
  for this pass.

## Scan coverage

No hits anywhere in the chapter for: §1-2 undue-emphasis/notability
language, §4 promotional language ("boasts," "vibrant," "nestled"),
§5 vague attribution, §6 "Challenges and Future Prospects" sections,
§8 copula avoidance ("serves as," "features a"), §9 negative
parallelism/tailing negation, §10 rule-of-three abuse beyond the
structurally real counts noted above, §11 elegant variation, §12 false
ranges, §15 boldface overuse, §16 inline-header vertical lists, §18
emoji, §19 curly quotes, §20-22 chatbot-communication artifacts and
sycophancy, §21 knowledge-cutoff disclaimers, §23-24 filler phrases and
hedging, §25 generic positive conclusions, §26 hyphenated-pair overuse
(every hyphenated compound found is correctly attributive), §27
persuasive-authority tropes, §28 signposting ("let's," "here's what"),
§32 aphorism formulas, and the rest of §7's AI-vocabulary list beyond
"crucial." Person consistency was checked in full: the three sites in
A1 are the only first-person-plural slips in the chapter.
