[[Reviewed]]
# Humanizer candidates: Chapters/24_Singleton.md

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

The chapter is close to clean on the classic AI-tell checklist: no
AI-vocabulary hits, no signposting, no boldface-header lists, no curly
quotes, no em dashes at all (so nothing to preserve or fix there), and
the "nothing else" family didn't turn up anything the August sweep
missed. What did turn up was small and structural: a genuine leftover
duplicate sentence in "Lazy Creation," a three-site first-person-plural
slip ("we"), and a small cluster of emphasis-only italics. One
fragmented-header candidate was Tier B, arguable either way.

All Tier A and Tier B edits have been applied, along with the
Housekeeping stray-blank-line fix.

## Considered and not flagged

- **Em dashes / spaced ` -- `.** None anywhere in the chapter, so
  nothing to preserve and nothing to flag.
- **Curly quotes.** None found.
- **`[[ ]]` draft notes.** None found.
- **AI-vocabulary list (§7).** Zero hits (no *delve*, *tapestry*,
  *pivotal*, *underscore* as a verb, etc.), consistent with 46 and 47.
- **Signposting/announcements (§28), boldface-header lists (§16),
  emoji (§18).** None present.
- **Repeated `*Borg*` italics (lines 439, 445, 667).** Looks like a
  deliberate proper-noun-style treatment for a coined pattern nickname
  rather than plain emphasis, closer to how the book italicizes a book
  title on every mention than to a stray emphasis italic. Left alone;
  flag if you disagree.
- **"no sentinel, no guard, and no race" (line 339).** A tailing
  triple-negative, but it's doing real contrastive work against the
  lazy form's "it carries the sentinel and the guard" one sentence
  earlier, not padding for its own sake. Left alone.
- **"Mutate through any name. Rebind only through the module."
  (lines 47-48) and its echo "Mutate through any name. Declare only
  what you rebind." (lines 201-202).** A deliberate two-line aphorism
  used as a callback between sections, not filler repetition.
- **"Privacy in Python is advice, not enforcement." (line 121).**
  Aphorism-shaped, but states a specific, true technical claim rather
  than a hollow profundity. Left alone.
- **Isolated short sentences** ("No class, no ceremony.",
  "This is not a narrow window.").
  Single instances, not a stacked run, so they don't meet the
  staccato-drama bar the skill sets.
- **Footnote quoting Star Trek** ("we are all one," line 439).
  Secondhand text inside a quotation, not an authorial "we"; excluded
  from the person-consistency finding.

## Scan coverage

No hits on: undue-significance language (§1-2), promotional/
advertisement language (§4), vague attribution (§5), "Challenges and
Future" sections (§6), copula avoidance (§8), rule-of-three padding
(§10, aside from the genuinely functional "Three implementation
notes"), elegant variation (§11), false ranges (§12), boldface overuse
(§15), collaborative-communication artifacts (§20), knowledge-cutoff
disclaimers (§21), sycophancy (§22), filler phrases (§23), excessive
hedging (§24), generic positive conclusions (§25), hyphenated-pair
overuse (§26), persuasive-authority tropes (§27), aphorism formulas
(§32, aside from the one considered above), and conversational
rhetorical openers (§33). The "nothing else" family was already swept
book-wide in August and turned up nothing new here.
