[[Reviewed]]
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
and Builder material. Almost every finding sat in the newer layer.
The largest single one was the `we`/`let's` cluster, five sites, three of
them in the legacy layer.
Two hard rules from `CLAUDE.md` were broken outright: "spellings" at line
488 (third-tier, don't use) and two stranded prepositions at 554 and 747.
No em dashes anywhere in the chapter, so §14 had nothing to protect.

All Tier A and Tier B edits have been applied.

## Housekeeping

1. **Semantic Line Break drift.** Several prose lines run well past a
   clause boundary without breaking. The worst were 88, 283, 362, 468,
   and 484 (before the edits above; line numbers have shifted), all over
   140 characters with internal comma or parenthetical breaks available.
   `make reflow CH=27` fixes it; no gate catches it.
2. **No double blank lines.** Heading spacing is uniform throughout.
3. **Line 6 uses the Unicode ellipsis character `…`**, not `...`:
   "without disturbing existing code … or so it seems." It is the only
   one in the chapter. Reported, not changed; it reads as deliberate
   typography for the trailing-off.
4. **No `[[ ]]` draft notes, no spaced ` -- `, and no em dashes at all.**
   §14 had nothing to preserve and nothing to flag.
5. **`## The Pythonic Factory: a Dictionary`** is the one heading with a
   lowercase interior word. No edit made, since the anchor is gated by
   `heading_links.py`; noted only in case you want to normalize it yourself.

## Not implemented, deliberately

- **The legacy `happens` clefts**, "It happens to be the creation
  of the type that matters here" and "It happens to be a string
  here," plus "The actual creation of shapes happens in
  `ShapeFactory.create_shape()`." All hit the `happen` watch list and are
  cleft constructions, but they are the inherited voice of this chapter's
  Java edition. Left untouched; say the word if you want these swept too.

## Considered and not flagged

- **"with not one but several factory methods."** A §9 negative
  parallelism, but the contrast with the single-method factory is real and
  the line is legacy prose.
- **"*GoF Design Patterns* emphasizes that..."** `emphasizing`
  is on the §7 list, but this has a real subject doing real emphasizing.
- **"(translated from the Java version)."** Reads like §30
  diff-anchored narration, but it records genuine provenance that explains
  why the base classes exist at all.
- **§29 fragmented headers.** Two candidates: `### Preventing Direct
  Creation` opening with "To disallow direct access to the classes," and
  `## Builder` opening with "The remaining creational pattern ... is
  *Builder*." Neither is a rhetorical warm-up; each carries the technique
  or the definition. Declined in 46, accepted in 47, so no third
  precedent was forced here.
- **"The privacy has a price."** A single short emphatic
  sentence, which the skill explicitly says not to flag on its own.
- **"The deep copy is the part that matters."** A mild cleft,
  but it names the specific thing the next two sentences prove.
- **"ever"** ("nothing ever imported the module that defines
  it") and **"never"** ("the factory never needs editing").
  Both on the avoid-if-possible list; both are genuine absolutes about a
  whole program run rather than intensifiers.
- **"already"** ("Because classes are already first-class
  objects"). Marks a real prior state, established earlier in the chapter.
- **Rule-of-three lists**, "pooling, caching, or consulting
  external configuration" and "creating rooms, connecting
  doors, then placing the robot." Real enumerations; the second one is
  the three stages the listing actually has.
- **"with no base class to derive from while still type
  checking."** The preposition's object precedes it inside the same clause
  and the sentence does not end there, so this is not the stranding the
  rule targets.
- **Every pattern-name italic** (*factory*, *generator*, *Factory
  Method*, *Abstract Factory*, *Prototype*, *Builder*, *telescoping
  constructor*, *initial conditions*, *state change*, *Protocol*).
  All are first-use introductions or pattern names, which the italics
  rule allows.

## Scan coverage

The word-level half of the skill was nearly clean: two §7 hits
(`valuable`, `intricacies`, the second in legacy prose, both since
addressed above) and nothing else. No curly quotes, no emoji, no
boldface-header lists, no promotional or sycophantic language, no filler
phrases, no hedging stacks, no knowledge-cutoff disclaimers, no
collaborative artifacts, no false ranges, no elegant variation, no copula
avoidance, no predicate hyphenation, no generic upbeat conclusion, and no
em dashes to consider. Everything else was structural: person,
announcements, staccato pairs, emphasis italics, echoes, stranded
prepositions.
