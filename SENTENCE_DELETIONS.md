# Sentence Deletion Candidates

**The scan is complete: all 31 chapters are done, and `STATUS` is now `READY`.**
The list below holds **50 candidate sentences across 19 chapters**. The
purpose-written chapters (8-13, 16, 20, 23, 25, 30, 31) yielded little or
nothing; the Thinking-in-Java-derived chapters (2-6, 14, 17) and the
author's-voice asides in the pattern chapters account for most of it.

Each bullet below is one sentence from the book that may not pull its weight:
filler, redundant restatement, or an aside that adds little. The sentences are
quoted verbatim (collapsed to a single line), grouped by the chapter file they
live in. Several are marked "borderline" in their comment: kept on the
generous side so you can decide.

## How to use this file

- Every sentence listed here is **proposed for deletion** from the book.
- To **keep** a sentence, **delete its bullet line** from this file.
- Whatever bullet lines **remain** when you are done will be removed from the
  book automatically.
- When finished, change the `STATUS:` line below from `BUILDING`/`READY` to
  `DONE` and tell me. I will then delete every remaining sentence from its
  chapter, run the drift/test gates, and remove this file.

Do not edit the chapter-file headings (`### Markdown/...`) or the wording inside
a bullet you intend to delete from the book: I match the quoted text against the
source, ignoring differences in whitespace only.

<!--
  STATUS values:
    BUILDING = I am still scanning chapters; do not edit yet.
    READY    = scan complete; safe to review and prune.
    DONE     = you are finished; I will apply the remaining deletions.
  PROGRESS tracks the last chapter I scanned.
-->
STATUS: READY
PROGRESS: scanned through chapter 31 (all chapters complete)

---

### Markdown/01_Introduction.md
- There are plenty of excellent Python tutorials and online courses for that. <!-- aside; the previous sentence already says this is not an introductory book -->
- If your grasp of objects is shaky, it will grow stronger as you watch objects used in many different situations here. <!-- reassurance that adds nothing -->

### Markdown/02_A_Python_Tour.md
- But it is far more than a scripting language. <!-- restates the preceding sentence -->
- Python is practical; Python language design decisions were based on providing the maximum benefits to the programmer. <!-- marketing filler -->
- This is accomplished through clean, to-the-point syntax. <!-- restates the prior sentence -->
- First notice the `if` statement. <!-- empty pointer -->
- You can see that the basic syntax of Python is C-ish. <!-- vague, adds nothing -->
- Even from the brief example above you can see that the language is designed to be as simple as possible, and yet still very readable. <!-- self-congratulatory summary -->
- The above example also shows a little bit about Python string handling, which is the best of any language I've seen. <!-- weak transition plus an unsupported boast -->
- Python also has very sophisticated regular expressions. <!-- dangling aside, off topic here -->

### Markdown/03_Containers_and_Control_Flow.md
- This adds much to the elegance of the language. <!-- vague praise -->
- This makes a lot of sense when you think about it, since you're almost always using a `for` loop to step through an array or a container. <!-- "makes a lot of sense when you think about it" is filler -->
- You can print the list and it will look exactly as you put it in (in contrast, remember that I had to create a special `Arrays2` class in *Thinking in Java* in order to print arrays in Java). <!-- Thinking-in-Java digression -->
- You can create a list of numbers with the `range()` function, so if you really need to imitate C's `for`, you can. <!-- range() is covered properly later -->
- It's as if Python is designed so that you only need to press the keys that absolutely must. <!-- awkward, says nothing concrete -->

### Markdown/04_Functions.md
- When the operator '`+`' is used with strings, it means concatenation (yes, Python supports operator overloading, and it does a nice job of it). <!-- the parenthetical boast carries the sentence -->

### Markdown/05_Modules_and_Packages.md
- This example is primarily useful to show you the consistency of the package model. <!-- meta-comment that adds nothing -->
- You will rarely do anything like this, probably only with an especially complex project. <!-- mild filler -->

### Markdown/06_Classes.md
- Python's spare syntax makes you realize that the `new` keyword isn't really necessary in C++ or Java, either. <!-- editorializing aside -->
- This seems a little strange coming from C++ or Java where you must decide ahead of time how much space your object is going to occupy, but it turns out to be a very flexible way to program. <!-- "but it turns out to be a very flexible way to program" adds nothing -->
- Thus, in Python you automatically get the equivalent of templates, without having to learn that particularly difficult syntax and semantics. <!-- boast that does not teach anything -->

<!-- chapter 07 (Initialization and Cleanup): no filler candidates; prose is tight -->

### Markdown/08_Static_Type_Checking.md
- There is almost no new vocabulary to learn for everyday code. <!-- borderline: reassurance more than information -->

