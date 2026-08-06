[[Reviewed]]
# Humanizer candidates: Chapters/38_Simulation.md

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

The chapter is in good shape. The word-level half of the scan found nothing:
no §7 AI vocabulary, no curly quotes, no emoji, no boldface, no promotional
language, no hedging, no filler phrases, and no em dashes to preserve or flag.
Two hard rule violations exist: `near-miss` at line 738, which is on the
don't-use list, and a stranded preposition at line 503 ("what it is for" in
another shape). The largest finding is a cluster in the Chladni half: a §33
rhetorical-question opener with a pause-and-reveal fragment at 1034, two
flourishes ("with no window in sight", "lets the numbers tell the story"),
and a staccato run of four one-clause sentences at 868. Also two
first-person-plural slips in a second-person book.

## Tier A

### A1 — line 738 — banned word: `near-miss`

`near-miss` is on the don't-use tier of the watch list. The sentence is
naming the mistake, so say that.

CURRENT
```text
The near-miss is `zip(teleports, teleports)`,
```

PROPOSED
```text
The mistake to avoid is `zip(teleports, teleports)`,
```

### A2 — lines 318, 867 — first person plural

The book is second person. Delete individual rows you want left alone.
Line 867's rewrite also removes a "happen."

**line 318**

CURRENT
```text
We can create a GUI demonstration using the same model.
```

PROPOSED
```text
You can create a GUI demonstration using the same model.
```

**line 867**

CURRENT
```text
In each case we knew what should happen and ran the program to check it.
```

PROPOSED
```text
In each case you knew the outcome in advance and ran the program to confirm it.
```

### A3 — line 503 — stranded preposition

"which is the only thing `Room` is for" strands "for" after moving its
object, the shape `CLAUDE.md` names with "what it is for."

CURRENT
```text
It is `True` only for a type checker reading the file,
which is the only thing `Room` is for.
```

PROPOSED
```text
It is `True` only for a type checker reading the file,
which `Room`'s sole purpose here.
```

### A4 — lines 399-400 — broken parallel

Three items describing what each occupant does, but the middle one flips to
the passive with the food as a patient rather than an actor. Keeping "eaten"
in a finite verb phrase restores the parallel without losing the image.

CURRENT
```text
A wall keeps the robot where it is, food is eaten and the robot moves in,
a teleport returns a distant room.
```

PROPOSED
```text
A wall keeps the robot where it is, food gets eaten and lets the robot in,
a teleport returns a distant room.
```

### A5 — lines 1034-1036 — §33 rhetorical opener, §13 subjectless fragment

A question, then a verbless fragment answering it, then the real answer.
The theatrical pause-and-reveal is the tell; the claim survives intact.

CURRENT
```text
What can a test assert about a million random kicks?
Not where any particular grain ends up.
It pins down the aggregate instead.
```

PROPOSED
```text
A test cannot guess where a particular grain lands after a million random kicks.
It pins down the aggregate instead.
```

### A6 — lines 746-747 — flourish, and a cross-section echo

"with no window in sight" is decoration on a sentence that already says the
thing. Swapping "pin down" for "check" also clears the echo with line 1036,
where "pins down" does real work.

CURRENT
```text
The maze rendering, `show_maze()`, returns a string,
so the model's correctness is something a test can pin down with no window in sight.
```

PROPOSED
```text
The maze rendering, `show_maze()`, returns a string,
so a test can check the model's correctness without opening a window.
```

### A7 — line 969 — flourish

"lets the numbers tell the story" is a stock phrase standing in for what the
demo does.

CURRENT
```text
The demo shakes the plate 1200 times and lets the numbers tell the story:
```

PROPOSED
```text
The demo shakes the plate 1200 times and displays the agitation as it happens:
```

### A8 — line 740 — §31 manufactured punchline

The paragraph has already explained the mechanism twice, once positively and
once through the mistake. This third pass adds no information and "the whole
trick" is the punchline shape. Cut the line.

CURRENT
```text
which walks two independent passes over the list and pairs every room with itself.
One iterator, referenced twice, is the whole trick.
The `assert isinstance` lines that follow are for the type checker as much as for safety:
```

PROPOSED
```text
which walks two independent passes over the list and pairs every room with itself.
The `assert isinstance` lines that follow are for the type checker as much as for safety:
```

## Tier B

### B1 — line 14 — the "nothing else" family

"and little else" is the same construction as "and nothing else." The next two
sentences spell the exclusion out, which is the rule's giveaway.
I lean toward applying.

CURRENT
```text
A *maze* knows its own layout and little else.
```

PROPOSED
```text
A *maze* knows its own layout.
```

### B3 — lines 510-512 — staccato run with stacked tailing negations

Two "not X" tails back to back, then a third sentence restarting on the same
subject. Merging the second into the third also clears the
declares/declaration echo. I lean toward applying, though "not a placeholder"
is doing real work against a reader who would read `room: Room` as one.

