> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review: `Chapters/29_Changing_the_Interface.md`

Run right after the deep-review edits landed, so the split `adapter.py` /
`adapter_variations.py` prose, the rewritten `ProxyAdapter` naming aside, the
new `WhatIWant` sentence, the deprecation version clause, and the new exercise 4
get the same scan as the older prose.
No completed readability review exists for this chapter, so nothing is carried
forward.

The chapter reads as human prose, and the Façade epigraph plus "A façade is an
agreement about which names to call, not a lock on the rest" are the strongest
lines in it.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, no boldface or bullet
inflation, no formulaic conclusion.
The findings are one paragraph whose subject drifts, two watch-list clefts, and
a short run of single words.

Line numbers refer to the chapter as it stands now.

***

**Line 56 — "wants" applied to a class**
**Pattern:** watch list, "don't use"

Current (prose added this pass):
> `WhatIUse` wants an `f()` and `WhatIHave` has none,
> so `ProxyAdapter` supplies one and builds it out of the methods the adaptee does have.

A class does not want anything; it requires. This is the first sentence a
reader meets after the chapter's first listing, so it sets the register.

Proposed:
> `WhatIUse` calls `f()` and `WhatIHave` has none,
> so `ProxyAdapter` supplies one and builds it out of the methods the adaptee does have.

"Calls" is also more precise than "requires" here: the requirement exists
because `op()` makes the call.

[] Reject

***

**Line 334 — "the Adapter is what a Proxy becomes"**
**Pattern:** "is what" cleft (global rule)

Current:
> Under that reading the Adapter is what a Proxy becomes once you stop insisting on the interface,
> which is why the `ProxyAdapter` above answers to both names.

The verb sits right after the cleft ("is what ... becomes"), which is the
giveaway the rule names.

Proposed:
> Under that reading a Proxy becomes an Adapter once you stop insisting on the interface,
> which is why the `ProxyAdapter` above answers to both names.

[] Reject

***

**Line 230 — "That is what *Façade* accomplishes"**
**Pattern:** "is what" cleft, plus a §29 warm-up line after the epigraph

Current:
> > If something is ugly, hide it inside an object.
>
> That is what *Façade* accomplishes.
> If you have a confusing collection of classes and interactions the client programmer doesn't need to see,
> create an interface that presents only what's necessary.

The epigraph states the idea; the next line restates that the idea has a name,
then the third sentence starts the actual explanation.

Proposed:
> > If something is ugly, hide it inside an object.
>
> That is *Façade*.
> If you have a confusing collection of classes and interactions the client programmer doesn't need to see,
> create an interface that presents only what's necessary.

Alternative, if you want the sentence gone entirely: delete it and let the
epigraph run straight into "If you have a confusing collection...". I
recommend the shortened version; the naming sentence does connect the quote to
the pattern.

[] Reject

***

**Lines 112-117 (after `adapter_variations.py`)**
**Pattern:** a paragraph whose subject shifted when the listing split

Current:
> The output is deliberately monotonous.
> Four different structures produce one behavior:
> every route ends at the same two methods on a `WhatIHave`.
> The approaches differ only in where the adaptation lives.
> When the output cannot tell them apart,
> the choice among them is purely one of packaging.

"Four different structures" now counts across two listings, and the reader is
looking at a listing showing three.
The paragraph was written when one listing held all four.

Proposed:
> The output is deliberately monotonous.
> Counting the object adapter above, four structures produce one behavior:
> every route ends at the same two methods on a `WhatIHave`.
> The approaches differ only in where the adaptation lives.
> When the output cannot tell them apart,
> the choice among them is purely one of packaging.

The next paragraph already opens "The four also split into two families," so
that one reads correctly once this fixes the count.

[] Reject

***

**Line 127 — "needs a closer look"**
**Pattern:** the replacement for "repay attention" is blander than what it replaced

Current:
> One detail in the second listing needs a closer look.

You asked for "repay attention" to be rewritten and this is what went in.
It is a §29 warm-up line: it announces that an explanation follows instead of
starting it.

Proposed: cut the sentence and let the paragraph open on the detail.
> The `/` in `WhatIUse.op()` makes its parameter positional-only,
> and removing it breaks the override:

The paragraph is already the only place the `/` is discussed, so nothing
orients the reader that the sentence was providing.

[] Reject

***

**Line 201 — "which is what `copy.copy()` and `pickle` do"**
**Pattern:** "is what" cleft

Current:
> `__getattr__()` reading `self._adaptee` recurses forever on an instance built without `__init__()`,
> which is what `copy.copy()` and `pickle` do,

Proposed:
> `__getattr__()` reading `self._adaptee` recurses forever on an instance built without `__init__()`,
> as `copy.copy()` and `pickle` build one,

Note the identical phrasing exists in `Chapters/26_Surrogate.md` around the
`RecursionError` trap, added in an earlier pass. If you take this, that one
should match. Chapter 26's readability review does not raise it, so it would
need a small follow-up there.

[] Reject

***

**Line 197 — "defines those dunders itself"**
**Pattern:** watch list, "itself" as a flourish

Current:
> so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders itself,

The reflexive is doing no work: the adapter is the only thing that could define
them, and the sentence already names it as the subject.

Proposed:
> so an adapter that must support `adapter[key]` or `len(adapter)` defines those dunders,

[] Reject

***

**Line 10 — "a later section sorts the four apart"**
**Pattern:** none; noting a claim that is now correct

No change proposed.
The chapter's opening used to say the chapter "ends by" sorting the four apart,
which was wrong once "Retiring the Old Interface" became the closing section.
The deep-review pass corrected it to "a later section," and the accrued note in
`deep-review/SKILL.md` was corrected to match.
Recorded so a later pass does not restore the tidier-sounding but false version.

[] Reject
