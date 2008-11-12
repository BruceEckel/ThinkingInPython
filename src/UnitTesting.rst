
********************************************************************************
Unit Testing & Test-Driven Development
********************************************************************************

..  note:: This chapter has not had any significant translation yet. Should
           introduce and compare the various common test systems.

One of the important recent realizations is the dramatic value of unit testing.

This is the process of building integrated tests into all the code that you
create, and running those tests every time you do a build. It's as if you are
extending the compiler, telling it more about what your program is supposed to
do. That way, the build process can check for more than just syntax errors,
since you teach it how to check for semantic errors as well.

C-style programming languages, and C++ in particular, have typically valued
performance over programming safety. The reason that developing programs in Java
is so much faster than in C++ (roughly twice as fast, by most accounts) is
because of Java's safety net: features like better type checking, enforced
exceptions and garbage collection. By integrating unit testing into your build
process, you are extending this safety net, and the result is that you can
develop faster. You can also be bolder in the changes that you make, and more
easily refactor your code when you discover design or implementation flaws, and
in general produce a better product, faster.

Unit testing is not generally considered a design pattern; in fact, it might be
considered a "development pattern," but perhaps there are enough "pattern"
phrases in the world already. Its effect on development is so significant that
it will be used throughout this book, and thus will be introduced here.

My own experience with unit testing began when I realized that every program in
a book must be automatically extracted and organized into a source tree, along
with appropriate makefiles (or some equivalent technology) so that you could
just type **make** to build the whole tree. The effect of this process on the
code quality of the book was so immediate and dramatic that it soon became (in
my mind) a requisite for any programming book-how can you trust code that you
didn't compile? I also discovered that if I wanted to make sweeping changes, I
could do so using search-and-replace throughout the book, and also bashing the
code around at will. I knew that if I introduced a flaw, the code extractor and
the makefiles would flush it out.

