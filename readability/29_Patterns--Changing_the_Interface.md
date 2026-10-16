> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over chapter 29, 2026-10-16.
The chapter reads as edited prose with few AI tells:
no Tier 1A vocabulary, no signposting, no stacked hedges, and the watch-list hits are restrictions or contrasts the book keeps.
Four small edits went in directly, and this file holds no live block, so it is the record of those edits and of what was considered and left alone.
`tip reflow` and `tip verify-ch CH=29` pass.

## Applied directly

- L24, §34 real/actual inflation: "In a common real case," -> "In a common case,". Nothing in the sentence contrasts with "real", and the example that follows uses placeholder names.
- L436, split-the-"and" rule: "a module loads once, and every importer shares the same module" -> "a module loads once, so every importer shares the same module". The second clause is the consequence of the first.
- L533-534, split-the-"and" rule: "takes two steps, and writing the new interface is the first" -> "takes two steps. The first is writing the new interface."
- L538, antecedents: "The second step marks it, which keeps it working" -> "The second step marks the old interface as deprecated, which keeps it working". The "it" had to reach back past a sentence whose subject was the act of deleting.

## Considered and declined

- L167, "(see exercise 5). mypy accepts it,": two sentences share one source line. Breaking the line before the lowercase "mypy" was tried; `tip reflow` joins it back, since its sentence splitter does not treat a lowercase word as a sentence start. The render is unaffected.
- L18-19 and L535-536, near-verbatim restatement ("callers keep using the old one until a deprecation mark tells them to switch" / "until something tells them to switch"). The introduction previews the section, and the section carries an explicit anchor that other chapters link, so it must stand on its own. Both stay.
- L292 "has a real adapter, `PairCoord`" and L416 "In real code": "real" contrasts with the toy `WhatIHave` listing and with the three-class `facade.py` the sentence before calls "small enough here to read at a glance". Named-contrast carve-out.
- L23 "An adapter's only job", L359 "presents only what the client programmer needs", L477 "appears only inside `total()`", L602 "warn only the callers still passing a string", L603 "static only": each is one of the ruled-fine shapes, and each restriction is the claim.
- L149-150 "Composition keeps the two interfaces separate. Inheritance merges them.": a deliberate two-beat contrast after a long paragraph, not a staccato run.
- L355-357, the epigraph "If something is ugly, hide it inside an object." and "That is *Façade*.": first-edition voice.
- L287-288 "the idiomatic Python adapter: a thin wrapper, not a hierarchy": the colon introduces a restatement, so it is not a §69 reveal.
- L529 "Name a wrapper for why it is there, not for its shape.": a closing line by position, but it is the advice the table and the paragraph above support, not an aphorism standing in for a claim.
- L363 "GoF supplies both halves of that combination.": a topic sentence whose two halves the next two sentences name, one each.
- L409-410 "Turning the key primes the pump, and priming starts the engine." and "An `Ignition` holds a `FuelPump` and a `FuelPump` holds an `Engine`": the "and" joins two steps of one chain, which the split rule keeps.
