

********************************************************************************
Jython
********************************************************************************

.. note:: This chapter is being brought up to date with Jython 2.5,
   	  and will need changes when Jython 3 comes out.

This chapter looks at the value of crossing language boundaries. It is often
advantageous to solve a problem using more than one programming language, rather
than being arbitrarily stuck using a single language. As you'll see in this
chapter, a problem that is very difficult or tedious to solve in one language
can often be solved quickly and easily in another. If you can combine the use of
languages, you can create your product much more quickly and cheaply.

The most straightforward use of this idea is the *Interpreter* design
pattern, which adds an interpreted language to your program to allow
the end user to easily customize a solution. If the application user
needs greater run time flexibility, for example to create scripts
describing the desired behavior of the system, you can use the
*Interpreter* by creating and embedding a language interpreter into
your program.

In Java, the easiest and most powerful way to do this is with *Jython*
[#]_, an implementation of Python in pure Java byte codes. As you will
see, this brings together the benefits of both worlds.

*Interpreter* solves a particular problem - that of creating a
scripting language for the user. But sometimes it's just easier and
faster to temporarily step into another language to solve a particular
aspect of your problem. You're not creating an interpreter, you're
just writing some code in another language.  Again, Jython is a good
example of this, but CORBA also allows you to cross language
boundaries.

Interpreter Motivation
=======================================================================

Remember that each design pattern allows one or more factors to change, so it's
important to first be aware of which factor is changing. Sometimes the end users
of your application (rather than the programmers of that application) need
complete flexibility in the way that they configure some aspect of the program.
That is, they need to do some kind of simple programming. The interpreter
pattern provides this flexibility by adding a language interpreter.

The problem is that developing your own language and building an interpreter is
a time-consuming distraction from the process of developing your application.
You must ask whether you want to finish writing your application or create a new
language.  The best solution is to reuse code: embed an interpreter that's
already been built and debugged for you. The Python language can be freely
embedded into your for-profit application without signing any license agreement,
paying royalties, or dealing with strings of any kind. There are basically no
restrictions at all when you're using Python.

For solving Java problems, we will look at a special version of Python called
Jython. This is generated entirely in Java byte codes, so incorporating it into
your application is quite simple,  and it's as portable as Java is. It has an
extremely clean interface with Java: Java can call Python classes, and Python
can call Java classes.

Because Jython is just Java classes, it can often be "stealthed" into
companies that have rigid processes for using new languges and
tools. If Java has been accepted, such companies often accept anything
that runs on the JVM without question.

Python is designed with classes from the ground up and is a truly pure object
oriented language (both C++ and Java violate purity in various ways). Python
scales up so that you can create very big programs without losing control of the
code.

Installation
=======================================================================

To install Jython, go to `http://jython.sourceforge.net
<http://jython.sourceforge.net>`_.  

.. note:: Select "test the beta".

The download is a **.class** file, which will run an installer when
you execute it with Java.

You also need to add **jython-complete.jar** to your Java CLASSPATH.
As an example, here is the appropriate section in my ``.bashrc``::

   export set JYTHON_HOME="/Users/bruceeckel/jython2.5b0"
   export set CLASSPATH=.:..:$JYTHON_HOME/jython-complete.jar

When you run Jython, you might get the error: ``can't create package
cache dir, '/cachedir/packages'``. Jython caching requires
``/cachedir/packages/`` in the ``python.home`` directory. It is often
the case on \*nix that users lack sufficient priveledges to create or
write to this directory. Because the problem is merely permissions,
something like ``mkdir cachedir; chmod a+rw cachedir`` within the
Jython directory should eliminate this error message.

Getting the Trunk
-----------------------------------------------------------------------

.. note:: This section has not been successfuly tested yet.

The Jython development trunk is very stable so it's safe to get as the most recent
version of the implementation. The subversion command is::

	svn co https://jython.svn.sourceforge.net/svnroot/jython/trunk/jython

Then just invoke ``ant`` against the ``build.xml`` file.
``dist/bin/jython`` is a shell script that starts up jython in console mode.
Lastly, modify the registry (in dist/registry) so that::

	python.console=org.python.util.ReadlineConsole
	python.console.readlinelib=GnuReadline

(``readline`` is GPL, so it makes it a bit harder to automate this part of the distro).
See: http://wiki.python.org/jython/ReadlineSetup


Scripting
=======================================================================

One very compelling benefit of using a dynamic language on the JVM is
scripting.  You can rapidly create and test code, and solve problems
more quickly.

Here's an example that shows a little of what you can do in a Jython
script, and also gives you a sense of performance::

	# Jython/Simple.py
	import platform, glob, time
	from subprocess import Popen, PIPE

	print platform.uname() # What are we running on?
	print glob.glob("*.py") # Find files with .py extensions
	# Send a command to the OS and capture the results:
	print Popen(["ping", "-c", "1", "www.mindview.net"], 
	               stdout=PIPE).communicate()[0]
        # Time an operation:
	start = time.time()
	for n in xrange(1000000):
	    for i in xrange(10): 
	            oct(i)
        print time.time() - start

..  note:: The ``timeit`` module in the alpha distribution could not
   	   be used as it tries to turn off the Java garbage collector.

If you run this program under both cpython and Jython, you'll see that
the timed loop produces very similar results; Jython 2.5 is in beta so
this is quite impressive and should get faster -- there's even talk
that Jython could run faster than cpython, because of the optimization
benefits of the JVM. The total runtime of the cpython version is
faster because of its rapid startup time; the JVM always has a delay
for startup.

Note that things that require much more code (and often research) in
Java are very quick to write in Jython.

Often more sophisticated programs begin as scripts, and then evolve.
The fact that you can quickly try things out allows you to test
concepts, and then create more refined code as needed.

Creating a Language
=======================================================================

It turns out to be remarkably simple to use Jython to create an
interpreted language inside your application. Consider the greenhouse
controller example from *Thinking in Java*. This is a situation where
you want the end user -- the person managing the greenhouse -- to have
configuration control over the system, and so a simple scripting
language is the ideal solution.  This is often called a
*domain-specific language* (DSL) because it solves a particular
domain problem.

To create the language, we'll simply write a set of Python classes,
and the constructor of each will add itself to a (static) master
list. The common data and behavior will be factored into the base
class **Event**. Each **Event** object will contain an **action**
string (for simplicity - in reality, you'd have some sort of
functionality) and a time when the event is supposed to run.  The
constructor initializes these fields, and then adds the new **Event**
object to a static list called **events** (defining it in the class,
but outside of any methods, is what makes it static)::

    # Jython/GreenHouseLanguage.py

    class Event:
        events = [] # static
        def __init__(self, action, time):
            self.action = action
            self.time = time
            Event.events.append(self)
        # Used by sort(). This will cause
        # comparisons to be based only on time:
        def __cmp__ (self, other):
            if self.time < other.time: return -1
            if self.time > other.time: return 1
            return 0
        def run(self):
            print("%.2f: %s" % (self.time, self.action))

    class LightOn(Event):
        def __init__(self, time):
            Event.__init__(self, "Light on", time)

    class LightOff(Event):
        def __init__(self, time):
            Event.__init__(self, "Light off", time)

    class WaterOn(Event):
        def __init__(self, time):
            Event.__init__(self, "Water on", time)

    class WaterOff(Event):
        def __init__(self, time):
            Event.__init__(self, "Water off", time)

    class ThermostatNight(Event):
        def __init__(self, time):
            Event.__init__(self,"Thermostat night", time)

    class ThermostatDay(Event):
        def __init__(self, time):
            Event.__init__(self, "Thermostat day", time)

    class Bell(Event):
        def __init__(self, time):
            Event.__init__(self, "Ring bell", time)

    def run():
        Event.events.sort();
        for e in Event.events:
            e.run()

    if __name__ == "__main__":
        ThermostatNight(5.00)
        LightOff(2.00)
        WaterOn(3.30)
        WaterOff(4.45)
        LightOn(1.00)
        ThermostatDay(6.00)
        Bell(7.00)
        run()

.. note:: To run this program say ``python GreenHouseLanguage.py`` or
   	  ``jython GreenHouseLanguage.py``.

The constructor of each derived class calls the base-class constructor, which
adds the new object to the list. The **run( )** function sorts the list, which
automatically uses the **__cmp__( )** method that was defined in **Event** to
base comparisons on time only. In this example, it only prints out the list, but
in the real system it would wait for the time of each event to come up and then
run the event.

The **__main__** section performs a simple test on the classes.

The above file is now a module that can be included in another Python program to
define all the classes it contains. But instead of an ordinary Python program,
let's use Jython, inside of Java. This turns out to be remarkably simple: you
import some Jython classes, create a **PythonInterpreter** object, and cause the
Python files to be loaded:

..  code-block:: java

    // Jython/GreenHouseController.java
    import org.python.core.*;
    import org.python.util.PythonInterpreter;

    public class GreenHouseController {
      public static void main(String[] args) throws PyException  {
        PythonInterpreter interp = new PythonInterpreter();
        System.out.println("Loading GreenHouse Language");
        interp.execfile("GreenHouseLanguage.py");
        System.out.println("Loading GreenHouse Script");
        interp.execfile("Schedule.ghs");
        System.out.println("Executing GreenHouse Script");
        interp.exec("run()");
      }
    }


The **PythonInterpreter** object is a complete Python interpreter that accepts
commands from the Java program. One of these commands is **execfile( )**, which
tells it to execute all the statements it finds in a particular file. By
executing **GreenHouseLanguage.py**, all the classes from that file are loaded
into our **PythonInterpreter** object, and so it now "holds" the greenhouse
controller language. The **Schedule.ghs** file is the one created by the end
user to control the greenhouse. Here's an example::

    # Jython/Schedule.ghs
    Bell(7.00)
    ThermostatDay(6.00)
    WaterOn(3.30)
    LightOn(1.00)
    ThermostatNight(5.00)
    LightOff(2.00)
    WaterOff(4.45)


This is the goal of the interpreter design pattern: to make the configuration of
your program as simple as possible for the end user. With Jython you can achieve
this with almost no effort at all.

One of the other methods available to the **PythonInterpreter** is
**exec( )**, which allows you to send a command to the interpreter. In
the above program, the **run( )** function is called using **exec()**.

Controlling the Interpreter
=======================================================================

The prior example only creates and runs the interpreter using external scripts.
In the rest of this chapter, we shall look at more sophisticated ways to
interact with Jython. The simplest way to exercise more control over the
**PythonInterpreter** object from within Java is to send data to the
interpreter, and pull data back out.

Putting Data In
--------------------------------------------------------------------------------

To inject data into your Python program, the **PythonInterpreter** class has a
deceptively simple method: **set( )**. However, **set( )** takes many different
data types and performs conversions upon them.  The following example is a
reasonably thorough exercise of the various **set( )** possibilities, along with
comments that should give a fairly complete explanation:

..  code-block:: java

    // Jython/PythonInterpreterSetting.java
    // Passing data from Java to python when using
    // the PythonInterpreter object.
    import org.python.util.PythonInterpreter;
    import org.python.core.*;
    import java.util.*;

    public class PythonInterpreterSetting {
      public static void main(String[] args) throws PyException  {
        PythonInterpreter interp = new PythonInterpreter();
        // It automatically converts Strings
        // into native Python strings:
        interp.set("a", "This is a test");
        interp.exec("print(a)");
        interp.exec("print(a[5:])"); // A slice
        // It also knows what to do with arrays:
        String[] s = { "How", "Do", "You", "Do?" };
        interp.set("b", s);
        interp.exec("for x in b: print(x[0], x)");
        // set() only takes Objects, so it can't
        // figure out primitives. Instead,
        // you have to use wrappers:
        interp.set("c", new PyInteger(1));
        interp.set("d", new PyFloat(2.2));
        interp.exec("print(c + d)");
        // You can also use Java's object wrappers:
        interp.set("c", new Integer(9));
        interp.set("d", new Float(3.14));
        interp.exec("print(c + d)");
        // Define a Python function to print arrays:
        interp.exec(
          "def prt(x): \n" +
          "  print(x)\n" +
          "  for i in x: \n" +
          "    print(i,)\n" +
          "  print(x.__class__)\n");
        // Arrays are Objects, so it has no trouble
        // figuring out the types contained in arrays:
        Object[] types = {
          new boolean[]{ true, false, false, true },
          new char[]{ 'a', 'b', 'c', 'd' },
          new byte[]{ 1, 2, 3, 4 },
          new int[]{ 10, 20, 30, 40 },
          new long[]{ 100, 200, 300, 400 },
          new float[]{ 1.1f, 2.2f, 3.3f, 4.4f },
          new double[]{ 1.1, 2.2, 3.3, 4.4 },
        };
        for(int i = 0; i < types.length; i++) {
          interp.set("e", types[i]);
          interp.exec("prt(e)");
        }
        // It uses toString() to print Java objects:
        interp.set("f", new Date());
        interp.exec("print(f)");
        // You can pass it a List
        // and index into it...
        List x = new ArrayList();
        for(int i = 0; i < 10; i++)
            x.add(new Integer(i * 10));
        interp.set("g", x);
        interp.exec("print(g)");
        interp.exec("print(g[1])");
        // ... But it's not quite smart enough
        // to treat it as a Python array:
        interp.exec("print(g.__class__)");
        // interp.exec("print(g[5:])"); // Fails
        // must extract the Java array:
        System.out.println("ArrayList to array:");
        interp.set("h", x.toArray());
        interp.exec("print(h.__class__)");
        interp.exec("print(h[5:])");
        // Passing in a Map:
        Map m = new HashMap();
        m.put(new Integer(1), new Character('a'));
        m.put(new Integer(3), new Character('b'));
        m.put(new Integer(5), new Character('c'));
        m.put(new Integer(7), new Character('d'));
        m.put(new Integer(11), new Character('e'));
        System.out.println("m: " + m);
        interp.set("m", m);
        interp.exec("print(m, m.__class__," +
          "m[1], m[1].__class__)");
        // Not a Python dictionary, so this fails:
        //! interp.exec("for x in m.keys():" +
        //!   "print(x, m[x])");
        // To convert a Map to a Python dictionary, use PyUtil:
        interp.set("m", PyUtil.toPyDictionary(m));
        interp.exec("print(m, m.__class__, " +
          "m[1], m[1].__class__)");
        interp.exec("for x in m.keys():print(x,m[x])");
      }
    }


As usual with Java, the distinction between real objects and primitive types
causes trouble. In general, if you pass a regular object to **set( )**, it knows
what to do with it, but if you want to pass in a primitive you must perform a
conversion. One way to do this is to create a "Py" type, such as **PyInteger**
or **PyFloat**. but it turns out you can also use Java's own object wrappers
like **Integer** and **Float**, which is probably going to be a lot easier to
remember.

Early in the program you'll see an **exec( )** containing the Python statement::

    print(a[5:])

The colon inside the indexing statement indicates a Python *slice*, which
produces a range of elements from the original array. In this case, it produces
an array containing the elements from number 5 until the end of the array. You
could also say '**a[3:5]**' to produce elements 3 through 5, or '**a[:5]**' to
produce the elements zero through 5. The reason a slice is used in this
statement is to make sure that the Java **String** has really been converted to
a Python string, which can also be treated as an array of characters.

You can see that it's possible, using **exec( )**, to create a Python function
(although it's a bit awkward). The **prt( )** function prints the whole array,
and then (to make sure it's a real Python array), iterates through each element
of the array and prints it. Finally, it prints the class of the array, so we can
see what conversion has taken place (Python not only has run-time type
information, it also has the equivalent of Java reflection). The **prt( )**
function is used to print arrays that come from each of the Java primitive
types.

Although a Java **ArrayList** does pass into the interpreter using **set( )**,
and you can index into it as if it were an array, trying to create a slice
fails. To completely convert it into an array, one approach is to simply extract
a Java array using **toArray( )**, and pass that in. The **set( )** method
converts it to a **PyArray** - one of the classes provided with Jython - which
can be treated as a Python array (you can also explicitly create a **PyArray**,
but this seems unnecessary).

Finally, a **Map** is created and passed directly into the interpreter. While it
is possible to do simple things like index into the resulting object, it's not a
real Python dictionary so you can't (for example) call the **keys( )** method.
There is no straightforward way to convert a Java **Map** into a Python
dictionary, and so I wrote a utility called **toPyDictionary( )** and made it a
**static** method of **net.mindview.python.PyUtil**. This also includes
utilities to extract a Python array into a Java **List**, and a Python
dictionary into a Java **Map**:

..  code-block:: java

    // Jython/PyUtil.java
    // PythonInterpreter utilities
    import org.python.util.PythonInterpreter;
    import org.python.core.*;
    import java.util.*;

    public class PyUtil {
      /** Extract a Python tuple or array into a Java
      List (which can be converted into other kinds
      of lists and sets inside Java).
      @param interp The Python interpreter object
      @param pyName The id of the python list object
      */
      public static List
      toList(PythonInterpreter interp, String pyName){
        return new ArrayList(Arrays.asList(
          (Object[])interp.get(
            pyName, Object[].class)));
      }
      /** Extract a Python dictionary into a Java Map
      @param interp The Python interpreter object
      @param pyName The id of the python dictionary
      */
      public static Map
      toMap(PythonInterpreter interp, String pyName){
        PyList pa = ((PyDictionary)interp.get(
          pyName)).items();
        Map map = new HashMap();
        while(pa.__len__() != 0) {
          PyTuple po = (PyTuple)pa.pop();
          Object first = po.__finditem__(0)
            .__tojava__(Object.class);
          Object second = po.__finditem__(1)
            .__tojava__(Object.class);
          map.put(first, second);
        }
        return map;
      }
      /** Turn a Java Map into a PyDictionary,
      suitable for placing into a PythonInterpreter
      @param map The Java Map object
      */
      public static PyDictionary toPyDictionary(Map map) {
        Map m = new HashMap();
        Iterator it = map.entrySet().iterator();
        while(it.hasNext()) {
          Map.Entry e = (Map.Entry)it.next();
          m.put(Py.java2py(e.getKey()),
            Py.java2py(e.getValue()));
        }
        return new PyDictionary(m);
      }
    }


Here is the unit testing code:

..  code-block:: java

    // Jython/TestPyUtil.java
    import org.python.util.PythonInterpreter;
    import java.util.*;

    public class TestPyUtil {
      PythonInterpreter pi = new PythonInterpreter();
      public void test1() {
        pi.exec("tup=('fee','fi','fo','fum','fi')");
        List lst = PyUtil.toList(pi, "tup");
        System.out.println(lst);
        System.out.println(new HashSet(lst));
      }
      public void test2() {
        pi.exec("ints=[1,3,5,7,9,11,13,17,19]");
        List lst = PyUtil.toList(pi, "ints");
        System.out.println(lst);
      }
      public void test3() {
        pi.exec("dict = { 1 : 'a', 3 : 'b', " +
          "5 : 'c', 9 : 'd', 11 : 'e'}");
        Map mp = PyUtil.toMap(pi, "dict");
        System.out.println(mp);
      }
      public void test4() {
        Map m = new HashMap();
        m.put("twas", new Integer(11));
        m.put("brillig", new Integer(27));
        m.put("and", new Integer(47));
        m.put("the", new Integer(42));
        m.put("slithy", new Integer(33));
        m.put("toves", new Integer(55));
        System.out.println(m);
        pi.set("m", PyUtil.toPyDictionary(m));
        pi.exec("print(m)");
        pi.exec("print(m['slithy'])");
      }
      public static void main(String args[]) {
        TestPyUtil test = new TestPyUtil();
        test.test1();
        test.test2();
        test.test3();
        test.test4();
      }
    }


We'll see the use of the extraction tools in the next section.

Getting Data Out
--------------------------------------------------------------------------------

There are a number of different ways to extract data from the
**PythonInterpreter**. If you simply call the **get( )** method, passing it the
object identifier as a string, it returns a **PyObject** (part of the
**org.python.core** support classes). It's possible to "cast" it using the
**__tojava__( )** method, but there are better alternatives:


1.  The convenience methods in the **Py** class, such as **py2int( )**, take a
    **PyObject** and convert it to a number of different types.

2.  An overloaded version of **get( )** takes the desired Java **Class** object
    as a second argument, and produces an object that has that run-time type (so you
    still need to perform a cast on the result in your Java code).

Using the second approach, getting an array from the **PythonInterpreter** is
quite easy. This is especially useful because Python is exceptionally good at
manipulating strings and files, and so you will commonly want to extract the
results as an array of strings. For example, you can do a wildcard expansion of
file names using Python's **glob( )**, as shown further down in the following
code:

..  code-block:: java

    // Jython/PythonInterpreterGetting.java
    // Getting data from the PythonInterpreter object.
    import org.python.util.PythonInterpreter;
    import org.python.core.*;
    import java.util.*;

    public class PythonInterpreterGetting {
      public static void
      main(String[] args) throws PyException  {
        PythonInterpreter interp = new PythonInterpreter();
        interp.exec("a = 100");
        // If you just use the ordinary get(),
        // it returns a PyObject:
        PyObject a = interp.get("a");
        // There's not much you can do with a generic
        // PyObject, but you can print it out:
        System.out.println("a = " + a);
        // If you know the type it's supposed to be,
        // you can "cast" it using __tojava__() to
        // that Java type and manipulate it in Java.
        // To use 'a' as an int, you must use
        // the Integer wrapper class:
        int ai= ((Integer)a.__tojava__(Integer.class))
          .intValue();
        // There are also convenience functions:
        ai = Py.py2int(a);
        System.out.println("ai + 47 = " + (ai + 47));
        // You can convert it to different types:
        float af = Py.py2float(a);
        System.out.println("af + 47 = " + (af + 47));
        // If you try to cast it to an inappropriate
        // type you'll get a runtime exception:
        //! String as = (String)a.__tojava__(
        //!   String.class);

        // If you know the type, a more useful method
        // is the overloaded get() that takes the
        // desired class as the 2nd argument:
        interp.exec("x = 1 + 2");
        int x = ((Integer)interp
          .get("x", Integer.class)).intValue();
        System.out.println("x = " + x);

        // Since Python is so good at manipulating
        // strings and files, you will often need to
        // extract an array of Strings. Here, a file
        // is read as a Python array:
        interp.exec("lines = " +
          "open('PythonInterpreterGetting.java')" +
          ".readlines()");
        // Pull it in as a Java array of String:
        String[] lines = (String[])
          interp.get("lines", String[].class);
        for(int i = 0; i < 10; i++)
          System.out.print(lines[i]);

        // As an example of useful string tools,
        // global expansion of ambiguous file names
        // using glob is very useful, but it's not
        // part of the standard Jython package, so
        // you'll have to make sure that your
        // Python path is set to include these, or
        // that you deliver the necessary Python
        // files with your application.
        interp.exec("from glob import glob");
        interp.exec("files = glob('*.java')");
        String[] files = (String[])
          interp.get("files", String[].class);
        for(int i = 0; i < files.length; i++)
          System.out.println(files[i]);

        // You can extract tuples and arrays into
        // Java Lists with net.mindview.PyUtil:
        interp.exec("tup = ('fee', 'fi', 'fo', 'fum', 'fi')");
        List tup = PyUtil.toList(interp, "tup");
        System.out.println(tup);
        // It really is a list of String objects:
        System.out.println(tup.get(0).getClass());
        // You can easily convert it to a Set:
        Set tups = new HashSet(tup);
        System.out.println(tups);
        interp.exec("ints=[1,3,5,7,9,11,13,17,19]");
        List ints = PyUtil.toList(interp, "ints");
        System.out.println(ints);
        // It really is a List of Integer objects:
        System.out.println((ints.get(1)).getClass());

        // If you have a Python dictionary, it can
        // be extracted into a Java Map, again with
        // net.mindview.PyUtil:
        interp.exec("dict = { 1 : 'a', 3 : 'b'," +
          "5 : 'c', 9 : 'd', 11 : 'e' }");
        Map map = PyUtil.toMap(interp, "dict");
        System.out.println("map: " + map);
        // It really is Java objects, not PyObjects:
        Iterator it = map.entrySet().iterator();
        Map.Entry e = (Map.Entry)it.next();
        System.out.println(e.getKey().getClass());
        System.out.println(e.getValue().getClass());
      }
    }


The last two examples show the extraction of Python tuples and lists into Java
**List**s, and Python dictionaries into Java **Map**s. Both of these cases
require more processing than is provided in the standard Jython library, so I
have again created utilities in **net.mindview.pyton.PyUtil**: **toList( )** to
produce a **List** from a Python sequence, and **toMap( )** to produce a **Map**
from a Python dictionary. The **PyUtil** methods make it easier to take
important data structures back and forth between Java and Python.

Multiple Interpreters
--------------------------------------------------------------------------------

It's also worth noting that you can have multiple **PythonInterpreter** objects
in a program, and each one has its own name space:

..  code-block:: java

    // Jython/MultipleJythons.java
    // You can run multiple interpreters, each
    // with its own name space.
    import org.python.util.PythonInterpreter;
    import org.python.core.*;

    public class MultipleJythons {
      public static void
      main(String[] args) throws PyException  {
        PythonInterpreter
          interp1 =  new PythonInterpreter(),
          interp2 =  new PythonInterpreter();
        interp1.set("a", new PyInteger(42));
        interp2.set("a", new PyInteger(47));
        interp1.exec("print(a)");
        interp2.exec("print(a)");
        PyObject x1 = interp1.get("a");
        PyObject x2 = interp2.get("a");
        System.out.println("a from interp1: " + x1);
        System.out.println("a from interp2: " + x2);
      }
    }


When you run the program you'll see that the value of **a** is distinct within
each **PythonInterpreter**.

Controlling Java from Jython
=======================================================================

Since you have the Java language at your disposal, and you can set and retrieve
values in the interpreter, there's a tremendous amount that you can accomplish
with the above approach (controlling Python from Java).  But one of the amazing
things about Jython is that it makes Java classes almost transparently available
from within Jython. Basically, a Java class looks like a Python class. This is
true for standard Java library classes as well as classes that you create
yourself, as you can see here::

    # Jython/JavaClassInPython.py
    # run with: jython.bat JavaClassInPython.py
    # Using Java classes within Jython
    from java.util import Date, HashSet, HashMap
    from Jython.javaclass import JavaClass
    from math import sin

    d = Date() # Creating a Java Date object
    print(d) # Calls toString()

    # A "generator" to easily create data:
    class ValGen:
        def __init__(self, maxVal):
            self.val = range(maxVal)
        # Called during 'for' iteration:
        def __getitem__(self, i):
            # Returns a tuple of two elements:
            return self.val[i], sin(self.val[i])

    # Java standard containers:
    map = HashMap()
    set = HashSet()

    for x, y in ValGen(10):
        map.put(x, y)
        set.add(y)
        set.add(y)

    print(map)
    print(set)

    # Iterating through a set:
    for z in set:
        print(z, z.__class__)

    print(map[3]) # Uses Python dictionary indexing
    for x in map.keySet(): # keySet() is a Map method
        print(x, map[x])

    # Using a Java class that you create yourself is
    # just as easy:
    jc = JavaClass()
    jc2 = JavaClass("Created within Jython")
    print(jc2.getVal())
    jc.setVal("Using a Java class is trivial")
    print(jc.getVal())
    print(jc.getChars())
    jc.val = "Using bean properties"
    print(jc.val)


The "**=M**" comment is recognized by the makefile generator tool (that I
created for this book) as a replacement makefile command. This will be used
instead of the commands that the extraction tool would normally place in the
makefile.

Note that the **import** statements map to the Java package structure exactly as
you would expect. In the first example, a **Date( )** object is created as if it
were a native Python class, and printing this object just calls **toString( )**.

**ValGen** implements the concept of a "generator" which is used a great deal in
the C++ STL (*Standard Template Library*, part of the Standard C++ Library). A
generator is an object that produces a new object every time its "generation
method" is called, and it is quite convenient for filling containers. Here, I
wanted to use it in a **for** iteration, and so I needed the generation method
to be the one that is called by the iteration process. This is a special method
called **__getitem__( )**, which is actually the overloaded operator for
indexing, '**[ ]**'. A **for** loop calls this method every time it wants to
move the iteration forward, and when the elements run out, **__getitem__( )**
throws an out-of-bounds exception and that signals the end of the **for** loop
(in other languages, you would never use an exception for ordinary control flow,
but in Python it seems to work quite well). This exception happens automatically
when **self.val[i]** runs out of elements, so the **__getitem__( )** code turns
out to be simple. The only complexity is that **__getitem__( )** appears to
return *two* objects instead of just one. What Python does is automatically
package multiple return values into a tuple, so you still only end up returning
a single object (in C++ or Java you would have to create your own data structure
to accomplish this). In addition, in the **for** loop where **ValGen** is used,
Python automatically "unpacks" the tuple so that you can have multiple iterators
in the **for**. These are the kinds of syntax simplifications that make Python
so endearing.

The **map** and **set** objects are instances of Java's **HashMap** and
**HashSet**, again created as if those classes were just native Python
components. In the **for** loop, the **put( )** and **add( )** methods work just
like they do in Java. Also, indexing into a Java **Map** uses the same notation
as for dictionaries, but note that to iterate through the keys in a **Map** you
must use the **Map** method **keySet( )** rather than the Python dictionary
method **keys( )**.

The final part of the example shows the use of a Java class that I created from
scratch, to demonstrate how trivial it is. Notice also that Jython intuitively
understands JavaBeans properties, since you can either use the **getVal( )** and
**setVal( )** methods, or assign to and read from the equivalent **val**
property. Also, **getChars( )** returns a **Character[]** in Java, and this
becomes an array in Python.

The easiest way to use Java classes that you create for use inside a Python
program is to put them inside a package. Although Jython can also import
unpackaged java classes (**import JavaClass**), all such unpackaged java classes
will be treated as if they were defined in different packages so they can only
see each other's public methods.

Java packages translate into Python modules, and Python must import a module in
order to be able to use the Java class. Here is the Java code for **JavaClass**:

..  code-block:: java

    // Jython/javaclass/JavaClass.java
    package Jython.javaclass;
    import java.util.*;

    public class JavaClass {
      private String s = "";
      public JavaClass() {
        System.out.println("JavaClass()");
      }
      public JavaClass(String a) {
        s = a;
        System.out.println("JavaClass(String)");
      }
      public String getVal() {
        System.out.println("getVal()");
        return s;
      }
      public void setVal(String a) {
        System.out.println("setVal()");
        s = a;
      }
      public Character[] getChars() {
        System.out.println("getChars()");
        Character[] r = new Character[s.length()];
        for(int i = 0; i < s.length(); i++)
          r[i] = new Character(s.charAt(i));
        return r;
      }
      public static void main(String[] args) {
        JavaClass
          x1 = new JavaClass(),
          x2 = new JavaClass("UnitTest");
        System.out.println(x2.getVal());
        x1.setVal("SpamEggsSausageAndSpam");
        System.out.println(Arrays.toString(x1.getChars()));
      }
    }


You can see that this is just an ordinary Java class, without any awareness that
it will be used in a Jython program. For this reason, one of the important uses
of Jython is in testing Java code [#]_. Because Python is such a powerful,
flexible, dynamic language it is an ideal tool for automated test frameworks,
without making any changes to the Java code that's being tested.

Inner Classes
------------------------------------------------------------------------------

Inner classes becomes attributes on the class object. Instances of **static**
inner classes can be created with the usual call::

    com.foo.JavaClass.StaticInnerClass()

Non-**static** inner classes must have an outer class instance supplied
explicitly as the first argument::

    com.foo.JavaClass.InnerClass(com.foo.JavaClass())

Using Java libraries
=======================================================================

Jython wraps the Java libraries so that any of them can be used directly or via
inheritance. In addition, Python shorthand simplifies coding.

As an example, consider the **HTMLButton.java** example from Chapter 9 of
*Thinking in Java* (you presumably have already downloaded and installed the
source code for that book from `www.MindviewInc.com
<http://www.MindviewInc.com>`_, since a number of examples in this book use
libraries from that book). Here is its conversion to Jython::

    # Jython/PythonSwing.py
    # The HTMLButton.java example from "Thinking in Java"
    # converted into Jython.
    from javax.swing import JFrame, JButton, JLabel
    from java.awt import FlowLayout

    frame = JFrame("HTMLButton", visible=1,
      defaultCloseOperation=JFrame.EXIT_ON_CLOSE)

    def kapow(e):
        frame.contentPane.add(
          JLabel("<html><i><font size=+4>Kapow!"))
        # Force a re-layout to include the new label:
        frame.validate()

    button = JButton("<html><b><font size=+2>" +
      "<center>Hello!<br><i>Press me now!",
      actionPerformed=kapow)
    frame.contentPane.layout = FlowLayout()
    frame.contentPane.add(button)
    frame.pack()
    frame.size=200, 500


If you compare the Java version of the program to the above Jython
implementation, you'll see that Jython is shorter and generally easier to
understand. For example, in the Java version to set up the frame you had to make
several calls: the constructor for **JFrame( )**, the **setVisible( )** method
and the **setDefaultCloseOperation( )** method, whereas in the above code all
three of these operations are performed with a single constructor call.

Also notice that the **JButton** is configured with an **actionListener( )**
method inside the constructor, with the assignment to **kapow**. In addition,
Jython's JavaBean awareness means that a call to any method with a name that
begins with "**set**" can be replaced with an assignment, as you can see above.

The only method that did not come over from Java is the **pack( )** method,
which seems to be essential in order to force the layout to happen properly.
It's also important that the call to **pack( )** appear *before* the **size**
setting.

Inheriting from Java library Classes
-------------------------------------------------------------------------------

You can easily inherit from standard Java library classes in
Jython. Here's the **Dialogs.java** example from *Thinking in Java*,
converted into Jython::

    # Jython/PythonDialogs.py
    # Dialogs.java from "Thinking in Java," converted into Jython.
    from java.awt import FlowLayout
    from javax.swing import JFrame, JDialog, JLabel
    from javax.swing import JButton

    class MyDialog(JDialog):
      def __init__(self, parent=None):
          JDialog.__init__(self,
                           title="My dialog", modal=1)
          self.contentPane.layout = FlowLayout()
          self.contentPane.add(JLabel("A dialog!"))
          self.contentPane.add(JButton("OK",
              actionPerformed = lambda e, t=self: t.dispose()))
          self.pack()

    frame = JFrame("Dialogs", visible=1,
                   defaultCloseOperation=JFrame.EXIT_ON_CLOSE)
    dlg = MyDialog()
    frame.contentPane.add(
        JButton("Press here to get a Dialog Box",
                actionPerformed = lambda e: dlg.show()))
    frame.pack()


**MyDialog** is inherited from **JDialog**, and you can see named arguments
being used in the call to the base-class constructor.

In the creation of the "OK" **JButton**, note that the **actionPerformed**
method is set right inside the constructor, and that the function is created
using the Python **lambda** keyword. This creates a nameless function with the
arguments appearing before the colon and the expression that generates the
returned value after the colon. As you should know, the Java prototype for the
**actionPerformed( )** method only contains a single argument, but the lambda
expression indicates two. However, the second argument is provided with a
default value, so the function *can* be called with only one argument. The
reason for the second argument is seen in the default value, because this is a
way to pass **self** into the lambda expression, so that it can be used to
dispose of the dialog.

Compare this code with the version that's published in *Thinking in Java*.
You'll find that Python language features allow a much more succinct and direct
implementation.

Creating Java classes with Jython
=======================================================================

.. note:: Jython 2.5.0 does not support jythonc. Support is planned
   	  for 2.5.1. jythonc basically converted python source to java
   	  source, the replacement will generate bytecodes directly,
   	  and enable jython code to be imported directly into java
   	  (via generated proxies).

Jython can also create Java classes directly from your Jython
code. This can produce very useful results, as you are then able to
treat the results as if they are native Java classes, albeit with
Python power under the hood.

To produce Java classes from Python code, Jython comes with a compiler called
**jythonc**.

The process of creating Python classes that will produce Java classes
is a bit more complex than when calling Java classes from Python,
because the methods in Java classes are statically typed, while Python
functions and methods are dynamically typed. Thus, you must somehow
tell **jythonc** that a Python method is intended to have a particular
set of argument types and that its return value is a particular
type. You accomplish this with the "@sig" string, which is placed
right after the beginning of the Python method definition (this is the
standard location for the Python documentation string). For example::

    def returnArray(self):
        "@sig public java.lang.String[] returnArray()"

The Python definition doesn't specify any return type, but the @sig string gives
the full type information about what is being passed and returned. The
**jythonc** compiler uses this information to generate the correct Java code.

There's one other set of rules you must follow in order to get a successful
compilation: you must inherit from a Java class or interface in your Python
class (you do not need to specify the **@sig** signature for methods defined in
the superclass/interface). If you do not do this, you won't get your desired
methods - unfortunately, **jythonc** gives you no warnings or errors in this
case, but you won't get what you want. If you don't see what's missing, it can
be very frustrating.

In addition, you must import the appropriate java class and give the correct
package specification.  In the example below, **java** is imported so you must
inherit from **java.lang.Object**, but you could also say **from java.lang
import Object** and then you'd just inherit from **Object** without the package
specification. Unfortunately, you don't get any warnings or errors if you get
this wrong, so you must be patient and keep trying.

Here is an example of a Python class created to produce a Java class. This also
introduces the '**=T**' directive for the makefile builder tool, which specifies
a different target than the one that is normally used by the tool. In this case,
the Python file is used to build a Java **.class** file, so the class file is
the desired target::

    # Jython/PythonToJavaClass.py
    # A Python class converted into a Java class
    # Compile with:
    # jythonc --package python.java.test PythonToJavaClass.py
    from jarray import array
    import java

    class PythonToJavaClass(java.lang.Object):
        # The '@sig' signature string is used to create the
        # proper signature in the resulting Java code:
        def __init__(self):
            "@sig public PythonToJavaClass()"
            print("Constructor for PythonToJavaClass")

        def simple(self):
            "@sig public void simple()"
            print("simple()")

        # Returning values to Java:
        def returnString(self):
            "@sig public java.lang.String returnString()"
            return "howdy"

        # You must construct arrays to return along
        # with the type of the array:
        def returnArray(self):
            "@sig public java.lang.String[] returnArray()"
            test = [ "fee", "fi", "fo", "fum" ]
            return array(test, java.lang.String)

        def ints(self):
            "@sig public java.lang.Integer[] ints()"
            test = [ 1, 3, 5, 7, 11, 13, 17, 19, 23 ]
            return array(test, java.lang.Integer)

        def doubles(self):
            "@sig public java.lang.Double[] doubles()"
            test = [ 1, 3, 5, 7, 11, 13, 17, 19, 23 ]
            return array(test, java.lang.Double)

        # Passing arguments in from Java:
        def argIn1(self, a):
            "@sig public void argIn1(java.lang.String a)"
            print("a: %s" % a)
            print("a.__class__", a.__class__)

        def argIn2(self, a):
            "@sig public void argIn1(java.lang.Integer a)"
            print("a + 100: %d" % (a + 100))
            print("a.__class__", a.__class__)

        def argIn3(self, a):
            "@sig public void argIn3(java.util.List a)"
            print("received List:", a, a.__class__)
            print("element type:", a[0].__class__)
            print("a[3] + a[5]:", a[5] + a[7])
            #! print("a[2:5]:", a[2:5]) # Doesn't work

        def argIn4(self, a):
            "@sig public void \
               argIn4(org.python.core.PyArray a)"
            print("received type:", a.__class__)
            print("a: ", a)
            print("element type:", a[0].__class__)
            print("a[3] + a[5]:", a[5] + a[7])
            print("a[2:5]:", a[2:5] # A real Python array)

        # A map must be passed in as a PyDictionary:
        def argIn5(self, m):
            "@sig public void \
               argIn5(org.python.core.PyDictionary m)"
            print("received Map: ", m, m.__class__)
            print("m['3']:", m['3'])
            for x in m.keys():
                print(x, m[x])


First note that **PythonToJavaClass** is inherited from **java.lang.Object**; if
you don't do this you will quietly get a Java class without the right
signatures. You are not required to inherit from **Object**; any other Java
class will do.

This class is designed to demonstrate different  arguments and return values, to
provide you with enough examples that you'll be able to easily create your own
signature strings. The first three of these are fairly self-explanatory, but
note the full qualification of the Java name in the signature string.

In **returnArray( )**, a Python array must be returned as a Java array. To do
this, the Jython **array( )** function (from the **jarray** module) must be
used, along with the type of the class for the resulting array. Any time you
need to return an array to Java, you must use **array( )**, as seen in the
methods **ints( )** and **doubles( )**.

The last methods show how to pass arguments in from Java. Basic types happen
automatically as long as you specify them in the **@sig** string, but you must
use objects and you cannot pass in primitives (that is, primitives must be
ensconced in wrapper objects, such as **Integer**).

In **argIn3( )**, you can see that a Java **List** is transparently converted to
something that behaves just like a Python array, but is not a true array because
you cannot take a slice from it. If you want a true Python array, then you must
create and pass a **PyArray** as in **argIn4( )**, where the slice is
successful. Similarly, a Java **Map** must come in as a **PyDictionary** in
order to be treated as a Python dictionary.

Here is the Java program to exercise the Java classes produced by the
above Python code. You can't compile **TestPythonToJavaClass.java**
until **PythonToJavaClass.class** is available:

..  code-block:: java

    // Jython/TestPythonToJavaClass.java
    import java.lang.reflect.*;
    import java.util.*;
    import org.python.core.*;
    import java.util.*;
    import net.mindview.python.*;
    // The package with the Python-generated classes:
    import python.java.test.*;

    public class TestPythonToJavaClass {
      PythonToJavaClass p2j = new PythonToJavaClass();
      public void testDumpClassInfo() {
        System.out.println(
          Arrays.toString(
            p2j.getClass().getConstructors()));
        Method[] methods = p2j.getClass().getMethods();
        for(int i = 0; i < methods.length; i++) {
          String nm = methods[i].toString();
          if(nm.indexOf("PythonToJavaClass") != -1)
            System.out.println(nm);
        }
      }
      public static void main(String[] args) {
        p2j.simple();
        System.out.println(p2j.returnString());
        System.out.println(
          Arrays.toString(p2j.returnArray()));
        System.out.println(
          Arrays.toString(p2j.ints());
        System.out.println(
          Arrays.toString(p2j.doubles()));
        p2j.argIn1("Testing argIn1()");
        p2j.argIn2(new Integer(47));
        ArrayList a = new ArrayList();
        for(int i = 0; i < 10; i++)
          a.add(new Integer(i));
        p2j.argIn3(a);
        p2j.argIn4(
          new PyArray(Integer.class, a.toArray()));
        Map m = new HashMap();
        for(int i = 0; i < 10; i++)
          m.put("" + i, new Float(i));
        p2j.argIn5(PyUtil.toPyDictionary(m));
      }
    }


For Python support, you'll usually only need to import the classes in
**org.python.core**. Everything else in the above example is fairly
straightforward, as **PythonToJavaClass** appears, from the Java side, to be
just another Java class. **dumpClassInfo( )** uses reflection to verify that the
method signatures specified in **PythonToJavaClass.py** have come through
properly.

Building Java Classes from Python
--------------------------------------------------------------------------------

Part of the trick of creating Java classes from Python code is the @sig
information in the method documentation strings. But there's a second problem
which stems from the fact that Python has no "package" keyword - the Python
equivalent of packages (modules) are implicitly created based on the file name.
However, to bring the resulting class files into the Java program, **jythonc**
must be given information about how to create the Java package for the Python
code. This is done on the **jythonc** command line using the **--package** flag,
followed by the package name you wish to produce (including the separation dots,
just as you would give the package name using the **package** keyword in a Java
program). This will put the resulting **.class** files in the appropriate
subdirectory off of the current directory. Then you only need to import the
package in your Java program, as shown above (you'll need '**.**' in your
CLASSPATH in order to run it from the code directory).

Here are the **make** dependency rules that I used to build the above example
(the backslashes at the ends of the lines are understood by **make** to be line
continuations)::

    TestPythonToJavaClass.class: \\
            TestPythonToJavaClass.java \\
            python\java\test\PythonToJavaClass.class
        javac TestPythonToJavaClass.java

    python\java\test\PythonToJavaClass.class: \\
            PythonToJavaClass.py
        jythonc.bat --package python.java.test \\
        PythonToJavaClass.py

The first target, **TestPythonToJavaClass.class**, depends on both
**TestPythonToJavaClass.java** and the **PythonToJavaClass.class**, which is the
Python code that's converted to a class file. This latter, in turn, depends on
the Python source code. Note that it's important that the directory where the
target lives be specified, so that the makefile will create the Java program
with the minimum necessary amount of rebuilding.

Summary
=======================================================================

This chapter has arguably gone much deeper into Jython than required to use the
interpreter design pattern. Indeed, once you decide that you need to use
interpreter and that you're not going to get lost inventing your own language,
the solution of installing Jython is quite simple, and you can at least get
started by following the **GreenHouseController** example.

Of course, that example is often too simple and you may need something more
sophisticated, often requiring more interesting data to be passed back and
forth. When I encountered the limited documentation, I felt it necessary to come
up with a more thorough examination of Jython.

In the process, note that there could be another equally powerful
design pattern lurking in here, which could perhaps be called
*multiple languages* or *language hybridizing*. This is based on the
experience of having each language solve a certain class of problems
better than the other; by combining languages you can solve problems
much faster than with either language by itself. CORBA is another way
to bridge across languages, and at the same time bridging between
computers and operating systems.

To me, Python and Java present a very potent combination for program development
because of Java's architecture and tool set, and Python's extremely rapid
development (generally considered to be 5-10 times faster than C++ or Java).
Python is usually slower, however, but even if you end up re-coding parts of
your program for speed, the initial fast development will allow you to more
quickly flesh out the system and uncover and solve the critical sections. And
often, the execution speed of Python is not a problem - in those cases it's an
even bigger win. A number of commercial products already use Java and Jython,
and because of the terrific productivity leverage I expect to see this happen
more in the future.

Exercises
=======================================================================

#.  Modify **GreenHouseLanguage.py** so that it checks the times for the events
    and runs those events at the appropriate times.

#.  Modify **GreenHouseLanguage.py** so that it calls a function for **action**
    instead of just printing a string.

#.  Create a Swing application with a **JTextField** (where the user will enter
    commands) and a **JTextArea** (where the command results will be displayed).
    Connect to a **PythonInterpreter** object so that the output will be sent to
    the **JTextArea** (which should scroll). You'll need to locate the
    **PythonInterpreter** command that redirects the output to a Java stream.

#.  Modify **GreenHouseLanguage.py** to add a master controller class (instead
    of the static array inside **Event**) and provide a **run( )** method for
    each of the subclasses. Each **run( )** should create and use an object from
    the standard Java library during its execution. Modify
    **GreenHouseController.java** to use this new class.

#.  Modify the resulting **GreenHouseLanguage.py** from exercise two to produce
    Java classes (add the @sig documentation strings to produce the correct Java
    signatures, and create a makefile to build the Java **.class** files). Write
    a Java program that uses these classes.

.. rubric:: Footnotes

.. [#]  The original version of this was called *JPython*\, but the project
        changed and the name was changed to emphasize the distinctness of the new
        version.

.. [#]  Changing the registry setting **python.security.respectJavaAccessibility
        = true** to **false** makes testing even more powerful because it allows
        the test script to use *all* methods, even protected and package-
        private.



