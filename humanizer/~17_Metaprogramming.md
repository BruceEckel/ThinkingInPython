[[Reviewed]]
# Humanizer candidates: Chapters/17_Metaprogramming.md

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

Mostly clean. The chapter's only real cluster was person: four "we" sites
(one pair back to back in the opening paragraph, two more at later section
openers) in a book written second person throughout. There's also a
recurring "X itself" tic, dense enough to be worth a pass but genuinely
mixed, some sites draw a real contrast and earn the word. One bullet list
broke its own parallel structure for no reason. No em dashes anywhere in
the chapter, no word-level AI vocabulary, no promotional language, no
fragmented-header padding beyond two borderline openers.

All Tier A and Tier B edits have been applied, along with the
Housekeeping listing-comment fix (needs `make sync` to reach `Examples/`).

## Considered and not flagged

- **Em dashes.** Zero in this chapter, `---` and spaced ` -- ` both
  absent. Nothing to report either way.
- **Italics.** Every italicized term (*classes*, *metaclasses*, *Class
  decorators*, *descriptor*, *data descriptor*, *class object*,
  *metamethods*, *class variable*) introduces that term on first use.
  None is used for bare emphasis.
- **"itself" sites left alone.** Three more hits looked at and kept:
  line 568 ("a metaclass is itself a subclass of `type`") does real work
  setting up why naming it as a base class means something different
  from using `metaclass=`; line 1157 ("storage that lives on the object
  itself") parallels "storage borrowed from the class" earlier in the
  same sentence and the contrast would blur without it; line 1184
  ("which can look like the class defined them itself") is the
  paragraph's actual point, that the dunders only look self-defined but
  are inherited unchanged from `object`.
- **"not only descriptors" (line 472).** Reads like §9's negative
  parallelism at a glance, but it's an ordinary qualifier ("every class
  attribute that defines it, not only descriptors"), not the "not
  only...but" rhetorical pairing the pattern describes. No "but" half,
  no manufactured drama.
- **Word-level AI vocabulary (§7).** No hits: no *delve*, *crucial*,
  *pivotal*, *tapestry*, *landscape*, *underscore* (verb), *fostering*,
  *garner*, or similar. Consistent with the note that this scan is
  usually a dead end in this book.
- **Rule of three (§10).** Several three-item and four-item bullet
  lists (the simpler-hooks list near the top, the `inspect` predicates,
  the metaclass use cases at the end), but each enumerates genuinely
  distinct technical options rather than padding for the appearance of
  thoroughness.
- **Everything else on the pattern list.** No promotional language, no
  vague attributions, no "Challenges" section, no copula avoidance, no
  false ranges, no elegant variation, no hedging, no filler phrases, no
  boldface overuse, no inline-header vertical lists, no emojis, no curly
  quotes, no collaborative-communication artifacts, no knowledge-cutoff
  disclaimers, no sycophantic tone, no aphorism formulas, no
  conversational rhetorical openers, no diff-anchored writing, no
  staccato drama.

## Scan coverage

Full word-level sweep (§7 AI vocabulary, §1-6 content-pattern phrase
lists, §26 hyphenated-pair overuse) came back clean, as did the
structural checks for boldface, vertical lists, emojis, curly quotes,
em dashes, and draft notes. Blank-line hygiene is clean throughout
(no double blank lines before any heading). Structural attention went
to person (one real cluster, applied), italics (clean), fragmented
headers (two borderline sites), broken parallels (one site), and the
CLAUDE.md "itself" rule (checked every instance individually rather
than as a blanket word search, since several genuinely earn their
place). A rerun can skip the word-level sweep and focus on anything
merged into this chapter later.
