> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 25_Patterns--Template_Method

This chapter carried almost no AI-writing tells, and a watch-list scan of its prose found no hits.
One fix had one sensible answer and is applied below.
The file holds no live block, so it is the record of the applied change and of the findings judged and kept.
`readability_db.md` was read first, and no prior `readability/~25_*` review exists.

## Applied directly

- Line 142, §24 hedge: "and it can use the standard library's `difflib`" -> "and uses the standard library's `difflib`".
  `near_miss.py` calls `get_close_matches()` in every `__init_subclass__()` run, so "can use" understated what the listing does.

## Considered and declined

- Line 8, "At the heart of a framework is the *Template Method*".
  A §4 figure by shape, but it is the chapter's opening sentence, first-edition voice, and the sole figure of its kind in the chapter.
- Lines 361-362, "An unexpected exception, an empty step the flow needs, and a skipped pass each change what the anchored algorithm does."
  Restates the three failures from lines 323-326 (treadmill test), but the earlier list says they pass the type checker and this one says they change the algorithm's behavior, which is a different claim, and it sets up the next sentence about empty steps.
- Lines 365 and 463, "faithful substitute".
  §35 lists "faithful" on a technical noun, but the chapter's own listing is `faithless_step.py`, so the word pair is the chapter's deliberate vocabulary for Liskov substitution.
- Line 449, "An anchored algorithm is only as secure as its anchor."
  §32 aphorism by shape, but it opens the closing section rather than ending it, and the list that follows delivers the concrete claim item by item.
- Lines 452-465, the four bullets with a label and a period ("- Structure, in `template_function.py`.").
  §58 by shape. `readability_db.md` records this list's uniformity as a decision table the book keeps, and each label is followed by several sentences, which a colon would not introduce cleanly.
- Lines 109, 214, 432, and 461 each say that only the type checker enforces `@final`.
  The repetition is the chapter's thread: each time it sets up the contrast with a runtime anchor (`__init_subclass__()` or the function form).
