---
name: stutter
description: Find and fix word stutters. A prose word beside its own code-span form ("The next `next()`", "without a `return` returns `None`"), one verb said of two or three different things in a sentence ("`close()` returns the value the generator returned ... and the call returns"), and a prose noun and a code variable of one spelling naming different things in one paragraph ("`job`" the loop variable against "the job" the generator). Each candidate is read aloud, tested for whether the two occurrences do different jobs, and reworded with words the passage already has. Use when asked to remove stutters, echoes, or word repeats from a chapter (or the book). The argument names chapters by number or name, optionally followed by `section "<heading>"`; no argument means all of Chapters/.
---

# Stutter: one sound, one job

A stutter is a word that recurs within a few tokens of itself doing a
different job the second time, so the reader hears one sound and has to
re-sort what it points at.
The case that started this pass (chapter 45, 2026-11-07):
"The next `next()` links that frame back into the call stack."
Bruce called it awkward: the adjective "next" and the function `next()`
sit side by side, the font is the only thing separating them, and read
aloud the phrase stutters.
The fix was "The call that resumes the generator links that frame back
into the call stack", which also covers `send()` and `throw()`.
The scan he asked for next found two more in the chapter.
"`close()` returns the value the generator returned while handling
`GeneratorExit`, so the driver prints `closed`, and the call returns"
said "return" of three different things, `close()` handing a value
back, the generator's `return` statement, and the call completing;
now `close()` "hands the driver the value".
A walk of `task_runner_send.py` wrote "`job`" (the loop variable) in one
sentence and "job" (the generator) in the next, and "so that `job`
leaves `ready`" read as a purpose clause once the font stopped
separating the words; now the paragraph says "job" in prose throughout.

The shape is rare.
The book-wide sweep that day read 1,311 candidates in 93 files and
reworded 56; a pass that rewrites a tenth of its hits has gone wrong.
This pass edits `Chapters/NN_*.md` prose only;
code blocks, `#:` output markers, headings, and quoted material stay.
Given a `Solutions/<chapter>/README.md`, it edits that file's prose the
same way, except the block quote under each `## N.` heading, which
`tip statements` copies from the chapter; a stutter there is fixed in
the chapter's exercise.

## Mechanical candidates

Run `tip stutter CH=NN` first (`tools/word_stutter.py`) and keep the
hits inside the scope.
It keeps no baseline, so every hit prints every time.

- `[CODE!]` and `[CODE]`: a prose word within three tokens of a code
  span holding the same identifier; `!` means adjacent or one apart.
- `[STEM~]`: a stem in two inflections within three tokens in one
  sentence ("returns ... returned", "resumes ... resuming"), the tier
  most often worth rewording.
- `[STEM=]`: the same form twice ("the generator ... the generator"),
  mostly the topic noun named again, which the antecedents rule
  prefers to a pronoun; judge these from the context line.

The scan is a floor.
A sentence boundary stops its window, so the `job` paragraph above is
invisible to it; a link's text is hidden; a pair joined by "and", "or",
"to", "but", "than", or a preposition is dropped.
`ARGS="--window 4"` widens the gap by one token (the `close()` sentence
needs it), at about a third more candidates.
A same-shape stutter noticed while reading a paragraph is a hit.

## The test

1. Read the sentence aloud, with the code span read as its identifier.
2. Name the job each occurrence does: the part of speech, the thing it
   names, the subject it is said of.
3. If the two jobs differ and the repeat makes the reader re-sort them,
   reword.
   If the repeat carries structure or names one thing consistently,
   keep.
4. Before rewording a claim about a listing, open the listing and
   confirm which thing each occurrence names.
   A rewrite that names the wrong thing is worse than the stutter.

## Reword when

