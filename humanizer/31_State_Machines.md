# Humanizer candidates: Chapters/31_State_Machines.md

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

Mostly clean prose; the word-level AI-vocabulary lists (§1-§8, §15-§30) turned
up almost nothing. The one real recurring pattern is first-person-plural
slippage: five "we"/"us" spots break the book's second-person voice, the
largest single finding. A handful of decorative italics and a couple of
stranded prepositions round out the rest. No em dashes appear anywhere in
this chapter, so there was nothing to protect there. No `[[ ]]` notes, no
blank-line or Semantic Line Break drift (`tools/reflow_prose.py` reports zero
changes for this file).

## Tier A

### A1 — lines 36, 38, 42, 382, 672 — person consistency ("we"/"us")

Five spots drop into first-person plural, breaking the book's you-address.
Delete individual rows you want left alone. The line-382 row also
straightens a broken parallel (the three list items shift between question
forms) while it removes "we".

**line 36-37**

CURRENT
```text
However, it allows us to say that something is a `State` object in code,
and provide a slightly different error message when a derived class fails to implement all the methods.
```

PROPOSED
```text
However, it lets you say that something is a `State` object in code,
and provide a slightly different error message when a derived class fails to implement all the methods.
```

**line 38**

CURRENT
```text
We could have gotten nearly the same effect by saying:
```

PROPOSED
```text
You could get nearly the same effect by saying:
```

**line 42**

CURRENT
```text
because we still get exceptions if code calls `run()` or `next()` on a derived type that hasn't implemented them.
```

PROPOSED
```text
because calling `run()` or `next()` on a derived type that hasn't implemented them still raises an exception.
```

**line 380-382**

CURRENT
```text
For a given current state and input, a transition row answers three questions:
is there a condition to check, what action runs during the transition,
and what state do we move to next.
```

PROPOSED
```text
For a given current state and input, a transition row answers three questions:
whether a condition must pass, what action runs during the transition,
and what state comes next.
```

**line 672**

CURRENT
```text
Using `tkinter` we can create a GUI representation of the vending machine.
```

PROPOSED
```text
Using `tkinter`, you can create a GUI representation of the vending machine.
```

### A2 — line 47-48 — negative parallelism ("not only... but also")

§9's classic correlative-conjunction padding. The plain conjunction says the
same thing without the scaffolding.

CURRENT
```text
This method not only moves to the next state,
but it also calls `run()` for each state object.
```

PROPOSED
```text
This method moves to the next state
and calls `run()` for each state object.
```

### A3 — line 359-360 — emphasis italics ("unexpected")

Not a first-use term, just decorative emphasis on an ordinary adjective.

CURRENT
```text
The two versions also answer a question this input file never asks:
what happens on an *unexpected* input?
```

PROPOSED
```text
The two versions also answer a question this input file never asks:
what happens on an unexpected input?
```

### A4 — line 376 — emphasis italics ("entire")

Same pattern: emphasis, not term introduction.

CURRENT
```text
A pure state machine can go further and represent the *entire* machine as a single transition table.
```

PROPOSED
```text
A pure state machine can go further and represent the entire machine as a single transition table.
```

### A5 — line 74-75 — stranded preposition

"warned about" leaves the preposition stranded at the sentence's end with no
object; front the claim onto a transitive verb instead.

CURRENT
```text
The constructor also runs the initial state,
the construction-starts-the-engine choice that chapter warned about.
```

PROPOSED
```text
The constructor also runs the initial state,
the construction-starts-the-engine choice that drew a warning in that chapter.
```

## Tier B

### B1 — line 246-248 — emphasis italics ("other")

Arguable: the italics could be read as disambiguating (these are states
*other than* the current one), not pure emphasis. Lean toward dropping it
since nothing else in the sentence needs the stress.

CURRENT
```text
You cannot write a table inside its class,
because its entries name the *other* states,
which do not all exist until every class definition runs.
```

PROPOSED
```text
You cannot write a table inside its class,
because its entries name the other states,
which do not all exist until every class definition runs.
```

### B2 — line 440 — emphasis italics ("exactly")

Same call as B1: arguably load-bearing (contrasting exact dict-key matching
against an `isinstance()` walk), but it's still emphasis on an ordinary word.
Lean toward dropping the italics; the colon and the contrast that follows
already carry the point.

CURRENT
```text
Note that the lookup keys on `type(event)` *exactly*: a dictionary probe,
not an `isinstance()` walk.
```

PROPOSED
```text
Note that the lookup keys on `type(event)` exactly: a dictionary probe,
not an `isinstance()` walk.
```

### B3 — lines 16, 370 — mild stranded prepositions

