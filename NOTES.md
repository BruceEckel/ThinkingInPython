I'd like to produce a nice readable layout of both classes and objects, to use in the book to show people what the
  class or object looks like. I tried the builtin help() but it was not as compact as I'd like and produced output that
  was too wide. I wonder if there might be third-party libraries to do this, but it could also be a supplemental
  utility (perhaps stored in 'tools'?) custom written for the book.

Before bed: In a loop, one chapter at a time, review chapters 02 through 08.
If you run out of tokens during a chapter, resume when it resets.
Put each chapter review in a file named REVIEW_02.md, REVIEW_03.md, etc. so I can go over them at my leisure.
DO make essential changes, and put everything else in the REVIEW files.

/loop through chapters looking for examples that (after the dataclass chapter) could work better as dataclasses, and convert them.
Look for chapters that have class variables (after that topic was introduced) and make sure they use ClassVar
Also make sure the syntax and type annotations are modernized (after type annotations have been introduced)

Look for duplication on Singleton between Metaprogramming and Singleton chapters.

Review chapter 14. Make obious changes and put everything I need to look at first in REVIEW_14.md

Functional programming in Python (chapter). Have Claude draft it to see what it thinks it is.

Run 'make prose' on each chapter

Creating your own context managers -- didn't I write about this?

in 04, the statement: The same `*` and `**` *unpack* a sequence or dictionary back into arguments at a call site,
  the mirror image of collecting them.
  Can you demo this either in the previous example or a new one

- Is full polymorphism covered? (Not just inheritance-based)
- 11 Pattern matching: ensure there is a comparison to polymorphism at the end
- Check order of examples in 30_Pattern_Refactoring.md

- "have to", "could" -> "can"
- which was
- which will be

- Consider using "*GoF Design Patterns*" to specify the book vs the concept. Also search for "the book" phrase
- Consider more specific links, to specific subsections rather than whole chapters.

- Check exercises. Potentially create new exercises.

- active voice

- Indexing using Leanpub format, before publishing to leanpub

- Search feature on website?

******************

- Introductory Python YouTube Playlists:
  - [Socratica's Python Programming Tutorials](https://www.youtube.com/playlist?list=PLi01XoE8jYohWFPpC17Z-wWhPOSuh8Er-)
  - [TheNewBoston's Python 3.4 Programming Tutorials](https://www.youtube.com/playlist?list=PL6gx4Cwl9DGAcbMi1sH6oAMk4JHw91mC_)

- Learning Sites:
  - [Learning Python](http://www.makeuseof.com/tag/5-websites-learn-python-programming/)