CURRENT
```text
That line stores nothing, not even `None`.
It is a declaration, not a placeholder.
It declares to the type checker that a `Room` will be there,
```

PROPOSED
```text
That line stores nothing, not even `None`.
It is a declaration: it tells the type checker that a `Room` will be there,
```

### B4 — lines 736-737 — §3 participle tail

"with ... lining the partners up beforehand" hangs a participle off an already
long sentence. As its own sentence the fact reads straight. I lean toward
applying.

CURRENT
```text
so each pass consumes two rooms: the first and second `a`, then the two `b`s,
with the sort by target letter lining the partners up beforehand.
```

PROPOSED
```text
so each pass consumes two rooms: the first and second `a`, then the two `b`s.
The sort by target letter lines those partners up beforehand.
```

### B5 — lines 868-871 — §31 staccato run of four

Four one-clause sentences in a row, each landing like a closer. The content is
two claims. I lean toward applying.

CURRENT
```text
This final example is different.
Its result appears in no line of its code.
That is simulation's other purpose.
It discovers behavior instead of confirming it.
```

PROPOSED
```text
This final example is different.
Its result appears in no line of its code.
That is simulation's other purpose, to discover behavior instead of confirming it.
```

### B6 — lines 895-897 — three short negatives, nothing/Nothing echo

The three-beat build is deliberate and the third line is the payoff, so I am
not asking you to flatten it. The only real defect is "nothing." at the end of
one sentence and "Nothing" at the start of the next. Merging the first two
fixes that and keeps the payoff standing alone. Lean: mild apply.

CURRENT
```text
Grains never look at each other.
They remember nothing.
Nothing in the code knows the pattern exists.
```

PROPOSED
```text
Grains never look at each other and remember nothing.
Nothing in the code knows the pattern exists.
```

### B7 — lines 1029-1030 — ambiguous pronouns in a §9 negative parallelism

"It is the engine that produces it" uses "it" twice with different referents:
the randomness, then the order. Merging fixes the referents and drops the
negative parallelism. If you want to keep the two-sentence shape, replacing
only the second "it" with "that order" is the minimal fix.

CURRENT
```text
The randomness is not fighting the order.
It is the engine that produces it.
```

PROPOSED
```text
The randomness is not fighting the order but producing it.
```

### B8 — line 1121 — §11 synonym cycling, plus a participle tail

Two adjacent sentences describe sibling `itertools` functions doing the same
thing, one with "constructs" and one with "creates." Matching the verbs also
lets the participle tail go. Lean: apply.

CURRENT
```text
`itertools.count()` creates an infinite iterator yielding evenly spaced numerical values.
```

PROPOSED
```text
`itertools.count()` constructs an infinite iterator of evenly spaced numbers.
```

### B9 — line 1129 — "never" three times in four lines

Lines 1128, 1129, and 1131 each carry a "never." This one is also the hardest
to parse, since "structure the agents never encode" drops the relative
pronoun. Changing it clears both. Lean: apply.

CURRENT
```text
Even so, structure the agents never encode appears in the aggregate.
```

PROPOSED
```text
Even so, structure that no agent encodes appears in the aggregate.
```

### B10 — lines 34, 1038 — "ever"

Watch-list word in both places, and "no two rats" and "no kick" already carry
the universal. Delete individual rows you want left alone. Lean: apply both.

**line 34**

CURRENT
```text
This way, no two rats ever cover the same ground.
```

PROPOSED
```text
This way, no two rats cover the same ground.
```

**line 1038**

CURRENT
```text
and no kick may ever throw a grain off the plate.
```

PROPOSED
```text
and no kick may throw a grain off the plate.
```

### B11 — lines 516, 1025 — "happen"

Watch-list word. Delete individual rows you want left alone.
Line 1025's "happens to" is meant to say "by chance," which "random wander"
already says. Lean: apply both, 1025 more strongly than 516.

**line 516**

CURRENT
```text
and the builder runs first so that never happens.
```

PROPOSED
```text
and the builder runs first, so nothing reads it earlier.
```

**line 1025**

CURRENT
```text
A loud region flings its grains around until a random wander happens to cross a quiet line,
```

PROPOSED
```text
A loud region flings its grains around until a random wander crosses a quiet line,
```

### B12 — line 322 — word echo

"turning green in turn." Small, but it is an echo inside one clause.
Lean: mild apply.

CURRENT
```text
then each claimed cell turning green in turn,
```

PROPOSED
```text
then each claimed cell turning green one after another,
```

## Housekeeping

1. **Semantic Line Break drift**, concentrated in the exercises. Lines 1152,
   1168, and 1173 each run well past a top-level clause boundary (1168 is 155
   characters), and 1158 is close behind. A few prose lines are also long
   without breaking: 281, 1120, 1125. `make reflow CH=38` fixes these; no gate
   catches them. Re-check line numbers after applying any edits above.
