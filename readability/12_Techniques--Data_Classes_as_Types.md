> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Data Classes as Types

This chapter carries few AI-writing tells.
Earlier passes have already cleared the watch-list vocabulary, the colon reveals, and the empty adverbs,
and the remaining hits are keeps that `readability_db.md` covers.
This run applied three fixes directly and leaves no live block,
so this file is the record of those changes and of what was considered and declined.

## Applied directly

- Line 977, comma splice plus a positive restatement: "A month is not an `int`, it carries one, and `max_days` reads the number through `.value`." -> "A month carries an `int` rather than being one. `max_days` reads that number through `.value`." The "and" joined two subjects whose relation was evidence, not addition, so it became a period.
- Line 1078, §52/§69 staged reveal: "It gains one thing:" -> "It gains one thing, a check that the factory builds the type the annotation names:". The listing shows the failure of `Unchecked`, not the gain, and the gain itself waited three paragraphs (the "Subscripting makes the factory's return type concrete" paragraph). The lead-in now states it before the listing. Checked against line 1119, which says `dict[int, int]` on that field draws a type error.
- Line 1641, §53 endorsement frame: "the overhead is [worth measuring](...)" -> "[measure the overhead](...)". The link target is unchanged; the sentence now gives the instruction the "worth" frame only rated.

## Considered and declined

- Line 105, "Nothing objects: not the annotation, not the type checker, not the running program." A colon by shape, but the global style guide cites this sentence as a correct colon. Line 1104's "Nothing objects to `Unchecked`." echoes it on purpose.
- Line 275, "Copying instead of mutating reduces errors." A portable claim by the portability test. The chapter supports it at length afterward (Immutability, Parse, Don't Validate), and a sharper version would add a claim the sentence does not make.
- Line 325, "For clarity, `show()` also excludes `__hash__`". "For clarity" is thin as a reason, but the link to `#data-classes` carries the real one (a mutable data class sets `__hash__` to `None`), and spelling it out here would repeat line 235.
- Lines 437 and 439, "A Real `ClassVar`". §34 by shape; the contrast is named, against `B`'s `[CV]` class variables that carry no `ClassVar` annotation, and line 437 is a heading.
- Lines 687-689, "holding the type is proof the check passed. No other code repeats the check, because it cannot fail. Illegal values are unrepresentable." Three short closers in a row, but each makes a separate claim, and the last is the slogan the section names.
- Line 695, "states more than a type: the value passed the check." The colon passes the "namely" test.
- Line 803, "especially useful at the edges of a program". A single §42 cue with its reason in the same clause.
- Line 1400, "is what you do with any immutable value". The complement is a clause that cannot attach without "is what" (recurring keep).
- Lines 1184 and 1201, "quietly" and "silently". Each states the claim (no error is reported), not emphasis.
- Lines 1327 and 1329, "plain subclass" and "plain base". "Plain" names the contrast with a frozen data class, as the section heading does.
