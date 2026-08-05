# Humanizer candidates: Chapters/35_Flyweight.md

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

Clean of the classic AI-vocabulary and structure tells (§7-§12, §15-§33
all came back empty or single-isolated). The real finds are two of
Bruce's own watch-list words landing in one sentence, a lone person
slip, and an emphasis italic. The largest single finding: line 39 uses
both "spelling" and "load-bearing" in the same sentence, both on the
CLAUDE.md "Don't use" tier. Five Tier A items, five Tier B, no
housekeeping. No `[[ ]]` notes, no em-dash issues, no Semantic Line
Break drift (checked with `tools/reflow_prose.py --diff`), no listing
comments beyond file-path headers.

## Tier A

### A1 — line 39 — banned words "spelling" / "load-bearing"

Both words are on CLAUDE.md's "Don't use" tier in the same sentence.
"Spelling" stands in for "the exact form of the call"; "load-bearing"
stands in for "this detail matters." The next three sentences already
spell out (sorry) the consequence of changing it, so the fix just
names the fact plainly.

CURRENT
```text
The `int("...")` spelling is load-bearing.
```

PROPOSED
```text
Calling `int("...")` on a string, not a literal, matters here.
```

### A2 — line 75 — first-person-plural slip

The book is second person throughout. This is the only "we"/"us"/"our"
in the chapter, and it isn't one of the deliberate acknowledgment-style
exceptions noted in the ch46/47 precedent.

CURRENT
```text
Here, we'll limit it to grass, water, and rock.
```

PROPOSED
```text
Here, the map is limited to grass, water, and rock.
```

### A3 — line 247 — emphasis italics

`*are*` introduces no term; it's a stress mark. Every other italic in
the chapter (*Flyweight*, *Intrinsic state*, *Extrinsic state*,
*interning*) introduces a term on first use, so this one stands out
by contrast, confirming it's the odd one out rather than house style.

CURRENT
```text
for a perfectly interned type, equal values *are* the same object,
```

PROPOSED
```text
for a perfectly interned type, equal values are the same object,
```

### A4 — line 46 — "exactly" as intensifier

CLAUDE.md calls this pattern out by name ("exactly because"). Dropping
it loses nothing: "this reason" already points at the sentence right
before it.

CURRENT
```text
(Python warns about `is` on a literal for exactly this reason: the compiler makes the answer misleading.)
```

PROPOSED
```text
(Python warns about `is` on a literal for this reason: the compiler makes the answer misleading.)
```

### A5 — line 243 — "exactly" as intensifier

Same pattern as A4. "That re-run" already identifies which re-run;
"exactly" adds no further precision.

CURRENT
```text
whose generated `__init__()` reintroduces exactly that re-run.
```

PROPOSED
```text
whose generated `__init__()` reintroduces that re-run.
```

## Tier B

### B1 — line 17 — "already-existing"

"Already" is on the "avoid if possible" tier, and "already-existing" is
a redundant compound: existing already implies prior existence.
Tightening loses nothing, but it's a minor enough phrase that leaving
it is defensible.

CURRENT
```text
Second, route construction through a factory that returns the already-existing instance for a given value.
```

PROPOSED
```text
Second, route construction through a factory that returns the existing instance for a given value.
```

### B2 — line 248 — "already" as filler

Weaker case than B1: "already" here leans on "without doing anything
extra," which is arguably real content (it ties back to "costs less
than it appears" two clauses earlier). I'd lean cut, but it's close.

CURRENT
```text
so the default identity comparison already answers correctly.
```

PROPOSED
```text
so the default identity comparison answers correctly.
```

### B3 — line 196 — "honest"

"Honest" is on the "avoid if possible" tier and personifies the
factory function. It's also a deliberate voice choice that sets up the
contrast with "hide the pool inside `__new__`" two sentences later, so
there's a real argument for keeping it. I'd lean toward applying this,
but it's closer to a style call than a clear violation.

CURRENT
```text
A factory function like `tile()` is an honest extra name.
```

