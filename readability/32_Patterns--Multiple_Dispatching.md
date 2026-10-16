> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: 32_Patterns--Multiple_Dispatching

The chapter reads as finished technical prose.
It has no AI-vocabulary clusters, no curly quotes or spaced ` -- `, no signposting, and no staccato runs. Its sentence lengths vary.
Every watch-list hit in the prose is a keep: four uses of "exactly" mean a precise match, "itself included" is reflexive, and the two "even"s carry a scalar claim that exercise 9 quotes.
Two sentences in the paragraph that introduces the table version made a vague or inaccurate claim. Both were fixed directly.
This file holds no live block, so it is the applied-directly record.

## Applied directly

- Line 202, pointer with two candidates: "The table version keeps the checking and declares each name once" -> "... and repeats no method names". "Each name" could be read as the class names, which the table repeats in its keys; the new wording answers line 200's "repeats every class's method names" directly.
- Line 207, wrong actor: "so a new class inherits `compete()` and adds rows instead of methods" -> "... and needs rows instead of methods". A class cannot add rows to `OUTCOME`, which sits outside it (exercise 1 adds them by hand).

## Considered and declined

- Lines 6 and 17, the repeated "end up testing ... by hand". The first sentence names the symptom and the second gives its cause (one dispatch at a time), closing the loop on the opening. Kept.
- Lines 27-28, "Runtime dispatch resolves on the type of one object, the one receiving the method call," which restates line 16. It brings the problem back after the three-forms digression and sets up "The solution is *Multiple Dispatching*" on the next line. Kept.
- Lines 31-33, "Two unknown types means two dispatches", restating line 31. The sentence exists to attach the term *double dispatching*. Kept.
- Lines 175-177, "Its class is `Paper`. Its name says `Scissors`. Which item does that method's result describe?" Two short sentences and a question by shape, but they stage the exact confusion the paragraph resolves, and the question is the content (recurring keep).
- Line 12, "how can you get them to interact properly?" The question is the chapter's problem, which the next sections answer (recurring keep).
- Line 314, "Adding a new `Item` then means adding rows to the table and leaving the classes as they are," the third statement of this point (207, 271). Line 356's "closed the way the table is" leans on it. Kept.
- Line 418, "Most programmers first write a third version." An unsupported generalization by §5's shape, but it is the author's framing of the familiar `isinstance()` ladder and is not a vague authority. Kept.
- Line 421, "It works." A one-beat concession among long sentences (recurring keep).
- Line 434, "so even elaborate behavior fits the table." "even" is on the avoid tier, but it marks a scalar claim, and exercise 9 quotes the sentence verbatim. Kept.
- Line 630, "That is the standard convention rather than a shortcut." The contrast answers the reader's suspicion that `-> Meters` is lazy, which the next three sentences then refute. Kept.
- Line 276, "a table you are still filling in." "in" is the particle of "fill in", not a stranded preposition.
