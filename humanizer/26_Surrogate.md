[[Reviewed]]
# Humanizer candidates: Chapters/26_Surrogate.md

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

This chapter is clean. Nothing from the AI-vocabulary list, no curly
quotes, no boldface lists, no manufactured drama, no fragmented
headers, no signposting. What surfaced is small and mechanical: one
person slip, one stranded preposition, and two emphasis italics.
The single most important finding is the lone "If we implement" at
line 28, the only first-person slip in a second-person book.
Two Tier B calls are genuinely arguable and lean toward decline.

## Tier A

### A1 — line 28 — person ("we" to "you")

The chapter is second person throughout. This is the only "we" in
the prose (the other "We" hits are Monty Python lyrics inside a
code listing and are off limits).

CURRENT
```text
If we implement *Proxy* by following the above diagram, it looks like this:
```

PROPOSED
```text
If you implement *Proxy* by following the above diagram, it looks like this:
```

### A2 — line 59 — stranded preposition

"the class it forwards method calls to," strands "to" from its
fronted object. Fronting the preposition reads cleaner and matches
the CLAUDE.md rule.

CURRENT
```text
As long as `Proxy` is somehow "speaking for" the class it forwards method calls to,
it satisfies the basic idea
(this statement is at odds with the definition for Proxy in *GoF Design Patterns*).
```

PROPOSED
```text
As long as `Proxy` is somehow "speaking for" the class to which it forwards method calls,
it satisfies the basic idea
(this statement is at odds with the definition for Proxy in *GoF Design Patterns*).
```

### A3 — line 171 — emphasis italics

`*type*` italicizes an already-established word for emphasis, not to
introduce it. The chapter's own italics convention (pattern names,
first-use terms) is otherwise consistent, which makes this one stand out.

CURRENT
```text
Python looks up dunders like `__len__()` and `__str__()` on the proxy's *type*,
```

PROPOSED
```text
Python looks up dunders like `__len__()` and `__str__()` on the proxy's type,
```

### A4 — line 364 — emphasis italics

Same pattern: `*every*` is emphasis, not a first-use term. Contrast
with line 361's `*fallback*`, which correctly italicizes on first use
and drops the italics on its second mention at line 369 ("The
fallback hook") — that one is done right and stays as is.

CURRENT
```text
`__getattribute__()` intercepts *every* attribute access,
```

PROPOSED
```text
`__getattribute__()` intercepts every attribute access,
```

## Tier B

### B1 — line 302 — passive construction, echoes line 18

"is in the problems that are solved" is passive where an active verb
is available, and it echoes "the difference between *Proxy* and
*State* is..." from line 18 almost word for word. Could be an
intentional bookend (opens the distinction, closes it at the
chapter's end) rather than a slip. I lean toward applying the small
active-voice fix and leaving the echo alone, since the echo reads as
a deliberate callback.

CURRENT
```text
The difference between *Proxy* and *State* is in the problems that are solved.
```

PROPOSED
```text
The difference between *Proxy* and *State* is in the problem each one solves.
```

### B2 — broken parallel in the GoF proxy-use list

Items 1 and 2 open with "This + verb." Item 3 switches to a
subjectless "Used when...", and item 4 switches again to an
infinitive "To add actions...". Restoring "This" evens the rhythm.
Genuinely arguable: the list may be deliberately varied to avoid a
mechanical four-in-a-row, and it stays close to how GoF's own
categories are usually phrased. Delete individual rows you want left
alone.

**line 312**

CURRENT
```text
3.  *Protection proxy*.
    Used when you don't want the client programmer to have full access to the proxied object.
```

PROPOSED
```text
3.  *Protection proxy*.
    This is used when you don't want the client programmer to have full access to the proxied object.
```

## Housekeeping

1. Line 61: `Proxy` is not italicized inside the parenthetical
   `(this statement is at odds with the definition for Proxy in
   *GoF Design Patterns*)`, unlike every other prose reference to the
   *Proxy* pattern name in this chapter. A formatting inconsistency,
   not a wording change.
2. No Semantic Line Break drift: `uv run python tools/reflow_prose.py
   --diff Chapters/26_Surrogate.md` reports 0 paragraphs changed.
3. No double-blank-line-before-heading drift: every heading in this
   chapter (`## Proxy`, `## State`, `## Exercises`) sits behind a
   single blank line, consistently.
4. No `[[ ]]` draft notes and no spaced ` -- ` anywhere in the file.

## Considered and not flagged

- Italicized pattern names (*Proxy*, *State*, *GoF Design Patterns*,
  *Remote proxy*, *Virtual proxy*, *Protection proxy*,
  *Smart reference*, *Surrogate*, *copy-on-write*) — confirmed as a
  book-wide convention by checking sibling pattern chapters
  (27_Factory, 30_Observer, 33_Visitor, 25_Template_Method, etc.),
  not an emphasis-italics tell.
- `*fallback*` at line 361 — legitimate first-use term introduction;
  the second mention at line 369 ("The fallback hook") correctly
  drops the italics, so the rule is already applied correctly here.
- "The beauty of using `__getattr__()` is that `Proxy2` is completely
  generic" (line 167) — this is the author's long-standing signature
  phrasing across the "Thinking in ___" series, not an AI aphorism
  formula.
- The four-item GoF proxy-use list (lines 305-317) as a whole — not a
  manufactured "rule of three." It's a direct, sourced citation of
  GoF's own taxonomy, and there are four items, not three. (The
  internal parallel-structure question is handled separately in B2.)
- "only" (seven hits) — each one is restrictive and precise about
  actual runtime behavior (e.g. "intercepts only the lookups not
  found," "counts only callable accesses"), not filler.
- "itself" at line 366 ("calls itself forever") — reflexive and
  load-bearing per the CLAUDE.md exception, left alone.
- The "We're Knights of the Round Table" / "We dance..." lines
  (251-274) — quoted Monty Python lyrics inside a code listing, not
  authorial first person, and off limits as code regardless.

## Scan coverage

Clean on: §7 AI-vocabulary word list, curly quotes, boldface
inline-header lists, emojis, sycophantic/servile tone,
knowledge-cutoff disclaimers and speculative gap-filling,
collaborative-communication artifacts, rule-of-three padding, false
ranges, excessive hedging, aphorism formulas, manufactured-punchline
staccato, fragmented headers, diff-anchored writing, and
signposting/announcements. Listing comments (the `#` prose inside
each ```python block) were checked individually and hold no watch-list
words, no "we," and nothing else worth a Housekeeping note. Findings
that did surface were structural: person consistency and emphasis
italics, both direct hits against named precedents from chapters 46
and 47.