- A prose word sits beside its own identifier in a different role: an
  adjective beside the function ("the next `next()`"), a verb beside
  the keyword ("a function that finishes without a `return` returns
  `None`" became "reaches the end of its body returns `None`"), a verb
  beside a method of that name ("[Inheritance] shows `Derived.show()`
  printing" became "In [Inheritance], `Derived.show()` prints"), a noun
  beside a variable of that spelling that names a different thing
  ("binds the inner instance, `instance` always holds" became "binds
  the inner object to `instance`, that class variable always holds").
- One verb is said of two or three subjects in one sentence ("The same
  file runs, and the interpreter runs its busiest paths" became "The
  interpreter runs the same file and executes its busiest paths").
- Two compounds share a word in one phrase and the reader hears a
  third sense ("`timeit` times with `time.perf_counter()`" became
  "`timeit` uses `time.perf_counter()`"; "times each variant five
  times" became "in five rounds").
- A noun and a verb of one stem in one clause ("each claimed cell turns
  green in turn" became "in that order"; "the `gc.collect()` call runs
  that collector" became "makes that collector run").
- A `Done when:` criterion with the shape ("runs its body `times`
  times" became "as many times as `times` holds"; "six draws" beside
  `Oval.draw` became "six random shapes"); the criterion is prose the
  pass owns.

## Keep when

- A deliberate parallel: "the yield channel and the return channel",
  "the Moore shape and the Mealy shape", "one state at a time, one
  transition at a time", "Choosing the factory chooses both halves".
- The topic noun named again where a pronoun would have two
  candidates: "a generator function creates the generator. The
  generator body runs later."
  Never trade a repeated noun for a pronoun that could point two ways,
  and never for a synonym: the book uses one name per thing, and
  elegant variation is a worse fault than the repeat.
- A function or listing whose name is the verb it performs, in subject
  position: "`tg.cancel()` cancels every task", "`squares()` yields
  squares", "`flatten.py` flattens nested lists", "C's `round()` rounds
  half away from zero".
- A definition or an identity: "an empty set is `set()`", "`Effect` is
  an alias for", "the `trace` decorator traces calls" where the
  sentence introduces `trace`.
- A plural beside its singular doing the distributive job: "a list of
  tuples, one tuple per case"; "`n` entries, each new entry evicts".
- A compound term beside its head word: "the type checker types each
  field", "a return type the type checker reads", "the `class`
  statement declared the class".
- A quoted diagnostic, an output line, a heading, a bold step label in
  a Solutions ladder ("**Accept any factory.** `build_shapes()`
  accepts"), a book title, and the exercise statement itself, which is
  Bruce's wording.
- A code-font word beside the prose word for the same thing in the
  same role: "every move in `MOVES`", "each `runner.run()` call runs
  one coroutine".

When the test is close, keep.

## The repair

The repair uses words the passage already has.

- Replace one occurrence with the thing's role or the noun the
  sentence is about ("The next `next()`" became "The call that resumes
  the generator"; `close()` "returns" became "hands the driver").
- Give each occurrence its own clause when one verb carries two
  subjects.
- Delete the occurrence the sentence does not need ("the skipped side
  effect" after "skips the `print()`" became "the side effect").
- Choose one form, prose or code, for a thing the paragraph names both
  ways, and use it throughout: code font when the sentence is about
  the variable or the call, prose for the object it stands for.
- Never introduce a synonym for a technical term.
  A verb the chapter already uses for the action is fine ("executes"
  beside `run()` in chapter 47, which uses it twice more).

## After the edits

1. `uv run tip verify-ch CH=NN` (reflows, syncs, gates).
2. `uv run tip prose CH=NN`: a `NEW` hit on a sentence the pass wrote is
   a sentence to fix; a `stale` entry paired with a `NEW` whose flagged
   word is unchanged is a re-keyed keep, accepted with the scoped
   `tip <check>-accept CH=NN`.
   A rewrite that adds "no", "nothing", "has no", or "whatever" draws a
   watch-words hit of its own: two sweep agents had to reword twice.
3. Read `git diff Chapters/`: a changed `#:` marker means an edit
   strayed into code.
4. Commit the chapter and any baseline files together.

## Report

Each rewrite as `path:line` old -> new, abbreviated to the changed
words, then the keeps grouped by the shapes above with counts, then the
close calls either way.

## Accrued shapes

Shapes Bruce flags that the catalog above lacks go here, with the
sentence, the date, and the repair.

- (none yet beyond the three chapter 45 cases, 2026-11-07)
