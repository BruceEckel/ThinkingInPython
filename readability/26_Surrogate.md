> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/26_Surrogate.md`

Run right after the deep-review edits landed, so the new `protection_proxy.py`
and `proxy_setattr.py` prose, the moved `__getattr__()`/`__getattribute__()`
paragraph, the identity escape hatches, the rewritten State typing paragraph,
and the rewritten conclusion get the same scan as the older prose.
No completed readability review exists for this chapter, so nothing is
carried forward.

The chapter reads as human prose overall.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation, no rhetorical openers.
Sentence length varies well.
The findings below are mostly single words on the global watch list plus three
sentences that need a real rewrite; the first two are in prose written during
the deep-review pass.

Line numbers refer to the chapter as it stands now.

***

**Line 370 (identity escapes, first sentence)**
**Pattern:** §35 moral-adjective category error, plus §31 manufactured punchline

Current:
> Two escapes exist, and both lie.

An escape hatch cannot lie; only a person can.
The sentence is engineered to land, and the thing it gestures at is stated
plainly two lines later ("Each satisfies the runtime check and neither
satisfies a type checker"), so the drama buys nothing the paragraph does not
already say.

Proposed:
> Two escapes exist, and each makes `isinstance()` answer a question nothing
> verified.

That keeps the warning and names the mechanism instead of assigning a motive.
An alternative, if you would rather not restate the mechanism this early:
cut the clause and open with "Two escapes exist." on its own.
I recommend the first.

[] Reject

***

**Line 186 (after `proxy_2.py`)**
**Pattern:** §4 promotional framing, §8 copula avoidance, §23 empty adverb

Current:
> The beauty of using `__getattr__()` is that the forwarding is completely generic:
> `Proxy` names no method of `Implementation`,
> so it keeps working when the implementation grows a method.

"The beauty of X is that Y" praises before it explains, and the colon already
supplies the evidence, so the praise is scaffolding.
"completely" adds nothing to "generic."

Proposed:
> `__getattr__()` makes the forwarding generic:
> `Proxy` names no method of `Implementation`,
> so it keeps working when the implementation grows a method.

I flag this at the top rather than lower down because it may be original voice
carried forward from the first edition rather than drafted prose, and that is
your call, not mine.

[] Reject

***

**Line 191 (double-underscore paragraph)**
**Pattern:** stock phrase, and now inconsistent with the conclusion

Current:
> The double underscore on `self.__implementation` earns its place here:

The deep-review pass removed "earns its keep" from the conclusion at your
instruction. "Earns its place" is the same figure, twelve lines from a listing
that the same paragraph is justifying, so the chapter now uses the family once
after having it cut once.

Proposed:
> The double underscore on `self.__implementation` matters here:

If you want the phrase kept somewhere in the book, this is the better of the
two places to keep it, since the paragraph does argue that the name pays for
its awkwardness. Then this block is a reject.

[] Reject

***

**Lines 438-439 (after `state.py`)**
**Pattern:** §70 interpretive metadiscourse, low information density

Current:
> The demo uses the first implementation for a while,
> then swaps in the second and uses that.

The listing shows this, and "for a while" is vaguer than the four calls the
listing makes. The sentence exists to bridge into the typing paragraph, so
cutting it outright leaves a jump.

Proposed, replacing it with the observation the demo actually earns:
> `run()` never changes and neither does `b`.
> Only the object behind the surrogate does.

That states what *State* buys and leads into the typing paragraph, which is
about what the checker can see through that same surrogate.

[] Reject

***

**Line 208 (interface-payoff paragraph)**
**Pattern:** pronoun with two possible referents

Current:
> The interface work above still applies on the implementation side:
> the checker verifies that whatever you hand the proxy has the methods.
> It stops at the proxy.

"It" can be the interface work or the checker, and the sentence turns on which.

Proposed:
> That verification stops at the proxy.

[] Reject

***

**Line 451 (end of the State typing paragraph)**
**Pattern:** "is where" cleft, the cousin of the banned "is what"

Current:
> The hop through the surrogate is where the guarantee is lost.

The cleft delays the verb and the sentence means the same without it.

Proposed:
> The hop through the surrogate loses the guarantee.

[] Reject

***

**Lines 330 and 374 — stranded "fronts for"**
**Pattern:** stranded preposition (global rule)

Two sentences move the object out from under "for":
> A proxy is not an instance of the class it fronts for;

and, in prose added this pass,
> A surrogate is not the thing it fronts for,

The verb also appears correctly at line 620 ("*Proxy* fronts for one
implementation"), where its object is present, so only these two need
attention.

Proposed for 374, where the abstraction is doing no work anyway:
> A surrogate is not its implementation,
> and code that needs it to be should ask for a method instead.

Proposed for 330:
> A proxy is not an instance of the implementation's class;

I would fix 374 for certain, since it is new prose.
Line 330 has read that way through earlier passes, so it is more your call.

[] Reject

***

**Line 533 — "ever"**
**Pattern:** watch list, "avoid if possible"

Current:
> A *Smart reference* proxy adds behavior around each access without ever refusing one.

Proposed:
> A *Smart reference* proxy adds behavior around each access without refusing any.

[] Reject

***

**Line 494 — "at all"**
**Pattern:** watch list, "avoid if possible"

Current:
> A *Protection proxy* decides whether a call reaches the implementation at all.

The contrast with the counting proxy is carried by the paragraph after the
listing, so "at all" is not doing the work here that it does there.

Proposed:
> A *Protection proxy* decides whether a call reaches the implementation.

[] Reject

***

**Line 296 — "has to"**
**Pattern:** watch list, "consider rewriting"

Current:
> and that method has to let the proxy's own attributes through or the assignment in `__init__()` recurses:

Proposed:
> and that method must let the proxy's own attributes through,
> or the assignment in `__init__()` recurses:

The added comma also splits a sentence that currently reads as one clause until
the reader hits "or."

[] Reject

***

**Line 587 — "plain"**
**Pattern:** watch list, use only when the sentence fails without it

Current:
> and that it counts calls without counting a plain attribute read:

"Attribute read" is already the contrast with "call," so "plain" qualifies
nothing.

Proposed:
> and that it counts calls without counting an attribute read:

[] Reject

***

**Line 618 — "really"**
**Pattern:** §34 intensifier inflation, §23 empty adverb

Current:
> But both are really a *Surrogate*:

Deleting the word changes nothing, and the colon already announces the
definition.

Proposed:
> But both are a *Surrogate*:

[] Reject

***

**Lines 574-575 (the `CountingProxy` underscore note)**
**Pattern:** repetition inside one sentence

Current:
> `CountingProxy` uses single underscores rather than the mangled `self.__implementation` of the earlier proxies,
> so the trap below can name `self._imp` without the mangling getting in the way.

"Mangled" and "the mangling" in one sentence, and "getting in the way" is vague
about what it gets in the way of.

Proposed:
> `CountingProxy` uses single underscores rather than the earlier proxies' `self.__implementation`,
> so the trap below can misspell `self._imp` without name mangling obscuring the typo.

[] Reject

***

**Lines 453 and 586 — the same test sentence twice**
**Pattern:** formulaic repetition

Both test introductions open the same way:
> Testing hands the State surrogate a small stand-in and confirms calls reach the current implementation,

> The test for the counting proxy uses a small stand-in to confirm that the proxy forwards a call and returns its result,

Two "small stand-in" phrases 130 lines apart is not glaring, but the shape is
identical and the second one is the weaker sentence.

Proposed for 586:
> The counting proxy's test confirms that a call reaches the implementation and returns its result,

[] Reject

***

**Line 9 — "The basic idea is simple."**
**Pattern:** §29 warm-up sentence

The sentence after it states the idea, so this one only announces that a
statement is coming.
Cutting it starts the paragraph on the content:
> From a base class, you derive the surrogate along with the class or classes that provide the actual implementation:

Low confidence: this reads like first-edition voice, and a one-line breath
before a diagram is a reasonable thing to want.

[] Reject

***

**Line 262 — "which is the worse case"**
**Pattern:** §70 interpretive metadiscourse

Current:
> A bypassed dunder that `object` defines fails silently, which is the worse case.

The comparison is real (silence versus a `TypeError`), but the clause tells the
reader how to rank the two rather than saying why.

Proposed:
> A bypassed dunder that `object` defines fails silently, with no error pointing at the miss.

I lean toward making this change, though the current version is defensible: the
`TypeError` two paragraphs up is the thing being ranked against, and the reader
has it in view.

[] Reject
