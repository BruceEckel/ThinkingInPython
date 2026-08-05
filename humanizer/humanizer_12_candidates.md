[[Reviewed]]
# Humanizer candidates: Chapters/12_Data_Classes_as_Types.md

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

The word-level half of the scan came up empty again: no em dashes anywhere in
the chapter, no curly quotes, no emoji, no boldface at all, no §7 AI vocabulary
beyond two stray "actually"s, no promotional language, no hedging, no rule-of-three
padding. All five italics introduce a term on first use.

The largest finding is person: eleven lines carry an editorial "we," clustered at
the chapter opening and at the head of `## Comparing Ordinary Classes and Data
Classes`, where the "we" also wraps a two-sentence announcement of what the
section is about to do. After that it is small stuff: three watch-list words from
`CLAUDE.md` ("in the first place," "buys," "at all"), one "is what makes" cleft,
two announcement sentences, and one word echo inside a single clause.

One thing needs your ruling rather than an edit: the bare-annotation "promise"
metaphor. See Housekeeping 3.

## Tier A

### A1 — lines 216-217 — §28 announcement

"Notice the last two lines" points at the listing and then says the thing.
Merging drops the pointer and keeps the claim.

CURRENT
```text
Notice the last two lines.
A data class is mutable, so `m.name = "bar"` works.
```

PROPOSED
```text
The last two lines show that a data class is mutable, so `m.name = "bar"` works.
```

### A2 — line 341 — "in the first place"

On the don't-use list in `CLAUDE.md`. Cutting it also cuts the doubled negative:
`never` plus `in the first place` says one thing twice.

CURRENT
```text
An illegal value can never produce a `Stars` in the first place.
```

PROPOSED
```text
An illegal value never produces a `Stars`.
```

### A3 — line 621 — "buys" plus litotes

"buy" is on the avoid-if-possible list, and "turns out not to be nothing" is a
double negative doing the work of one adjective.

CURRENT
```text
It buys one thing, which turns out not to be nothing:
```

PROPOSED
```text
It gains one small but real thing:
```

### A4 — line 894 — "is what makes"

The giveaway case from `CLAUDE.md`: a verb sits right after the cleft, so the
construction only delays it.

CURRENT
```text
A validated type stays validated across a replacement,
which is what makes "transform one legal value into a new legal value" a safe thing to say.
```

PROPOSED
```text
A validated type stays validated across a replacement,
which makes "transform one legal value into a new legal value" a safe thing to say.
```

### A5 — line 931 — "at all"

Avoid-if-possible list, and "no separate fields" already excludes everything.

CURRENT
```text
`Color` stores no separate fields at all,
```

PROPOSED
```text
`Color` stores no separate fields,
```

### A6 — line 939 — §28 announcement

Announces that a rule is coming and comments on its length before giving it.
The two sentences that follow are the rule.

Note: this block and B6 are fragments of the same two lines but do not overlap,
so you can take either or both. Apply this one first if you take both.

CURRENT
```text
The rule for deciding is short.
Define `__replace__()` when your type is immutable
```

PROPOSED
```text
Define `__replace__()` when your type is immutable
```

### A7 — lines 1051-1053 — §28 announcement plus §29 restatement

Line 1051 restates the heading it sits under, line 1052 announces a second thing
the section will do, and line 1053 is the real opener. Folding 1052's content into
1053 keeps the cross-reference and loses the warm-up. This also resolves two of
the "we" sites in A10, which is why they are not listed there.

CURRENT
```text
Now we can look at the differences between these two types of classes.
In addition, we can add some insight to [Class Attributes](09_Class_Attributes.md).
Four small classes make the differences concrete:
```

PROPOSED
```text
Four small classes make the differences concrete,
and add some insight to [Class Attributes](09_Class_Attributes.md):
```

### A8 — lines 1116-1117 — word echo in adjacent clauses

"class variables" twice in one sentence. The second is recoverable from the first.

CURRENT
```text
which turn them from bare annotations into class variables,
because the assignments allocate storage for those class variables:
```

PROPOSED
```text
which turn them from bare annotations into class variables,
because the assignments allocate storage:
```

### A9 — lines 1108, 1183, 1185, 1249 — filler intensifiers

Four sites, all in the `A`/`B`/`C`/`D` comparison section: two "actually" and two
"exactly," each on the watch list and each deletable without changing the meaning.
Delete individual rows you want left alone.

**line 1108**

CURRENT
```text
but nothing is actually stored anywhere until assigned in code.
```

PROPOSED
```text
but nothing is stored anywhere until assigned in code.
```

**line 1183**

CURRENT
```text
exactly as it was before.
```

PROPOSED
```text
as it was before.
```

**line 1185**

CURRENT
```text
when the generated `__init__()` actually runs.
```

PROPOSED
```text
when the generated `__init__()` runs.
```

**line 1249**

CURRENT
```text
so it is a bare annotation exactly like `x` and `s` were back in `A`:
```

