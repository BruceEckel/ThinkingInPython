> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/26_Patterns--Surrogate/README.md`
(2026-10-16 sweep). The file carries few AI-writing tells: no Tier 1A
vocabulary, no curly quotes, no spaced ` -- `, no metadiscourse frames.
What fired was a handful of "and" joins between clauses with different
subjects, two awkward word orders, a repeated phrase or word, and a run
narrated in the past tense. Each had one sensible fix and was applied
directly. This file holds no live block; it is the applied-directly
record.

## Applied directly

- Line 49, "and" with a subject change (consequence): "normal lookup
  finds it, and the three reads build nothing" -> "... finds it, so the
  three reads build nothing".
- Line 52, word order: "A property also ends the lookup before
  `__getattr__()`, at the class" -> "A property also stops the lookup at
  the class, before `__getattr__()`".
- Line 108, present tense for the listing's behavior: "The proxy served
  ... it held ... and deferred" -> "serves ... holds ... defers", matching
  the surrounding walkthrough. Rewrapped the paragraph.
- Line 313, repeated "still": "`a` still points at the original `Box`,
  whose list still holds" -> "`a` keeps the original `Box`, whose list
  still holds". Rewrapped the paragraph.
- Line 554, "and" with a subject change plus a negative: "`Pool` builds
  every `Connection` in its constructor, and nothing else creates one" ->
  "`Pool` alone creates `Connection` objects, all of them in its
  constructor". Rewrapped the paragraph.
- Line 562, rewrap only: rejoined "returning / that connection to the
  pool" onto one line.
- Line 626, repetition: "`p.__len__()` returns 2 through
  `__getattr__()`" in a sentence that opens "If `Proxy` forwards through
  `__getattr__()` alone" -> "`p.__len__()` returns 2". Rewrapped.
- Line 667, "and" with a subject change (contrast): "Both give the same
  answer, and `len()` reads better" -> two sentences. Rewrapped.

## Considered and declined

- The bold step labels ("**Answer `description` without building.**",
  "**Copy before a shared write.**", and the rest) are the Solutions
  files' step-label convention, not §15 boldface overuse.
- Line 105, "forwards the lookup with no report and no build": a
  tailing negation by shape, but it is the half of the contrast with
  `[1]`, which reports and builds. Kept.
- Line 392, "The trap is specific to the fallback method": partly
  restates the trace above it (treadmill), but it turns the one trace
  into the general rule that the next paragraph applies. Kept.
- Line 476, "When a later `acquire()` lends connection 0 to another
  client": the listing's next `acquire()` would pop connection 1, since
  `c2` is released first, but the sentence is a condition ("when"), not
  a claim about this run. Kept.
- Line 574, "*protection proxy*" and "*smart reference*" in lowercase
  italics: proxy variants the chapter names, governed by the pattern-name
  gate, which passes. Kept.
- Line 772, "The decision compares the type of the implementation ...
  with the type of `new`": checked against `state_surrogate.py`, which
  annotates both `implementation` and `new_implementation` as `Any`, so
  the claim that the checker sees `Any` for both holds. Kept as written.
- The heading of exercise 1 ("answers the cheap requests itself") uses
  "itself" reflexively; headings are out of scope regardless.
