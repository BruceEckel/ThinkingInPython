> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability: 44_Effects--Effect_Management

Readability pass over chapter 44 (2026-10-16).
No earlier review of this chapter exists in `readability/`, so `readability_db.md` was the carry-forward.
The chapter reads clean of AI-vocabulary clusters, staged reveals, and filler adverbs.
The findings were mostly the global rules' "and" joining two subjects, plus one stalling question and one metadiscourse sentence.
Seven edits were applied directly; one block asks what a sentence's reason is meant to claim.

## Applied directly

- L226, split "and" with a subject change: "The specifications exposed implementation details, and most people now count them a failure." -> two sentences.
- L376, §43 self-answered question: "What do you gain by keeping the rest pure? The first and most obvious answer is parallelism." -> "The most obvious gain from keeping the rest pure is parallelism."
- L404, split "and" (the relation is "but"): "A test must run in an environment it controls, and an untracked Effect is part of the environment outside that control." -> two sentences.
- L416, split "and" (consequence) and a colon that pointed at nothing named: "..., and that makes code hard to understand:" -> "... leave out. The omission makes code hard to understand, and leaves these questions open:".
- L465, §70 metadiscourse: cut "The difference between it and the whole list matters in the chapters that follow." and merged "The first item can stand alone" with the definition into "On its own, the first item is *Effect tracking*." The dropped definition sentence ("*Effect tracking* tells you which Effects a function can perform") restated item 1 of the list just above; the forward pointer at the paragraph's end ("Tracking alone appears twice later in this chapter") still carries the concrete reason the distinction matters.
- L492, split "and" (the relation is "while"): "Variation concentrates at the edge of the program, and the functions below it stay simple and uniform." -> two sentences.
- L924, split "and" (the relation is "but"): "Each of these supplies part of an EMS, and none supplies all three parts." -> two sentences, so "None supplies all three parts." sits against the next paragraph's "One library supplies all three parts."

## Live blocks

### L75: the reason a side effect is easy to spot

"Explain enough" (global rules).
The sentence reads:

> A side effect is easy to spot in the function that performs it,
> because the side effect changes something outside that function.
> One call up, the side effect is invisible.

The "because" clause gives the definition of a side effect, not the reason it is visible in its own function.
The contrast with "One call up" suggests the intended reason is that the operation sits in that function's body, where a reader sees it.
Proposed:

> A side effect is easy to spot in the function that performs it,
> because the operation that changes the environment sits in that function's body.
> One call up, the side effect is invisible.

A block rather than a direct edit because it changes what the sentence claims as its reason.

[] Reject

## Considered and declined

- L368, "is a space heater with extra steps." A §32 kicker by shape, but it is the author's joke landing the `pure_and_pointless.py` demonstration, and it carries the claim (CPU work with no observable result).
- L370, "Effects are not a defect to design away. They are the reason a program exists." §9 by shape; the negation is half of a real contrast.
- L336 "not even the exit code" and L708 "A handler can even invoke the continuation several times": "even" marks the end of an escalation in both (the last output channel; the capability `except` lacks), so it states the claim rather than emphasis.
- L944, "Could Python itself gain Effect tracking ...?" The rhetorical question is the section's content (the paragraph answers it), and "itself" draws the language-versus-library contrast with Stateless just above.
- L105, "Does the exception break purity?" Same keep: the two-answer list that follows is the content.
- L449 and L613: "A native system adds each Effect for you. A library like Stateless has you declare each one ..." is restated 160 lines later ("A native system maintains it for you. With a library like Stateless, you write the declarations ..."). The second sits after the `ContextVar` paragraph's "The type checker can no longer verify it" and sets up the "second channel"; the repetition reorients rather than pads.
- L216, L411, L1012: "An Effect Management System replaces ..." / "moves the bookkeeping into the type system" recur as the chapter's refrain, each closing a different argument (callee reading, inspection, the barrier history).
- L969, "The history of programming is a history of scaling barriers." §32 by shape, but it states the section's thesis, which the namespace, version-control, testing, and garbage-collection examples then support.
- L1022, "Effect tracking will look obvious in hindsight ..." A prediction, but the author's stated conviction closing the barrier argument, not a §49 generic closer.
- L985, the ` -- ` inside the Zen of Python quotation: secondhand text, quoted as Python prints it, already fenced with a Vale suppression.
- L1000-1006, "We build programs ...", "It might ... It might ... It might ...": Bruce's "we" and a deliberate anaphora.
- L1039, exercise 1's "Serving a new context without edits is what delayed binding provides." The "is what" complement is a clause that cannot attach without it.
