# Introduction

This is a collection of essays that give you a deeper understanding of
programming in Python. The next chapter,
[Python for Programmers](02_Python_for_Programmers.md), is a fast tour of the
language, but this is not an introductory book. There are plenty of excellent
Python tutorials and online courses for that. The rest of the chapters assume
you can already read and write Python and follow along. If a language feature is
new to you, look it up as you go.

Think of this as an intermediate book. The "somewhat advanced" label fits too,
but the "somewhat" matters. Because the book is not introductory, two
constraints fall away:

1.  An introductory book must describe everything in lock step, never using an
    idea before it has been formally introduced. This one does not.
2.  An introductory book chooses topics by where they fall in a beginner's path.
    This one chooses them by whether they are interesting and useful.

## Who This Book Is For

I am writing for the programmer who already knows how to program, knows at least
the basics of Python, and now wants to understand it more deeply. Maybe you came
to Python from another language, the way I came from C++ and Java. Maybe you
picked up the syntax from a tutorial, get real work done, and still sense there
is more to the language than you are using. Either way the goal is the same: to
move from writing Python that works to writing Python that is clear, idiomatic,
and a pleasure to maintain.

A theme runs through the book, and especially the pattern chapters in the second
half. Many of the classic design patterns were invented to work around
limitations of other languages. Python often dissolves the problem a pattern was
solving, or shrinks it to a few lines. Where that happens I say so plainly. Where
a pattern still earns its keep I keep it and explain why. Learning to ask "does
the language already handle this?" is one of the most useful habits this book can
give you.

## What You Should Already Know

You should be comfortable with:

- Functions, classes, and objects, including inheritance and polymorphism.
- Python's syntax and its built-in containers: lists, dictionaries, tuples, and
  sets.
- Running a Python program and installing a package.

The book is about the language, not the tooling around it. It does not explain
installing Python, setting up virtual environments, or managing packages. Those
are assumed, or easy to find elsewhere, starting with the official Python
documentation.

You do not need to know design patterns, metaclasses, or type checking before
you start. The book builds those up. If your grasp of objects is shaky, it will
grow stronger as you watch objects used in many different situations here.

## How to Read This Book

The early chapters cover language features and idioms: testing, decorators,
metaprogramming, comprehensions, and more. The later chapters work through the
design patterns, reframed for Python. You can read straight through, or jump to
a chapter that matches a problem in front of you, since each one is largely
self-contained.

Every example is real. The examples are extracted from these chapters, then run
and type-checked automatically, so the code you read is the code that ran, and
the output shown is the output it produced. The examples target Python 3.14 and
later, use type hints throughout, and are checked with Astral's `ty`. If type
checking is new to you, [Static Type Checking](04_Static_Type_Checking.md) has
its own chapter.

## The Code Examples

Every code block that starts with a filename comment, like `# trace.py`, is a
complete program. These files are extracted from the chapters and live in the
`Examples/` directory of the
[source repository](https://github.com/BruceEckel/ThinkingInPython), one folder
per chapter, named to match the chapter. So a block tagged `# trace.py` in the
Decorators chapter is the file `Examples/08_Decorators/trace.py`. The examples
that read a data file, or that span several files, keep them together in the same
chapter folder.

The build tooling is managed by [uv](https://docs.astral.sh/uv), and a `Makefile`
drives it. Once you have cloned the repository and installed uv, these are the
targets worth knowing:

- `make examples` extracts every example from the chapters and runs each one.
- `make test` runs the book's pytest examples.
- `make ty` type-checks the examples with `ty`.
- `make site` builds the browsable HTML version of the book, and `make serve`
  serves it at a local address.
- `make ci` runs the whole set of checks, the same ones that guard every change
  to the book.

If you do not have `make`, each target is a short `uv run python tools/...`
command. The details are in `tools/README.md`.

If you find a mistake, corrections are welcome. See `CONTRIBUTING.md` in the
source repository.
