# Introduction

Every language has habits worth learning and habits worth dropping.
Programmers who come to Python from C++ or Java arrive with patterns,
ceremonies, and defensive structures that those languages made necessary.
Python needs far fewer of these.
Instead of a class that exists only to hold one method, Python has the function.
A *Singleton* is a module.
A *Visitor* is a function that dispatches on type.
The recurring theme in this book is to ask, before reaching for idioms or patterns,
whether the language already solves the problem,
and to add the structure only when the answer is no.

This book is not a catalog of features but the judgment to choose the smallest thing that works.
That judgement is found through insights, idioms, and patterns.
It is also honest about design patterns.
Most were invented to work around the limits of static,
inheritance-heavy languages,
and in Python many of them dissolve or shrink.
If a pattern still earns its keep, it stays.

This is an intermediate book, which removes two constraints:

1.  An introductory book must describe everything in lock step,
    never using an idea before it has been formally introduced.
    This one does not.
2.  An introductory book chooses topics by where they fall in a beginner's path.
    This one chooses them by whether they are interesting and useful.

If a language feature is new to you, look it up as you go.

## Who This Book Is For

I am writing for the programmer who already knows how to program, either in another language or in Python itself.
The goal is to move from writing Python that works to writing Python that is clear,
idiomatic, and a pleasure to maintain.

You should be comfortable with:

- Functions, classes, objects, and inheritance.
- Containers: lists, dictionaries, tuples, and sets.
- Running a Python program and installing a package.

You do not need to know design patterns, metaclasses,
or type checking; we cover that here.
The book is about the language, not the tooling around it,
so it does not explain installing Python, setting up virtual environments,
or managing packages.
I assume you know about those or are comfortable learning about them,
starting with the official Python documentation.

## AI Trigger Warning

I started this book in 2008, with the idea of taking the design patterns work I had done in Java and translating it to Python.
In 2011 I abandoned the project with many of the design patterns still in Java.
Eventually I even wrote a message confirming I was not going to complete it.

In June of 2026, after having people mention it to me at recent Pycons, I decided to see what the AI Claude could do with it.
The experience was amazing, and I began adding material from talks, writing, and presentations (mostly at Pycon).
Claude allowed me to create tooling for the book that I had imagined but never fully realized.
Every perfectionistic whim was easily realized.

This book never would have happened without the help of Claude, which gave me tremendous support throughout the process.
That said, it is still my work, derived from existing work, designed by me, checked and rewritten by me.
It has my voice, and I've gone over every sentence multiple times, editing, rewriting, and adding.

I know some people don't like AI.
Without it, this book wouldn't exist.
And it's free, so if AI bothers you more than the resulting product might benefit you, please ignore it.

The process of creating this book has been deeply satisfying.
I don't actually know what the future of books is.
The internet and eBooks have certainly impacted the print book industry.
But with AI, how many people -- especially in the computer profession -- will keep reading books?
I hardly do. If I need something I ask AI.
So my only hope is that this book will be engaging to read,
and that you will have some of the same satisfaction that I've had while writing it.

## How the Book Is Organized

Each chapter is largely self-contained, so you can read straight through,
or jump to a chapter that interests you.

*Foundations* is a fast tour of the language: its syntax, containers, functions,
classes, and static typing.
This section is for programmers coming to Python from another language.
If you already know Python, you can skim for topics you don't know, or skip it altogether.

*Techniques* covers the idioms and tools that give Python its character:
testing, data classes as types, pattern matching, functional error handling,
decorators, comprehensions, and metaprogramming.
At the end of this part, a chapter steps back to question object orientation itself,
because several of the patterns that follow exist to manage problems that objects create.
Many of these chapters came from various presentations I've given, mostly at Pycon.

*Patterns* works through the classic design patterns,
each reframed for Python and weighed against the language.
I consistently ask what problem we are solving and whether the language already supports a particular pattern.
Learning to ask those questions is one of the most useful things this book can give you.

## The Examples

The book targets Python 3.14 and later, uses type hints throughout, and uses `pytest` for testing.

Every code block that begins with a filename comment, like `# tracer.py`,
is a complete program.
These files live in the `Examples/` directory of the [source repository](https://github.com/BruceEckel/ThinkingInPython),
one folder per chapter,
so the block tagged `# tracer.py` in [Decorators](13_Decorators.md#maintaining-the-wrapped-interface) is the file `Examples/13_Decorators/tracer.py`.
The repository's `tools/README.md` explains how to build the book and run the examples yourself.

The book's tooling extracts the examples,
then type-checks (with Astral's `ty`), runs, and tests them.
The code you read is the code that runs,
and the output shown is the output it produces.

If you find a mistake, corrections are welcome;
see `CONTRIBUTING.md` in the source repository.

## Resources

- [The official Python tutorial](https://docs.python.org/3/tutorial/)
- [The Python Programming FAQ](https://docs.python.org/3/faq/programming.html)
- [Python Bytes](https://pythonbytes.fm/), podcast and newsletter
- [Planet Python](https://planetpython.org/), an aggregator of Python articles from around the web
