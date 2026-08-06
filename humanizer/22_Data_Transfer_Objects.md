[[Reviewed]]
# Humanizer candidates: Chapters/22_Data_Transfer_Objects.md

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

This is a short, plain chapter and it is clean.
No em dashes, no first-person plural, no curly quotes, no boldface,
no AI-vocabulary hits, no promotional or hedging language anywhere in it.
The one real finding is a single participle tail ("producing a mutable
record") of the kind chapters 46 and 47 already flagged and applied.
A second item, a one-line callback right after a heading, is a
per-instance judgment call rather than a clear defect, so it sits in
Tier B. Nothing else in the chapter warranted a block.

## Tier A

### A1 — line 69-70 — participle tail

"producing a mutable record" tacks a present-participle clause onto the
sentence the way §3 describes. Coordinating it with "generates" as a
second finite verb reads the same and drops the tail.

CURRENT
```text
A `@dataclass` generates `__init__()`, `__repr__()`,
and equality from those declarations, producing a mutable record:
```

PROPOSED
```text
A `@dataclass` generates `__init__()`, `__repr__()`,
and equality from those declarations, and produces a mutable record:
```

## Tier B

### B1 — line 127-130 — fragmented header

The heading is followed by a one-line callback before the real content
starts, the §29 shape. Chapter 46 declined this pattern, 47 accepted
it, so it is genuinely a coin flip. Here the callback line does
connect back to the chapter's opening promise ("The most typical use
is for function return values," line 4), which is a point in its
favor; without it the section drops straight into the example with no
bridge. I'd lean toward keeping it, so this is here mainly so the call
is on record.

CURRENT
```text
## Returning Multiple Values

This is the return-value use promised at the start.
Here, a function computes two results, returned in a `NamedTuple`:
```

PROPOSED
```text
## Returning Multiple Values

Here, a function computes two results, returned in a `NamedTuple`:
```

### B2 — line 5 — passive voice

"Tuples and dictionaries are often used for that" hides the actor,
the §13 pattern (advisory here, not absolute). An active rewrite fits
the book's second-person voice, but the passive also isn't wrong: it
keeps tuples and dictionaries as the subject, which is what the rest
of the paragraph is about. I'd understand leaving this alone.

CURRENT
```text
Tuples and dictionaries are often used for that, but both rely on indexing.
```

PROPOSED
```text
You often use tuples and dictionaries for that, but both rely on indexing.
```

## Housekeeping

None found. Every heading has exactly one blank line before it, no
line shows Semantic Line Break drift beyond what `reflow_prose.py`'s
greedy packing already explains (the two 118-character exercise lines
have no earlier top-level comma/semicolon/colon to break at, so they
are not drift), no `[[ ]]` draft note, and no spaced ` -- `.

## Considered and not flagged

- **"documents itself at each call site" (line 153).** `itself` is the
  grammatical object of "documents," not an emphasis flourish; the
  sentence doesn't parse without it.
- **"only" (lines 34, 35, 123, 206).** Every instance is a genuine
  restriction ("accepts only keyword arguments," "only to show,"
  "only its own kind"), not filler.
- **Three-item lists (lines 120-122, 203-204).** Both name the actual
  three constructs the chapter covers (`SimpleNamespace`/`@dataclass`/
  `NamedTuple`, and the three reasons to choose `NamedTuple`). Real
  taxonomy, not a rule-of-three pad.
- **"This refines the selection rule." (line 202).** Short, but it
  points at a concrete earlier rule (the "Use X for Y..." guidance at
  line 120) rather than gesturing at nothing.
- **"knowledge... knowledge" (lines 151-152).** Deliberate repetition
  building a contrast ("owns the knowledge... knowledge the code no
  longer states anywhere"), not an accidental AI echo.
- **Italics on *Messenger* / *Data Transfer Object* (line 3).** Both
  are first-use term introductions, the one case italics is supposed
  to cover, and the only italics in the chapter.
- **Em dashes.** None appear anywhere in this chapter, so there was
  nothing to preserve or flag.

## Scan coverage

Zero hits on the §7 AI-vocabulary list, promotional language (§4),
vague attributions (§5), "Challenges" sections (§6), copula avoidance
(§8), negative parallelism and tailing negation (§9), false ranges
(§12), boldface (§15), inline-header lists (§16), emoji (§18), curly
quotes (§19), collaborative/chatbot artifacts (§20), knowledge-cutoff
disclaimers (§21), sycophantic tone (§22), filler phrases (§23),
hedging (§24), generic positive conclusions (§25), hyphen-pair misuse
(§26), persuasive-authority tropes (§27), signposting openers like
"let's" (§28), manufactured staccato (§31), aphorism formulas (§32),
and conversational rhetorical openers (§33). Person is clean throughout
(no "we"/"us"/"our"; the book's "you" is used consistently). Matches
the 46/47 precedent that word-level scanning is usually a dead end;
the only real yield here was structural (§3 and, arguably, §29).
