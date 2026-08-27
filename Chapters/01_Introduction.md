# Introduction

This book is about developing the judgment to choose the smallest thing that works.
You build that judgment through insights, idioms, and patterns.
The book also questions design patterns.
Most arose to work around the limits of static, inheritance-heavy languages,
and in Python many of them diminish or dissolve.
If an idiom or pattern is still useful, it stays.

Every language has habits worth learning and habits worth dropping.
Programmers who come to Python from C++ or Java arrive with patterns,
ceremonies, and defensive structures that those languages make necessary.
Python needs far fewer of these.
Instead of a class that exists only to hold one method, Python has functions.
A [Singleton](24_Singleton.md) is a module.
A [Visitor](33_Visitor.md) is a function that dispatches on type.
Before using an idiom or pattern,
this book asks whether the language already solves the problem,
and adds the complexity only when the answer is no.

## Who This Book Is For

I am writing for the programmer who already knows how to program,
either in another language or in Python.
The goal is to move from writing Python that works to writing Python that is clear,
idiomatic, and a pleasure to maintain.

This is an intermediate-to-advanced book,
which removes two constraints that introductory books carry:

1.  An introductory book must describe everything in lockstep,
    never using an idea before formally introducing it.
    This one does not.
2.  An introductory book chooses topics by where they fall in a beginner's path.
    This one chooses them by whether they are interesting and useful.

You should be comfortable with:

- Functions, classes, objects, and inheritance.
- Containers: lists, dictionaries, tuples, and sets.

If a language feature is new to you, look it up as you go.

You do not need to know design patterns, metaclasses, or type checking.
This book covers them.
The book is about the language, not the tooling around it.

## How the Book Fits Together

You can read straight through, or jump to a chapter that interests you,
since most chapters are self-contained.
The book has five parts.

Part I, *Foundations*, is a fast tour of the language: its syntax, containers,
control flow, functions, modules, classes, static typing, class attributes,
and object cleanup.
This part is for programmers coming to Python from another language.
If you already know Python, you can skim for topics you don't know,
or skip it altogether.
If you skip Part I, come back for [Static Typing](08_Static_Typing.md):
every chapter after it annotates its examples,
and it is the one Part I chapter the rest of the book assumes.

Part II, *Techniques*,
covers the idioms and tools that give Python its character: testing,
data classes as types, pattern matching, decorators, context managers,
comprehensions, and metaprogramming.
It closes with performance and concurrency,
where the question changes from what the code says to how fast it runs.
Many of these chapters came from presentations I've given, mostly at PyCon.

Part III, *Patterns*, opens by stepping back to question object orientation,
because several of the patterns that follow exist to manage problems that objects create.
A short chapter then introduces the design-patterns movement itself,
and the question the rest of the part keeps asking.
The part then works through the classic design patterns,
reframing each for Python and weighing it against the language.
I ask what problem you are solving and whether the language already does the pattern's job.
Learning to ask those questions is one of the most useful things this book can give you.
The part ends by refactoring one problem through several designs,
building a simulation out of the pieces,
and cataloging the classic patterns together with the ones the literature added later.

Part IV, *Functional Programming*, covers pure functions,
the `functools` and `itertools` toolkits,
errors returned as values instead of raised exceptions,
and a spectrum of assurances that runs from local reasoning up to machine-checked proof.

Part V, *Effects*, closes the book by covering everything a program does that a pure function cannot.
One chapter surveys the languages that track Effects in a function's type,
and asks what Python could adopt.
Another develops the full generator protocol on which such tracking depends.
The last two put that idea to work with `stateless`,
a library that brings Effect tracking to Python today.

## AI Trigger Warning

I started this book in 2008,
with the idea of taking the design patterns work I had done in Java and translating it to Python.
In 2011 I abandoned the project with many of the design patterns still in Java.
Eventually I even wrote a message confirming I was not going to complete it.

In June of 2026, after people mentioned the online book to me at recent PyCons,
I decided to see what the Claude AI could do with it.
The experience was amazing,
and I began adding material from my blog posts and presentations.
Claude allowed me to create tooling for the book that I had imagined but never fully realized.

This book never would have happened without the help of Claude.
That said, it is still my work, derived from existing work, designed by me,
checked and rewritten by me.
It has my voice, and I've gone over every sentence multiple times, editing,
rewriting, and adding.

I know some people don't like AI.
Without it, this book wouldn't exist.
The book is free, so if AI bothers you more than the resulting product might benefit you,
please ignore this book.

Using Claude made me realize how many compromises I've made on books in the past.
I would get a good idea about something
(for example, automatically interleaving commented output in the listings).
I either couldn't implement it, or it seemed too hard, so I didn't do it.
But with AI I can explore and often implement every whim,
from things as seemingly straightforward as inserting a new chapter to ones as daunting as that commented-output system.
The result is much better than anything I managed before.
I keep going until I've tweaked everything that occurs to me.