2. **Line 1120, "from the source item."** `itertools.cycle()` takes an
   iterable, and the sentence before it says so. This reads like a slip for
   "iterable" or just "source." Not a humanizer finding, so it is here rather
   than in a block, but it looks wrong.
3. **Clean structurally.** No double blank lines anywhere, no `[[ ]]` draft
   notes, no spaced ` -- `, and no em dashes at all in the chapter, so §14 had
   nothing to preserve and nothing to flag.
4. **Line 199 is a code comment containing "we"** ("while we wait"). It sits
   inside a fenced `python` block, so it is out of scope for this pass. If you
   want the book fully second-person down to the comments, that one needs a
   listing edit plus `make sync`, not a prose edit.

## Considered and not flagged

- **Line 220, "so the file is the maze."** This is the already-swept form of
  the "nothing else" rule from `CLAUDE.md`, which cites this exact sentence.
  Left alone.
- **Line 1070, "the field on which they sit."** Likewise the already-fixed
  form of the stranded-preposition rule, which cites "the field they sit on"
  as the defect. Left alone.
- **Line 883-885, `### The Model` followed by "The model needs almost
  nothing."** A §29 near-miss. It makes a claim rather than restating the
  heading, and it opens a paragraph rather than standing alone. §29 is a
  per-instance call by the 46/47 precedent, and this instance does not earn a
  block.
- **Line 575-576, `### Building the Maze in Stages` followed by "assembles the
  maze in three stages."** Same call, and the sentence goes on to name the
  three stages, so it is delivering content.
- **Line 153, "`claim()` is the heart of the program."** Reads near §27's
  "heart of the matter," but it names one specific method and the paragraph
  then proves the claim. Ordinary idiom, not ceremony.
- **Line 733, "a small idiom worth decoding."** Mild §28 announcement, but
  flagging the difficulty for the reader earns its place before a genuinely
  tricky two lines.
- **Line 1132-1135**, "The rats cooperate through a blackboard. / The robot
  follows a script. / The grains know nothing." A rule of three and a staccato
  run, kept: these are the chapter's three actual examples in order, and the
  next sentence depends on the ranking.
- **Lines 1138-1139**, "When behavior emerges, reading the code is not enough.
  / Run it." A manufactured closer, kept. It is the chapter's last line and the
  imperative is the argument, matching the call made on 47's closing lines.
- **Line 881**, "a different spot ... a different mode ... a different figure."
  Triple echo, but the repetition is the parallel and each "different" points
  at a different thing.
- **Line 1069**, "The order was never a property of the grains." "never" is on
  the avoid-if-possible tier, but here it means "at no point, including while
  the figure formed," which is the claim.
- **Line 525**, "using the class hierarchy as the registry." A §3 participle
  tail in shape, but it names the actual mechanism instead of adding depth.
- **Line 1068**, "It bursts back into chaos, mixes, and condenses into a
  different figure." Rule of three, but a real sequence in that order.
- **Lines 1027-1028**, "Noise can carry a grain into a quiet place. / It cannot
  carry the grain back out." A negative parallelism, kept: the asymmetry is the
  mechanism the whole section explains.
- **"only" nine times** (lines 18, 42, 146, 502, 503, 509, 805, 1127, 1150).
  Each draws a real contrast: line 42 against "does not import," 502 against
  runtime, 805 against the rest of the program. B2 removes one and A3 the
  clumsiest.
- **Line 515, "raises `AttributeError`."** The `CLAUDE.md` example uses an
  article ("raises a `NameError`"), but the rule's requirement is an object,
  and the specific exception is named. Not flagged.
- **Italics.** *maze*, *blackboard*, *rat*, *nodal lines*, *emergence*, and the
  book title *Atomic Kotlin*. Every one is a first-use term introduction or a
  title. No emphasis italics in the chapter.
- **Signs of human writing left untouched.** The 1787 Chladni anecdote, the
  Jeremy Meyer credit, "food eaten and all," and the *Atomic Kotlin*
  attribution are the specific, hard-to-fabricate details the skill says to
  preserve.

## Scan coverage

The word-level half of the skill found nothing. No hits on the §7
AI-vocabulary list (the only matches were `highlightthickness` inside three
`tkinter` listings), no curly quotes, no emoji, no boldface at all (every `**`
match is a maze row inside a fence), no inline-header vertical lists, no
promotional language (§4), no vague attributions (§5), no
"Challenges and Future Prospects" section (§6), no copula avoidance (§8), no
rule-of-three padding beyond the two real enumerations noted above, no false
ranges (§12), no collaborative artifacts (§20), no knowledge-cutoff
disclaimers (§21), no sycophancy (§22), no filler phrases (§23), no hedging
stacks (§24), no generic upbeat conclusion (§25), no hyphenated-pair overuse
(§26, and the technical compounds present are all attributive), and no
diff-anchored writing (§30). Everything above is structural or watch-list:
§31 staccato, §33 rhetorical opener, §3 participle tails, §9 negative
parallelism, §11 synonym cycling, person, and the `CLAUDE.md` word list.
