> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Classes

Chapter 07 carries almost no AI-writing tells.
The sweep found no Tier 1 or Tier 2 vocabulary, no signposting, no significance inflation, and no staccato runs, and `tip prose` reports zero new hits.
The four changes below apply the global rule on an "and" that joins two clauses with different subjects.
This file holds no live block, so it is the record of the direct edits.

## Applied directly

- Lines 300-301, "and" joining different subjects: "you define a new method instead, and Python reports nothing" -> two sentences, "...a new method instead. Python reports nothing."
- Line 382, "and" hiding a contrast: "`radius` is a plain attribute and `area` is a computation" -> "...a plain attribute, while `area` is a computation."
- Lines 541-542, "and" hiding a consequence: "`del n.total` removes the stored value from `__dict__`, and reading `n.total` again runs the method" -> two sentences, the second "Reading `n.total` again then runs the method." (Close alternative: ", so reading".)
- Lines 552-553, "and" hiding a contrast: "`__str__()` is the readable form for users, and `__repr__()` is the unambiguous form for developers:" -> "..., while `__repr__()` is...:".

## Considered and declined

- Line 223, "that import trick is a curiosity more than a technique": an aphorism shape (§32), but it is the author's verdict on the technique, and the next sentence names the alternative. Whether the class-body `import` paragraph belongs in the Inheritance section at all is a content question, not a readability one.
- Line 265, "runs `A`'s `show()`, not `B`'s `show()`": a tailing negation (§9) by shape, but the contrast is the listing's point, and trimming it to "not `B`'s" would strand the possessive.
- Line 189, "not at the class that defines the calling method": the contrast carries the claim about lookup order (positive-statement rule's own carve-out).
- Lines 361, 382, 430, 543, "plain attribute" and "a plain `@property`": each draws a contrast with a computed or validated property or with `cached_property` (recurring keep).
- Line 454, "keeps each method from calling itself": reflexive and load-bearing (recurring keep).
- Line 550, "That display says nothing about the value the object holds": the negative is the claim the section answers.
- Line 58, "(though anything else probably confuses people)": deliberate aside in the author's voice.
- Line 126, "Python is different.": a short beat among longer sentences (recurring keep).
- Line 438, "`@radius.setter` reads that object, and its `setter()` method returns a new property": the subjects differ, but the clauses are two steps of one action, which the "and" rule keeps.
- Lines 656-657, "`is_freezing()` also works as a module-level function, and that is the usual choice": additive, so the "and" stays.
