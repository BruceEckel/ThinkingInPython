
"happen" "is what" "does it" "ever" "at all" "only" "exactly" "has to" "actually" "itself"
"was to" "in the first place" "already" "even" "honest" "buy" "ships" "lands" "fuse" "hooks"
"load-bearing" "never" "part ways" "anyway" "wants" "spelling" "rides on" "near-miss"

lets this book's build pass
passes the book build?

Look for places display_object could be replaced with print(vars(obj))

Look through chapter 19 for words or phrasing that is confusing, odd, or out-of-character.
My goal is:
- Simple, plain, clear explanations
- Short sentences that remove uneccessary words without being overly terse
- Avoid flourishes
- Avoid writing that obscures


Should we introduce https://peps.python.org/pep-0593/, perhaps in the last chapter?

That's the whole trick behind effect systems:
the code that requests an effect is decoupled from the code that performs it (A handler sits in between).

Review all the exercises and make sure they all have solutions that work.

Review the book looking for consistency issues

Deep review chapter 20 as both editor and teacher: fix errors, but also propose additions — misconceptions left unaddressed, mechanisms shown only by outcome, lookalike constructs never contrasted, near-miss code a reader would write. Implement the ones you're confident in, report the rest.

Have we learned anything here that should be added to thinking-in-python-skill.md?

Run 'make prose' on each chapter

Review all exercises to make sure they refer to existing examples and that all  exercises have solutions

- Is full polymorphism covered? (Not just inheritance-based). for example, @overload

- Check order of examples in 37_Pattern_Refactoring.md

- "have to", "could" -> "can"
- which was
- which will be

- active voice: Ask gemini to create a claude skill and how to install it

- Indexing using Leanpub format, before publishing to leanpub

- Do an adversarial review of the book -- what doesn't work, what isn't correct, what could be better? Put the result
  at the root in ADVERSARIAL.md

- Potential example: A task runner based on decorators

/loop through the chapters in the book and look for correctness, style and voice issues.
Fix any obvious issues, and put all the rest in CORRECTNESS_STYLE_AND_VOICE.md, demarking each chapter in the file.
Do not give overviews or summaries or anything other than issues.
The issues you put in CORRECTNESS_STYLE_AND_VOICE.md should be suggested fixes you need me to review.
I will review CORRECTNESS_STYLE_AND_VOICE.md and hand it back to you.
If I haven't deleted a suggested fix, it means I want you to do it.
I may also make further notes next to a suggested fix, inside [[]], giving instructions about the fix.
If you run out of tokens during a chapter, resume when it resets.

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
