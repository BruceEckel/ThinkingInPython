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