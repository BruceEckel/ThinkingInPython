[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/16_Comprehensions.md`

Run after the deep-review edits landed, so the new prose gets the same scan the
rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human technical prose.
No AI vocabulary hits, no significance inflation, no signposting, no boldface
padding, no curly quotes, no spaced ` -- `.
Five findings, all in prose written during the deep review.

***

[] Reject

**Section:** List Comprehensions (after `map_and_filter.py`)
**Pattern:** out-of-character diction (P2)

Current:
> `map()` and `filter()` are beneficial when the function already exists,

Proposed:
> `map()` and `filter()` pay off when the function already exists,

Why: "are beneficial" is stiffer than the surrounding prose and than the
sentence it is echoing.
[Functional Foundations](40_Functional_Foundations.md) makes the same point as
"earn their keep when the function already exists," and the chapter uses "pays
off" elsewhere for exactly this shape of claim.

***

[] Reject

**Section:** List Comprehensions (end of the walrus paragraph)
**Pattern:** §23 clarity, distant pronoun (P2)

Current:
> Two things it cannot do: rebind the comprehension's own iteration variable,
> and appear in a comprehension inside a class body.
> Both are a `SyntaxError`.

Proposed:
> The walrus cannot rebind the comprehension's own iteration variable,
> and it cannot appear in a comprehension inside a class body.
> Both are a `SyntaxError`.

Why: "it" reaches back past `total`, "the enclosing scope", and "a
comprehension" to find "the walrus operator" three sentences earlier.
Naming the subject also drops the counted-list frame, which the two clauses do
not need.

***

[] Reject

**Section:** Feeding the Iterator Clause (after `zip_unpack.py`)
**Pattern:** watch list, `exactly` (P2)

Current:
> `values` has a third element, and `zip()` drops it, exactly as above.

Proposed:
> `values` has a third element, and `zip()` drops it, as it did above.

Why: the watch list keeps "exactly" for a precise numeric or logical match, and
here it is an intensifier on a comparison that is already exact.

***

[] Reject

**Section:** Feeding the Iterator Clause (end of the `path_walk_comprehension.py` discussion)
**Pattern:** §11 repetition (P2)

Current:
> By then the directory is gone.
> The comprehension finished building `py_paths` as strings while the directory still existed,
> so nothing later needs the files.
> Turning those brackets into parentheses would break it:
> a generator expression would not walk the tree until `sorted()` pulled on it,
> and by then the directory is gone.

Proposed: keep the first four lines and end the new sentence differently:
> Turning those brackets into parentheses would break it:
> a generator expression would not start walking until `sorted()` pulled on it,
> and that pull happens outside the `with`.

Why: "and by then the directory is gone" repeats a sentence three lines above it
word for word, so the new warning reads as a restatement rather than as the new
consequence it is. Naming where the pull happens is the part the reader does not
already have.

***

[] Reject

**Section:** Exercises, exercise 4
**Pattern:** §23 clarity, an instruction that misnames the action (P2)

Current:
> In `set_comprehension.py`, change the filter to keep names of any length,

Proposed:
> In `set_comprehension.py`, drop the `if len(name) > 1` filter,

Why: the answer is to delete the clause, so "change the filter" sends the reader
looking for a new predicate to write.
Naming the clause also makes the exercise readable without opening the file.
