// Jython/TestPythonToJavaClass.java
//+D python\java\test\PythonToJavaClass.class
package jython;
import java.lang.reflect.*;
import java.util.*;
import org.python.core.*;
import junit.framework.*;
import java.util.*;
import net.mindview.python.*;
// The package with the Python-generated classes:
import python.java.test.*;

public class
TestPythonToJavaClass extends TestCase  {
  PythonToJavaClass p2j = new PythonToJavaClass();
  public void testDumpClassInfo() {
    System.out.println(
      Arrays.toString(
        p2j.getClass().getConstructors()));
    Method[] methods =
      p2j.getClass().getMethods();
    for(int i = 0; i < methods.length; i++) {
      String nm = methods[i].toString();
      if(nm.indexOf("PythonToJavaClass") != -1)
        System.out.println(nm);
    }
  }
  public void test1() {
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
  public static void main(String[] args) {
    junit.textui.TestRunner.run(
      TestPythonToJavaClass.class);
  }
}