When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/40_Functional_Foundations.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers validate,
`ty`, ruff, and pytest are clean on `build/examples/40_Functional_Foundations`
(no tests in this chapter), and all fourteen scripts run. The chapter's
checker claims were each probed on the pinned `ty` 0.0.70: the `Placeholder`
`# type: ignore` workaround is still required (without the ignores, `ty`
reports `invalid-argument-type` for `Placeholder` where an `int` is declared
and types `percent` as taking zero arguments, which is the limitation the
prose describes); the missing-`nonlocal` diagnostic is verbatim
`Name 'count' used when not defined`; `MAX_SIZE = 200` is `invalid-assignment`
while `CONFIG.append(3)` passes silently; and `Sequence.append` is
`unresolved-attribute`, all as exercise 6 and the prose claim. Runtime probes
confirm the `Placeholder` prose: a no-argument `percent()` call raises a
`TypeError`, a trailing placeholder is rejected at construction
("trailing Placeholders are not allowed"), `percent.args` reprs as
`(0, Placeholder, 100)`, and `partial(power, 2)(5)` computes `32` as the
keyword-binding paragraph warns. Every outbound link was checked against its
target: 43's "Automatic Parallelism", 41's `cache`, 44's "Are Exceptions
Impure?" (which does re-use `slope()`), 20's "The Immutability Solution",
5's "Lambdas", 28's `late_binding.py`, 23's `#generators`, and 27's
dictionary-factory anchor all exist. "Those four chapters are Part IV"
matches `build_site.py`'s `PARTS` (IV starts at 40, V at 44). The bare
`from exceptions import ignore` matches the book convention (chapters 17,
18, 36, and 44 also reuse it with no gloss after 15 teaches it). No finding
needs a decision, so this file has no live blocks; everything found was
either applied directly or recorded below as considered and declined.

## Applied directly

- New exercise 8 (with its solution in
  `Solutions/40_Functional_Foundations.md`): give `make_counter()` a `step`
  parameter, explain why `count` needs `nonlocal` and `step` does not, then
  delete the declaration and compare `ty`'s report with the runtime failure.
  Closures get the chapter's longest treatment and call forgetting
  `nonlocal` "the standard stumble", yet the only closures exercise was
  adding `multiplier(4)`; this one cements the read-versus-assign
  distinction the section teaches.
- "Partial Application": the paragraph after the listing ended "which is
  handy when a higher-order function needs a single-argument callable" and
  the next paragraph opened "Use partial application when an API expects a
  function of one argument and you have a function of several", the same
  advice twice in adjacent sentences. The first clause is cut, and in its
  place the section now connects backward: `multiplier()` in Closures did
  the same by hand (a factory fixing one argument), and `partial()` removes
  the factory when the general function exists. The two sections built the
  same kind of specialized function (`double` appears in both) with nothing
  relating them.
- "Higher-Order Functions": after the finished-list-versus-iterator
  contrast, one sentence notes that a generator expression from chapter 16
  is the comprehension's lazy form and removes that difference. Without it,
  the laziness argument for `map()` reads as if only `map()` can be lazy,
  which a reader who knows generator expressions would rightly question;
  the existing-function rule of thumb is untouched.
- Dispatch-versus-`match` paragraph: "known to the compiler" is now "fixed
  when you write the function". Python has no compiler in the sense the
  sentence needed, and the neighboring sentence already credits the
  checker.
- "Composing Functions" close: "The standard library provides these
  building blocks ready-made" is now "supplies whole modules of these
  small, composable pieces". The stdlib has no `compose()`, so "these
  building blocks" placed at the end of the composition section
  over-claimed; the new wording matches 41's own opening line.
- Placeholder paragraph: "The caller must supply it" is now "The caller
  must still fill the reserved position" (the "it" read as supplying the
  `Placeholder` rather than the argument it reserves).
- Same section: "would mean exactly what `partial(clamp, 0)` already
  means" is now "would mean the same as `partial(clamp, 0)`".
- Immutability intro: "that same list, which anyone can still append to"
  is now "and anyone can still append to it" (stranded preposition).
- `Sequence` caveat: "who still holds the `list` and can append to it
  whenever it likes" is now "at any time" (the "who ... it likes" pronoun
  clash).
- Closures: "on the `count += 1` line itself" dropped "itself".

## Considered and declined

- Intro, "a sliding window from `itertools`": `itertools` has no
  `sliding_window()` (it is a docs recipe), but chapter 41 tours
  `pairwise`, which is a sliding window of two, and the phrase evokes the
  right module without naming a function the reader has not met. Renaming
  it "a pairwise window" before the concept is taught reads worse. Left as
  written.
- "Mutability alone is not what removes hashing": the cleft sets up the
  answering sentence "What removes hashing is equality based on
  *contents*", and flattening it to "does not remove hashing" would break
  the question-answer pair. Kept.
- "This way, a function can carry state without a class" introduces
  `multiplier()`, whose `factor` is fixed configuration rather than
  changing state. The section's second listing (`make_counter()`) supplies
  the mutable case two paragraphs later, and the prose then contrasts the
  two directly, so the broad word does no harm. Left.
