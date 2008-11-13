// Jython/Test.java
package net.mindview.python;
import org.python.util.PythonInterpreter;
import java.util.*;
import junit.framework.*;

public class Test extends TestCase  {
  PythonInterpreter pi =
    new PythonInterpreter();
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
    junit.textui.TestRunner.run(Test.class);
  }
}