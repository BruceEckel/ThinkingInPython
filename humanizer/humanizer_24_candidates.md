# Humanizer candidates: Chapters/24_Singleton.md

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

The chapter is close to clean on the classic AI-tell checklist: no
AI-vocabulary hits, no signposting, no boldface-header lists, no curly
quotes, no em dashes at all (so nothing to preserve or fix there), and
the "nothing else" family didn't turn up anything the August sweep
missed. What did turn up is small and structural: a genuine leftover
duplicate sentence in "Lazy Creation," a three-site first-person-plural
slip ("we"), and a small cluster of emphasis-only italics. One
fragmented-header candidate is Tier B, arguable either way.

## Tier A

### A1 — line 236 — redundant duplicate sentence

"This version builds the inner instance on the first call" and "It
builds the inner object on the first call" say the same thing twice,
two sentences apart, with "it is lazy" sandwiched between the halves.
Reads like an unmerged edit. The Eager Creation section right below it
makes the equivalent point once.

CURRENT
```text
This version builds the inner instance on the first call.
It is *lazy*.
It builds the inner object on the first call,
which is why it needs the `None` sentinel and the `if` guard.
```

PROPOSED
```text
It is *lazy*: it builds the inner object on the first call,
which is why it needs the `None` sentinel and the `if` guard.
```

### A2 — three sites — first-person plural ("we")

The book is second person throughout, and the chapter's own prose
already uses "you" for this ("You can use a class decorator...",
"Sometimes you do want a class"). These three lines slip into "we."

**line 101**

CURRENT
```text
Only if the type never left the module would we use `_Settings`.
```

PROPOSED
```text
Only if the type never left the module would you use `_Settings`.
```

**line 346**

CURRENT
```text
We can use `__new__()`, the method that creates an instance,
to return the same object every time:
```

PROPOSED
```text
You can use `__new__()`, the method that creates an instance,
to return the same object every time:
```

**line 399**

CURRENT
```text
Here we keep the single instance in a class variable.
```

PROPOSED
```text
Here you keep the single instance in a class variable.
```

Delete individual rows you want left alone.

### A3 — three sites — emphasis italics

The chapter's italics are otherwise disciplined: term on first use
(*singleton*, *constructor function*, *memoizes*, *lazy*, *eagerly*,
*Borg*). These three instances italicize an ordinary word already in
circulation, for stress rather than introduction.

**line 334**

CURRENT
```text
The two forms differ only in *when* they create the inner object.
```

PROPOSED
```text
The two forms differ only in when they create the inner object.
```

**line 436**

CURRENT
```text
that what you usually want is not one *object* but one shared set of *state*.
```

PROPOSED
```text
that what you usually want is not one object but one shared set of state.
```

**line 663**

CURRENT
```text
- For almost everything, use a *module* with module-level state.
```

PROPOSED
```text
- For almost everything, use a module with module-level state.
```

Delete individual rows you want left alone.

## Tier B

### B1 — line 50 — fragmented header

The heading asks "when you want a class," and the paragraph opens by
restating it almost word for word ("Sometimes you do want a class")
before adding the real content. Unlike the skill's textbook example
("Speed matters."), this restatement isn't pure filler: the second
clause ("every construction should return the same object") does carry
new information the heading doesn't. I lean toward leaving it, since
cutting the echo also cuts a smooth lead-in to "The simplest solution
is..."; but it's the same pattern flagged (and decided both ways) in
46 and 47.

CURRENT
```text
## When You Want a Class, Cache the Instance

Sometimes you do want a class,
but every construction should return the same object.
The simplest solution is to hide construction behind a cached factory.
```

PROPOSED
```text
## When You Want a Class, Cache the Instance

Every construction should return the same object.
The simplest solution is to hide construction behind a cached factory.
```

## Housekeeping

1. Stray double blank line before the `singleton_pattern.py` fence in
   "Lazy Creation" (the blank run currently sitting at lines 240-241).
   Every other code fence in the chapter has exactly one blank line
   before it; this one has two. `make verify` won't catch this since
   it's whitespace, not a marker or sync issue.

## Considered and not flagged

- **Em dashes / spaced ` -- `.** None anywhere in the chapter, so
  nothing to preserve and nothing to flag.
- **Curly quotes.** None found.
- **`[[ ]]` draft notes.** None found.
- **AI-vocabulary list (§7).** Zero hits (no *delve*, *tapestry*,
  *pivotal*, *underscore* as a verb, etc.), consistent with 46 and 47.
- **Signposting/announcements (§28), boldface-header lists (§16),
  emoji (§18).** None present.
- **Repeated `*Borg*` italics (lines 439, 445, 667).** Looks like a
  deliberate proper-noun-style treatment for a coined pattern nickname
  rather than plain emphasis, closer to how the book italicizes a book
  title on every mention than to a stray emphasis italic. Left alone;
  flag me if you disagree.
- **"no sentinel, no guard, and no race" (line 339).** A tailing
  triple-negative, but it's doing real contrastive work against the
  lazy form's "it carries the sentinel and the guard" one sentence
  earlier, not padding for its own sake. Left alone.
- **"Mutate through any name. Rebind only through the module."
  (lines 47-48) and its echo "Mutate through any name. Declare only
  what you rebind." (lines 201-202).** A deliberate two-line aphorism
  used as a callback between sections, not filler repetition.
- **"Privacy in Python is advice, not enforcement." (line 121).**
  Aphorism-shaped, but states a specific, true technical claim rather
  than a hollow profundity. Left alone.
- **Isolated short sentences** ("No class, no ceremony.",
  "This is not a narrow window.").
  Single instances, not a stacked run, so they don't meet the
  staccato-drama bar the skill sets.
- **Footnote quoting Star Trek** ("we are all one," line 439).
  Secondhand text inside a quotation, not an authorial "we"; excluded
  from the person-consistency finding.

## Scan coverage

No hits on: undue-significance language (§1-2), promotional/
advertisement language (§4), vague attribution (§5), "Challenges and
Future" sections (§6), copula avoidance (§8), rule-of-three padding
(§10, aside from the genuinely functional "Three implementation
notes"), elegant variation (§11), false ranges (§12), boldface overuse
(§15), collaborative-communication artifacts (§20), knowledge-cutoff
disclaimers (§21), sycophancy (§22), filler phrases (§23), excessive
hedging (§24), generic positive conclusions (§25), hyphenated-pair
overuse (§26), persuasive-authority tropes (§27), aphorism formulas
(§32, aside from the one considered above), and conversational
rhetorical openers (§33). The "nothing else" family was already swept
book-wide in August and turned up nothing new here.