<!-- chapter 09 (Testing): no filler candidates; prose is tight -->

<!-- chapter 10 (Data Classes as Types): no filler candidates; purpose-written and tight -->

<!-- chapter 11 (Pattern Matching): no filler candidates; purpose-written and tight -->

<!-- chapter 12 (Functional Error Handling): no filler candidates; purpose-written and tight -->

<!-- chapter 13 (Decorators): no filler candidates; purpose-written and tight -->

### Markdown/14_Comprehensions.md
- Once that shift clicks they become compelling. <!-- editorializing -->
- Python 2.0 introduced list comprehensions. <!-- version history of little value in a 3.14 book -->
- Python 3.0 added dictionary and set comprehensions. <!-- version history of little value in a 3.14 book -->
- It would be more efficient to represent the structure as a tuple of tuples, but the whole point of this example is to use lists. <!-- meta-aside about the example -->

### Markdown/15_Metaprogramming.md
- This is a good example of how Python 3 retired one of the classic reasons to write a metaclass. <!-- borderline: restates the chapter's theme -->

<!-- chapter 16 (Rethinking Objects): no filler candidates; purpose-written (PyCon 2023) and tight -->

### Markdown/17_The_Pattern_Concept.md
- This should whet your appetite to read *Design Patterns* by Gamma et al., a source of what has now become an essential, almost mandatory, vocabulary for OOP programmers. <!-- borderline: marketing for another book -->
- I feel this helps put things in perspective, and to show where something might fit. <!-- vague self-assessment -->
- One could also argue for the inclusion of *Analysis Pattern* and *Architectural Pattern* in this taxonomy. <!-- tangential aside -->
- While this was an interesting experiment, I don't think it produced much of use in the end because the point is to solve problems, so a helpful approach will look at the problem to solve and try to find relationships between the problem and potential solutions. <!-- recounts an abandoned experiment -->
- Currently, I'm just trying to make a list, but eventually I hope to make steps towards connecting these structures with patterns (or I may come up with a different approach altogether; this is still in its formative stages). <!-- work-in-progress confession -->

### Markdown/18_Messenger.md
- That is probably easier for the reader to follow, too. <!-- borderline: mild add-on to the prior point -->

### Markdown/19_Singleton.md
- This is small and obvious. <!-- borderline: flourish of the kind the style guide discourages -->

<!-- chapter 20 (Application Frameworks): no filler candidates; rewritten and tight -->

### Markdown/21_Fronting_for_an_Implementation.md
- One is tempted to just lump the two together into a pattern called *Surrogate*, but the term "proxy" has a long-standing and specialized meaning, which probably explains the reason for the two different patterns. <!-- meandering aside; hedged -->

### Markdown/22_State_Machines.md
- Basically, this is a "state machine" using objects. <!-- "Basically," opener; restates the heading -->
- As your state machine gets bigger, you might decide to use an automation tool whereby you configure a table and the tool generates the state machine code for you. <!-- tangential aside about tooling -->

<!-- chapter 23 (Iterators): no filler candidates; rewritten and tight -->

### Markdown/24_Factory.md
- This was done for convenience of use. <!-- filler -->
- This is certainly a reasonable solution, as it throws a box around the process of creating objects. <!-- borderline: "certainly a reasonable solution" is padding -->
- You might want to study the two examples for comparison, however. <!-- empty directive -->

<!-- chapter 25 (Function Objects): no filler candidates; rewritten and tight -->

### Markdown/26_Changing_the_Interface.md
- However, if you have the two words together: "proxy adapter," it is perhaps more reasonable. <!-- hedged terminology aside -->

### Markdown/27_Observer.md
- The `notify_observers()` method is part of the base class `Observable`. <!-- restates the prior sentence -->
- That is, the observer pattern allows you to modify both of these without affecting the surrounding code. <!-- "That is," elaboration of the prior sentence -->
- The "observed object" that decides when and how to do the updating will be called the `Observable`. <!-- Observable was already named above -->

### Markdown/28_Multiple_Dispatching.md
- Generally, you'll set up a configuration such that a single member function call produces more than one dynamic method call and thus determines more than one type in the process. <!-- restates the double-dispatch idea (also "member function") -->
- To get this effect, you need to work with more than one polymorphic method call: you'll need one call for each dispatch. <!-- restates the prior two sentences -->

### Markdown/29_Visitor.md
- So the dilemma is that you need to add methods to the base class, but you can't touch the base class. <!-- borderline: restates the prior sentence -->

<!-- chapter 30 (Pattern Refactoring): no filler candidates; rewritten and tight -->

<!-- chapter 31 (Simulation): no filler candidates; rewritten and tight -->