PROPOSED
```text
so it is a bare annotation, as `x` and `s` were back in `A`:
```

### A10 — lines 7-10, 87, 155, 285-288, 450 — person consistency

The book is second person. Five sites, plus the two inside A7. The opening
paragraph is the one I'd expect you to argue about: its "we" is a claim about
programmers as a group, not an editorial stand-in for the reader, so the proposal
names the group once and then goes impersonal rather than switching to "you"
mid-paragraph. Delete individual rows you want left alone.

**lines 7-10**

CURRENT
```text
We have historically been bad at keeping objects inside that set.
We let code construct an object in an illegal state,
or we let later code mutate it into one,
and then we scatter checks everywhere to defend against the mess.
```

PROPOSED
```text
Programmers have historically been bad at keeping objects inside that set.
It's too easy to construct or mutate an object in an illegal state.
Checks to defend against the mess become scattered throughout your code.
```

**line 87**

CURRENT
```text
The `int` annotation says "any integer," which is not what we mean.
```

PROPOSED
```text
The `int` annotation says "any integer," which is not what you mean.
```

**line 155**

CURRENT
```text
We can see what `@dataclass` generates using `display_object()`,
```

PROPOSED
```text
You can see what `@dataclass` generates using `display_object()`,
```

**lines 285-288**

CURRENT
```text
If we make `Stars` a frozen data class,
we can guarantee that every `Stars` object is legal.
To validate it after the fields receive their values,
we define `__post_init__()`.
```

PROPOSED
```text
If you make `Stars` a frozen data class,
you can guarantee that every `Stars` object is legal.
To validate it after the fields receive their values,
define `__post_init__()`.
```

**line 450**

CURRENT
```text
As an example, we'll create a `BirthDate` containing a month, day, and year.
```

PROPOSED
```text
As an example, a `BirthDate` contains a month, day, and year.
```

## Tier B

### B1 — line 48 — manufactured significance

"matters more than it appears" tells the reader a point is important instead of
making it. The next four lines give two concrete reasons, so naming the count
does the same job with content. I lean toward applying this. It also removes an
echo with line 890, "The last case matters more than the convenience."

CURRENT
```text
`eq=False` turns off the generated `__eq__()`,
which matters more than it appears.
```

PROPOSED
```text
`eq=False` turns off the generated `__eq__()`,
for two reasons.
```

### B3 — lines 352-353 — "ensures", and an overclaim

"ensures" is in the §3 family, and it is also imprecise: the test does not ensure
the rejection, it confirms it. "every value outside the set" overstates a
four-value `parametrize`. I lean toward applying, mostly for the precision.

CURRENT
```text
Testing demonstrates that illegal values cannot exist.
`pytest.raises()` ensures that the constructor rejects every value outside the set:
```

PROPOSED
```text
Testing demonstrates that illegal values cannot exist.
`pytest.raises()` confirms that the constructor rejects values outside the set:
```

### B4 — line 676 — §29 fragmented header