PROPOSED
```text
A factory function like `tile()` is a visibly different name.
```

### B4 — line 25 — fragmented header

"Python Uses Flyweights" followed by "CPython flyweights its most
common values" mostly restates the heading before the section's real
content starts. Per the ch46/47 precedent this is a per-instance call,
not a rule. Weak case for cutting here: the line does add specifics
("CPython," "most common values") that frame both the integer and
string examples that follow, so I'd lean toward keeping it.

CURRENT
```text
CPython flyweights its most common values.

It creates small integers once and shares them:
```

PROPOSED
```text
CPython creates small integers once and shares them:
```

### B5 — line 398 — fragmented header / announcement opener

"The pattern is easy to spot once you know its shape" is a generic
frame before the real content (compilers, column stores, text
systems). Weaker defense than B4: this sentence doesn't add any fact
the following sentences don't already carry, so I'd lean toward
cutting it.

CURRENT
```text
The pattern is easy to spot once you know its shape.

Compilers and interpreters intern identifiers so that scope lookups compare pointers instead of characters.
```

PROPOSED
```text
Compilers and interpreters intern identifiers so that scope lookups compare pointers instead of characters.
```

## Housekeeping

None. No double blank line before a heading (the chapter uses a
single blank line before every heading, consistently), no Semantic
Line Break drift (`uv run python tools/reflow_prose.py --diff
Chapters/35_Flyweight.md` reported zero paragraphs to change), no
`[[ ]]` draft notes, no spaced ` -- `, and no code-listing comments
beyond the standard `# path/slug.py` header line in each block (so
nothing to report under "Listing comments").

## Considered and not flagged

- **Line 153, "trusts its argument is already a `Symbol`."** "Already"
  here carries real meaning: it marks that the value was validated
  before reaching `tile()`, which is the point of the sentence
  (locating the untrusted boundary at `to_symbol()`). Left alone.
- **Line 43, "so even `100000 is 100000` prints `True`."** "Even"
  draws a genuine contrast, the surprising fact that constant folding
  makes even the "uncached" literal compare equal. Left alone.
- **Line 400, "Column stores such as Pandas and Polars offer
  categorical types."** A single, isolated instance of the
  §8 copula-avoidance pattern ("offers a"). Detection guidance says a
  lone hit isn't a tell; nothing else clusters with it. Left alone.
- **"So" as a causal connector.** Used often across the chapter
  ("so it can live...", "so caching produces...", "so the untrusted
  boundary is..."). Not on any watch list; reads as a consistent
  authorial habit for short causal clauses, not an AI tell.
- **Passive constructions (§13, advisory here).** A few sentences use
  passive voice ("is unchanged," "are frozen"), but none obscure the
  actor in a way active voice would clearly improve. Left alone per
  the skill's own advisory note for technical prose.

## Scan coverage

Clean, no hits at all: AI vocabulary (§7), promotional/advertisement
language (§4), vague attributions (§5), "Challenges" sections (§6),
negative parallelism and tailing negation (§9), rule-of-three overuse
(§10), elegant variation (§11), false ranges (§12), boldface overuse
(§15), inline-header vertical lists (§16), emojis (§18), curly quotes
(§19), collaborative-communication artifacts (§20), knowledge-cutoff
disclaimers (§21), sycophantic tone (§22), filler phrases (§23),
excessive hedging (§24), generic positive conclusions (§25),
hyphenated-pair overuse (§26), persuasive authority tropes (§27),
aphorism formulas (§32), conversational rhetorical openers (§33),
diff-anchored writing (§30), staccato/manufactured-punchline runs
(§31), and the "nothing else" family (already swept book-wide). Also
checked and clean: em dashes (none present, so no spaced-dash issue
either) and the full CLAUDE.md watch list (`actually`, `already`,
`even`, `honest`, `buy`, `hooks`, `never`, `anyway`, `at all`,
`promise`, `is what`, `has to`, `itself`, `was to`, `ever`, `does it`,
`reach for`, `plain`, and the third-tier "don't use" list) beyond what
is flagged above.
