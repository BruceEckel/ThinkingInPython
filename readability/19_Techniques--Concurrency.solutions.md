> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

Readability review of `Solutions/19_Techniques--Concurrency/README.md`,
2026-10-16.
The prose carried no AI-vocabulary clusters and no watch-list hits
that needed changing. The findings were mostly "and" joining clauses
with different subjects, two short restatements, and one pointer with
two candidates. Eleven fixes went in directly, and no finding needed
Bruce's judgment, so this file holds no live block and serves as the
applied-directly record.
The `main()` pointer in solution 15 and the "original version" claim in
solution 11 were checked against `mixed_await.py` and `context_var.py`
in the chapter.
`tip verify-ch CH=19 ISOLATED=1` passed, 27 of 27.

## Applied directly

- Line 511, "and" joining clauses with different subjects, plus §34
  "real": "The `RuntimeError` comes from a safety check, and the
  recursion is the real failure." became "The recursion is the failure.
  The `RuntimeError` comes from a safety check against it."
- Line 596, one concept per paragraph: the free-threaded sentence and
  "The fix is a lock ..." now start their own paragraph, apart from the
  standard build's switch points.
- Line 838, §70 metadiscourse: "What a `TaskGroup` cannot undo matters
  when the tasks do more than sleep. A group of six writes ..." became
  "When the tasks write to a database instead of sleeping, a group of
  six writes ...". The database comes from the paragraph above.
- Line 909, unclear consequence: "The type checker passes that
  version, so Python reports the failure at run time." became "... so
  the mistake shows up only at run time."
- Lines 1003-1009, treadmill: "Every task reads `main`, where each task
  in the original version read the name of its own request." repeated
  the paragraph's first sentence. Its contrast moved into that first
  sentence ("All three tasks print `context main`, where each task in
  the original version printed the name of its own request.") and the
  repeat was cut.
- Line 1229, "and" joining different subjects: "A lock protects the
  statements it encloses, and a `for` loop calls `next()` ..." became
  two sentences.
- Line 1316, "and" joining different subjects: "The first task
  finishes and releases both locks, and the second task then finds ..."
  became two sentences.
- Line 1325, "and" joining different subjects: "... than every lock it
  holds, and "later" never loops back ..." became two sentences.
- Line 1346 (hint), "and" joining two separate hints: "The bridge is
  `loop.run_in_executor()`, and the `ExceptionGroup` comes from ..."
  became two sentences.
- Line 1385, "and" joining different subjects: "... like any other
  `await`, and the loop keeps running the other two tasks in the
  meantime." became "... like any other `await`. In the meantime the
  loop keeps running the other two tasks."
- Line 1392, pointer with two candidates: "`main()` has no `except*`"
  came right after a sentence about `task_group.py`, so it now reads
  "`mixed_await.py`'s `main()` has no `except*`".

## Considered and declined

- Line 444, watch word "Exactly": "Exactly half the increments
  survive." The marker reads 200 of 400, so this is a precise numeric
  match, the case the rule allows.
- Line 329, "Waiting does not create overlap. Suspending does." A
  negative and its positive form side by side make a deliberate beat,
  and the contrast is the claim.
- Line 834, §34 "a real `fetch()`": the contrast with the demo's
  sleeping `fetch()` is named, so it stays.
- Line 455, treadmill: "That second holder reintroduces the race the
  lock is there to prevent." It partly repeats "Admit a second holder,"
  but it ties the race back to the lock comparison that the paragraph
  draws.
- Lines 830-832, the bold label "**Cancel what is still running.**"
  followed by "A `TaskGroup` cancels what is still running". The label
  echoes the sentence, but bold step labels are a Solutions convention,
  and the sentence goes on to explain the original `FETCHES`.
- Lines 1088-1093, solution 12 states that the results agree three
  times (the reason, "Five calls therefore produce the same five
  results", and "Swapping the executor changes when the work runs, not
  what it computes"). Each adds a step: the claim, its derivation, and
  the general rule. Left alone.
- Line 1019, "which is the contrast the example exists to draw": a
  borderline §70 aside, but it tells the reader why `current` is in the
  listing, which the paragraph then explains.
- Solution 10's paragraph about the `return` sits between the opening
  paragraph and the "Propagate the first failure" step. Moving it to
  the end would close the solution on a side note instead of the
  `return_exceptions`/`TaskGroup` conclusion, so it stays.
- The prose's hand-wrapping is uneven in several places (lines 145-149,
  236-247, 505-508, 908-918). Rewrapping changes no wording, so only
  the edited paragraphs were rewrapped.
