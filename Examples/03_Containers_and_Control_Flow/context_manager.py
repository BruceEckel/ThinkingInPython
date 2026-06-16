# context_manager.py
import os
import tempfile

path = os.path.join(tempfile.gettempdir(), "demo.txt")
with open(path, "w") as f:
    f.write("one\ntwo\n")  # f.close() happens automatically

with open(path) as f:
    for line in f:
        print(line.strip())
os.remove(path)
