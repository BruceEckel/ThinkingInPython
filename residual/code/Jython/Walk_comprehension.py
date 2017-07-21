# Jython/Walk_comprehension.py
import os
restFiles = [os.path.join(d[0], f) for d in os.walk(".")
             for f in d[2] if f.endswith(".java") and 
             "PythonInterpreter" in open(os.path.join(d[0], f)).read()]
for r in restFiles:
    print(r)
