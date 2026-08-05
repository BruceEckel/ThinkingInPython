# Humanizer candidates: Chapters/27_Factory.md

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

Twelve Tier A findings, eleven Tier B, five housekeeping notes.
The chapter reads as two layers: inherited *Thinking in Java* prose in the
Simple Factory, Polymorphic Factories, and Abstract Factories sections,
and newer Python-side commentary in the registry, Protocol, Prototype,
and Builder material. Almost every finding sits in the newer layer.
The largest single one is the `we`/`let's` cluster, five sites, three of
them in the legacy layer where you may want the authorial voice kept.
Two hard rules from `CLAUDE.md` are broken outright: "spellings" at line
488 (third-tier, don't use) and two stranded prepositions at 554 and 747.
No em dashes anywhere in the chapter, so §14 had nothing to protect.

## Tier A

### A1 — line 488 — banned word

`spellings` is on the don't-use list. "Forms" says the same thing.

CURRENT
```text
The two spellings look interchangeable in a listing and fail at different moments.
```

PROPOSED
```text
The two forms look interchangeable in a listing and fail at different moments.
```

### A2 — line 377 — §7 AI vocabulary, plus an emphasis italic

`valuable` is on the §7 high-frequency list, and the italic on *class*
is emphasis rather than a first-use introduction.
Restore the italic in the PROPOSED fence if you want the contrast marked.

CURRENT
```text
A separate factory *class* becomes valuable when creating an object takes real work beyond calling a constructor,
```

PROPOSED
```text
A separate factory class is worth writing when creating an object takes real work beyond calling a constructor,
```

### A3 — line 554 — stranded preposition

"what the interfaces were for" is the exact shape your rule names
("what it is for").

CURRENT
```text
It preserves what the interfaces were for,
```

PROPOSED
```text
It preserves the purpose of the interfaces,
```

### A4 — line 747 — stranded preposition

Same pattern: the object of "for" has moved to the front of the clause.

CURRENT
```text
`dataclasses.replace()` covers the other thing builder chains are used for:
```

PROPOSED
```text
`dataclasses.replace()` covers the other use of builder chains:
```

### A5 — line 482 — §28 announcement

Announces the observation instead of making it. The next line,
"They fail at *call* time:", still reads correctly after the swap,
since "They" then refers to the bodies.

CURRENT
```text
Note what their `raise NotImplementedError` bodies do and do not enforce.
```

PROPOSED
```text
Those `raise NotImplementedError` bodies enforce less than the listing suggests.
```

### A6 — line 601 — filler intensifier

"Simply" adds nothing; the sentence is already the small claim it needs to be.

CURRENT
```text
The `clone()` method simply wraps `copy.deepcopy()`.
```

PROPOSED
```text
The `clone()` method wraps `copy.deepcopy()`.
```

### A7 — lines 721-722 — §31 concede-then-reveal pair

Two short declaratives staged as a setup and a punchline.
One sentence with the contrast inside it does the same work.

CURRENT
```text
The class works, and it reads well.
It also solves a problem Python does not have.
```

PROPOSED
```text
The class works and reads well, but it solves a problem Python does not have.
```

### A8 — lines 778-779 — §33 rhetorical question opener

Question, then a verbless fragment as the reveal.
The answer is a perfectly good sentence on its own.

CURRENT
```text
When does Builder survive in Python?
When construction genuinely is a process.
```

PROPOSED
```text
Builder survives in Python when construction genuinely is a process.
```

### A9 — line 792 — stock idiom

"Hides in plain sight" is a borrowed phrase where a direct one works.

CURRENT
```text
The humblest builder in Python hides in plain sight.
```

PROPOSED
```text
The humblest builder in Python is easy to overlook.
```

### A10 — line 237 — emphasis italic

The chapter's other italics all introduce a term or name a pattern.
This one is emphasis on a single ordinary word.

CURRENT
```text
Know *when* the registration happens:
```

PROPOSED
```text
Know when the registration happens:
```

### A11 — lines 555-557 — repeated closer

The sentence before it has already made this point, and both sentences
end on "shared base class." Cutting the second removes the echo and the
paragraph still closes on the contrast.

CURRENT
```text
without the coupling a shared base class imposes.
Python's version of interface inheritance is a `Protocol`,
not a shared base class.
```

PROPOSED
```text
without the coupling a shared base class imposes.
```

### A12 — five sites — first person plural

The book is second person. Five editorial `we`/`let's` sites.
Lines 20, 30, and 31 are inherited *Thinking in Java* prose, so those
three are the ones where you may prefer the older authorial voice.
Line 90's "I have also used a *generator*" is first person singular and
authorial; I left it alone. Delete individual rows you want left alone.

**line 20**

CURRENT
```text
We force the creation of objects to go through a common *factory* rather than spreading creational code throughout the system.
```

PROPOSED
```text
You force the creation of objects to go through a common *factory* rather than spreading creational code throughout the system.
```

**line 30**

CURRENT
```text
As an example, let's revisit the `Shape` system.
```

PROPOSED
```text
As an example, revisit the `Shape` system.
```

**line 31**

CURRENT
```text
We can make the factory a `@staticmethod` of the base class:
```

PROPOSED
```text
The factory can be a `@staticmethod` of the base class:
```

**line 382**

CURRENT
```text
The *Abstract Factory* pattern looks like the factory objects we've seen previously,
```

PROPOSED
```text
The *Abstract Factory* pattern looks like the factory objects shown previously,
```

**line 603**

CURRENT
```text
We can combine prototype with a registry.
```

PROPOSED
```text
You can combine prototype with a registry.
```

## Tier B

### B1 — lines 193-195 — §31 staccato run

Three short sentences in a row, the last two saying one thing twice.
I lean toward flagging: the middle sentence is the padding, and
"The `dict` is the factory" is worth keeping as the landing.

CURRENT
```text
Thus, the simplest factory is a dictionary that maps names to classes.
No factory method or factory class exists.
The `dict` is the factory.
```

PROPOSED
```text
Thus, the simplest factory is a dictionary that maps names to classes.
There is no factory method and no factory class; the `dict` is the factory.
```

### B2 — lines 375-376 — two-word imperative fragment

"Prefer that." is the manufactured-punchline shape (§31), though it is
also just terse advice. I lean mildly toward folding it in.

CURRENT
```text
It maps a name to a class and constructs it.
Prefer that.
```

PROPOSED
```text
It maps a name to a class and constructs it,
so prefer that version.
```

### B3 — line 363 — §7 word plus hedging

`intricacies` is on the §7 list and "it seems that" is hedging, but this
line predates LLMs by two decades, so the hit is coincidence. Your call
whether the voice or the rule wins. I lean toward flagging, weakly.

CURRENT
```text
However, it seems that much of the time you don't need the intricacies of the polymorphic factory method,
```

PROPOSED
```text
However, much of the time you don't need the complexity of the polymorphic factory method,
```

### B4 — lines 483 and 485 — emphasis italics

Both mark a moment rather than introducing a term, so the italics rule
says they are findings. I lean toward keeping them: the contrast between
the two moments is the whole point of the passage, and dropping the
italics makes it easy to skim past. Delete either row.

**line 483**

CURRENT
```text
They fail at *call* time:
```

PROPOSED
```text
They fail at call time:
```

**line 485**

CURRENT
```text
An `@abstractmethod` fails at *instantiation*,
```

PROPOSED
```text
An `@abstractmethod` fails at instantiation,
```

### B5 — lines 643-644 — vague claim plus "never"

"Show that Prototypes are safe because" front-loads a conclusion the
tests do not state; they show independence. `never` is on the
avoid-if-possible list. I lean toward flagging.

CURRENT
```text
These tests show that Prototypes are safe because each spawn is independent,
and the stored prototype never changes:
```

PROPOSED
```text
These tests show that each spawn is independent
and that the stored prototype does not change:
```

### B6 — line 235 — §28 forward announcement

A §28 hit by the letter of the rule, but it earns its place: it tells the
reader why three more sections of older factories follow a section that
just called the registry the idiomatic answer. I lean toward keeping it.

CURRENT
```text
The sections below show the classic object-oriented factories for contrast.
```

PROPOSED
```text
The remaining sections cover the classic object-oriented factories, for contrast.
```

### B7 — lines 178-179 — word echo across adjacent clauses

"On every call, so each call to" repeats within one sentence.

CURRENT
```text
The nested `class` statements run again on every call,
so each call to `factory()` defines fresh `Circle` and `Square` classes.
```

PROPOSED
```text
The nested `class` statements run again on every call,
so `factory()` defines fresh `Circle` and `Square` classes each time.
```

### B8 — lines 782-783 — §27 authority trope

"The real thing" implies the earlier examples were counterfeit, which is
roughly your argument, so this may be deliberate. I lean toward flagging
because the following sentences already prove the point concretely.

CURRENT
```text
`GameBuilder` in [Simulation](38_Simulation.md#a-robot-in-a-maze)
is the real thing.
```

PROPOSED
```text
`GameBuilder` in [Simulation](38_Simulation.md#a-robot-in-a-maze)
qualifies.
```

### B9 — line 794 — §32 aphorism formula

"Builder's essence" gestures at the claim the sentence has already made.
I lean toward flagging, weakly; the sentence is also carrying three
appositives, and splitting it helps.

CURRENT
```text
a string, through a mutable intermediate, which is Builder's essence.
```

PROPOSED
```text
a string, through a mutable intermediate.
That is the structure Builder describes.
```

### B10 — line 816 — "exactly"

On the watch list, though here it does push the student toward precision
rather than intensifying. I lean toward keeping it.

CURRENT
```text
    and explain exactly which line of which file performs the registration,
```

PROPOSED
```text
    and explain which line of which file performs the registration,
```

### B11 — line 799 — awkward "already are"

The word order is the problem more than the word. "Already" is doing
little that "are" does not, since the point is that no extra class is needed.

CURRENT
```text
keyword arguments and a data class already are the builder.
```

PROPOSED
```text
keyword arguments and a data class are the builder.
```

## Housekeeping

1. **Semantic Line Break drift.** Several prose lines run well past a
   clause boundary without breaking. The worst are 88, 283, 362, 468,
   and 484, all over 140 characters with internal comma or parenthetical
   breaks available. `make reflow CH=27` fixes it; no gate catches it.
   Line 398 is the image alt text and is long for the same reason,
   but check what `reflow` does to it rather than assuming.
2. **No double blank lines.** Heading spacing is uniform throughout.
3. **Line 6 uses the Unicode ellipsis character `…`**, not `...`:
   "without disturbing existing code … or so it seems." It is the only
   one in the chapter. Reported, not proposed; it reads as deliberate
   typography for the trailing-off.
4. **No `[[ ]]` draft notes, no spaced ` -- `, and no em dashes at all.**
   §14 had nothing to preserve and nothing to flag.
5. **`## The Pythonic Factory: a Dictionary`** is the one heading with a
   lowercase interior word. No edit proposed, since the anchor is gated by
   `heading_links.py`; noted only in case you want to normalize it yourself.

## Considered and not flagged

- **The legacy `happens` clefts**, line 14 ("It happens to be the creation
  of the type that matters here") and line 86 ("It happens to be a string
  here"). Both hit the `happen` watch list and both are cleft
  constructions, but they are the inherited voice of this chapter's Java
  edition. Say the word and I will sweep them; I did not want a style pass
  rewriting the chapter's oldest prose without you asking.
- **Line 359**, "The actual creation of shapes happens in
  `ShapeFactory.create_shape()`." Same call, same reason.
- **Line 382**, "with not one but several factory methods." A §9 negative
  parallelism, but the contrast with the single-method factory is real and
  the line is legacy prose.
- **Line 283**, "*GoF Design Patterns* emphasizes that..." `emphasizing`
  is on the §7 list, but this has a real subject doing real emphasizing.
- **Line 480**, "(translated from the Java version)." Reads like §30
  diff-anchored narration, but it records genuine provenance that explains
  why the base classes exist at all.
- **§29 fragmented headers.** Two candidates: `### Preventing Direct
  Creation` opening with "To disallow direct access to the classes," and
  `## Builder` opening with "The remaining creational pattern ... is
  *Builder*." Neither is a rhetorical warm-up; each carries the technique
  or the definition. You declined this pattern in 46 and accepted it in
  47, so I did not force a third precedent.
- **Line 177**, "The privacy has a price." A single short emphatic
  sentence, which the skill explicitly says not to flag on its own.
- **Line 597**, "The deep copy is the part that matters." A mild cleft,
  but it names the specific thing the next two sentences prove.
- **Line 242's "ever"** ("nothing ever imported the module that defines
  it") and **line 197's "never"** ("the factory never needs editing").
  Both on the avoid-if-possible list; both are genuine absolutes about a
  whole program run rather than intensifiers.
- **Line 373's "already"** ("Because classes are already first-class
  objects"). Marks a real prior state, established at line 190.
- **Rule-of-three lists**, line 378 ("pooling, caching, or consulting
  external configuration") and line 785 ("creating rooms, connecting
  doors, then placing the robot"). Real enumerations; the second one is
  the three stages the listing actually has.
- **Line 492**, "with no base class to derive from while still type
  checking." The preposition's object precedes it inside the same clause
  and the sentence does not end there, so this is not the stranding your
  rule targets.
- **Every pattern-name italic** (*factory*, *generator*, *Factory
  Method*, *Abstract Factory*, *Prototype*, *Builder*, *telescoping
  constructor*, *initial conditions*, *state change*, *Protocol*).
  All are first-use introductions or pattern names, which the italics
  rule allows.

## Scan coverage

The word-level half of the skill was nearly clean: two §7 hits
(`valuable` at 377, `intricacies` at 363, the second in legacy prose) and
nothing else. No curly quotes, no emoji, no boldface-header lists, no
promotional or sycophantic language, no filler phrases, no hedging
stacks, no knowledge-cutoff disclaimers, no collaborative artifacts, no
false ranges, no elegant variation, no copula avoidance, no predicate
hyphenation, no generic upbeat conclusion, and no em dashes to consider.
Everything else above is structural: person, announcements, staccato
pairs, emphasis italics, echoes, stranded prepositions.
