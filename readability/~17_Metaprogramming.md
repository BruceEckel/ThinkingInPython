[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/17_Metaprogramming.md`

This chapter reads as human-written throughout.
A full sweep for Tier 1A vocabulary (§7) turned up zero hits, as did the checks for chatbot artifacts (§20), cutoff disclaimers (§21), boldface overuse (§15), curly quotes (§19), significance inflation (§1), and vague attribution (§5).
The four findings below are all P2 polish: one redundant tail clause, one announcement sentence, one inaccurate "from X to Y" range, and one short bullet list that reads better as prose.

***

[] Reject

**Section:** Intercepting Instance Creation
**Pattern:** §23 Filler Phrases (P2)

Current:
> It is the same method that makes any object callable when it is called.

Proposed:
> It is the same method that makes any object callable.

Why: The trailing clause is circular (an object is callable "when it is called") and the next sentence, `obj()` invokes `type(obj).__call__(obj, ...)`, already supplies the mechanism.
Deletion test: the sentence means the same without it.

***

[] Reject

**Section:** Multiple Inheritance in a Metaclass
**Pattern:** §28 Signposting and Announcements (P2)

Current:
> That raises a natural question.
> Can a metaclass inherit from more than one class, the way an ordinary class can?

Proposed:
> Can a metaclass inherit from more than one class, the way an ordinary class can?

Why: The first sentence announces that a question is coming instead of asking it, and "natural" does no work.
The question itself is earned by the two sentences of setup above it and is answered immediately, so it stands on its own.

***

[] Reject

**Section:** The `inspect` Module
**Pattern:** §60 Excessive Bullet Lists (P2, borderline)

Current:
> It answers questions like:
>
> - Which members an object has
> - What a function's signature is
> - What its docstring says

Proposed:
> It answers questions like which members an object has,
> what a function's signature is,
> and what its docstring says.

Why: Three short parallel clauses broken into bullets, immediately followed by a second bullet list (the four `inspect` functions) that is genuine reference content.
Running the first as prose keeps the bullets for the list that needs them.
Borderline: three items is under the §59 threshold, and the bulleting may be a deliberate choice.

***

[] Reject

**Section:** The Tool in Use
**Pattern:** §12 False Ranges (P2)

Current:
> The rest, from `__class__` to `__static_attributes__`,
> is the bookkeeping every class carries.

Proposed:
> The rest is the bookkeeping every class carries.

Why: The named range does not actually span "the rest": the listing above it also includes `__annotations_cache__`, which sorts before `__class__`, and `__weakref__`, which sorts after `__static_attributes__`.
Cutting the range removes the inaccuracy without adding any claim the chapter does not already make.
