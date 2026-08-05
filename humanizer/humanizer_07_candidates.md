[[Reviewed]]
# Humanizer candidates: Chapters/07_Classes.md

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

The chapter is close to clean. No word-level AI vocabulary, no rule-of-three
padding, no fragmented headers, no curly quotes, no stray blank lines. The
one real thread is person: two walkthrough sentences slip into "we" where
the rest of the chapter addresses "you," plus one italic used for emphasis
rather than to introduce a term. Everything else below is minor and low
confidence.

## Tier A

### A1 — lines 109, 392 — person: walkthrough "we"

Both sentences narrate what a code example does using "we," while the
chapter otherwise speaks to "you" or describes the code impersonally.

**line 109**

CURRENT
```text
Here, we import and subclass `Simple`, from the `simple_class` module:
```

PROPOSED
```text
This example imports and subclasses `Simple`, from the `simple_class` module:
```

**line 392**

CURRENT
```text
Here we compose that method into a class:
```

PROPOSED
```text
This example composes that method into a class:
```

Delete individual rows you want left alone.

### A2 — line 41 — italics used for emphasis, not a new term

`*define*` isn't a term being introduced; it's the ordinary verb, italicized
for emphasis. Every other italic in the chapter (*initializer*, *constructor*,
*setter*, *lazily initialized*) marks a first-use term, so this one stands out.

CURRENT
```text
When you *define* a method you must explicitly specify the reference as the first parameter.
```

PROPOSED
```text
When you define a method you must explicitly specify the reference as the first parameter.
```

### A3 — line 209 — watch-list word "actually"

CURRENT
```text
If `Derived.show` does not actually override a method in a base class,
```

PROPOSED
```text
If `Derived.show` does not override a method in a base class,
```

## Tier B

### B1 — lines 53, 56 — person: "we" describing the book's own convention

Different flavor from A1: this "we" is the author talking about a choice
made in writing the book (calling `__init__()` "the constructor"), close to
the acknowledgment-style exception kept in chapter 47. Could go either way.
I lean toward converting, since the surrounding chapter is otherwise
consistently "you," but this is the more defensible "we" in the chapter.

**line 53**

CURRENT
```text
The `__new__()` method is the *constructor*, but we hardly ever use that.
```

PROPOSED
```text
The `__new__()` method is the *constructor*, which you rarely use.
```

**line 56**

CURRENT
```text
We follow that practice in this book.
```

PROPOSED
```text
This book follows that practice.
```

Delete individual rows you want left alone.

### B2 — line 246 — italics on "read-only"

Arguable whether this is a term being introduced (paired later with
"setter," contrasted with a writable property) or just emphasis on an
ordinary compound adjective. I lean toward dropping the italics, since
"read-only" doesn't recur as vocabulary the way "setter" and "lazily
initialized" do.

CURRENT
```text
The default `@property` is *read-only*.
```

PROPOSED
```text
The default `@property` is read-only.
```

## Housekeeping

None found. Heading blank-line spacing is consistent throughout, no
`[[ ]]` draft notes, no spaced ` -- `, no em-dash issues (all `---` and
none found needing attention), and Semantic Line Breaks look intact.

## Considered and not flagged

- **"## Composing Methods with `import`" opening sentence** ("You can
  compose methods into a class using `import`.") echoes the heading, which
  looks like it could be a fragmented header (§29). Declined: the sentence
  states the actual mechanism rather than restating the heading as inert
  filler, and the second sentence in the same paragraph adds real content
  immediately, unlike the classic pattern's isolated one-liner.
- **"All it cares about is that it can call `show()` on `obj`, with no
  other type requirements"** (line 175-176) has the shape of the "nothing
  else" family but doesn't use any of its trigger phrasing, and the
  exclusion it states is real and load-bearing for the point about dynamic
  typing. Left alone.
- **"Cache only what cannot change."** (line 321) is a short declarative
  closer, but it's a single instance, not a run of staccato fragments, and
  it's genuine advice rather than a manufactured punchline. Not flagged
  (§31).
- **`raises an AttributeError` / `still raises the setter's ValueError`**
  (lines 248, 424) both name the exception, satisfying the "raise needs an
  object" rule already. No finding.
- **"plain attribute" / "plain method" / "plain `@property`" / "plain
  module-level function"** (lines 221, 229, 283, 320, 415) all pair "plain"
  against something more elaborate (computed property, class with a
  property, cached_property, composition/mixins). Each earns its place per
  the contrast test; none flagged.
- **Word-level AI vocabulary (§1-§7, §26 hyphen pairs)**: none found.
  No "testament," "underscore," "landscape," "delve," "crucial," "boasts,"
  "serves as," rule-of-three lists, or false ranges. Consistent with the
  chapters 46/47 finding that this scan is usually a dead end here.

## Scan coverage

Clean on: undue-significance language (§1-§2), participle-tail padding
(§3), promotional language (§4), vague attribution (§5), "Challenges"
sections (§6), AI vocabulary (§7), copula avoidance (§8), negative
parallelism and tailing negation (§9), rule of three (§10), elegant
variation (§11), false ranges (§12), boldface/inline-header lists
(§15-§16), curly quotes (§19), chatbot correspondence artifacts (§20-§22),
filler phrases and hedging (§23-§25), diff-anchored writing (§30), aphorism
formulas (§32), and conversational rhetorical openers (§33). No `[[ ]]`
notes, no spaced ` -- `, no heading-spacing drift. The only substantive
findings are person (A1, B1) and italics discipline (A2, B2), plus one
watch-list word (A3).
