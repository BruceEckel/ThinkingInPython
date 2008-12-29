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