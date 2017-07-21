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