# lazy_modules_check.py
import sys
lazy from noisy import announce

print(len(sys.lazy_modules) > 1)
#: True
print("noisy" in sys.lazy_modules)
#: True
announce()
#: noisy module loaded
#: noisy.announce() called
print("noisy" in sys.lazy_modules)
#: False
