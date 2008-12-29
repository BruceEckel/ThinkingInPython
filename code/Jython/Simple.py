# Jython/Simple.py
import platform, glob, time
from subprocess import Popen, PIPE

print platform.uname() # What are we running on?
print glob.glob("*.py") # Find files with .py extensions
# Send a command to the OS and capture the results:
print Popen(["ping", "-c", "1", "www.mindview.net"], 
               stdout=PIPE).communicate()[0]

# Time an operation:
start = time.time()
for n in xrange(1000000):
    for i in xrange(10): 
        oct(i)
print time.time() - start
