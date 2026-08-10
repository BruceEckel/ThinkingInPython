Fable: Review the book to find and fix consistency issues

New book cover & favicon

60 character limit on code listings, for better ebook reading experience

Use Fable for deep-review

Fable: What else should I do before I start my hand-editing pass? I'm hoping this requires as few hand-edits as possible.

Active voice (Fable)
make prose reveals many

Add Epub link info on README and bottom of index page.

Pong game, autoplay with builtin gui
Game that incorporates both game theory and NVC with the hypothesis that there is a connection.
Examples that demonstrate probability or statistics, very simply

Should we introduce https://peps.python.org/pep-0593/, perhaps in the last chapter?

Fatal vs recoverable errors

- "happens"
- "have to", "could" -> "can"
- which was
- which will be
- would have

- active voice: Ask gemini to create a claude skill and how to install it

- Indexing using Leanpub format, before publishing to leanpub

- Potential example: A task runner based on decorators and generators

## Periodic

- Have we learned anything new that should be added to thinking-in-python-skill.md?
- Run 'make prose' on each chapter
- Do an adversarial review of the book -- what doesn't work, what isn't correct, what could be better?
  Put the result at the root in ADVERSARIAL.md
- Pass through looking for metadiscourse phrases, empty frames, and expletive constructions



******************

Apply the "xxx" skill to each chapter.
As this skill processes each chapter in isolation,
you should be able to parallelize many tasks at once, one per chapter.
If a chapter needs to modify another chapter,
it should only write that into the review file, so parallelizing isn't compromised.

******************

