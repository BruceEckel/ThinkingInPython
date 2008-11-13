// Jython/PythonInterpreterSetting.java
// Passing data from Java to python when using
// the PythonInterpreter object.
package jython;
import org.python.util.PythonInterpreter;
import org.python.core.*;
import java.util.*;
import net.mindview.python.*;
import junit.framework.*;

public class
PythonInterpreterSetting extends TestCase  {
  PythonInterpreter interp =
    new PythonInterpreter();
  public void test() throws PyException  {
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
    // To convert a Map to a Python dictionary,
    // use net.mindview.python.PyUtil:
    interp.set("m", PyUtil.toPyDictionary(m));
    interp.exec("print(m, m.__class__, " +
      "m[1], m[1].__class__)");
    interp.exec("for x in m.keys():print(x,m[x])");
  }
  public static void
  main(String[] args) throws PyException  {
    junit.textui.TestRunner.run(
      PythonInterpreterSetting.class);
  }
}