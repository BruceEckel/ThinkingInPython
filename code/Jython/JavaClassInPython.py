# Jython/JavaClassInPython.py
# run with: jython.bat JavaClassInPython.py
# Using Java classes within Jython
from java.util import Date, HashSet, HashMap
from jython.javaclass import JavaClass
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