With all the kinds of additions and changes we've made in 'tools', can you imagine
an architecture that would be well-suited to making future changes easy?
Consider what the common data structures might be, and common functions
that could be reused across the tools.
Also consider small pieces that could be assembled to produce larger results,
and this might also produce common reusable functions.
If functions can be run in parallel we might see speed improvements.
Understandability is also a goal, in case a human wants to add or change something by hand.
Perhaps some kind of plug-in architecture? (I'm just guessing here)
I'm also not averse to considering a third-party library if one fits especially well,
but my preference is to use standard library components if possible.
Only provide me with an analysis, do not make changes. We are planning, not executing.


******************

Appendix perhaps containing learning resources, ask Claude to find the best ones

- Introductory Python YouTube Playlists:
  - [Socratica's Python Programming Tutorials](https://www.youtube.com/playlist?list=PLi01XoE8jYohWFPpC17Z-wWhPOSuh8Er-)
  - [TheNewBoston's Python 3.4 Programming Tutorials](https://www.youtube.com/playlist?list=PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_)

- Learning Sites:
  - [Learning Python](http://www.makeuseof.com/tag/5-websites-learn-python-programming/)

---
Potential Pycon talks:
Concurrency for beginners

---
Short monty python phrases
- "Ni!"
- "Spam"
- "Spam, spam, spam"
- "And now for something completely different"
- "It's..."
- "Nudge nudge"
- "Wink wink"
- "Say no more"
- "Nobody expects the Spanish Inquisition!"
- "This is an ex-parrot"
- "Pining for the fjords"
- "'E's not dead, 'e's resting"
- "I'm not dead yet"
- "It's just a flesh wound"
- "Bring out your dead"
- "Your father smelt of elderberries"
- "A shrubbery"
- "What is your favourite colour?"
- "African or European?"
- "Naughty naughty, very naughty"
- "Lumberjack"
- "Albatross!"
- "My hovercraft is full of eels"
- "Silly walks"
- "Argument Clinic"
- "No it isn't"
- "Cheese shop"
- "Blancmange"
- "Crunchy frog"
- "Run away!"
- "Fetchez la vache"
- "Nudge, wink, say no more"


## Review process analysis by Fable

```
do deep_review/12_X.md, then run readability on the chapter
```


❯ I've been using Opus to apply the 'deep-review' skill to all the chapters, and then once I've integrated that, I apply the 'readability' skill and integrate that. I'm wondering if it would make sense and/or be practical to apply both skills at once. Also if there's any better strategies to use to improve the book.

Let me look at both skills to understand what each pass does before weighing in.

  Searched for 1 pattern, read 2 files

Short answer: keep them as two distinct passes, because your current order does something a merged pass can't, but you can collapse the sessions to save most of the overhead. Here's the reasoning, based on reading both skill files.

Why the sequence matters

Your order (deep-review, integrate, then readability) has a property that's easy to miss: readability reviews prose that deep-review created. Deep-review adds new material: teaching additions, warnings about near-miss code, new listings with surrounding prose. That newly drafted prose is the most likely place for AI tells to appear; the readability skill's own "out-of-character" section says newly drafted prose is the usual source. If you run both skills against the same original text at once, readability audits the old prose and the deep-review additions arrive unaudited.

Two more practical problems with a true merge:

- Conflicting anchors. Both skills quote offending lines and cite sections. Deep-review restructures; readability's findings would then point at text that no longer exists, or exists in a different form, by the time you apply them. Sequential passes keep every finding anchored to text that's current when it's applied.
- Attention split. Deep-review is four passes with a chapter-level pedagogy checklist; readability is seventy patterns plus structural rhythm tests. Asking one session to hold both means each gets a shallower read. Deep-review's fourth pass (prose language) overlaps readability a little, but readability is far more granular, and the overlap is not a substitute.

What you can collapse

The real cost of your current workflow is the repeated setup: each skill run re-reads the chapter, re-runs gates, and you do two vetting rounds. Two ways to cut that without losing the ordering benefit:

1. Fold readability into the deep-review apply step. When you hand back do deep_review/NN.md, the session applies the blocks, and the chapter is now in its post-integration state with the context warm. That is the ideal moment to run readability: same session, chapter fresh in context, and it sees every addition the apply step just made. You'd say something like do deep_review/12_X.md, then run readability on the chapter. One session instead of two, and readability covers the new prose, which is the whole point of running it second.
2. Pipeline across chapters. While you vet chapter N's deep-review file, a session can be producing chapter N+1's. The vetting is your time; the reviewing is the model's. Overlapping them roughly halves the wall-clock without touching either skill.

I'd take option 1 and skip merging the skills.

Other strategies worth considering

- A part-level or book-level pass. Deep-review works at chapter altitude, and nothing in the current workflow reviews above it. Your project memory records the failure modes this leaves open: cross-chapter threads whose ends drift apart, "previous chapter" references broken by splits, terminology that shifts between chapters, concepts explained twice or assumed before taught across a chapter boundary. A dedicated pass that reads a whole Part (or the section-heading outline of the whole book) and checks arc, redundancy, and terminology consistency would catch a class of problems no number of chapter reviews will. The "assumes/introduces two-column" technique from deep-review's ordering bullet scales up to chapters as the units.
- A final whole-book readability sweep, late. Every integration round adds prose, so whatever chapter you readability-reviewed first has accumulated unaudited edits since. One cheap sweep near the end, after chapter-level work settles, mops that up. Density-based tells (vocabulary clusters, sentence-length uniformity) also read better over long stretches than a chapter at a time.
- Use acceptance rate as a stopping rule. The reject-checkbox history gives you a free signal: when a chapter's review round comes back and you reject most of it, that chapter is done and further rounds are churn. Move the effort to the book-level pass instead. Your memory note that repeated audits should widen scope rather than re-run the same check points the same direction.
- A fresh-reader pass for exercises. Deep-review checks that exercises are answerable from the chapter, but a session that actually attempts each exercise cold, using nothing but the chapter, is a stronger test and would also surface Solutions drift, which your memory notes is still partly ungated.

So: same two skills, same order, one fewer session per chapter, and consider adding the book-altitude pass, which is the review neither skill currently gives you.
