[[Reviewed]]
> When this file has been applied, change this file's name so it has a leading
> `~` to indicate completion.

# Readability review 2: `Chapters/24_Singleton.md`

Run after the deep-review edits landed, so the new prose, the new
`singleton_eager_factory.py` lead-in, the Borg warning, and the two new
exercises get the same scan the rest of the chapter got in review 1.
Nothing from review 1 was rejected, so nothing is carried forward.

The chapter still reads as human prose.
No §7 vocabulary hits, no curly quotes, no spaced ` -- `, and the new
exercises match the voice of the four before them.
Three findings, all in sentences written during this pass.

***

**Section:** Borg: Singleton By Inheritance (the new sharing warning)
**Pattern:** names used that appear in no listing (P1)

Current:
> Constructing an `A("apple")` and then a `B("banana")` leaves both objects reading `"banana"`.

Proposed:
> A second subclass alongside `Singleton` writes into the same dict,
> so constructing one of each leaves both objects reading the value set last.

Why: `A` and `B` appear nowhere in the chapter.
They come from the scratch classes I used to verify the behavior, and I carried
them into the prose, so the reader meets two undefined names in the sentence
that is supposed to make the trap concrete.
The listing above defines only `Singleton`, and `Borg`.

This one needs your call because the honest fix might be a listing rather than
a rewording.
The paragraph asserts a two-subclass collision while the page shows one
subclass, so a reader cannot see the failure, only read about it, and this is
the near-miss the section exists to warn about.
Exercise 6 now asks the reader to build exactly this, which is an argument for
leaving the prose short and letting the exercise carry it: that is why I did
not propose a second listing here.
The rewording above works either way.

[] Reject

***

**Section:** When You Want a Class, Cache the Instance (after `singleton_eager_factory.py`)
**Pattern:** stranded preposition (P2)

Current:
> The priming call is safe for the reason the chapter opened with:
> the import system runs a module body once,
> so the object exists before any thread can ask for it.

Proposed:
> The priming call is safe for the same reason the module form is:
> the import system runs a module body once,
> so the object exists before any thread can ask for it.

Why: "the reason the chapter opened with" strands "with" on a moved object.
Naming the module form instead of "the chapter" also points at the thing that
carries the guarantee, which is what the colon then explains.

[] Reject

***

**Section:** When You Want a Class, Cache the Instance (after `singleton_eager_factory.py`)
**Pattern:** "is what" cleft, and a vague "it" (P2)

Current:
> Laziness is what the race needs, and this gives it up on purpose.

Proposed:
> The race needs laziness, and this listing gives it up on purpose.

Why: deleting the cleft changes nothing, which is the test for it.
"this" also had no clear referent, since the nearest noun was the guarantee
rather than the listing.

[] Reject
