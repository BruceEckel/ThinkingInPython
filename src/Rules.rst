*******************************************************************************
Book Development Rules
*******************************************************************************

Guidelines for the creation process.

.. note:: This is just a start. This document will evolve as more issues appear.

Contribute What You Can
===============================================================================

One of the things I've learned by holding open-spaces conferences is that
everyone has something useful to contribute, although they often don't know it.

Maybe you're don't feel expert enough at Python to contribute anything yet.
But you're in this field, so you've got some useful abilities.

- Maybe you're good at admin stuff, figuring out how things work and configuring
  things.

- If you have a flair for design and can figure out Sphinx templating,
  that will be useful.

- Perhaps you are good at Latex. We need to figure out how to format the
  PDF version of the book from the Sphinx sources, so that we can produce
  the print version of the book without going through hand work in a layout
  program.

- You probably have ideas about things you'd like to understand, that haven't
  been covered elsewhere.

- And sometimes people are particularly good at spotting typos.

Don't Get Attached
===============================================================================

Writing is rewriting. Your stuff will get rewritten, probably multiple times.
This makes it better for the reader. It doesn't mean it was bad. Everything can
be made better.

By the same measure, don't worry if your examples or prose aren't perfect. Don't
let that keep you from contributing them early. They'll get rewritten anyway, so
don't worry too much -- do the best you can, but don't get blocked.

There's also an editor who will be rewriting for clarity and active voice. He
doesn't necessarily understand the technology but he will still be able to
improve the flow. If you discover he has introduced technical errors in the
prose, then feel free to fix it but try to maintain any clarity that he has
added.

If something is moved to Volume 2 or the electronic-only appendices, it's just
a decision about the material, not about you.

Credit
===============================================================================

As much as possible, I want to give credit to contributions. Much of this will
be taken care of automatically by the Launchpad.net "Karma" system. However, if
you contribute something significant, for example the bulk of a new chapter,
then you should put "contributed by" at the beginning of that chapter, and if
you make significant improvements and changes to a chapter you should say
"further contributions by" or "further changes by", accordingly.

Mechanics
===============================================================================

- Automate everything. Everything should be in the build script; nothing should
  be done by hand.

- All documents will be in Sphinx restructured text format. Here's the
  `link to the Sphinx documentation <http://sphinx.pocoo.org/contents.html>`_.

- Everything goes through Launchpad.net and uses Launchpad's Bazzar distributed
  version control system.

- Follow PEP8 for style. That way we don't have to argue about it.

- Camelcasing for naming. PEP8 suggests underscores as a preference rather than
  a hard-and fast rule, and camelcasing *feels* more like OO to me, as if we are
  emphasizing the design here (which I want to do) and putting less focus on the
  C-ish nature that *can* be expressed in Python.

::

    The above point is still being debated.

- Four space indents.

- We're not using chapter numbers because we'll be moving chapters around.
  If you need to cross-reference a chapter, use the chapter name and a
  link.

- Index as you go. Indexing will happen throughout the project. Although
  finalizing the index is a task in itself, it will be very helpful if everyone
  adds index entries anytime they occur to you. You can find example index
  entries by going to the index, clicking on one of the entries, then selecting
  "view source" in the left-side bar (Sphinx cleverly shows you the Sphinx
  source so you can use it as an example).

- Don't worry about chapter length. Some chapters may be very small, others may
  be quite significant. It's just the nature of this book. Trying to make the
  chapters the same length will end up fluffing some up which will not benefit
  the reader. Make the chapters however long they need to be, but no longer.

Diagrams
===============================================================================

Create diagrams using whatever tool is convenient for you, as long as it produces
formats that Sphinx can use.

It doesn't matter if your diagram is imperfect. Even if you just sketch something
by hand and scan it in, it will help readers visualize what's going on.

At some point, diagrams will be redone for consistency using a single tool,
with print publication in mind. This tool may be a commercial product. However,
if you need to change the diagram you can replace it with your new version using
your tool of choice. The important thing is to get the diagram right; at some
point it will be redone to look good.

Note that all image tags should use a ``*`` at the end, not the file extension
name. For example ``..image:: _images/foo.*``. This way the tag will work for
both the HTML output and the Latex output. Also, all images should be placed
in the ``_images`` directory.

Here's an example which was done with the free online service Gliffy.com, then
modified using the free Windows program Paint.NET (note, however, that we should
not use color because it won't translate well to the print book):

.. image:: _images/DistributedSystem.*

