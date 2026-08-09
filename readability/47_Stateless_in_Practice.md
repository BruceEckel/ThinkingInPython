> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/47_Stateless_in_Practice.md`

Second review of this chapter.
The findings in `readability/~47_Stateless_in_Practice.md` were all accepted and
applied, and none were rejected, so nothing is carried forward.

The deep review that ran just before this one cut the
`Why retry() Decorates the Function` subsection, retitled two headings, added a
motivation sentence to "Abilities Are Not Special", tightened the type-bound
paragraph, added three explanatory sentences and a closing paragraph, and added
three exercises. Every finding below is in that new or rewritten prose.

---

**The renamed final section: "One Type for Four Mechanisms" names an argument
the section makes third, not first.**

The section now opens on adoption advice ("Use Stateless when a system is large
enough that hidden Effects have already cost you a production incident"), then
the new habit paragraph, then the direction, and the four-mechanisms argument
sits in the middle. A reader who arrives via the heading looks for the four
mechanisms and finds a verdict.

The deep review offered two candidate titles and did not pick one. Having read
the section again with the new closing paragraph in place, I think neither
quite fits, because the section now does three things: it weighs adoption, it
names the habit that outlives the library, and it makes the composition
argument.

Proposed change: title it for the thing the reader takes away rather than for
any one of the three.

> ## What Survives the Library

That covers the habit paragraph (which is now the section's most useful
sentence-for-sentence content), sets up the adoption advice as the question it
answers, and still fits the closing line about capacity.

Alternative, if you prefer the deep review's framing: keep "One Type for Four
Mechanisms" and move the composition paragraph to the top of the section, so
the heading describes the opening rather than the middle. That is a bigger
edit and reorders the book's last section, which is why I list it second.

[] Reject

---

**The new closing paragraph: "Name each contact with the outside, the clock,
the feed, the pool, the console, and bind it at the edge" has four commas doing
two different jobs.**

> Name each contact with the outside, the clock, the feed, the pool, the console,
> and bind it at the edge instead of calling it in the middle.

The middle four commas separate a list of examples; the outer two attach that
list as an appositive and then resume the sentence. The reader meets "the
clock" and cannot yet tell whether it is a second thing to name or a gloss on
the first, and the resumption at "and bind it" reads at first as the fifth list
item.

The deep review's draft used em dashes here, which would have solved it, and
those are yours to write rather than mine.

Proposed change without them, using parentheses:

> Name each contact with the outside (the clock, the feed, the pool, the console)
> and bind it at the edge instead of calling it in the middle.

Alternative, splitting into two sentences:

> Name each contact with the outside and bind it at the edge,
> instead of calling it in the middle.
> The clock, the feed, the pool, and the console are all such contacts.

I recommend the parentheses. The list is an aside, and the second version gives
it more weight than it needs at the end of a book.

[] Reject

---

**"Abilities Are Not Special": the new motivation paragraph answers a question
the reader has not been asked yet.**

The section now opens:

> A `Need` asks for an instance and gets whatever was supplied.
> Your own Ability can ask for anything you can name,
> and the handler answering it is an ordinary function,
> so the answer can differ every time it is asked.

This is the right content and it fixed a real problem: the section used to open
with reassurance rather than motivation. The seam is that it opens on a
contrast with `Need` before saying what the section is about, so the first
sentence of the last chapter's last major idea is a comparison to something
from the previous chapter.

Proposed change: state the subject, then the contrast.

> A custom Ability is a request you design.
> A `Need` asks for an instance and gets whatever was supplied;
> your own Ability can ask for anything you can name,
> and the handler answering it is an ordinary function,
> so the answer can differ every time it is asked.

One added sentence, and the paragraph now opens on its own topic.

[] Reject

---

**"Switching Implementations Mid-Run": the new `catch()` sentence repeats the
word "yield" three times in two lines.**

> `catch()` matches yielded values, and a handler yields nothing,
> so no `catch()` around this program intercepts it.

The sentence is doing exactly the job the deep review wanted (naming the
mechanism rather than only the outcome), and the repetition is the cost of
saying it compactly. It reads as a tongue-twister on the first pass.

Proposed change:

> `catch()` matches values an Effect yields, and a handler is not part of the
> Effect, so no `catch()` around this program intercepts it.

That also states the more useful fact. The reason is not that handlers happen
not to yield, it is that a handler sits outside the channel entirely, which is
what the sentence after it already says ("A handler sits outside the channel it
feeds"). The two now agree instead of offering two different reasons.

[] Reject

---

**"The Success Path": the new `topic_of()` explanation ends on a sentence that
generalizes further than the paragraph earns.**

> `topic_of()` is written out again because `research.py`'s version is decorated:
> it returns an Effect, and ordinary `try`/`except` code cannot call it.
> Lifting a function takes it away from its unlifted callers.

The first two lines are the explanation and they are exactly what the listing
needed. The third is an aphorism, and it overstates: an unlifted caller can
still call a lifted function, it just has to `run()` it, which this chapter has
shown a dozen times.

Proposed change: cut the third line, or make it accurate.

> `topic_of()` is written out again because `research.py`'s version is decorated:
> it returns an Effect, and ordinary `try`/`except` code cannot call it directly.

I recommend the cut with "directly" added, since that one word carries the
qualification the aphorism was missing.

[] Reject

---

## Checked and clean

- Zero hits across the §7 Tier 1A, 1B, 2, and 3 vocabulary tables in the new
  prose.
- `banned_phrases.py` and `prose_lint.py` both pass on the chapter. The deep
  review's draft closing paragraph contained "reaching for", which was replaced
  with "calling it in the middle" before it was applied.
- No em dashes, no spaced ` -- `, no curly quotes, no boldface, no emojis, no
  slot-fill placeholders.
- `### 4. The discipline is all-or-nothing` now matches its four siblings, which
  all state a limit as a sentence. Scanning the five headings works again.
- The new intro line ("The chapter then collects every tool in one table and
  weighs what the whole approach costs") was checked against both sections it
  announces. Both exist and both do what it says.
- The two-sentence replacement for the cut `Why retry() Decorates the Function`
  subsection was checked against chapter 46's `An Effect Runs Once`, which now
  carries the explanation. The claim is not repeated, only cited, which is what
  the cut was for.
- The three new exercises were checked against their solutions. Exercise 12's
  two annotation-deletion questions have different answers (one silently
  weakens caller checking, one raises at decoration time), which is what makes
  the pairing worth asking.
