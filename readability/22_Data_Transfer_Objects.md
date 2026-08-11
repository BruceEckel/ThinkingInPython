When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first readability pass over
`Chapters/22_Data_Transfer_Objects.md`, run after the deep review in
`deep_review/~22_Data_Transfer_Objects.md` was applied.
The chapter is clean: no Tier 1A/1B/2 vocabulary, no curly quotes,
no spaced `--`, no metadiscourse, no hedge stacks, and the sentence
rhythm varies well
("The attribute bag caught nothing; a declared field catches this."
against the longer serialization sentences).
No direct edits were needed and no finding requires a decision,
so there is no Applied directly section and there are no live blocks.
Everything examined and kept is recorded below so a later sweep does
not re-raise it.

## Considered and declined

- **"When you want the fields named and checked, declare them"**
  (Standard-Library Versions section).
  "Want" is on the don't-use list, but the ban targets anthropomorphized
  objects ("the function wants a string"); this "you want" addresses the
  reader's intent, the same carve-out `readability_db.md` records for
  31_State_Machines' "a bug you want flagged."
- **"The hand-rolled `Messenger` is worth writing only to show how
  `SimpleNamespace` works underneath"** (Which Should You Use?).
  §53 flags the "worth" endorsement family, but its carve-out keeps
  "worth" weighing a real cost: this sentence weighs writing the class
  against its one purpose, and tells the reader when to do it.
- **"a different record type that happens to have the same shape"**
  (A NamedTuple Is Still a Tuple).
  "Happen" is on the consider-rewriting list, but the coincidence is
  the claim: the shapes match by accident while the meanings differ,
  which is the danger the section demonstrates.
- **"The rest is what `SimpleNamespace` adds"**.
  The global "is what" rule keeps the construction when what follows is
  a clause that cannot attach without it, its own example being
  "`R` is what it produces"; "what `SimpleNamespace` adds" has the same
  shape.
- **"When it need only *become* a dict on the way out"** (closing
  section).
  "On the way out" is not the banned "the way out" (an escape or
  solution); it means "as the data leaves as JSON," and the deep review
  edited this sentence and kept the phrase.
- **"type-blind" in predicate position, twice** (A NamedTuple Is Still
  a Tuple).
  §26 drops predicate hyphens on stock pairs like "high-quality";
  "type-blind" is a coined compound whose unhyphenated form reads as a
  typo, so both uses keep the hyphen.
- **"a comparison between two different frozen types raises one even
  then"**.
  "Even" is on the avoid-if-possible list but carries the contrast:
  `order=True` enables ordering within a type yet still refuses it
  across types.
- **The three-part "Use `SimpleNamespace` for ... a `@dataclass` for
  ... and a `NamedTuple` for ..." opener** (Which Should You Use?).
  §10 shape, but the chapter teaches these three tools, so the list
  is the content rather than padding.
- **"the value stays a real dict"** (closing section).
  §34 flags bare "real" intensifiers; this one draws the named
  contrast the carve-out allows: `TypedDict` types the keys for the
  checker while the runtime value remains an ordinary dict, unlike the
  record types above it.
- **"The `m: Any` annotation is not decoration"** (opening section).
  A negative opener by shape, but the next sentence supplies the
  reason (the checker rejects both uses without it), and the beat is
  authorial voice, not a manufactured reveal.
- **"equals only its own kind"** (Which Should You Use?).
  "Only" is load-bearing the same way `readability_db.md`'s
  30_Observer "a lambda equals only itself" entry records: without it
  the claim is trivially true.
