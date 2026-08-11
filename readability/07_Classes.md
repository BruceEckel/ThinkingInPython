When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

---

Readability pass over `Chapters/07_Classes.md`,
with `readability_db.md` and `deep_review/~07_Classes.md`'s
declined items read first as carry-forward.
The chapter reads as human, edited prose:
varied sentence lengths, specific claims tied to listings,
no Tier 1A vocabulary, no curly quotes, no spaced `--`.
The few findings were mechanical, so all were applied directly;
nothing needs a decision, and there are no live blocks.

## Applied directly

- Line 203 (Inheritance, after the demo), imperative-plus-consequence:
  "Remove the `super().__init__(text)` line and `self.s` is never created"
  became "If you remove the `super().__init__(text)` line,
  `self.s` is never created".
  The sentence came from the deep review two commits ago,
  in the banned command-then-report form.
- Line 205 (same paragraph), empty adverb (§23):
  "simply inherits and runs the base version"
  became "inherits and runs the base version";
  the sentence means the same without it.
- Line 297 (Marking Overrides), imperative-plus-consequence:
  "Uncomment the decorator on `Typo.shwo` and it says:"
  became "If you uncomment the decorator on `Typo.shwo`, it says:".
  The error output is printed right below,
  so this is a hypothetical whose result the text states,
  not a real instruction like exercise 6's.
- Line 506 (String Representation), repetition:
  the second "which is why" in one paragraph
  ("which is why it reads `Point(3, 4)`")
  became "so it reads `Point(3, 4)`";
  the first ("which is why the list prints `Point(3, 4)`") stays.

## Considered and declined

- **"it doesn't really care about interfaces" (Inheritance opener).**
  A hedge by shape, but the deep review already examined it and recorded it
  as deliberate voice that survived the hedge-cutting commit (812dcd9d).
  Carried forward, not re-raised.
- **"Called on a subclass, `cls` is that subclass" (Static and Class
  Methods).** A dangling modifier read literally (the method is called,
  not `cls`), but it is terse book compression, not an AI tell,
  and any expansion ("When you call it on a subclass, the method receives
  that subclass as `cls`") trades rhythm for pedantry. Left alone.
- **"This is a curiosity more than a technique" and "This is the conversion
  the section opened with, carried out."** Both are first-edition voice
  doing deliberate work: the first deflates the `import` trick,
  the second closes the loop the Properties section opened. Left alone.
- **"which is why" elsewhere (lines 67 and 389).** Two more uses,
  each the only one in its paragraph. Repetition across a chapter is a
  human habit, not synonym cycling; only the adjacent pair was varied.
- **"again, and again, until the interpreter raises a `RecursionError`"
  (setter recursion).** The repetition is deliberate rhythm miming the
  recursion. Left alone.
- **"never calls a base-class constructor automatically" and "never
  consults `__str__()`."** "Never" is on the avoid list, but both are
  factual absolutes about language behavior, not intensifiers.
- **"only records the type," "Cache only what cannot change," "add
  `__str__()` only when users see the output."** Each "only" restricts a
  real claim; deleting any of them changes the meaning.