The section opens by restating its own heading ("A `NamedTuple` Cannot Take That
Responsibility") and the sentence after it says the same thing concretely:
"nowhere to put one" is what "forbids overriding the methods that build an
instance" means. You declined this pattern in 46 and took it in 47, so it is your
call per instance. I lean toward applying here, because the restatement sits
between the heading and its own explanation.

CURRENT
```text
and it is tempting for a small type like `Stars`.
It cannot hold a guarantee, because it has nowhere to put one.
`typing.NamedTuple` forbids overriding the methods that build an instance,
```

PROPOSED
```text
and it is tempting for a small type like `Stars`.
`typing.NamedTuple` forbids overriding the methods that build an instance,
```

### B5 — lines 810-813 — section closes on its own opening

The first two sentences repeat lines 731-732 nearly word for word ("A data class
builds its `__init__` from its fields and assigns them directly. It does not call
the base class `__init__`."). Only the third sentence is new. The proposal leads
with the new part and compresses the repeat. I lean mildly toward applying;
declining is defensible, since three listings sit between the two statements.

CURRENT
```text
A data class assembles its `__init__` from a field list which includes its own fields plus any inherited from data class bases.
It builds the body by assigning those fields, not by chaining to the base.
It has no way to know what arguments a non-data-class base constructor expects,
so it does not call it.
```

PROPOSED
```text
A data class has no way to know what arguments a non-data-class base constructor expects,
so it does not call it.
Its field list covers its own fields plus any inherited from data class bases,
and it builds the body by assigning those fields.
```

### B6 — line 940 — "want"

"wants" is on the don't-use list, aimed at anthropomorphized functions and types.
This one is milder, since callers are closer to people than a function is, but
"need" says it without the metaphor. Weak lean toward applying. See the note in A6
about taking both.

CURRENT
```text
and callers will want a variant of it.
```

PROPOSED
```text
and callers will need variants of it.
```

## Housekeeping

1. **Typo at line 1171.** `` `C`s generated `__init__(...)` `` is missing an
   apostrophe. Line 1237 writes the same construction correctly as
   `` `show(D())`'s ``.
2. **Semantic Line Break drift.** Several prose lines run well past a sentence or
   clause boundary without breaking: 130, 176, 810, 991, 1039, 1171 are the worst,
   and 1171 is 128 characters. `make reflow CH=12` fixes these; no gate catches
   them. Line numbers shift if you apply anything above, so re-check rather than
   trusting this list.
3. **The "promise" metaphor is a book-wide question, not a chapter-12 edit.**
   `CLAUDE.md` says to avoid "promise" as a metaphor and names the annotation case
   directly: an annotation *declares*, *states*, or *requires*. The metaphor
   appears four times here (1105, 1109, 1184, 1250). I am not proposing an edit,
   because line 1104-1105 is an attributed quotation of chapter 09, which
   originates the wording at its own lines 109 and 124 ("a promise rather than a
   placeholder"). Rewriting 12 alone would leave the two chapters disagreeing
   about a metaphor one of them cites the other for. Either both change or neither
   does, and that is your call. If you want it changed, the fix is one term
   substituted consistently across both chapters, not a reword per site.
4. **Nothing else structural.** No double blank lines before any heading, no
   `[[ ]]` draft notes, no spaced ` -- `, no trailing whitespace runs.

## Considered and not flagged

Recorded so a later pass doesn't re-litigate these.

- **No em dashes in this chapter at all.** §14 had nothing to preserve and nothing
  to flag, same as 46 and 47.
- **All five italics introduce a term on first use**: *type* (3), *Design by
  Contract* (131), *data class* (140), *parse, don't validate* (335), *bare
  annotations* (1103). No emphasis italics anywhere, so the §-italics rule found
  nothing.
- **No boldface in the entire chapter.** §15 and §16 both vacuous here.
- **Lines 322-323**, "If you are holding a `Stars`, it is legal. / You know it
  without checking." A short declarative pair (§31). Kept: the second sentence is
  the chapter's actual claim, not drama, and it is the payoff the section built to.
- **Line 342**, "Illegal values are unrepresentable." A four-word closer, but it
  names the standard term for the idea the paragraph just built.
- **Line 860**, "It is what you do with any immutable value." Survives the
  `CLAUDE.md` deletion test: the words after "is what" are a clause that cannot
  attach without it, so cutting it breaks the sentence rather than tightening it.
- **Line 992**, "The type guards itself." "itself" is genuinely reflexive here,
  since the guard and the guarded thing are the same object.
- **Line 1078**, "`A` is the plain case." "plain" draws a real contrast with `B`'s
  defaults and `C`'s decorator, which is the exception the rule allows.
- **Line 715**, "because a factory function is advice rather than a gate." Reads as
  a §32 aphorism formula, but it states a checkable property and the test above it
  demonstrates exactly that.
- **Line 936**, "recover the constructor arguments, override the named ones,
  rebuild." Rule of three (§10), but it is the actual three-step algorithm, and the
  listing above performs all three.
- **Lines 818 and 1040**, "recursing into nested data classes" and "recursing
  through lists and nested objects." §3 participle tails, but each carries real
  behavior a reader needs, not fake depth.
- **Line 1240**, "`s`, declared `ClassVar[str]`, is a different story." Ordinary
  human idiom, and it earns its place as the pivot between two contrasted fields.
- **"never" x8** (14, 16, 337, 341, 653, 718, 1099, 1103, 1247). Avoid-if-possible
  list, but the chapter's subject is guarantees, and each one states one.
- **"only" x9** (178, 214, 270, 273, 320, 858, 1071, 1184, 1254). Every one is a
  real exclusion.
- **"already" x2** (327, 619). Both mark a genuine prior state.
- **"even" at 995.** Means "including when nested," not emphasis.
- **Line 1060**, "Each one is inspected with the same helper." Passive, but §13 is
  advisory in this repo and the four classes are the right subject to keep in focus.
- **Line 605**, "Every instance shares a single default object." Reads as a claim
  about behavior the language actually rejects, but it is describing the trap the
  rejection prevents, and the cross-reference to chapter 05 lands right there.

## Scan coverage

For a rerun: the word-level half of the skill is clean and does not need
re-running. No hits on §7 beyond the two "actually"s in A9, no curly quotes (§19),
no emoji (§18), no boldface (§15) and therefore no inline-header lists (§16), no
promotional language (§4), no vague attributions (§5), no filler phrases (§23), no
hedging stacks (§24), no sycophancy (§22), no collaborative artifacts (§20), no
knowledge-cutoff disclaimers (§21), no false ranges (§12), no copula avoidance
(§8), no negative parallelisms (§9), no synonym cycling (§11), no hyphenated-pair
overuse (§26), no persuasive-authority tropes (§27), no conversational openers
(§33), no generic upbeat conclusion (§25) — the chapter ends on exercises. Every
finding above is structural: person, announcements, one fragmented header, one
echo, and watch-list words from `CLAUDE.md` rather than from the skill.