For things that I have generated rather than written from scratch,
I've become the director of the movie instead of an actor in it.
This book is what I've always wanted to create,
but have never had the capacity to flesh out in all its myriad detail.
With Claude and my directing and rewriting, I can build my ideal book.

Using Claude greatly simplified and sped the writing process.
It did not make it trivial.
Once Claude had translated and integrated my own work into the book,
and once it had generated the first versions of new material,
I went through line by line and concept by concept,
inevitably rewriting and asking for clarification,
often creating more examples to answer further questions.
One pass would often change the book enough that it needed another pass.
It was much faster than without Claude, but it still took time and effort.

I can't predict the future of books.
The internet and eBooks have been changing the print book industry for decades.
But with AI, how many people will keep reading computer programming books?
I hardly do.
If I need something, I ask AI.
My only hope is that this book will be engaging to read,
and that you will experience some of the same satisfaction that I've had while writing it.

I think most programmers will regularly use AI, if they don't already.
I have found that the knowledge in this book has helped me guide AIs toward better solutions.

Perhaps I am teaching the equivalent of assembly language after everyone has started using the equivalent of compilers.
However, Python seems to be the most popular language
(at the time of this writing) for AI-generated code.
Some small percentage of people might still wish to analyze what the AIs are generating.
This book might have some value yet.

## The Examples

The book targets Python 3.15 and later, uses type hints,
and tests with `pytest`.
Early chapters mostly omit type hints,
until [Static Typing](08_Static_Typing.md) introduces the syntax.
Every chapter afterward uses them consistently.

Every code block that begins with a filename comment, like `# tracer.py`,
is a complete file rather than a fragment.
Most run on their own; some are modules that another listing imports,
and `pytest` runs each `test_*.py` file.
These files live in the `Examples/` directory of the [source repository](https://github.com/BruceEckel/ThinkingInPython),
one folder per chapter,
so the code block starting with `# tracer.py` in [Decorators](14_Decorators.md#maintaining-the-wrapped-interface)
is the file `Examples/14_Decorators/tracer.py`.
A helper that more than one chapter uses names a `utils/` path instead,
like `# utils/result.py`,
and lives in `Examples/utils/` rather than in a chapter folder.

`uv` and other tools make setup short.
The repository's [README](https://github.com/BruceEckel/ThinkingInPython#setup)
has the instructions,
and `tools/README.md` explains how to build the book and run the examples yourself.

The book's build system extracts the examples, then type-checks
(with Astral's `ty`), lints, runs, and tests them.
The code you read is the code that runs,
and the output you see is the output it produces.

Output appears inside the listings as comments beginning with `#:`,
one line of output per marker.
A run of markers shows everything the code above it printed since the previous run,
in order.
Output from inside a loop, or from an `import`,
therefore appears in the run of markers after the loop or the `import`,
not next to the line that produced it.
A `print("affirmative")` above a line reading `#: affirmative` means the program prints `affirmative` at that point.
The build regenerates these markers from a real run,
so they cannot drift from what the code prints.

If you find a mistake, please send a correction.
See `CONTRIBUTING.md` in the source repository.

## The Exercises

Most chapters end with a short "Exercises" section.
These come from workshops, where pairs work through them at a keyboard.
They are short enough to do on your own, and they are worth doing that way.
They usually ask you to change a small,
already-working example from that chapter and observe the result: add a class,
break an invariant on purpose, extend a table, rewrite one function two ways.
The point is to touch the code, predict what it does, then run it and check.
A few chapters in the Patterns part keep larger exercises,
where a pattern only shows its value in a program you build yourself.

Solutions live in the `Solutions/` directory of the source repository.
Try the exercise yourself before reading the solution.
The value is in the prediction and the surprise when you are wrong,
not in the code you produce.

## Resources

This book is freely readable at [thinkinginpython.com](https://thinkinginpython.com/),
which always holds the current version.

Other resources:

- [The official Python tutorial](https://docs.python.org/3/tutorial/)
- [The Python Programming FAQ](https://docs.python.org/3/faq/programming.html)
- [What's New in Python 3.15](https://docs.python.org/3.15/whatsnew/3.15.html),
  the release notes for the version this book targets
- [The Python type system specification](https://typing.python.org/en/latest/spec/),
  the reference behind the annotations the book uses throughout
- [Python Bytes](https://pythonbytes.fm/), podcast and newsletter
- [Planet Python](https://planetpython.org/),
  an aggregator of Python articles from around the web

## Copyright

© 2026 Bruce Eckel.
This book is licensed under [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en):
you may share it unchanged, with attribution, for noncommercial use.
It is freely readable online; no reproduction without permission.
The source repository's `CONTRIBUTING.md` has the details.
