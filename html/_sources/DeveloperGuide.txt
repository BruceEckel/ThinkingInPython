*******************************************************************************
Developer Guide
*******************************************************************************

Details for people participating in the book development process.

Getting Started: The Easiest Approach
===============================================================================

If all of the details are a little overwhelming at first, there's an easy way
for you to make contributions without learning about distributed version control
and Sphinx:

1.  Create an account at http://www.BitBucket.org.

2.  In your account, you get a wiki. In your wiki, create a page for your
    contribution. Just add your code and descriptions using plain text.

3.  Point us to your wiki via the `newsgroup
    <http://groups.google.com/group/python3patterns/>`_.

4.  We'll take your contribution and do the necessary formatting.

If you want to take another step, you can learn how to format your wiki page
using Sphinx by looking at the source for pages in the book. You can try it
right now -- on the left side of this page (in the HTML book) you'll see a
header that says **This Page** and underneath it **Show Source**. Click on
**Show Source** and you'll see the Sphinx source for this page. Just look at
the page sources and imitate that.

When you're ready, you can learn more about Sphinx and Mercurial and begin
making contributions that way.

The following sections are for those who are ready to build the book on their
own machines.

For Windows Users
===============================================================================

You need to install Cygwin; go to:

    http://www.cygwin.com

You need to install at least the ``make`` utility, but I find that ``chere``
(command prompt here) is also very useful.

Also install ``openssh`` (under **Net**), so you can create your RSA key
for Mercurial.

I've discovered that it's best if you *don't* install Python as part of
Cygwin; instead use a single Python installation under windows. Cygwin will
find the installation if it is on your Windows PATH.

Because of this, you shouldn't select "mercurial" when you're
installing Cygwin because that will cause Python to be installed. Instead,
install them as standalone Windows applications (see below).

Installing Sphinx
===============================================================================

Because we are sometimes pushing the boundaries of Sphinx, you'll need to get
the very latest development version (a.k.a. the "tip").

#. Get mercurial:

    http://www.selenic.com/mercurial

    Avoid installing the tortoiseHG part - it has caused trouble w/ Python
    debuggers.

#. To get the Sphinx trunk, start with:

    ``$ hg clone http://www.bitbucket.org/birkenfeld/sphinx/``

    and to update, use:

    ``$ hg pull``

    Once you update, run

    ``$ python setup.py install``

    (You can repeat this step whenever you need to update).

    We may talk about minimum version numbers to process the book. Check your
    version with:

    ``$ hg identify -n``

The full anouncement from Georg (Sphinx creator) is here:

    http://groups.google.com/group/sphinx-dev/browse_thread/thread/6dd415847e5cbf7c

Mercurial Cheat sheets & quick starts should be enough to answer your questions:

    - http://edong.net/2008v1/docs/dongwoo-Hg-120dpi.png
    - http://www.ivy.fr/mercurial/ref/v1.0/

Getting the Development Branch of the Book
===============================================================================

This book uses BitBucket.org tools, and additional tools if necessary.

#.  Sign up for an account at http://BitBucket.org.

#.  You must create an rsa key. Under OSX and Linux, and if you installed
    ``openssh with`` Cygwin under windows, you run ``ssh-keygen`` to generate
    the key, and then add it to your BitBucket account.

#.  Go to http://www.bitbucket.org/BruceEckel/python-3-patterns-idioms/, and
    you'll see instructions for getting a branch for development.

#.  Work on your branch and make local commits and commits to your BitBucket
    account.

Building the Book
===============================================================================

To ensure you have Cygwin installed correctly (if you're using windows) and
to see what the options are, type:

    ``make``

at a shell prompt. Then you can use ``make html`` to build the HTML version of
the book, or ``make htmlhelp`` to make the windows help version, etc.

You can also use the ``build`` system I've created (as a book example; it is
part of the distribution). This will call ``make`` and it simplifies many of the
tasks involved. Type:

    ``build help``

to see the options.

.. todo:: The remainder of this document needs rewriting. Rewrite this section for BitBucket & Mercurial; make some project specific diagrams;
Working with BitBucket and Mercurial

===============================================================================

.. note:: Adapted from a posting by Yarko Tymciurak


This assumes that you have created a local branch on your private machine where
you do work, and keep it merged with the trunk.

That is, you've done:

   - Forked a branch of http://www.bitbucket.org/BruceEckel/python-3-patterns-idioms/ (the main trunk; this fork will provide a place for review and comment)
   - cloned the trunk to your local machine:
     - hg clone https://my_login@bitbucket.org/BruceEckel/python-3-patterns-idioms/
   - cloned your local copy of trunk to create a working directory:
     - hg clone python-3-patterns-idioms devel

.. ToDo:: This section still work in progress:

   - ``hg branch lp:python3patterns``
   - ``hg commit -m 'initial checkout'``
   - (hack, hack, hack....)
   - ``hg merge``   (pull new updates)
   - ``hg commit -m 'checkin after merge...'``
   - ... and so on...

When you have a new function idea, or think you've found a bug, ask Bruce
on the group.

   -  If you have a new feature, register a blueprint on BitBucket and
      describe what you're going to do.
   -  If you have found a bug, make a bug report on BitBucket (later assign
      it to yourself, and link your branch to it);
   -  If you want to work on a project, look for an unassigned bug and try to
      work it out - then proceed as below...

When you are ready to share your work have others review, register a branch.


.. note:: You can re-use one branch for multiple bug fixes.

1.  Sign up for an account on BitBucket.org

2.  Go to the project and select "register branch"
    (``https://code.BitBucket.org/python3patterns/+addbranch``). Suggest you
    create a hosted branch, then you can work locally, and pull/push as you make
    progress (see
    http://doc.Mercurial-vcs.org/latest/en/user-guide/index.html#organizing).

3.  Once you have registered your branch, BitBucket will provide you with
    instructions on how to pull and push to your personal development copy.

4.  Link your bug report or blueprint to your branch.

5.  Merge from your "parent" (the trunk, or others you are working with) as needed.

6.  Push your working copy to BitBucket as your work is ready for others to
    review or test.

7.  Once you are done making your changes, have completed testing, and are
    ready for the project team to inspect & test, please select "propose for
    merging"

8.  Somebody on the core team will make a test merge (it may include
    merging with other patches). Once tests pass, and your branch is accepted,
    it will be merged into the trunk.


