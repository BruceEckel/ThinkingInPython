// jython/GreenHouseController.java
package jython;
import org.python.util.PythonInterpreter;
import org.python.core.*;
import junit.framework.*;

public class
GreenHouseController extends TestCase  {
  PythonInterpreter interp =
    new PythonInterpreter();
  public void test() throws PyException  {
    System.out.println(
      "Loading GreenHouse Language");
    interp.execfile("GreenHouseLanguage.py");
    System.out.println(
      "Loading GreenHouse Script");
    interp.execfile("Schedule.ghs");
    System.out.println(
      "Executing GreenHouse Script");
    interp.exec("run()");
  }
  public static void
  main(String[] args) throws PyException  {
    junit.textui.TestRunner.run(GreenHouseController.class);
  }
}