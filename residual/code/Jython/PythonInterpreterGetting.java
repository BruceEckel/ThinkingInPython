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