# Introduction

This book is about cultivating the judgment to choose the smallest thing that works.
You build that judgment through insights, idioms, and patterns.
It is also honest about design patterns.
Most were invented to work around the limits of static,
inheritance-heavy languages, and in Python many of them diminish or dissolve.
If an idiom or pattern still earns its keep, it stays.

Every language has habits worth learning and habits worth dropping.
Programmers who come to Python from C++ or Java arrive with patterns,
ceremonies, and defensive structures that those languages made necessary.
Python needs far fewer of these.
Instead of a class that exists only to hold one method, Python has functions.
A *Singleton* is a module.
A *Visitor* is a function that dispatches on type.
Before using an idiom or pattern,
this book asks whether the language already solves the problem,
and adds the complexity only when the answer is no.

## AI Trigger Warning

I started this book in 2008, with the idea of taking the design patterns work I had done in Java and translating it to Python.
In 2011 I abandoned the project with many of the design patterns still in Java.
Eventually I even wrote a message confirming I was not going to complete it.

In June of 2026, after having people mention the online book to me at recent PyCons,
I decided to see what the Claude AI could do with it.
The experience was amazing, and I began adding material from talks, writing, and presentations (mostly at PyCon).
Claude allowed me to create tooling for the book that I had imagined but never fully realized.

This book never would have happened without the help of Claude, which gave me tremendous support throughout the process.
That said, it is still my work, derived from existing work, designed by me, checked and rewritten by me.
It has my voice, and I've gone over every sentence multiple times, editing, rewriting, and adding.

I know some people don't like AI.
Without it, this book wouldn't exist.
And it's free, so if AI bothers you more than the resulting product might benefit you, please ignore this book.

Using Claude made me realize how many compromises I've made on books in the past.
I would have a good idea about something (for example, automatically interleaving commented output in the listings),
but I was either unable to implement it or it just seemed too hard so I didn't do it.
But with AI I've been able to explore and often implement every whim,
from things as seemingly straightforward as inserting a new chapter
to ones as daunting as that commented-output system.
The result is much better than I've been able to achieve in the past.
I'm able to keep going until I've tweaked everything that occurs to me.

I can't predict the future of books.
The internet and eBooks have already changed the print book industry.
But with AI, how many people will keep reading computer programming books?
I hardly do.
If I need something, I ask AI.
My only hope is that this book will be engaging to read,
and that you will experience some of the same satisfaction that I've had while writing it.

## Who This Book Is For

I am writing for the programmer who already knows how to program, either in another language or in Python itself.
The goal is to move from writing Python that works to writing Python that is clear,
idiomatic, and a pleasure to maintain.

This is an intermediate book, which removes two constraints:

1.  An introductory book must describe everything in lock step,
    never using an idea before it has been formally introduced.
    This one does not.
2.  An introductory book chooses topics by where they fall in a beginner's path.
    This one chooses them by whether they are interesting and useful.

If a language feature is new to you, look it up as you go.

You should be comfortable with:

- Functions, classes, objects, and inheritance.
- Containers: lists, dictionaries, tuples, and sets.

You do not need to know design patterns, metaclasses,
or type checking; we cover them here.
The book is about the language, not the tooling around it.
Fortunately, `uv` and other tools greatly simplify setup,
so you don't need to spend time on it.
The repository's [README](https://github.com/BruceEckel/ThinkingInPython#thinking-in-python)
gives detailed setup instructions.

## How the Book Is Organized

Each chapter is largely self-contained, so you can read straight through,
or jump to a chapter that interests you.

*Foundations* is a fast tour of the language: its syntax, containers, functions,
classes, and static typing.
This part is for programmers coming to Python from another language.
If you already know Python, you can skim for topics you don't know, or skip it altogether.

*Techniques* covers the idioms and tools that give Python its character:
testing, data classes as types, pattern matching, functional error handling,
decorators, comprehensions, and metaprogramming.
At the end of this part, a chapter steps back to question object orientation itself,
because several of the patterns that follow exist to manage problems that objects create.
Many of these chapters came from presentations I've given, mostly at PyCon.

*Patterns* works through the classic design patterns,
each reframed for Python and weighed against the language.
I consistently ask what problem we are solving and whether the language already does the pattern's job.
Learning to ask those questions is one of the most useful things this book can give you.

## The Examples

The book targets Python 3.14 and later, uses type hints throughout, and tests with `pytest`.

Every code block that begins with a filename comment, like `# tracer.py`,
is a complete program.
These files live in the `Examples/` directory of the [source repository](https://github.com/BruceEckel/ThinkingInPython),
one folder per chapter,
so the code block starting with `# tracer.py` in [Decorators](15_Decorators.md#maintaining-the-wrapped-interface) is the file `Examples/15_Decorators/tracer.py`.
The repository's `tools/README.md` explains how to build the book and run the examples yourself.

The tooling extracts the book examples,
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