As programs became more complex, however, I also found that there was a serious
hole in my system. Being able to successfully compile programs is clearly an
important first step, and for a published book it seemed a fairly revolutionary
one-usually due to the pressures of publishing, it's quite typical to randomly
open a programming book and discover a coding flaw. However, I kept getting
messages from readers reporting semantic problems in my code (in *Thinking in
Java*). These problems could only be discovered by running the code. Naturally,
I understood this and had taken some early faltering steps towards implementing
a system that would perform automatic execution tests, but I had succumbed to
the pressures of publishing, all the while knowing that there was definitely
something wrong with my process and that it would come back to bite me in the
form of embarrassing bug reports (in the open source world, embarrassment is one
of the prime motivating factors towards increasing the quality of one's code!).

The other problem was that I was lacking a structure for the testing system.
Eventually, I started hearing about unit testing and Junit [#]_, which provided
a basis for a testing structure. However, even though JUnit is intended to make
the creation of test code easy, I wanted to see if I could make it even easier,
applying the Extreme Programming principle of "do the simplest thing that could
possibly work" as a starting point, and then evolving the system as usage
demands (In addition, I wanted to try to reduce the amount of test code, in an
attempt to fit more functionality in less code for screen presentations). This
chapter is the result.

Write Tests First
=======================================================================

As I mentioned, one of the problems that I encountered-that most people
encounter, it turns out-was submitting to the pressures of publishing and as a
result letting tests fall by the wayside. This is easy to do if you forge ahead
and write your program code because there's a little voice that tells you that,
after all, you've got it working now, and wouldn't it be more
interesting/useful/expedient to just go on and write that other part (we can
always go back and write the tests later). As a result, the tests take on less
importance, as they often do in a development project.

The answer to this problem, which I first found described in *Extreme
Programming Explained*, is to write the tests *before* you write the code. This
may seem to artificially force testing to the forefront of the development
process, but what it actually does is to give testing enough additional value to
make it essential. If you write the tests first, you:

#.  Describe what the code is supposed to do, not with some external graphical
    tool but with code that actually lays the specification down in concrete,
    verifiable terms.

#.  Provide an example of how the code should be used; again, this is a working,
    tested example, normally showing all the important method calls, rather than
    just an academic description of a library.

#.  Provide a way to verify when the code is finished (when all the tests run
    correctly).

Thus, if you write the tests first then testing becomes a development tool, not
just a verification step that can be skipped if you happen to feel comfortable
about the code that you just wrote (a comfort, I have found, that is usually
wrong).

You can find convincing arguments in *Extreme Programming Explained*, as "write
tests first" is a fundamental principle of XP. If you aren't convinced you need
to adopt any of the changes suggested by XP, note that according to Software
Engineering Institute (SEI) studies, nearly 70% of software organizations are
stuck in the first two levels of SEI's scale of sophistication: chaos, and
slightly better than chaos. If you change nothing else, add automated testing.

Simple Python Testing
=======================================================================

Sanity check for a quick test of the programs in this book, and to append the
output of each program (as a string) to its listing::

    # SanityCheck.py
    #! /usr/bin/env python
    import string, glob, os
    # Do not include the following in the automatic
    # tests:
    exclude = ("SanityCheck.py", "BoxObserver.py",)

    def visitor(arg, dirname, names):
        dir = os.getcwd()
        os.chdir(dirname)
        try:
            pyprogs = [p for p in glob.glob('*.py')
                       if p not in exclude ]
            if not pyprogs: return
            print('[' + os.getcwd() + ']')
            for program in pyprogs:
                print('\t', program)
                os.system("python %s > tmp" % program)
                file = open(program).read()
                output = open('tmp').read()
                # Append output if it's not already there:
                if file.find("output = '''") == -1 and \
                  len(output) > 0:
                    divider = '#' * 50 + '\n'
                    file = file.replace('#' + ':~', '#<hr>\n')
                    file += "output = '''\n" + \
                      open('tmp').read() + "'''\n"
                    open(program,'w').write(file)
        finally:
            os.chdir(dir)

    if __name__ == "__main__":
        os.path.walk('.', visitor, None)


Just run this from the root directory of the code listings for the book; it will
descend into each subdirectory and run the program there. An easy way to check
things is to redirect standard output to a file, then if there are any errors
they will be the only thing that appears at the console during program
execution.

A Very Simple Framework
=======================================================================

As mentioned, a primary goal of this code is to make the writing of unit testing
code very simple, even simpler than with JUnit. As further needs are discovered
*during the use* of this system, then that functionality can be added, but to
start with the framework will just provide a way to easily create and run tests,
and report failure if something breaks (success will produce no results other
than normal output that may occur during the running of the test). My intended
use of this framework is in makefiles, and **make** aborts if there is a non-
zero return value from the execution of a command. The build process will
consist of compilation of the programs and execution of unit tests, and if
**make** gets all the way through successfully then the system will be
validated, otherwise it will abort at the place of failure. The error messages
will report the test that failed but not much else, so that you can provide
whatever granularity that you need by writing as many tests as you want, each
one covering as much or as little as you find necessary.

In some sense, this framework provides an alternative place for all those
"print" statements I've written and later erased over the years.

To create a set of tests, you start by making a **static** inner class inside
the class you wish to test (your test code may also test other classes; it's up
to you). This test code is distinguished by inheriting from **UnitTest**::

    # UnitTesting/UnitTest.py
    # The basic unit testing class

    class UnitTest:
        testID = ""
        static List errors = ArrayList()
        # Override cleanup() if test object
        # creation allocates non-memory
        # resources that must be cleaned up:
        def cleanup(self):
        # Verify the truth of a condition:
        def affirm(boolean condition):
            if(!condition)
                errors.add("failed: " + testID)


The only testing method [[ So far ]] is **affirm( )** [#]_, which is
**protected** so that it can be used from the inheriting class. All this method
does is verify that something is **true**. If not, it adds an error to the list,
reporting that the current test (established by the **static testID**, which is
set by the test-running program that you shall see shortly) has failed. Although
this is not a lot of information-you might also wish to have the line number,
which could be extracted from an exception-it may be enough for most situations.

Unlike JUnit (which uses **setUp( )** and **tearDown( )** methods), test objects
will be built using ordinary Python construction. You define the test objects by
creating them as ordinary class members of the test class, and a new test class
object will be created for each test method (thus preventing any problems that
might occur from side effects between tests). Occasionally, the creation of a
test object will allocate non-memory resources, in which case you must override
**cleanup( )** to release those resources.

Writing Tests
=======================================================================

Writing tests becomes very simple. Here's an example that creates the necessary
**static** inner class and performs trivial tests::

    # UnitTesting/TestDemo.py
    # Creating a test

    class TestDemo:
        objCounter = 0
        id = ++objCounter
        def TestDemo(String s):
            print(s + ": count = " + id)

        def close(self):
            print("Cleaning up: " + id)

        def someCondition(self): return True
        class Test(UnitTest):
            TestDemo test1 = TestDemo("test1")
            TestDemo test2 = TestDemo("test2")
            def cleanup(self):
                test2.close()
                test1.close()

            def testA(self):
                print("TestDemo.testA")
                affirm(test1.someCondition())

            def testB(self):
                print("TestDemo.testB")
                affirm(test2.someCondition())
                affirm(TestDemo.objCounter != 0)

            # Causes the build to halt:
            #! def test3(): affirm(0)


The **test3( )**  method is commented out because, as you'll see, it causes the
automatic build of this book's source-code tree to stop.

You can name your inner class anything you'd like; the only important factor is
that it **extends UnitTest**. You can also include any necessary support code in
other methods. Only **public** methods that take no arguments and return
**void** will be treated as tests (the names of these methods are also not
constrained).

The above test class creates two instances of **TestDemo**. The **TestDemo**
constructor prints something, so that we can see it being called. You could also
define a default constructor (the only kind that is used by the test framework),
although none is necessary here. The **TestDemo** class has a **close( )**
method which suggests it is used as part of object cleanup, so this is called in
the overridden **cleanup( )** method in **Test**.

The testing methods use the **affirm( )** method to validate expressions, and if
there is a failure the information is stored and printed after all the tests are
run.  Of course, the **affirm( )** arguments are usually more complicated than
this; you'll see more examples throughout the rest of this book.

Notice that in **testB( )**, the **private** field **objCounter** is accessible
to the testing code-this is because **Test** has the permissions of an inner
class.

You can see that writing test code requires very little extra effort, and no
knowledge other than that used for writing ordinary classes.

To run the tests, you use **RunUnitTests.py** (which will be introduced
shortly). The command for the above code looks like this:

**java com.bruceeckel.test.RunUnitTests TestDemo**

It produces the following output::

    test1: count = 1
    test2: count = 2
    TestDemo.testA
    Cleaning up: 2
    Cleaning up: 1
    test1: count = 3
    test2: count = 4
    TestDemo.testB
    Cleaning up: 4
    Cleaning up: 3


All the output is noise as far as the success or failure of the unit testing is
concerned. Only if one or more of the unit tests fail does the program returns a
non-zero value to terminate the **make** process after the error messages are
produced. Thus, you can choose to produce output or not, as it suits your needs,
and the test class becomes a good place to put any printing code you might need-
if you do this, you tend to keep such code around rather than putting it in and
stripping it out as is typically done with tracing code.

If you need to add a test to a class derived from one that already has a test
class, it's no problem, as you can see here::

    # UnitTesting/TestDemo2.py
    # Inheriting from a class that
    # already has a test is no problem.

    class TestDemo2(TestDemo):
        def __init__(self, s): TestDemo.__init__(s)
        # You can even use the same name
        # as the test class in the base class:
        class Test(UnitTest):
            def testA(self):
                print("TestDemo2.testA")
                affirm(1 + 1 == 2)

            def testB(self):
                print("TestDemo2.testB")
                affirm(2 * 2 == 4)


Even the name of the inner class can be the same. In the above code, all the
assertions are always true so the tests will never fail.

White-Box & Black-Box Tests
=======================================================================

The unit test examples so far are what are traditionally called *white-box
tests*. This means that the test code has complete access to the internals of
the class that's being tested (so it might be more appropriately called
"transparent box" testing). White-box testing happens automatically when you
make the unit test class as an inner class of the class being tested, since
inner classes automatically have access to all their outer class elements, even
those that are **private**.

A possibly more common form of testing is *black-box testing*, which refers to
treating the class under test as an impenetrable box. You can't see the
internals; you can only access the **public** portions of the class. Thus,
black-box testing corresponds more closely to functional testing, to verify the
methods that the client programmer is going to use. In addition, black-box
testing provides a minimal instruction sheet to the client programmer - in the
absence of all other documentation, the black-box tests at least demonstrate how
to make basic calls to the **public** class methods.

To perform black-box tests using the unit-testing framework presented in this
book, all you need to do is create your test class as a global class instead of
an inner class. All the other rules are the same (for example, the unit test
class must be **public**, and derived from **UnitTest**).

There's one other caveat, which will also provide a little review of Java
packages. If you want to be completely rigorous, you must put your black-box
test class in a separate directory than the class it tests, otherwise it will
have package access to the elements of the class being tested. That is, you'll
be able to access **protected** and **friendly** elements of the class being
tested. Here's an example::

    # UnitTesting/Testable.py

    class Testable:
        def f1(): pass
        def f2(self): pass # "Friendly": package access
        def f3(self): pass # Also package access
        def f4(self): pass


Normally, the only method that should be directly accessible to the client
programmer is **f4( )**. However, if you put your black-box test in the same
directory, it automatically becomes part of the same package (in this case, the
default package since none is specified) and then has inappropriate access::

    # UnitTesting/TooMuchAccess.py

    class TooMuchAccess(UnitTest):
        Testable tst = Testable()
        def test1(self):
            tst.f2() # Oops!
            tst.f3() # Oops!
            tst.f4() # OK


You can solve the problem by moving **TooMuchAccess.py** into its own
subdirectory, thereby putting it in its own default package (thus a different
package from **Testable.py**). Of course, when you do this, then **Testable**
must be in its own package, so that it can be imported (note that it is also
possible to import a "package-less" class by giving the class name in the
**import** statement and ensuring that the class is in your CLASSPATH)::

    # UnitTesting/testable/Testable.py
    package c02.testable

    class Testable:
        def f1(): pass
        def f2(self): # "Friendly": package access
        def f3(self): # Also package access
        def f4(self):


Here's the black-box test in its own package, showing how only public methods
may be called::

    # UnitTesting/BlackBoxTest.py

    class BlackBoxTest(UnitTest):
        Testable tst = Testable()
        def test1(self):
            #! tst.f2() # Nope!
            #! tst.f3() # Nope!
            tst.f4() # Only public methods available


Note that the above program is indeed very similar to the one that the client
programmer would write to use your class, including the imports and available
methods. So it does make a good programming example. Of course, it's easier from
a coding standpoint to just make an inner class, and unless you're ardent about
the need for specific black-box testing you may just want to go ahead and use
the inner classes (with the knowledge that if you need to you can later extract
the inner classes into separate black-box test classes, without too much
effort).

Running tests
=======================================================================

The program that runs the tests makes significant use of reflection so that
writing the tests can be simple for the client programmer::

    # UnitTesting/RunUnitTests.py
    # Discovering the unit test
    # class and running each test.

    class RunUnitTests:
        def require(requirement, errmsg):
            if(!requirement):
                print(errmsg)
                sys.exit()

        def main(self, args):
            require(args.length == 1,
              "Usage: RunUnitTests qualified-class")
            try:
                Class c = Class.forName(args[0])
                # Only finds the inner classes
                # declared in the current class:
                Class[] classes = c.getDeclaredClasses()
                Class ut = null
                for(int j = 0 j < classes.length j++):
                    # Skip inner classes that are
                    # not derived from UnitTest:
                    if(!UnitTest.class.
                        isAssignableFrom(classes[j]))
                        continue
                    ut = classes[j]
                    break # Finds the first test class only

                # If it found an inner class,
                # that class must be static:
                if(ut != null)
                    require(
                      Modifier.isStatic(ut.getModifiers()),
                      "inner UnitTest class must be static")
                # If it couldn't find the inner class,
                # maybe it's a regular class (for black-
                # box testing:
                if(ut == null)
                    if(UnitTest.class.isAssignableFrom(c))
                        ut = c
                require(ut != null,
                  "No UnitTest class found")
                require(
                  Modifier.isPublic(ut.getModifiers()),
                  "UnitTest class must be public")
                Method[] methods = ut.getDeclaredMethods()
                for(int k = 0 k < methods.length k++):
                    Method m = methods[k]
                    # Ignore overridden UnitTest methods:
                    if(m.getName().equals("cleanup"))
                        continue
                    # Only public methods with no
                    # arguments and void return
                    # types will be used as test code:
                    if(m.getParameterTypes().length == 0 &&
                       m.getReturnType() == void.class &&
                       Modifier.isPublic(m.getModifiers())):
                        # The name of the test is
                        # used in error messages:
                        UnitTest.testID = m.getName()
                        # A instance of the
                        # test object is created and
                        # cleaned up for each test:
                        Object test = ut.newInstance()
                        m.invoke(test, Object[0])
                        ((UnitTest)test).cleanup()

            except e:
                e.printStackTrace(System.err)
                # Any exception will return a nonzero
                # value to the console, so that
                # 'make' will abort:
                System.err.println("Aborting make")
                System.exit(1)

            # After all tests in this class are run,
            # display any results. If there were errors,
            # abort 'make' by returning a nonzero value.
            if(UnitTest.errors.size() != 0):
                it = UnitTest.errors.iterator()
                while(it.hasNext()):
                    print(it.next())
                sys.exit(1)


Automatically Executing Tests
=======================================================================

Exercises
=======================================================================

#.  Install this book's source code tree and ensure that you have a **make**
    utility installed on your system (Gnu **make** is freely available on the
    internet at various locations). In **TestDemo.py**, un-comment **test3( )**,
    then type **make** and observe the results.

#.  Modify TestDemo.py by adding a new test that throws an exception. Type
    **make** and observe the results.

#.  Modify your solutions to the exercises in Chapter 1 by adding unit tests.
    Write makefiles that incorporate the unit tests.

.. rubric:: Footnotes

.. [#] *http://www.junit.org*

.. [#] I had originally called this **assert()**, but that word became reserved
       in JDK 1.4 when assertions were added to the language.


