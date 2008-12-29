// Jython/MultipleJythons.java
// You can run multiple interpreters, each
// with its own name space.
package jython;
import org.python.util.PythonInterpreter;
import org.python.core.*;
import junit.framework.*;

public class MultipleJythons extends TestCase  {
  PythonInterpreter
    interp1 =  new PythonInterpreter(),
    interp2 =  new PythonInterpreter();
  public void test() throws PyException {
    interp1.set("a", new PyInteger(42));
    interp2.set("a", new PyInteger(47));
    interp1.exec("print(a)");
    interp2.exec("print(a)");
    PyObject x1 = interp1.get("a");
    PyObject x2 = interp2.get("a");
    System.out.println("a from interp1: " + x1);
    System.out.println("a from interp2: " + x2);
  }
  public static void
  main(String[] args) throws PyException  {
    junit.textui.TestRunner.run(MultipleJythons.class);
  }
}