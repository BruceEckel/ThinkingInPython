> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Class Attributes

The chapter carries few AI-writing tells: no Tier 1A vocabulary, no colon reveals, no generic closers, and its watch-list hits are all keeps under `readability_db.md`.
The fixes below are mostly the global "and" rule (clauses with different subjects joined by an additive "and"), one restated sentence, one staccato run, and two wordy phrasings.
Every finding had one sensible answer, so this file holds no live block and serves as the record of what was applied.

## Applied directly

- Line 81 (§70 restatement; "and" rule): "Assigning through the class name changes the entry, as `Stars.rating = 9` does, and `setattr(...)` does the same" -> "To change the entry, assign through the class name, or call `setattr(...)` when the name arrives as a string." The `Stars.rating = 9` reminder repeated line 51.
- Line 176 ("and" rule): "Shadowing starts with an assignment, and `.append()` leaves `a`'s dictionary empty" -> two sentences.
- Line 179 (repetition): "The type checker accepts the line too" -> "The type checker also accepts the line", since the sentence before already ends on "too".
- Line 190 ("and" rule, contrast): "and `b` still reads the shared one" -> "while `b` still reads the shared one".
- Line 311 ("and" rule): "creates the attribute on the class, and an instance finds it by fallback" -> two sentences, "An instance then finds it by fallback."
- Line 322 (wordiness): "The assigned value brings the attribute into existence." -> "The assignment creates the attribute." (matches the listing's comment "The assignment creates it").
- Line 330 (scope of "usually"): "A base class usually declares a `ClassVar` with no value to name what its subclasses must supply" read as a claim about base classes in general -> "A `ClassVar` with no value usually appears in a base class, naming what its subclasses must supply".
- Line 371 ("and" rule, consequence): "The declaration says the attribute exists, and the checker accepts that statement." -> two sentences.
- Line 405 (§31 staccato run of five short trace sentences): "Every `Tally` counts itself once. The shared counter stays at `0`." -> one sentence joined by "while".
- Line 517 ("and" rule): "`Base()` (`[1]`) increments `Base.total` to `1`, and `Sub.total` reads through to that `1`." -> two sentences.
- Line 625 ("and" rule; vague pointer): "Assignment answers it, and the answer depends on whether you assign through `self` or through the class name." -> "Assignment answers it. Assigning through `self` writes the instance's dictionary, and assigning through the class name writes the class's dictionary." The closing section now states the answer instead of naming its variable, using the rule lines 49-52 establish.

## Considered and declined

- Lines 417-418, "The bug is not the class attribute. It is writing one where you meant a per-object default." The "not X. It is Y" shape is a §9 negative parallelism by form, but the negation is half of a real contrast (the global rule's "the mistake, not the model" keep), and it corrects the misreading the chapter opens with.
- Lines 83-84, "a plain `dict` holding what the code assigned, and that alone." "plain" contrasts with the read-only `mappingproxy` named two lines up, and "and that alone" excludes the compiler bookkeeping the class dictionary carries, so the tag carries weight.
- Lines 419-423, the three kinds of class-attribute value. Rule-of-three keep in `readability_db.md`: the prose then uses the items ("`Tally.total` is the first of these", "For the third kind").
- Line 266, "It never checks whether some method sets the attribute." The "never" is the claim (watch-list absolute stating a guarantee).
- Lines 247 and 540, "a real `label` attribute" and "real per-object defaults." Each "real" contrasts with a named alternative (a declaration; a class attribute misread as a default), and the second echoes the section heading.
- Lines 11-12, "It is not one." A short beat among longer sentences, not a staccato run.
- Line 22, "which comes up below." A signpost by shape, but it tells the reader the `__slots__` exception is handled rather than skipped.
- Line 619, "covers the details." Mild, but it names what the linked chapter adds.
- Exercises: imperatives exempt; "plain (non-`ClassVar`)" and "needs only the one expression" are a named contrast and an "only the X" shape.
