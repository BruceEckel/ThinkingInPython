> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability pass over `Solutions/25_Patterns--Template_Method/README.md`
(2026-10-16 sweep). The file carries few AI-writing tells: no Tier 1A
vocabulary, no watch-list words, no curly quotes, no spaced ` -- `.
Most of what fired was the global rule on an "and" joining two clauses
with different subjects, plus one garden-path relative clause, one
manufactured punchline, one restated pair, and one stranded
possessive, each fixed directly. The claim that the type checker
reports constructing an abstract `HalfDone` was probed under `ty`
0.0.87 (`call-non-callable: Cannot instantiate abstract class`) before
that sentence was touched. This file holds no live block; it is the
applied-directly record.

## Applied directly

- Line 129, wrapping: the bold-labeled paragraph left "as" alone on a
  line; rewrapped. Link text and target unchanged.
- Line 134, "and" with a subject change (contrast): "The subclass
  overrides `process()`, and the function form passes `str.upper`" ->
  two sentences.
- Line 172, cause and concession inverted: "Both produce ..., because
  both supply the same step through two different mechanisms" -> "The
  two mechanisms supply the same step, so both produce ...".
- Line 230, "and" with a subject change (contrast): "`Search` stores it
  in a field, and the lambda closes over ..." -> two sentences.
- Line 232, "and" with a subject change: "A new policy is a new step,
  and the algorithm that calls the step belongs to the framework" ->
  two sentences.
- Line 376, "and" with a subject change: "is silent on the order, and
  every type checker accepts the usual one" -> two sentences.
- Line 377, garden-path clause: "from the subclass's own `step()`,
  which a base class someone else wrote called" -> "raised in the
  subclass's own `step()`, called from a base class someone else
  wrote".
- Line 379, "and" with a subject change (contrast): "a rule the next
  author must remember, and that author may not have read this
  chapter" -> two sentences.
- Line 381, §31/§32 manufactured punchline: cut "A rule to remember is
  not a repair.", which restated the sentence before it as an
  aphorism. The close alternative was to keep it and cut the sentence
  before; that sentence carries the "may not have read this chapter"
  point the exercise asks about, so it stays.
- Line 386, "and" with a subject change: "Each call site gains a line,
  `greeter.run()`, and that line moves the decision ..." -> two
  sentences.
- Line 481, "and" with a subject change: "The program runs, and the
  steps come out in the reversed order" -> "The program runs and
  prints the steps in the reversed order".
- Line 494, "and" with a subject change (contrast): "sets `__final__ =
  True` on the function, and nothing in the interpreter consults that
  attribute" -> two sentences.
- Line 599, wrapping: rewrapped the over-long middle line.
- Line 606, "and" with a subject change: "raises an exception instead,
  and the exception propagates out of `run()`" -> "raises an exception
  instead, which propagates out of `run()`".
- Line 613, "and" with a subject change (contrast): "breaks the second
  half, and the program completes normally" -> "breaks the second
  half. The program still completes normally."
- Line 618, "and" with a subject change (contrast): "need different
  things from a type checker, and only one of those things exists" ->
  two sentences.
- Lines 621-623, restatement: "The `...` body makes the step optional.
  Through it, the base class declares that a subclass may skip this
  step." said the same thing twice; merged into "Through the `...`
  body, the base class declares that a subclass may skip this step."
- Line 626, "and" with a subject change: "are the same code, and only
  the base class can record that difference" -> two sentences.
- Line 629, two consequences each carrying its own claim: "raises a
  `TypeError`, and the type checker reports the construction ..." ->
  two sentences (claim checked under `ty`, see above).
- Line 735, "and" with a subject change, plus a stranded possessive:
  "`MyApp` adds `report()`, and a subclass of `MyApp` inherits that
  name along with the framework's own:" -> "`MyApp` adds `report()`. A
  subclass of `MyApp` inherits that name along with the framework's own
  names:".
- Lines 796-798, restatement: "Yet `report()` is a helper that `MyApp`
  added, not a step of the framework. The framework enforces a rule
  about a name that `MyApp` defined." -> one sentence ending "so the
  framework enforces a rule about a name that belongs to `MyApp`."
- Line 873, "and" with a subject change: "a new method that nothing
  calls, and the framework accepts it" -> two sentences.

## Considered and declined

- The bold step labels ("**Let a subclass be a record.**", "**Give the
  step its data.**", "**Compare against every base.**", and the rest)
  are the Solutions files' step-label convention, not §15 boldface
  overuse.
- Line 481, "Python objects to nothing.": a negative that is the claim,
  answering the exercise's "which of the two objects". Kept, as is the
  beat "The anchored algorithm is no longer anchored."
- Line 503, `near_miss.py` contains the don't-use phrase "near-miss",
  but it is a listing name the chapter owns; prose cannot rename it.
- Line 642, "That split is the chapter's point stated from the other
  side." §70 by shape, but it ties the exercise back to the chapter's
  structure-versus-discipline close (the "Structure fixes it ...
  Discipline fixes the rest" anaphora `readability_db.md` keeps). Kept.
- Line 643, "`@final` protects ..., and `@abstractmethod` protects ...,
  because both are ...": a parallel pair sharing one "because", so the
  "and" is additive. Kept. The same goes for line 646, "What a step
  does once called is behavior, and Liskov substitution is a rule about
  behavior": the two premises of one argument, where neither "but" nor
  "so" fits.
- Line 794, "every non-dunder name in every base, and `report` is one
  of those names": the second clause completes the premise rather than
  contrasting with it. Kept.
- Mixed wrapping: the `Hint:` paragraphs and a few prose paragraphs use
  one sentence per line while the rest is hand-wrapped near 70
  columns. Only the lines an edit touched were rewrapped; a whole-file
  rewrap would bury the real changes in the diff.
