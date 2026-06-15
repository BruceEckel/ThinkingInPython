# os_walk_comprehension.py
import os

rest_files = [os.path.join(d[0], f) for d in os.walk(".")
             for f in d[2] if f.endswith(".rst")]
for r in rest_files:
    print(r)
