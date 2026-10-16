> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: Changing the Interface, Solutions

The Solutions file for chapter 29 carries no Tier 1 or Tier 2
vocabulary, no signposting, and no significance inflation.
Most of the nine direct edits split an "and" that joined clauses with
different subjects, where the relation was a consequence or a contrast.
One rewrites exercise 5's last step, whose first sentence repeated its
bold label.
Edited paragraphs are rewrapped to the file's 70-column hand wrap.
One block remains: a "so" in exercise 3 that claims a cause the code
does not support, where the fix depends on what the paragraph is meant
to say about `@staticmethod`.

## Applied directly

- Lines 17-18 (hint 1), "and" joining different subjects: "not through `__getattr__()`, and that rule explains what `len()` does" -> two sentences.
- Lines 89-90, "and" joining different subjects: "`append()` changes the list, and the adapter's `pairs` field refers to the same list" -> two sentences.
- Line 282, "and" hiding a consequence: "marks them as private, and `from shop import *` skips them" -> "private, so `from shop import *` skips them".
- Lines 301-302, "and" joining two claims with different subjects: "supports the underscore convention and `__all__`, and Python runs its top-level code once" -> two sentences.
- Lines 341-342, "and" hiding a contrast: "The caller asks for `read()`, and the wrapped object offers `next_chunk()` instead" -> two sentences. (Close alternative: ", but the wrapped object".)
- Lines 350-351, "and" hiding a contrast: "Both wrappers forward, and only the *Adapter* changes the name" -> two sentences.
- Lines 361-362, "and" hiding a contrast inside a "because" clause: "to a few names and each of these wraps one object" -> "to a few names, while each of these wraps one object" (a period would cut the reason in half).
- Line 538, "and" hiding a consequence: "has no parameter named `what_i_want`, and the call raises a `TypeError`" -> ", so the call raises".
- Lines 541-546, label echo and "and" splice: "**Keep the base parameter's name.** The fix keeps the base class's parameter name, `what_i_want`. ... It also accepts the keyword every `WhatIUse` caller uses." -> "`WhatIUse2.op()` names its parameter `what_i_want`, as the base class does, so it accepts the keyword every `WhatIUse` caller may pass. It still widens the type to the union, ..." The "may pass" matches line 438's wording; "uses" overstated it, since a positional caller passes no keyword.

## Exercise 3: the "so" before `@staticmethod` (lines 298-299)

> None of these functions uses `self`,
> so `@staticmethod` makes Python call each one with the caller's arguments alone.

The "so" reads as cause and effect, but not using `self` does not
cause `@staticmethod` to do anything.
The decorator's behavior holds either way.
And `Facade.start_car()` called on the class works without the
decorator, since a function read through the class binds nothing; the
decorator matters when someone calls the method through an instance.
So the sentence's real claim is unclear: why the class version carries
`@staticmethod`, or what the decorator does.

Proposed, if the point is what the decorator does:

> None of these functions uses `self`.
> `@staticmethod` makes Python call each one with the caller's
> arguments alone, even through an instance.

The "even through an instance" adds a fact the file does not state,
which is why this is a block rather than a direct edit.
The other choice is to cut the sentence, since the paragraph's argument
(the class version adds a `class` statement and a decorator per
function, the module adds nothing) stands without it.

[] Reject

## Considered and declined

- Line 278, "The caller sees one function.": the output two paragraphs later shows `record` as well, but the next paragraph explains that name, and the caller's own code imports one function.
- Lines 176-179, "A library that subclasses a deprecated class emits the warning as soon as Python imports that library": close to the module-level sentence before it, but it names who sees the warning, a library's users, which is the practical consequence. The lines' long wrap is the bold-label insertion's, left as it stands.
- Line 287, "A real module therefore either sets `__all__` ...": §34 by shape, but "real" contrasts with the exercise's teaching module, named in the same paragraph.
- Lines 336 and 358, "What you lose is the log." and "What you lose is control over ...": a cleft with a noun-phrase complement, repeated on purpose to answer the exercise's "say what you lose" for each wrapper.
- Line 364, "Purpose, not code, decides the classification.": §47 shape, but the contrast is the paragraph's claim, which the next sentence supports with the single `__getattr__()` forwarder.
- Lines 304-308, the four-sentence run ending "Neither version enforces privacy.": a side-by-side comparison of what each caller sees, not staccato drama.
- Line 170, "A caller who wants to act on the warning": "want" with a human subject (recurring keep).
- Line 195 (hint 3), "A module is already a namespace": "already" marks work the reader does not have to do (recurring keep).
- Line 351, "Only the *Adapter* changes the name": a ruled-fine "only the X" shape.
