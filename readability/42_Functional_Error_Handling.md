> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/42_Functional_Error_Handling.md`

Second review of this chapter.
All four findings in `readability/~42_Functional_Error_Handling.md` were accepted
and applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one added `@final` and a generic error
parameter to `utils/result.py`, a `must_unwrap.py` listing, a `combining_two.py`
listing, a `safe_demo.py` split out of `utils/safe.py`, three exercises, a new
`## Which Failures Get a Result` heading, and a capability paragraph at the end.
It also moved `test_result.py` into "Composing With bind" and shrank the
narrowing paragraph after `noted_result.py` from nine lines to three.

Most findings below are in that new prose. The first is not: it is a sentence
the previous deep-review pass introduced and this one left in place.

---

**"A Result Type": "`unwrap()` is what makes that literal" is a cleft that
delays its own verb.**

> To get the answer, the caller must unpack the `Result`.
> `unwrap()` is what makes that literal: it is defined on `Ok` and not on `Err`,

The global rules name this construction directly: cut "is what" when deleting it
changes nothing, and the giveaway is a verb immediately after it. Here the verb
is "makes," and "`unwrap()` makes that literal" says the same thing one word
sooner.

Proposed change:

> `unwrap()` makes that literal: it is defined on `Ok` and not on `Err`,

Worth noting because this sentence now sits four lines above a new listing that
demonstrates the same claim, so the paragraph is the most-read part of the
section.

[] Reject

---

**`must_unwrap.py` follow-up: four sentences to explain a two-line listing, and
the middle two overlap.**

> The `# type: ignore` is the point of the listing rather than an apology for it.
> Without that comment `ty` refuses the line,
> reporting that `unwrap` is not defined on `Err[str]` in the union,
> and a reader who writes this in their own code never reaches the traceback.
> The comment suppresses a real error so the listing can show what the checker was preventing.

The first and last sentences say the same thing: the ignore comment is
deliberate, and it exists to reveal what the checker blocks. The middle sentence
carries the new information.

There is a second problem. "reporting that `unwrap` is not defined on `Err[str]`
in the union" repeats, nearly word for word, a clause eleven lines above it in
the same section ("which reports that `unwrap` is not defined on `Err[str]` in
the union"). The listing was added precisely so the prose would not have to
assert this, so the assertion above it is now the redundant one.

Proposed change: cut the closing sentence here, and cut the earlier assertion
where the listing now covers it.

> The `# type: ignore` is the point of the listing rather than an apology for it.
> Without that comment `ty` refuses the line,
> and a reader who writes this in their own code never reaches the traceback.

with the earlier paragraph shortened to:

> `unwrap()` makes that literal: it is defined on `Ok` and not on `Err`.
> Using the `Result` as if it were a number fails the same way.
> Narrowing to one of the two classes is the only route to the answer.
> The asymmetry is visible at runtime as well as to the checker:

I recommend taking both halves together. Taking only the first leaves the
duplicate claim standing.

[] Reject

---

**"Which Failures Get a Result": the new closing paragraph announces itself.**

> What you can do now that you could not at the start of the chapter:
> write a function whose signature admits it can fail,
> and chain three of them without a single `try` in the calling code.

The opening clause is the deep-review checklist's question quoted into the
chapter. It frames the capability instead of stating it, which is the §70 gloss,
and "what you can do now that you could not at the start" is a sentence about
the chapter rather than about the reader's code.

Proposed change:

> You can now write a function whose signature admits it can fail,
> and chain three of them without a single `try` in the calling code.
> The chain either delivers an answer or hands back the first failure,
> and the checker will not let a caller confuse the two.

The claim survives intact and arrives two clauses earlier.

Alternative, if you want the retrospective framing kept: move it to the start of
the sentence as a short adverbial, "By this point you can write a function...".
I recommend the first; the second still spends words on the frame.

[] Reject

---

**`combining_two.py` follow-up: "That scoping is the reason for the nesting" and
the sentence before it make one point twice.**

> Each lambda's parameter is the previous step's answer,
> and the answers stay reachable because the nesting keeps them in scope:
> `a` is still visible inside the inner lambda where `b` arrives.
> That scoping is the reason for the nesting,
> and it is what a flat sequence of `bind()` calls could not give you.

The first two lines state that nesting keeps the answers in scope, with a
concrete instance. The fourth line states that scoping is the reason for the
nesting. That is the same fact with subject and predicate swapped.

The genuinely new content is the last clause, about what a flat chain cannot do,
and it is worth keeping because it answers the question a reader has at exactly
this point.

Proposed change:

> Each lambda's parameter is the previous step's answer,
> and the answers stay reachable because the nesting keeps them in scope:
> `a` is still visible inside the inner lambda where `b` arrives.
> A flat sequence of `bind()` calls could not give you that,
> because each step would see only the value handed to it.

The added clause explains the contrast rather than asserting it, which the
original last line did not.

[] Reject

---

**`@final` explanation: "narrow a `Result` to exactly one of the two" states the
effect without the cause, three sections before the cause matters.**

> `@final` states that neither will be subclassed,
> which lets the checker narrow a `Result` to exactly one of the two.

A reader meeting this at the class definition has no reason to care yet, and no
way to see why subclassing would prevent narrowing. The mechanism (a value could
otherwise inherit from both classes, so a positive `isinstance()` cannot rule
either out) was in the chapter until this pass, in the paragraph after
`noted_result.py`, and the shrink removed it.

Proposed change: keep this sentence as the short forward reference it is, and
restore one clause of the mechanism where it now pays off, in the narrowing
paragraph:

> The `Err` branch reads `error.__notes__`,
> which checks because `@final` on the two classes rules out a value that
> inherits from both, leaving the checker one class to narrow to,
> whether you use `match` or `isinstance()`.

This costs one line and puts the reason where the reader is looking at the
consequence.

Alternative: leave both as they are. The chapter is correct either way, and the
deep review shrank this paragraph deliberately. I recommend the change, because
"lets the checker narrow" is currently asserted twice and explained nowhere.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- The new monad sentences ("`Maybe` chains a value that might be absent,
  `Result` chains one that might have failed, and an async container chains one
  that has not arrived yet") are a rule of three, but the three are the three
  cases chapter 39's catalog entry names, so the count is the content. Not
  flagged.
- "Python's untagged spelling of a *sum type*" uses "spelling," which the global
  watch list bans as a metaphor for how something is written. Here it is the
  established type-theory sense (an untagged versus tagged encoding of the same
  construct) and it sits against "tagged union" three paragraphs later, so it is
  the technical term rather than the metaphor. Not flagged, but worth a second
  opinion since the word is on the do-not-use list.
- The `safe_demo.py` lead-in ("Decorating a function that raises an exception is
  all it takes") was checked against the imperative-plus-consequence ban; it is
  a statement, not a command followed by its result.
