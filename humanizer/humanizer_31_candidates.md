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

A clean chapter overall: no AI vocabulary, no filler phrases, no rule-of-three
padding, no fragmented headers, no signposting, no boldface lists, no curly
quotes, no em dashes at all (so nothing to preserve or misflag there), and
`reflow_prose.py --diff` found zero Semantic Line Break drift.
The real findings are structural, not lexical: a five-site cluster of
first-person plural ("we"/"us") in a book that is otherwise second person,
one sentence that violates the imperative-plus-consequence rule directly,
and four italics used for emphasis rather than to introduce a term.
The largest single finding is the "we"/"us" cluster.

## Tier A

### A1 — lines 36, 38, 42, 382, 672 — first-person plural

The book is second person throughout.
These five sites lapse into "we"/"us," three of them clustered in one
paragraph about the empty `State` base class.

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
because code that calls `run()` or `next()` on a derived type that hasn't implemented them still raises an exception.
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
is there a condition to check, what action runs during the transition,
and what state the machine moves to next.
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

Delete individual rows you want left alone.

### A2 — line 443-444 — imperative-plus-consequence

Commands the reader, then reports what happens, exactly the construction
`CLAUDE.md` calls out ("Remove `frozen=True` and the pattern fails").
The condition form reads the same and doesn't put the reader in the driver's
seat of a hypothetical they didn't ask to perform.

CURRENT
```text
and it cuts the other way too:
define a further subclass of an event type and it matches none of its parent's rows.
```

PROPOSED
```text
and it cuts the other way too:
if you define a further subclass of an event type, it matches none of its parent's rows.
```

### A3 — lines 247, 360, 376, 440 — emphasis italics

Italics are reserved for introducing a term on first use elsewhere in the
book (the pattern names `State`, `StateMachine`, `Template Method` are
italicized consistently throughout, which is a different, legitimate
convention). These four instead italicize an ordinary word for emphasis.

**line 247**

CURRENT
```text
because its entries name the *other* states,
```

PROPOSED
```text
because its entries name the other states,
```

**line 360**

CURRENT
```text
what happens on an *unexpected* input?
```

PROPOSED
```text
what happens on an unexpected input?
```

**line 376**

CURRENT
```text
A pure state machine can go further and represent the *entire* machine as a single transition table.
```

PROPOSED
```text
A pure state machine can go further and represent the entire machine as a single transition table.
```

**line 440-441**

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

Delete individual rows you want left alone.

## Tier B

### B1 — line 47-48 — negative parallelism

"Not only...but also" is the §9 construction the skill flags, though here
it's used for a plain factual description rather than rhetorical inflation,
so this is a genuine judgment call, not a clear tell.

CURRENT
```text
This method not only moves to the next state,
but it also calls `run()` for each state object.
```

PROPOSED
```text
This method moves to the next state and also calls `run()` for each state object.
```

I lean toward applying it; the plain version is shorter with no loss.

### B2 — line 357 — stacked verbs

"Quickly read and understand" pairs two verbs where one clearer one would
do. Minor, and arguably fine as conversational emphasis.

CURRENT
```text
since it's easier to quickly read and understand the state transitions from looking at the table.
```

PROPOSED
```text
since the state transitions are easier to see at a glance in the table.
```

## Housekeeping

1. Content mismatch, not a humanizer finding: line 129 says each `State`
   subclass "establishes its next state with an `if-else` clause," but the
   code immediately below (lines 144-192) uses `match`/`case`, not
   `if`/`else`. Worth a look independent of this pass.

## Considered and not flagged

- Pattern-name italics (`*State*`, `*StateMachine*`, `*Template Method*`,
  `*generator*` in the exercises) appear on nearly every mention, not just
  first use. That's the book's typographic convention for design-pattern
  and vocabulary names, not emphasis, so none of those are findings.
- "Nothing here needs a `switch`, reflection, or a `Condition`/`Transition`
  class hierarchy" (line 601): "nothing" as the sentence's subject is
  ordinary English per the `CLAUDE.md` "nothing else" family rule, not the
  trailing-tag construction the rule targets.
- "The conditions and actions are plain methods" (line 453): "plain" draws
  a real contrast against the `Condition`/`Transition` class hierarchies
  described two paragraphs earlier (the Java version needed them; Python
  doesn't), so it earns its place rather than being a filler qualifier.
- The three-question breakdown of a transition row (line 380) and the
  three-item list of what the table replaces (line 601, "`switch`,
  reflection, or a ... class hierarchy") both describe a real fixed count
  (a 3-tuple; three concrete alternatives from the Java comparison), not a
  manufactured rule-of-three.
- "That chapter" at line 75 (referring to Template Method) sits one
  sentence after an explicit link to `25_Template_Method.md`, so it
  resolves cleanly and doesn't need its own link per the project's
  cross-reference convention.
- Checked every heading (Table-Driven State Machine, The Engine, A Vending
  Machine, Exercises) for a fragmented-header restatement; none of the
  paragraphs that follow merely restate their heading.
- No em dashes anywhere in the chapter, so nothing to preserve or misflag.
- No `[[ ]]` draft notes and no spaced ` -- ` anywhere in the chapter.

## Scan coverage

Zero hits on: AI-vocabulary words (§7), promotional/advertisement language
(§4), vague weasel-word attribution (§5), "Challenges and Future Prospects"
sections (§6), false ranges (§12), boldface overuse (§15), inline-header
bullet lists (§16), emoji (§18), curly quotes (§19), collaborative-chatbot
artifacts (§20), knowledge-cutoff disclaimers (§21), sycophantic tone (§22),
filler phrases (§23), excessive hedging (§24), generic positive conclusions
(§25), hyphenated-pair overuse (§26), persuasive-authority tropes (§27),
signposting/announcements (§28), diff-anchored writing (§30), aphorism
formulas (§32), and conversational rhetorical openers (§33).
`reflow_prose.py --diff` confirms no Semantic Line Break drift, so that
housekeeping category is clean too.
