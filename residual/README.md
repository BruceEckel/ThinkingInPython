Why This Project Failed
=======================

### Summary: Experiments and Assumptions

-   Tried some different sharing formats (e.g. wiki)

-   Ended up here for DVCS

-   Too many people didn't understand DVCS

-   I didn't understand DVCS

### This Project Was An Experiment

I had to extract a lot of the design patterns from a later edition of Thinking
in Java because that book was getting too big. I thought it would be interesting
to see if they translated to Python and also to try an open-source book project.
This was really my first attempt at the learning curve of creating open-source
(I had grown up with closed source and I now realize there's a cultural shift;
people who've started in programming in recent years have an advantage here).

So one of my first hurdles was "how do I incorporate feedback and
contributions?" I attempted several web-document approaches like Google Docs and
a Wiki, but there were problems with each that I can’t remember.

Finally, someone pointed out that open source is effectively based on
*Distributed Version Control Systems* (DVCS), so it made sense to move it to
BitBucket (BitBucket used Mercurial at the time, which is written in Python, so
a logical place for a Python project. BitBucket has since changed to being
predominantly Git, as Git has ultimately dominated the DVCS landscape).

I slowly began to discover that most people don’t know how to use DVCS. More
importantly, **I** didn’t know how to use it (part of the project was to learn
it, I guess). In particular, I started getting these things called “pull
requests” and I kept thinking “if you want to pull something, pull it! Why are
you bothering asking me to pull something?” I now understand that the pull
request is poorly named. It should be called a “patch request” or something more
intuitive.

I apologize profusely to all those whose pull requests I ignored. That’s why: I
had no idea what they were about. (I've written a [blog post explaining pull requests](http://bruceeckel.github.io/2015/08/03/pull-requests-the-linchpin-of-open-source/))

And for everyone else, the DVCS was too big of a hurdle to figure out *and* at
the same time help contribute to the book. Another lesson that we humans are not
equipped to multitask.

By the time I had understood all this, it seemed like the moment had passed.

1.  I’ve moved on to other projects

2.  I’m not even sure how much sense it makes to try to adapt design patterns
    from another language into Python. I’ve internalized the “design patterns
    represent language failures” concept so I wonder how many of these patterns
    will ultimately be useful. But clearly, a simple translation of the
    Gang-of-Four patterns into Python is not that helpful. (Here's Peter Norvig on 
    [Design Patterns for Dynamic Languages](http://norvig.com/design-patterns/)).

I’m leaving this project up for archival etc. reasons, and in case someone wants
to fork it and incorporate the pull requests (see, that’s another basic question
I don’t have the answer to: If you fork this project, do you automatically get
all the pull requests too?).