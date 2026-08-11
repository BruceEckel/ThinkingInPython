When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

Readability pass over `Chapters/26_Surrogate.md`.
`readability_db.md` carries nothing binding for this chapter.
The deep review (`deep_review/~26_Surrogate.md`) ran three days ago
and its style audit removed the intensifiers this pass hunts
("even simpler", a filler "already"),
so the prose comes to this pass clean.
The mechanical sweep found no curly quotes, no spaced ` -- `,
no Tier 1A vocabulary, and no structural tells:
the colons are definitional labels, not §69 reveals;
the three proxy kinds enumerated after `counting_proxy.py`
name the three listings shown, not a padded triple;
sentence lengths vary well.
Every remaining watch-list hit was judged and kept, below.
No direct fixes; no live blocks.

## Considered and declined

- Kinds of Proxy, smart reference: "in order to implement the
  *copy-on-write* idiom" is the one Tier 1B hit in the chapter, and the
  deep review deliberately restored the "in order" (its applied-directly
  list records the reason: the bare comma version read as two unrelated
  purposes, losing the causal link that counting references is how
  copy-on-write knows when to copy). Binding; not re-flagged.
- "the *fallback* hook" and "`__getattr__()` is a read hook": "hooks" is
  on the avoid-if-possible list, but here it names the actual mechanism
  (Python's data-model docs describe `__getattr__()` as a fallback),
  the italics introduce it as chapter vocabulary, and exercise 4 depends
  on the term ("the fallback-hook behavior described in this chapter").
  Kept.
- "`run()` never changes and neither does `b`." Watch-list "never",
  declined by the deep review as the State pattern's point: the caller
  and surrogate are constant while behavior changes. Carried forward.
- "the real class that does the work" (intro) and "the actual
  implementation": §34-shaped, but both draw the named contrast the
  section exists to teach, surrogate versus implementation. Kept.
- "As long as `Proxy` is somehow 'speaking for' the class": "somehow" is
  a hedge, but the looseness is the claim; the paragraph is defining a
  deliberately looser reading than GoF's and says so two lines later.
  Kept.
- The counted openers "One caveat:", "One limit:", "Two escapes exist":
  a repeated construction, but consistency rather than synonym cycling,
  and each colon introduces the content it labels. Kept.
- The reflexives all pass the load-bearing test: "which it constructs
  itself" (constructs rather than receives), "calls itself forever"
  (the recursion), "the proxy prints as itself" (as the proxy, not the
  implementation). Kept.
- "simpler and just as flexible" (conclusion): "just" carries the real
  comparison "equally flexible", not filler emphasis. Kept.