Both are idiomatic and would read fine to most readers ("move to," "hear
about,"), but they fit CLAUDE.md's stranded-preposition rule exactly. Lean
toward leaving these alone unless you want the stricter reading applied
everywhere; delete either row independently.

**line 16**

CURRENT
```text
each `State` object decides what other states it can move to,
```

PROPOSED
```text
each `State` object decides which other states to enter,
```

**line 370**

CURRENT
```text
where a missing entry is a bug you want to hear about,
```

PROPOSED
```text
where a missing entry is a bug you want flagged,
```

### B4 — lines 14, 16-17 — word echo

The same idea ("what state to move to," keyed off "input") gets restated
almost verbatim one sentence apart. Could be tightened, but it could also be
deliberate: the paragraph goes on to restate the same distinction a third
way ("Another way to put it is..."), so the repetition may be an intentional
teaching device rather than a slip. Lean toward leaving it; flagging in case
you disagree.

CURRENT
```text
you can also pass it an "input" object so it can tell you what new state to move to based on that "input."
The key distinction between this design and the next is that here,
each `State` object decides what other states it can move to,
based on the "input,"
whereas in the subsequent design a single table holds all of the state transitions.
```

PROPOSED
```text
you can also pass it an "input" object so it can tell you what new state to move to.
The key distinction between this design and the next is that here,
each `State` object makes that decision on its own,
whereas in the subsequent design a single table holds all of the state transitions.
```

## Housekeeping

1. **Listing comment, line 546-547.** The `vending_machine.py` comment
   "so the model never touches the screen" uses a watch-list word inside a
   code comment, which the hard rules treat as a real finding even though it
   reads as an ordinary technical statement here. If you want it reworded
   (e.g. "so the model does not touch the screen"), it needs a re-sync
   (`make verify` handles it) since the comment lives inside an extracted
   listing.

## Considered and not flagged

- **Pattern-name italics** (`*State*`, `*StateMachine*`, `*Template Method*`,
  `*Proxy*`). Confirmed via chapters 21, 25, and 26 that the book
  italicizes pattern names on every mention, not just first use. This is a
  book-wide convention, not an emphasis-italics violation.
- **"plain methods"** (line 453). Directly contrasts with the
  `Condition`/`Transition` class hierarchy described two sentences earlier
  (the Java version's approach), so it earns its place per CLAUDE.md's
  "plain" test.
- **The word "exactly" in plain prose** (line 353, "the output continues
  exactly as in the first version"). A genuine precise/logical match,
  allowed under CLAUDE.md's carve-out. Distinct from the italics markup on
  the *other* "exactly" at line 440 (B2), which is what's actually flagged
  there.
- **The staccato pair at lines 368-371** ("Ignoring suits a machine fed from
  a noisy source..." / "Failing fast suits a table you are still
  building..."). Each half states a distinct concrete claim rather than
  manufacturing drama, so left alone.
- **"### The Engine" and "### A Vending Machine" opening sentences.**
  Considered as possible fragmented headers (§29), but neither restates the
  heading text; both move straight into specific mechanism ("the engine
  walks the candidate transitions in order...", "It collects money, takes a
  two-digit selection..."), so they don't match the pattern.
- **The "three questions" list at lines 380-382.** Reflects the actual
  three-field transition tuple `(condition, action, next_state)` shown in
  the table sketch two lines later, not a decorative rule-of-three. Only its
  broken parallel structure is flagged (see A1's last row).
- **"never" in ordinary prose** (line 668, "the model never draws
  anything"). A plain factual statement, not a hedge. Distinguished from the
  listing-comment instance in Housekeeping.
- No promotional language, vague attributions, "Challenges and Future"
  section, copula avoidance, elegant variation, false ranges, curly quotes,
  emoji, boldface, or inline-header-colon lists found anywhere in the
  chapter.

## Scan coverage

Clean: §1 (significance/legacy), §2 (notability), §3 (-ing analysis
padding), §4 (promotional language), §5 (vague attributions), §6
("Challenges" sections), §7 (AI-vocabulary word list, aside from the one §9
hit), §8 (copula avoidance), §10 (decorative rule-of-three), §11 (elegant
variation), §12 (false ranges), §13 (passive/subjectless fragments), §15-§19
(boldface, inline-header lists, title case, emoji, curly quotes), §20-§25
(collaborative artifacts, cutoff disclaimers, sycophancy, filler phrases,
hedging, generic conclusions), §27-§30 (authority tropes, signposting,
fragmented headers, diff-anchored writing). No em dashes exist in this
chapter at all. `tools/reflow_prose.py` reports zero paragraphs needing
reflow; no double blank lines, `[[ ]]` notes, or spaced ` -- ` found.
