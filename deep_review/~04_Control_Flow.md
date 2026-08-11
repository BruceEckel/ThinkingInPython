[[Reviewed]]
When this file has been applied, change this file's name so it has a leading
`~` to indicate completion.

This is the first deep review of `Chapters/04_Control_Flow.md` in the
clean-slate sweep. The mechanical layer is sound: all `#:` markers
validate, ruff and `ty` are clean on `build/examples/04_Control_Flow`,
and every script runs. The technical claims were re-verified: chained
comparisons, `zip(strict=True)`'s exact `ValueError` message, the
list-skips/dict-raises mutation contrast, soft keywords, the
`BaseException` ancestry of `KeyboardInterrupt`/`SystemExit`, the three
`raise`/`from` report lines (checked against real tracebacks by the
listing itself), `isdigit()` vs `int()` in both directions, and `with`
creating no scope. The three inbound anchors other chapters use
(#comprehensions, #context-managers, #pattern-matching) are untouched.
The review found one outright error (the two-loop escape idiom
attributed the `else` to the outer loop; it belongs to the inner one),
one construct used nineteen chapters before it is taught (`iter()`/
`next()` in `while_true.py`), and a handful of teaching gaps, all small
enough to close directly. Everything found had one sensible answer, so
this file has no decision blocks; the applied list below is the review.

## Applied directly

- `while_true.py`: replaced `values = iter([...])` / `next(values)`
  with a plain list and `values.pop(0)`. Iterators and `next()` are
  [Iterators](23_Iterators.md) material; `pop(0)` is taught in
  Containers. Output and the `#: 8` marker are unchanged.
- Loops: "or a `for`/`else` on the outer one" was wrong; in the
  two-loop escape idiom the `else` attaches to the *inner* loop. Now
  reads "or the loop `else` introduced below".
- Loops: after the loop-`else` paragraph, added two sentences spelling
  out that escape idiom (`continue` in the inner loop's `else`, a
  `break` right after it), since the chapter raises the two-loop
  question itself and previously answered it incorrectly. The
  alternative was a small listing; prose felt like the right weight for
  a tour chapter.
- Walrus: added the tie-back "It also collapses `while_true.py` into
  its loop header: `while (value := values.pop(0)) != 0:`." The
  bottom-tested `while True` and the walrus header test are a lookalike
  pair the chapter showed without connecting.
- Exceptions: added "one that never does stops the program and prints
  the traceback" to the propagation sentence. Exercise 4 depends on
  the concept and nothing stated it.
- Exceptions: added one sentence on bare `raise` (log and let it
  propagate). The section covered raising new exceptions and chaining
  but never re-raising unchanged, which chapter 42 later uses.
- Exceptions: added "Class definitions get their full treatment in
  [Classes](07_Classes.md)" after the `BadNumber` explanation, since
  `class BadNumber(Exception)` uses syntax three chapters early.
- EAFP: added the time-of-check gap (a file that existed at the `if`
  can be gone by the `open()`). The section argued only that test and
  operation can *disagree*; that the world can change between them is
  the other half of the EAFP case.
- New exercise 9 plus its solution in `Solutions/04_Control_Flow.md`:
  predict the mutation-trap survivor for `[2, 2, 1, 3]`. The
  mutating-while-looping trap is one of the chapter's main claims and
  had no exercise; the variant makes the survivor land at the front,
  so the reader must apply the shifting-slots mechanism rather than
  pattern-match the chapter's output.
- Exercise 3 no longer states its own answer ("does not matter")
  inside the prompt; it now asks for the prediction and an explanation
  of what you find. The solution already carries the reasoning.
- Conditionals: dropped "also" from the comparison-chaining sentence
  (it collided with "also shows" two sentences later), and changed
  "Adding `elif` ... chains multiple tests" to "tests several
  conditions in order", so "chain" is not reused for a different
  mechanism lines after comparison chaining is introduced by that word.
- Comprehensions intro: "`list`, dictionary, or set" had backticks on
  only the first word; now all three are plain prose.

## Considered and declined

- The Loops section formally introduces `for` and `range()` ("`for`
  walks any iterable directly", "Use `range()` for counting") only
  after `break_continue.py` and `loop_else.py` have used both. Moving
  that paragraph up would split the range/enumerate/zip cluster it
  anchors, and the audience has been reading `for x in container`
  since Tour's truthiness listing and throughout Containers, so the
  late formality costs little. Left in place.
- `while_loop.py` (Collatz) opens the section above minimal
  complexity for a first `while` listing. Kept: a loop whose
  iteration count is unknowable in advance is exactly what motivates
  `while` over `for`, and the body reuses the conditional expression
  taught a page earlier.
- `demonstrate_exceptions.py` discards `checked_divide()`'s return
  value. Binding and printing it in the `else` would demonstrate
  try-assigned names surviving into `else`, but muddies the
  try/except/else/finally shape the listing exists to show.
- `assert` is absent from the chapter. It is taught in
  Testing (chapter 11), its natural home.
- No exercises on EAFP, the walrus, or `zip()`. The set at nine covers
  the chapter's main claims (loops and their `else`, the mutation
  trap, exceptions and chaining, `match`, `with`, comprehensions)
  without bloating.
