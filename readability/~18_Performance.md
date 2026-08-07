[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading `~` to indicate completion.

# Readability review: `Chapters/18_Performance.md`

This chapter reads as human technical prose throughout: varied sentence length, concrete
numbers ("about 22,000 times faster," "344 bytes against 48"), and real hedging about
measurement noise. A vocabulary sweep for Tier 1A/1B/2 words turns up almost nothing.
The few findings below are isolated: one Tier 1A word, one broken pronoun reference,
two bits of metadiscourse, and one restated point. No cluster anywhere.

***

[] Reject

**Section:** Opening (before "Is It Too Slow?"), line 3
**Pattern:** §62 Transition-Phrase Openers (P2)

Current:
> Performance means at least two things when it comes to computing:

Proposed:
> Performance means at least two things in computing:

Why: "when it comes to X" is on the watch list; it pads without connecting, and the
plain preposition says the same thing in four fewer words.

***

[] Reject

**Section:** Lazy Evaluation with Generators, the memory-cliff paragraph
**Pattern:** §70 Interpretive Metadiscourse / treadmill restatement (P2)

Current:
> The slowdown is a cliff, not a slope:
> nothing warns you as the data approaches the limit,
> and everything changes the moment it crosses.

Proposed:
> Nothing warns you as the data approaches the limit,
> and everything changes the moment it crosses.

Why: the paragraph already opened with "The risk is the cliff at the edge of that memory"
and already drew the same contrast at "a thousandfold slowdown, not a modest one," so the
clause before the colon is the third statement of a point the reader has; the two clauses
after it are the only new information.

***

[] Reject

**Section:** Converting a Slow Function to Rust, opening paragraph
**Pattern:** Portability test / vague claim (P2)

Current:
> It also lets you do things that are difficult in Python.

Proposed:
> Cut this sentence.

Why: the sentence names nothing, and the chapter never says what those things are, so
there is no specific here to sharpen it with; borderline, since you may intend it as a
forward pointer to `rust/`, in which case reject this block.

***

[] Reject

**Section:** Converting a Slow Function to Rust, the summary after `demo.py`
**Pattern:** §70 Interpretive Metadiscourse (P2)

Current:
> That closes the arc this chapter has been building:
> one baseline and three ways past it.

Proposed:
> That is one baseline and three ways past it.

Why: the frame is about the chapter's construction rather than about performance, and
the four sentences that follow already show the baseline and the three routes; borderline,
since a deliberate summarizing beat here is defensible.

***

[] Reject

**Section:** Concurrency
**Pattern:** §7 Overused "AI Vocabulary" Words, Tier 1A (P1)

Current:
> If the work can be done in parallel (pure functions can do this seamlessly),

Proposed:
> If the work can be done in parallel (pure functions make this easy),

Why: "seamlessly" is a Tier 1A replace-on-sight word and the only one in the chapter;
"make this easy" carries the same claim without the marketing register.

***

[] Reject

**Section:** Choosing a Strategy, first two lines
**Pattern:** Dangling referent (editing error, outside the §1-§70 set) (P1)

Current:
> Measure first.
> A profiler is how you find them without guessing.

Proposed:
> Measure first.
> A profiler is how you find the slow spots without guessing.

Why: "them" has no antecedent in this section, since the nearest plural noun is in the
previous chapter section; naming the referent costs two words.
